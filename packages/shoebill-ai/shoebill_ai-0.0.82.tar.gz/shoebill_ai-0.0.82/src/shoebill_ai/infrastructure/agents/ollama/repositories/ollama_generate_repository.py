from typing import Optional, Dict, Any

from .....domain.agents.interfaces.llm_generate_repository import LlmGenerateRepository
from .base_ollama_repository import BaseOllamaRepository



class OllamaGenerateRepository(BaseOllamaRepository, LlmGenerateRepository):
    """
    Repository for generating text using the Ollama API.
    """

    def __init__(self, api_url: str, model_name: str, system_prompt: str = None, 
                 temperature: float = None, seed: int = None, max_tokens: int = 5000, 
                 api_token: str = None, timeout: int = None):
        """
        Initialize a new OllamaGenerateRepository.

        Args:
            api_url: The base URL of the Ollama API.
            model_name: The name of the model to use.
            system_prompt: Optional system prompt to use for generation.
            temperature: The temperature to use for generation.
            seed: Optional seed for reproducible generation.
            max_tokens: The maximum number of tokens to generate.
            api_token: Optional API token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        super().__init__(api_url, model_name, api_token, timeout)
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.seed = seed
        self.max_tokens = max_tokens


    def generate(self, user_prompt: str, system_prompt: str = None, max_tokens: int = None) -> Optional[Dict[str, Any]]:
        """
        Generate text using the Ollama API via the ollama-python library.

        Args:
            user_prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to override the default.
            max_tokens: Optional maximum number of tokens to generate.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"OllamaGenerateRepository: Preparing generate request for model {self.model_name}")
        logger.debug(f"OllamaGenerateRepository: User prompt: {user_prompt[:50]}...")

        system_prompt = system_prompt or self.system_prompt
        if system_prompt:
            logger.debug(f"OllamaGenerateRepository: System prompt: {system_prompt[:50]}...")

        # Prepare the payload for the ollama-python library
        payload = {
            "model": self.model_name,
            "stream": False,
            "num_ctx": self.max_tokens  # Use integer value directly
        }
        logger.debug(f"OllamaGenerateRepository: Using max tokens: {self.max_tokens}")

        # Add common parameters
        if self.seed:
            payload["seed"] = self.seed  # Use integer value directly
            logger.debug(f"OllamaGenerateRepository: Using seed: {self.seed}")
        if self.temperature is not None:
            payload["temperature"] = self.temperature  # Use float value directly
            logger.debug(f"OllamaGenerateRepository: Using temperature: {self.temperature}")
        if max_tokens:
            payload["num_ctx"] = max_tokens  # Use integer value directly
            logger.debug(f"OllamaGenerateRepository: Overriding max tokens: {max_tokens}")

        # Use standard formatting
        payload["prompt"] = user_prompt
        if system_prompt:
            payload["system"] = system_prompt

        logger.debug(f"OllamaGenerateRepository: Using prompt: {user_prompt[:50]}...")

        endpoint = "generate"
        logger.info(f"OllamaGenerateRepository: Sending request to {endpoint} endpoint")
        logger.debug(f"OllamaGenerateRepository: Payload: {payload}")

        # Call the generate endpoint using the ollama-python library
        response_data = self.http_client.post(endpoint, payload)
        if response_data:
            logger.info("OllamaGenerateRepository: Received response from API")

            # Extract the response content for logging
            response_content = response_data.get("response", "")
            logger.debug(f"OllamaGenerateRepository: Response content: {response_content[:100]}...")

            # Log other fields in the response
            eval_metrics = response_data.get("eval_metrics", {})
            if eval_metrics:
                logger.debug(f"OllamaGenerateRepository: Eval metrics: {eval_metrics}")

            # Return the full response data without cleaning
            return response_data

        logger.error("OllamaGenerateRepository: Failed to get response from API")
        return None
