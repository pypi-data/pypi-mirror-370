from typing import Optional, List
import logging

from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from .base_ollama_repository import BaseOllamaRepository

logger = logging.getLogger(__name__)


class OllamaEmbeddingRepository(BaseOllamaRepository, LlmEmbeddingRepository):
    """
    Repository for creating embeddings using the Ollama API.
    """

    def __init__(self, api_url: str, model_name: str, api_token: str = None, timeout: int = None):
        """
        Initialize a new OllamaEmbeddingRepository.

        Args:
            api_url: The base URL of the Ollama API.
            model_name: The name of the model to use.
            api_token: Optional API token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        super().__init__(api_url, model_name, api_token, timeout)

    def embed(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for the given text using the Ollama API via the ollama-python library.

        Args:
            text: The text to create an embedding for.

        Returns:
            Optional[List[float]]: The embedding vector, or None if the request failed.
        """
        payload = {
            "model": self.model_name,
            "prompt": text
        }

        logger.info(f"Creating embedding with model {self.model_name}")
        logger.debug(f"Text for embedding: {text[:50]}...")

        # Call the embeddings endpoint using the ollama-python library
        response_data = self.http_client.post("embeddings", payload)
        if response_data:
            embedding = response_data.get("embedding")
            if embedding:
                logger.info("Embedding created successfully")
                logger.debug(f"Embedding vector length: {len(embedding)}")
                return embedding
            else:
                logger.error("Embedding response did not contain embedding data")
        else:
            logger.error("Failed to get response from embeddings API")

        return None
