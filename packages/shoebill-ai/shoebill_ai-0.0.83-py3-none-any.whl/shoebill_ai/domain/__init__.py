"""
Domain layer for the shoebill_ai package.

This package contains domain models, interfaces, and business logic.
It defines the core abstractions and rules of the application.
"""

__all__ = [
    # Agent classes
    'BaseAgent',
    'EmbeddingAgent',
    'MultimodalAgent',
    'TextAgent',
    'VisionAgent',

    # Agent interfaces
    'AgentRegistry',
    'ModelFactory',
    'LlmChatRepository',
    'LlmEmbeddingRepository',
    'LlmGenerateRepository',
]

# Import agent classes
from .agents.base_agent import BaseAgent
from .agents.embedding_agent import EmbeddingAgent
from .agents.multimodal_agent import MultimodalAgent
from .agents.text_agent import TextAgent
from .agents.vision_agent import VisionAgent

# Import agent interfaces
from .agents.interfaces.agent_registry import AgentRegistry
from .agents.interfaces.model_factory import ModelFactory
from .agents.interfaces.llm_chat_repository import LlmChatRepository
from .agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from .agents.interfaces.llm_generate_repository import LlmGenerateRepository
