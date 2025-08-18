from ...domain.agents.interfaces.agent_registry import AgentRegistry
from ...domain.workflows.interfaces.workflow_execution_engine import WorkflowExecutionEngine


class SimpleWorkflowExecutionEngine(WorkflowExecutionEngine):
    """
    A simple implementation of the WorkflowExecutionEngine interface.
    
    This implementation directly executes workflows without the complexity
    of the DAG-based execution engine.
    """
    
    def __init__(self, agent_registry: AgentRegistry):
        """
        Initialize the simple workflow execution engine.
        
        Args:
            agent_registry: Registry for retrieving agents
        """
        super().__init__()
        self.agent_registry = agent_registry