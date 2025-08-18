from abc import abstractmethod
from typing import Dict, List, Optional, Any

from .base_service import BaseService


class BaseTextService(BaseService):
    """
    Base class for text-only services.
    Defines the common interface that all text services must implement.
    """

    def __init__(self, api_url: str, model_name: str, api_token: str = None, temperature: float = 0.6,
                 max_tokens: int = 2500, ):
        """
        Initialize a new BaseTextService.

        Args:
            api_url: The base URL of the API.
            api_token: Optional API token for authentication.
            temperature: The temperature to use for a generation.
            max_tokens: The maximum number of tokens to generate.
            model_name: The name of the model to use.

        Raises:
            ValueError: If the api_url is empty or None, or if temperature or max_tokens are invalid.
        """
        super().__init__(api_url, api_token)

        if temperature < 0:
            raise ValueError("Temperature must be non-negative")
        if max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        if not model_name:
            raise ValueError("Model name cannot be empty or None")

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = None  # System prompts should only be set at the agent level
        self.model_name = model_name

    @abstractmethod
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
        pass

    @abstractmethod
    def chat(self, message: str, session_id: str, 
                    documents: List[Dict[str, str]] = None,
                    tools: List[Dict[str, Any]] = None,
                    chat_history: List[Dict[str, str]] = None, 
                    system_prompt: str = None,
                    format: Dict[str, Any] = None,
                    stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Unified chat method that can handle regular chat, documents, and tools.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            documents: Optional list of documents to use as context.
            tools: Optional list of tools to make available to the model for this chat session.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the model doesn't support the requested features.
                The dictionary includes:
                - 'message': The model's response message
                - 'tool_calls': Any tool calls made by the model (if tools were used)
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields

        Raises:
            ValueError: If the message is empty or None, or if the session_id is empty or None.
        """
        pass
