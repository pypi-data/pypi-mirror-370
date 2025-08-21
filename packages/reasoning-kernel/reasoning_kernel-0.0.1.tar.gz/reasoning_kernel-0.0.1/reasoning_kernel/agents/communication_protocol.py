"""
Unified Agent Communication Protocol for MSA Reasoning System

This module defines the communication protocol and coordination mechanisms
for the four core MSA agents:
- ModelSynthesisAgent
- ProbabilisticReasoningAgent
- KnowledgeRetrievalAgent
- EvaluationAgent

Features:
- Standard message formats between agents
- Async communication patterns
- Error handling and retry mechanisms
- Coordination workflow management
- Comprehensive logging and monitoring
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import math
from typing import Any, Callable, Dict, List, Optional

from reasoning_kernel.utils.security import get_secure_logger
from reasoning_kernel.utils.security import SecureRandom


logger = get_secure_logger(__name__)


class MessageType(Enum):
    """Types of messages in the communication protocol"""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    COORDINATION = "coordination"


class AgentRole(Enum):
    """Roles of agents in the MSA system"""

    MODEL_SYNTHESIS = "model_synthesis"
    PROBABILISTIC_REASONING = "probabilistic_reasoning"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    EVALUATION = "evaluation"
    ORCHESTRATOR = "orchestrator"


class MessagePriority(Enum):
    """Priority levels for messages"""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class AgentMessage:
    """Standard message format for agent communication"""

    message_id: str
    message_type: MessageType
    sender: AgentRole
    recipient: AgentRole
    priority: MessagePriority
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    retry_count: int = 0
    timeout_seconds: int = 30
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowStep:
    """Individual step in a coordination workflow"""

    step_id: str
    agent_role: AgentRole
    function_name: str
    inputs: Dict[str, Any]
    dependencies: List[str]
    timeout_seconds: int = 30
    retry_policy: Dict[str, Any] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class CoordinationWorkflow:
    """Complete workflow for coordinating multiple agents"""

    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "created"  # created, running, completed, failed, cancelled
    results: Dict[str, Any] = None
    error: Optional[str] = None


class RetryPolicy:
    """Retry policy configuration"""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0,
        exponential: bool = True,
    ):
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self.exponential = exponential

    def get_delay(self, retry_count: int) -> float:
        """Calculate delay for a given retry count"""
        if self.exponential:
            if self.backoff_multiplier > 1:
                # Calculate the maximum exponent that does not exceed max_delay
                max_exponent = int(math.log(self.max_delay, self.backoff_multiplier))
                capped_retry_count = min(retry_count, max_exponent)
            else:
                capped_retry_count = retry_count
            delay = min(self.max_delay, math.pow(self.backoff_multiplier, capped_retry_count))
        else:
            delay = min(self.max_delay, retry_count * self.backoff_multiplier)
        return delay


class CommunicationManager:
    """
    Central manager for agent communication and coordination.

    Handles message routing, workflow orchestration, error handling,
    and monitoring of agent interactions.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[AgentRole, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_messages: Dict[str, AgentMessage] = {}
        self.active_workflows: Dict[str, CoordinationWorkflow] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}

        # Communication statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_failed": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "average_response_time": 0.0,
        }

        # Default retry policy
        self.default_retry_policy = RetryPolicy(
            max_retries=self.config.get("max_retries", 3),
            backoff_multiplier=self.config.get("backoff_multiplier", 2.0),
            max_delay=self.config.get("max_delay", 60.0),
        )

        # Start background tasks
        self._message_processor_task = None
        self._heartbeat_task = None
        self._cleanup_task = None

    async def initialize(self):
        """Initialize the communication manager"""
        logger.info("Initializing agent communication manager")

        # Start background tasks
        self._message_processor_task = asyncio.create_task(self._process_messages())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_messages())

        logger.info("Communication manager initialized successfully")

    async def shutdown(self):
        """Shutdown the communication manager"""
        logger.info("Shutting down communication manager")

        # Cancel background tasks
        if self._message_processor_task:
            self._message_processor_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(
            self._message_processor_task,
            self._heartbeat_task,
            self._cleanup_task,
            return_exceptions=True,
        )

        logger.info("Communication manager shutdown complete")

    def register_agent(self, role: AgentRole, agent_instance: Any):
        """Register an agent with the communication manager"""
        self.agents[role] = agent_instance
        logger.info(f"Registered agent: {role.value}")

    async def send_message(self, message: AgentMessage) -> str:
        """
        Send a message to another agent.

        Args:
            message: The message to send

        Returns:
            Message ID for tracking
        """
        try:
            # Validate message
            if not self._validate_message(message):
                raise ValueError("Invalid message format")

            # Add to queue for processing
            await self.message_queue.put(message)

            # Track pending message if expecting response
            if message.message_type == MessageType.REQUEST:
                self.pending_messages[message.message_id] = message

            self.stats["messages_sent"] += 1
            logger.debug(
                f"Message queued: {message.message_id} from {message.sender.value} to {message.recipient.value}"
            )

            return message.message_id

        except Exception as e:
            self.stats["messages_failed"] += 1
            logger.error(f"Failed to send message: {e}")
            raise

    async def send_request(
        self,
        sender: AgentRole,
        recipient: AgentRole,
        function_name: str,
        parameters: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Send a request message and wait for response.

        Args:
            sender: Requesting agent role
            recipient: Target agent role
            function_name: Function to call on recipient
            parameters: Function parameters
            priority: Message priority
            timeout: Timeout in seconds

        Returns:
            Response payload
        """
        message_id = SecureRandom.generate_uuid()
        correlation_id = message_id

        request_message = AgentMessage(
            message_id=message_id,
            message_type=MessageType.REQUEST,
            sender=sender,
            recipient=recipient,
            priority=priority,
            payload={"function_name": function_name, "parameters": parameters},
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            timeout_seconds=timeout,
        )

        # Send request
        await self.send_message(request_message)

        # Wait for response
        response = await self._wait_for_response(correlation_id, timeout)

        if response.message_type == MessageType.ERROR:
            raise Exception(f"Request failed: {response.payload.get('error', 'Unknown error')}")

        return response.payload

    async def send_response(
        self,
        original_request: AgentMessage,
        response_payload: Dict[str, Any],
        success: bool = True,
    ):
        """Send a response to a request message"""
        response_message = AgentMessage(
            message_id=SecureRandom.generate_uuid(),
            message_type=MessageType.RESPONSE if success else MessageType.ERROR,
            sender=original_request.recipient,
            recipient=original_request.sender,
            priority=original_request.priority,
            payload=response_payload,
            timestamp=datetime.now(),
            correlation_id=original_request.correlation_id,
        )

        await self.send_message(response_message)

    async def broadcast_event(self, sender: AgentRole, event_type: str, event_data: Dict[str, Any]):
        """Broadcast an event to all agents"""
        event_message = AgentMessage(
            message_id=SecureRandom.generate_uuid(),
            message_type=MessageType.EVENT,
            sender=sender,
            recipient=AgentRole.ORCHESTRATOR,  # Use orchestrator as broadcast recipient
            priority=MessagePriority.NORMAL,
            payload={"event_type": event_type, "event_data": event_data},
            timestamp=datetime.now(),
        )

        # Send to all registered agents
        for agent_role in self.agents.keys():
            if agent_role != sender:
                event_copy = AgentMessage(
                    message_id=SecureRandom.generate_uuid(),
                    message_type=event_message.message_type,
                    sender=event_message.sender,
                    recipient=agent_role,
                    priority=event_message.priority,
                    payload=event_message.payload,
                    timestamp=event_message.timestamp,
                )
                await self.send_message(event_copy)

    async def execute_workflow(self, workflow: CoordinationWorkflow) -> Dict[str, Any]:
        """
        Execute a coordination workflow across multiple agents.

        Args:
            workflow: The workflow to execute

        Returns:
            Workflow results
        """
        logger.info(f"Starting workflow execution: {workflow.name}")

        try:
            workflow.status = "running"
            workflow.started_at = datetime.now()
            self.active_workflows[workflow.workflow_id] = workflow

            # Execute steps based on dependencies
            completed_steps = set()
            step_results = {}

            while len(completed_steps) < len(workflow.steps):
                # Find ready steps (all dependencies completed)
                ready_steps = [
                    step
                    for step in workflow.steps
                    if step.status == "pending" and all(dep in completed_steps for dep in step.dependencies)
                ]

                if not ready_steps:
                    # Check for failed steps
                    failed_steps = [step for step in workflow.steps if step.status == "failed"]
                    if failed_steps:
                        raise Exception(f"Workflow failed due to step failures: {[s.step_id for s in failed_steps]}")

                    # No ready steps - possible circular dependency
                    pending_steps = [step for step in workflow.steps if step.status == "pending"]
                    if pending_steps:
                        raise Exception(
                            f"Circular dependency detected in workflow steps: {[s.step_id for s in pending_steps]}"
                        )

                    break  # All steps completed

                # Execute ready steps in parallel
                step_tasks = []
                for step in ready_steps:
                    step.status = "running"
                    task = asyncio.create_task(self._execute_workflow_step(step, step_results))
                    step_tasks.append((step, task))

                # Wait for all steps to complete
                for step, task in step_tasks:
                    try:
                        result = await task
                        step.result = result
                        step.status = "completed"
                        step_results[step.step_id] = result
                        completed_steps.add(step.step_id)
                        logger.debug(f"Workflow step completed: {step.step_id}")

                    except Exception as e:
                        step.error = str(e)
                        step.status = "failed"
                        logger.error(f"Workflow step failed: {step.step_id} - {e}")

                        # Check if this is a critical step
                        if step.retry_policy is None or step.retry_count >= step.retry_policy.get("max_retries", 0):
                            # No retry or max retries exceeded
                            workflow.status = "failed"
                            workflow.error = f"Critical step failed: {step.step_id}"
                            raise e

            # Workflow completed successfully
            workflow.status = "completed"
            workflow.completed_at = datetime.now()
            workflow.results = step_results

            self.stats["workflows_completed"] += 1
            logger.info(f"Workflow completed successfully: {workflow.name}")

            return step_results

        except Exception as e:
            workflow.status = "failed"
            workflow.error = str(e)
            workflow.completed_at = datetime.now()

            self.stats["workflows_failed"] += 1
            logger.error(f"Workflow failed: {workflow.name} - {e}")
            raise

        finally:
            # Clean up workflow from active workflows
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]

    async def _execute_workflow_step(self, step: WorkflowStep, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            # Get target agent
            target_agent = self.agents.get(step.agent_role)
            if not target_agent:
                raise Exception(f"Agent not found: {step.agent_role}")

            # Prepare inputs (may include results from previous steps)
            resolved_inputs = self._resolve_step_inputs(step.inputs, previous_results)

            # Send request to agent
            response = await self.send_request(
                sender=AgentRole.ORCHESTRATOR,
                recipient=step.agent_role,
                function_name=step.function_name,
                parameters=resolved_inputs,
                timeout=step.timeout_seconds,
            )

            return response

        except Exception as e:
            logger.error(f"Step execution failed: {step.step_id} - {e}")
            raise

    def _resolve_step_inputs(self, inputs: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve step inputs by substituting references to previous step results"""
        resolved = {}

        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Reference to previous step result
                reference = value[2:-1]  # Remove ${ and }

                if "." in reference:
                    step_id, result_key = reference.split(".", 1)
                    if step_id in previous_results and isinstance(previous_results[step_id], dict):
                        resolved[key] = previous_results[step_id].get(result_key, value)
                    else:
                        resolved[key] = value  # Keep original if not found
                else:
                    resolved[key] = previous_results.get(reference, value)
            else:
                resolved[key] = value

        return resolved

    async def _process_messages(self):
        """Background task to process messages from the queue"""
        while True:
            try:
                message = await self.message_queue.get()
                await self._handle_message(message)
                self.message_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue

    async def _handle_message(self, message: AgentMessage):
        """Handle an individual message"""
        try:
            # Responses and errors don't require a registered recipient agent
            if message.message_type == MessageType.RESPONSE:
                await self._handle_response(message)
                # Update metrics
                self.stats["messages_received"] += 1
                return
            if message.message_type == MessageType.ERROR:
                await self._handle_error(message)
                # Update metrics
                self.stats["messages_received"] += 1
                return

            recipient_agent = self.agents.get(message.recipient)
            if not recipient_agent:
                logger.warning(f"Recipient agent not found: {message.recipient}")
                return

            start_time = datetime.now()

            if message.message_type == MessageType.REQUEST:
                # Handle request message
                await self._handle_request(message, recipient_agent)

            elif message.message_type == MessageType.EVENT:
                # Handle event message
                await self._handle_event(message, recipient_agent)

            # Update response time statistics
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_response_time_stats(response_time)

            self.stats["messages_received"] += 1

        except Exception as e:
            logger.error(f"Failed to handle message {message.message_id}: {e}")

            # Send error response if it was a request
            if message.message_type == MessageType.REQUEST:
                await self.send_response(message, {"error": str(e)}, success=False)

    async def _handle_request(self, message: AgentMessage, recipient_agent: Any):
        """Handle a request message"""
        try:
            function_name = message.payload.get("function_name")
            parameters = message.payload.get("parameters", {})

            # Call the function on the recipient agent
            if hasattr(recipient_agent, function_name):
                function = getattr(recipient_agent, function_name)

                if asyncio.iscoroutinefunction(function):
                    result = await function(**parameters)
                else:
                    result = function(**parameters)

                # Send success response
                from dataclasses import asdict
                from dataclasses import is_dataclass

                if is_dataclass(result):
                    result = asdict(result)

                # Send success response
                await self.send_response(message, {"result": result}, success=True)

            else:
                raise AttributeError(f"Function {function_name} not found on agent {message.recipient}")

        except Exception as e:
            # Send error response
            await self.send_response(message, {"error": str(e)}, success=False)

    async def _handle_response(self, message: AgentMessage):
        """Handle a response message"""
        correlation_id = message.correlation_id
        if correlation_id and correlation_id in self.pending_messages:
            # Store response for waiting request
            self.pending_messages[correlation_id] = message

    async def _handle_event(self, message: AgentMessage, recipient_agent: Any):
        """Handle an event message"""
        event_type = message.payload.get("event_type")
        event_data = message.payload.get("event_data", {})

        # Call event listeners
        listeners = self.event_listeners.get(event_type, [])
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event_data)
                else:
                    listener(event_data)
            except Exception as e:
                logger.error(f"Event listener failed: {e}")

    async def _handle_error(self, message: AgentMessage):
        """Handle an error message"""
        logger.error(f"Received error message: {message.payload}")

        # Update pending message if this is a response to a request
        correlation_id = message.correlation_id
        if correlation_id and correlation_id in self.pending_messages:
            self.pending_messages[correlation_id] = message

    async def _wait_for_response(self, correlation_id: str, timeout: int) -> AgentMessage:
        """Wait for a response message with the given correlation ID"""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            if correlation_id in self.pending_messages:
                stored = self.pending_messages.get(correlation_id)
                # Only return once an actual RESPONSE or ERROR has been stored
                if isinstance(stored, AgentMessage) and stored.message_type in (
                    MessageType.RESPONSE,
                    MessageType.ERROR,
                ):
                    response = self.pending_messages.pop(correlation_id)
                    return response

            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

        raise TimeoutError(f"Response timeout after {timeout} seconds")

    async def _heartbeat_monitor(self):
        """Monitor agent health with heartbeat messages"""
        while True:
            try:
                for agent_role, agent in self.agents.items():
                    # Send heartbeat message
                    heartbeat_message = AgentMessage(
                        message_id=SecureRandom.generate_uuid(),
                        message_type=MessageType.HEARTBEAT,
                        sender=AgentRole.ORCHESTRATOR,
                        recipient=agent_role,
                        priority=MessagePriority.LOW,
                        payload={"timestamp": datetime.now().isoformat()},
                        timestamp=datetime.now(),
                        timeout_seconds=10,
                    )

                    try:
                        await self.send_message(heartbeat_message)
                    except Exception as e:
                        logger.warning(f"Heartbeat failed for agent {agent_role}: {e}")

                # Wait before next heartbeat cycle
                await asyncio.sleep(self.config.get("heartbeat_interval", 30))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(5)  # Short delay before retry

    async def _cleanup_expired_messages(self):
        """Clean up expired pending messages"""
        while True:
            try:
                current_time = datetime.now()
                expired_messages = []

                for message_id, message in self.pending_messages.items():
                    if (current_time - message.timestamp).total_seconds() > message.timeout_seconds:
                        expired_messages.append(message_id)

                for message_id in expired_messages:
                    del self.pending_messages[message_id]
                    logger.debug(f"Cleaned up expired message: {message_id}")

                # Cleanup every minute
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message cleanup error: {e}")
                await asyncio.sleep(60)

    def _validate_message(self, message: AgentMessage) -> bool:
        """Validate message format and content"""
        if not isinstance(message.message_id, str) or not message.message_id:
            return False

        if not isinstance(message.sender, AgentRole) or not isinstance(message.recipient, AgentRole):
            return False

        if not isinstance(message.message_type, MessageType):
            return False

        if not isinstance(message.payload, dict):
            return False

        return True

    def _update_response_time_stats(self, response_time: float):
        """Update average response time statistics"""
        current_avg = self.stats["average_response_time"]
        message_count = self.stats["messages_received"]

        if message_count == 0:
            self.stats["average_response_time"] = response_time
        else:
            # Exponential moving average
            alpha = 0.1  # Smoothing factor
            self.stats["average_response_time"] = alpha * response_time + (1 - alpha) * current_avg

    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics"""
        return {
            **self.stats,
            "active_workflows": len(self.active_workflows),
            "pending_messages": len(self.pending_messages),
            "registered_agents": len(self.agents),
        }


# Workflow builder helper functions
def create_msa_reasoning_workflow(scenario: str, config: Dict[str, Any] = None) -> CoordinationWorkflow:
    """
    Create a standard MSA reasoning workflow.

    This workflow coordinates all four agents to perform complete reasoning:
    1. Knowledge retrieval
    2. Model synthesis
    3. Probabilistic reasoning
    4. Evaluation
    """
    workflow_id = SecureRandom.generate_uuid()
    config = config or {}

    steps = [
        # Step 1: Retrieve relevant knowledge
        WorkflowStep(
            step_id="knowledge_retrieval",
            agent_role=AgentRole.KNOWLEDGE_RETRIEVAL,
            function_name="retrieve_knowledge",
            inputs={
                "query": scenario,
                "max_results": config.get("max_knowledge_items", 10),
                "min_relevance_score": config.get("min_relevance", 0.5),
            },
            dependencies=[],
            timeout_seconds=30,
        ),
        # Step 2: Synthesize probabilistic model
        WorkflowStep(
            step_id="model_synthesis",
            agent_role=AgentRole.MODEL_SYNTHESIS,
            function_name="synthesize_model",
            inputs={
                "scenario": scenario,
                "knowledge_base": "${knowledge_retrieval.knowledge_items}",
                "max_iterations": config.get("max_synthesis_iterations", 5),
            },
            dependencies=["knowledge_retrieval"],
            timeout_seconds=60,
        ),
        # Step 3: Perform probabilistic reasoning
        WorkflowStep(
            step_id="probabilistic_reasoning",
            agent_role=AgentRole.PROBABILISTIC_REASONING,
            function_name="perform_inference",
            inputs={
                "model_code": "${model_synthesis.program_code}",
                "query_variables": config.get("query_variables", ["outcome"]),
                "num_samples": config.get("num_samples", 1000),
                "inference_method": config.get("inference_method", "mcmc"),
            },
            dependencies=["model_synthesis"],
            timeout_seconds=120,
        ),
        # Step 4: Evaluate reasoning quality
        WorkflowStep(
            step_id="evaluation",
            agent_role=AgentRole.EVALUATION,
            function_name="evaluate_reasoning",
            inputs={
                "reasoning_result": {
                    "knowledge_extraction": "${knowledge_retrieval}",
                    "model_synthesis": "${model_synthesis}",
                    "probabilistic_reasoning": "${probabilistic_reasoning}",
                    "scenario": scenario,
                },
                "context": scenario,
                "evaluation_criteria": config.get("evaluation_criteria", ["coherence", "consistency", "completeness"]),
            },
            dependencies=[
                "knowledge_retrieval",
                "model_synthesis",
                "probabilistic_reasoning",
            ],
            timeout_seconds=45,
        ),
    ]

    return CoordinationWorkflow(
        workflow_id=workflow_id,
        name="MSA Reasoning Workflow",
        description=f"Complete MSA reasoning workflow for scenario: {scenario[:100]}...",
        steps=steps,
        created_at=datetime.now(),
    )


# Export main classes and functions
__all__ = [
    "CommunicationManager",
    "AgentMessage",
    "WorkflowStep",
    "CoordinationWorkflow",
    "MessageType",
    "AgentRole",
    "MessagePriority",
    "RetryPolicy",
    "create_msa_reasoning_workflow",
]
