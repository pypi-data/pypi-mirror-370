from abc import abstractmethod
from typing import Optional, Dict, Any

from .base_repository import BaseRepository


class LlmGenerateRepository(BaseRepository):
    """
    Repository for text generation with an LLM.
    """

    @abstractmethod
    def generate(self, user_prompt: str, system_prompt: str = None, max_tokens: int = None) -> Optional[Dict[str, Any]]:
        """
        Generate text using the LLM.

        Args:
            user_prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to use.
            max_tokens: Optional maximum number of tokens to generate.

        Returns:
            Optional[Dict[str, Any]]: The full response data, or None if the request failed.
                The dictionary includes:
                - 'response': The generated text
                - 'eval_metrics': Any evaluation metrics
                - Other model-specific fields
        """
        ...
