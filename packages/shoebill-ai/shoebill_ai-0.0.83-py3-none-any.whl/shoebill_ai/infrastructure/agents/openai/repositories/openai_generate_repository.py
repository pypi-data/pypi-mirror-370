from typing import Optional, Dict, Any

from .....domain.agents.interfaces.llm_generate_repository import LlmGenerateRepository
from .base_openai_repository import BaseOpenAIRepository


class OpenAIGenerateRepository(BaseOpenAIRepository, LlmGenerateRepository):
    """
    Repository for generating text using the OpenAI API.
    """

    def __init__(self, api_key: str, model_name: str, system_prompt: str = None, 
                 temperature: float = None, max_tokens: int = 2000, 
                 organization: str = None, timeout: int = None):
        """
        Initialize a new OpenAIGenerateRepository.

        Args:
            api_key: The API key for authentication.
            model_name: The name of the model to use.
            system_prompt: Optional system prompt to use for generation.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            organization: Optional organization ID for API requests.
            timeout: Optional timeout in seconds for API requests.
        """
        super().__init__(api_key, model_name, organization, timeout)
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, user_prompt: str, system_prompt: str = None, max_tokens: int = None) -> Optional[Dict[str, Any]]:
        """
        Generate text using the OpenAI API.

        Args:
            user_prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to override the default.
            max_tokens: Optional maximum number of tokens to generate.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OpenAIGenerateRepository: Preparing generate request for model {self.model_name}")
        logger.debug(f"OpenAIGenerateRepository: User prompt: {user_prompt[:50]}...")

        system_prompt = system_prompt or self.system_prompt
        if system_prompt:
            logger.debug(f"OpenAIGenerateRepository: System prompt: {system_prompt[:50]}...")

        # For OpenAI, we'll use the chat completions API for generation
        # Create a list of messages with system and user messages
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": user_prompt})

        # Prepare the payload for the OpenAI API
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }

        # Add common parameters
        if self.temperature is not None:
            payload["temperature"] = self.temperature
            logger.debug(f"OpenAIGenerateRepository: Using temperature: {self.temperature}")
        if max_tokens or self.max_tokens:
            payload["max_tokens"] = max_tokens or self.max_tokens
            logger.debug(f"OpenAIGenerateRepository: Using max tokens: {max_tokens or self.max_tokens}")

        logger.debug(f"OpenAIGenerateRepository: Using prompt: {user_prompt[:50]}...")

        endpoint = "chat"
        logger.info(f"OpenAIGenerateRepository: Sending request to {endpoint} endpoint")
        logger.debug(f"OpenAIGenerateRepository: Payload: {payload}")

        # Call the chat endpoint using the OpenAI client
        response_data = self.http_client.post(endpoint, payload)
        if response_data:
            logger.info("OpenAIGenerateRepository: Received response from API")

            # Extract the response content for logging
            response_content = response_data.get("message", {}).get("content", "")
            logger.debug(f"OpenAIGenerateRepository: Response content: {response_content[:100]}...")

            # Format the response to match the expected structure for generate
            # The generate method is expected to return a dict with a 'response' key
            formatted_response = {
                "response": response_content
            }

            # Return the formatted response
            return formatted_response

        logger.error("OpenAIGenerateRepository: Failed to get response from API")
        return None