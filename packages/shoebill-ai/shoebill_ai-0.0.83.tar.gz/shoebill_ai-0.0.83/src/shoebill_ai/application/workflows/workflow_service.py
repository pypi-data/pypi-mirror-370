from typing import Dict, List, Any, Optional, Type
import uuid

from ...domain.workflows.interfaces.workflow_repository import WorkflowRepository
from ...domain.workflows.workflow import Workflow
from ...domain.workflows.interfaces.workflow_execution_engine import WorkflowExecutionEngine


class WorkflowService:
    """
    Application service for managing workflows.

    This service provides high-level operations for creating, updating, and executing workflows.
    """

    def __init__(self, 
                 workflow_repository: WorkflowRepository,
                 execution_engine: WorkflowExecutionEngine):
        """
        Initialize the workflow service.

        Args:
            workflow_repository: Repository for storing and retrieving workflows
            execution_engine: Engine for executing workflows
        """
        self.workflow_repository = workflow_repository
        self.execution_engine = execution_engine

    def register_workflow(self, workflow: Workflow) -> None:
        """
        Register a workflow.

        Args:
            workflow: The workflow to register
        """
        self.workflow_repository.save(workflow)

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by its ID.

        Args:
            workflow_id: The ID of the workflow to retrieve

        Returns:
            The workflow if found, None otherwise
        """
        return self.workflow_repository.get(workflow_id)

    def update_workflow(self, workflow: Workflow) -> None:
        """
        Update a workflow.

        Args:
            workflow: The workflow to update
        """
        self.workflow_repository.save(workflow)

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.

        Args:
            workflow_id: The ID of the workflow to delete

        Returns:
            True if the workflow was deleted, False otherwise
        """
        return self.workflow_repository.delete(workflow_id)

    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all workflows.

        Returns:
            Dict mapping workflow IDs to workflow metadata
        """
        return self.workflow_repository.list_workflows()


    async def execute_workflow(self, 
                         workflow_id: str, 
                         input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: The ID of the workflow to execute
            input_data: Optional input data for the workflow

        Returns:
            Dict[str, Any]: The execution results containing:
                - execution_id: The unique ID of this execution
                - status: The execution status (completed, failed, or cancelled)
                - results: The workflow output values
                - execution_time: The execution time in seconds

        Raises:
            ValueError: If the workflow is not found
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        return await self.execution_engine.execute_workflow(workflow, input_data)

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: The ID of the execution

        Returns:
            Optional[Dict[str, Any]]: The execution status containing:
                - execution_id: The unique ID of this execution
                - workflow_id: The ID of the workflow that was executed
                - status: The execution status (completed, failed, or cancelled)
                - start_time: The time when execution started
                - end_time: The time when execution ended (or None if still running)
                - execution_time: The total execution time in seconds
                - current_node_id: The ID of the currently executing node (if active)
                - execution_path: The sequence of nodes that were executed
                - error_count: The number of errors that occurred during execution
                - has_errors: Whether any errors occurred during execution
                - is_active: Whether the execution is still active
            Returns None if the execution is not found.
        """
        return self.execution_engine.get_execution_status(execution_id)

    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running workflow execution.

        Args:
            execution_id: The ID of the execution to cancel

        Returns:
            True if the execution was cancelled, False otherwise
        """
        return self.execution_engine.cancel_execution(execution_id)

    def list_executions(self, workflow_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all executions, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping execution IDs to execution summaries.
            Each summary contains:
                - execution_id: The unique ID of the execution
                - workflow_id: The ID of the workflow that was executed
                - status: The execution status (completed, failed, or cancelled)
                - start_time: The time when execution started
                - end_time: The time when execution ended (or None if still running)
                - execution_time: The total execution time in seconds
                - is_active: Whether the execution is still active
        """
        return self.execution_engine.list_executions(workflow_id)
