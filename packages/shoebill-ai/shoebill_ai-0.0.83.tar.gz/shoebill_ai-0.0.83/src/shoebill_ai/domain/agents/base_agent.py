from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BaseAgent(ABC):
    """
    Base class for all agent types.

    This abstract class defines the common interface and properties for all agent types.
    Specific agent types (TextAgent, VisionAgent, etc.) should inherit from this class.
    """
    agent_id: str
    name: str
    description: str
    service_id: str = ""
    system_prompt: Optional[str] = None
    tools: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """
        Get the agent ID.

        This property provides a more intuitive way to access the agent ID.
        It returns the same value as agent_id.

        Returns:
            str: The agent ID
        """
        return self.agent_id

    @abstractmethod
    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input data and return results.

        This method must be implemented by all agent types to handle processing requests.

        Args:
            input_data: The input data for the agent to process
            context: Optional context information

        Returns:
            Dict[str, Any]: The processing results
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "service_id": self.service_id,
            "system_prompt": self.system_prompt,
            "tools": self.tools,
            "tags": self.tags,
            "config": self.config,
            "agent_type": self.__class__.__name__
        }
