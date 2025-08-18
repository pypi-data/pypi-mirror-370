import uuid
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class WorkflowExecutionResult:
    """Represents the result of a workflow execution."""
    execution_id: str
    workflow_id: str
    status: str  # "completed", "failed", "cancelled"
    start_time: float
    end_time: Optional[float] = None
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None
    error_message: Optional[str] = None

    @property
    def execution_time(self) -> float:
        """Get the execution time in seconds."""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time


@dataclass
class Workflow(ABC):
    """
    Abstract base class for workflows.

    Users can extend this class to create their own workflows by implementing
    the execute method.
    """
    workflow_id: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def id(self) -> str:
        """
        Get the workflow ID.

        This property provides a more intuitive way to access the workflow ID.
        It returns the same value as workflow_id.

        Returns:
            str: The workflow ID
        """
        return self.workflow_id


    @abstractmethod
    async def execute(self, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the workflow with the given input data.

        Args:
            input_data: Optional input data for the workflow

        Returns:
            Dict[str, Any]: The execution results
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the workflow
        """
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> 'Workflow':
        """
        Create a workflow from a dictionary representation.

        This method must be implemented by subclasses to properly deserialize
        their specific attributes.

        Args:
            data: Dictionary representation of the workflow
            **kwargs: Additional arguments to pass to the constructor

        Returns:
            Workflow: The created workflow
        """
        raise NotImplementedError("Subclasses must implement from_dict")
