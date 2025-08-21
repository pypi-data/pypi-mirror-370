"""Unit tests for AgentOrchestrator."""

import pytest
from unittest.mock import Mock, AsyncMock

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatMessageContent

from reasoning_kernel.agents.agent_orchestrator import (
    AgentOrchestrator,
    Task,
    TaskStatus,
)
from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent


class MockAgent(BaseReasoningAgent):
    """Mock agent for testing."""

    async def _process_message(self, message: str, **kwargs):
        return f"Mock response: {message}"


class TestAgentOrchestrator:
    """Test suite for AgentOrchestrator."""

    @pytest.fixture
    def kernel(self):
        """Create a mock kernel."""
        return Mock(spec=Kernel)

    @pytest.fixture
    def orchestrator(self, kernel):
        """Create an orchestrator."""
        return AgentOrchestrator(kernel, max_concurrent_tasks=2)

    @pytest.fixture
    def mock_agent(self, kernel):
        """Create a mock agent."""
        agent = MockAgent(
            name="mock_agent",
            kernel=kernel,
        )
        agent.invoke = AsyncMock(return_value=ChatMessageContent(role="assistant", content="Mock response"))
        return agent

    def test_register_agent(self, orchestrator, mock_agent):
        """Test registering an agent."""
        orchestrator.register_agent(mock_agent)

        assert "mock_agent" in orchestrator._agents
        assert orchestrator._agents["mock_agent"] == mock_agent

    def test_unregister_agent(self, orchestrator, mock_agent):
        """Test unregistering an agent."""
        orchestrator.register_agent(mock_agent)
        orchestrator.unregister_agent("mock_agent")

        assert "mock_agent" not in orchestrator._agents

    def test_add_task(self, orchestrator):
        """Test adding a task."""
        task = Task(
            task_id="task1",
            description="Test task",
        )

        orchestrator.add_task(task)

        assert "task1" in orchestrator._tasks
        assert orchestrator._tasks["task1"] == task

    @pytest.mark.asyncio
    async def test_execute_single_task(self, orchestrator, mock_agent):
        """Test executing a single task."""
        orchestrator.register_agent(mock_agent)

        task = Task(
            task_id="task1",
            description="Test task",
        )
        orchestrator.add_task(task)

        results = await orchestrator.execute_tasks()

        assert "task1" in results
        assert results["task1"] == "Mock response"
        assert task.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_tasks_with_dependencies(self, orchestrator, mock_agent):
        """Test executing tasks with dependencies."""
        orchestrator.register_agent(mock_agent)

        task1 = Task(task_id="task1", description="First task")
        task2 = Task(task_id="task2", description="Second task", dependencies=["task1"])
        task3 = Task(task_id="task3", description="Third task", dependencies=["task1", "task2"])

        orchestrator.add_task(task1)
        orchestrator.add_task(task2)
        orchestrator.add_task(task3)

        results = await orchestrator.execute_tasks()

        assert len(results) == 3
        assert all(task_id in results for task_id in ["task1", "task2", "task3"])

    @pytest.mark.asyncio
    async def test_task_assignment(self, orchestrator, kernel):
        """Test task assignment to specific agents."""
        agent1 = MockAgent(name="agent1", kernel=kernel)
        agent2 = MockAgent(name="agent2", kernel=kernel)

        agent1.invoke = AsyncMock(return_value=ChatMessageContent(role="assistant", content="Agent1 response"))
        agent2.invoke = AsyncMock(return_value=ChatMessageContent(role="assistant", content="Agent2 response"))

        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)

        task1 = Task(task_id="task1", description="Task for agent1", assigned_agent="agent1")
        task2 = Task(task_id="task2", description="Task for agent2", assigned_agent="agent2")

        orchestrator.add_task(task1)
        orchestrator.add_task(task2)

        results = await orchestrator.execute_tasks()

        assert results["task1"] == "Agent1 response"
        assert results["task2"] == "Agent2 response"

    @pytest.mark.asyncio
    async def test_coordinate_discussion(self, orchestrator, mock_agent):
        """Test coordinating a discussion between agents."""
        orchestrator.register_agent(mock_agent)

        messages = await orchestrator.coordinate_discussion(topic="AI Ethics", rounds=2)

        assert len(messages) == 2  # 1 agent * 2 rounds
        assert all(isinstance(msg, ChatMessageContent) for msg in messages)

    @pytest.mark.asyncio
    async def test_aggregate_results(self, orchestrator, mock_agent):
        """Test aggregating results."""
        orchestrator.register_agent(mock_agent)

        results = ["Result 1", "Result 2", "Result 3"]

        summary = await orchestrator.aggregate_results(results, aggregation_method="summary")

        assert summary == "Mock response"
        mock_agent.invoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator, mock_agent):
        """Test error handling in task execution."""
        mock_agent.invoke = AsyncMock(side_effect=Exception("Test error"))
        orchestrator.register_agent(mock_agent)

        task = Task(task_id="error_task", description="This will fail")
        orchestrator.add_task(task)

        results = await orchestrator.execute_tasks()

        assert "error_task" in results
        assert "error" in results["error_task"]
        assert task.status == TaskStatus.FAILED
        assert task.error == "Test error"

    @pytest.mark.asyncio
    async def test_no_agent_available(self, orchestrator):
        """Test handling when no agent is available."""
        task = Task(task_id="task1", description="No agent task")
        orchestrator.add_task(task)

        results = await orchestrator.execute_tasks()

        assert "task1" in results
        assert "error" in results["task1"]
        assert "No suitable agent found" in results["task1"]["error"]
