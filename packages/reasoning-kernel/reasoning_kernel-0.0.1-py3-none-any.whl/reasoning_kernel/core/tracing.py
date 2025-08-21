"""
OpenTelemetry Tracing Infrastructure for MSA Reasoning Kernel

This module provides comprehensive tracing support for the MSA pipeline stages,
including span tracking, performance profiling, and correlation ID management.
"""

from contextlib import contextmanager
import functools
import os
import time
from typing import Any, Callable, Dict, Optional
import uuid

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter


try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )

    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False
    OTLPSpanExporter = None

try:
    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    LOGGING_INSTRUMENTATION_AVAILABLE = True
except ImportError:
    LOGGING_INSTRUMENTATION_AVAILABLE = False
    LoggingInstrumentor = None
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.core.settings import settings
from reasoning_kernel.core.error_handling import simple_log_error


logger = get_logger(__name__)

# Global tracer instance
_tracer: Optional[trace.Tracer] = None
_initialized = False

# Correlation ID storage (thread-local would be better in production)
_correlation_context: Dict[str, Any] = {}


def get_correlation_id() -> str:
    """Get or generate correlation ID for request tracing"""
    if "correlation_id" not in _correlation_context:
        _correlation_context["correlation_id"] = str(uuid.uuid4())
    return _correlation_context["correlation_id"]


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for request tracing"""
    _correlation_context["correlation_id"] = correlation_id


@contextmanager
def correlation_context(correlation_id: str, **context):
    """Context manager for setting correlation ID and additional context"""
    global _correlation_context
    old_context = _correlation_context.copy()
    _correlation_context.update({"correlation_id": correlation_id, **context})
    try:
        yield
    finally:
        _correlation_context = old_context


def initialize_tracing(
    service_name: str = "reasoning-kernel",
    service_version: str = "0.1.0",
    otlp_endpoint: Optional[str] = None,
    enable_console_export: bool = True,
) -> None:
    """Initialize OpenTelemetry tracing with OTLP and console exporters"""
    global _tracer, _initialized

    if _initialized:
        logger.info("Tracing already initialized")
        return

    try:
        # Create resource with service information
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: service_name,
                ResourceAttributes.SERVICE_VERSION: service_version,
                ResourceAttributes.SERVICE_INSTANCE_ID: str(uuid.uuid4()),
            }
        )

        # Initialize tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # Add console exporter for development
        if enable_console_export:
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            tracer_provider.add_span_processor(console_processor)
            logger.info("Console span exporter initialized")

        # Add OTLP exporter if configured and available
        if otlp_endpoint and OTLP_AVAILABLE and OTLPSpanExporter:
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info(f"OTLP exporter configured for endpoint: {otlp_endpoint}")
            except Exception as e:
                logger.warning(f"Failed to configure OTLP exporter: {e}")
        elif otlp_endpoint:
            logger.warning("OTLP endpoint configured but opentelemetry-exporter-otlp not available")

        # Initialize instrumentations
        if LOGGING_INSTRUMENTATION_AVAILABLE and LoggingInstrumentor:
            try:
                LoggingInstrumentor().instrument()
            except Exception as e:
                logger.warning(f"Failed to instrument logging: {e}")
        else:
            logger.warning("Logging instrumentation not available")

        # Get tracer instance
        _tracer = trace.get_tracer(__name__)
        _initialized = True

        logger.info("OpenTelemetry tracing initialized successfully")

    except Exception as e:
        simple_log_error(logger, "initialize_tracing", e)
        raise


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance"""
    global _tracer
    if _tracer is None:
        # Initialize with defaults if not already done
        initialize_tracing()
    return _tracer  # type: ignore


@contextmanager
def trace_operation(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
):
    """Context manager for tracing operations with automatic error handling"""
    tracer = get_tracer()

    # Merge correlation context with provided attributes
    span_attributes = {"correlation_id": get_correlation_id(), **(attributes or {}), **_correlation_context}

    with tracer.start_as_current_span(operation_name, attributes=span_attributes) as span:
        start_time = time.time()
        span.set_attribute("operation.start_time", start_time)

        # Prepare initial log attributes
        log_attrs = {"operation": operation_name, **span_attributes}
        # Only add correlation_id if not already in span_attributes
        if "correlation_id" not in log_attrs:
            log_attrs["correlation_id"] = get_correlation_id()

        try:
            # Safe logging with fallback
            try:
                logger.info("Operation started", **log_attrs)
            except Exception:
                logger.info(f"Operation started: {operation_name}")
            
            yield span

            # Record success
            duration = time.time() - start_time
            span.set_attribute("operation.duration", duration)
            span.set_attribute("operation.status", "success")

            completion_attrs = {"operation": operation_name, "duration": duration, "status": "success"}
            if "correlation_id" not in span_attributes:
                completion_attrs["correlation_id"] = get_correlation_id()

            try:
                logger.info("Operation completed", **completion_attrs)
            except Exception:
                logger.info(f"Operation completed: {operation_name} in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            span.set_attribute("operation.duration", duration)
            span.set_attribute("operation.status", "error")
            span.set_attribute("operation.error", str(e))

            if record_exception:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            error_attrs = {"operation": operation_name, "duration": duration, "status": "error", "error": str(e)}
            if "correlation_id" not in span_attributes:
                error_attrs["correlation_id"] = get_correlation_id()

            simple_log_error(logger, "trace_operation", e, operation=operation_name)
            raise


def trace_function(
    operation_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
):
    """Decorator for tracing function calls"""

    def decorator(func: Callable) -> Callable:
        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_attributes = {"function.name": func.__name__, "function.module": func.__module__, **(attributes or {})}

            with trace_operation(op_name, func_attributes, record_exception):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_attributes = {"function.name": func.__name__, "function.module": func.__module__, **(attributes or {})}

            with trace_operation(op_name, func_attributes, record_exception):
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class MSAStageTracer:
    """Specialized tracer for MSA pipeline stages"""

    def __init__(self, stage_name: str, stage_type: str):
        self.stage_name = stage_name
        self.stage_type = stage_type
        self.tracer = get_tracer()

    @contextmanager
    def trace_stage_execution(
        self, input_data: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace MSA stage execution with stage-specific attributes"""
        attributes = {
            "msa.stage.name": self.stage_name,
            "msa.stage.type": self.stage_type,
            "correlation_id": get_correlation_id(),
        }

        if input_data:
            attributes["msa.stage.input_size"] = str(len(str(input_data)))
            attributes["msa.stage.input_keys"] = str(list(input_data.keys()))

        if metadata:
            attributes.update({f"msa.stage.meta.{k}": v for k, v in metadata.items()})

        operation_name = f"msa.stage.{self.stage_type}.{self.stage_name}"

        with trace_operation(operation_name, attributes) as span:
            yield MSAStageSpan(span, self.stage_name)


class MSAStageSpan:
    """Wrapper for MSA stage span with convenience methods"""

    def __init__(self, span: trace.Span, stage_name: str):
        self.span = span
        self.stage_name = stage_name

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to the current span"""
        self.span.add_event(name, attributes or {})

    def set_attribute(self, key: str, value: Any):
        """Set attribute on the current span"""
        self.span.set_attribute(key, value)

    def record_output(self, output_data: Dict[str, Any]):
        """Record stage output information"""
        self.set_attribute("msa.stage.output_size", str(len(str(output_data))))
        self.set_attribute("msa.stage.output_keys", str(list(output_data.keys())))

        # Record specific metrics based on output
        if "confidence" in output_data:
            self.set_attribute("msa.stage.confidence", str(output_data["confidence"]))
        if "reasoning_steps" in output_data:
            self.set_attribute("msa.stage.reasoning_steps_count", str(len(output_data["reasoning_steps"])))


def trace_msa_stage(stage_name: str, stage_type: str):
    """Decorator for MSA stage methods"""

    def decorator(func: Callable) -> Callable:
        tracer = MSAStageTracer(stage_name, stage_type)

        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            input_data = kwargs.get("input_data") or (args[0] if args else None)
            metadata = kwargs.get("metadata", {})

            with tracer.trace_stage_execution(input_data, metadata) as stage_span:
                stage_span.add_event("stage_execution_started")

                try:
                    result = await func(self, *args, **kwargs)

                    if isinstance(result, dict):
                        stage_span.record_output(result)

                    stage_span.add_event("stage_execution_completed")
                    return result

                except Exception as e:
                    stage_span.add_event("stage_execution_failed", {"error": str(e)})
                    raise

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            input_data = kwargs.get("input_data") or (args[0] if args else None)
            metadata = kwargs.get("metadata", {})

            with tracer.trace_stage_execution(input_data, metadata) as stage_span:
                stage_span.add_event("stage_execution_started")

                try:
                    result = func(self, *args, **kwargs)

                    if isinstance(result, dict):
                        stage_span.record_output(result)

                    stage_span.add_event("stage_execution_completed")
                    return result

                except Exception as e:
                    stage_span.add_event("stage_execution_failed", {"error": str(e)})
                    raise

        # Return appropriate wrapper based on function type
        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def get_trace_context() -> Dict[str, Any]:
    """Get current trace context for manual span linking"""
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        span_context = current_span.get_span_context()
        return {
            "trace_id": format(span_context.trace_id, "032x"),
            "span_id": format(span_context.span_id, "016x"),
            "correlation_id": get_correlation_id(),
        }
    return {"correlation_id": get_correlation_id()}


# Initialize tracing on module import with environment-based configuration
def auto_initialize_tracing():
    """Auto-initialize tracing based on environment configuration"""
    if not _initialized:
        otlp_endpoint = getattr(settings, "otlp_endpoint", None)
        enable_console = getattr(settings, "enable_console_tracing", True)

        try:
            initialize_tracing(otlp_endpoint=otlp_endpoint, enable_console_export=enable_console)
        except Exception as e:
            logger.warning(f"Failed to auto-initialize tracing: {e}")


# Auto-initialize if not in test environment
if os.getenv("ENVIRONMENT") != "test":
    auto_initialize_tracing()
