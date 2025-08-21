"""
Enhanced Agent Orchestration System

Improvements for agent coordination, state management, and communication
in the MSA Reasoning Kernel.
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.agents.communication_protocol import CommunicationManager
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class OrchestrationStrategy(Enum):
    """Different orchestration strategies for agent coordination."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"


class AgentState(Enum):
    """Enhanced agent state tracking."""

    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"


@dataclass
class AgentCapability:
    """Represents agent capabilities for smart task assignment."""

    name: str
    skill_level: float  # 0.0 - 1.0
    resource_requirements: Dict[str, Any]
    estimated_duration: float  # seconds
    success_rate: float  # 0.0 - 1.0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TaskExecutionPlan:
    """Detailed execution plan for complex tasks."""

    task_id: str
    strategy: OrchestrationStrategy
    estimated_duration: float
    resource_requirements: Dict[str, Any]
    agent_assignments: Dict[str, str]  # step_id -> agent_name
    dependency_graph: Dict[str, List[str]]  # step_id -> dependencies
    fallback_agents: Dict[str, List[str]]  # step_id -> backup agents
    quality_gates: List[Dict[str, Any]]
    rollback_strategy: Optional[Dict[str, Any]] = None


@dataclass
class AgentMetrics:
    """Comprehensive agent performance metrics."""

    agent_name: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_response_time: float = 0.0
    success_rate: float = 1.0
    current_load: float = 0.0
    last_heartbeat: Optional[datetime] = None
    capabilities: Dict[str, AgentCapability] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)


class EnhancedAgentOrchestrator:
    """
    Enhanced orchestrator with advanced coordination patterns,
    state management, and adaptive task assignment.
    """

    def __init__(
        self,
        kernel,
        max_concurrent_tasks: int = 5,
        enable_state_persistence: bool = True,
        adaptive_load_balancing: bool = True,
    ):
        """Initialize enhanced orchestrator.

        Args:
            kernel: Semantic Kernel instance
            max_concurrent_tasks: Maximum concurrent task limit
            enable_state_persistence: Enable Redis state persistence
            adaptive_load_balancing: Enable adaptive load balancing
        """
        self._kernel = kernel
        self._max_concurrent_tasks = max_concurrent_tasks
        self._enable_state_persistence = enable_state_persistence
        self._adaptive_load_balancing = adaptive_load_balancing

        # Agent registry with enhanced metadata
        self._agents: Dict[str, BaseReasoningAgent] = {}
        self._agent_states: Dict[str, AgentState] = {}
        self._agent_metrics: Dict[str, AgentMetrics] = {}
        self._agent_capabilities: Dict[str, Dict[str, AgentCapability]] = {}

        # Task management
        self._active_tasks: Dict[str, TaskExecutionPlan] = {}
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._completed_tasks: Dict[str, Dict[str, Any]] = {}

        # Communication and coordination
        self._communication_manager = CommunicationManager()
        self._coordination_lock = asyncio.Lock()
        self._state_sync_interval = 30.0  # seconds

        # Monitoring and health
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._metrics_collector_task: Optional[asyncio.Task] = None
        self._state_sync_task: Optional[asyncio.Task] = None

        # Strategy patterns
        self._strategy_handlers = {
            OrchestrationStrategy.SEQUENTIAL: self._execute_sequential,
            OrchestrationStrategy.PARALLEL: self._execute_parallel,
            OrchestrationStrategy.PIPELINE: self._execute_pipeline,
            OrchestrationStrategy.HIERARCHICAL: self._execute_hierarchical,
            OrchestrationStrategy.ADAPTIVE: self._execute_adaptive,
        }

    async def initialize(self) -> None:
        """Initialize the enhanced orchestrator."""
        logger.info("Initializing enhanced agent orchestrator")

        # Initialize communication manager
        await self._communication_manager.initialize()

        # Start background tasks
        self._health_monitor_task = asyncio.create_task(self._monitor_agent_health())
        self._metrics_collector_task = asyncio.create_task(self._collect_metrics())

        if self._enable_state_persistence:
            self._state_sync_task = asyncio.create_task(self._sync_state_periodically())

        # Load persisted state if enabled
        if self._enable_state_persistence:
            await self._load_persisted_state()

        logger.info("Enhanced orchestrator initialized successfully")

    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator."""
        logger.info("Shutting down enhanced orchestrator")

        # Cancel background tasks
        tasks_to_cancel = [
            self._health_monitor_task,
            self._metrics_collector_task,
            self._state_sync_task,
        ]

        for task in tasks_to_cancel:
            if task and not task.done():
                task.cancel()

        # Wait for graceful shutdown
        if tasks_to_cancel:
            await asyncio.gather(*[t for t in tasks_to_cancel if t], return_exceptions=True)

        # Persist final state
        if self._enable_state_persistence:
            await self._persist_state()

        # Shutdown communication manager
        await self._communication_manager.shutdown()

        logger.info("Enhanced orchestrator shutdown complete")

    async def register_agent(
        self,
        agent: BaseReasoningAgent,
        capabilities: Optional[Dict[str, AgentCapability]] = None,
    ) -> None:
        """Register an agent with enhanced capabilities.

        Args:
            agent: Agent to register
            capabilities: Agent capabilities for task assignment
        """
        async with self._coordination_lock:
            self._agents[agent.name] = agent
            self._agent_states[agent.name] = AgentState.IDLE
            self._agent_metrics[agent.name] = AgentMetrics(agent_name=agent.name)

            if capabilities:
                self._agent_capabilities[agent.name] = capabilities
                self._agent_metrics[agent.name].capabilities = capabilities

            # Initialize default capabilities if none provided
            if agent.name not in self._agent_capabilities:
                await self._discover_agent_capabilities(agent)

            logger.info(f"Registered enhanced agent: {agent.name}")

    async def create_execution_plan(
        self,
        task_description: str,
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> TaskExecutionPlan:
        """Create an intelligent execution plan for a complex task.

        Args:
            task_description: Description of the task
            strategy: Orchestration strategy to use
            requirements: Task requirements and constraints

        Returns:
            Detailed execution plan
        """
        task_id = str(uuid.uuid4())
        requirements = requirements or {}

        # Analyze task complexity and requirements
        task_analysis = await self._analyze_task_complexity(task_description, requirements)

        # Select optimal agents based on capabilities
        agent_assignments = await self._select_optimal_agents(task_analysis)

        # Build dependency graph
        dependency_graph = await self._build_task_dependencies(task_analysis, agent_assignments)

        # Estimate execution time and resources
        estimated_duration = await self._estimate_execution_time(task_analysis, agent_assignments)

        # Create execution plan
        plan = TaskExecutionPlan(
            task_id=task_id,
            strategy=strategy,
            estimated_duration=estimated_duration,
            resource_requirements=task_analysis.get("resources", {}),
            agent_assignments=agent_assignments,
            dependency_graph=dependency_graph,
            fallback_agents=await self._identify_fallback_agents(agent_assignments),
            quality_gates=await self._define_quality_gates(task_analysis),
            rollback_strategy=await self._create_rollback_strategy(task_analysis),
        )

        self._active_tasks[task_id] = plan

        logger.info(f"Created execution plan {task_id} with strategy {strategy.value}")
        return plan

    async def execute_plan(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute a task execution plan.

        Args:
            plan: Execution plan to execute

        Returns:
            Execution results
        """
        logger.info(f"Executing plan {plan.task_id} with strategy {plan.strategy.value}")

        start_time = datetime.now()

        try:
            # Execute using appropriate strategy
            handler = self._strategy_handlers[plan.strategy]
            results = await handler(plan)

            # Record completion
            execution_time = (datetime.now() - start_time).total_seconds()
            results["execution_time"] = execution_time
            results["status"] = "completed"

            self._completed_tasks[plan.task_id] = results

            # Update agent metrics
            await self._update_agent_metrics(plan, results, success=True)

            logger.info(f"Plan {plan.task_id} completed successfully in {execution_time:.2f}s")
            return results

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_results = {
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time,
            }

            # Update agent metrics
            await self._update_agent_metrics(plan, error_results, success=False)

            logger.error(f"Plan {plan.task_id} failed after {execution_time:.2f}s: {e}")
            return error_results

        finally:
            # Cleanup
            if plan.task_id in self._active_tasks:
                del self._active_tasks[plan.task_id]

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status.

        Returns:
            Status information including agents, tasks, and metrics
        """
        return {
            "agents": {
                name: {
                    "state": self._agent_states.get(name, AgentState.UNAVAILABLE).value,
                    "metrics": self._agent_metrics.get(name, AgentMetrics(name)).__dict__,
                    "capabilities": list(self._agent_capabilities.get(name, {}).keys()),
                }
                for name in self._agents.keys()
            },
            "tasks": {
                "active": len(self._active_tasks),
                "completed": len(self._completed_tasks),
                "queue_size": self._task_queue.qsize(),
            },
            "system": {
                "max_concurrent": self._max_concurrent_tasks,
                "adaptive_balancing": self._adaptive_load_balancing,
                "state_persistence": self._enable_state_persistence,
            },
            "communication": self._communication_manager.stats,
        }

    # Strategy Implementation Methods

    async def _execute_sequential(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute tasks sequentially."""
        results = {"strategy": "sequential", "steps": {}}

        # Execute steps in dependency order
        execution_order = self._topological_sort(plan.dependency_graph)

        for step_id in execution_order:
            agent_name = plan.agent_assignments.get(step_id)
            if agent_name and agent_name in self._agents:
                agent = self._agents[agent_name]

                # Execute step
                step_result = await self._execute_step(agent, step_id, plan)
                results["steps"][step_id] = step_result

                # Check quality gates
                if not await self._check_quality_gates(step_result, plan.quality_gates):
                    raise Exception(f"Quality gate failed for step {step_id}")

        return results

    async def _execute_parallel(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute independent tasks in parallel."""
        results = {"strategy": "parallel", "steps": {}}

        # Group steps by dependency level
        dependency_levels = await self._group_by_dependency_level(plan.dependency_graph)

        for level, step_ids in dependency_levels.items():
            # Execute all steps in this level concurrently
            level_tasks = []
            for step_id in step_ids:
                agent_name = plan.agent_assignments.get(step_id)
                if agent_name and agent_name in self._agents:
                    agent = self._agents[agent_name]
                    task = self._execute_step(agent, step_id, plan)
                    level_tasks.append((step_id, task))

            # Wait for all tasks in this level to complete
            level_results = await asyncio.gather(*[task for _, task in level_tasks], return_exceptions=True)

            # Process results
            for (step_id, _), result in zip(level_tasks, level_results):
                if isinstance(result, Exception):
                    raise result
                results["steps"][step_id] = result

        return results

    async def _execute_pipeline(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute tasks in a streaming pipeline."""
        results = {"strategy": "pipeline", "steps": {}}

        # Create pipeline queues between stages
        pipeline_queues = {}
        execution_order = self._topological_sort(plan.dependency_graph)

        # Start pipeline stages
        stage_tasks = []
        for i, step_id in enumerate(execution_order):
            agent_name = plan.agent_assignments.get(step_id)
            if agent_name and agent_name in self._agents:
                # Create input/output queues
                input_queue = pipeline_queues.get(step_id, asyncio.Queue())
                output_queue = asyncio.Queue()
                pipeline_queues[f"{step_id}_output"] = output_queue

                # Start stage
                task = self._execute_pipeline_stage(self._agents[agent_name], step_id, input_queue, output_queue, plan)
                stage_tasks.append(task)

        # Wait for pipeline completion
        pipeline_results = await asyncio.gather(*stage_tasks, return_exceptions=True)

        for i, result in enumerate(pipeline_results):
            if isinstance(result, Exception):
                raise result
            step_id = execution_order[i]
            results["steps"][step_id] = result

        return results

    async def _execute_hierarchical(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute tasks with hierarchical coordination."""
        results = {"strategy": "hierarchical", "steps": {}}

        # Identify coordinator agent (highest capability score)
        coordinator = await self._select_coordinator_agent()

        if coordinator:
            # Use coordinator to manage sub-agents - get coordination plan
            await coordinator.invoke(f"Coordinate the following task execution plan: {plan.__dict__}")

            # Execute coordinated plan
            for step_id, agent_name in plan.agent_assignments.items():
                if agent_name in self._agents:
                    agent = self._agents[agent_name]
                    step_result = await self._execute_step(agent, step_id, plan)
                    results["steps"][step_id] = step_result

        return results

    async def _execute_adaptive(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute with adaptive strategy selection."""
        # Analyze current system state
        system_load = await self._calculate_system_load()
        agent_availability = await self._check_agent_availability()
        task_complexity = len(plan.agent_assignments)

        # Select optimal strategy based on conditions
        if system_load > 0.8:
            selected_strategy = OrchestrationStrategy.SEQUENTIAL
        elif task_complexity < 3 and agent_availability > 0.7:
            selected_strategy = OrchestrationStrategy.PARALLEL
        elif task_complexity > 5:
            selected_strategy = OrchestrationStrategy.HIERARCHICAL
        else:
            selected_strategy = OrchestrationStrategy.PIPELINE

        # Update plan strategy and execute
        plan.strategy = selected_strategy
        handler = self._strategy_handlers[selected_strategy]

        results = await handler(plan)
        results["selected_strategy"] = selected_strategy.value
        results["system_load"] = system_load
        results["agent_availability"] = agent_availability

        return results

    # Helper Methods

    async def _monitor_agent_health(self) -> None:
        """Background task to monitor agent health."""
        while True:
            try:
                for agent_name in list(self._agents.keys()):
                    # Send heartbeat and update agent state based on response
                    try:
                        # Simple health check - try to invoke agent
                        agent = self._agents[agent_name]
                        await asyncio.wait_for(agent.invoke("health_check"), timeout=5.0)
                        self._agent_states[agent_name] = AgentState.IDLE

                        # Update last heartbeat
                        if agent_name in self._agent_metrics:
                            self._agent_metrics[agent_name].last_heartbeat = datetime.now()

                    except asyncio.TimeoutError:
                        self._agent_states[agent_name] = AgentState.UNAVAILABLE
                        logger.warning(f"Agent {agent_name} health check timeout")
                    except Exception as e:
                        self._agent_states[agent_name] = AgentState.ERROR
                        logger.error(f"Agent {agent_name} health check failed: {e}")

                await asyncio.sleep(30)  # Health check interval

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)

    async def _collect_metrics(self) -> None:
        """Background task to collect performance metrics."""
        while True:
            try:
                # Update system metrics
                for agent_name, metrics in self._agent_metrics.items():
                    # Calculate success rate
                    total_tasks = metrics.tasks_completed + metrics.tasks_failed
                    if total_tasks > 0:
                        metrics.success_rate = metrics.tasks_completed / total_tasks

                    # Update current load (simplified)
                    metrics.current_load = min(
                        1.0,
                        len(
                            [
                                task
                                for task in self._active_tasks.values()
                                if agent_name in task.agent_assignments.values()
                            ]
                        )
                        / 3.0,
                    )

                await asyncio.sleep(60)  # Metrics collection interval

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(30)

    async def _sync_state_periodically(self) -> None:
        """Periodically sync state to Redis."""
        while True:
            try:
                await self._persist_state()
                await asyncio.sleep(self._state_sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"State sync error: {e}")
                await asyncio.sleep(60)

    async def _persist_state(self) -> None:
        """Persist orchestrator state to Redis."""
        # Simplified state persistence - could integrate with Redis if available
        try:
            state_data = {
                "agent_states": {k: v.value for k, v in self._agent_states.items()},
                "agent_metrics": {k: v.__dict__ for k, v in self._agent_metrics.items()},
                "active_tasks": {k: v.__dict__ for k, v in self._active_tasks.items()},
                "timestamp": datetime.now().isoformat(),
            }

            # Could save to file or Redis here
            logger.debug(f"State persisted: {len(state_data)} items")

        except Exception as e:
            logger.error(f"State persistence failed: {e}")

    async def _load_persisted_state(self) -> None:
        """Load persisted state from Redis."""
        # Simplified state loading - could integrate with Redis if available
        try:
            # Could load from file or Redis here
            logger.debug("State loading attempted")

        except Exception as e:
            logger.error(f"Failed to load persisted state: {e}")

    def _topological_sort(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on dependency graph."""
        from collections import defaultdict, deque

        # Build reverse graph and calculate in-degrees
        reverse_graph = defaultdict(list)
        in_degree = defaultdict(int)

        all_nodes = set(dependency_graph.keys())
        for node, deps in dependency_graph.items():
            for dep in deps:
                reverse_graph[dep].append(node)
                in_degree[node] += 1
                all_nodes.add(dep)

        # Initialize queue with nodes having no dependencies
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            for neighbor in reverse_graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

    # Additional helper methods would be implemented here...
    async def _analyze_task_complexity(self, description: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task complexity for planning."""
        # Simplified complexity analysis
        return {
            "complexity_score": min(10, len(description.split()) / 10),
            "estimated_steps": max(1, len(description.split("then")) + len(description.split("after"))),
            "resources": requirements,
        }

    async def _select_optimal_agents(self, task_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Select optimal agents for task steps."""
        # Simplified agent selection
        assignments = {}
        available_agents = [name for name, state in self._agent_states.items() if state == AgentState.IDLE]

        num_steps = task_analysis.get("estimated_steps", 1)
        for i in range(num_steps):
            if available_agents:
                step_id = f"step_{i+1}"
                # Round-robin assignment for simplicity
                assignments[step_id] = available_agents[i % len(available_agents)]

        return assignments

    async def _build_task_dependencies(
        self, task_analysis: Dict[str, Any], assignments: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """Build dependency graph for task steps."""
        # Simplified dependency building
        dependencies = {}
        step_ids = list(assignments.keys())

        for i, step_id in enumerate(step_ids):
            if i > 0:
                dependencies[step_id] = [step_ids[i - 1]]  # Sequential dependency
            else:
                dependencies[step_id] = []

        return dependencies

    async def _estimate_execution_time(self, task_analysis: Dict[str, Any], assignments: Dict[str, str]) -> float:
        """Estimate total execution time."""
        complexity = task_analysis.get("complexity_score", 1)
        num_steps = len(assignments)
        base_time = 30.0  # Base time per step

        return base_time * num_steps * (1 + complexity / 10)

    async def _identify_fallback_agents(self, assignments: Dict[str, str]) -> Dict[str, List[str]]:
        """Identify fallback agents for each assignment."""
        fallbacks = {}
        all_agents = list(self._agents.keys())

        for step_id, assigned_agent in assignments.items():
            available = [name for name in all_agents if name != assigned_agent]
            fallbacks[step_id] = available[:2]  # Up to 2 fallback agents

        return fallbacks

    async def _define_quality_gates(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define quality gates for task execution."""
        return [
            {"type": "response_time", "threshold": 60.0},
            {"type": "success_rate", "threshold": 0.8},
            {"type": "content_quality", "threshold": 0.7},
        ]

    async def _create_rollback_strategy(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create rollback strategy for failed executions."""
        return {
            "enabled": True,
            "max_retries": 3,
            "retry_delay": 5.0,
            "fallback_strategy": "sequential",
        }

    async def _discover_agent_capabilities(self, agent: BaseReasoningAgent) -> None:
        """Discover agent capabilities automatically."""
        # Simplified capability discovery
        capabilities = {
            "general_reasoning": AgentCapability(
                name="general_reasoning",
                skill_level=0.8,
                resource_requirements={"cpu": 0.5, "memory": 512},
                estimated_duration=30.0,
                success_rate=0.9,
            )
        }

        self._agent_capabilities[agent.name] = capabilities

    async def _execute_step(self, agent: BaseReasoningAgent, step_id: str, plan: TaskExecutionPlan) -> Dict[str, Any]:
        """Execute a single step with an agent."""
        start_time = datetime.now()

        try:
            # Update agent state
            self._agent_states[agent.name] = AgentState.BUSY

            # Execute step
            response = await agent.invoke(f"Execute step {step_id}")

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "step_id": step_id,
                "agent": agent.name,
                "result": response.content,
                "execution_time": execution_time,
                "status": "success",
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "step_id": step_id,
                "agent": agent.name,
                "error": str(e),
                "execution_time": execution_time,
                "status": "failed",
            }

        finally:
            # Reset agent state
            self._agent_states[agent.name] = AgentState.IDLE

    async def _check_quality_gates(self, result: Dict[str, Any], gates: List[Dict[str, Any]]) -> bool:
        """Check if result passes quality gates."""
        for gate in gates:
            gate_type = gate.get("type")
            threshold = gate.get("threshold")

            if gate_type == "response_time":
                if result.get("execution_time", 0) > threshold:
                    return False
            elif gate_type == "success_rate":
                if result.get("status") != "success":
                    return False

        return True

    async def _group_by_dependency_level(self, dependency_graph: Dict[str, List[str]]) -> Dict[int, List[str]]:
        """Group steps by dependency level for parallel execution."""
        levels = {}
        processed = set()
        level = 0

        while len(processed) < len(dependency_graph):
            current_level = []

            for step_id, deps in dependency_graph.items():
                if step_id not in processed and all(dep in processed for dep in deps):
                    current_level.append(step_id)

            if not current_level:
                break  # Circular dependency or error

            levels[level] = current_level
            processed.update(current_level)
            level += 1

        return levels

    async def _execute_pipeline_stage(
        self,
        agent: BaseReasoningAgent,
        step_id: str,
        input_queue: asyncio.Queue,
        output_queue: asyncio.Queue,
        plan: TaskExecutionPlan,
    ) -> Dict[str, Any]:
        """Execute a pipeline stage."""
        results = []

        while True:
            try:
                # Get input (with timeout)
                input_data = await asyncio.wait_for(input_queue.get(), timeout=60.0)

                if input_data is None:  # End signal
                    break

                # Process input
                response = await agent.invoke(f"Process: {input_data}")

                # Send to output
                await output_queue.put(response.content)
                results.append(response.content)

                input_queue.task_done()

            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Pipeline stage {step_id} error: {e}")
                await output_queue.put(None)  # Error signal
                break

        return {
            "step_id": step_id,
            "agent": agent.name,
            "processed_items": len(results),
            "status": "completed",
        }

    async def _select_coordinator_agent(self) -> Optional[BaseReasoningAgent]:
        """Select the best agent to act as coordinator."""
        best_agent = None
        best_score = 0.0

        for agent_name, agent in self._agents.items():
            if self._agent_states.get(agent_name) == AgentState.IDLE:
                # Calculate coordination score
                metrics = self._agent_metrics.get(agent_name)
                if metrics:
                    score = metrics.success_rate * (1 - metrics.current_load)
                    if score > best_score:
                        best_score = score
                        best_agent = agent

        return best_agent

    async def _calculate_system_load(self) -> float:
        """Calculate current system load."""
        if not self._agent_metrics:
            return 0.0

        total_load = sum(metrics.current_load for metrics in self._agent_metrics.values())
        return total_load / len(self._agent_metrics)

    async def _check_agent_availability(self) -> float:
        """Check agent availability ratio."""
        if not self._agent_states:
            return 0.0

        available = sum(1 for state in self._agent_states.values() if state == AgentState.IDLE)
        return available / len(self._agent_states)

    async def _update_agent_metrics(self, plan: TaskExecutionPlan, results: Dict[str, Any], success: bool) -> None:
        """Update agent performance metrics."""
        for step_id, agent_name in plan.agent_assignments.items():
            if agent_name in self._agent_metrics:
                metrics = self._agent_metrics[agent_name]

                if success:
                    metrics.tasks_completed += 1
                else:
                    metrics.tasks_failed += 1

                # Update average response time
                step_result = results.get("steps", {}).get(step_id, {})
                exec_time = step_result.get("execution_time", 0)
                if exec_time > 0:
                    current_avg = metrics.average_response_time
                    total_tasks = metrics.tasks_completed + metrics.tasks_failed
                    metrics.average_response_time = (current_avg * (total_tasks - 1) + exec_time) / total_tasks


@asynccontextmanager
async def orchestrator_session(orchestrator: EnhancedAgentOrchestrator):
    """Context manager for orchestrator sessions."""
    await orchestrator.initialize()
    try:
        yield orchestrator
    finally:
        await orchestrator.shutdown()
