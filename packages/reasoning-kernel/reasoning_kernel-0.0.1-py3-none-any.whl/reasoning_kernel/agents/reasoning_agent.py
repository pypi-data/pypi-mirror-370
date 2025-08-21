"""Concrete implementation of a reasoning agent."""

import logging
from typing import Any, Dict, Optional

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function


logger = logging.getLogger(__name__)


class ReasoningAgent(BaseReasoningAgent):
    """Concrete reasoning agent implementation."""

    def __init__(
        self,
        name: str,
        kernel: Kernel,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        execution_settings: Optional[Dict[str, Any]] = None,
        reasoning_style: str = "analytical",
    ):
        """Initialize the reasoning agent.

        Args:
            name: Agent name
            kernel: Semantic Kernel instance
            description: Agent description
            instructions: Agent instructions
            execution_settings: Execution settings
            reasoning_style: Style of reasoning (analytical, creative, systematic)
        """
        super().__init__(
            name=name,
            kernel=kernel,
            description=description,
            instructions=instructions,
            execution_settings=execution_settings,
        )
        self._reasoning_style = reasoning_style

    async def _process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message through the reasoning pipeline.

        Args:
            message: Input message
            **kwargs: Additional arguments

        Returns:
            Processed response
        """
        # Build reasoning prompt based on style (currently not used directly)
        _ = self._build_reasoning_prompt(message)

        # Get chat completion service
        chat_service = self._kernel.get_service("chat_completion")

        if not chat_service:
            logger.error("No chat completion service available")
            return "Error: No chat service configured"

        # Create execution settings
        settings = self._execution_settings.copy()
        settings.update(kwargs.get("execution_settings", {}))

        # Execute completion
        try:
            response = await chat_service.get_chat_message_content(
                chat_history=self._chat_history,
                settings=settings,
            )
            return response.content
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Error processing message: {str(e)}"

    def _build_reasoning_prompt(self, message: str) -> str:
        """Build a reasoning prompt based on the agent's style.

        Args:
            message: Input message

        Returns:
            Formatted reasoning prompt
        """
        style_prompts = {
            "analytical": f"""
                Analyze the following message step by step:
                {message}
                
                Consider:
                1. What are the key components?
                2. What are the relationships between them?
                3. What patterns or principles apply?
                4. What are the implications?
                
                Provide a thorough analytical response.
            """,
            "creative": f"""
                Explore creative solutions for:
                {message}
                
                Think about:
                1. Unconventional approaches
                2. Novel combinations of ideas
                3. Metaphors and analogies
                4. "What if" scenarios
                
                Provide an innovative and creative response.
            """,
            "systematic": f"""
                Address the following systematically:
                {message}
                
                Follow this structure:
                1. Define the problem/question clearly
                2. Identify all relevant factors
                3. Develop a methodical approach
                4. Execute step by step
                5. Verify and validate results
                
                Provide a systematic and thorough response.
            """,
        }

        return style_prompts.get(self._reasoning_style, f"{self.instructions}\n\n{message}")

    @kernel_function(name="analyze", description="Analyze a topic in depth")
    async def analyze(self, topic: str) -> str:
        """Analyze a topic in depth.

        Args:
            topic: Topic to analyze

        Returns:
            Analysis result
        """
        prompt = f"Provide an in-depth analysis of: {topic}"
        return await self._process_message(prompt)

    @kernel_function(name="solve", description="Solve a problem")
    async def solve(self, problem: str) -> str:
        """Solve a problem.

        Args:
            problem: Problem to solve

        Returns:
            Solution
        """
        prompt = f"Solve the following problem: {problem}"
        return await self._process_message(prompt)

    @kernel_function(name="brainstorm", description="Brainstorm ideas")
    async def brainstorm(self, topic: str, count: int = 5) -> str:
        """Brainstorm ideas on a topic.

        Args:
            topic: Topic to brainstorm about
            count: Number of ideas to generate

        Returns:
            List of ideas
        """
        prompt = f"Brainstorm {count} innovative ideas related to: {topic}"
        return await self._process_message(prompt)
