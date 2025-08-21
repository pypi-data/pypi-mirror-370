"""
Monitoring and Observability Module

This module provides comprehensive monitoring and observability capabilities
for the Thinking Exploration Framework, including:

- OpenTelemetry integration for distributed tracing
- Custom metrics collection and visualization
- Performance monitoring and alerting
- Health checks and system diagnostics
- Real-time observability dashboards

Components:
- metrics.py: Custom metrics collection and aggregation
- tracing.py: Distributed tracing with OpenTelemetry
- health.py: Health checks and system status
- dashboards.py: Performance visualization and dashboards
- alerts.py: Monitoring alerts and notifications

Usage:
    from reasoning_kernel.monitoring import ThinkingMetrics, TracingManager

    metrics = ThinkingMetrics()
    metrics.increment_counter("thinking.explorations.total")

    tracer = TracingManager()
    with tracer.span("thinking_exploration") as span:
        # Your thinking exploration code here
        pass
"""

from .dashboards import MetricsDashboard
from .dashboards import PerformanceDashboard
from .health import HealthChecker
from .health import SystemHealth
from .metrics import MetricType
from .metrics import ThinkingMetrics
from .tracing import create_tracer
from .tracing import TracingManager


__all__ = [
    "ThinkingMetrics",
    "MetricType",
    "TracingManager",
    "create_tracer",
    "HealthChecker",
    "SystemHealth",
    "MetricsDashboard",
    "PerformanceDashboard",
]
