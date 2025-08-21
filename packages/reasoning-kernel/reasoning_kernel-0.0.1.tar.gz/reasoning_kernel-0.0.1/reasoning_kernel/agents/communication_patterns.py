"""
Enhanced Communication Patterns for Agent Orchestration

Advanced communication protocols, message routing, and coordination patterns
for improved agent collaboration in the MSA Reasoning Kernel.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
from abc import ABC, abstractmethod

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class CommunicationPattern(Enum):
    """Different communication patterns for agent coordination."""

    DIRECT = "direct"  # Direct agent-to-agent communication
    BROADCAST = "broadcast"  # One-to-many messaging
    MULTICAST = "multicast"  # Many-to-many messaging
    PIPELINE = "pipeline"  # Sequential processing chain
    SCATTER_GATHER = "scatter_gather"  # Parallel processing and aggregation
    PUBLISH_SUBSCRIBE = "publish_subscribe"  # Event-driven communication
    REQUEST_RESPONSE = "request_response"  # Synchronous request/response


class MessagePriority(Enum):
    """Message priority levels."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class MessageStatus(Enum):
    """Message processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class CommunicationMessage:
    """Enhanced message structure for agent communication."""

    message_id: str
    pattern: CommunicationPattern
    priority: MessagePriority
    sender: str
    recipients: List[str]
    payload: Dict[str, Any]
    timestamp: datetime
    timeout_seconds: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    requires_response: bool = False
    response_timeout: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: MessageStatus = MessageStatus.PENDING
    responses: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CommunicationChannel:
    """Represents a communication channel between agents."""

    channel_id: str
    participants: Set[str]
    channel_type: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    is_active: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)


class CommunicationProtocol(ABC):
    """Abstract base class for communication protocols."""

    @abstractmethod
    async def send_message(self, message: CommunicationMessage) -> bool:
        """Send a message through this protocol."""
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[CommunicationMessage]:
        """Receive a message from this protocol."""
        pass

    @abstractmethod
    async def handle_response(self, message: CommunicationMessage, response: Any) -> None:
        """Handle a response to a message."""
        pass


class DirectCommunicationProtocol(CommunicationProtocol):
    """Direct one-to-one communication protocol."""

    def __init__(self, agents: Dict[str, BaseReasoningAgent]):
        self._agents = agents
        self._message_queues: Dict[str, asyncio.Queue] = {}

    async def send_message(self, message: CommunicationMessage) -> bool:
        """Send a message directly to recipients."""
        try:
            for recipient in message.recipients:
                if recipient in self._agents:
                    if recipient not in self._message_queues:
                        self._message_queues[recipient] = asyncio.Queue()

                    await self._message_queues[recipient].put(message)
                    logger.debug(f"Sent direct message {message.message_id} to {recipient}")

            return True

        except Exception as e:
            logger.error(f"Failed to send direct message: {e}")
            return False

    async def receive_message(self, agent_name: str) -> Optional[CommunicationMessage]:
        """Receive a message for a specific agent."""
        if agent_name not in self._message_queues:
            self._message_queues[agent_name] = asyncio.Queue()

        try:
            message = await asyncio.wait_for(self._message_queues[agent_name].get(), timeout=1.0)
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive message for {agent_name}: {e}")
            return None

    async def handle_response(self, message: CommunicationMessage, response: Any) -> None:
        """Handle a response to a direct message."""
        message.responses.append({"timestamp": datetime.now(), "response": response, "status": "completed"})


class BroadcastCommunicationProtocol(CommunicationProtocol):
    """One-to-many broadcast communication protocol."""

    def __init__(self, agents: Dict[str, BaseReasoningAgent]):
        self._agents = agents
        self._broadcast_channels: Dict[str, List[str]] = {}
        self._message_queues: Dict[str, asyncio.Queue] = {}

    async def send_message(self, message: CommunicationMessage) -> bool:
        """Broadcast a message to all recipients."""
        try:
            broadcast_id = str(uuid.uuid4())

            for recipient in message.recipients:
                if recipient in self._agents:
                    if recipient not in self._message_queues:
                        self._message_queues[recipient] = asyncio.Queue()

                    # Add broadcast metadata
                    broadcast_message = CommunicationMessage(
                        message_id=f"{message.message_id}_{recipient}",
                        pattern=CommunicationPattern.BROADCAST,
                        priority=message.priority,
                        sender=message.sender,
                        recipients=[recipient],
                        payload=message.payload,
                        timestamp=message.timestamp,
                        correlation_id=broadcast_id,
                        metadata={**message.metadata, "broadcast_id": broadcast_id},
                    )

                    await self._message_queues[recipient].put(broadcast_message)

            logger.info(f"Broadcast message {message.message_id} to {len(message.recipients)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return False

    async def receive_message(self, agent_name: str) -> Optional[CommunicationMessage]:
        """Receive a broadcast message for a specific agent."""
        if agent_name not in self._message_queues:
            self._message_queues[agent_name] = asyncio.Queue()

        try:
            message = await asyncio.wait_for(self._message_queues[agent_name].get(), timeout=1.0)
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive broadcast message for {agent_name}: {e}")
            return None

    async def handle_response(self, message: CommunicationMessage, response: Any) -> None:
        """Handle a response to a broadcast message."""
        message.responses.append(
            {
                "recipient": message.recipients[0],
                "timestamp": datetime.now(),
                "response": response,
                "status": "completed",
            }
        )


class PipelineCommunicationProtocol(CommunicationProtocol):
    """Sequential pipeline communication protocol."""

    def __init__(self, agents: Dict[str, BaseReasoningAgent]):
        self._agents = agents
        self._pipeline_stages: Dict[str, List[str]] = {}
        self._stage_queues: Dict[str, asyncio.Queue] = {}

    async def send_message(self, message: CommunicationMessage) -> bool:
        """Send a message through the pipeline."""
        try:
            pipeline_id = message.metadata.get("pipeline_id", str(uuid.uuid4()))
            stages = message.recipients

            # Initialize pipeline stages
            self._pipeline_stages[pipeline_id] = stages

            # Send to first stage
            if stages:
                first_stage = stages[0]
                if first_stage not in self._stage_queues:
                    self._stage_queues[first_stage] = asyncio.Queue()

                pipeline_message = CommunicationMessage(
                    message_id=f"{message.message_id}_stage_0",
                    pattern=CommunicationPattern.PIPELINE,
                    priority=message.priority,
                    sender=message.sender,
                    recipients=[first_stage],
                    payload=message.payload,
                    timestamp=message.timestamp,
                    correlation_id=pipeline_id,
                    metadata={
                        **message.metadata,
                        "pipeline_id": pipeline_id,
                        "stage_index": 0,
                        "total_stages": len(stages),
                        "all_stages": stages,
                    },
                )

                await self._stage_queues[first_stage].put(pipeline_message)
                logger.info(f"Started pipeline {pipeline_id} with {len(stages)} stages")

            return True

        except Exception as e:
            logger.error(f"Failed to send pipeline message: {e}")
            return False

    async def receive_message(self, agent_name: str) -> Optional[CommunicationMessage]:
        """Receive a pipeline message for a specific agent."""
        if agent_name not in self._stage_queues:
            self._stage_queues[agent_name] = asyncio.Queue()

        try:
            message = await asyncio.wait_for(self._stage_queues[agent_name].get(), timeout=1.0)
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive pipeline message for {agent_name}: {e}")
            return None

    async def handle_response(self, message: CommunicationMessage, response: Any) -> None:
        """Handle a response in the pipeline and forward to next stage."""
        try:
            pipeline_id = message.metadata.get("pipeline_id")
            stage_index = message.metadata.get("stage_index", 0)
            all_stages = message.metadata.get("all_stages", [])

            # Record response
            message.responses.append(
                {
                    "stage": message.recipients[0],
                    "timestamp": datetime.now(),
                    "response": response,
                    "status": "completed",
                }
            )

            # Forward to next stage if exists
            next_stage_index = stage_index + 1
            if next_stage_index < len(all_stages):
                next_stage = all_stages[next_stage_index]

                if next_stage not in self._stage_queues:
                    self._stage_queues[next_stage] = asyncio.Queue()

                next_message = CommunicationMessage(
                    message_id=f"{message.message_id}_stage_{next_stage_index}",
                    pattern=CommunicationPattern.PIPELINE,
                    priority=message.priority,
                    sender=message.sender,
                    recipients=[next_stage],
                    payload={"input": response, "previous_results": message.responses},
                    timestamp=datetime.now(),
                    correlation_id=pipeline_id,
                    metadata={
                        **message.metadata,
                        "stage_index": next_stage_index,
                    },
                )

                await self._stage_queues[next_stage].put(next_message)
                logger.debug(f"Forwarded pipeline message to stage {next_stage_index}")
            else:
                logger.info(f"Pipeline {pipeline_id} completed")

        except Exception as e:
            logger.error(f"Failed to handle pipeline response: {e}")


class ScatterGatherCommunicationProtocol(CommunicationProtocol):
    """Scatter-gather parallel processing protocol."""

    def __init__(self, agents: Dict[str, BaseReasoningAgent]):
        self._agents = agents
        self._scatter_sessions: Dict[str, Dict[str, Any]] = {}
        self._message_queues: Dict[str, asyncio.Queue] = {}

    async def send_message(self, message: CommunicationMessage) -> bool:
        """Scatter message to all recipients for parallel processing."""
        try:
            scatter_id = str(uuid.uuid4())

            # Initialize scatter session
            self._scatter_sessions[scatter_id] = {
                "total_recipients": len(message.recipients),
                "responses": {},
                "start_time": datetime.now(),
                "timeout": message.timeout_seconds,
            }

            # Send to all recipients
            for i, recipient in enumerate(message.recipients):
                if recipient in self._agents:
                    if recipient not in self._message_queues:
                        self._message_queues[recipient] = asyncio.Queue()

                    scatter_message = CommunicationMessage(
                        message_id=f"{message.message_id}_scatter_{i}",
                        pattern=CommunicationPattern.SCATTER_GATHER,
                        priority=message.priority,
                        sender=message.sender,
                        recipients=[recipient],
                        payload=message.payload,
                        timestamp=message.timestamp,
                        correlation_id=scatter_id,
                        requires_response=True,
                        metadata={
                            **message.metadata,
                            "scatter_id": scatter_id,
                            "part_index": i,
                            "total_parts": len(message.recipients),
                        },
                    )

                    await self._message_queues[recipient].put(scatter_message)

            logger.info(f"Scattered message {message.message_id} to {len(message.recipients)} agents")
            return True

        except Exception as e:
            logger.error(f"Failed to scatter message: {e}")
            return False

    async def receive_message(self, agent_name: str) -> Optional[CommunicationMessage]:
        """Receive a scattered message for a specific agent."""
        if agent_name not in self._message_queues:
            self._message_queues[agent_name] = asyncio.Queue()

        try:
            message = await asyncio.wait_for(self._message_queues[agent_name].get(), timeout=1.0)
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive scattered message for {agent_name}: {e}")
            return None

    async def handle_response(self, message: CommunicationMessage, response: Any) -> None:
        """Handle a response and gather results when all responses received."""
        try:
            scatter_id = message.metadata.get("scatter_id")
            if not scatter_id or scatter_id not in self._scatter_sessions:
                return

            session = self._scatter_sessions[scatter_id]
            recipient = message.recipients[0]

            # Store response
            session["responses"][recipient] = {"timestamp": datetime.now(), "response": response, "status": "completed"}

            # Check if all responses received
            if len(session["responses"]) == session["total_recipients"]:
                # All responses gathered - process results
                gathered_results = []
                for resp_data in session["responses"].values():
                    gathered_results.append(resp_data["response"])

                # Store final results
                message.responses = gathered_results
                message.status = MessageStatus.COMPLETED

                # Cleanup session
                del self._scatter_sessions[scatter_id]

                logger.info(f"Gathered {len(gathered_results)} responses for scatter {scatter_id}")

        except Exception as e:
            logger.error(f"Failed to handle scatter-gather response: {e}")


class EnhancedCommunicationManager:
    """
    Enhanced communication manager with multiple protocol support
    and advanced message routing capabilities.
    """

    def __init__(self, agents: Dict[str, BaseReasoningAgent]):
        self._agents = agents
        self._protocols: Dict[CommunicationPattern, CommunicationProtocol] = {}
        self._channels: Dict[str, CommunicationChannel] = {}
        self._message_history: List[CommunicationMessage] = []
        self._active_messages: Dict[str, CommunicationMessage] = {}

        # Message routing
        self._message_router = MessageRouter()
        self._message_queue = asyncio.PriorityQueue()

        # Background tasks
        self._message_processor_task: Optional[asyncio.Task] = None
        self._timeout_monitor_task: Optional[asyncio.Task] = None

        # Performance metrics
        self._stats = {
            "messages_sent": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            "average_processing_time": 0.0,
            "protocol_usage": {},
        }

        # Initialize protocols
        self._initialize_protocols()

    def _initialize_protocols(self) -> None:
        """Initialize communication protocols."""
        self._protocols[CommunicationPattern.DIRECT] = DirectCommunicationProtocol(self._agents)
        self._protocols[CommunicationPattern.BROADCAST] = BroadcastCommunicationProtocol(self._agents)
        self._protocols[CommunicationPattern.PIPELINE] = PipelineCommunicationProtocol(self._agents)
        self._protocols[CommunicationPattern.SCATTER_GATHER] = ScatterGatherCommunicationProtocol(self._agents)

    async def initialize(self) -> None:
        """Initialize the communication manager."""
        logger.info("Initializing enhanced communication manager")

        # Start background tasks
        self._message_processor_task = asyncio.create_task(self._process_messages())
        self._timeout_monitor_task = asyncio.create_task(self._monitor_timeouts())

        logger.info("Enhanced communication manager initialized")

    async def shutdown(self) -> None:
        """Shutdown the communication manager."""
        logger.info("Shutting down enhanced communication manager")

        # Cancel background tasks
        if self._message_processor_task:
            self._message_processor_task.cancel()
        if self._timeout_monitor_task:
            self._timeout_monitor_task.cancel()

        # Wait for tasks to complete
        tasks = [self._message_processor_task, self._timeout_monitor_task]
        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)

        logger.info("Enhanced communication manager shutdown complete")

    async def send_message(
        self,
        pattern: CommunicationPattern,
        sender: str,
        recipients: List[str],
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        **kwargs,
    ) -> str:
        """Send a message using the specified communication pattern.

        Args:
            pattern: Communication pattern to use
            sender: Sender agent name
            recipients: List of recipient agent names
            payload: Message payload
            priority: Message priority
            **kwargs: Additional message parameters

        Returns:
            Message ID
        """
        message = CommunicationMessage(
            message_id=str(uuid.uuid4()),
            pattern=pattern,
            priority=priority,
            sender=sender,
            recipients=recipients,
            payload=payload,
            timestamp=datetime.now(),
            **kwargs,
        )

        # Add to active messages
        self._active_messages[message.message_id] = message

        # Queue for processing
        await self._message_queue.put((priority.value, message))

        self._stats["messages_sent"] += 1
        self._stats["protocol_usage"][pattern.value] = self._stats["protocol_usage"].get(pattern.value, 0) + 1

        logger.info(
            f"Queued {pattern.value} message {message.message_id} from {sender} to {len(recipients)} recipients"
        )
        return message.message_id

    async def create_channel(
        self, channel_type: str, participants: List[str], properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a communication channel.

        Args:
            channel_type: Type of channel
            participants: Participating agent names
            properties: Channel properties

        Returns:
            Channel ID
        """
        channel_id = str(uuid.uuid4())

        channel = CommunicationChannel(
            channel_id=channel_id,
            participants=set(participants),
            channel_type=channel_type,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            properties=properties or {},
        )

        self._channels[channel_id] = channel

        logger.info(f"Created {channel_type} channel {channel_id} with {len(participants)} participants")
        return channel_id

    async def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a message.

        Args:
            message_id: Message ID

        Returns:
            Message status information
        """
        if message_id in self._active_messages:
            message = self._active_messages[message_id]
            return {
                "message_id": message_id,
                "status": message.status.value,
                "sender": message.sender,
                "recipients": message.recipients,
                "timestamp": message.timestamp,
                "responses_received": len(message.responses),
                "pattern": message.pattern.value,
            }

        # Check message history
        for msg in self._message_history:
            if msg.message_id == message_id:
                return {
                    "message_id": message_id,
                    "status": msg.status.value,
                    "sender": msg.sender,
                    "recipients": msg.recipients,
                    "timestamp": msg.timestamp,
                    "responses_received": len(msg.responses),
                    "pattern": msg.pattern.value,
                }

        return None

    async def get_communication_statistics(self) -> Dict[str, Any]:
        """Get communication statistics.

        Returns:
            Communication statistics
        """
        stats = self._stats.copy()
        stats.update(
            {
                "active_messages": len(self._active_messages),
                "active_channels": len(self._channels),
                "message_history_size": len(self._message_history),
                "available_protocols": list(self._protocols.keys()),
            }
        )

        return stats

    # Private methods

    async def _process_messages(self) -> None:
        """Background task to process messages."""
        while True:
            try:
                # Get message from queue
                priority, message = await self._message_queue.get()

                # Process message with appropriate protocol
                await self._route_and_process_message(message)

                self._stats["messages_processed"] += 1

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                await asyncio.sleep(1)

    async def _route_and_process_message(self, message: CommunicationMessage) -> None:
        """Route and process a message.

        Args:
            message: Message to process
        """
        try:
            # Get protocol for message pattern
            protocol = self._protocols.get(message.pattern)
            if not protocol:
                logger.error(f"No protocol found for pattern {message.pattern.value}")
                message.status = MessageStatus.FAILED
                return

            # Update message status
            message.status = MessageStatus.PROCESSING

            # Send message through protocol
            success = await protocol.send_message(message)

            if success:
                # For patterns that don't require responses, mark as completed
                if message.pattern in [CommunicationPattern.BROADCAST, CommunicationPattern.DIRECT]:
                    if not message.requires_response:
                        message.status = MessageStatus.COMPLETED
                        await self._complete_message(message)
            else:
                message.status = MessageStatus.FAILED
                await self._complete_message(message)

        except Exception as e:
            logger.error(f"Failed to route message {message.message_id}: {e}")
            message.status = MessageStatus.FAILED
            await self._complete_message(message)

    async def _monitor_timeouts(self) -> None:
        """Background task to monitor message timeouts."""
        while True:
            try:
                current_time = datetime.now()
                timed_out_messages = []

                for message_id, message in self._active_messages.items():
                    if message.status == MessageStatus.PROCESSING:
                        elapsed = (current_time - message.timestamp).total_seconds()
                        if elapsed > message.timeout_seconds:
                            timed_out_messages.append(message)

                # Handle timed out messages
                for message in timed_out_messages:
                    message.status = MessageStatus.TIMEOUT
                    await self._complete_message(message)
                    logger.warning(f"Message {message.message_id} timed out")

                await asyncio.sleep(5)  # Check every 5 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Timeout monitor error: {e}")
                await asyncio.sleep(10)

    async def _complete_message(self, message: CommunicationMessage) -> None:
        """Complete a message and move it to history.

        Args:
            message: Message to complete
        """
        # Move to history
        self._message_history.append(message)

        # Remove from active messages
        if message.message_id in self._active_messages:
            del self._active_messages[message.message_id]

        # Trim history if needed
        if len(self._message_history) > 1000:
            self._message_history = self._message_history[-1000:]

        logger.debug(f"Completed message {message.message_id} with status {message.status.value}")


class MessageRouter:
    """Advanced message routing logic."""

    def __init__(self):
        self._routing_rules: List[Callable] = []
        self._default_routes: Dict[str, List[str]] = {}

    def add_routing_rule(self, rule: Callable) -> None:
        """Add a custom routing rule.

        Args:
            rule: Function that takes a message and returns routing info
        """
        self._routing_rules.append(rule)

    def set_default_route(self, sender: str, recipients: List[str]) -> None:
        """Set default recipients for a sender.

        Args:
            sender: Sender agent name
            recipients: Default recipient list
        """
        self._default_routes[sender] = recipients

    async def route_message(self, message: CommunicationMessage) -> List[str]:
        """Route a message and return final recipient list.

        Args:
            message: Message to route

        Returns:
            Final recipient list
        """
        # Apply custom routing rules
        for rule in self._routing_rules:
            try:
                result = await rule(message) if asyncio.iscoroutinefunction(rule) else rule(message)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Routing rule error: {e}")

        # Use default routes if no custom rules apply
        if message.sender in self._default_routes and not message.recipients:
            return self._default_routes[message.sender]

        # Return original recipients
        return message.recipients
