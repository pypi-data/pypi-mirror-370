"""Base Reasoning Agent implementation for Semantic Kernel 1.35.3.

This class intentionally does NOT inherit from semantic_kernel.agents.Agent to
avoid version-specific interface constraints. Tests expect a lightweight async
API that returns ChatMessageContent and manages simple chat history.
"""

from abc import ABC, abstractmethod
import logging
import re
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)

from semantic_kernel import Kernel
from semantic_kernel.contents import AuthorRole
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.functions import (  # noqa: F401 (placeholder for plugin function types)
    KernelFunction,
)


logger = logging.getLogger(__name__)


class BaseReasoningAgent(ABC):
    """Base class for reasoning agents compatible with SK 1.35.3."""

    def __init__(
        self,
        name: str,
        kernel: Kernel,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        execution_settings: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the base reasoning agent.

        Args:
            name: Agent name
            kernel: Semantic Kernel instance
            description: Agent description
            instructions: Agent instructions/system prompt
            execution_settings: Execution settings for the agent
        """
        # Basic identity and instructions (mirroring Agent fields expected by tests)
        self.name = name
        self.description = description or f"Reasoning agent: {name}"
        self.instructions = instructions or "You are a helpful reasoning agent."
        self._kernel = kernel
        self._execution_settings = execution_settings or {}
        self._chat_history: List[ChatMessageContent] = []
        self._plugins: Dict[str, Any] = {}

    @runtime_checkable
    class SupportsFunctions(Protocol):
        """Protocol for plugin-like objects that expose a 'functions' iterable."""

        functions: Iterable[KernelFunction]

    @property
    def kernel(self) -> Kernel:
        """Get the kernel instance."""
        return self._kernel

    async def invoke(self, message: str, **kwargs: Any) -> ChatMessageContent:
        """Invoke the agent with a message.

        Args:
            message: Input message
            **kwargs: Additional arguments

        Returns:
            Agent response as ChatMessageContent
        """
        # Add message to history
        user_message = ChatMessageContent(role=AuthorRole.USER, content=message)
        self._chat_history.append(user_message)

        # Process message through reasoning pipeline
        response = await self._process_message(message, **kwargs)

        # Add response to history
        agent_message = ChatMessageContent(role=AuthorRole.ASSISTANT, content=response)
        self._chat_history.append(agent_message)

        return agent_message

    @abstractmethod
    async def _process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message through the reasoning pipeline.

        Args:
            message: Input message
            **kwargs: Additional arguments

        Returns:
            Processed response
        """
        pass

    def register_plugin(self, plugin_name: str, plugin: object) -> None:
        """Register a plugin with the agent.

        Args:
            plugin_name: Name of the plugin
            plugin: Plugin instance
        """
        self._plugins[plugin_name] = plugin
        if isinstance(plugin, BaseReasoningAgent.SupportsFunctions):
            for func in plugin.functions:
                # Register provided functions with the kernel under the plugin name
                try:
                    self._kernel.add_function(plugin_name, func)
                except Exception:
                    # Keep plugin registry even if kernel registration fails
                    logger.debug("Plugin function registration skipped", exc_info=True)

    def get_chat_history(self) -> List[ChatMessageContent]:
        """Get the chat history.

        Returns:
            List of chat messages
        """
        return self._chat_history.copy()

    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self._chat_history.clear()

    async def plan(self, goal: str) -> List[str]:
        """Create a plan to achieve a goal.

        Args:
            goal: Goal to achieve

        Returns:
            List of steps to achieve the goal
        """
        # Default implementation - can be overridden
        planning_prompt = f"""
        Create a step-by-step plan to achieve the following goal:
        {goal}
        
        Provide the plan as a numbered list of concrete actions.
        """

        response = await self._process_message(planning_prompt)

        # Parse response into steps
        steps = [line.strip() for line in response.split("\n") if line.strip() and re.match(r"^\d+\.", line.strip())]

        return steps

    async def execute_step(self, step: str) -> str:
        """Execute a single step from a plan.

        Args:
            step: Step to execute

        Returns:
            Result of executing the step
        """
        execution_prompt = f"""
        Execute the following step and provide the result:
        {step}
        
        Be specific and detailed in your response.
        """

        return await self._process_message(execution_prompt)
