from typing import Dict, Optional

from ...domain.workflows.workflow_schedule import WorkflowSchedule
from ...domain.workflows.interfaces.workflow_schedule_repository import WorkflowScheduleRepository


class InMemoryWorkflowScheduleRepository(WorkflowScheduleRepository):
    """
    In-memory implementation of WorkflowScheduleRepository.
    Useful for testing and development.
    """
    
    def __init__(self):
        """
        Initialize a new InMemoryWorkflowScheduleRepository.
        """
        self._schedules: Dict[str, WorkflowSchedule] = {}
        
    def save(self, schedule: WorkflowSchedule) -> None:
        """
        Save a workflow schedule.
        
        Args:
            schedule: The schedule to save
        """
        self._schedules[schedule.schedule_id] = schedule
        
    def get(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """
        Get a workflow schedule by ID.
        
        Args:
            schedule_id: The ID of the schedule to retrieve
            
        Returns:
            The schedule if found, None otherwise
        """
        return self._schedules.get(schedule_id)
        
    def delete(self, schedule_id: str) -> bool:
        """
        Delete a workflow schedule.
        
        Args:
            schedule_id: The ID of the schedule to delete
            
        Returns:
            True if the schedule was deleted, False otherwise
        """
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False
        
    def list_schedules(self, workflow_id: Optional[str] = None) -> Dict[str, WorkflowSchedule]:
        """
        List all workflow schedules, optionally filtered by workflow ID.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            Dict mapping schedule IDs to schedules
        """
        if workflow_id is None:
            return self._schedules.copy()
        
        return {
            schedule_id: schedule 
            for schedule_id, schedule in self._schedules.items() 
            if schedule.workflow_id == workflow_id
        }