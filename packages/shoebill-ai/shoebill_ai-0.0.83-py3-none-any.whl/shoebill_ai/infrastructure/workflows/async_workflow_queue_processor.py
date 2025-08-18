import asyncio
import logging
from collections import deque
from typing import Dict, List, Any, Deque, Optional, Callable

from ...domain.workflows.interfaces.workflow_execution_engine import WorkflowExecutionEngine
from ...domain.workflows.interfaces.workflow_queue_processor import WorkflowQueueProcessor
from ...domain.workflows.workflow import Workflow


class AsyncWorkflowQueueProcessor(WorkflowQueueProcessor):
    """
    Asynchronous implementation of the WorkflowQueueProcessor interface.

    Processes workflow executions from a queue with configurable wait times.
    """

    def __init__(self, 
                 execution_engine: WorkflowExecutionEngine,
                 workflow: Workflow,
                 process_interval_seconds: float = 60.0,
                 refresh_interval_seconds: float = 300.0,
                 max_batch_size: int = 100):
        """
        Initialize a new AsyncWorkflowQueueProcessor.

        Args:
            execution_engine: The execution engine to use for workflow execution
            workflow: The workflow to execute for each queue item
            process_interval_seconds: Time to wait between processing queue items (in seconds)
            refresh_interval_seconds: Time to wait before checking for new items when queue is empty (in seconds)
            max_batch_size: Maximum number of items to process in a batch
        """
        self.execution_engine = execution_engine
        self.workflow = workflow
        self.process_interval_seconds = process_interval_seconds
        self.refresh_interval_seconds = refresh_interval_seconds
        self.max_batch_size = max_batch_size

        self._running = False
        self._task = None
        self._queue: Deque[Dict[str, Any]] = deque()
        self._item_processor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
        self._results: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Add items to the processing queue.

        Args:
            items: List of items to add to the queue
        """
        self._queue.extend(items)
        self.logger.info(f"Added {len(items)} items to the queue. Queue size: {len(self._queue)}")

    def set_item_processor(self, processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Set a custom processor function for queue items before they're passed to the workflow.

        Args:
            processor: Function that takes a queue item and returns processed input data for the workflow
        """
        self._item_processor = processor

    async def start(self) -> None:
        """
        Start processing the queue as a background task.
        This method doesn't block and allows other operations to continue.
        """
        if self._running:
            self.logger.info("Queue processor is already running")
            return

        if len(self._queue) > 0:
            self._running = True
            self._task = asyncio.create_task(self._process_queue())
            self.logger.info(f"Started queue processor with {len(self._queue)} items")
        else:
            self.logger.info("No items in queue. Queue processor not started.")

    async def _process_queue(self) -> None:
        """
        Process items in the queue at the configured interval.
        This runs as a background task until the queue is empty or stop() is called.
        """
        self.logger.info(f"Queue processor running. Queue size: {len(self._queue)}")

        while self._running and self._queue:
            # Get the next item
            item = self._queue.popleft()

            try:
                # Process the item
                self.logger.info(f"Processing queue item: {item}")

                # Prepare input data for the workflow
                if self._item_processor:
                    input_data = self._item_processor(item)
                else:
                    input_data = item

                # Execute the workflow
                result = await self.execution_engine.execute_workflow(
                    workflow=self.workflow,
                    input_data=input_data
                )

                # Store the result
                self._results.append(result)

                self.logger.info(f"Processed item. Remaining in queue: {len(self._queue)}")

                # If there are more items in the queue, wait before processing the next one
                if self._queue and self._running:
                    self.logger.info(f"Waiting {self.process_interval_seconds} seconds before processing next item")
                    await asyncio.sleep(self.process_interval_seconds)

            except Exception as e:
                self.logger.error(f"Error processing queue item: {str(e)}")
                # Optionally, you could add error handling logic here, such as:
                # - Retrying the item
                # - Storing the error in a separate list
                # - Notifying an administrator

        # If we've processed all items or were stopped
        if not self._queue:
            self.logger.info("Queue is empty. Queue processor stopping.")

        self._running = False

    def stop(self) -> None:
        """
        Stop the queue processor.
        """
        if not self._running:
            self.logger.info("Queue processor is not running")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

        self.logger.info("Queue processor stopped")

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get the results of processed items.

        Returns:
            List of workflow execution results
        """
        return self._results

    def is_running(self) -> bool:
        """
        Check if the queue processor is currently running.

        Returns:
            True if the queue processor is running, False otherwise
        """
        return self._running

    def get_queue_size(self) -> int:
        """
        Get the current size of the queue.

        Returns:
            The number of items in the queue
        """
        return len(self._queue)
