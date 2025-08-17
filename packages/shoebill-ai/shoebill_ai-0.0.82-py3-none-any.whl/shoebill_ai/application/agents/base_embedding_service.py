from abc import abstractmethod
from typing import List, Optional

from .base_service import BaseService

class BaseEmbeddingService(BaseService):
    """
    Base class for embedding services.
    Defines the common interface that all embedding services must implement.
    """
    
    @abstractmethod
    def embed(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for the given text.
        
        Args:
            text: The text to create an embedding for.
            
        Returns:
            Optional[List[float]]: The embedding vector, or None if an error occurs.
            
        Raises:
            ValueError: If the text is empty or None.
        """
        pass
    
    def batch_embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Create embeddings for multiple texts in a single batch.
        Default implementation processes each text individually.
        
        Args:
            texts: List of texts to create embeddings for.
            
        Returns:
            Optional[List[List[float]]]: List of embedding vectors, or None if an error occurs.
            
        Raises:
            ValueError: If the texts list is empty or None.
        """
        if not texts:
            raise ValueError("Texts list cannot be empty or None")
            
        # Filter out empty texts
        valid_texts = [text for text in texts if text]
        if not valid_texts:
            raise ValueError("All texts in the list are empty")
            
        # Process each text individually
        # Subclasses can override this with more efficient batch processing
        embeddings = []
        for text in valid_texts:
            embedding = self.embed(text)
            if embedding is None:
                return None  # If any embedding fails, return None
            embeddings.append(embedding)
            
        return embeddings