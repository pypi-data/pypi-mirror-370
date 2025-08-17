import logging
from typing import Dict, List, Any, Optional
import copy
from datetime import datetime

from ...domain.workflows.interfaces.workflow_repository import WorkflowRepository
from ...domain.workflows.workflow import Workflow


class InMemoryWorkflowRepository(WorkflowRepository):
    """
    In-memory implementation of the WorkflowRepository interface.

    This implementation stores workflows in memory and is suitable for testing and development.
    """

    def __init__(self):
        """
        Initialize the in-memory workflow repository.
        """
        self._workflows: Dict[str, Workflow] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(__name__)

    def save(self, workflow: Workflow) -> None:
        """
        Save a workflow to the repository.

        Args:
            workflow: The workflow to save
        """
        self.logger.info(f"Saving workflow with ID: {workflow.workflow_id}, version: {workflow.version}")
        self.logger.debug(f"Workflow name: {workflow.name}")

        # Store a deep copy of the workflow to prevent external modifications
        self._workflows[workflow.workflow_id] = copy.deepcopy(workflow)

        # Store version history
        if workflow.workflow_id not in self._versions:
            self.logger.debug(f"Creating new version history for workflow: {workflow.workflow_id}")
            self._versions[workflow.workflow_id] = []

        # Create a version record
        version_record = {
            "version": workflow.version,
            "timestamp": datetime.now().isoformat(),
            "workflow": workflow.to_dict()
        }

        # Add to version history
        self._versions[workflow.workflow_id].append(version_record)
        self.logger.info(f"Workflow {workflow.workflow_id} saved successfully with version {workflow.version}")

    def get(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by its ID.

        Args:
            workflow_id: The ID of the workflow to retrieve

        Returns:
            The workflow if found, None otherwise
        """
        self.logger.info(f"Getting workflow with ID: {workflow_id}")

        workflow = self._workflows.get(workflow_id)
        if workflow:
            self.logger.info(f"Found workflow with ID: {workflow_id}, version: {workflow.version}")
            self.logger.debug(f"Workflow name: {workflow.name}")
            # Return a deep copy to prevent external modifications
            return copy.deepcopy(workflow)

        self.logger.info(f"Workflow with ID {workflow_id} not found")
        return None

    def delete(self, workflow_id: str) -> bool:
        """
        Delete a workflow from the repository.

        Args:
            workflow_id: The ID of the workflow to delete

        Returns:
            True if the workflow was deleted, False otherwise
        """
        self.logger.info(f"Deleting workflow with ID: {workflow_id}")

        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            self.logger.debug(f"Removed workflow {workflow_id} from workflows dictionary")

            if workflow_id in self._versions:
                del self._versions[workflow_id]
                self.logger.debug(f"Removed version history for workflow {workflow_id}")

            self.logger.info(f"Workflow {workflow_id} deleted successfully")
            return True

        self.logger.warning(f"Attempted to delete non-existent workflow with ID: {workflow_id}")
        return False

    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all workflows in the repository.

        Returns:
            Dict mapping workflow IDs to workflow metadata
        """
        self.logger.info("Listing all workflows in the repository")

        result = {}
        for workflow_id, workflow in self._workflows.items():
            result[workflow_id] = {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "version": workflow.version
            }

        self.logger.info(f"Found {len(result)} workflows in the repository")
        self.logger.debug(f"Workflow IDs: {list(result.keys())}")
        return result

    def get_by_name(self, name: str) -> List[Workflow]:
        """
        Get workflows by name.

        Args:
            name: The name to search for

        Returns:
            List of workflows with the specified name
        """
        self.logger.info(f"Getting workflows with name: {name}")

        result = []
        for workflow in self._workflows.values():
            if workflow.name == name:
                self.logger.debug(f"Found matching workflow with ID: {workflow.workflow_id}")
                # Return deep copies to prevent external modifications
                result.append(copy.deepcopy(workflow))

        self.logger.info(f"Found {len(result)} workflows with name: {name}")
        if result:
            self.logger.debug(f"Matching workflow IDs: {[w.workflow_id for w in result]}")
        return result

    def get_by_tags(self, tags: List[str]) -> List[Workflow]:
        """
        Get workflows by tags.

        Args:
            tags: The tags to filter by

        Returns:
            List of workflows that have all the specified tags
        """
        self.logger.info(f"Getting workflows with tags: {tags}")

        if not tags:
            self.logger.info("Empty tags list provided, returning empty result")
            return []

        result = []
        for workflow in self._workflows.values():
            # Check if workflow metadata contains tags
            workflow_tags = workflow.metadata.get("tags", [])
            # Check if all specified tags are in the workflow's tags
            if all(tag in workflow_tags for tag in tags):
                self.logger.debug(f"Found matching workflow with ID: {workflow.workflow_id}, tags: {workflow_tags}")
                # Return deep copies to prevent external modifications
                result.append(copy.deepcopy(workflow))

        self.logger.info(f"Found {len(result)} workflows matching tags: {tags}")
        if result:
            self.logger.debug(f"Matching workflow IDs: {[w.workflow_id for w in result]}")
        return result

    def get_version_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get the version history of a workflow.

        Args:
            workflow_id: The ID of the workflow

        Returns:
            List of workflow versions, ordered by version number
        """
        self.logger.info(f"Getting version history for workflow with ID: {workflow_id}")

        if workflow_id not in self._versions:
            self.logger.info(f"No version history found for workflow with ID: {workflow_id}")
            return []

        versions = self._versions[workflow_id]
        self.logger.info(f"Found {len(versions)} versions for workflow with ID: {workflow_id}")
        self.logger.debug(f"Version numbers: {[v.get('version') for v in versions]}")

        # Return a copy of the version history to prevent external modifications
        return copy.deepcopy(versions)
