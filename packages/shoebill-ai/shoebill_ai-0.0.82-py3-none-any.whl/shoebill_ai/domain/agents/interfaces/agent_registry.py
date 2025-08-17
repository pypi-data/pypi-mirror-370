from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

from ... import BaseAgent

# Type variable for agent types
T = TypeVar('T', bound=BaseAgent)


class AgentRegistry(Generic[T], ABC):
    """
    Interface for the agent registry, which manages the collection of available agents.

    The registry can work with any agent type that inherits from BaseAgent.
    """

    @abstractmethod
    def register(self, agent: T) -> None:
        """
        Register an agent with the registry.

        Args:
            agent: The agent to register
        """
        pass

    @abstractmethod
    def unregister(self, agent_id: str) -> None:
        """
        Unregister an agent from the registry.

        Args:
            agent_id: The ID of the agent to unregister
        """
        pass

    @abstractmethod
    def get(self, agent_id: str) -> Optional[T]:
        """
        Get an agent by its ID.

        Args:
            agent_id: The ID of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[T]:
        """
        List all registered agents.

        Returns:
            A list of all registered agents
        """
        pass

    @abstractmethod
    def get_by_tags(self, tags: List[str]) -> List[T]:
        """
        Get agents by tags.

        Args:
            tags: The tags to filter by

        Returns:
            A list of agents that have all the specified tags
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[T]:
        """
        Get an agent by its name.

        Args:
            name: The name of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        pass
