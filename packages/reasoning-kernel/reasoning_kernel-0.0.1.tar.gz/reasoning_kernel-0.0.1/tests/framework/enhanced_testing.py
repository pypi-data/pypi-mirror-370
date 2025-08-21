"""
Enhanced Testing Framework for MSA Reasoning Kernel

Comprehensive testing utilities, fixtures, and infrastructure for
integration, performance, and end-to-end testing.
"""

import asyncio
import functools
import inspect
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, Mock
from semantic_kernel import Kernel
from semantic_kernel.contents import ChatMessageContent, AuthorRole

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.agents.enhanced_orchestrator import EnhancedAgentOrchestrator, AgentCapability
from reasoning_kernel.agents.state_manager import StateManager
from reasoning_kernel.agents.communication_patterns import EnhancedCommunicationManager
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


@dataclass
class TestMetrics:
    """Test execution metrics."""

    test_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    memory_usage: Dict[str, float] = field(default_factory=dict)
    assertions_passed: int = 0
    assertions_failed: int = 0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Get test duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


@dataclass
class PerformanceBenchmark:
    """Performance benchmark configuration and results."""

    name: str
    description: str
    target_duration: float  # Target execution time in seconds
    max_memory_mb: float  # Maximum memory usage in MB
    iterations: int = 1
    warmup_iterations: int = 0

    # Results
    actual_duration: float = 0.0
    actual_memory_mb: float = 0.0
    iterations_completed: int = 0
    passed: bool = False
    error: Optional[str] = None


class EnhancedTestCase:
    """Enhanced test case with performance tracking and utilities."""

    def __init__(self, name: str, category: str = "unit"):
        self.name = name
        self.category = category
        self.metrics = TestMetrics(name, datetime.now())
        self._setup_complete = False
        self._teardown_complete = False

    async def setup(self):
        """Setup test case."""
        logger.debug(f"Setting up test: {self.name}")
        self._setup_complete = True

    async def teardown(self):
        """Teardown test case."""
        logger.debug(f"Tearing down test: {self.name}")
        self._teardown_complete = True
        self.metrics.end_time = datetime.now()
        self.metrics.execution_time = self.metrics.duration

    def assert_performance(self, benchmark: PerformanceBenchmark):
        """Assert performance meets benchmark criteria."""
        if self.metrics.execution_time > benchmark.target_duration:
            raise AssertionError(
                f"Performance test failed: {self.metrics.execution_time:.3f}s > {benchmark.target_duration:.3f}s"
            )

        memory_usage = self.metrics.memory_usage.get("peak", 0.0)
        if memory_usage > benchmark.max_memory_mb:
            raise AssertionError(f"Memory test failed: {memory_usage:.1f}MB > {benchmark.max_memory_mb:.1f}MB")


class MockAgentFactory:
    """Factory for creating mock agents with different behaviors."""

    @staticmethod
    def create_basic_agent(name: str, kernel: Optional[Kernel] = None) -> BaseReasoningAgent:
        """Create a basic mock agent."""
        kernel = kernel or Mock(spec=Kernel)

        class BasicMockAgent(BaseReasoningAgent):
            async def _process_message(self, message: str, **kwargs) -> str:
                return f"Basic response from {self.name}: {message}"

        agent = BasicMockAgent(name=name, kernel=kernel)
        agent.invoke = AsyncMock(
            return_value=ChatMessageContent(role=AuthorRole.ASSISTANT, content=f"Mock response from {name}")
        )
        return agent

    @staticmethod
    def create_slow_agent(name: str, delay: float = 1.0, kernel: Optional[Kernel] = None) -> BaseReasoningAgent:
        """Create a mock agent that simulates slow processing."""
        kernel = kernel or Mock(spec=Kernel)

        class SlowMockAgent(BaseReasoningAgent):
            async def _process_message(self, message: str, **kwargs) -> str:
                await asyncio.sleep(delay)
                return f"Slow response from {self.name}: {message}"

        agent = SlowMockAgent(name=name, kernel=kernel)

        async def slow_invoke(message: str, **kwargs):
            await asyncio.sleep(delay)
            return ChatMessageContent(role=AuthorRole.ASSISTANT, content=f"Slow mock response from {name}")

        agent.invoke = slow_invoke
        return agent

    @staticmethod
    def create_failing_agent(
        name: str, failure_rate: float = 0.5, kernel: Optional[Kernel] = None
    ) -> BaseReasoningAgent:
        """Create a mock agent that fails randomly."""
        kernel = kernel or Mock(spec=Kernel)

        class FailingMockAgent(BaseReasoningAgent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.call_count = 0

            async def _process_message(self, message: str, **kwargs) -> str:
                self.call_count += 1
                if self.call_count * failure_rate >= 1.0:
                    self.call_count = 0
                    raise Exception(f"Simulated failure in {self.name}")
                return f"Success response from {self.name}: {message}"

        agent = FailingMockAgent(name=name, kernel=kernel)

        call_count = 0

        async def failing_invoke(message: str, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count * failure_rate >= 1.0:
                call_count = 0
                raise Exception(f"Simulated failure in {name}")
            return ChatMessageContent(role=AuthorRole.ASSISTANT, content=f"Success mock response from {name}")

        agent.invoke = failing_invoke
        return agent

    @staticmethod
    def create_specialized_agent(
        name: str, capabilities: Dict[str, AgentCapability], kernel: Optional[Kernel] = None
    ) -> BaseReasoningAgent:
        """Create a mock agent with specific capabilities."""
        kernel = kernel or Mock(spec=Kernel)

        class SpecializedMockAgent(BaseReasoningAgent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.capabilities = capabilities

            async def _process_message(self, message: str, **kwargs) -> str:
                # Simulate capability-based processing
                capability_names = list(self.capabilities.keys())
                return f"Specialized response from {self.name} using {capability_names}: {message}"

        agent = SpecializedMockAgent(name=name, kernel=kernel)
        agent.invoke = AsyncMock(
            return_value=ChatMessageContent(role=AuthorRole.ASSISTANT, content=f"Specialized mock response from {name}")
        )
        return agent


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_reasoning_scenarios(count: int = 10) -> List[Dict[str, Any]]:
        """Generate reasoning test scenarios."""
        scenarios = []

        scenario_templates = [
            {
                "description": "Simple mathematical reasoning",
                "input": "If I have {} apples and give away {}, how many do I have left?",
                "expected_type": "arithmetic",
                "complexity": "low",
            },
            {
                "description": "Causal reasoning scenario",
                "input": "What happens if {} causes {} which leads to {}?",
                "expected_type": "causal",
                "complexity": "medium",
            },
            {
                "description": "Complex multi-step reasoning",
                "input": "Given conditions A={}, B={}, and C={}, determine the outcome when all interact.",
                "expected_type": "multi_step",
                "complexity": "high",
            },
        ]

        for i in range(count):
            template = scenario_templates[i % len(scenario_templates)]
            scenario = template.copy()

            # Fill in template variables
            if "mathematical" in template["description"]:
                scenario["input"] = template["input"].format(10 + i, 2 + i)
            elif "causal" in template["description"]:
                scenario["input"] = template["input"].format(f"event_{i}", f"condition_{i}", f"outcome_{i}")
            else:
                scenario["input"] = template["input"].format(f"value_a_{i}", f"value_b_{i}", f"value_c_{i}")

            scenario["scenario_id"] = f"scenario_{i:03d}"
            scenarios.append(scenario)

        return scenarios

    @staticmethod
    def generate_agent_communication_scenarios(count: int = 5) -> List[Dict[str, Any]]:
        """Generate agent communication test scenarios."""
        patterns = ["direct", "broadcast", "pipeline", "scatter_gather"]
        scenarios = []

        for i in range(count):
            scenario = {
                "scenario_id": f"comm_scenario_{i:03d}",
                "pattern": patterns[i % len(patterns)],
                "participants": [f"agent_{j}" for j in range(2 + (i % 3))],  # 2-4 agents
                "message_count": 1 + (i % 5),  # 1-5 messages
                "complexity": ["low", "medium", "high"][i % 3],
                "expected_duration": 1.0 + (i * 0.5),  # Increasing duration
            }
            scenarios.append(scenario)

        return scenarios


class PerformanceTestSuite:
    """Performance testing suite with benchmarking capabilities."""

    def __init__(self):
        self.benchmarks: List[PerformanceBenchmark] = []
        self.results: Dict[str, PerformanceBenchmark] = {}

    def add_benchmark(self, benchmark: PerformanceBenchmark):
        """Add a performance benchmark."""
        self.benchmarks.append(benchmark)

    async def run_benchmark(self, benchmark: PerformanceBenchmark, test_function: Callable) -> PerformanceBenchmark:
        """Run a performance benchmark."""
        logger.info(f"Running benchmark: {benchmark.name}")

        # Warmup iterations
        for _ in range(benchmark.warmup_iterations):
            try:
                await test_function()
            except Exception as e:
                logger.warning(f"Warmup iteration failed: {e}")

        # Actual benchmark iterations
        start_time = time.perf_counter()

        try:
            for i in range(benchmark.iterations):
                await test_function()
                benchmark.iterations_completed = i + 1

            end_time = time.perf_counter()
            benchmark.actual_duration = (end_time - start_time) / benchmark.iterations

            # Check if benchmark passed
            benchmark.passed = benchmark.actual_duration <= benchmark.target_duration

        except Exception as e:
            benchmark.error = str(e)
            benchmark.passed = False

        self.results[benchmark.name] = benchmark
        return benchmark

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance testing report."""
        report = {
            "summary": {
                "total_benchmarks": len(self.results),
                "passed": sum(1 for b in self.results.values() if b.passed),
                "failed": sum(1 for b in self.results.values() if not b.passed),
                "total_time": sum(b.actual_duration for b in self.results.values()),
            },
            "benchmarks": {},
        }

        for name, benchmark in self.results.items():
            report["benchmarks"][name] = {
                "passed": benchmark.passed,
                "target_duration": benchmark.target_duration,
                "actual_duration": benchmark.actual_duration,
                "iterations": benchmark.iterations_completed,
                "error": benchmark.error,
            }

        return report


class IntegrationTestFramework:
    """Framework for running integration tests across components."""

    def __init__(self):
        self.test_cases: List[EnhancedTestCase] = []
        self.fixtures: Dict[str, Any] = {}
        self.mock_services: Dict[str, Any] = {}

    def register_fixture(self, name: str, factory: Callable):
        """Register a test fixture."""
        self.fixtures[name] = factory

    def register_mock_service(self, name: str, mock: Mock):
        """Register a mock service."""
        self.mock_services[name] = mock

    async def setup_integration_environment(self) -> Dict[str, Any]:
        """Set up integration testing environment."""
        environment = {}

        # Create mock kernel
        kernel = Mock(spec=Kernel)
        environment["kernel"] = kernel

        # Create test agents
        agent_factory = MockAgentFactory()
        environment["agents"] = {
            "basic_agent": agent_factory.create_basic_agent("basic_agent", kernel),
            "slow_agent": agent_factory.create_slow_agent("slow_agent", 0.1, kernel),
            "failing_agent": agent_factory.create_failing_agent("failing_agent", 0.3, kernel),
        }

        # Create orchestration components
        environment["orchestrator"] = EnhancedAgentOrchestrator(
            kernel=kernel,
            max_concurrent_tasks=3,
            enable_state_persistence=False,  # Disable for testing
        )

        environment["state_manager"] = StateManager(
            storage_path=None,  # Use in-memory for testing
            snapshot_interval=9999,  # Disable automatic snapshots
            max_history_size=100,
            enable_compression=False,
        )

        environment["communication_manager"] = EnhancedCommunicationManager(environment["agents"])

        # Initialize components
        await environment["orchestrator"].initialize()
        await environment["state_manager"].initialize()
        await environment["communication_manager"].initialize()

        # Register agents with orchestrator
        for agent in environment["agents"].values():
            await environment["orchestrator"].register_agent(agent)

        return environment

    async def teardown_integration_environment(self, environment: Dict[str, Any]):
        """Tear down integration testing environment."""
        # Shutdown components in reverse order
        if "communication_manager" in environment:
            await environment["communication_manager"].shutdown()

        if "orchestrator" in environment:
            await environment["orchestrator"].shutdown()

        if "state_manager" in environment:
            await environment["state_manager"].shutdown()

    async def run_integration_test(self, test_case: EnhancedTestCase, test_function: Callable) -> TestMetrics:
        """Run an integration test."""
        logger.info(f"Running integration test: {test_case.name}")

        environment = None
        try:
            # Setup
            await test_case.setup()
            environment = await self.setup_integration_environment()

            # Execute test
            if inspect.iscoroutinefunction(test_function):
                await test_function(environment)
            else:
                test_function(environment)

            test_case.metrics.assertions_passed += 1

        except Exception as e:
            test_case.metrics.assertions_failed += 1
            logger.error(f"Integration test failed: {test_case.name} - {e}")
            raise

        finally:
            # Teardown
            if environment:
                await self.teardown_integration_environment(environment)
            await test_case.teardown()

        return test_case.metrics


# Decorators for enhanced testing


def performance_test(target_duration: float = 1.0, max_memory_mb: float = 100.0):
    """Decorator for performance tests."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            benchmark = PerformanceBenchmark(
                name=func.__name__,
                description=func.__doc__ or f"Performance test for {func.__name__}",
                target_duration=target_duration,
                max_memory_mb=max_memory_mb,
            )

            performance_suite = PerformanceTestSuite()
            result = await performance_suite.run_benchmark(benchmark, lambda: func(*args, **kwargs))

            if not result.passed:
                error_msg = (
                    result.error
                    or f"Performance target not met: {result.actual_duration:.3f}s > {result.target_duration:.3f}s"
                )
                raise AssertionError(error_msg)

            return result

        return wrapper

    return decorator


def integration_test(category: str = "integration"):
    """Decorator for integration tests."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            test_case = EnhancedTestCase(func.__name__, category)
            framework = IntegrationTestFramework()

            return await framework.run_integration_test(test_case, lambda env: func(env, *args, **kwargs))

        return wrapper

    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 0.1):
    """Decorator to retry flaky tests."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    if inspect.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Test attempt {attempt + 1} failed, retrying: {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Test failed after {max_retries + 1} attempts")
                        break

            if last_exception:
                raise last_exception
            raise Exception("Test failed with no exception details")

        return wrapper

    return decorator


# Context managers for test environments


@asynccontextmanager
async def test_orchestration_environment(
    agents: Optional[Dict[str, BaseReasoningAgent]] = None,
    config: Optional[Dict[str, Any]] = None,
):
    """Context manager for orchestration testing environment."""
    kernel = Mock(spec=Kernel)
    config = config or {}

    # Create agents if not provided
    if agents is None:
        factory = MockAgentFactory()
        agents = {
            "agent1": factory.create_basic_agent("agent1", kernel),
            "agent2": factory.create_basic_agent("agent2", kernel),
        }

    # Create orchestration components
    orchestrator = EnhancedAgentOrchestrator(
        kernel=kernel,
        max_concurrent_tasks=config.get("max_concurrent_tasks", 3),
        enable_state_persistence=False,
        adaptive_load_balancing=config.get("adaptive_load_balancing", True),
    )

    state_manager = StateManager(
        storage_path=None,
        snapshot_interval=9999,
        max_history_size=100,
        enable_compression=False,
    )

    communication_manager = EnhancedCommunicationManager(agents)

    try:
        # Initialize
        await orchestrator.initialize()
        await state_manager.initialize()
        await communication_manager.initialize()

        # Register agents
        for agent in agents.values():
            await orchestrator.register_agent(agent)

        yield {
            "orchestrator": orchestrator,
            "state_manager": state_manager,
            "communication_manager": communication_manager,
            "agents": agents,
            "kernel": kernel,
        }

    finally:
        # Cleanup
        await communication_manager.shutdown()
        await orchestrator.shutdown()
        await state_manager.shutdown()


# Assertion helpers


def assert_agent_response_quality(response: str, min_length: int = 10, expected_keywords: Optional[List[str]] = None):
    """Assert agent response meets quality criteria."""
    assert len(response) >= min_length, f"Response too short: {len(response)} < {min_length}"

    if expected_keywords:
        response_lower = response.lower()
        for keyword in expected_keywords:
            assert keyword.lower() in response_lower, f"Expected keyword '{keyword}' not found in response"


def assert_performance_acceptable(actual_time: float, target_time: float, tolerance: float = 0.1):
    """Assert performance is within acceptable range."""
    max_allowed = target_time * (1 + tolerance)
    assert actual_time <= max_allowed, f"Performance not acceptable: {actual_time:.3f}s > {max_allowed:.3f}s"


def assert_orchestration_successful(results: Dict[str, Any], expected_steps: int):
    """Assert orchestration completed successfully."""
    assert results.get("status") == "completed", f"Orchestration failed: {results.get('status')}"
    assert (
        len(results.get("steps", {})) == expected_steps
    ), f"Expected {expected_steps} steps, got {len(results.get('steps', {}))}"
