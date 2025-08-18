import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..workflow import Workflow
from ...agents.text_agent import TextAgent
from ...agents.interfaces.agent_registry import AgentRegistry

class SimpleTextWorkflow(Workflow):
    """
    A simple workflow that uses a text agent to process input text.
    """
    agent_id: Optional[str] = None
    system_prompt: str = "You are a helpful assistant."
    agent_registry: Optional[AgentRegistry] = None

    def __init__(self, 
                 workflow_id: str, 
                 name: str, 
                 description: Optional[str] = None,
                 metadata: Dict[str, Any] = None,
                 version: str = "1.0.0",
                 created_at: datetime = None,
                 updated_at: datetime = None,
                 agent_id: Optional[str] = None,
                 system_prompt: str = "You are a helpful assistant.",
                 agent_registry: Optional[AgentRegistry] = None):
        """
        Initialize a new SimpleTextWorkflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the workflow
            description: Optional description of the workflow
            metadata: Optional metadata for the workflow
            version: The version of the workflow
            created_at: The creation time of the workflow
            updated_at: The last update time of the workflow
            agent_id: Optional ID of the agent to use
            system_prompt: The system prompt to use for the agent
            agent_registry: Optional registry for retrieving agents
        """
        super().__init__(
            workflow_id=workflow_id,
            name=name,
            description=description,
            metadata=metadata or {},
            version=version,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.agent_registry = agent_registry

    async def execute(self, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the workflow with the given input data.

        Args:
            input_data: Input data containing 'text' to process

        Returns:
            Dict[str, Any]: The execution results
        """
        if not input_data or 'text' not in input_data:
            raise ValueError("Input data must contain 'text' field")

        # Get the agent
        if not self.agent_registry:
            raise ValueError("Agent registry is required")

        agent = self.agent_registry.get_text_agent(self.agent_id)

        if not agent:
            raise ValueError(f"Agent {self.agent_id} not found")

        # Process the text
        response = await agent.generate_text(
            prompt=input_data['text'],
            system_prompt=self.system_prompt
        )

        return {
            "response": response,
            "input_text": input_data['text']
        }


    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> 'SimpleTextWorkflow':
        """
        Create a workflow from a dictionary representation.

        Args:
            data: Dictionary representation of the workflow
            **kwargs: Additional arguments to pass to the constructor

        Returns:
            SimpleTextWorkflow: The created workflow
        """
        # Extract the basic workflow fields
        workflow_id = data["workflow_id"]
        name = data["name"]
        description = data.get("description")
        metadata = data.get("metadata", {})
        version = data.get("version", "1.0.0")
        created_at = datetime.fromisoformat(data.get("created_at")) if "created_at" in data else None
        updated_at = datetime.fromisoformat(data.get("updated_at")) if "updated_at" in data else None

        # Extract the specific fields for this workflow type
        agent_id = data.get("agent_id")  # Now optional
        system_prompt = data.get("system_prompt", "You are a helpful assistant.")

        # Create the workflow
        return cls(
            workflow_id=workflow_id,
            name=name,
            description=description,
            metadata=metadata,
            version=version,
            created_at=created_at,
            updated_at=updated_at,
            agent_id=agent_id,
            system_prompt=system_prompt,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the workflow
        """
        # Get the basic workflow fields
        result = super().to_dict()

        # Add the specific fields for this workflow type
        result["agent_id"] = self.agent_id
        result["system_prompt"] = self.system_prompt

        return result
