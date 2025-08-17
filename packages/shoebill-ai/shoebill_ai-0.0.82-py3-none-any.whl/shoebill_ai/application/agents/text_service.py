from typing import Dict, List, Optional, Any

from .base_text_service import BaseTextService
from ...domain.agents.interfaces.text_service_interface import TextServiceInterface
from ...domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from ...domain.agents.interfaces.llm_generate_repository import LlmGenerateRepository
from ...domain.agents.interfaces.model_factory import ModelFactory
from ...infrastructure.agents.ollama.factories import OllamaFactory
from ...infrastructure.agents.openai.factories import OpenAIFactory


class TextService(BaseTextService, TextServiceInterface):
    """
    Implementation of a text-only service that can work with any text model.
    """

    def __init__(self, factory: OllamaFactory, temperature: float = 0.6,
                 max_tokens: int = 2500,
                 tools: List[Dict[str, Any]] = None, timeout: int = None):
        """
        Initialize a new TextService.

        Args:
            api_url: The base URL of the API.
            api_token: Optional API token for authentication.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            model_name: The name of the model to use.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
            factory: Optional model factory to use. If not provided, a factory will be created based on the model_name.

        Raises:
            ValueError: If the api_url is empty or None, or if temperature or max_tokens are invalid.
            ValueError: If chat_repository or generate_repository is None.
        """
        super().__init__(api_url=factory.api_url, api_token=factory.api_token, model_name=factory.model_name, temperature=temperature, max_tokens=max_tokens)

        # Store tools and timeout
        self.tools = tools or []
        self.timeout = timeout
        self.factory = factory


        # Use the provided factory or create one based on the model_name
        # if factory:
        #
        # else:
        #     # Check if the model is supported by Ollama
        #     if OllamaFactory.is_text_model(model_name):
        #
        #     # Check if the model is supported by OpenAI
        #     elif OpenAIFactory.is_text_model(model_name):
        #         self.factory = OpenAIFactory(
        #             api_key=api_token,  # API token is used as API key for OpenAI
        #             temperature=temperature,
        #             max_tokens=max_tokens,
        #             model_name=model_name,
        #             tools=self.tools,
        #             timeout=self.timeout
        #         )
        #     else:
        #         raise ValueError(f"Unsupported text model: {model_name}. Must be an Ollama or OpenAI text model.")

        # Store repositories
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
             system_prompt: str = None, format: Dict[str, Any] = None, stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Chat with the model.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

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
            format=format,
            system_prompt=system_prompt or self.system_prompt,
            stream=stream
        )

        return response_data

    def _chat_with_documents(self, message: str, session_id: str, documents: List[Dict[str, str]],
                           chat_history: List[Dict[str, str]] = None, 
                           system_prompt: str = None,
                           format: Dict[str, Any] = None,
                           stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Chat with the model using provided documents as context.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            documents: List of documents to use as context.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if an error occurs.
                The dictionary includes:
                - 'message': The model's response message
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields
        """
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")
        if not documents:
            raise ValueError("Documents list cannot be empty or None")

        # Format documents for the message
        docs_text = "\n\n".join([f"Document: {doc.get('title', 'Untitled')}\n{doc.get('content', '')}" 
                                for doc in documents])

        # Combine documents with the user's message
        combined_message = f"Context:\n{docs_text}\n\nUser question: {message}"

        return self.chat(
            message=combined_message,
            session_id=session_id,
            chat_history=chat_history,
            system_prompt=system_prompt or self.system_prompt,
            format=format,
            stream=stream
        )

    def _chat_with_tools(self, message: str, session_id: str, tools: List[Dict[str, Any]] = None,
                       chat_history: List[Dict[str, str]] = None, 
                       system_prompt: str = None,
                       format: Dict[str, Any] = None,
                       stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Chat with the model using provided tools.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            tools: Optional list of tools to make available to the model for this chat session.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the model doesn't support tool-based chat.
                The dictionary includes:
                - 'message': The model's response message
                - 'tool_calls': Any tool calls made by the model
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields
        """
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")

        # Use the tools provided in the method call, or fall back to the tools provided at initialization
        current_tools = tools or self.tools

        # If no tools are available, fall back to regular chat
        if not current_tools:
            return self._chat(message, session_id, chat_history, system_prompt, format, stream)

        # Create custom messages with tools
        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]

        # Add chat history if provided
        if chat_history:
            # Insert history before the current message
            for i, msg in enumerate(chat_history):
                role = msg.get("role", "user" if i % 2 == 0 else "assistant")
                content = msg.get("content", "")
                messages.insert(i + 1, {"role": role, "content": content})

        # Use chat with messages and tools
        response_data = self.chat_repository.chat(
            messages=messages,
            tools=current_tools,
            format=format,
            system_prompt=system_prompt or self.system_prompt,
            stream=stream
        )

        return response_data

    def _chat_with_documents_and_tools(self, message: str, session_id: str, documents: List[Dict[str, str]],
                                     tools: List[Dict[str, Any]] = None,
                                     chat_history: List[Dict[str, str]] = None, 
                                     system_prompt: str = None,
                                     format: Dict[str, Any] = None,
                                     stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Chat with the model using provided documents as context and tools.

        Args:
            message: The user's message.
            session_id: The ID of the chat session.
            documents: List of documents to use as context.
            tools: Optional list of tools to make available to the model for this chat session.
            chat_history: Optional chat history to include in the conversation.
            system_prompt: Optional system prompt to override the default.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the model doesn't support tool-based chat.
                The dictionary includes:
                - 'message': The model's response message
                - 'tool_calls': Any tool calls made by the model
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields
        """
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")
        if not documents:
            raise ValueError("Documents list cannot be empty or None")

        # Use the tools provided in the method call, or fall back to the tools provided at initialization
        current_tools = tools or self.tools

        # If no tools are available, fall back to regular chat with documents
        if not current_tools:
            return self._chat_with_documents(message, session_id, documents, chat_history, system_prompt, format, stream)

        # Format documents for the message
        docs_text = "\n\n".join([f"Document: {doc.get('title', 'Untitled')}\n{doc.get('content', '')}" 
                                for doc in documents])

        # Combine documents with the user's message
        combined_message = f"Context:\n{docs_text}\n\nUser question: {message}"

        # Create custom messages with document context
        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": combined_message}
        ]

        # Add chat history if provided
        if chat_history:
            # Insert history before the current message
            for i, msg in enumerate(chat_history):
                role = msg.get("role", "user" if i % 2 == 0 else "assistant")
                content = msg.get("content", "")
                messages.insert(i + 1, {"role": role, "content": content})

        # Use chat with messages and tools
        response_data = self.chat_repository.chat(
            messages=messages,
            tools=current_tools,
            format=format,
            system_prompt=system_prompt or self.system_prompt,
            stream=stream
        )

        return response_data

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
        if not message:
            raise ValueError("Message cannot be empty or None")
        if not session_id:
            raise ValueError("Session ID cannot be empty or None")

        # Use the tools provided in the method call, or fall back to the tools provided at initialization
        current_tools = tools or self.tools

        # Route to the appropriate specialized method based on the parameters
        if documents and current_tools:
            return self._chat_with_documents_and_tools(message, session_id, documents, current_tools, chat_history, system_prompt, format, stream)
        elif documents:
            return self._chat_with_documents(message, session_id, documents, chat_history, system_prompt, format, stream)
        elif current_tools:
            return self._chat_with_tools(message, session_id, current_tools, chat_history, system_prompt, format, stream)
        else:
            return self._chat(message, session_id, chat_history, system_prompt, format, stream)
