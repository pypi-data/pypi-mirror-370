"""
shoebill_ai package for interacting with LLM models.

This package provides a high-level API for interacting with LLM models.
Users should import from this package, not from the application, domain, or infrastructure layers directly.
"""

__all__ = [
    # Main orchestration class
    'AgentOrchestrator',

    # Agent services
    'EmbeddingService', 'TextService', 'MultimodalService', 'VisionService',

    # Workflow services
    'WorkflowService', 'WorkflowQueueService'
]

from .application.agents.embedding_service import EmbeddingService
from .application.agents.multimodal_service import MultimodalService
from .application.agents.text_service import TextService
from .application.agents.vision_service import VisionService
from .application.workflows import AgentOrchestrator, WorkflowService, WorkflowQueueService
