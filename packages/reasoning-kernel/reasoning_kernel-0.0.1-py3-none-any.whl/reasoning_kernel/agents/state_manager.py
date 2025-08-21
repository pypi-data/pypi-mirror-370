"""
Agent State Management System

Enhanced state tracking, persistence, and recovery for agent orchestration.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import json
import os

from reasoning_kernel.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class StateChangeType(Enum):
    """Types of state changes."""

    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    AGENT_STATE_CHANGED = "agent_state_changed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    METRIC_UPDATED = "metric_updated"


@dataclass
class StateChange:
    """Represents a state change event."""

    change_type: StateChangeType
    timestamp: datetime
    entity_id: str  # agent name or task id
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateSnapshot:
    """Complete state snapshot for recovery."""

    timestamp: datetime
    agents: Dict[str, Dict[str, Any]]
    tasks: Dict[str, Dict[str, Any]]
    metrics: Dict[str, Dict[str, Any]]
    system_config: Dict[str, Any]
    change_history: List[StateChange] = field(default_factory=list)


class StateManager:
    """
    Advanced state management system for agent orchestration.

    Features:
    - State change tracking and history
    - Automatic snapshots and recovery
    - State validation and corruption detection
    - Performance-optimized state operations
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        snapshot_interval: int = 300,  # 5 minutes
        max_history_size: int = 1000,
        enable_compression: bool = True,
    ):
        """Initialize state manager.

        Args:
            storage_path: Directory for state persistence
            snapshot_interval: Seconds between automatic snapshots
            max_history_size: Maximum number of state changes to keep
            enable_compression: Enable state compression for storage
        """
        self._storage_path = storage_path or "./orchestrator_state"
        self._snapshot_interval = snapshot_interval
        self._max_history_size = max_history_size
        self._enable_compression = enable_compression

        # State tracking
        self._current_state: Optional[StateSnapshot] = None
        self._change_history: List[StateChange] = []
        self._state_listeners: List[callable] = []

        # Background tasks
        self._snapshot_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        # Performance metrics
        self._state_operations = 0
        self._last_snapshot_time: Optional[datetime] = None

        # Ensure storage directory exists
        os.makedirs(self._storage_path, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize the state manager."""
        logger.info("Initializing state manager")

        # Try to load existing state
        await self._load_latest_snapshot()

        # Start background tasks
        self._snapshot_task = asyncio.create_task(self._periodic_snapshots())
        self._cleanup_task = asyncio.create_task(self._cleanup_old_states())

        logger.info(f"State manager initialized with storage at {self._storage_path}")

    async def shutdown(self) -> None:
        """Shutdown the state manager."""
        logger.info("Shutting down state manager")

        # Cancel background tasks
        if self._snapshot_task:
            self._snapshot_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Final snapshot
        await self._create_snapshot()

        logger.info("State manager shutdown complete")

    async def record_state_change(
        self,
        change_type: StateChangeType,
        entity_id: str,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **metadata,
    ) -> None:
        """Record a state change.

        Args:
            change_type: Type of state change
            entity_id: ID of the entity that changed
            old_value: Previous value
            new_value: New value
            **metadata: Additional metadata
        """
        change = StateChange(
            change_type=change_type,
            timestamp=datetime.now(),
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            metadata=metadata,
        )

        self._change_history.append(change)
        self._state_operations += 1

        # Trim history if needed
        if len(self._change_history) > self._max_history_size:
            self._change_history = self._change_history[-self._max_history_size :]

        # Notify listeners
        await self._notify_state_listeners(change)

        logger.debug(f"Recorded state change: {change_type.value} for {entity_id}")

    async def create_snapshot(
        self,
        agents: Dict[str, Dict[str, Any]],
        tasks: Dict[str, Dict[str, Any]],
        metrics: Dict[str, Dict[str, Any]],
        system_config: Dict[str, Any],
    ) -> StateSnapshot:
        """Create a state snapshot.

        Args:
            agents: Current agent states
            tasks: Current task states
            metrics: Current metrics
            system_config: System configuration

        Returns:
            Created snapshot
        """
        snapshot = StateSnapshot(
            timestamp=datetime.now(),
            agents=agents.copy(),
            tasks=tasks.copy(),
            metrics=metrics.copy(),
            system_config=system_config.copy(),
            change_history=self._change_history[-100:],  # Last 100 changes
        )

        self._current_state = snapshot
        await self._persist_snapshot(snapshot)

        logger.info(f"Created state snapshot with {len(agents)} agents and {len(tasks)} tasks")
        return snapshot

    async def restore_from_snapshot(self, snapshot_path: Optional[str] = None) -> Optional[StateSnapshot]:
        """Restore state from a snapshot.

        Args:
            snapshot_path: Path to specific snapshot file

        Returns:
            Restored snapshot or None if failed
        """
        try:
            if snapshot_path:
                snapshot = await self._load_snapshot_file(snapshot_path)
            else:
                snapshot = await self._load_latest_snapshot()

            if snapshot:
                self._current_state = snapshot
                self._change_history = snapshot.change_history.copy()

                logger.info(f"Restored state from snapshot: {snapshot.timestamp}")
                return snapshot

        except Exception as e:
            logger.error(f"Failed to restore from snapshot: {e}")

        return None

    async def validate_state_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of current state.

        Returns:
            Validation results
        """
        if not self._current_state:
            return {"valid": False, "error": "No current state"}

        validation_results = {
            "valid": True,
            "timestamp": self._current_state.timestamp,
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # Check agent states
        agent_count = len(self._current_state.agents)
        validation_results["checks"]["agent_count"] = agent_count

        if agent_count == 0:
            validation_results["warnings"].append("No agents in state")

        # Check tasks
        task_count = len(self._current_state.tasks)
        validation_results["checks"]["task_count"] = task_count

        # Check metrics consistency
        metric_count = len(self._current_state.metrics)
        validation_results["checks"]["metric_count"] = metric_count

        if metric_count != agent_count:
            validation_results["warnings"].append(
                f"Metric count ({metric_count}) doesn't match agent count ({agent_count})"
            )

        # Check for orphaned tasks
        orphaned_tasks = []
        for task_id, task_data in self._current_state.tasks.items():
            assigned_agents = task_data.get("agent_assignments", {})
            for agent_name in assigned_agents.values():
                if agent_name not in self._current_state.agents:
                    orphaned_tasks.append(task_id)
                    break

        if orphaned_tasks:
            validation_results["warnings"].append(f"Orphaned tasks: {orphaned_tasks}")
            validation_results["checks"]["orphaned_tasks"] = len(orphaned_tasks)

        # Overall validation
        if validation_results["errors"]:
            validation_results["valid"] = False

        return validation_results

    async def get_state_history(
        self,
        entity_id: Optional[str] = None,
        change_types: Optional[List[StateChangeType]] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[StateChange]:
        """Get filtered state change history.

        Args:
            entity_id: Filter by entity ID
            change_types: Filter by change types
            since: Filter changes since timestamp
            limit: Maximum number of changes to return

        Returns:
            Filtered state changes
        """
        filtered_changes = self._change_history.copy()

        # Apply filters
        if entity_id:
            filtered_changes = [c for c in filtered_changes if c.entity_id == entity_id]

        if change_types:
            filtered_changes = [c for c in filtered_changes if c.change_type in change_types]

        if since:
            filtered_changes = [c for c in filtered_changes if c.timestamp >= since]

        # Sort by timestamp (most recent first)
        filtered_changes.sort(key=lambda x: x.timestamp, reverse=True)

        # Apply limit
        if limit:
            filtered_changes = filtered_changes[:limit]

        return filtered_changes

    async def get_state_statistics(self) -> Dict[str, Any]:
        """Get state management statistics.

        Returns:
            Statistics about state management
        """
        current_time = datetime.now()

        stats = {
            "state_operations": self._state_operations,
            "history_size": len(self._change_history),
            "last_snapshot": self._last_snapshot_time.isoformat() if self._last_snapshot_time else None,
            "storage_path": self._storage_path,
            "compression_enabled": self._enable_compression,
        }

        # Current state info
        if self._current_state:
            stats.update(
                {
                    "current_state_age": (current_time - self._current_state.timestamp).total_seconds(),
                    "agent_count": len(self._current_state.agents),
                    "task_count": len(self._current_state.tasks),
                    "metric_count": len(self._current_state.metrics),
                }
            )

        # Change type distribution
        change_type_counts = {}
        for change in self._change_history:
            change_type = change.change_type.value
            change_type_counts[change_type] = change_type_counts.get(change_type, 0) + 1

        stats["change_type_distribution"] = change_type_counts

        # Recent activity
        recent_threshold = current_time - timedelta(minutes=10)
        recent_changes = [c for c in self._change_history if c.timestamp >= recent_threshold]
        stats["recent_activity"] = len(recent_changes)

        return stats

    def add_state_listener(self, listener: callable) -> None:
        """Add a state change listener.

        Args:
            listener: Function to call on state changes
        """
        self._state_listeners.append(listener)

    def remove_state_listener(self, listener: callable) -> None:
        """Remove a state change listener.

        Args:
            listener: Function to remove
        """
        if listener in self._state_listeners:
            self._state_listeners.remove(listener)

    # Private methods

    async def _periodic_snapshots(self) -> None:
        """Background task for periodic snapshots."""
        while True:
            try:
                await asyncio.sleep(self._snapshot_interval)
                await self._create_snapshot()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic snapshot error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _cleanup_old_states(self) -> None:
        """Background task to cleanup old state files."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_snapshot_files()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"State cleanup error: {e}")
                await asyncio.sleep(300)  # Wait before retrying

    async def _create_snapshot(self) -> None:
        """Create a snapshot if current state exists."""
        if self._current_state:
            await self._persist_snapshot(self._current_state)
            self._last_snapshot_time = datetime.now()

    async def _persist_snapshot(self, snapshot: StateSnapshot) -> None:
        """Persist a snapshot to disk.

        Args:
            snapshot: Snapshot to persist
        """
        try:
            timestamp_str = snapshot.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"state_snapshot_{timestamp_str}.json"
            filepath = os.path.join(self._storage_path, filename)

            # Convert to serializable format
            snapshot_data = {
                "timestamp": snapshot.timestamp.isoformat(),
                "agents": snapshot.agents,
                "tasks": snapshot.tasks,
                "metrics": snapshot.metrics,
                "system_config": snapshot.system_config,
                "change_history": [
                    {
                        "change_type": change.change_type.value,
                        "timestamp": change.timestamp.isoformat(),
                        "entity_id": change.entity_id,
                        "old_value": change.old_value,
                        "new_value": change.new_value,
                        "metadata": change.metadata,
                    }
                    for change in snapshot.change_history
                ],
            }

            # Write to file
            with open(filepath, "w") as f:
                json.dump(snapshot_data, f, indent=2 if not self._enable_compression else None)

            logger.debug(f"Persisted snapshot to {filename}")

        except Exception as e:
            logger.error(f"Failed to persist snapshot: {e}")

    async def _load_snapshot_file(self, filepath: str) -> Optional[StateSnapshot]:
        """Load a snapshot from a file.

        Args:
            filepath: Path to snapshot file

        Returns:
            Loaded snapshot or None if failed
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Convert back to objects
            change_history = []
            for change_data in data.get("change_history", []):
                change = StateChange(
                    change_type=StateChangeType(change_data["change_type"]),
                    timestamp=datetime.fromisoformat(change_data["timestamp"]),
                    entity_id=change_data["entity_id"],
                    old_value=change_data.get("old_value"),
                    new_value=change_data.get("new_value"),
                    metadata=change_data.get("metadata", {}),
                )
                change_history.append(change)

            snapshot = StateSnapshot(
                timestamp=datetime.fromisoformat(data["timestamp"]),
                agents=data["agents"],
                tasks=data["tasks"],
                metrics=data["metrics"],
                system_config=data["system_config"],
                change_history=change_history,
            )

            return snapshot

        except Exception as e:
            logger.error(f"Failed to load snapshot from {filepath}: {e}")
            return None

    async def _load_latest_snapshot(self) -> Optional[StateSnapshot]:
        """Load the most recent snapshot.

        Returns:
            Latest snapshot or None if no snapshots exist
        """
        try:
            snapshot_files = [
                f for f in os.listdir(self._storage_path) if f.startswith("state_snapshot_") and f.endswith(".json")
            ]

            if not snapshot_files:
                logger.info("No existing snapshots found")
                return None

            # Sort by timestamp (newest first)
            snapshot_files.sort(reverse=True)
            latest_file = os.path.join(self._storage_path, snapshot_files[0])

            snapshot = await self._load_snapshot_file(latest_file)
            if snapshot:
                logger.info(f"Loaded latest snapshot from {snapshot_files[0]}")

            return snapshot

        except Exception as e:
            logger.error(f"Failed to load latest snapshot: {e}")
            return None

    async def _cleanup_old_snapshot_files(self) -> None:
        """Clean up old snapshot files."""
        try:
            snapshot_files = [
                f for f in os.listdir(self._storage_path) if f.startswith("state_snapshot_") and f.endswith(".json")
            ]

            if len(snapshot_files) <= 10:  # Keep at least 10 snapshots
                return

            # Sort by timestamp and remove oldest files
            snapshot_files.sort()
            files_to_remove = snapshot_files[:-10]  # Keep newest 10

            for filename in files_to_remove:
                filepath = os.path.join(self._storage_path, filename)
                os.remove(filepath)
                logger.debug(f"Removed old snapshot: {filename}")

            logger.info(f"Cleaned up {len(files_to_remove)} old snapshot files")

        except Exception as e:
            logger.error(f"Failed to cleanup old snapshots: {e}")

    async def _notify_state_listeners(self, change: StateChange) -> None:
        """Notify all state change listeners.

        Args:
            change: State change to notify about
        """
        for listener in self._state_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(change)
                else:
                    listener(change)
            except Exception as e:
                logger.error(f"State listener error: {e}")
