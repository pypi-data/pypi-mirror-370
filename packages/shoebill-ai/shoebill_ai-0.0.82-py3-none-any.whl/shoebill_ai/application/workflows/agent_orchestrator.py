import uuid
from typing import Dict, List, Any, Callable, Optional, TypeVar, Awaitable, Union
from datetime import datetime

from ... import TextService, EmbeddingService, MultimodalService, VisionService
from ...application.workflows.workflow_service import WorkflowService
from ...application.workflows.workflow_queue_service import WorkflowQueueService
from ...domain.agents.base_agent import BaseAgent
from ...domain.agents.embedding_agent import EmbeddingAgent
from ...domain.agents.multimodal_agent import MultimodalAgent
from ...domain.agents.text_agent import TextAgent
from ...domain.agents.vision_agent import VisionAgent
from ...domain.workflows.workflow import Workflow
from ...domain.workflows.workflow_schedule import WorkflowSchedule
from ...infrastructure.agents.in_memory_agent_registry import InMemoryAgentRegistry
from ...infrastructure.agents.in_memory_workflow_repository import InMemoryWorkflowRepository
from ...infrastructure.workflows.simple_workflow_execution_engine import SimpleWorkflowExecutionEngine
from ...infrastructure.workflows.in_memory_workflow_schedule_repository import InMemoryWorkflowScheduleRepository
from ...infrastructure.workflows.workflow_scheduler import WorkflowScheduler

# Type variable for agent types
T = TypeVar('T', bound=BaseAgent)


class AgentOrchestrator:
    """
    Main entry point for the Agent Orchestration Framework.

    This class provides a simple API for creating and executing workflows with AI agents.
    """

    def __init__(self, api_url: str = None, api_token: str = None, 
                 text_service: TextService = None, 
                 embedding_service: EmbeddingService = None,
                 multimodal_service: MultimodalService = None,
                 vision_service: VisionService = None):
        """
        Initialize the Agent Orchestration Framework with default in-memory implementations.

        Args:
            api_url: Optional base URL for LLM services. If not provided, LLM services will not be initialized.
            api_token: Optional API token for LLM services.
            text_service: Optional pre-configured TextService instance.
            embedding_service: Optional pre-configured EmbeddingService instance.
            multimodal_service: Optional pre-configured MultimodalService instance.
            vision_service: Optional pre-configured VisionService instance.
        """
        # Create registries and repositories
        self.agent_registry = InMemoryAgentRegistry()
        self.workflow_repository = InMemoryWorkflowRepository()

        # Create an execution engine
        self.execution_engine = SimpleWorkflowExecutionEngine(
            agent_registry=self.agent_registry
        )

        # Store API URL and token
        self.api_url = api_url
        self.api_token = api_token

        # Store provided services
        self.text_service = text_service
        self.embedding_service = embedding_service
        self.multimodal_service = multimodal_service
        self.vision_service = vision_service

        # Create services
        self.workflow_service = WorkflowService(
            workflow_repository=self.workflow_repository,
            execution_engine=self.execution_engine
        )
        self.workflow_queue_service = WorkflowQueueService(
            agent_registry=self.agent_registry
        )

        # Initialize workflow scheduling components
        self.schedule_repository = InMemoryWorkflowScheduleRepository()
        self.workflow_scheduler = WorkflowScheduler(
            schedule_repository=self.schedule_repository,
            workflow_repository=self.workflow_repository,
            execution_engine=self.execution_engine
        )

    # Agent Management

    def create_text_agent(self,
                         name: str,
                         description: str,
                         system_prompt: Optional[str] = None,
                         tools: List[Dict[str, Any]] = None,
                         tags: List[str] = None,
                         config: Dict[str, Any] = None,
                         temperature: float = 0.6,
                         max_tokens: int = 2500,
                         timeout: Optional[int] = None) -> TextAgent:
        """
        Create a new TextAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            system_prompt: Optional system prompt to guide the agent's behavior
            tools: Optional list of tools the agent can use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate
            timeout: Optional timeout in seconds for API requests

        Returns:
            The created TextAgent
        """
        if not self.api_url and not self.text_service:
            raise ValueError("Either API URL or a TextService must be provided to create a TextAgent")

        # Create the agent using the create method
        agent = TextAgent.create(
            name=name,
            description=description,
            service=self.text_service,
            system_prompt=system_prompt,
            tools=tools,
            tags=tags,
            config=config
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def create_vision_agent(self,
                           name: str,
                           description: str,
                           system_prompt: Optional[str] = None,
                           tags: List[str] = None,
                           config: Dict[str, Any] = None,
                           temperature: float = 0.6,
                           max_tokens: int = 2500,
                           timeout: Optional[int] = None) -> VisionAgent:
        """
        Create a new VisionAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            system_prompt: Optional system prompt to guide the agent's behavior
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate
            timeout: Optional timeout in seconds for API requests

        Returns:
            The created VisionAgent
        """
        if not self.api_url and not self.vision_service:
            raise ValueError("Either API URL or a VisionService must be provided to create a VisionAgent")


        # Create the agent using the create method
        agent = VisionAgent.create(
            name=name,
            description=description,
            service=self.vision_service,
            system_prompt=system_prompt,
            tags=tags,
            config=config
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def create_multimodal_agent(self,
                               name: str,
                               description: str,
                               system_prompt: Optional[str] = None,
                               tools: List[Dict[str, Any]] = None,
                               tags: List[str] = None,
                               config: Dict[str, Any] = None,
                               temperature: float = 0.6,
                               max_tokens: int = 2500,
                               timeout: Optional[int] = None) -> MultimodalAgent:
        """
        Create a new MultimodalAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            system_prompt: Optional system prompt to guide the agent's behavior
            tools: Optional list of tools the agent can use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate
            timeout: Optional timeout in seconds for API requests

        Returns:
            The created MultimodalAgent
        """
        if not self.api_url and not self.multimodal_service:
            raise ValueError("Either API URL or a MultimodalService must be provided to create a MultimodalAgent")

        # Create the agent using the create method
        agent = MultimodalAgent.create(
            name=name,
            description=description,
            service=self.multimodal_service,
            system_prompt=system_prompt,
            tools=tools,
            tags=tags,
            config=config
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def create_embedding_agent(self,
                              name: str,
                              description: str,
                              tags: List[str] = None,
                              config: Dict[str, Any] = None,
                              timeout: Optional[int] = None) -> EmbeddingAgent:
        """
        Create a new EmbeddingAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            timeout: Optional timeout in seconds for API requests

        Returns:
            The created EmbeddingAgent
        """
        if not self.api_url and not self.embedding_service:
            raise ValueError("Either API URL or an EmbeddingService must be provided to create an EmbeddingAgent")


        # Create the agent using the create method
        agent = EmbeddingAgent.create(
            name=name,
            description=description,
            service=self.embedding_service,
            tags=tags,
            config=config
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by its ID.

        This method can return any agent type that inherits from BaseAgent,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Args:
            agent_id: The ID of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        # Get the agent from the registry
        return self.agent_registry.get(agent_id)

    def list_agents(self) -> List[BaseAgent]:
        """
        List all registered agents.

        This method returns all agent types that inherit from BaseAgent,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Returns:
            A list of all registered agents
        """
        # Get agents from the registry
        return self.agent_registry.list_agents()

    def get_agents_by_tags(self, tags: List[str]) -> List[BaseAgent]:
        """
        Get agents by tags.

        This method returns all agent types that inherit from BaseAgent and match the tags,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Args:
            tags: The tags to filter by

        Returns:
            A list of agents that have all the specified tags
        """
        # Get agents from the registry
        return self.agent_registry.get_by_tags(tags)

    def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by its name.

        This method can return any agent type that inherits from BaseAgent,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Args:
            name: The name of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        # Get the agent from the registry
        return self.agent_registry.get_by_name(name)

    # Function Management


    # Workflow Management

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by its ID.

        Args:
            workflow_id: The ID of the workflow to retrieve

        Returns:
            The workflow if found, None otherwise
        """
        return self.workflow_service.get_workflow(workflow_id)

    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all workflows.

        Returns:
            Dict mapping workflow IDs to workflow metadata
        """
        return self.workflow_service.list_workflows()


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
        """
        return await self.workflow_service.execute_workflow(
            workflow_id=workflow_id,
            input_data=input_data
        )

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
        return self.workflow_service.get_execution_status(execution_id)

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
        return self.workflow_service.list_executions(workflow_id)

    # Workflow Queue Processing

    def create_workflow_queue(self, 
                             workflow_id: str,
                             process_interval_seconds: float = 60.0,
                             refresh_interval_seconds: float = 300.0,
                             max_batch_size: int = 100) -> str:
        """
        Create a queue processor for batch processing of workflow executions.

        Args:
            workflow_id: The ID of the workflow to execute for each queue item
            process_interval_seconds: Time to wait between processing queue items (in seconds)
            refresh_interval_seconds: Time to wait before checking for new items when queue is empty (in seconds)
            max_batch_size: Maximum number of items to process in a batch

        Returns:
            The ID of the created queue processor
        """
        workflow = self.workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow with ID '{workflow_id}' not found")

        return self.workflow_queue_service.create_queue_processor(
            workflow=workflow,
            process_interval_seconds=process_interval_seconds,
            refresh_interval_seconds=refresh_interval_seconds,
            max_batch_size=max_batch_size
        )

    def add_items_to_queue(self, processor_id: str, items: List[Dict[str, Any]]) -> None:
        """
        Add items to a workflow processing queue.

        Args:
            processor_id: The ID of the queue processor
            items: List of items to add to the queue
        """
        self.workflow_queue_service.add_items(processor_id, items)

    def set_queue_item_processor(self, 
                               processor_id: str, 
                               item_processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Set a custom processor function for queue items before they're passed to the workflow.

        Args:
            processor_id: The ID of the queue processor
            item_processor: Function that takes a queue item and returns processed input data for the workflow
        """
        self.workflow_queue_service.set_item_processor(processor_id, item_processor)

    async def start_queue_processing(self, processor_id: str) -> None:
        """
        Start processing a workflow queue as a background task.

        Args:
            processor_id: The ID of the queue processor
        """
        await self.workflow_queue_service.start_processing(processor_id)

    def stop_queue_processing(self, processor_id: str) -> None:
        """
        Stop a workflow queue processor.

        Args:
            processor_id: The ID of the queue processor
        """
        self.workflow_queue_service.stop_processing(processor_id)

    def get_queue_results(self, processor_id: str) -> List[Dict[str, Any]]:
        """
        Get the results of processed queue items.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            List of workflow execution results
        """
        return self.workflow_queue_service.get_results(processor_id)

    def is_queue_running(self, processor_id: str) -> bool:
        """
        Check if a queue processor is currently running.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            True if the queue processor is running, False otherwise
        """
        return self.workflow_queue_service.is_running(processor_id)

    def get_queue_size(self, processor_id: str) -> int:
        """
        Get the current size of a workflow processing queue.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            The number of items in the queue
        """
        return self.workflow_queue_service.get_queue_size(processor_id)

    def list_queue_processors(self) -> List[str]:
        """
        List all workflow queue processors.

        Returns:
            List of queue processor IDs
        """
        return self.workflow_queue_service.list_processors()

    # Workflow Scheduling

    def create_workflow_schedule(self,
                               workflow_id: str,
                               cron_expression: str,
                               input_data: Optional[Dict[str, Any]] = None,
                               name: Optional[str] = None,
                               description: Optional[str] = None,
                               timezone: str = "UTC",
                               enabled: bool = True) -> WorkflowSchedule:
        """
        Create a new schedule for a workflow.

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
        """
        return self.workflow_scheduler.create_schedule(
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            input_data=input_data,
            name=name,
            description=description,
            timezone=timezone,
            enabled=enabled
        )

    def get_workflow_schedule(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """
        Get a workflow schedule by ID.

        Args:
            schedule_id: The ID of the schedule to retrieve

        Returns:
            The schedule if found, None otherwise
        """
        return self.workflow_scheduler.get_schedule(schedule_id)

    def update_workflow_schedule(self, schedule: WorkflowSchedule) -> None:
        """
        Update a workflow schedule.

        Args:
            schedule: The schedule to update
        """
        self.workflow_scheduler.update_schedule(schedule)

    def delete_workflow_schedule(self, schedule_id: str) -> bool:
        """
        Delete a workflow schedule.

        Args:
            schedule_id: The ID of the schedule to delete

        Returns:
            True if the schedule was deleted, False otherwise
        """
        return self.workflow_scheduler.delete_schedule(schedule_id)

    def list_workflow_schedules(self, workflow_id: Optional[str] = None) -> Dict[str, WorkflowSchedule]:
        """
        List all workflow schedules, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict mapping schedule IDs to schedules
        """
        return self.workflow_scheduler.list_schedules(workflow_id)

    def get_next_schedule_run_time(self, schedule_id: str) -> Optional[datetime]:
        """
        Get the next run time for a schedule.

        Args:
            schedule_id: The ID of the schedule

        Returns:
            The next run time, or None if the schedule doesn't exist or is disabled
        """
        return self.workflow_scheduler.get_next_run_time(schedule_id)

    def get_next_n_schedule_run_times(self, schedule_id: str, n: int) -> List[datetime]:
        """
        Get the next n run times for a schedule.

        Args:
            schedule_id: The ID of the schedule
            n: Number of run times to get

        Returns:
            List of the next n run times
        """
        return self.workflow_scheduler.get_next_n_run_times(schedule_id, n)

    async def start_scheduler(self) -> None:
        """
        Start the workflow scheduler.
        """
        await self.workflow_scheduler.start()

    def stop_scheduler(self) -> None:
        """
        Stop the workflow scheduler.
        """
        self.workflow_scheduler.stop()
