"""
Distributed Tracing with OpenTelemetry

This module provides comprehensive distributed tracing capabilities for the
Thinking Exploration Framework using OpenTelemetry standards.

Features:
- Automatic span creation and management
- Context propagation across async operations
- Custom span attributes for thinking operations
- Integration with external tracing systems (Jaeger, Zipkin)
- Performance correlation with metrics
"""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import functools
import threading
import time
from typing import Any, Callable, Dict, Optional
import uuid


# OpenTelemetry imports (mock for now, would be real in production)
class MockSpan:
    """Mock span implementation for development/testing"""

    def __init__(self, name: str, parent: Optional["MockSpan"] = None):
        self.name = name
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = str(uuid.uuid4())[:16]
        self.parent = parent
        self.start_time = time.time()
        self.end_time = None
        self.attributes = {}
        self.events = []
        self.status = "OK"
        self.status_description = ""

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute"""
        self.attributes[key] = str(value)

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span"""
        event = {"name": name, "timestamp": time.time(), "attributes": attributes or {}}
        self.events.append(event)

    def set_status(self, status: str, description: str = "") -> None:
        """Set the span status"""
        self.status = status
        self.status_description = description

    def end(self) -> None:
        """End the span"""
        self.end_time = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.set_status("ERROR", str(exc_val))
        self.end()


@dataclass
class TraceContext:
    """Context information for distributed tracing"""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = None

    def __post_init__(self):
        if self.baggage is None:
            self.baggage = {}


class TracingManager:
    """
    Comprehensive tracing manager for thinking exploration operations

    Provides:
    - Automatic span creation and management
    - Context propagation
    - Performance correlation
    - Custom thinking-specific tracing
    """

    def __init__(self, service_name: str = "thinking-exploration"):
        """
        Initialize the tracing manager

        Args:
            service_name: Name of the service for tracing
        """
        self.service_name = service_name
        self._current_span: Optional[MockSpan] = None
        self._span_stack = []
        self._lock = threading.RLock()

        # Thinking-specific trace data
        self._exploration_traces = {}
        self._active_explorations = {}

    def create_span(self, name: str, parent: Optional[MockSpan] = None) -> MockSpan:
        """
        Create a new span

        Args:
            name: Span name
            parent: Parent span (optional)

        Returns:
            New span instance
        """
        with self._lock:
            if parent is None:
                parent = self._current_span

            span = MockSpan(name, parent)
            span.set_attribute("service.name", self.service_name)
            span.set_attribute("span.kind", "internal")

            return span

    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager for automatic span management

        Args:
            name: Span name
            attributes: Optional span attributes
        """
        span = self.create_span(name)

        # Set attributes
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        with self._lock:
            self._span_stack.append(self._current_span)
            self._current_span = span

        try:
            yield span
        finally:
            with self._lock:
                self._current_span = self._span_stack.pop()
            span.end()

    def start_exploration_trace(self, exploration_id: str, mode: str, context: Dict[str, Any]) -> str:
        """
        Start tracing for a thinking exploration

        Args:
            exploration_id: Unique exploration identifier
            mode: Exploration mode
            context: Exploration context

        Returns:
            Trace ID for the exploration
        """
        with self.span(
            f"thinking_exploration_{mode}",
            {
                "exploration.id": exploration_id,
                "exploration.mode": mode,
                "exploration.context_size": len(str(context)),
                "exploration.timestamp": datetime.now().isoformat(),
            },
        ) as span:

            trace_id = span.trace_id

            with self._lock:
                self._exploration_traces[exploration_id] = {
                    "trace_id": trace_id,
                    "span": span,
                    "mode": mode,
                    "start_time": time.time(),
                    "context": context,
                    "phases": [],
                }
                self._active_explorations[exploration_id] = span

            span.add_event(
                "exploration_started", {"mode": mode, "context_complexity": self._assess_context_complexity(context)}
            )

            return trace_id

    def add_exploration_phase(self, exploration_id: str, phase: str, data: Dict[str, Any]) -> None:
        """
        Add a phase to an exploration trace

        Args:
            exploration_id: Exploration identifier
            phase: Phase name
            data: Phase data
        """
        if exploration_id not in self._exploration_traces:
            return

        with self.span(
            f"exploration_phase_{phase}",
            {"exploration.id": exploration_id, "phase.name": phase, "phase.data_size": len(str(data))},
        ) as span:

            span.add_event(f"phase_{phase}_started")

            # Add phase to exploration trace
            with self._lock:
                phase_data = {"name": phase, "start_time": time.time(), "data": data, "span_id": span.span_id}
                self._exploration_traces[exploration_id]["phases"].append(phase_data)

            span.set_attribute("phase.order", len(self._exploration_traces[exploration_id]["phases"]))

    def add_model_invocation_trace(
        self, exploration_id: str, model_type: str, input_data: Dict[str, Any], duration: float, success: bool
    ) -> None:
        """
        Add model invocation tracing

        Args:
            exploration_id: Exploration identifier
            model_type: Type of model invoked
            input_data: Input data for the model
            duration: Invocation duration
            success: Whether the invocation was successful
        """
        with self.span(
            f"model_invocation_{model_type}",
            {
                "exploration.id": exploration_id,
                "model.type": model_type,
                "model.input_size": len(str(input_data)),
                "model.duration": duration,
                "model.success": success,
            },
        ) as span:

            span.add_event(
                "model_invocation_started",
                {"model_type": model_type, "input_complexity": self._assess_input_complexity(input_data)},
            )

            if success:
                span.add_event("model_invocation_completed")
                span.set_status("OK")
            else:
                span.add_event("model_invocation_failed")
                span.set_status("ERROR", "Model invocation failed")

    def add_trigger_detection_trace(
        self, exploration_id: str, trigger_type: str, confidence: float, context: Dict[str, Any]
    ) -> None:
        """
        Add trigger detection tracing

        Args:
            exploration_id: Exploration identifier
            trigger_type: Type of trigger detected
            confidence: Detection confidence
            context: Detection context
        """
        with self.span(
            f"trigger_detection_{trigger_type}",
            {
                "exploration.id": exploration_id,
                "trigger.type": trigger_type,
                "trigger.confidence": confidence,
                "trigger.context_size": len(str(context)),
            },
        ) as span:

            span.add_event(
                "trigger_detected",
                {
                    "trigger_type": trigger_type,
                    "confidence": confidence,
                    "context_complexity": self._assess_context_complexity(context),
                },
            )

    def end_exploration_trace(
        self, exploration_id: str, success: bool, result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        End an exploration trace

        Args:
            exploration_id: Exploration identifier
            success: Whether the exploration was successful
            result: Optional exploration result
        """
        if exploration_id not in self._exploration_traces:
            return

        with self._lock:
            trace_data = self._exploration_traces[exploration_id]
            span = self._active_explorations.get(exploration_id)

            if span:
                duration = time.time() - trace_data["start_time"]

                span.set_attribute("exploration.duration", duration)
                span.set_attribute("exploration.success", success)
                span.set_attribute("exploration.phases_count", len(trace_data["phases"]))

                if result:
                    span.set_attribute("exploration.result_size", len(str(result)))

                if success:
                    span.add_event(
                        "exploration_completed", {"duration": duration, "phases_count": len(trace_data["phases"])}
                    )
                    span.set_status("OK")
                else:
                    span.add_event("exploration_failed")
                    span.set_status("ERROR", "Exploration failed")

                # Clean up
                del self._active_explorations[exploration_id]

    def get_exploration_trace(self, exploration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace data for an exploration

        Args:
            exploration_id: Exploration identifier

        Returns:
            Trace data if available
        """
        with self._lock:
            return self._exploration_traces.get(exploration_id)

    def get_active_traces(self) -> Dict[str, Dict[str, Any]]:
        """Get all active exploration traces"""
        with self._lock:
            return self._active_explorations.copy()

    def _assess_context_complexity(self, context: Dict[str, Any]) -> str:
        """Assess the complexity of a context"""
        context_str = str(context)
        if len(context_str) < 100:
            return "simple"
        elif len(context_str) < 1000:
            return "medium"
        else:
            return "complex"

    def _assess_input_complexity(self, input_data: Dict[str, Any]) -> str:
        """Assess the complexity of input data"""
        return self._assess_context_complexity(input_data)

    def export_traces(self) -> Dict[str, Any]:
        """
        Export all trace data

        Returns:
            Complete trace export
        """
        with self._lock:
            return {
                "service_name": self.service_name,
                "timestamp": datetime.now().isoformat(),
                "exploration_traces": {
                    exploration_id: {
                        "trace_id": trace_data["trace_id"],
                        "mode": trace_data["mode"],
                        "start_time": trace_data["start_time"],
                        "phases": trace_data["phases"],
                        "duration": (
                            time.time() - trace_data["start_time"]
                            if exploration_id in self._active_explorations
                            else None
                        ),
                    }
                    for exploration_id, trace_data in self._exploration_traces.items()
                },
                "active_explorations": list(self._active_explorations.keys()),
            }


def create_tracer(service_name: str = "thinking-exploration") -> TracingManager:
    """
    Create a new tracing manager instance

    Args:
        service_name: Service name for tracing

    Returns:
        TracingManager instance
    """
    return TracingManager(service_name)


def trace_thinking_operation(operation_name: str):
    """
    Decorator for automatically tracing thinking operations

    Args:
        operation_name: Name of the operation to trace
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = create_tracer()
            with tracer.span(f"thinking_operation_{operation_name}"):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = create_tracer()
            with tracer.span(f"thinking_operation_{operation_name}"):
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global tracer instance
_global_tracer = None


def get_tracer() -> TracingManager:
    """Get the global tracer instance"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = create_tracer()
    return _global_tracer
