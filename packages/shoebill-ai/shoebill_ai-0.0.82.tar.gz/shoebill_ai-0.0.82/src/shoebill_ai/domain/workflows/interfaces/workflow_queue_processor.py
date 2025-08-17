from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable


class WorkflowQueueProcessor(ABC):
    """
    Interface for the workflow queue processor, which manages asynchronous execution of workflows.
    """
    
    @abstractmethod
    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Add items to the processing queue.
        
        Args:
            items: List of items to add to the queue
        """
        pass
    
    @abstractmethod
    def set_item_processor(self, processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Set a custom processor function for queue items before they're passed to the workflow.
        
        Args:
            processor: Function that takes a queue item and returns processed input data for the workflow
        """
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """
        Start processing the queue as a background task.
        This method doesn't block and allows other operations to continue.
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the queue processor.
        """
        pass
    
    @abstractmethod
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get the results of processed items.
        
        Returns:
            List of workflow execution results
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the queue processor is currently running.
        
        Returns:
            True if the queue processor is running, False otherwise
        """
        pass
    
    @abstractmethod
    def get_queue_size(self) -> int:
        """
        Get the current size of the queue.
        
        Returns:
            The number of items in the queue
        """
        pass