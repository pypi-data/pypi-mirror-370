"""
Agent Orchestration Integration Utilities

Integration utilities to connect enhanced orchestration features
with existing MSA Reasoning Kernel components.
"""

import asyncio
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from semantic_kernel import Kernel

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.agents.enhanced_orchestrator import (
    EnhancedAgentOrchestrator,
    AgentCapability,
    OrchestrationStrategy,
)
from reasoning_kernel.agents.state_manager import StateManager, StateChangeType
from reasoning_kernel.agents.communication_patterns import (
    EnhancedCommunicationManager,
    CommunicationPattern,
    MessagePriority,
)
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class OrchestrationIntegration:
    """
    Main integration class for enhanced agent orchestration features.
    Provides a unified interface for all orchestration capabilities.
    """

    def __init__(
        self,
        kernel: Kernel,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize orchestration integration.

        Args:
            kernel: Semantic Kernel instance
            config: Configuration options
        """
        self._kernel = kernel
        self._config = config or {}

        # Initialize components
        self._orchestrator = EnhancedAgentOrchestrator(
            kernel=kernel,
            max_concurrent_tasks=self._config.get("max_concurrent_tasks", 5),
            enable_state_persistence=self._config.get("enable_state_persistence", True),
            adaptive_load_balancing=self._config.get("adaptive_load_balancing", True),
        )

        self._state_manager = StateManager(
            storage_path=self._config.get("state_storage_path"),
            snapshot_interval=self._config.get("snapshot_interval", 300),
            max_history_size=self._config.get("max_history_size", 1000),
            enable_compression=self._config.get("enable_compression", True),
        )

        self._communication_manager: Optional[EnhancedCommunicationManager] = None

        # Registered agents
        self._agents: Dict[str, BaseReasoningAgent] = {}

        # Integration state
        self._is_initialized = False

    async def initialize(self) -> None:
        """Initialize all orchestration components."""
        if self._is_initialized:
            return

        logger.info("Initializing orchestration integration")

        # Initialize state manager
        await self._state_manager.initialize()

        # Initialize orchestrator
        await self._orchestrator.initialize()

        # Set up state change listeners
        self._state_manager.add_state_listener(self._on_state_change)

        self._is_initialized = True
        logger.info("Orchestration integration initialized successfully")

    async def shutdown(self) -> None:
        """Shutdown all orchestration components."""
        if not self._is_initialized:
            return

        logger.info("Shutting down orchestration integration")

        # Shutdown components in reverse order
        if self._communication_manager:
            await self._communication_manager.shutdown()

        await self._orchestrator.shutdown()
        await self._state_manager.shutdown()

        self._is_initialized = False
        logger.info("Orchestration integration shutdown complete")

    async def register_agent(
        self,
        agent: BaseReasoningAgent,
        capabilities: Optional[Dict[str, AgentCapability]] = None,
    ) -> None:
        """Register an agent with orchestration capabilities.

        Args:
            agent: Agent to register
            capabilities: Agent capabilities for task assignment
        """
        if not self._is_initialized:
            await self.initialize()

        # Register with orchestrator
        await self._orchestrator.register_agent(agent, capabilities)

        # Store locally
        self._agents[agent.name] = agent

        # Initialize communication manager if this is the first agent
        if self._communication_manager is None:
            self._communication_manager = EnhancedCommunicationManager(self._agents)
            await self._communication_manager.initialize()

        # Record state change
        await self._state_manager.record_state_change(
            StateChangeType.AGENT_REGISTERED,
            agent.name,
            new_value={
                "description": agent.description,
                "capabilities": list(capabilities.keys()) if capabilities else [],
            },
        )

        logger.info(f"Registered agent {agent.name} with orchestration integration")

    async def execute_complex_task(
        self,
        task_description: str,
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a complex task using enhanced orchestration.

        Args:
            task_description: Description of the task
            strategy: Orchestration strategy to use
            requirements: Task requirements and constraints

        Returns:
            Task execution results
        """
        if not self._is_initialized:
            await self.initialize()

        logger.info(f"Executing complex task with {strategy.value} strategy")

        # Create execution plan
        plan = await self._orchestrator.create_execution_plan(task_description, strategy, requirements)

        # Record task start
        await self._state_manager.record_state_change(
            StateChangeType.TASK_STARTED,
            plan.task_id,
            new_value={
                "description": task_description,
                "strategy": strategy.value,
                "estimated_duration": plan.estimated_duration,
            },
        )

        try:
            # Execute plan
            results = await self._orchestrator.execute_plan(plan)

            # Record completion
            await self._state_manager.record_state_change(
                StateChangeType.TASK_COMPLETED,
                plan.task_id,
                new_value={
                    "status": results.get("status"),
                    "execution_time": results.get("execution_time"),
                },
            )

            logger.info(f"Complex task completed successfully: {results.get('status')}")
            return results

        except Exception as e:
            # Record failure
            await self._state_manager.record_state_change(
                StateChangeType.TASK_FAILED, plan.task_id, new_value={"error": str(e)}
            )

            logger.error(f"Complex task failed: {e}")
            raise

    async def coordinate_agent_discussion(
        self,
        topic: str,
        participants: Optional[List[str]] = None,
        rounds: int = 3,
        pattern: CommunicationPattern = CommunicationPattern.BROADCAST,
    ) -> List[Dict[str, Any]]:
        """Coordinate a discussion between agents using enhanced communication.

        Args:
            topic: Discussion topic
            participants: Participating agent names (all if None)
            rounds: Number of discussion rounds
            pattern: Communication pattern to use

        Returns:
            Discussion messages and results
        """
        if not self._is_initialized or not self._communication_manager:
            await self.initialize()

        if participants is None:
            participants = list(self._agents.keys())

        logger.info(f"Starting agent discussion on '{topic}' with {len(participants)} participants")

        discussion_results = []

        for round_num in range(rounds):
            round_messages = []

            # Send discussion prompt to all participants via communication manager
            if self._communication_manager:
                await self._communication_manager.send_message(
                    pattern=pattern,
                    sender="orchestrator",
                    recipients=participants,
                    payload={
                        "action": "discuss",
                        "topic": topic,
                        "round": round_num + 1,
                        "total_rounds": rounds,
                        "previous_messages": discussion_results[-5:] if discussion_results else [],
                    },
                    priority=MessagePriority.NORMAL,
                    requires_response=True,
                    timeout_seconds=60.0,
                )

            # Wait for responses (simplified - in real implementation would use communication protocols)
            await asyncio.sleep(2.0)  # Give agents time to respond

            # Collect responses from agents
            for participant in participants:
                try:
                    response = await self._agents[participant].invoke(
                        f"Discuss topic: {topic}. Round {round_num + 1}/{rounds}"
                    )

                    round_messages.append(
                        {
                            "agent": participant,
                            "content": response.content,
                            "round": round_num + 1,
                            "timestamp": response.role,  # Using role field for timestamp placeholder
                        }
                    )

                except Exception as e:
                    logger.error(f"Failed to get response from {participant}: {e}")

            discussion_results.extend(round_messages)
            logger.info(f"Completed discussion round {round_num + 1}")

        return discussion_results

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status.

        Returns:
            System status information
        """
        if not self._is_initialized:
            return {"status": "not_initialized"}

        status = {
            "initialized": True,
            "orchestrator": await self._orchestrator.get_orchestrator_status(),
            "state_manager": await self._state_manager.get_state_statistics(),
            "agents": {
                name: {
                    "name": agent.name,
                    "description": agent.description,
                }
                for name, agent in self._agents.items()
            },
        }

        # Add communication manager stats if available
        if self._communication_manager:
            status["communication"] = await self._communication_manager.get_communication_statistics()

        return status

    async def validate_system_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of the orchestration system.

        Returns:
            Validation results
        """
        if not self._is_initialized:
            return {"valid": False, "error": "System not initialized"}

        # Validate state manager
        state_validation = await self._state_manager.validate_state_integrity()

        # Validate orchestrator
        orchestrator_status = await self._orchestrator.get_orchestrator_status()

        # Check agent consistency
        agent_validation = {
            "total_agents": len(self._agents),
            "orchestrator_agents": len(orchestrator_status["agents"]),
            "consistency": len(self._agents) == len(orchestrator_status["agents"]),
        }

        overall_valid = state_validation.get("valid", False) and agent_validation["consistency"]

        return {
            "valid": overall_valid,
            "state_manager": state_validation,
            "agent_consistency": agent_validation,
            "orchestrator_status": orchestrator_status,
        }

    async def create_state_snapshot(self) -> Dict[str, Any]:
        """Create a comprehensive state snapshot.

        Returns:
            State snapshot information
        """
        if not self._is_initialized:
            return {"error": "System not initialized"}

        # Get current states
        orchestrator_status = await self._orchestrator.get_orchestrator_status()

        agents_data = {}
        for name, agent in self._agents.items():
            agents_data[name] = {
                "name": agent.name,
                "description": agent.description,
                "chat_history_size": len(agent.get_chat_history()),
            }

        # Create snapshot
        snapshot = await self._state_manager.create_snapshot(
            agents=agents_data,
            tasks=orchestrator_status["tasks"],
            metrics={name: data["metrics"] for name, data in orchestrator_status["agents"].items()},
            system_config=self._config,
        )

        return {
            "snapshot_id": f"snapshot_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}",
            "timestamp": snapshot.timestamp.isoformat(),
            "agents": len(snapshot.agents),
            "tasks": len(snapshot.tasks),
            "metrics": len(snapshot.metrics),
        }

    # Private methods

    async def _on_state_change(self, change) -> None:
        """Handle state change events.

        Args:
            change: StateChange event
        """
        logger.debug(f"State change: {change.change_type.value} for {change.entity_id}")

        # Could implement additional logic here, such as:
        # - Triggering alerts for critical changes
        # - Updating external monitoring systems
        # - Adjusting orchestration parameters based on state


@asynccontextmanager
async def orchestration_context(
    kernel: Kernel,
    config: Optional[Dict[str, Any]] = None,
):
    """Context manager for orchestration integration.

    Args:
        kernel: Semantic Kernel instance
        config: Configuration options

    Yields:
        Initialized orchestration integration
    """
    integration = OrchestrationIntegration(kernel, config)
    await integration.initialize()

    try:
        yield integration
    finally:
        await integration.shutdown()


# Convenience functions for common orchestration tasks


async def quick_agent_discussion(
    agents: List[BaseReasoningAgent],
    topic: str,
    kernel: Kernel,
    rounds: int = 2,
) -> List[Dict[str, Any]]:
    """Quickly set up and run an agent discussion.

    Args:
        agents: List of agents to participate
        topic: Discussion topic
        kernel: Semantic Kernel instance
        rounds: Number of discussion rounds

    Returns:
        Discussion results
    """
    async with orchestration_context(kernel) as integration:
        # Register agents
        for agent in agents:
            await integration.register_agent(agent)

        # Run discussion
        return await integration.coordinate_agent_discussion(topic, rounds=rounds)


async def execute_adaptive_task(
    agents: List[BaseReasoningAgent],
    task_description: str,
    kernel: Kernel,
    requirements: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a task with adaptive orchestration.

    Args:
        agents: List of available agents
        task_description: Task to execute
        kernel: Semantic Kernel instance
        requirements: Task requirements

    Returns:
        Execution results
    """
    async with orchestration_context(kernel) as integration:
        # Register agents
        for agent in agents:
            await integration.register_agent(agent)

        # Execute task
        return await integration.execute_complex_task(task_description, OrchestrationStrategy.ADAPTIVE, requirements)
