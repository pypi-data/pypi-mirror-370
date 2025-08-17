from typing import Dict, List, Any, Callable, Optional

from ...domain.agents.interfaces.agent_registry import AgentRegistry
from ...domain.workflows.interfaces.workflow_queue_processor import WorkflowQueueProcessor
from ...domain.workflows.interfaces.workflow_repository import WorkflowRepository
from ...domain.workflows.workflow import Workflow
from ...infrastructure.workflows.simple_workflow_execution_engine import SimpleWorkflowExecutionEngine
from ...infrastructure.workflows.async_workflow_queue_processor import AsyncWorkflowQueueProcessor


class WorkflowQueueService:
    """
    Application service for managing asynchronous workflow queue processing.

    This service provides a high-level API for adding items to a workflow queue,
    starting and stopping queue processing, and retrieving results.

    Note: This service uses the SimpleWorkflowExecutionEngine for workflow execution.
    """

    def __init__(self, 
                 agent_registry: AgentRegistry,
                 workflow_repository: Optional[WorkflowRepository] = None):
        """
        Initialize a new WorkflowQueueService.

        Args:
            agent_registry: Registry for retrieving and executing agents
            workflow_repository: Optional repository for retrieving workflows (not used in SimpleWorkflowExecutionEngine)
        """
        # Create a SimpleWorkflowExecutionEngine
        self.execution_engine = SimpleWorkflowExecutionEngine(
            agent_registry=agent_registry
        )
        self._queue_processors: Dict[str, WorkflowQueueProcessor] = {}

    def create_queue_processor(self, 
                              workflow: Workflow,
                              process_interval_seconds: float = 60.0,
                              refresh_interval_seconds: float = 300.0,
                              max_batch_size: int = 100) -> str:
        """
        Create a new queue processor for the specified workflow.

        Args:
            workflow: The workflow to execute for each queue item
            process_interval_seconds: Time to wait between processing queue items (in seconds)
            refresh_interval_seconds: Time to wait before checking for new items when queue is empty (in seconds)
            max_batch_size: Maximum number of items to process in a batch

        Returns:
            The ID of the created queue processor
        """
        processor_id = f"queue_processor_{workflow.workflow_id}"

        # Create a new queue processor
        processor = AsyncWorkflowQueueProcessor(
            execution_engine=self.execution_engine,
            workflow=workflow,
            process_interval_seconds=process_interval_seconds,
            refresh_interval_seconds=refresh_interval_seconds,
            max_batch_size=max_batch_size
        )

        self._queue_processors[processor_id] = processor
        return processor_id

    def add_items(self, processor_id: str, items: List[Dict[str, Any]]) -> None:
        """
        Add items to the processing queue.

        Args:
            processor_id: The ID of the queue processor
            items: List of items to add to the queue
        """
        processor = self._get_processor(processor_id)
        processor.add_items(items)

    def set_item_processor(self, 
                          processor_id: str, 
                          item_processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Set a custom processor function for queue items before they're passed to the workflow.

        Args:
            processor_id: The ID of the queue processor
            item_processor: Function that takes a queue item and returns processed input data for the workflow
        """
        processor = self._get_processor(processor_id)
        processor.set_item_processor(item_processor)

    async def start_processing(self, processor_id: str) -> None:
        """
        Start processing the queue as a background task.

        Args:
            processor_id: The ID of the queue processor
        """
        processor = self._get_processor(processor_id)
        await processor.start()

    def stop_processing(self, processor_id: str) -> None:
        """
        Stop the queue processor.

        Args:
            processor_id: The ID of the queue processor
        """
        processor = self._get_processor(processor_id)
        processor.stop()

    def get_results(self, processor_id: str) -> List[Dict[str, Any]]:
        """
        Get the results of processed items.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            List of workflow execution results
        """
        processor = self._get_processor(processor_id)
        return processor.get_results()

    def is_running(self, processor_id: str) -> bool:
        """
        Check if the queue processor is currently running.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            True if the queue processor is running, False otherwise
        """
        processor = self._get_processor(processor_id)
        return processor.is_running()

    def get_queue_size(self, processor_id: str) -> int:
        """
        Get the current size of the queue.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            The number of items in the queue
        """
        processor = self._get_processor(processor_id)
        return processor.get_queue_size()

    def list_processors(self) -> List[str]:
        """
        List all queue processors.

        Returns:
            List of queue processor IDs
        """
        return list(self._queue_processors.keys())

    def _get_processor(self, processor_id: str) -> WorkflowQueueProcessor:
        """
        Get a queue processor by ID.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            The queue processor

        Raises:
            ValueError: If the processor ID is not found
        """
        if processor_id not in self._queue_processors:
            raise ValueError(f"Queue processor with ID '{processor_id}' not found")
        return self._queue_processors[processor_id]
