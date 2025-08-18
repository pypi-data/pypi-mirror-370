from typing import Optional, List, Dict, Any

from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .base_ollama_repository import BaseOllamaRepository
from ..models.ollama_chat_message import OllamaChatMessage
from ..models.ollama_chat_session import OllamaChatSession


class OllamaChatRepository(BaseOllamaRepository, LlmChatRepository):
    """
    Repository for chat interactions using the Ollama API.
    """

    def __init__(self, api_url: str, model_name: str, system_prompts: list[str] = None, 
                 temperature: float = None, seed: int = None, api_token: str = None,
                 tools: List[Dict[str, Any]] = None, timeout: int = None, max_tokens: int = None):
        """
        Initialize a new OllamaChatRepository.

        Args:
            api_url: The base URL of the Ollama API.
            model_name: The name of the model to use.
            system_prompts: Optional list of system prompts to use for the chat.
            temperature: The temperature to use for generation.
            seed: Optional seed for reproducible generation.
            api_token: Optional API token for authentication.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
            max_tokens: The maximum number of tokens to generate.
        """
        super().__init__(api_url, model_name, api_token, timeout)
        self.temperature = temperature
        self.seed = seed
        self.system_prompts = system_prompts or []
        self.tools = tools or []
        self.max_tokens = max_tokens

    def chat(self, user_message: str = None, session_id: str = None, chat_history: List[dict] = None, 
             format: Dict[str, Any] = None, system_prompt: str = None, 
             messages: List[Any] = None, tools: List[Dict[str, Any]] = None,
             stream: bool = False) -> Optional[str]:
        """
        Chat with the model using the Ollama API.

        This is the main method for chatting with the model. It can handle simple chat scenarios,
        custom messages, and tools.

        Args:
            user_message: The user's message. Can be a string or a dictionary with 'content' and optional 'images'.
                         Not required if messages is provided.
            session_id: The ID of the chat session. Not required if messages is provided.
            chat_history: Optional chat history to include in the conversation.
                         Each message can include 'role', 'content', and optional 'images'.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            messages: Optional custom list of messages to send to the model. If provided, user_message,
                     session_id, and chat_history are ignored.
            tools: Optional list of tools to make available to the model for this chat session.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[str]: The model's response, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        # If messages is provided, use it directly with the appropriate method
        if messages is not None:
            logger.info(f"OllamaChatRepository: Using provided messages list with {len(messages)} messages")

            # If tools are provided, use _chat_with_messages_and_tools
            if tools is not None:
                logger.info(f"OllamaChatRepository: Using provided tools with {len(tools)} tools")
                return self._chat_with_messages_and_tools(messages, tools, format, system_prompt, stream)
            else:
                # Otherwise, use _chat_with_messages
                return self._chat_with_messages(messages, format, system_prompt, stream)

        # If no messages are provided, we need user_message and session_id
        if user_message is None or session_id is None:
            logger.error("OllamaChatRepository: user_message and session_id are required when messages is not provided")
            return None

        logger.info(f"OllamaChatRepository: Starting chat with session_id {session_id}")
        # Handle both string and dictionary user messages for logging
        if isinstance(user_message, str):
            logger.debug(f"OllamaChatRepository: User message: {user_message[:50]}...")
        else:
            logger.debug(f"OllamaChatRepository: User message: {user_message}")
        logger.debug(f"OllamaChatRepository: Chat history length: {len(chat_history) if chat_history else 0}")

        # Start with system prompts and user message
        messages = []

        # Use provided system_prompt if available, otherwise use the default system_prompts
        if system_prompt:
            messages.append(OllamaChatMessage("system", system_prompt))
            logger.debug(f"OllamaChatRepository: Added provided system prompt: {system_prompt[:50]}...")
        else:
            for prompt in self.system_prompts:
                messages.append(OllamaChatMessage("system", prompt))
                # Handle both string and dictionary system prompts for logging
                if isinstance(prompt, str):
                    logger.debug(f"OllamaChatRepository: Added system prompt: {prompt[:50]}...")
                else:
                    logger.debug(f"OllamaChatRepository: Added system prompt: {prompt}")

        # Add chat history if provided
        if chat_history:
            logger.info(f"OllamaChatRepository: Adding {len(chat_history)} messages from chat history")
            for message in chat_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                images = message.get("images", None)

                # Create the chat message with images if they exist
                if images:
                    chat_msg = OllamaChatMessage(role, content, images)
                    logger.debug(f"OllamaChatRepository: Added {role} message from history with {len(images)} images")
                else:
                    chat_msg = OllamaChatMessage(role, content)
                    # Handle both string and dictionary content for logging
                    if isinstance(content, str):
                        logger.debug(f"OllamaChatRepository: Added {role} message from history: {content[:50]}...")
                    else:
                        logger.debug(f"OllamaChatRepository: Added {role} message from history: {content}")

                messages.append(chat_msg)

        # Add the current user message
        # Check if user_message is a dictionary with content and images
        if isinstance(user_message, dict):
            content = user_message.get("content", "")
            images = user_message.get("images", None)
            if images:
                messages.append(OllamaChatMessage("user", content, images))
                logger.info(f"OllamaChatRepository: Added current user message with {len(images)} images")
            else:
                messages.append(OllamaChatMessage("user", content))
                logger.info(f"OllamaChatRepository: Added current user message")
        else:
            # User message is a string
            messages.append(OllamaChatMessage("user", user_message))
            logger.info(f"OllamaChatRepository: Added current user message")

        # Create a session
        session = OllamaChatSession(session_id, messages)
        logger.info(f"OllamaChatRepository: Created chat session with {len(session.messages)} messages")

        # If tools are provided, use _chat_with_messages_and_tools
        if tools is not None:
            logger.info(f"OllamaChatRepository: Using provided tools with {len(tools)} tools")
            result = self._chat_with_messages_and_tools(session.messages, tools, format, system_prompt, stream)
        else:
            # Otherwise, use _chat_with_messages
            logger.info(f"OllamaChatRepository: Calling _chat_with_messages")
            result = self._chat_with_messages(session.messages, format, system_prompt, stream)

        if result:
            logger.info(f"OllamaChatRepository: Received response")
            logger.debug(f"OllamaChatRepository: Response: {str(result)[:100]}...")
        else:
            logger.error(f"OllamaChatRepository: Failed to get response")

        return result

    def _chat_with_messages(self, messages: List[Any], format: Dict[str, Any] = None, system_prompt: str = None, stream: bool = False) -> Optional[str]:
        """
        Private method to chat with the model using a custom list of messages.

        This method allows for more flexibility in message formatting, such as including
        document messages or other special message types.

        Args:
            messages: The list of messages to send to the model. Each message should have
                     'role' and 'content' attributes or keys.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[str]: The model's response, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OllamaChatRepository: Starting chat_with_messages with {len(messages)} messages")

        # If system_prompt is provided, check if we need to add it or replace an existing system message
        if system_prompt:
            logger.debug(f"OllamaChatRepository: Using provided system prompt: {system_prompt[:50]}...")

            # Create a new messages list with the system prompt at the beginning
            new_messages = []
            system_message_added = False

            # Check if there's already a system message
            for msg in messages:
                role = getattr(msg, "role", "unknown") if hasattr(msg, "role") else msg.get("role", "unknown")

                # If this is the first system message, replace it with our new system prompt
                if role == "system" and not system_message_added:
                    if hasattr(msg, "role"):
                        # It's an object with attributes
                        msg.content = system_prompt
                    else:
                        # It's a dictionary
                        msg["content"] = system_prompt
                    system_message_added = True

                new_messages.append(msg)

            # If no system message was found, add one at the beginning
            if not system_message_added:
                new_messages.insert(0, OllamaChatMessage("system", system_prompt))

            messages = new_messages

        # Log the first few messages to help with debugging
        for i, msg in enumerate(messages[:3]):  # Log only first 3 messages to avoid excessive logging
            role = getattr(msg, "role", "unknown") if hasattr(msg, "role") else msg.get("role", "unknown")
            content = getattr(msg, "content", "") if hasattr(msg, "content") else msg.get("content", "")
            # Handle both string and dictionary content for logging
            if isinstance(content, str):
                logger.debug(f"OllamaChatRepository: Message {i+1} - Role: {role}, Content: {content[:50]}...")
            else:
                logger.debug(f"OllamaChatRepository: Message {i+1} - Role: {role}, Content: {content}")

        if len(messages) > 3:
            logger.debug(f"OllamaChatRepository: ... and {len(messages) - 3} more messages")

        # Call the Ollama API
        return self._call_ollama_api(messages, format, stream)


    def _chat_with_messages_and_tools(self, messages: List[Any], tools: List[Dict[str, Any]] = None, format: Dict[str, Any] = None, system_prompt: str = None, stream: bool = False) -> Optional[str]:
        """
        Private method to chat with the model using a custom list of messages and specific tools.

        This method allows for more flexibility in message formatting and tool usage,
        without modifying the repository's default tools.

        Args:
            messages: The list of messages to send to the model. Each message should have
                     'role' and 'content' attributes or keys.
            tools: Optional list of tools to make available to the model for this chat session.
                  If None, uses the repository's default tools.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[str]: The model's response, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OllamaChatRepository: Starting chat_with_messages_and_tools with {len(messages)} messages")

        if system_prompt:
            logger.debug(f"OllamaChatRepository: Using provided system prompt: {system_prompt[:50]}...")

            # If system_prompt is provided, check if we need to add it or replace an existing system message
            new_messages = []
            system_message_added = False

            # Check if there's already a system message
            for msg in messages:
                role = getattr(msg, "role", "unknown") if hasattr(msg, "role") else msg.get("role", "unknown")

                # If this is the first system message, replace it with our new system prompt
                if role == "system" and not system_message_added:
                    if hasattr(msg, "role"):
                        # It's an object with attributes
                        msg.content = system_prompt
                    else:
                        # It's a dictionary
                        msg["content"] = system_prompt
                    system_message_added = True

                new_messages.append(msg)

            # If no system message was found, add one at the beginning
            if not system_message_added:
                new_messages.insert(0, OllamaChatMessage("system", system_prompt))

            messages = new_messages

        if tools:
            logger.info(f"OllamaChatRepository: Using {len(tools)} custom tools for this chat session")

        # Store original tools
        original_tools = self.tools

        try:
            # Temporarily update tools if provided
            if tools is not None:
                self.tools = tools

            # Call the Ollama API with the updated tools
            return self._call_ollama_api(messages, format, stream)
        finally:
            # Restore original tools
            self.tools = original_tools


    def _format_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """
        Format messages in the standard Ollama API format.

        Args:
            messages: The messages to format. Each message should have 'role' and 'content' attributes.
                     May also include 'images' for multimodal models.

        Returns:
            List[Dict[str, Any]]: The formatted messages.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OllamaChatRepository: Formatting {len(messages)} messages in standard format")

        result = []
        for i, message in enumerate(messages):
            # Handle OllamaChatMessage objects
            if hasattr(message, 'to_dict'):
                logger.debug(f"OllamaChatRepository: Message {i+1} is an OllamaChatMessage object")
                msg_dict = message.to_dict()

                # If content is a dictionary with text and image, extract the text
                if isinstance(msg_dict['content'], dict) and 'text' in msg_dict['content']:
                    msg_dict['content'] = msg_dict['content']['text']
                    logger.debug(f"OllamaChatRepository: Extracted text from vision content")

                result.append(msg_dict)
            # Handle dict-like objects
            elif hasattr(message, 'get'):
                logger.debug(f"OllamaChatRepository: Message {i+1} is a dict-like object")
                role = message.get("role", "user")
                content = message.get("content", "")
                images = message.get("images", None)

                # Extract text from dictionary content
                if isinstance(content, dict) and 'text' in content:
                    content = content['text']
                    logger.debug(f"OllamaChatRepository: Extracted text from dictionary content")

                # Create the formatted message
                formatted_msg = {
                    "role": role,
                    "content": content
                }

                # Add images if they exist
                if images:
                    formatted_msg["images"] = images
                    logger.debug(f"OllamaChatRepository: Added {len(images)} images to message")

                result.append(formatted_msg)
                logger.debug(f"OllamaChatRepository: Added message with role '{role}' and content: {str(content)[:50]}...")
            # Handle objects with role and content attributes
            else:
                logger.debug(f"OllamaChatRepository: Message {i+1} is an object with attributes")
                role = getattr(message, "role", "user")
                content = getattr(message, "content", "")
                images = getattr(message, "images", None) if hasattr(message, "images") else None

                # Extract text from dictionary content
                if isinstance(content, dict) and 'text' in content:
                    content = content['text']
                    logger.debug(f"OllamaChatRepository: Extracted text from dictionary content")

                # Create the formatted message
                formatted_msg = {
                    "role": role,
                    "content": content
                }

                # Add images if they exist
                if images:
                    formatted_msg["images"] = images
                    logger.debug(f"OllamaChatRepository: Added {len(images)} images to message")

                result.append(formatted_msg)
                logger.debug(f"OllamaChatRepository: Added message with role '{role}' and content: {str(content)[:50]}...")

        logger.info(f"OllamaChatRepository: Formatted {len(result)} messages in standard format")
        return result

    def _call_ollama_api(self, messages: List[Any], format: Dict[str, Any] = None, stream: bool = False) -> Optional[str]:
        """
        Call the Ollama API with the given messages using the ollama-python library.

        Args:
            messages: The messages to send to the API. Each message should have 'role' and 'content' attributes.
                     May also include 'images' for multimodal models.
            format: Optional JSON schema defining the structure of the expected output.
            stream: Whether to stream the response from the API.

        Returns:
            Optional[str]: The model's response, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OllamaChatRepository: Preparing chat request for model {self.model_name}")

        # Format messages for the ollama-python library
        formatted_messages = []

        # Format messages for the ollama-python library
        for msg in messages:
            role = getattr(msg, "role", None) if hasattr(msg, "role") else msg.get("role", None)
            content = getattr(msg, "content", None) if hasattr(msg, "content") else msg.get("content", None)

            # Get images if available
            images = getattr(msg, "images", None) if hasattr(msg, "images") else msg.get("images", None)

            # Skip messages with missing role or content
            if not role or content is None:
                continue

            # Create the formatted message
            formatted_msg = {
                "role": role,
                "content": content
            }

            # Handle content that is a dictionary but not in the expected format
            if isinstance(content, dict) and 'text' not in content:
                # Convert dictionary to JSON string
                import json
                formatted_msg["content"] = json.dumps(content)
                logger.debug(f"OllamaChatRepository: Converted dictionary content to JSON string")

            # Add images if they exist
            if images:
                formatted_msg["images"] = images
                logger.debug(f"OllamaChatRepository: Added {len(images)} images to message")

            formatted_messages.append(formatted_msg)
            logger.debug(f"OllamaChatRepository: Added {role} message: {str(formatted_msg['content'])[:50]}...")

        # Create the payload for the ollama-python library
        payload = {
            "model": self.model_name,
            "stream": stream,
            "messages": formatted_messages
        }

        # Add temperature, seed, and max_tokens if provided
        if self.temperature is not None:
            payload["temperature"] = self.temperature  # Use float value directly
            logger.debug(f"OllamaChatRepository: Using temperature {self.temperature}")
        if self.seed:
            payload["seed"] = self.seed  # Use integer value directly
            logger.debug(f"OllamaChatRepository: Using seed {self.seed}")
        if self.max_tokens:
            payload["num_ctx"] = self.max_tokens  # Use integer value directly
            logger.debug(f"OllamaChatRepository: Using max tokens {self.max_tokens}")

        # Add tools if provided
        if self.tools:
            payload["tools"] = self.tools
            logger.debug(f"OllamaChatRepository: Using {len(self.tools)} tools")

        # Add format if provided
        if format:
            payload["format"] = f"{format}"
            logger.debug(f"OllamaChatRepository: Using format schema for structured output")

        # Always use the chat endpoint
        endpoint = "chat"
        logger.info(f"OllamaChatRepository: Sending request to {endpoint} endpoint")

        # Call the API endpoint using the ollama-python library
        response_data = self.http_client.post(endpoint, payload)
        if response_data:
            # Return the full response data
            logger.info("OllamaChatRepository: Received response from API")

            # Extract the message content for logging
            message_content = response_data.get("message", {}).get("content", "")
            logger.debug(f"OllamaChatRepository: Message content: {message_content[:100]}...")

            # Log other fields in the response
            eval_metrics = response_data.get("eval_metrics", {})
            if eval_metrics:
                logger.debug(f"OllamaChatRepository: Eval metrics: {eval_metrics}")

            # Return the full response data without cleaning
            return response_data

        logger.error("OllamaChatRepository: Failed to get response from API")
        return None
