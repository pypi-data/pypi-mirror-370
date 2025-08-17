from typing import Dict, List, Any, Optional
import uuid
from dataclasses import dataclass, field

from .base_agent import BaseAgent
from .interfaces.multimodal_service_interface import MultimodalServiceInterface


@dataclass
class MultimodalAgent(BaseAgent):
    """
    An agent that wraps a MultimodalServiceInterface to provide multimodal AI capabilities.

    This agent directly uses the service's methods for processing requests,
    eliminating the need for an intermediate AgentService.
    """
    service: MultimodalServiceInterface = field(default=None, repr=False, compare=False)

    @classmethod
    def create(cls, 
               name: str, 
               description: str,
               service: MultimodalServiceInterface,
               system_prompt: Optional[str] = None,
               tools: List[Dict[str, Any]] = None,
               tags: List[str] = None,
               config: Dict[str, Any] = None) -> 'MultimodalAgent':
        """
        Create a new MultimodalAgent with a MultimodalServiceInterface.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            service: An implementation of MultimodalServiceInterface
            system_prompt: Optional system prompt to guide the agent's behavior
            tools: Optional list of tools the agent can use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent

        Returns:
            The created MultimodalAgent
        """

        # Create and return the MultimodalAgent
        return cls(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=service,
            system_prompt=system_prompt,
            tools=tools or [],
            tags=tags or [],
            config=config or {}
        )

    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None, use_generate: bool = False) -> Dict[str, Any]:
        """
        Process input data and return results.

        This method determines which MultimodalService method to call based on the input data.

        Args:
            input_data: The input data for the agent to process
            context: Optional context information
            use_generate: If True, use the generate method instead of chat (default: False)

        Returns:
            Dict[str, Any]: The processing results
        """
        # Extract relevant parameters from input_data
        message = input_data.get('message', input_data.get('query', ''))
        session_id = input_data.get('session_id', self.agent_id)
        image_path = input_data.get('image_path')
        documents = input_data.get('documents')
        chat_history = input_data.get('chat_history')
        max_tokens = input_data.get('max_tokens')
        stream = input_data.get('stream', False)

        # Determine which method to use based on the use_generate parameter
        if use_generate:
            # Use the MultimodalService's generate method
            result = self.service.generate(
                prompt=message,
                system_prompt=self.system_prompt,
                max_tokens=max_tokens
            )
        else:
            # Use the MultimodalService's chat method
            result = self.service.chat(
                message=message,
                session_id=session_id,
                image_path=image_path,
                documents=documents,
                tools=self.tools,
                chat_history=chat_history,
                system_prompt=self.system_prompt,
                stream=stream
            )

        # Format the result
        if isinstance(result, dict):
            # Add agent information to the result
            result['agent_id'] = self.agent_id
            result['agent_name'] = self.name
            return result
        else:
            # If result is not a dict, wrap it
            return {
                'result': result,
                'agent_id': self.agent_id,
                'agent_name': self.name
            }

    def chat(self, message: str, session_id: str = None, 
             image_path: str = None,
             documents: List[Dict[str, str]] = None,
             chat_history: List[Dict[str, str]] = None,
             stream: bool = False) -> Dict[str, Any]:
        """
        Chat with the agent.

        This method directly calls the MultimodalService's chat method.

        Args:
            message: The user's message
            session_id: Optional session ID (defaults to agent_id)
            image_path: Optional path to an image to analyze
            documents: Optional list of documents to use as context
            chat_history: Optional chat history
            stream: Whether to stream the response from the API (default: False)

        Returns:
            Dict[str, Any]: The chat response
        """
        return self.service.chat(
            message=message,
            session_id=session_id or self.agent_id,
            image_path=image_path,
            documents=documents,
            tools=self.tools,
            chat_history=chat_history,
            system_prompt=self.system_prompt,
            stream=stream
        )

    def generate(self, prompt: str, max_tokens: int = None) -> Dict[str, Any]:
        """
        Generate text using the agent.

        This method directly calls the MultimodalService's generate method.

        Args:
            prompt: The prompt to generate text from
            max_tokens: Optional maximum number of tokens to generate

        Returns:
            Dict[str, Any]: The generation response
        """
        return self.service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=max_tokens
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        base_dict = super().to_dict()
        base_dict.update({
            "model_name": self.service.model_name,
            "api_url": self.service.api_url
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any], service: MultimodalServiceInterface) -> 'MultimodalAgent':
        """
        Create a MultimodalAgent from a dictionary representation.

        Args:
            data: Dictionary representation of the agent
            service: An implementation of MultimodalServiceInterface

        Returns:
            MultimodalAgent: The created agent
        """

        # Create and return the MultimodalAgent
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            description=data["description"],
            service=service,
            system_prompt=data.get("system_prompt"),
            tools=data.get("tools", []),
            tags=data.get("tags", []),
            config=data.get("config", {})
        )
