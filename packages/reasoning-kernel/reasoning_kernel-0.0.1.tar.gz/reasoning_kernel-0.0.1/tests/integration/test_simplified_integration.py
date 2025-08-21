"""
Simplified Integration Tests for MSA Reasoning Kernel

Focused integration testing covering essential cross-component interactions.
"""

import time
from typing import Dict, Any

from unittest.mock import Mock, AsyncMock

from tests.framework.enhanced_testing import (
    integration_test,
    performance_test,
    retry_on_failure,
    assert_agent_response_quality,
    assert_performance_acceptable,
    MockAgentFactory,
    TestDataGenerator,
)

from reasoning_kernel.agents.enhanced_orchestrator import (
    OrchestrationStrategy,
    AgentCapability,
    TaskExecutionPlan,
)
from reasoning_kernel.agents.orchestration_integration import OrchestrationIntegration
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class TestBasicOrchestrationIntegration:
    """Basic integration tests for orchestration components."""

    @integration_test("orchestration")
    async def test_orchestration_integration_initialization(self, environment: Dict[str, Any]):
        """Test that orchestration integration initializes correctly."""
        # Create integration with test configuration
        integration = OrchestrationIntegration(
            kernel=environment["kernel"],
            config={
                "max_concurrent_tasks": 3,
                "enable_state_persistence": False,
                "adaptive_load_balancing": True,
            },
        )

        # Test initialization
        await integration.initialize()
        assert integration._is_initialized

        # Register test agents
        for agent in environment["agents"].values():
            await integration.register_agent(agent)

        # Verify agents were registered
        assert len(integration._agents) == len(environment["agents"])

        # Test shutdown
        await integration.shutdown()
        assert not integration._is_initialized

    @integration_test("orchestration")
    async def test_orchestration_plan_creation_and_execution(self, environment: Dict[str, Any]):
        """Test creating and executing orchestration plans."""
        orchestrator = environment["orchestrator"]

        # Register test agents
        for agent in environment["agents"].values():
            await orchestrator.register_agent(agent)

        # Create execution plan
        plan = await orchestrator.create_execution_plan(
            task_description="Test task for orchestration",
            strategy=OrchestrationStrategy.SEQUENTIAL,
            requirements={"timeout": 5.0},
        )

        # Verify plan creation
        assert isinstance(plan, TaskExecutionPlan)
        assert plan.strategy == OrchestrationStrategy.SEQUENTIAL
        assert len(plan.agent_assignments) > 0

        # Execute the plan
        results = await orchestrator.execute_plan(plan)

        # Verify execution results
        assert results["status"] == "completed"
        assert "execution_time" in results
        assert results["execution_time"] > 0

    @integration_test("state_management")
    async def test_state_management_with_sessions(self, environment: Dict[str, Any]):
        """Test state management functionality with sessions."""
        state_manager = environment["state_manager"]

        # Create test session
        session_id = "test_integration_session"
        await state_manager.create_session(session_id)

        # Update session state
        await state_manager.update_state(session_id, "test_update", {"step": "initial", "data": "test_data"})

        # Verify state was recorded
        session_state = await state_manager.get_session_state(session_id)
        assert session_state is not None
        assert session_state.session_id == session_id

        # Verify state changes
        changes = await state_manager.get_state_changes(session_id)
        assert len(changes) > 0

        # Create checkpoint
        checkpoint = await state_manager.create_checkpoint(session_id, "test_checkpoint")
        assert checkpoint is not None

        # Verify checkpoint can be restored
        await state_manager.restore_checkpoint(session_id, checkpoint.checkpoint_id)

    @integration_test("communication")
    async def test_communication_manager_basic_functionality(self, environment: Dict[str, Any]):
        """Test basic communication manager functionality."""
        communication_manager = environment["communication_manager"]
        agents = list(environment["agents"].values())

        if len(agents) < 2:
            # Add more agents if needed
            factory = MockAgentFactory()
            extra_agent = factory.create_basic_agent("extra_agent", environment["kernel"])
            agents.append(extra_agent)
            communication_manager.agents["extra_agent"] = extra_agent

        sender = agents[0]
        receiver = agents[1]

        # Test direct communication
        response = await communication_manager.send_direct_message(
            from_agent=sender.name, to_agent=receiver.name, message="Test direct message", context={"test": True}
        )

        # Verify communication
        assert response is not None
        assert_agent_response_quality(response, min_length=5)

        # Test broadcast communication
        responses = await communication_manager.broadcast_message(
            from_agent=sender.name,
            to_agents=[agent.name for agent in agents[1:]],
            message="Test broadcast message",
            context={"broadcast": True},
        )

        # Verify broadcast
        assert len(responses) == len(agents) - 1
        for response in responses:
            assert_agent_response_quality(response, min_length=5)


class TestPerformanceIntegration:
    """Performance integration tests."""

    @integration_test("performance")
    @performance_test(target_duration=2.0, max_memory_mb=100.0)
    async def test_parallel_orchestration_performance(self, environment: Dict[str, Any]):
        """Test parallel orchestration performance."""
        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create fast agents for parallel testing
        fast_agents = []
        for i in range(5):
            agent = factory.create_basic_agent(f"fast_agent_{i}", kernel)
            agent.invoke = AsyncMock(return_value=Mock(content=f"Fast response {i}"))
            fast_agents.append(agent)
            await orchestrator.register_agent(agent)

        # Create and execute parallel plan
        plan = await orchestrator.create_execution_plan(
            task_description="Parallel performance test",
            strategy=OrchestrationStrategy.PARALLEL,
            requirements={"agents": [agent.name for agent in fast_agents]},
        )

        # Execute with timing
        start_time = time.perf_counter()
        results = await orchestrator.execute_plan(plan)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Verify performance
        assert results["status"] == "completed"
        assert_performance_acceptable(execution_time, 1.5, tolerance=0.5)

    @integration_test("performance")
    @performance_test(target_duration=1.0, max_memory_mb=75.0)
    async def test_state_management_performance(self, environment: Dict[str, Any]):
        """Test state management performance with rapid updates."""
        state_manager = environment["state_manager"]

        # Create session
        session_id = "performance_test_session"
        await state_manager.create_session(session_id)

        # Perform rapid state updates
        num_updates = 25
        start_time = time.perf_counter()

        for i in range(num_updates):
            await state_manager.update_state(session_id, f"update_{i}", {"iteration": i, "timestamp": time.time()})

        end_time = time.perf_counter()
        update_time = end_time - start_time

        # Verify all updates were recorded
        changes = await state_manager.get_state_changes(session_id)
        assert len(changes) >= num_updates

        # Verify performance
        average_update_time = update_time / num_updates
        assert average_update_time < 0.02, f"State updates too slow: {average_update_time:.4f}s per update"


class TestErrorHandlingIntegration:
    """Error handling integration tests."""

    @integration_test("error_handling")
    @retry_on_failure(max_retries=2)
    async def test_orchestration_with_failing_agents(self, environment: Dict[str, Any]):
        """Test orchestration error handling with failing agents."""
        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create mix of working and failing agents
        working_agent = factory.create_basic_agent("working_agent", kernel)
        failing_agent = factory.create_failing_agent("failing_agent", 1.0, kernel)  # Always fails

        # Register agents
        await orchestrator.register_agent(working_agent)
        await orchestrator.register_agent(failing_agent)

        # Create plan that includes failing agent
        plan = await orchestrator.create_execution_plan(
            task_description="Test with failing agent",
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )

        # Execute plan (should handle failures gracefully)
        try:
            results = await orchestrator.execute_plan(plan)
            # Some strategies might complete despite partial failures
            assert results["status"] in ["completed", "partial_success", "failed"]
        except Exception as e:
            # Acceptable if orchestration fails but provides error details
            assert "error" in str(e).lower() or "fail" in str(e).lower()

    @integration_test("error_handling")
    async def test_state_recovery_after_failure(self, environment: Dict[str, Any]):
        """Test state recovery capabilities after failures."""
        state_manager = environment["state_manager"]

        # Create session
        session_id = "recovery_test_session"
        await state_manager.create_session(session_id)

        # Set initial state
        await state_manager.update_state(session_id, "initial", {"step": 1})

        # Create checkpoint
        checkpoint = await state_manager.create_checkpoint(session_id, "before_failure")

        # Simulate state corruption by updating to invalid state
        await state_manager.update_state(session_id, "corrupted", {"step": "invalid"})

        # Recover from checkpoint
        await state_manager.restore_checkpoint(session_id, checkpoint.checkpoint_id)

        # Verify recovery
        recovered_state = await state_manager.get_session_state(session_id)
        assert recovered_state is not None
        assert recovered_state.session_id == session_id


class TestEndToEndWorkflow:
    """End-to-end workflow integration tests."""

    @integration_test("end_to_end")
    @performance_test(target_duration=3.0, max_memory_mb=150.0)
    async def test_complete_reasoning_workflow(self, environment: Dict[str, Any]):
        """Test complete end-to-end reasoning workflow."""
        # Use the full integration for comprehensive testing
        integration = OrchestrationIntegration(
            kernel=environment["kernel"],
            config={
                "max_concurrent_tasks": 3,
                "enable_state_persistence": False,  # For testing
            },
        )

        await integration.initialize()

        # Create specialized reasoning agents
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Analysis capabilities
        analysis_caps = {
            "analysis": AgentCapability(
                name="analysis",
                skill_level=0.9,
                estimated_duration=1.0,
                success_rate=0.95,
                resource_requirements={},
            ),
        }

        analyzer = factory.create_specialized_agent("analyzer", analysis_caps, kernel)
        analyzer.invoke = AsyncMock(return_value=Mock(content="Analysis complete: problem broken down"))

        # Reasoning capabilities
        reasoning_caps = {
            "reasoning": AgentCapability(
                name="reasoning",
                skill_level=0.85,
                estimated_duration=2.0,
                success_rate=0.9,
                resource_requirements={},
            ),
        }

        reasoner = factory.create_specialized_agent("reasoner", reasoning_caps, kernel)
        reasoner.invoke = AsyncMock(return_value=Mock(content="Reasoning complete: solution found"))

        # Register agents
        await integration.register_agent(analyzer, analysis_caps)
        await integration.register_agent(reasoner, reasoning_caps)

        # Execute multi-phase workflow
        # Phase 1: Analysis
        analysis_plan = await integration._orchestrator.create_execution_plan(
            task_description="Analyze complex problem",
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )

        analysis_results = await integration._orchestrator.execute_plan(analysis_plan)
        assert analysis_results["status"] == "completed"

        # Phase 2: Reasoning
        reasoning_plan = await integration._orchestrator.create_execution_plan(
            task_description="Apply reasoning to analysis",
            strategy=OrchestrationStrategy.SEQUENTIAL,
        )

        reasoning_results = await integration._orchestrator.execute_plan(reasoning_plan)
        assert reasoning_results["status"] == "completed"

        # Verify complete workflow
        total_execution_time = analysis_results["execution_time"] + reasoning_results["execution_time"]
        assert total_execution_time > 0
        assert total_execution_time < 5.0  # Should complete in reasonable time

        await integration.shutdown()


# Test utility functions
def generate_test_scenarios():
    """Generate test scenarios for integration testing."""
    generator = TestDataGenerator()

    return {
        "reasoning_scenarios": generator.generate_reasoning_scenarios(count=3),
        "communication_scenarios": generator.generate_agent_communication_scenarios(count=2),
    }


if __name__ == "__main__":
    # Run integration tests
    import pytest

    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--maxfail=3",
            "-x",
        ]
    )
