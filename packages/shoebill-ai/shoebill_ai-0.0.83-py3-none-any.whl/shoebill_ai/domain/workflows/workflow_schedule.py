from datetime import datetime
import uuid
from typing import Dict, Any, Optional


class WorkflowSchedule:
    """
    Represents a scheduled workflow execution.
    """
    
    def __init__(self, 
                 schedule_id: str,
                 workflow_id: str,
                 cron_expression: str,
                 input_data: Optional[Dict[str, Any]] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 timezone: str = "UTC",
                 enabled: bool = True,
                 max_iterations: int = 100,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        """
        Initialize a new WorkflowSchedule.
        
        Args:
            schedule_id: Unique identifier for the schedule
            workflow_id: ID of the workflow to execute
            cron_expression: Cron expression defining the schedule
            input_data: Optional input data for the workflow execution
            name: Optional name for the schedule
            description: Optional description of the schedule
            timezone: Timezone for the cron expression
            enabled: Whether the schedule is enabled
            max_iterations: Maximum number of iterations for workflow execution
            created_at: When the schedule was created
            updated_at: When the schedule was last updated
        """
        self.schedule_id = schedule_id
        self.workflow_id = workflow_id
        self.cron_expression = cron_expression
        self.input_data = input_data or {}
        self.name = name
        self.description = description
        self.timezone = timezone
        self.enabled = enabled
        self.max_iterations = max_iterations
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        
    @classmethod
    def create(cls, 
               workflow_id: str,
               cron_expression: str,
               input_data: Optional[Dict[str, Any]] = None,
               name: Optional[str] = None,
               description: Optional[str] = None,
               timezone: str = "UTC",
               enabled: bool = True,
               max_iterations: int = 100) -> 'WorkflowSchedule':
        """
        Create a new WorkflowSchedule with a generated ID.
        
        Args:
            workflow_id: ID of the workflow to execute
            cron_expression: Cron expression defining the schedule
            input_data: Optional input data for the workflow execution
            name: Optional name for the schedule
            description: Optional description of the schedule
            timezone: Timezone for the cron expression
            enabled: Whether the schedule is enabled
            max_iterations: Maximum number of iterations for workflow execution
            
        Returns:
            A new WorkflowSchedule instance
        """
        return cls(
            schedule_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            input_data=input_data,
            name=name,
            description=description,
            timezone=timezone,
            enabled=enabled,
            max_iterations=max_iterations
        )