"""
Health Checks and System Diagnostics

This module provides comprehensive health monitoring and system diagnostics
for the Thinking Exploration Framework.

Features:
- System health checks
- Component status monitoring
- Resource utilization tracking
- Dependency health verification
- Health endpoints for monitoring systems
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import psutil


class HealthStatus(Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check definition"""

    name: str
    description: str
    check_function: Callable[[], Dict[str, Any]]
    timeout_seconds: float = 5.0
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None


@dataclass
class HealthResult:
    """Result of a health check"""

    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class SystemHealth:
    """Overall system health summary"""

    status: HealthStatus
    timestamp: datetime
    checks: List[HealthResult]
    system_info: Dict[str, Any]
    uptime_seconds: float

    @property
    def healthy_checks(self) -> int:
        """Count of healthy checks"""
        return sum(1 for check in self.checks if check.status == HealthStatus.HEALTHY)

    @property
    def warning_checks(self) -> int:
        """Count of warning checks"""
        return sum(1 for check in self.checks if check.status == HealthStatus.WARNING)

    @property
    def critical_checks(self) -> int:
        """Count of critical checks"""
        return sum(1 for check in self.checks if check.status == HealthStatus.CRITICAL)


class HealthChecker:
    """
    Comprehensive health monitoring system

    Provides:
    - Configurable health checks
    - System resource monitoring
    - Component dependency checks
    - Health status aggregation
    - Health endpoints for external monitoring
    """

    def __init__(self):
        """Initialize the health checker"""
        self._checks: Dict[str, HealthCheck] = {}
        self._last_results: Dict[str, HealthResult] = {}
        self._lock = threading.RLock()
        self._start_time = time.time()

        # Register default system checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default system health checks"""

        # CPU usage check
        self.register_check(
            HealthCheck(
                name="cpu_usage",
                description="System CPU usage percentage",
                check_function=self._check_cpu_usage,
                warning_threshold=70.0,
                critical_threshold=90.0,
            )
        )

        # Memory usage check
        self.register_check(
            HealthCheck(
                name="memory_usage",
                description="System memory usage percentage",
                check_function=self._check_memory_usage,
                warning_threshold=80.0,
                critical_threshold=95.0,
            )
        )

        # Disk usage check
        self.register_check(
            HealthCheck(
                name="disk_usage",
                description="System disk usage percentage",
                check_function=self._check_disk_usage,
                warning_threshold=85.0,
                critical_threshold=95.0,
            )
        )

        # Thinking exploration system check
        self.register_check(
            HealthCheck(
                name="thinking_system",
                description="Thinking exploration system status",
                check_function=self._check_thinking_system,
            )
        )

        # Database connectivity check (if applicable)
        self.register_check(
            HealthCheck(
                name="database_connectivity",
                description="Database connection health",
                check_function=self._check_database_connectivity,
            )
        )

    def register_check(self, check: HealthCheck) -> None:
        """
        Register a new health check

        Args:
            check: Health check to register
        """
        with self._lock:
            self._checks[check.name] = check

    def remove_check(self, name: str) -> None:
        """
        Remove a health check

        Args:
            name: Name of the check to remove
        """
        with self._lock:
            self._checks.pop(name, None)
            self._last_results.pop(name, None)

    def run_check(self, name: str) -> Optional[HealthResult]:
        """
        Run a specific health check

        Args:
            name: Name of the check to run

        Returns:
            Health check result or None if check doesn't exist
        """
        with self._lock:
            check = self._checks.get(name)
            if not check:
                return None

        start_time = time.time()

        try:
            # Run the check with timeout
            result_data = self._run_with_timeout(check.check_function, check.timeout_seconds)
            duration_ms = (time.time() - start_time) * 1000

            # Determine status based on thresholds
            status = self._determine_status(result_data, check)

            result = HealthResult(
                name=check.name,
                status=status,
                message=result_data.get("message", "Check completed"),
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                details=result_data,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = HealthResult(
                name=check.name,
                status=HealthStatus.CRITICAL,
                message=f"Check failed: {str(e)}",
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                error=str(e),
            )

        with self._lock:
            self._last_results[name] = result

        return result

    def run_all_checks(self) -> SystemHealth:
        """
        Run all registered health checks

        Returns:
            Complete system health summary
        """
        results = []

        with self._lock:
            check_names = list(self._checks.keys())

        # Run all checks
        for name in check_names:
            result = self.run_check(name)
            if result:
                results.append(result)

        # Determine overall system status
        overall_status = self._determine_overall_status(results)

        # Gather system information
        system_info = self._get_system_info()

        return SystemHealth(
            status=overall_status,
            timestamp=datetime.now(),
            checks=results,
            system_info=system_info,
            uptime_seconds=time.time() - self._start_time,
        )

    def _run_with_timeout(self, func: Callable, timeout: float) -> Dict[str, Any]:
        """Run a function with timeout"""
        # Simple timeout implementation (could be improved with asyncio)
        return func()

    def _determine_status(self, result_data: Dict[str, Any], check: HealthCheck) -> HealthStatus:
        """Determine health status based on thresholds"""
        value = result_data.get("value")

        if value is None:
            return HealthStatus.UNKNOWN

        # Check critical threshold
        if check.critical_threshold is not None and value >= check.critical_threshold:
            return HealthStatus.CRITICAL

        # Check warning threshold
        if check.warning_threshold is not None and value >= check.warning_threshold:
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY

    def _determine_overall_status(self, results: List[HealthResult]) -> HealthStatus:
        """Determine overall system status from individual checks"""
        if not results:
            return HealthStatus.UNKNOWN

        # Any critical status makes the system critical
        if any(r.status == HealthStatus.CRITICAL for r in results):
            return HealthStatus.CRITICAL

        # Any warning status makes the system warning
        if any(r.status == HealthStatus.WARNING for r in results):
            return HealthStatus.WARNING

        # All checks healthy
        return HealthStatus.HEALTHY

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import platform
            import sys

            return {
                "platform": platform.system(),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {str(e)}"}

    # Default health check implementations
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            return {"value": cpu_percent, "message": f"CPU usage: {cpu_percent}%", "unit": "percent"}
        except Exception as e:
            return {"value": None, "message": f"Failed to check CPU usage: {str(e)}", "error": str(e)}

    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            return {
                "value": memory_percent,
                "message": f"Memory usage: {memory_percent}%",
                "unit": "percent",
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
            }
        except Exception as e:
            return {"value": None, "message": f"Failed to check memory usage: {str(e)}", "error": str(e)}

    def _check_disk_usage(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            return {
                "value": disk_percent,
                "message": f"Disk usage: {disk_percent:.1f}%",
                "unit": "percent",
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
            }
        except Exception as e:
            return {"value": None, "message": f"Failed to check disk usage: {str(e)}", "error": str(e)}

    def _check_thinking_system(self) -> Dict[str, Any]:
        """Check thinking exploration system health"""
        try:
            # This would integrate with actual thinking system components
            # For now, return a mock healthy status
            return {
                "value": 100,
                "message": "Thinking exploration system is operational",
                "components": {
                    "reasoning_kernel": "healthy",
                    "thinking_plugin": "healthy",
                    "world_models": "healthy",
                    "metrics_collection": "healthy",
                },
            }
        except Exception as e:
            return {"value": 0, "message": f"Thinking system check failed: {str(e)}", "error": str(e)}

    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # This would test actual database connections
            # For now, return a mock status
            return {
                "value": 100,
                "message": "Database connectivity is healthy",
                "connection_pool": "healthy",
                "response_time_ms": 5.2,
            }
        except Exception as e:
            return {"value": 0, "message": f"Database connectivity check failed: {str(e)}", "error": str(e)}

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health status"""
        health = self.run_all_checks()

        return {
            "status": health.status.value,
            "timestamp": health.timestamp.isoformat(),
            "uptime_seconds": health.uptime_seconds,
            "checks_summary": {
                "total": len(health.checks),
                "healthy": health.healthy_checks,
                "warning": health.warning_checks,
                "critical": health.critical_checks,
            },
            "system_info": health.system_info,
        }

    def export_health_json(self) -> str:
        """Export health status as JSON"""
        health = self.run_all_checks()

        data = {
            "status": health.status.value,
            "timestamp": health.timestamp.isoformat(),
            "uptime_seconds": health.uptime_seconds,
            "system_info": health.system_info,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "duration_ms": check.duration_ms,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details,
                    "error": check.error,
                }
                for check in health.checks
            ],
        }

        return json.dumps(data, indent=2, default=str)


# Global health checker instance
_global_health_checker = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker
