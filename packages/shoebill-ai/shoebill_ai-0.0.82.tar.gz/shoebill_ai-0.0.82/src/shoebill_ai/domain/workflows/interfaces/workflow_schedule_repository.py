from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ...workflows.workflow_schedule import WorkflowSchedule

class WorkflowScheduleRepository(ABC):
    """
    Interface for storing and retrieving workflow schedules.
    """
    
    @abstractmethod
    def save(self, schedule: WorkflowSchedule) -> None:
        """
        Save a workflow schedule.
        
        Args:
            schedule: The schedule to save
        """
        pass
    
    @abstractmethod
    def get(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """
        Get a workflow schedule by ID.
        
        Args:
            schedule_id: The ID of the schedule to retrieve
            
        Returns:
            The schedule if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, schedule_id: str) -> bool:
        """
        Delete a workflow schedule.
        
        Args:
            schedule_id: The ID of the schedule to delete
            
        Returns:
            True if the schedule was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def list_schedules(self, workflow_id: Optional[str] = None) -> Dict[str, WorkflowSchedule]:
        """
        List all workflow schedules, optionally filtered by workflow ID.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            Dict mapping schedule IDs to schedules
        """
        pass