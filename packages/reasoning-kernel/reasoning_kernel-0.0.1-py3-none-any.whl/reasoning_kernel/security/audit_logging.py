"""
Audit Logging System for MSA Reasoning Kernel

Provides comprehensive audit logging for:
- API requests and responses
- Authentication events
- Authorization failures
- System events
- Security incidents
- Performance metrics
"""

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from enum import Enum
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid

from fastapi import Request
from fastapi import Response
from reasoning_kernel.core.logging_config import get_logger
import redis.asyncio as redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware


logger = get_logger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""

    # Authentication events
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"

    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHECK = "permission_check"

    # API events
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    API_ERROR = "api_error"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    RATE_LIMIT_WARNING = "rate_limit_warning"

    # Security events
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_BLOCKED = "ip_blocked"

    # System events
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIG_CHANGE = "config_change"

    # Circuit breaker events
    CIRCUIT_OPENED = "circuit_opened"
    CIRCUIT_CLOSED = "circuit_closed"
    CIRCUIT_HALF_OPEN = "circuit_half_open"

    # Performance events
    SLOW_REQUEST = "slow_request"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    HIGH_CPU_USAGE = "high_cpu_usage"


class AuditSeverity(Enum):
    """Severity levels for audit events"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""

    # Basic identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AuditEventType = AuditEventType.API_REQUEST
    severity: AuditSeverity = AuditSeverity.LOW
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Request context
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Event details
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    # API context (if applicable)
    http_method: Optional[str] = None
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None

    # Security context
    threat_level: Optional[str] = None
    security_tags: List[str] = field(default_factory=list)

    # Performance context
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None

    # Additional metadata
    source_service: str = "reasoning_kernel"
    environment: str = "production"
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)

        # Convert enums to strings
        result["event_type"] = self.event_type.value
        result["severity"] = self.severity.value
        result["timestamp"] = self.timestamp.isoformat()

        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


class AuditLogger:
    """Centralized audit logging system"""

    def __init__(
        self,
        redis_url: Optional[str] = "redis://localhost:6379/2",
        file_path: Optional[str] = None,
        max_file_size_mb: int = 100,
        max_files: int = 10,
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None

        # File logging setup
        self.file_path = Path(file_path) if file_path else None
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.max_files = max_files

        # In-memory buffer for when external systems are unavailable
        self.memory_buffer: List[AuditEvent] = []
        self.max_buffer_size = 10000

        # Event statistics
        self.event_counts: Dict[str, int] = {}
        self.last_flush_time = time.time()

    async def initialize(self):
        """Initialize audit logger"""

        # Initialize Redis connection
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("Audit logger initialized with Redis backend")
            except Exception as e:
                logger.warning(f"Redis initialization failed for audit logger: {e}")
                self.redis_client = None

        # Ensure log directory exists
        if self.file_path:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Log system startup
        await self.log_event(
            AuditEvent(
                event_type=AuditEventType.SYSTEM_START,
                severity=AuditSeverity.MEDIUM,
                message="Audit logging system initialized",
                details={
                    "redis_enabled": self.redis_client is not None,
                    "file_logging_enabled": self.file_path is not None,
                    "buffer_size": self.max_buffer_size,
                },
            )
        )

    async def log_event(self, event: AuditEvent):
        """Log an audit event"""

        try:
            # Update statistics
            event_type_str = event.event_type.value
            self.event_counts[event_type_str] = self.event_counts.get(event_type_str, 0) + 1

            # Try Redis first
            if self.redis_client:
                await self._log_to_redis(event)

            # Log to file
            if self.file_path:
                await self._log_to_file(event)

            # Add to memory buffer as backup
            self._add_to_buffer(event)

            # Log to standard logger for critical events
            if event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                logger.warning(f"AUDIT: {event.event_type.value} - {event.message}")

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Ensure we don't lose the event
            self._add_to_buffer(event)

    async def log_api_request(
        self,
        request: Request,
        response: Response,
        response_time_ms: float,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
    ):
        """Log API request/response"""

        event = AuditEvent(
            event_type=AuditEventType.API_REQUEST,
            severity=AuditSeverity.LOW,
            request_id=getattr(request.state, "request_id", None),
            user_id=user_id,
            api_key_id=api_key_id,
            client_ip=self._get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            message=f"{request.method} {request.url.path}",
            http_method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            request_size_bytes=int(request.headers.get("Content-Length", 0)),
            details={
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "path_params": getattr(request, "path_params", {}),
            },
        )

        # Adjust severity based on status code and response time
        if response.status_code >= 500:
            event.severity = AuditSeverity.HIGH
        elif response.status_code >= 400:
            event.severity = AuditSeverity.MEDIUM
        elif response_time_ms > 5000:  # Slow request
            event.severity = AuditSeverity.MEDIUM
            event.event_type = AuditEventType.SLOW_REQUEST

        await self.log_event(event)

    async def log_auth_event(
        self,
        event_type: AuditEventType,
        success: bool,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log authentication event"""

        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        message = f"Authentication {'successful' if success else 'failed'}"

        if not success:
            severity = AuditSeverity.HIGH
            message += f" from IP {client_ip}"

        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            api_key_id=api_key_id,
            client_ip=client_ip,
            message=message,
            details=details or {},
        )

        await self.log_event(event)

    async def log_security_event(
        self,
        event_type: AuditEventType,
        message: str,
        client_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        threat_level: str = "medium",
        security_tags: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log security event"""

        event = AuditEvent(
            event_type=event_type,
            severity=AuditSeverity.HIGH,
            user_id=user_id,
            client_ip=client_ip,
            message=message,
            threat_level=threat_level,
            security_tags=security_tags or [],
            details=details or {},
        )

        await self.log_event(event)

    async def log_performance_event(
        self,
        event_type: AuditEventType,
        message: str,
        cpu_usage: Optional[float] = None,
        memory_usage_mb: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log performance event"""

        event = AuditEvent(
            event_type=event_type,
            severity=AuditSeverity.MEDIUM,
            message=message,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            details=details or {},
        )

        await self.log_event(event)

    async def search_events(
        self,
        event_types: Optional[List[AuditEventType]] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Search audit events with filters"""

        # This is a simplified implementation
        # In production, you'd want proper indexing and querying
        results = []

        # Search in Redis if available
        if self.redis_client:
            results.extend(
                await self._search_redis(event_types, severity, user_id, client_ip, start_time, end_time, limit)
            )

        # Search in memory buffer
        results.extend(self._search_buffer(event_types, severity, user_id, client_ip, start_time, end_time, limit))

        # Sort by timestamp and limit
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    async def get_statistics(self) -> Dict[str, Any]:
        """Get audit logging statistics"""

        return {
            "total_events": sum(self.event_counts.values()),
            "events_by_type": self.event_counts.copy(),
            "buffer_size": len(self.memory_buffer),
            "redis_available": self.redis_client is not None,
            "file_logging_enabled": self.file_path is not None,
            "last_flush_time": self.last_flush_time,
        }

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def _log_to_redis(self, event: AuditEvent):
        """Log event to Redis"""
        try:
            # Store event with timestamp-based key for ordering
            timestamp_key = int(event.timestamp.timestamp() * 1000000)  # microsecond precision
            redis_key = f"audit:{timestamp_key}:{event.event_id}"

            await self.redis_client.set(redis_key, event.to_json(), ex=86400 * 30)  # Keep for 30 days

            # Add to sorted set for efficient querying
            await self.redis_client.zadd("audit:timeline", {redis_key: timestamp_key})

            # Maintain indices for common queries
            await self._update_redis_indices(event, redis_key)

        except RedisError as e:
            logger.error(f"Failed to log to Redis: {e}")

    async def _update_redis_indices(self, event: AuditEvent, redis_key: str):
        """Update Redis indices for efficient searching"""
        timestamp = int(event.timestamp.timestamp())

        # Index by event type
        await self.redis_client.sadd(f"audit:type:{event.event_type.value}", redis_key)

        # Index by user
        if event.user_id:
            await self.redis_client.sadd(f"audit:user:{event.user_id}", redis_key)

        # Index by IP
        if event.client_ip:
            await self.redis_client.sadd(f"audit:ip:{event.client_ip}", redis_key)

        # Index by severity
        await self.redis_client.sadd(f"audit:severity:{event.severity.value}", redis_key)

    async def _log_to_file(self, event: AuditEvent):
        """Log event to file"""
        try:
            # Rotate log file if needed
            if self.file_path.exists() and self.file_path.stat().st_size > self.max_file_size_bytes:
                await self._rotate_log_file()

            # Append event to file
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(event.to_json() + "\n")

        except Exception as e:
            logger.error(f"Failed to log to file: {e}")

    async def _rotate_log_file(self):
        """Rotate log file when it gets too large"""
        if not self.file_path.exists():
            return

        # Move existing files
        for i in range(self.max_files - 1, 0, -1):
            old_file = self.file_path.with_suffix(f".{i}")
            new_file = self.file_path.with_suffix(f".{i + 1}")

            if old_file.exists():
                if new_file.exists():
                    new_file.unlink()
                old_file.rename(new_file)

        # Move current file to .1
        backup_file = self.file_path.with_suffix(".1")
        if backup_file.exists():
            backup_file.unlink()
        self.file_path.rename(backup_file)

    def _add_to_buffer(self, event: AuditEvent):
        """Add event to memory buffer"""
        self.memory_buffer.append(event)

        # Keep buffer size manageable
        if len(self.memory_buffer) > self.max_buffer_size:
            self.memory_buffer.pop(0)  # Remove oldest

    async def _search_redis(
        self,
        event_types: Optional[List[AuditEventType]] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Search events in Redis"""
        # Simplified implementation - would need proper query optimization
        return []

    def _search_buffer(
        self,
        event_types: Optional[List[AuditEventType]] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Search events in memory buffer"""
        results = []

        for event in self.memory_buffer:
            # Apply filters
            if event_types and event.event_type not in event_types:
                continue
            if severity and event.severity != severity:
                continue
            if user_id and event.user_id != user_id:
                continue
            if client_ip and event.client_ip != client_ip:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue

            results.append(event)

            if len(results) >= limit:
                break

        return results


class AuditMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for audit logging"""

    def __init__(self, app, audit_logger: AuditLogger):
        super().__init__(app)
        self.audit_logger = audit_logger

    async def dispatch(self, request: Request, call_next):
        """Process request with audit logging"""

        start_time = time.time()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response_time_ms = (time.time() - start_time) * 1000

            # Extract user context
            user_id = getattr(request.state, "user_id", None)
            api_key_metadata = getattr(request.state, "api_key_metadata", None)
            api_key_id = api_key_metadata.key_id if api_key_metadata else None

            # Log the request
            await self.audit_logger.log_api_request(
                request=request,
                response=response,
                response_time_ms=response_time_ms,
                user_id=user_id,
                api_key_id=api_key_id,
            )

            return response

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000

            # Log the error
            await self.audit_logger.log_event(
                AuditEvent(
                    event_type=AuditEventType.API_ERROR,
                    severity=AuditSeverity.HIGH,
                    request_id=request_id,
                    client_ip=self.audit_logger._get_client_ip(request),
                    message=f"API error: {str(e)}",
                    http_method=request.method,
                    endpoint=request.url.path,
                    response_time_ms=response_time_ms,
                    details={"error": str(e), "type": type(e).__name__},
                )
            )

            raise


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions
async def log_auth_success(user_id: str, api_key_id: str = None, client_ip: str = None):
    """Log successful authentication"""
    await audit_logger.log_auth_event(
        AuditEventType.AUTH_SUCCESS, success=True, user_id=user_id, api_key_id=api_key_id, client_ip=client_ip
    )


async def log_auth_failure(reason: str, client_ip: str = None, details: Dict[str, Any] = None):
    """Log authentication failure"""
    await audit_logger.log_auth_event(
        AuditEventType.AUTH_FAILURE, success=False, client_ip=client_ip, details={"reason": reason, **(details or {})}
    )


async def log_access_denied(endpoint: str, user_id: str = None, reason: str = None):
    """Log access denial"""
    await audit_logger.log_security_event(
        AuditEventType.ACCESS_DENIED,
        message=f"Access denied to {endpoint}",
        user_id=user_id,
        details={"endpoint": endpoint, "reason": reason},
    )


async def log_suspicious_activity(description: str, client_ip: str = None, details: Dict[str, Any] = None):
    """Log suspicious activity"""
    await audit_logger.log_security_event(
        AuditEventType.SUSPICIOUS_ACTIVITY,
        message=description,
        client_ip=client_ip,
        threat_level="high",
        security_tags=["suspicious", "investigation_required"],
        details=details,
    )
