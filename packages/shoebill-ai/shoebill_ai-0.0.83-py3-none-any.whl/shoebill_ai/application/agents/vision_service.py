from typing import Dict, List, Optional, Any
import os

from .base_vision_service import BaseVisionService
from ...domain.agents.interfaces.vision_service_interface import VisionServiceInterface
from ...domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from ...domain.agents.interfaces.llm_generate_repository import LlmGenerateRepository
from ...domain.agents.interfaces.model_factory import ModelFactory
from ...infrastructure.agents.utils.image_utils import encode_image
from ...infrastructure.agents.ollama.factories.ollama_factory import OllamaFactory
from ...infrastructure.agents.openai.factories.openai_factory import OpenAIFactory



class VisionService(BaseVisionService, VisionServiceInterface):
    """
    Implementation of a vision-only service that can work with any vision model.
    """

    def __init__(self, factory: OllamaFactory, temperature: float = 0.6,
                 max_tokens: int = 2500, timeout: int = None):
        """
        Initialize a new VisionService.

        Args:
            api_url: The base URL of the API.
            api_token: Optional API token for authentication.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            model_name: The name of the model to use.
            timeout: Optional timeout in seconds for API requests.
            factory: Optional model factory to use. If not provided, a factory will be created based on the model_name.

        Raises:
            ValueError: If the api_url is empty or None, or if temperature or max_tokens are invalid.
        """
        super().__init__(api_url=factory.api_url, api_token=factory.api_token, model_name=factory.model_name, temperature=temperature, max_tokens=max_tokens)

        self.timeout = timeout
        self.factory = factory

        # Use the provided factory or create one based on the model_name
        # if factory:
        #
        # else:
        #     # Create factory based on model name
        #     # Check if the model is supported by Ollama
        #     if OllamaFactory.is_vision_model(model_name):
        #
        #     # Check if the model is supported by OpenAI
        #     elif OpenAIFactory.is_vision_model(model_name):
        #         self.factory = OpenAIFactory(
        #             api_key=api_token,  # API token is used as API key for OpenAI
        #             temperature=temperature,
        #             max_tokens=max_tokens,
        #             model_name=model_name,
        #             timeout=self.timeout
        #         )
        #     else:
        #         raise ValueError(f"Unsupported vision model: {model_name}. Must be an Ollama or OpenAI vision model.")

        # Create repositories
        self.chat_repository: LlmChatRepository = self.factory.create_chat_repository()
        self.generate_repository: LlmGenerateRepository = self.factory.create_generate_repository()

        # Store sessions
        self.sessions = {}

    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = None) -> Optional[Dict[str, Any]]:
        """
        Generate text using the model.

        Args:
            prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to use.
            max_tokens: Optional maximum number of tokens to generate.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if an error occurs.
                The dictionary includes:
                - 'response': The generated text
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields

        Raises:
            ValueError: If the prompt is empty or None.
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty or None")

        response_data = self.generate_repository.generate(
            user_prompt=prompt,
            system_prompt=system_prompt or self.system_prompt,
            max_tokens=max_tokens or self.max_tokens
        )

        return response_data

    def _chat(self, message: str, session_id: str, chat_history: List[Dict[str, str]] = None, 
             system_prompt: str = None) -> Optional[Dict[str, Any]]:
        """
        Chat with the model.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if an error occurs.
                The dictionary includes:
                - 'message': The model's response message
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields

        Raises:
            ValueError: If the message is empty or None, or if the session_id is empty or None.
        """
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")

        response_data = self.chat_repository.chat(
            user_message=message,
            session_id=session_id,
            chat_history=chat_history,
            system_prompt=system_prompt or self.system_prompt
        )

        return response_data


    def _chat_with_image(self, message: str, image_path: str, session_id: str,
                        chat_history: List[Dict[str, str]] = None, 
                        system_prompt: str = None) -> Optional[Dict[str, Any]]:
        """
        Chat with the model using an image as context.

        Args:
            message: The user's message.
            image_path: Path to the image file to include in the conversation.
            session_id: The ID of the chat session.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if an error occurs.
                The dictionary includes:
                - 'message': The model's response message
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields

        Raises:
            ValueError: If the message is empty or None, if the session_id is empty or None,
                       or if the image_path is invalid.
            FileNotFoundError: If the image file does not exist.
        """
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")
        if not image_path:
            raise ValueError("Image path cannot be empty or None")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Encode the image to base64
        image_base64 = encode_image(image_path)

        # Create custom messages with image
        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": message, "images": [image_base64]}
        ]

        # Add chat history if provided
        if chat_history:
            # Insert history before the current message
            for i, msg in enumerate(chat_history):
                role = msg.get("role", "user" if i % 2 == 0 else "assistant")
                content = msg.get("content", "")
                # Preserve images if they exist in the history
                images = msg.get("images", None)
                history_msg = {"role": role, "content": content}
                if images:
                    # Encode images to base64 if they are paths
                    encoded_images = []
                    for img in images:
                        if isinstance(img, str) and os.path.exists(img):
                            encoded_images.append(encode_image(img))
                        else:
                            # Already encoded or not a path
                            encoded_images.append(img)
                    history_msg["images"] = encoded_images
                messages.insert(i + 1, history_msg)

        # Use chat with messages
        response_data = self.chat_repository.chat(
            messages=messages,
            format=None,
            system_prompt=system_prompt or self.system_prompt
        )
        return response_data

    def chat(self, message: str, session_id: str, 
                    image_path: str = None,
                    chat_history: List[Dict[str, str]] = None, 
                    system_prompt: str = None,
                    format: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Unified chat method that can handle regular chat and images.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            image_path: Optional path to an image file to include in the conversation.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.
            format: Optional JSON schema defining the structure of the expected output.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the model doesn't support the requested features.
                The dictionary includes:
                - 'message': The model's response message
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields

        Raises:
            ValueError: If the message is empty or None, or if the session_id is empty or None.
        """
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")

        # Route to the appropriate specialized method based on the parameters
        if image_path:
            return self._chat_with_image(message, image_path, session_id, chat_history, system_prompt)
        else:
            return self._chat(message, session_id, chat_history, system_prompt)
