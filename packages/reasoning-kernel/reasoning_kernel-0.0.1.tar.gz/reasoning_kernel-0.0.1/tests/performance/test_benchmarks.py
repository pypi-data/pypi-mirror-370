"""
Performance Benchmarking Tests for MSA Reasoning Kernel

Comprehensive performance testing and benchmarking for all major components
and workflows to validate optimization improvements.
"""

import asyncio
import time
import statistics
from typing import Dict, Any, List
from dataclasses import dataclass, field
from unittest.mock import Mock, AsyncMock

from tests.framework.enhanced_testing import (
    PerformanceTestSuite,
    MockAgentFactory,
    performance_test,
    integration_test,
)

from reasoning_kernel.agents.enhanced_orchestrator import (
    OrchestrationStrategy,
)
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


@dataclass
class BenchmarkResults:
    """Container for benchmark results."""

    component: str
    test_name: str
    iterations: int
    execution_times: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    success_rate: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def avg_time(self) -> float:
        """Average execution time."""
        return statistics.mean(self.execution_times) if self.execution_times else 0.0

    @property
    def median_time(self) -> float:
        """Median execution time."""
        return statistics.median(self.execution_times) if self.execution_times else 0.0

    @property
    def p95_time(self) -> float:
        """95th percentile execution time."""
        if len(self.execution_times) < 2:
            return self.avg_time
        sorted_times = sorted(self.execution_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def throughput(self) -> float:
        """Operations per second."""
        return 1.0 / self.avg_time if self.avg_time > 0 else 0.0


class ComponentBenchmarkSuite:
    """Comprehensive benchmarking suite for all components."""

    def __init__(self):
        self.results: List[BenchmarkResults] = []
        self.performance_suite = PerformanceTestSuite()

    async def run_orchestration_benchmarks(self, environment: Dict[str, Any]) -> List[BenchmarkResults]:
        """Run comprehensive orchestration performance benchmarks."""
        logger.info("Starting orchestration benchmarks")

        orchestrator = environment["orchestrator"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create test agents with different performance characteristics
        fast_agents = []
        medium_agents = []
        slow_agents = []

        # Fast agents (0.01s response time)
        for i in range(5):
            agent = factory.create_basic_agent(f"fast_{i}", kernel)
            agent.invoke = AsyncMock(return_value=Mock(content=f"Fast response {i}"))
            fast_agents.append(agent)
            await orchestrator.register_agent(agent)

        # Medium agents (0.1s response time)
        for i in range(3):
            agent = factory.create_slow_agent(f"medium_{i}", delay=0.1, kernel=kernel)
            medium_agents.append(agent)
            await orchestrator.register_agent(agent)

        # Slow agents (0.5s response time)
        for i in range(2):
            agent = factory.create_slow_agent(f"slow_{i}", delay=0.5, kernel=kernel)
            slow_agents.append(agent)
            await orchestrator.register_agent(agent)

        benchmarks = []

        # Benchmark 1: Sequential orchestration with fast agents
        benchmarks.append(
            await self._benchmark_orchestration_strategy(
                orchestrator, fast_agents, OrchestrationStrategy.SEQUENTIAL, "sequential_fast", iterations=10
            )
        )

        # Benchmark 2: Parallel orchestration with fast agents
        benchmarks.append(
            await self._benchmark_orchestration_strategy(
                orchestrator, fast_agents, OrchestrationStrategy.PARALLEL, "parallel_fast", iterations=10
            )
        )

        # Benchmark 3: Pipeline orchestration with mixed agents
        pipeline_agents = [fast_agents[0], medium_agents[0], fast_agents[1]]
        benchmarks.append(
            await self._benchmark_orchestration_strategy(
                orchestrator, pipeline_agents, OrchestrationStrategy.PIPELINE, "pipeline_mixed", iterations=8
            )
        )

        # Benchmark 4: Adaptive orchestration with mixed agents
        adaptive_agents = fast_agents[:2] + medium_agents[:1] + slow_agents[:1]
        benchmarks.append(
            await self._benchmark_orchestration_strategy(
                orchestrator, adaptive_agents, OrchestrationStrategy.ADAPTIVE, "adaptive_mixed", iterations=5
            )
        )

        # Benchmark 5: High-volume parallel orchestration
        benchmarks.append(
            await self._benchmark_orchestration_strategy(
                orchestrator, fast_agents, OrchestrationStrategy.PARALLEL, "high_volume_parallel", iterations=20
            )
        )

        self.results.extend(benchmarks)
        return benchmarks

    async def _benchmark_orchestration_strategy(
        self, orchestrator, agents: List, strategy: OrchestrationStrategy, test_name: str, iterations: int = 10
    ) -> BenchmarkResults:
        """Benchmark a specific orchestration strategy."""

        results = BenchmarkResults(component="orchestrator", test_name=test_name, iterations=iterations)

        successes = 0

        for i in range(iterations):
            try:
                # Create execution plan
                start_time = time.perf_counter()

                plan = await orchestrator.create_execution_plan(
                    task_description=f"Benchmark task {i} for {test_name}",
                    strategy=strategy,
                    requirements={"benchmark": True, "iteration": i},
                )

                # Execute plan
                execution_results = await orchestrator.execute_plan(plan)

                end_time = time.perf_counter()
                execution_time = end_time - start_time

                if execution_results["status"] == "completed":
                    results.execution_times.append(execution_time)
                    successes += 1
                else:
                    results.errors.append(f"Iteration {i}: {execution_results.get('error', 'Unknown error')}")

            except Exception as e:
                results.errors.append(f"Iteration {i}: {str(e)}")

        results.success_rate = successes / iterations

        logger.info(
            f"Benchmark {test_name} completed: "
            f"avg={results.avg_time:.3f}s, "
            f"success_rate={results.success_rate:.2%}"
        )

        return results

    async def run_state_management_benchmarks(self, environment: Dict[str, Any]) -> List[BenchmarkResults]:
        """Run state management performance benchmarks."""
        logger.info("Starting state management benchmarks")

        state_manager = environment["state_manager"]
        benchmarks = []

        # Benchmark 1: Rapid state updates
        benchmarks.append(await self._benchmark_rapid_state_updates(state_manager, iterations=50))

        # Benchmark 2: State queries under load
        benchmarks.append(await self._benchmark_state_queries(state_manager, iterations=100))

        # Benchmark 3: Checkpoint operations
        benchmarks.append(await self._benchmark_checkpoint_operations(state_manager, iterations=10))

        # Benchmark 4: Concurrent state access
        benchmarks.append(await self._benchmark_concurrent_state_access(state_manager, iterations=20))

        self.results.extend(benchmarks)
        return benchmarks

    async def _benchmark_rapid_state_updates(self, state_manager, iterations: int) -> BenchmarkResults:
        """Benchmark rapid state update performance."""

        results = BenchmarkResults(component="state_manager", test_name="rapid_updates", iterations=iterations)

        # Create test session
        session_id = "benchmark_rapid_updates"
        await state_manager.create_session(session_id)

        successes = 0

        for i in range(iterations):
            try:
                start_time = time.perf_counter()

                await state_manager.update_state(
                    session_id, f"update_{i}", {"iteration": i, "data": f"benchmark_data_{i}", "timestamp": time.time()}
                )

                end_time = time.perf_counter()
                results.execution_times.append(end_time - start_time)
                successes += 1

            except Exception as e:
                results.errors.append(f"Update {i}: {str(e)}")

        results.success_rate = successes / iterations

        # Verify all updates were recorded
        changes = await state_manager.get_state_changes(session_id)
        if len(changes) < successes:
            results.errors.append(f"Some updates not recorded: {len(changes)} < {successes}")

        return results

    async def _benchmark_state_queries(self, state_manager, iterations: int) -> BenchmarkResults:
        """Benchmark state query performance."""

        results = BenchmarkResults(component="state_manager", test_name="state_queries", iterations=iterations)

        # Create test session with data
        session_id = "benchmark_queries"
        await state_manager.create_session(session_id)

        # Pre-populate with some state data
        for i in range(10):
            await state_manager.update_state(session_id, f"prep_{i}", {"data": i})

        successes = 0

        for i in range(iterations):
            try:
                start_time = time.perf_counter()

                session_state = await state_manager.get_session_state(session_id)

                end_time = time.perf_counter()

                if session_state is not None:
                    results.execution_times.append(end_time - start_time)
                    successes += 1
                else:
                    results.errors.append(f"Query {i}: No state returned")

            except Exception as e:
                results.errors.append(f"Query {i}: {str(e)}")

        results.success_rate = successes / iterations
        return results

    async def _benchmark_checkpoint_operations(self, state_manager, iterations: int) -> BenchmarkResults:
        """Benchmark checkpoint creation and restoration."""

        results = BenchmarkResults(component="state_manager", test_name="checkpoint_ops", iterations=iterations)

        session_id = "benchmark_checkpoints"
        await state_manager.create_session(session_id)

        # Add some initial state
        await state_manager.update_state(session_id, "initial", {"data": "checkpoint_test"})

        successes = 0

        for i in range(iterations):
            try:
                # Benchmark checkpoint creation
                start_time = time.perf_counter()

                checkpoint = await state_manager.create_checkpoint(session_id, f"checkpoint_{i}")

                # Add some state changes
                await state_manager.update_state(session_id, f"change_{i}", {"change": i})

                # Benchmark checkpoint restoration
                await state_manager.restore_checkpoint(session_id, checkpoint.checkpoint_id)

                end_time = time.perf_counter()

                results.execution_times.append(end_time - start_time)
                successes += 1

            except Exception as e:
                results.errors.append(f"Checkpoint {i}: {str(e)}")

        results.success_rate = successes / iterations
        return results

    async def _benchmark_concurrent_state_access(self, state_manager, iterations: int) -> BenchmarkResults:
        """Benchmark concurrent state access performance."""

        results = BenchmarkResults(component="state_manager", test_name="concurrent_access", iterations=iterations)

        # Create multiple sessions for concurrent access
        session_ids = [f"concurrent_session_{i}" for i in range(5)]
        for session_id in session_ids:
            await state_manager.create_session(session_id)

        async def concurrent_operation(session_id: str, iteration: int):
            """Single concurrent operation."""
            await state_manager.update_state(session_id, f"concurrent_{iteration}", {"iter": iteration})
            return await state_manager.get_session_state(session_id)

        successes = 0

        for i in range(iterations):
            try:
                start_time = time.perf_counter()

                # Run concurrent operations on all sessions
                tasks = [concurrent_operation(session_id, i) for session_id in session_ids]

                await asyncio.gather(*tasks)

                end_time = time.perf_counter()
                results.execution_times.append(end_time - start_time)
                successes += 1

            except Exception as e:
                results.errors.append(f"Concurrent {i}: {str(e)}")

        results.success_rate = successes / iterations
        return results

    async def run_communication_benchmarks(self, environment: Dict[str, Any]) -> List[BenchmarkResults]:
        """Run communication performance benchmarks."""
        logger.info("Starting communication benchmarks")

        communication_manager = environment["communication_manager"]
        kernel = environment["kernel"]
        factory = MockAgentFactory()

        # Create additional agents for communication testing
        comm_agents = {}
        for i in range(8):
            agent = factory.create_basic_agent(f"comm_agent_{i}", kernel)
            comm_agents[f"comm_agent_{i}"] = agent

        # Update communication manager with new agents
        communication_manager.agents.update(comm_agents)

        benchmarks = []

        # Benchmark 1: Direct message performance
        benchmarks.append(await self._benchmark_direct_messages(communication_manager, iterations=50))

        # Benchmark 2: Broadcast message performance
        benchmarks.append(await self._benchmark_broadcast_messages(communication_manager, iterations=20))

        # Benchmark 3: Pipeline message performance
        benchmarks.append(await self._benchmark_pipeline_messages(communication_manager, iterations=15))

        self.results.extend(benchmarks)
        return benchmarks

    async def _benchmark_direct_messages(self, communication_manager, iterations: int) -> BenchmarkResults:
        """Benchmark direct message performance."""

        results = BenchmarkResults(
            component="communication_manager", test_name="direct_messages", iterations=iterations
        )

        agent_names = list(communication_manager.agents.keys())
        if len(agent_names) < 2:
            results.errors.append("Not enough agents for direct message testing")
            return results

        sender = agent_names[0]
        receiver = agent_names[1]

        successes = 0

        for i in range(iterations):
            try:
                start_time = time.perf_counter()

                response = await communication_manager.send_direct_message(
                    from_agent=sender,
                    to_agent=receiver,
                    message=f"Benchmark message {i}",
                    context={"benchmark": True, "iteration": i},
                )

                end_time = time.perf_counter()

                if response:
                    results.execution_times.append(end_time - start_time)
                    successes += 1
                else:
                    results.errors.append(f"Direct message {i}: No response")

            except Exception as e:
                results.errors.append(f"Direct message {i}: {str(e)}")

        results.success_rate = successes / iterations
        return results

    async def _benchmark_broadcast_messages(self, communication_manager, iterations: int) -> BenchmarkResults:
        """Benchmark broadcast message performance."""

        results = BenchmarkResults(
            component="communication_manager", test_name="broadcast_messages", iterations=iterations
        )

        agent_names = list(communication_manager.agents.keys())
        if len(agent_names) < 3:
            results.errors.append("Not enough agents for broadcast testing")
            return results

        broadcaster = agent_names[0]
        receivers = agent_names[1:6]  # Up to 5 receivers

        successes = 0

        for i in range(iterations):
            try:
                start_time = time.perf_counter()

                responses = await communication_manager.broadcast_message(
                    from_agent=broadcaster,
                    to_agents=receivers,
                    message=f"Broadcast benchmark {i}",
                    context={"benchmark": True, "iteration": i},
                )

                end_time = time.perf_counter()

                if responses and len(responses) == len(receivers):
                    results.execution_times.append(end_time - start_time)
                    successes += 1
                else:
                    results.errors.append(
                        f"Broadcast {i}: Incomplete responses {len(responses) if responses else 0}/{len(receivers)}"
                    )

            except Exception as e:
                results.errors.append(f"Broadcast {i}: {str(e)}")

        results.success_rate = successes / iterations
        return results

    async def _benchmark_pipeline_messages(self, communication_manager, iterations: int) -> BenchmarkResults:
        """Benchmark pipeline message performance."""

        results = BenchmarkResults(
            component="communication_manager", test_name="pipeline_messages", iterations=iterations
        )

        agent_names = list(communication_manager.agents.keys())
        if len(agent_names) < 3:
            results.errors.append("Not enough agents for pipeline testing")
            return results

        pipeline_agents = agent_names[:4]  # Use 4 agents in pipeline

        successes = 0

        for i in range(iterations):
            try:
                start_time = time.perf_counter()

                result = await communication_manager.send_pipeline_message(
                    agents=pipeline_agents,
                    initial_message=f"Pipeline benchmark {i}",
                    context={"benchmark": True, "iteration": i},
                )

                end_time = time.perf_counter()

                if result:
                    results.execution_times.append(end_time - start_time)
                    successes += 1
                else:
                    results.errors.append(f"Pipeline {i}: No result")

            except Exception as e:
                results.errors.append(f"Pipeline {i}: {str(e)}")

        results.success_rate = successes / iterations
        return results

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""

        report = {
            "summary": {
                "total_benchmarks": len(self.results),
                "components_tested": len(set(r.component for r in self.results)),
                "overall_success_rate": (
                    statistics.mean([r.success_rate for r in self.results]) if self.results else 0.0
                ),
            },
            "benchmarks": {},
            "performance_analysis": {},
            "recommendations": [],
        }

        # Group results by component
        by_component = {}
        for result in self.results:
            if result.component not in by_component:
                by_component[result.component] = []
            by_component[result.component].append(result)

        # Generate detailed analysis for each component
        for component, component_results in by_component.items():
            component_analysis = {
                "total_tests": len(component_results),
                "avg_success_rate": statistics.mean([r.success_rate for r in component_results]),
                "tests": {},
            }

            for result in component_results:
                test_analysis = {
                    "iterations": result.iterations,
                    "success_rate": result.success_rate,
                    "avg_time_ms": result.avg_time * 1000,
                    "median_time_ms": result.median_time * 1000,
                    "p95_time_ms": result.p95_time * 1000,
                    "throughput_ops_per_sec": result.throughput,
                    "error_count": len(result.errors),
                }

                # Performance assessment
                if result.avg_time < 0.1:
                    test_analysis["performance"] = "excellent"
                elif result.avg_time < 0.5:
                    test_analysis["performance"] = "good"
                elif result.avg_time < 2.0:
                    test_analysis["performance"] = "acceptable"
                else:
                    test_analysis["performance"] = "needs_improvement"

                component_analysis["tests"][result.test_name] = test_analysis

            report["benchmarks"][component] = component_analysis

        # Generate recommendations
        recommendations = []

        for result in self.results:
            if result.success_rate < 0.9:
                recommendations.append(
                    f"Improve reliability for {result.component}.{result.test_name} (success rate: {result.success_rate:.1%})"
                )

            if result.avg_time > 2.0:
                recommendations.append(
                    f"Optimize performance for {result.component}.{result.test_name} (avg time: {result.avg_time:.3f}s)"
                )

            if result.p95_time > result.avg_time * 3:
                recommendations.append(
                    f"Address performance variability in {result.component}.{result.test_name} (P95/avg ratio: {result.p95_time/result.avg_time:.1f})"
                )

        report["recommendations"] = recommendations

        return report


class PerformanceBenchmarkTests:
    """Main performance benchmark test class."""

    @integration_test("performance")
    @performance_test(target_duration=30.0, max_memory_mb=300.0)
    async def test_comprehensive_performance_benchmarks(self, environment: Dict[str, Any]):
        """Run comprehensive performance benchmarks across all components."""

        benchmark_suite = ComponentBenchmarkSuite()

        # Run orchestration benchmarks
        await benchmark_suite.run_orchestration_benchmarks(environment)

        # Run state management benchmarks
        await benchmark_suite.run_state_management_benchmarks(environment)

        # Run communication benchmarks
        await benchmark_suite.run_communication_benchmarks(environment)

        # Generate performance report
        report = benchmark_suite.generate_performance_report()

        # Log performance summary
        logger.info("Performance Benchmark Results:")
        logger.info(f"Total benchmarks: {report['summary']['total_benchmarks']}")
        logger.info(f"Overall success rate: {report['summary']['overall_success_rate']:.1%}")

        for component, results in report["benchmarks"].items():
            logger.info(f"{component}: {results['total_tests']} tests, {results['avg_success_rate']:.1%} success rate")

        if report["recommendations"]:
            logger.info("Performance recommendations:")
            for rec in report["recommendations"][:5]:  # Show top 5
                logger.info(f"  - {rec}")

        # Validate overall performance meets requirements
        assert report["summary"]["overall_success_rate"] >= 0.8, "Overall success rate below acceptable threshold"

        # Validate no component has catastrophic performance issues
        for component, results in report["benchmarks"].items():
            assert results["avg_success_rate"] >= 0.7, f"Component {component} has unacceptable success rate"

        return report


if __name__ == "__main__":
    # Run performance benchmarks
    import pytest

    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-s",  # Show output for performance results
        ]
    )
