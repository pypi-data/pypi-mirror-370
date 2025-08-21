"""Agent Orchestrator for coordinating multiple agents."""

import asyncio
from enum import Enum
from typing import Any, Dict, List, Optional

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatMessageContent


try:
    # SK 1.35.3 uses AuthorRole enum for roles
    from semantic_kernel.contents.author_role import AuthorRole  # type: ignore
except Exception:  # pragma: no cover - fallback if import path changes
    AuthorRole = None  # type: ignore

import logging

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Represents a task to be executed by agents."""

    def __init__(
        self,
        task_id: str,
        description: str,
        assigned_agent: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
    ):
        """Initialize a task.

        Args:
            task_id: Unique task identifier
            description: Task description
            assigned_agent: Name of assigned agent
            dependencies: List of task IDs this task depends on
        """
        self.task_id = task_id
        self.description = description
        self.assigned_agent = assigned_agent
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.result: Optional[str] = None
        self.error: Optional[str] = None


class AgentOrchestrator:
    """Orchestrator for coordinating multiple agents."""

    def __init__(self, kernel: Kernel, max_concurrent_tasks: int = 3):
        """Initialize the orchestrator.

        Args:
            kernel: Semantic Kernel instance
            max_concurrent_tasks: Maximum number of concurrent tasks
        """
        self._kernel = kernel
        self._agents: Dict[str, BaseReasoningAgent] = {}
        self._tasks: Dict[str, Task] = {}
        self._max_concurrent_tasks = max_concurrent_tasks
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._results: Dict[str, Any] = {}

    def register_agent(self, agent: BaseReasoningAgent) -> None:
        """Register an agent with the orchestrator.

        Args:
            agent: Agent to register
        """
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent.

        Args:
            agent_name: Name of agent to unregister
        """
        if agent_name in self._agents:
            del self._agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")

    def add_task(self, task: Task) -> None:
        """Add a task to be executed.

        Args:
            task: Task to add
        """
        self._tasks[task.task_id] = task
        logger.info(f"Added task: {task.task_id}")

    async def execute_tasks(self) -> Dict[str, Any]:
        """Execute all pending tasks.

        Returns:
            Dictionary of task results
        """
        # Build task queue respecting dependencies
        await self._build_task_queue()

        # Create worker tasks
        workers = [
            asyncio.create_task(self._task_worker(f"worker-{i}"))
            for i in range(min(self._max_concurrent_tasks, len(self._tasks)))
        ]

        # Wait for all tasks to complete
        await self._task_queue.join()

        # Cancel workers
        for worker in workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*workers, return_exceptions=True)

        return self._results

    async def _build_task_queue(self) -> None:
        """Build task queue respecting dependencies."""
        # Perform a simple Kahn topological sort to create an execution order
        # that respects dependencies. With multiple workers, this ensures dep
        # tasks appear earlier in the queue even if processed concurrently.
        indegree: Dict[str, int] = {}
        graph: Dict[str, List[str]] = {}

        # Initialize graph
        for task_id, task in self._tasks.items():
            indegree.setdefault(task_id, 0)
            for dep in task.dependencies:
                graph.setdefault(dep, []).append(task_id)
                indegree[task_id] = indegree.get(task_id, 0) + 1

        # Collect tasks with no incoming edges (no dependencies)
        from collections import deque

        queue: deque[str] = deque([tid for tid, deg in indegree.items() if deg == 0])
        visited_count = 0

        ordered: List[str] = []
        while queue:
            current = queue.popleft()
            ordered.append(current)
            visited_count += 1
            for neighbor in graph.get(current, []):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(indegree):
            logger.error("Circular dependencies detected or missing references; falling back to insertion order")
            ordered = list(self._tasks.keys())

        # Enqueue tasks in topological order
        for tid in ordered:
            await self._task_queue.put(self._tasks[tid])

    async def _task_worker(self, worker_name: str) -> None:
        """Worker to process tasks from the queue.

        Args:
            worker_name: Name of the worker
        """
        while True:
            try:
                task = await self._task_queue.get()
                logger.info(f"{worker_name} processing task: {task.task_id}")

                task.status = TaskStatus.IN_PROGRESS

                try:
                    result = await self._execute_task(task)
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    self._results[task.task_id] = result
                    logger.info(f"Task {task.task_id} completed successfully")

                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    self._results[task.task_id] = {"error": str(e)}
                    logger.error(f"Task {task.task_id} failed: {e}")

                finally:
                    self._task_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")

    async def _execute_task(self, task: Task) -> str:
        """Execute a single task.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        # Select agent for task
        agent = self._select_agent(task)

        if not agent:
            raise ValueError(f"No suitable agent found for task: {task.task_id}")

        # Execute task
        response = await agent.invoke(task.description)
        return response.content

    def _select_agent(self, task: Task) -> Optional[BaseReasoningAgent]:
        """Select an agent for a task.

        Args:
            task: Task to assign

        Returns:
            Selected agent or None
        """
        if task.assigned_agent and task.assigned_agent in self._agents:
            return self._agents[task.assigned_agent]

        # Default to first available agent
        if self._agents:
            return list(self._agents.values())[0]

        return None

    async def coordinate_discussion(self, topic: str, rounds: int = 3) -> List[ChatMessageContent]:
        """Coordinate a discussion between agents.

        Args:
            topic: Discussion topic
            rounds: Number of discussion rounds

        Returns:
            List of messages from the discussion
        """
        messages = []

        for round_num in range(rounds):
            logger.info(f"Discussion round {round_num + 1}/{rounds}")

            for agent_name, agent in self._agents.items():
                # Build context from previous messages
                # Render role as value if enum, else string
                def _role_to_str(role: object) -> str:
                    try:
                        val = getattr(role, "value", None)
                        return str(val) if val is not None else str(role)
                    except Exception:
                        return str(role)

                context = "\n".join(
                    [f"{_role_to_str(msg.role)}: {msg.content}" for msg in messages[-5:]]  # Last 5 messages
                )

                prompt = f"""
                Topic: {topic}
                Round: {round_num + 1}/{rounds}
                
                Previous discussion:
                {context if context else "This is the start of the discussion."}
                
                Please provide your perspective on this topic.
                """

                response = await agent.invoke(prompt)
                messages.append(response)

        return messages

    async def aggregate_results(self, results: List[str], aggregation_method: str = "summary") -> str:
        """Aggregate results from multiple agents.

        Args:
            results: List of results to aggregate
            aggregation_method: Method to use for aggregation

        Returns:
            Aggregated result
        """
        if not self._agents:
            raise ValueError("No agents registered")

        # Use first agent for aggregation
        agent = list(self._agents.values())[0]

        if aggregation_method == "summary":
            prompt = f"""
            Please provide a comprehensive summary of the following results:
            
            {chr(10).join(f"Result {i+1}: {result}" for i, result in enumerate(results))}
            
            Synthesize the key points and provide a cohesive summary.
            """
        elif aggregation_method == "consensus":
            prompt = f"""
            Analyze the following results and identify the consensus:
            
            {chr(10).join(f"Result {i+1}: {result}" for i, result in enumerate(results))}
            
            What are the common agreements and key differences?
            """
        else:
            prompt = f"""
            Aggregate the following results:
            
            {chr(10).join(f"Result {i+1}: {result}" for i, result in enumerate(results))}
            """

        response = await agent.invoke(prompt)
        return response.content
