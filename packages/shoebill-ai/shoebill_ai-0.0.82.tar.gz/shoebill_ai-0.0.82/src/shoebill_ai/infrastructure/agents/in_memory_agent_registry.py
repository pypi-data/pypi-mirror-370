import logging
from typing import Dict, List, Optional, TypeVar, Generic

from ...domain.agents.base_agent import BaseAgent
from ...domain.agents.interfaces.agent_registry import AgentRegistry

# Type variable for agent types
T = TypeVar('T', bound=BaseAgent)


class InMemoryAgentRegistry(AgentRegistry[T], Generic[T]):
    """
    In-memory implementation of the AgentRegistry interface.

    This implementation stores agents in memory and is suitable for testing and development.
    It can work with any agent type that inherits from BaseAgent.
    """

    def __init__(self):
        """
        Initialize the in-memory agent registry.
        """
        self._agents: Dict[str, T] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, agent: T) -> None:
        """
        Register an agent with the registry.

        Args:
            agent: The agent to register
        """
        self.logger.info(f"Registering agent with ID: {agent.agent_id}")
        self.logger.debug(f"Agent details: {agent}")
        self._agents[agent.agent_id] = agent
        self.logger.info(f"Agent {agent.agent_id} registered successfully")

    def unregister(self, agent_id: str) -> None:
        """
        Unregister an agent from the registry.

        Args:
            agent_id: The ID of the agent to unregister
        """
        self.logger.info(f"Unregistering agent with ID: {agent_id}")
        if agent_id in self._agents:
            del self._agents[agent_id]
            self.logger.info(f"Agent {agent_id} unregistered successfully")
        else:
            self.logger.warning(f"Attempted to unregister non-existent agent with ID: {agent_id}")

    def get(self, agent_id: str) -> Optional[T]:
        """
        Get an agent by its ID.

        Args:
            agent_id: The ID of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        self.logger.info(f"Getting agent with ID: {agent_id}")
        agent = self._agents.get(agent_id)
        if agent:
            self.logger.info(f"Found agent with ID: {agent_id}")
            self.logger.debug(f"Agent details: {agent}")
        else:
            self.logger.info(f"Agent with ID {agent_id} not found")
        return agent

    def list_agents(self) -> List[T]:
        """
        List all registered agents.

        Returns:
            A list of all registered agents
        """
        self.logger.info("Listing all registered agents")
        agents = list(self._agents.values())
        self.logger.info(f"Found {len(agents)} registered agents")
        self.logger.debug(f"Agent IDs: {[agent.agent_id for agent in agents]}")
        return agents

    def get_by_tags(self, tags: List[str]) -> List[T]:
        """
        Get agents by tags.

        Args:
            tags: The tags to filter by

        Returns:
            A list of agents that have all the specified tags
        """
        self.logger.info(f"Getting agents with tags: {tags}")

        if not tags:
            self.logger.info("Empty tags list provided, returning empty result")
            return []

        result = []
        for agent in self._agents.values():
            # Check if all specified tags are in the agent's tags
            if all(tag in agent.tags for tag in tags):
                result.append(agent)

        self.logger.info(f"Found {len(result)} agents matching tags: {tags}")
        self.logger.debug(f"Matching agent IDs: {[agent.agent_id for agent in result]}")
        return result

    def get_by_name(self, name: str) -> Optional[T]:
        """
        Get an agent by its name.

        Args:
            name: The name of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        self.logger.info(f"Getting agent with name: {name}")

        for agent in self._agents.values():
            if agent.name == name:
                self.logger.info(f"Found agent with name: {name}, ID: {agent.agent_id}")
                self.logger.debug(f"Agent details: {agent}")
                return agent

        self.logger.info(f"Agent with name {name} not found")
        return None
