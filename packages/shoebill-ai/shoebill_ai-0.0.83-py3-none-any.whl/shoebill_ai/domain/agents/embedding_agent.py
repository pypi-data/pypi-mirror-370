import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent
from .interfaces.embedding_service_interface import EmbeddingServiceInterface


@dataclass
class EmbeddingAgent(BaseAgent):
    """
    An agent that wraps an EmbeddingServiceInterface to provide embedding capabilities.

    This agent directly uses the service's methods for processing requests,
    eliminating the need for an intermediate AgentService.
    """
    service: EmbeddingServiceInterface = field(default=None, repr=False, compare=False)

    @classmethod
    def create(cls, 
               name: str, 
               description: str,
               service: EmbeddingServiceInterface,
               tags: List[str] = None,
               config: Dict[str, Any] = None) -> 'EmbeddingAgent':
        """
        Create a new EmbeddingAgent with an EmbeddingServiceInterface.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            service: An implementation of EmbeddingServiceInterface
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent

        Returns:
            The created EmbeddingAgent
        """

        # Create and return the EmbeddingAgent
        return cls(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=service,
            system_prompt=None,  # Embedding service doesn't use system prompts
            tools=[],  # Embedding service doesn't use tools
            tags=tags or [],
            config=config or {}
        )

    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input data and return results.

        This method determines which EmbeddingService method to call based on the input data.

        Args:
            input_data: The input data for the agent to process
            context: Optional context information

        Returns:
            Dict[str, Any]: The processing results
        """
        # Extract relevant parameters from input_data
        text = input_data.get('text', input_data.get('message', input_data.get('query', '')))
        batch = input_data.get('batch', False)

        # Process based on whether this is a batch request or not
        if batch and isinstance(text, list):
            # Use batch_embed for lists of text
            embeddings = self.service.batch_embed(text)
            result = {'embeddings': embeddings}
        else:
            # Use embed for single text
            embedding = self.service.embed(text)
            result = {'embedding': embedding}

        # Add agent information to the result
        result['agent_id'] = self.agent_id
        result['agent_name'] = self.name

        return result

    def embed(self, text: str) -> List[float]:
        """
        Create an embedding for the given text.

        This method directly calls the EmbeddingService's embed method.

        Args:
            text: The text to create an embedding for

        Returns:
            List[float]: The embedding vector
        """
        return self.service.embed(text)

    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts in a single batch.

        This method directly calls the EmbeddingService's batch_embed method.

        Args:
            texts: List of texts to create embeddings for

        Returns:
            List[List[float]]: List of embedding vectors
        """
        return self.service.batch_embed(texts)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        base_dict = super().to_dict()
        base_dict.update({
            "model_name": self.service.model_name,
            "api_url": self.service.api_url
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any], service: EmbeddingServiceInterface) -> 'EmbeddingAgent':
        """
        Create an EmbeddingAgent from a dictionary representation.

        Args:
            data: Dictionary representation of the agent
            service: An implementation of EmbeddingServiceInterface

        Returns:
            EmbeddingAgent: The created agent
        """

        # Create and return the EmbeddingAgent
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            description=data["description"],
            service=service,
            system_prompt=None,  # Embedding service doesn't use system prompts
            tools=[],  # Embedding service doesn't use tools
            tags=data.get("tags", []),
            config=data.get("config", {})
        )
