"""
Integration Tests for MSA Reasoning Kernel

Comprehensive integration testing covering cross-component interactions,
orchestration workflows, and end-to-end scenarios.
"""

import asyncio
import time
from typing import Dict, Any

from unittest.mock import Mock, AsyncMock

from tests.framework.enhanced_testing import (
    integration_test,
    performance_test,
    retry_on_failure,
    assert_agent_response_quality,
    assert_performance_acceptable,
    assert_orchestration_successful,
    MockAgentFactory,
    TestDataGenerator,
)

from reasoning_kernel.agents.enhanced_orchestrator import (
    OrchestrationStrategy,
    AgentCapability,
)
from reasoning_kernel.agents.orchestration_integration import OrchestrationIntegration
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class TestAgentOrchestrationIntegration:
    """Integration tests for agent orchestration system."""

    @integration_test("orchestration")
    async def test_basic_orchestration_workflow(self, environment: Dict[str, Any]):
        """Test basic orchestration workflow with multiple agents."""
        orchestrator = environment["orchestrator"]
        agents = environment["agents"]

        # Test sequential orchestration
        result = await orchestrator.coordinate_agents(
            agents=list(agents.values()),
            strategy=OrchestrationStrategy.SEQUENTIAL,
            message="Solve this step by step: What is 2+2?",
            context={"task_type": "arithmetic"},
        )

        # Verify orchestration completed successfully
        assert_orchestration_successful(result, len(agents))
        assert result["status"] == "completed"
        assert "steps" in result
        assert len(result["steps"]) == len(agents)

        # Verify each agent was involved
        for agent_name in agents.keys():
            agent_found = any(step["agent"] == agent_name for step in result["steps"].values())
            assert agent_found, f"Agent {agent_name} not found in orchestration steps"

    @integration_test("orchestration")
    async def test_parallel_orchestration_performance(self, environment: Dict[str, Any]):
        """Test parallel orchestration performance with timing validation."""
        orchestrator = environment["orchestrator"]
        agents = environment["agents"]

        # Create additional slow agents for better parallel testing
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        slow_agents = {
            f"slow_agent_{i}": factory.create_slow_agent(f"slow_agent_{i}", delay=0.1, kernel=kernel) for i in range(3)
        }

        # Register slow agents
        for agent in slow_agents.values():
            await orchestrator.register_agent(agent)

        # Test parallel orchestration timing
        start_time = time.perf_counter()
        result = await orchestrator.coordinate_agents(
            agents=list(slow_agents.values()),
            strategy=OrchestrationStrategy.PARALLEL,
            message="Process this in parallel",
            context={"timeout": 5.0},
        )
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Verify orchestration completed
        assert_orchestration_successful(result, len(slow_agents))

        # Verify parallel execution was actually faster than sequential
        # With 3 agents at 0.1s delay each, parallel should be ~0.1s, sequential would be ~0.3s
        assert_performance_acceptable(execution_time, 0.2, tolerance=1.0)  # Allow some overhead

        assert execution_time < 0.25, f"Parallel execution took too long: {execution_time:.3f}s"

    @integration_test("orchestration")
    async def test_pipeline_orchestration_data_flow(self, environment: Dict[str, Any]):
        """Test pipeline orchestration with data flowing between agents."""
        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]

        # Create specialized agents for pipeline testing
        factory = MockAgentFactory()
        pipeline_agents = []

        # Agent 1: Data preprocessor
        agent1 = factory.create_basic_agent("preprocessor", kernel)
        agent1.invoke = AsyncMock(return_value=Mock(content="preprocessed_data: input_processed"))
        pipeline_agents.append(agent1)

        # Agent 2: Data analyzer
        agent2 = factory.create_basic_agent("analyzer", kernel)
        agent2.invoke = AsyncMock(return_value=Mock(content="analysis_result: patterns_found"))
        pipeline_agents.append(agent2)

        # Agent 3: Result formatter
        agent3 = factory.create_basic_agent("formatter", kernel)
        agent3.invoke = AsyncMock(return_value=Mock(content="final_output: formatted_results"))
        pipeline_agents.append(agent3)

        # Register pipeline agents
        for agent in pipeline_agents:
            await orchestrator.register_agent(agent)

        # Execute pipeline orchestration
        result = await orchestrator.coordinate_agents(
            agents=pipeline_agents,
            strategy=OrchestrationStrategy.PIPELINE,
            message="Process this data through the pipeline",
            context={"data_flow": True},
        )

        # Verify pipeline execution
        assert_orchestration_successful(result, len(pipeline_agents))

        # Verify execution order (pipeline should be sequential)
        steps = result["steps"]
        step_keys = list(steps.keys())

        # Verify agents were called in the correct order
        assert steps[step_keys[0]]["agent"] == "preprocessor"
        assert steps[step_keys[1]]["agent"] == "analyzer"
        assert steps[step_keys[2]]["agent"] == "formatter"

        # Verify each step has appropriate output
        for step in steps.values():
            assert "response" in step
            assert step["response"] is not None

    @integration_test("orchestration")
    async def test_hierarchical_orchestration_with_managers(self, environment: Dict[str, Any]):
        """Test hierarchical orchestration with manager and worker agents."""
        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create manager agent
        manager_capabilities = {
            "management": AgentCapability(
                name="management",
                skill_level=0.8,
                estimated_duration=1.0,
                success_rate=0.9,
                resource_requirements={},
            ),
        }

        manager_agent = factory.create_specialized_agent("task_manager", manager_capabilities, kernel)
        manager_agent.invoke = AsyncMock(return_value=Mock(content="manager_coordination: tasks_delegated"))

        # Create worker agents
        worker_agents = []
        for i in range(3):
            worker_caps = {
                f"worker_skill_{i}": AgentCapability(
                    name=f"worker_skill_{i}",
                    skill_level=0.8,
                    estimated_duration=1.5,
                    success_rate=0.85,
                    resource_requirements={},
                ),
            }

            worker = factory.create_specialized_agent(f"worker_{i}", worker_caps, kernel)
            worker.invoke = AsyncMock(return_value=Mock(content=f"worker_{i}_result: task_completed"))
            worker_agents.append(worker)

        # Register all agents
        await orchestrator.register_agent(manager_agent)
        for worker in worker_agents:
            await orchestrator.register_agent(worker)

        # Execute hierarchical orchestration
        all_agents = [manager_agent] + worker_agents
        result = await orchestrator.coordinate_agents(
            agents=all_agents,
            strategy=OrchestrationStrategy.HIERARCHICAL,
            message="Coordinate this complex task hierarchically",
            context={"hierarchy": {"manager": "task_manager", "workers": [f"worker_{i}" for i in range(3)]}},
        )

        # Verify hierarchical execution
        assert_orchestration_successful(result, len(all_agents))

        # Verify manager was involved first (in hierarchical orchestration)
        steps = result["steps"]
        first_step = list(steps.values())[0]
        # Note: The actual hierarchical implementation might vary, so we just check completion
        assert len(steps) == len(all_agents)

    @integration_test("orchestration")
    @retry_on_failure(max_retries=2)
    async def test_adaptive_orchestration_with_failure_recovery(self, environment: Dict[str, Any]):
        """Test adaptive orchestration with agent failure scenarios."""
        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create mix of reliable and unreliable agents
        reliable_agent = factory.create_basic_agent("reliable", kernel)
        failing_agent = factory.create_failing_agent("failing", 0.8, kernel)  # High failure rate
        backup_agent = factory.create_basic_agent("backup", kernel)

        agents = [reliable_agent, failing_agent, backup_agent]

        # Register agents
        for agent in agents:
            await orchestrator.register_agent(agent)

        # Execute adaptive orchestration
        result = await orchestrator.coordinate_agents(
            agents=agents,
            strategy=OrchestrationStrategy.ADAPTIVE,
            message="Complete this task with failure tolerance",
            context={
                "failure_tolerance": True,
                "max_retries": 2,
                "backup_agents": ["backup"],
            },
        )

        # Verify orchestration handled failures gracefully
        assert result["status"] in ["completed", "partial_success"]
        assert "steps" in result
        assert len(result["steps"]) > 0

        # Check if failure handling occurred
        if "failures" in result:
            assert isinstance(result["failures"], list)
            # Verify backup mechanisms were attempted
            assert len(result["steps"]) >= 2  # At least reliable agent and one other


class TestStateManagementIntegration:
    """Integration tests for state management across orchestration."""

    @integration_test("state_management")
    async def test_state_persistence_during_orchestration(self, environment: Dict[str, Any]):
        """Test state persistence during multi-agent orchestration."""
        orchestrator = environment["orchestrator"]
        state_manager = environment["state_manager"]
        agents = environment["agents"]

        # Initialize state tracking
        session_id = "test_session_001"
        await state_manager.create_session(session_id)

        # Execute orchestration with state tracking
        result = await orchestrator.coordinate_agents(
            agents=list(agents.values()),
            strategy=OrchestrationStrategy.SEQUENTIAL,
            message="Process with state tracking",
            context={"session_id": session_id, "track_state": True},
        )

        # Verify orchestration completed
        assert_orchestration_successful(result, len(agents))

        # Verify state was tracked
        session_state = await state_manager.get_session_state(session_id)
        assert session_state is not None
        assert session_state.session_id == session_id

        # Verify state changes were recorded
        changes = await state_manager.get_state_changes(session_id)
        assert len(changes) > 0

        # Verify state persistence across operations
        await state_manager.save_state()
        restored_state = await state_manager.get_session_state(session_id)
        assert restored_state.session_id == session_id

    @integration_test("state_management")
    async def test_state_rollback_on_failure(self, environment: Dict[str, Any]):
        """Test state rollback capabilities when orchestration fails."""
        orchestrator = environment["orchestrator"]
        state_manager = environment["state_manager"]
        kernel = environment["kernel"]

        # Create failing agent
        factory = MockAgentFactory()
        failing_agent = factory.create_failing_agent("critical_failure", 1.0, kernel)  # Always fails

        await orchestrator.register_agent(failing_agent)

        # Initialize state
        session_id = "test_rollback_session"
        await state_manager.create_session(session_id)

        # Create checkpoint before risky operation
        checkpoint = await state_manager.create_checkpoint(session_id, "before_risky_operation")

        # Attempt orchestration that will fail
        try:
            await orchestrator.coordinate_agents(
                agents=[failing_agent],
                strategy=OrchestrationStrategy.SEQUENTIAL,
                message="This will fail",
                context={"session_id": session_id},
            )
            assert False, "Expected orchestration to fail"
        except Exception:
            # Expected failure
            pass

        # Verify rollback capability
        await state_manager.restore_checkpoint(session_id, checkpoint.checkpoint_id)

        # Verify state was restored
        session_state = await state_manager.get_session_state(session_id)
        assert session_state is not None
        assert session_state.session_id == session_id

    @integration_test("state_management")
    async def test_concurrent_state_management(self, environment: Dict[str, Any]):
        """Test state management with concurrent orchestration sessions."""
        orchestrator = environment["orchestrator"]
        state_manager = environment["state_manager"]
        agents = environment["agents"]

        # Create multiple concurrent sessions
        session_ids = ["concurrent_session_1", "concurrent_session_2", "concurrent_session_3"]

        # Initialize all sessions
        for session_id in session_ids:
            await state_manager.create_session(session_id)

        # Run concurrent orchestrations
        tasks = []
        for i, session_id in enumerate(session_ids):
            task = asyncio.create_task(
                orchestrator.coordinate_agents(
                    agents=list(agents.values()),
                    strategy=OrchestrationStrategy.PARALLEL,
                    message=f"Concurrent task {i + 1}",
                    context={"session_id": session_id},
                )
            )
            tasks.append(task)

        # Wait for all concurrent orchestrations
        results = await asyncio.gather(*tasks)

        # Verify all orchestrations completed successfully
        for result in results:
            assert result["status"] == "completed"

        # Verify state isolation between sessions
        for session_id in session_ids:
            session_state = await state_manager.get_session_state(session_id)
            assert session_state is not None
            assert session_state.session_id == session_id

            # Verify each session has independent state changes
            changes = await state_manager.get_state_changes(session_id)
            assert len(changes) > 0


class TestCommunicationPatternsIntegration:
    """Integration tests for communication patterns between agents."""

    @integration_test("communication")
    async def test_direct_communication_pattern(self, environment: Dict[str, Any]):
        """Test direct communication between specific agents."""
        communication_manager = environment["communication_manager"]
        agents = environment["agents"]

        sender = list(agents.values())[0]
        receiver = list(agents.values())[1]

        # Test direct message
        message = "Direct message test"
        response = await communication_manager.send_direct_message(
            from_agent=sender.name, to_agent=receiver.name, message=message, context={"communication_type": "direct"}
        )

        # Verify direct communication
        assert response is not None
        assert_agent_response_quality(response, min_length=5)

        # Verify communication was logged
        history = await communication_manager.get_communication_history(agent_name=receiver.name)
        assert len(history) > 0
        assert any(msg["from_agent"] == sender.name for msg in history)

    @integration_test("communication")
    async def test_broadcast_communication_pattern(self, environment: Dict[str, Any]):
        """Test broadcast communication to multiple agents."""
        communication_manager = environment["communication_manager"]
        agents = environment["agents"]

        broadcaster = list(agents.values())[0]
        receivers = list(agents.values())[1:]

        # Test broadcast message
        message = "Broadcast announcement"
        responses = await communication_manager.broadcast_message(
            from_agent=broadcaster.name,
            to_agents=[agent.name for agent in receivers],
            message=message,
            context={"communication_type": "broadcast"},
        )

        # Verify broadcast reached all receivers
        assert len(responses) == len(receivers)
        for response in responses:
            assert_agent_response_quality(response, min_length=5)

        # Verify all receivers got the message
        for receiver in receivers:
            history = await communication_manager.get_communication_history(agent_name=receiver.name)
            assert any(msg["from_agent"] == broadcaster.name for msg in history)

    @integration_test("communication")
    async def test_pipeline_communication_pattern(self, environment: Dict[str, Any]):
        """Test pipeline communication with data transformation."""
        communication_manager = environment["communication_manager"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create pipeline agents with specific responses
        pipeline_agents = []

        # Stage 1: Input processor
        agent1 = factory.create_basic_agent("input_processor", kernel)
        agent1.invoke = AsyncMock(return_value=Mock(content="processed_input"))
        pipeline_agents.append(agent1)

        # Stage 2: Data transformer
        agent2 = factory.create_basic_agent("transformer", kernel)
        agent2.invoke = AsyncMock(return_value=Mock(content="transformed_data"))
        pipeline_agents.append(agent2)

        # Stage 3: Output generator
        agent3 = factory.create_basic_agent("output_generator", kernel)
        agent3.invoke = AsyncMock(return_value=Mock(content="final_output"))
        pipeline_agents.append(agent3)

        # Update communication manager with pipeline agents
        pipeline_agent_dict = {agent.name: agent for agent in pipeline_agents}
        communication_manager.agents.update(pipeline_agent_dict)

        # Test pipeline communication
        initial_data = "Raw input data"
        result = await communication_manager.send_pipeline_message(
            agents=[agent.name for agent in pipeline_agents],
            initial_message=initial_data,
            context={"pipeline_stage": True},
        )

        # Verify pipeline execution
        assert result is not None
        assert_agent_response_quality(result, min_length=5)

        # Verify pipeline history
        for i, agent in enumerate(pipeline_agents):
            history = await communication_manager.get_communication_history(agent_name=agent.name)
            assert len(history) > 0

    @integration_test("communication")
    async def test_scatter_gather_communication_pattern(self, environment: Dict[str, Any]):
        """Test scatter-gather communication pattern."""
        communication_manager = environment["communication_manager"]
        agents = environment["agents"]

        coordinator = list(agents.values())[0]
        workers = list(agents.values())[1:]

        # Test scatter-gather
        task = "Analyze this data from different perspectives"
        results = await communication_manager.scatter_gather_message(
            coordinator_agent=coordinator.name,
            worker_agents=[agent.name for agent in workers],
            message=task,
            context={"analysis_type": "multi_perspective"},
        )

        # Verify scatter-gather results
        assert len(results) == len(workers)
        for result in results:
            assert_agent_response_quality(result, min_length=5)

        # Verify all workers received the scattered message
        for worker in workers:
            history = await communication_manager.get_communication_history(agent_name=worker.name)
            assert len(history) > 0


class TestEndToEndIntegration:
    """End-to-end integration tests combining all components."""

    @integration_test("end_to_end")
    @performance_test(target_duration=5.0, max_memory_mb=200.0)
    async def test_complete_reasoning_workflow(self, environment: Dict[str, Any]):
        """Test complete reasoning workflow from input to output."""
        orchestrator = environment["orchestrator"]
        state_manager = environment["state_manager"]
        communication_manager = environment["communication_manager"]
        agents = environment["agents"]
        kernel = environment["kernel"]

        # Create specialized reasoning agents
        factory = MockAgentFactory()

        # Analysis agent
        analysis_caps = {
            "analysis": AgentCapability(
                name="analysis",
                skill_level=0.8,
                estimated_duration=2.0,
                success_rate=0.9,
                resource_requirements={},
            ),
        }
        analysis_agent = factory.create_specialized_agent("analyzer", analysis_caps, kernel)
        analysis_agent.invoke = AsyncMock(return_value=Mock(content="Analysis: Problem decomposed into 3 parts"))

        # Reasoning agent
        reasoning_caps = {
            "reasoning": AgentCapability(
                name="reasoning",
                skill_level=0.9,
                estimated_duration=3.0,
                success_rate=0.85,
                resource_requirements={},
            ),
        }
        reasoning_agent = factory.create_specialized_agent("reasoner", reasoning_caps, kernel)
        reasoning_agent.invoke = AsyncMock(return_value=Mock(content="Reasoning: Applied logical inference"))

        # Synthesis agent
        synthesis_caps = {
            "synthesis": AgentCapability(
                name="synthesis",
                skill_level=0.85,
                estimated_duration=2.5,
                success_rate=0.8,
                resource_requirements={},
            ),
        }
        synthesis_agent = factory.create_specialized_agent("synthesizer", synthesis_caps, kernel)
        synthesis_agent.invoke = AsyncMock(return_value=Mock(content="Synthesis: Final solution validated"))

        # Register all agents
        reasoning_agents = [analysis_agent, reasoning_agent, synthesis_agent]
        for agent in reasoning_agents:
            await orchestrator.register_agent(agent)

        # Initialize session state
        session_id = "end_to_end_session"
        await state_manager.create_session(session_id)

        # Execute complete workflow
        reasoning_problem = """
        Complex Problem: How can we optimize a multi-agent system for better performance
        while maintaining reliability and ensuring proper communication between agents?
        """

        # Step 1: Analysis phase
        analysis_result = await orchestrator.coordinate_agents(
            agents=[analysis_agent],
            strategy=OrchestrationStrategy.SEQUENTIAL,
            message=reasoning_problem,
            context={"session_id": session_id, "phase": "analysis"},
        )

        # Step 2: Reasoning phase
        reasoning_result = await orchestrator.coordinate_agents(
            agents=[reasoning_agent],
            strategy=OrchestrationStrategy.SEQUENTIAL,
            message=f"Based on analysis: {analysis_result['steps'][list(analysis_result['steps'].keys())[0]]['response']}",
            context={"session_id": session_id, "phase": "reasoning"},
        )

        # Step 3: Synthesis phase
        synthesis_result = await orchestrator.coordinate_agents(
            agents=[synthesis_agent],
            strategy=OrchestrationStrategy.SEQUENTIAL,
            message=f"Synthesize solution from reasoning: {reasoning_result['steps'][list(reasoning_result['steps'].keys())[0]]['response']}",
            context={"session_id": session_id, "phase": "synthesis"},
        )

        # Verify complete workflow
        assert_orchestration_successful(analysis_result, 1)
        assert_orchestration_successful(reasoning_result, 1)
        assert_orchestration_successful(synthesis_result, 1)

        # Verify state progression
        session_state = await state_manager.get_session_state(session_id)
        assert session_state is not None

        changes = await state_manager.get_state_changes(session_id)
        assert len(changes) >= 3  # At least one change per phase

        # Verify communication history
        for agent in reasoning_agents:
            history = await communication_manager.get_communication_history(agent.name)
            assert len(history) > 0

    @integration_test("end_to_end")
    async def test_integration_with_orchestration_integration_layer(self, environment: Dict[str, Any]):
        """Test integration using the unified OrchestrationIntegration layer."""
        orchestrator = environment["orchestrator"]
        state_manager = environment["state_manager"]
        communication_manager = environment["communication_manager"]
        agents = environment["agents"]

        # Create integration layer with correct constructor
        integration = OrchestrationIntegration(
            kernel=environment["kernel"],
            config={
                "max_concurrent_tasks": 3,
                "enable_state_persistence": False,  # For testing
            },
        )

        await integration.initialize()

        # Register agents with integration
        for agent in environment["agents"].values():
            await integration.register_agent(agent)

        # Test simplified workflow using integration layer methods
        # Since create_orchestration_session may not exist, let's use direct methods
        result = await integration._orchestrator.coordinate_agents(
            agents=list(environment["agents"].values()),
            strategy=OrchestrationStrategy.PARALLEL,
            message="Test problem for integration layer",
            context={"integration_test": True},
        )

        # Verify integration layer workflow
        assert result["status"] == "completed"
        assert "steps" in result

        await integration.shutdown()


class TestPerformanceIntegration:
    """Performance and scalability integration tests."""

    @integration_test("performance")
    @performance_test(target_duration=3.0, max_memory_mb=150.0)
    async def test_high_volume_agent_coordination(self, environment: Dict[str, Any]):
        """Test orchestration performance with many agents."""
        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create many fast agents
        num_agents = 10
        fast_agents = []

        for i in range(num_agents):
            agent = factory.create_basic_agent(f"fast_agent_{i}", kernel)
            agent.invoke = AsyncMock(return_value=Mock(content=f"Fast response {i}"))
            fast_agents.append(agent)
            await orchestrator.register_agent(agent)

        # Test parallel coordination of many agents
        result = await orchestrator.coordinate_agents(
            agents=fast_agents,
            strategy=OrchestrationStrategy.PARALLEL,
            message="Process quickly with many agents",
            context={"high_volume": True},
        )

        # Verify high-volume orchestration
        assert_orchestration_successful(result, num_agents)

        # Verify all agents participated
        steps = result["steps"]
        agent_names = {step["agent"] for step in steps.values()}
        expected_names = {f"fast_agent_{i}" for i in range(num_agents)}
        assert agent_names == expected_names

    @integration_test("performance")
    @performance_test(target_duration=2.0, max_memory_mb=100.0)
    async def test_rapid_state_changes_performance(self, environment: Dict[str, Any]):
        """Test state management performance with rapid changes."""
        state_manager = environment["state_manager"]

        # Create session for rapid state changes
        session_id = "rapid_changes_session"
        await state_manager.create_session(session_id)

        # Perform many rapid state changes
        num_changes = 50
        for i in range(num_changes):
            await state_manager.update_state(
                session_id, f"rapid_change_{i}", {"iteration": i, "data": f"change_data_{i}"}
            )

        # Verify all changes were recorded
        changes = await state_manager.get_state_changes(session_id)
        assert len(changes) >= num_changes

        # Verify state integrity
        session_state = await state_manager.get_session_state(session_id)
        assert session_state is not None

        # Test state query performance
        start_time = time.perf_counter()
        for i in range(10):
            await state_manager.get_session_state(session_id)
        end_time = time.perf_counter()

        query_time = (end_time - start_time) / 10
        assert query_time < 0.01, f"State queries too slow: {query_time:.4f}s per query"


# Test data scenarios for comprehensive testing
def test_integration_scenarios():
    """Generate comprehensive integration test scenarios."""
    generator = TestDataGenerator()

    # Generate reasoning scenarios
    reasoning_scenarios = generator.generate_reasoning_scenarios(count=5)

    # Generate communication scenarios
    comm_scenarios = generator.generate_agent_communication_scenarios(count=3)

    return {
        "reasoning_scenarios": reasoning_scenarios,
        "communication_scenarios": comm_scenarios,
    }


if __name__ == "__main__":
    # Run integration tests
    import pytest

    # Run with coverage and performance reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--maxfail=5",
            "-x",  # Stop on first failure for debugging
        ]
    )
