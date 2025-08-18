from abc import ABC, abstractmethod
from typing import Optional, List


class EmbeddingServiceInterface(ABC):
    @abstractmethod
    def embed(self, text: str) -> Optional[List[float]]:
        pass

    @abstractmethod
    def batch_embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        pass
