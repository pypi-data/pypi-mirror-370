"""Unit tests for BaseReasoningAgent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatMessageContent

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.agents.reasoning_agent import ReasoningAgent
from reasoning_kernel.core.kernel_manager import KernelManager


class TestBaseReasoningAgent:
    """Test suite for BaseReasoningAgent."""

    @pytest.fixture
    def kernel(self):
        """Create a mock kernel."""
        kernel = Mock(spec=Kernel)
        kernel.get_service = Mock(return_value=None)
        kernel.add_function = Mock()
        return kernel

    @pytest.fixture
    def agent(self, kernel):
        """Create a test agent."""

        class TestAgent(BaseReasoningAgent):
            async def _process_message(self, message: str, **kwargs):
                return f"Processed: {message}"

        return TestAgent(
            name="test_agent",
            kernel=kernel,
            description="Test agent",
            instructions="Test instructions",
        )

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent, kernel):
        """Test agent initialization."""
        assert agent.name == "test_agent"
        assert agent.description == "Test agent"
        assert agent.instructions == "Test instructions"
        assert agent.kernel == kernel
        assert len(agent.get_chat_history()) == 0

    @pytest.mark.asyncio
    async def test_invoke_message(self, agent):
        """Test invoking agent with a message."""
        response = await agent.invoke("Hello, agent!")

        assert isinstance(response, ChatMessageContent)
        assert response.role == "assistant"
        assert response.content == "Processed: Hello, agent!"

        # Check chat history
        history = agent.get_chat_history()
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "Hello, agent!"
        assert history[1].role == "assistant"
        assert history[1].content == "Processed: Hello, agent!"

    @pytest.mark.asyncio
    async def test_clear_chat_history(self, agent):
        """Test clearing chat history."""
        await agent.invoke("Message 1")
        await agent.invoke("Message 2")

        assert len(agent.get_chat_history()) == 4

        agent.clear_chat_history()
        assert len(agent.get_chat_history()) == 0

    @pytest.mark.asyncio
    async def test_register_plugin(self, agent, kernel):
        """Test registering a plugin."""
        mock_plugin = Mock()
        mock_plugin.functions = [Mock(), Mock()]

        agent.register_plugin("test_plugin", mock_plugin)

        assert "test_plugin" in agent._plugins
        assert kernel.add_function.call_count == 2

    @pytest.mark.asyncio
    async def test_plan_creation(self, agent):
        """Test plan creation."""
        with patch.object(agent, "_process_message", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = """
            1. First step
            2. Second step
            3. Third step
            """

            steps = await agent.plan("Build a web application")

            assert len(steps) == 3
            assert "1. First step" in steps
            assert "2. Second step" in steps
            assert "3. Third step" in steps

    @pytest.mark.asyncio
    async def test_execute_step(self, agent):
        """Test executing a plan step."""
        result = await agent.execute_step("Deploy application")

        assert "Processed:" in result
        assert "Execute the following step" in result


class TestReasoningAgent:
    """Test suite for ReasoningAgent."""

    @pytest.fixture
    def kernel_manager(self):
        """Create a kernel manager."""
        manager = KernelManager(
            {
                "openai_api_key": "test_key",
                "openai_model_id": "gpt-4",
            }
        )
        return manager

    @pytest.fixture
    def reasoning_agent(self, kernel_manager):
        """Create a reasoning agent."""
        kernel = Mock(spec=Kernel)
        chat_service = AsyncMock()
        chat_service.get_chat_message_content = AsyncMock(return_value=Mock(content="Test response"))
        kernel.get_service = Mock(return_value=chat_service)

        return ReasoningAgent(
            name="reasoning_agent",
            kernel=kernel,
            reasoning_style="analytical",
        )

    @pytest.mark.asyncio
    async def test_reasoning_styles(self, reasoning_agent):
        """Test different reasoning styles."""
        styles = ["analytical", "creative", "systematic"]

        for style in styles:
            reasoning_agent._reasoning_style = style
            prompt = reasoning_agent._build_reasoning_prompt("Test message")

            assert "Test message" in prompt
            if style == "analytical":
                assert "Analyze" in prompt
            elif style == "creative":
                assert "creative" in prompt.lower()
            elif style == "systematic":
                assert "systematic" in prompt.lower()

    @pytest.mark.asyncio
    async def test_analyze_function(self, reasoning_agent):
        """Test the analyze kernel function."""
        result = await reasoning_agent.analyze("AI ethics")

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_solve_function(self, reasoning_agent):
        """Test the solve kernel function."""
        result = await reasoning_agent.solve("Complex problem")

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_brainstorm_function(self, reasoning_agent):
        """Test the brainstorm kernel function."""
        result = await reasoning_agent.brainstorm("Innovation", count=3)

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling when no chat service is available."""
        kernel = Mock(spec=Kernel)
        kernel.get_service = Mock(return_value=None)

        agent = ReasoningAgent(
            name="error_agent",
            kernel=kernel,
        )

        result = await agent._process_message("Test message")

        assert "Error:" in result
        assert "No chat service configured" in result
