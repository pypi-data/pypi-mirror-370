from typing import Optional, List, Dict, Any

from .....domain.agents.factories.model_factory import ModelFactory
from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from .....domain.agents.interfaces.llm_generate_repository import LlmGenerateRepository
from ..repositories.ollama_chat_repository import OllamaChatRepository
from ..repositories.ollama_embed_repository import OllamaEmbeddingRepository
from ..repositories.ollama_generate_repository import OllamaGenerateRepository


class OllamaFactory(ModelFactory):
    """
    Factory for creating repositories for Ollama models.
    This factory can create repositories for any Ollama model based on its capabilities.
    """

    def __init__(self, api_url: str, temperature: float = 0.6, max_tokens: int = 2500,
                 api_token: str = None, system_prompt: str = None,
                 model_name: str = None, tools: List[Dict[str, Any]] = None,
                 timeout: Optional[int] = None):
        """
        Initialize a new OllamaFactory.

        Args:
            api_url: The base URL of the Ollama API.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            api_token: Optional API token for authentication.
            system_prompt: Optional system prompt to use for generation and chat.
            model_name: The name of the model to use.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_token = api_token
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.tools = tools or []
        self.timeout = timeout

        if not model_name:
            raise ValueError("Model name cannot be empty or None")

    def create_chat_repository(self) -> LlmChatRepository:
        """
        Creates a chat repository for the model.

        Returns:
            LlmChatRepository: A repository for chat interactions with the model.
        """
        kwargs = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_token": self.api_token
        }

        # Add system prompts if provided
        if self.system_prompt:
            kwargs["system_prompts"] = [self.system_prompt]

        # Add tools if provided
        if self.tools:
            kwargs["tools"] = self.tools

        # Add timeout if provided
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        return OllamaChatRepository(**kwargs)

    def create_generate_repository(self) -> LlmGenerateRepository:
        """
        Creates a generate repository for the model.

        Returns:
            LlmGenerateRepository: A repository for text generation with the model.
        """
        kwargs = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_token": self.api_token
        }

        # Add system prompt if provided
        if self.system_prompt:
            kwargs["system_prompt"] = self.system_prompt

        # Add timeout if provided
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        return OllamaGenerateRepository(**kwargs)

    def create_embedding_repository(self) -> Optional[LlmEmbeddingRepository]:
        """
        Creates an embedding repository for the model if it supports embeddings.

        Returns:
            Optional[LlmEmbeddingRepository]: A repository for creating embeddings with the model,
                                             or None if the model doesn't support embeddings.
        """
        kwargs = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "api_token": self.api_token
        }

        # Add timeout if provided
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        return OllamaEmbeddingRepository(**kwargs)