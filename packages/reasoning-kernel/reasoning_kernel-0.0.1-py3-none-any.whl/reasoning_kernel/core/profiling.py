"""
Performance Profiling Decorators for MSA Reasoning Kernel

This module provides decorators and utilities for performance profiling
and monitoring of MSA pipeline components.
"""

from contextlib import contextmanager
import cProfile
import functools
import io
import pstats
import time
from typing import Any, Callable, Dict, Optional

from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.core.logging_config import performance_context
from reasoning_kernel.core.tracing import get_correlation_id
from reasoning_kernel.core.tracing import trace_operation
from reasoning_kernel.core.error_handling import simple_log_error


logger = get_logger(__name__)


def profile_performance(
    operation_name: Optional[str] = None,
    log_threshold: float = 1.0,  # Log if operation takes longer than 1 second
    enable_detailed_profiling: bool = False,
    profile_memory: bool = False,
):
    """
    Decorator for performance profiling with configurable thresholds.

    Args:
        operation_name: Optional custom operation name
        log_threshold: Log performance if execution time exceeds this (seconds)
        enable_detailed_profiling: Enable detailed cProfile profiling
        profile_memory: Enable memory usage profiling (requires psutil)
    """

    def decorator(func: Callable) -> Callable:
        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _profile_execution(
                func, args, kwargs, op_name, log_threshold, enable_detailed_profiling, profile_memory, is_async=True
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _profile_execution_sync(
                func, args, kwargs, op_name, log_threshold, enable_detailed_profiling, profile_memory
            )

        # Return appropriate wrapper based on function type
        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


async def _profile_execution(
    func: Callable,
    args: tuple,
    kwargs: dict,
    op_name: str,
    log_threshold: float,
    enable_detailed_profiling: bool,
    profile_memory: bool,
    is_async: bool = True,
) -> Any:
    """Execute function with performance profiling (async version)"""

    # Memory profiling setup
    memory_before = None
    if profile_memory:
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            logger.warning("psutil not available for memory profiling")
            profile_memory = False

    # Setup profiling
    profiler = None
    if enable_detailed_profiling:
        profiler = cProfile.Profile()
        profiler.enable()

    start_time = time.time()

    try:
        with trace_operation(f"performance.{op_name}") as span:
            # Execute function
            if is_async:
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Record execution time
            execution_time = time.time() - start_time

            # Memory usage after
            memory_after = None
            memory_delta = None
            if profile_memory and memory_before is not None:
                import os

                import psutil

                process = psutil.Process(os.getpid())
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = memory_after - memory_before

            # Add performance attributes to span
            span.set_attribute("performance.execution_time", str(execution_time))
            span.set_attribute("performance.threshold_exceeded", str(execution_time > log_threshold))

            if memory_delta is not None:
                span.set_attribute("performance.memory_delta_mb", str(memory_delta))
                span.set_attribute("performance.memory_after_mb", str(memory_after))

            # Log performance if threshold exceeded
            if execution_time > log_threshold:
                perf_data = {
                    "operation": op_name,
                    "execution_time": execution_time,
                    "threshold": log_threshold,
                    "correlation_id": get_correlation_id(),
                }

                if memory_delta is not None:
                    perf_data.update(
                        {
                            "memory_before_mb": memory_before,
                            "memory_after_mb": memory_after,
                            "memory_delta_mb": memory_delta,
                        }
                    )

                logger.warning("Performance threshold exceeded", **perf_data)
            else:
                logger.debug(f"Performance OK: {op_name} completed in {execution_time:.3f}s")

            # Process detailed profiling results
            if profiler is not None:
                profiler.disable()
                await _log_profiling_results(profiler, op_name, execution_time)

            return result

    except Exception as e:
        execution_time = time.time() - start_time
        simple_log_error(logger, "profile_execution_sync", e, operation=op_name, execution_time=execution_time, correlation_id=get_correlation_id())

        if profiler is not None:
            profiler.disable()

        raise


def _profile_execution_sync(
    func: Callable,
    args: tuple,
    kwargs: dict,
    op_name: str,
    log_threshold: float,
    enable_detailed_profiling: bool,
    profile_memory: bool,
) -> Any:
    """Execute function with performance profiling (sync version)"""

    # Memory profiling setup
    memory_before = None
    if profile_memory:
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            logger.warning("psutil not available for memory profiling")
            profile_memory = False

    # Setup profiling
    profiler = None
    if enable_detailed_profiling:
        profiler = cProfile.Profile()
        profiler.enable()

    start_time = time.time()

    try:
        with trace_operation(f"performance.{op_name}") as span:
            # Execute function
            result = func(*args, **kwargs)

            # Record execution time
            execution_time = time.time() - start_time

            # Memory usage after
            memory_after = None
            memory_delta = None
            if profile_memory and memory_before is not None:
                import os

                import psutil

                process = psutil.Process(os.getpid())
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = memory_after - memory_before

            # Add performance attributes to span
            span.set_attribute("performance.execution_time", str(execution_time))
            span.set_attribute("performance.threshold_exceeded", str(execution_time > log_threshold))

            if memory_delta is not None:
                span.set_attribute("performance.memory_delta_mb", str(memory_delta))
                span.set_attribute("performance.memory_after_mb", str(memory_after))

            # Log performance if threshold exceeded
            if execution_time > log_threshold:
                perf_data = {
                    "operation": op_name,
                    "execution_time": execution_time,
                    "threshold": log_threshold,
                    "correlation_id": get_correlation_id(),
                }

                if memory_delta is not None:
                    perf_data.update(
                        {
                            "memory_before_mb": memory_before,
                            "memory_after_mb": memory_after,
                            "memory_delta_mb": memory_delta,
                        }
                    )

                logger.warning("Performance threshold exceeded", **perf_data)
            else:
                logger.debug(f"Performance OK: {op_name} completed in {execution_time:.3f}s")

            # Process detailed profiling results
            if profiler is not None:
                profiler.disable()
                _log_profiling_results_sync(profiler, op_name, execution_time)

            return result

    except Exception as e:
        execution_time = time.time() - start_time
        simple_log_error(logger, "profile_execution", e, operation=op_name, execution_time=execution_time, correlation_id=get_correlation_id())

        if profiler is not None:
            profiler.disable()

        raise


async def _log_profiling_results(profiler: cProfile.Profile, op_name: str, execution_time: float):
    """Log detailed profiling results (async version)"""
    try:
        # Capture profiling stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions

        profiling_output = s.getvalue()

        logger.info(
            "Detailed profiling results",
            operation=op_name,
            execution_time=execution_time,
            profiling_output=profiling_output,
            correlation_id=get_correlation_id(),
        )

    except Exception as e:
        simple_log_error(logger, "log_profiling_results", e)


def _log_profiling_results_sync(profiler: cProfile.Profile, op_name: str, execution_time: float):
    """Log detailed profiling results (sync version)"""
    try:
        # Capture profiling stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions

        profiling_output = s.getvalue()

        logger.info(
            "Detailed profiling results",
            operation=op_name,
            execution_time=execution_time,
            profiling_output=profiling_output,
            correlation_id=get_correlation_id(),
        )

    except Exception as e:
        simple_log_error(logger, "log_profiling_results_sync", e)


@contextmanager
def performance_monitor(operation_name: str, log_threshold: float = 1.0, monitor_memory: bool = False):
    """Context manager for performance monitoring"""

    # Memory monitoring setup
    memory_before = None
    if monitor_memory:
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            monitor_memory = False

    start_time = time.time()

    try:
        with performance_context(operation_name) as perf_logger:
            yield perf_logger

        # Calculate metrics
        execution_time = time.time() - start_time

        # Memory calculation
        memory_delta = None
        if monitor_memory and memory_before is not None:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = memory_after - memory_before

        # Log results
        if execution_time > log_threshold:
            log_data = {
                "operation": operation_name,
                "execution_time": execution_time,
                "threshold": log_threshold,
                "correlation_id": get_correlation_id(),
            }

            if memory_delta is not None:
                log_data["memory_delta_mb"] = memory_delta

            logger.warning("Performance threshold exceeded in context", **log_data)

    except Exception as e:
        execution_time = time.time() - start_time
        simple_log_error(logger, "performance_monitor", e, operation=operation_name, execution_time=execution_time, correlation_id=get_correlation_id())
        raise


class PerformanceMetrics:
    """Utility class for collecting and reporting performance metrics"""

    def __init__(self):
        self.metrics: Dict[str, list] = {}

    def record_execution_time(self, operation: str, execution_time: float, metadata: Optional[Dict[str, Any]] = None):
        """Record execution time for an operation"""
        if operation not in self.metrics:
            self.metrics[operation] = []

        record = {"timestamp": time.time(), "execution_time": execution_time, "metadata": metadata or {}}
        self.metrics[operation].append(record)

    def get_statistics(self, operation: str) -> Dict[str, Any]:
        """Get statistics for an operation"""
        if operation not in self.metrics:
            return {"error": "No data for operation"}

        times = [record["execution_time"] for record in self.metrics[operation]]

        if not times:
            return {"error": "No timing data"}

        return {
            "operation": operation,
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "average": sum(times) / len(times),
            "total": sum(times),
            "latest_runs": times[-10:] if len(times) > 10 else times,
        }

    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations"""
        return {op: self.get_statistics(op) for op in self.metrics.keys()}

    def reset_metrics(self, operation: Optional[str] = None):
        """Reset metrics for specific operation or all operations"""
        if operation:
            self.metrics.pop(operation, None)
        else:
            self.metrics.clear()


# Global performance metrics instance
performance_metrics = PerformanceMetrics()


def profile_msa_stage(
    stage_name: Optional[str] = None,
    log_threshold: float = 5.0,  # MSA stages are expected to take longer
    enable_memory_profiling: bool = True,
    enable_detailed_profiling: bool = False,
):
    """Specialized performance profiler for MSA stages"""

    def decorator(func: Callable) -> Callable:
        op_name = stage_name or f"msa.stage.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with performance_monitor(op_name, log_threshold, enable_memory_profiling):
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Record metrics
                performance_metrics.record_execution_time(
                    op_name, execution_time, {"stage_type": "msa_stage", "correlation_id": get_correlation_id()}
                )

                return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with performance_monitor(op_name, log_threshold, enable_memory_profiling):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Record metrics
                performance_metrics.record_execution_time(
                    op_name, execution_time, {"stage_type": "msa_stage", "correlation_id": get_correlation_id()}
                )

                return result

        # Return appropriate wrapper
        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
