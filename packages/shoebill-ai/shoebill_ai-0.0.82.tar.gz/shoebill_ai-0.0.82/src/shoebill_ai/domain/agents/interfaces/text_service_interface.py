from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class TextServiceInterface(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def chat(self, message: str, session_id: str, 
             documents: List[Dict[str, str]] = None,
             tools: List[Dict[str, Any]] = None,
             chat_history: List[Dict[str, str]] = None, 
             system_prompt: str = None,
             format: Dict[str, Any] = None,
             stream: bool = False) -> Optional[Dict[str, Any]]:
        pass
