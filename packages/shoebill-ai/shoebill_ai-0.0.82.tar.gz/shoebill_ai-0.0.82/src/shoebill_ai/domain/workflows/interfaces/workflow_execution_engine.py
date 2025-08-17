from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
import time
import uuid
import asyncio
import logging
from datetime import datetime

from ..workflow import Workflow, WorkflowExecutionResult


class WorkflowExecutionEngine(ABC):
    """
    Interface for the workflow execution engine, which is responsible for executing workflows.
    """

    def __init__(self):
        self._executions: Dict[str, WorkflowExecutionResult] = {}
        self._active_executions: Dict[str, bool] = {}
        self.logger = logging.getLogger(__name__)

    async def execute_workflow(self, 
                         workflow: Workflow, 
                         input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a workflow with the given input data.

        Args:
            workflow: The workflow to execute
            input_data: Optional input data for the workflow

        Returns:
            Dict[str, Any]: The execution results
        """
        # Create execution result
        execution_id = str(uuid.uuid4())
        execution_result = WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=workflow.workflow_id,
            status="running",
            start_time=time.time()
        )

        self._executions[execution_id] = execution_result
        self._active_executions[execution_id] = True

        try:
            # Execute the workflow
            results = await workflow.execute(input_data)

            # Update execution result
            execution_result.status = "completed"
            execution_result.results = results
            execution_result.end_time = time.time()

            return {
                "execution_id": execution_id,
                "status": "completed",
                "results": results,
                "execution_time": execution_result.execution_time
            }

        except Exception as e:
            # Handle error
            execution_result.status = "failed"
            execution_result.error = e
            execution_result.error_message = str(e)
            execution_result.end_time = time.time()

            self.logger.error(f"Workflow execution failed: {str(e)}")

            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_result.execution_time
            }

        finally:
            # Mark execution as inactive
            self._active_executions[execution_id] = False

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: The ID of the execution

        Returns:
            Optional[Dict[str, Any]]: The execution status, or None if not found
        """
        execution_result = self._executions.get(execution_id)
        if not execution_result:
            return None

        return {
            "execution_id": execution_result.execution_id,
            "workflow_id": execution_result.workflow_id,
            "status": execution_result.status,
            "start_time": execution_result.start_time,
            "end_time": execution_result.end_time,
            "execution_time": execution_result.execution_time,
            "has_error": execution_result.error is not None,
            "error_message": execution_result.error_message,
            "is_active": self._active_executions.get(execution_id, False)
        }

    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running workflow execution.

        Args:
            execution_id: The ID of the execution to cancel

        Returns:
            bool: True if the execution was cancelled, False otherwise
        """
        if execution_id not in self._executions:
            return False

        if not self._active_executions.get(execution_id, False):
            return False

        # Mark the execution as cancelled
        execution_result = self._executions[execution_id]
        execution_result.status = "cancelled"
        execution_result.end_time = time.time()
        self._active_executions[execution_id] = False

        return True

    def list_executions(self, workflow_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all executions, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of execution IDs to execution summaries
        """
        result = {}

        for execution_id, execution_result in self._executions.items():
            if workflow_id and execution_result.workflow_id != workflow_id:
                continue

            result[execution_id] = {
                "execution_id": execution_result.execution_id,
                "workflow_id": execution_result.workflow_id,
                "status": execution_result.status,
                "start_time": execution_result.start_time,
                "end_time": execution_result.end_time,
                "execution_time": execution_result.execution_time,
                "is_active": self._active_executions.get(execution_id, False)
            }

        return result
