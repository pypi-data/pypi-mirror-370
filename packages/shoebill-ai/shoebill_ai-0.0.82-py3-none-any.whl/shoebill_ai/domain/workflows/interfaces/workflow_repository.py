from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from ..workflow import Workflow


class WorkflowRepository(ABC):
    """
    Interface for the workflow repository, which manages the storage and retrieval of workflows.
    """
    
    @abstractmethod
    def save(self, workflow: Workflow) -> None:
        """
        Save a workflow to the repository.
        
        Args:
            workflow: The workflow to save
        """
        pass
    
    @abstractmethod
    def get(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by its ID.
        
        Args:
            workflow_id: The ID of the workflow to retrieve
            
        Returns:
            The workflow if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, workflow_id: str) -> bool:
        """
        Delete a workflow from the repository.
        
        Args:
            workflow_id: The ID of the workflow to delete
            
        Returns:
            True if the workflow was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all workflows in the repository.
        
        Returns:
            Dict mapping workflow IDs to workflow metadata
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> List[Workflow]:
        """
        Get workflows by name.
        
        Args:
            name: The name to search for
            
        Returns:
            List of workflows with the specified name
        """
        pass
    
    @abstractmethod
    def get_by_tags(self, tags: List[str]) -> List[Workflow]:
        """
        Get workflows by tags.
        
        Args:
            tags: The tags to filter by
            
        Returns:
            List of workflows that have all the specified tags
        """
        pass
    
    @abstractmethod
    def get_version_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get the version history of a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            List of workflow versions, ordered by version number
        """
        pass