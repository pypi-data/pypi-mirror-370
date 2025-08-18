import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set

from ...domain.workflows.interfaces.workflow_repository import WorkflowRepository
from ...domain.workflows.interfaces.workflow_execution_engine import WorkflowExecutionEngine
from ...domain.workflows.workflow_schedule import WorkflowSchedule
from ...domain.workflows.interfaces.workflow_schedule_repository import WorkflowScheduleRepository
from .cron_parser import CronParser

class WorkflowScheduler:
    """
    Service for managing workflow schedules and triggering executions.
    """

    def __init__(self, 
                 schedule_repository: WorkflowScheduleRepository,
                 workflow_repository: WorkflowRepository,
                 execution_engine: WorkflowExecutionEngine,
                 check_interval_seconds: float = 60.0):
        """
        Initialize a new WorkflowScheduler.

        Args:
            schedule_repository: Repository for storing and retrieving schedules
            workflow_repository: Repository for retrieving workflows
            execution_engine: Engine for executing workflows
            check_interval_seconds: How often to check for due schedules (in seconds)
        """
        self.schedule_repository = schedule_repository
        self.workflow_repository = workflow_repository
        self.execution_engine = execution_engine
        self.check_interval_seconds = check_interval_seconds

        self._running = False
        self._task = None
        self._last_check_time = None
        self._executed_schedules: Set[str] = set()  # Track executed schedules to avoid duplicates
        self.logger = logging.getLogger(__name__)

    async def start(self) -> None:
        """
        Start the scheduler as a background task.
        """
        if self._running:
            self.logger.info("Scheduler is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_scheduler())
        self.logger.info("Started workflow scheduler")

    async def _run_scheduler(self) -> None:
        """
        Run the scheduler loop.
        """
        self.logger.info("Workflow scheduler running")

        while self._running:
            try:
                # Get current time
                now = datetime.now()

                # Initialize last check time if not set
                if self._last_check_time is None:
                    self._last_check_time = now - timedelta(seconds=self.check_interval_seconds)

                # Get all schedules
                schedules = self.schedule_repository.list_schedules()

                # Check each schedule
                for schedule_id, schedule in schedules.items():
                    if not schedule.enabled:
                        continue

                    try:
                        # Get next run time
                        next_run = CronParser.get_next_run_time(
                            schedule.cron_expression, 
                            self._last_check_time,
                            schedule.timezone
                        )

                        # Check if it's due
                        if next_run <= now:
                            # Generate a unique execution ID for this run
                            execution_key = f"{schedule_id}_{next_run.isoformat()}"

                            # Check if we've already executed this schedule at this time
                            if execution_key not in self._executed_schedules:
                                # Execute the workflow
                                await self._execute_scheduled_workflow(schedule)

                                # Mark as executed
                                self._executed_schedules.add(execution_key)

                                # Limit the size of the executed schedules set
                                if len(self._executed_schedules) > 1000:
                                    # Keep only the most recent 500 executions
                                    self._executed_schedules = set(list(self._executed_schedules)[-500:])

                    except Exception as e:
                        self.logger.error(f"Error processing schedule {schedule_id}: {str(e)}")

                # Update last check time
                self._last_check_time = now

                # Wait for next check
                await asyncio.sleep(self.check_interval_seconds)

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                # Wait a bit before retrying
                await asyncio.sleep(self.check_interval_seconds)

        self.logger.info("Workflow scheduler stopped")

    async def _execute_scheduled_workflow(self, schedule: WorkflowSchedule) -> None:
        """
        Execute a scheduled workflow.

        Args:
            schedule: The schedule to execute
        """
        try:
            # Get the workflow
            workflow = self.workflow_repository.get(schedule.workflow_id)
            if not workflow:
                self.logger.error(f"Workflow {schedule.workflow_id} not found for schedule {schedule.schedule_id}")
                return

            # Log the execution
            self.logger.info(f"Executing scheduled workflow: {schedule.name or schedule.schedule_id}")

            # Execute the workflow
            result = await self.execution_engine.execute_workflow(
                workflow=workflow,
                input_data=schedule.input_data
            )

            self.logger.info(f"Scheduled workflow execution completed: {schedule.name or schedule.schedule_id}")

            # Optionally, you could store the execution result somewhere

        except Exception as e:
            self.logger.error(f"Error executing scheduled workflow {schedule.schedule_id}: {str(e)}")

    def stop(self) -> None:
        """
        Stop the scheduler.
        """
        if not self._running:
            self.logger.info("Scheduler is not running")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

        self.logger.info("Stopped workflow scheduler")

    def create_schedule(self, 
                       workflow_id: str,
                       cron_expression: str,
                       input_data: Optional[Dict[str, Any]] = None,
                       name: Optional[str] = None,
                       description: Optional[str] = None,
                       timezone: str = "UTC",
                       enabled: bool = True) -> WorkflowSchedule:
        """
        Create a new workflow schedule.

        Args:
            workflow_id: ID of the workflow to execute
            cron_expression: Cron expression defining the schedule
            input_data: Optional input data for the workflow execution
            name: Optional name for the schedule
            description: Optional description of the schedule
            timezone: Timezone for the cron expression
            enabled: Whether the schedule is enabled

        Returns:
            The created schedule

        Raises:
            ValueError: If the cron expression is invalid or the workflow doesn't exist
        """
        # Validate the cron expression
        if not CronParser.validate(cron_expression):
            raise ValueError(f"Invalid cron expression: {cron_expression}")

        # Check if the workflow exists
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create the schedule
        schedule = WorkflowSchedule.create(
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            input_data=input_data,
            name=name,
            description=description,
            timezone=timezone,
            enabled=enabled
        )

        # Save the schedule
        self.schedule_repository.save(schedule)

        return schedule

    def update_schedule(self, schedule: WorkflowSchedule) -> None:
        """
        Update a workflow schedule.

        Args:
            schedule: The schedule to update

        Raises:
            ValueError: If the cron expression is invalid
        """
        # Validate the cron expression
        if not CronParser.validate(schedule.cron_expression):
            raise ValueError(f"Invalid cron expression: {schedule.cron_expression}")

        # Update the timestamp
        schedule.updated_at = datetime.now()

        # Save the schedule
        self.schedule_repository.save(schedule)

    def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete a workflow schedule.

        Args:
            schedule_id: The ID of the schedule to delete

        Returns:
            True if the schedule was deleted, False otherwise
        """
        return self.schedule_repository.delete(schedule_id)

    def get_schedule(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """
        Get a workflow schedule by ID.

        Args:
            schedule_id: The ID of the schedule to retrieve

        Returns:
            The schedule if found, None otherwise
        """
        return self.schedule_repository.get(schedule_id)

    def list_schedules(self, workflow_id: Optional[str] = None) -> Dict[str, WorkflowSchedule]:
        """
        List all workflow schedules, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict mapping schedule IDs to schedules
        """
        return self.schedule_repository.list_schedules(workflow_id)

    def get_next_run_time(self, schedule_id: str) -> Optional[datetime]:
        """
        Get the next run time for a schedule.

        Args:
            schedule_id: The ID of the schedule

        Returns:
            The next run time, or None if the schedule doesn't exist or is disabled
        """
        schedule = self.schedule_repository.get(schedule_id)
        if not schedule or not schedule.enabled:
            return None

        return CronParser.get_next_run_time(
            schedule.cron_expression, 
            datetime.now(),
            schedule.timezone
        )

    def get_next_n_run_times(self, schedule_id: str, n: int) -> List[datetime]:
        """
        Get the next n run times for a schedule.

        Args:
            schedule_id: The ID of the schedule
            n: Number of run times to get

        Returns:
            List of the next n run times, or empty list if the schedule doesn't exist or is disabled
        """
        schedule = self.schedule_repository.get(schedule_id)
        if not schedule or not schedule.enabled:
            return []

        return CronParser.get_next_n_run_times(
            schedule.cron_expression, 
            n,
            datetime.now(),
            schedule.timezone
        )
