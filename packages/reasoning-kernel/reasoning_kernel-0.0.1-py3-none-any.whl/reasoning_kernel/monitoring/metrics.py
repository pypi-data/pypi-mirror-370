"""
Custom Metrics Collection and Management

This module provides comprehensive metrics collection for the Thinking Exploration
Framework, including counters, gauges, histograms, and custom business metrics.

Features:
- Thread-safe metric collection
- Multiple metric types (Counter, Gauge, Histogram, Summary)
- Custom thinking-specific metrics
- Metric aggregation and reporting
- Export to monitoring systems (Prometheus, StatsD, etc.)
"""

from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
import json
import threading
import time
from typing import Any, Dict, List, Optional, Union


class MetricType(Enum):
    """Types of metrics that can be collected"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


@dataclass
class MetricValue:
    """Container for a metric value with metadata"""

    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class MetricSummary:
    """Summary statistics for a metric"""

    name: str
    metric_type: MetricType
    current_value: Union[int, float]
    min_value: Union[int, float]
    max_value: Union[int, float]
    avg_value: float
    total_samples: int
    labels: Dict[str, str] = field(default_factory=dict)


class ThinkingMetrics:
    """
    Thread-safe metrics collection for thinking exploration operations

    Provides comprehensive metrics collection with support for:
    - Counters: Monotonically increasing values
    - Gauges: Point-in-time values
    - Histograms: Distribution of values
    - Timers: Duration measurements
    - Custom business metrics
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize the metrics collector

        Args:
            max_history: Maximum number of metric values to retain per metric
        """
        self._lock = threading.RLock()
        self._metrics: Dict[str, List[MetricValue]] = defaultdict(list)
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._max_history = max_history
        self._start_time = datetime.now()

        # Thinking-specific metrics
        self._exploration_metrics = {
            "total_explorations": 0,
            "successful_explorations": 0,
            "failed_explorations": 0,
            "avg_exploration_duration": 0.0,
            "context_switches": 0,
            "model_invocations": 0,
            "trigger_detections": 0,
            "mode_changes": 0,
        }

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric

        Args:
            name: Metric name
            value: Value to add (default: 1.0)
            labels: Optional labels for the metric
        """
        with self._lock:
            self._counters[name] += value
            self._record_metric(name, self._counters[name], MetricType.COUNTER, labels or {})

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric value

        Args:
            name: Metric name
            value: Current value
            labels: Optional labels for the metric
        """
        with self._lock:
            self._gauges[name] = value
            self._record_metric(name, value, MetricType.GAUGE, labels or {})

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Record a value in a histogram

        Args:
            name: Metric name
            value: Value to record
            labels: Optional labels for the metric
        """
        with self._lock:
            self._histograms[name].append(value)
            # Keep only recent values
            if len(self._histograms[name]) > self._max_history:
                self._histograms[name] = self._histograms[name][-self._max_history :]
            self._record_metric(name, value, MetricType.HISTOGRAM, labels or {})

    def start_timer(self, name: str) -> "Timer":
        """
        Start a timer for measuring duration

        Args:
            name: Timer name

        Returns:
            Timer context manager
        """
        return Timer(self, name)

    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Record a timer duration

        Args:
            name: Timer name
            duration: Duration in seconds
            labels: Optional labels for the metric
        """
        with self._lock:
            self._timers[name].append(duration)
            self._record_metric(name, duration, MetricType.TIMER, labels or {})

    def _record_metric(
        self, name: str, value: Union[int, float], metric_type: MetricType, labels: Dict[str, str]
    ) -> None:
        """Record a metric value with metadata"""
        metric_value = MetricValue(value=value, timestamp=datetime.now(), labels=labels, metric_type=metric_type)

        self._metrics[name].append(metric_value)

        # Keep only recent values
        if len(self._metrics[name]) > self._max_history:
            self._metrics[name] = self._metrics[name][-self._max_history :]

    # Thinking-specific metric methods
    def record_exploration_start(self, mode: str, context_complexity: str = "medium") -> None:
        """Record the start of a thinking exploration"""
        self.increment_counter("thinking.explorations.total")
        self.increment_counter(f"thinking.explorations.mode.{mode}")
        self.set_gauge("thinking.explorations.active", self._get_active_explorations() + 1)
        self.increment_counter(f"thinking.context.complexity.{context_complexity}")

        with self._lock:
            self._exploration_metrics["total_explorations"] += 1

    def record_exploration_success(self, duration: float, mode: str) -> None:
        """Record a successful thinking exploration"""
        self.increment_counter("thinking.explorations.successful")
        self.record_timer("thinking.exploration.duration", duration)
        self.increment_counter(f"thinking.explorations.success.{mode}")
        self.set_gauge("thinking.explorations.active", max(0, self._get_active_explorations() - 1))

        # Update average duration
        with self._lock:
            self._exploration_metrics["successful_explorations"] += 1
            total_duration = (
                self._exploration_metrics["avg_exploration_duration"]
                * (self._exploration_metrics["successful_explorations"] - 1)
                + duration
            )
            self._exploration_metrics["avg_exploration_duration"] = (
                total_duration / self._exploration_metrics["successful_explorations"]
            )

    def record_exploration_failure(self, error_type: str, mode: str) -> None:
        """Record a failed thinking exploration"""
        self.increment_counter("thinking.explorations.failed")
        self.increment_counter(f"thinking.explorations.error.{error_type}")
        self.increment_counter(f"thinking.explorations.failure.{mode}")
        self.set_gauge("thinking.explorations.active", max(0, self._get_active_explorations() - 1))

        with self._lock:
            self._exploration_metrics["failed_explorations"] += 1

    def record_trigger_detection(self, trigger_type: str, confidence: float) -> None:
        """Record a trigger detection event"""
        self.increment_counter("thinking.triggers.detected")
        self.increment_counter(f"thinking.triggers.type.{trigger_type}")
        self.record_histogram("thinking.triggers.confidence", confidence)

        with self._lock:
            self._exploration_metrics["trigger_detections"] += 1

    def record_mode_change(self, from_mode: str, to_mode: str) -> None:
        """Record a mode change event"""
        self.increment_counter("thinking.modes.changes")
        self.increment_counter(f"thinking.modes.from.{from_mode}")
        self.increment_counter(f"thinking.modes.to.{to_mode}")

        with self._lock:
            self._exploration_metrics["mode_changes"] += 1

    def record_model_invocation(self, model_type: str, duration: float, success: bool) -> None:
        """Record a model invocation"""
        self.increment_counter("thinking.models.invocations")
        self.increment_counter(f"thinking.models.type.{model_type}")
        self.record_timer(f"thinking.models.duration.{model_type}", duration)

        if success:
            self.increment_counter(f"thinking.models.success.{model_type}")
        else:
            self.increment_counter(f"thinking.models.failure.{model_type}")

        with self._lock:
            self._exploration_metrics["model_invocations"] += 1

    def _get_active_explorations(self) -> int:
        """Get the current number of active explorations"""
        return int(self._gauges.get("thinking.explorations.active", 0))

    def get_metric_summary(self, name: str) -> Optional[MetricSummary]:
        """
        Get summary statistics for a metric

        Args:
            name: Metric name

        Returns:
            MetricSummary if metric exists, None otherwise
        """
        with self._lock:
            if name not in self._metrics:
                return None

            values = self._metrics[name]
            if not values:
                return None

            metric_values = [v.value for v in values]
            latest = values[-1]

            return MetricSummary(
                name=name,
                metric_type=latest.metric_type,
                current_value=latest.value,
                min_value=min(metric_values),
                max_value=max(metric_values),
                avg_value=sum(metric_values) / len(metric_values),
                total_samples=len(metric_values),
                labels=latest.labels,
            )

    def get_all_metrics(self) -> Dict[str, MetricSummary]:
        """Get summary statistics for all metrics"""
        with self._lock:
            return {
                name: summary for name in self._metrics.keys() if (summary := self.get_metric_summary(name)) is not None
            }

    def get_thinking_metrics(self) -> Dict[str, Any]:
        """Get thinking-specific metrics summary"""
        with self._lock:
            runtime = (datetime.now() - self._start_time).total_seconds()

            return {
                **self._exploration_metrics,
                "runtime_seconds": runtime,
                "explorations_per_second": self._exploration_metrics["total_explorations"] / max(runtime, 1),
                "success_rate": (
                    self._exploration_metrics["successful_explorations"]
                    / max(self._exploration_metrics["total_explorations"], 1)
                )
                * 100,
                "average_models_per_exploration": (
                    self._exploration_metrics["model_invocations"]
                    / max(self._exploration_metrics["total_explorations"], 1)
                ),
            }

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        with self._lock:
            for name, summary in self.get_all_metrics().items():
                # Convert name to Prometheus format
                prom_name = name.replace(".", "_").replace("-", "_")

                # Add help comment
                lines.append(f"# HELP {prom_name} {summary.metric_type.value} metric")
                lines.append(f"# TYPE {prom_name} {summary.metric_type.value}")

                # Add labels if present
                labels_str = ""
                if summary.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in summary.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"

                lines.append(f"{prom_name}{labels_str} {summary.current_value}")

        return "\n".join(lines)

    def export_json(self) -> str:
        """
        Export metrics in JSON format

        Returns:
            JSON-formatted metrics string
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "thinking_metrics": self.get_thinking_metrics(),
            "all_metrics": {
                name: {
                    "name": summary.name,
                    "type": summary.metric_type.value,
                    "current_value": summary.current_value,
                    "min_value": summary.min_value,
                    "max_value": summary.max_value,
                    "avg_value": summary.avg_value,
                    "total_samples": summary.total_samples,
                    "labels": summary.labels,
                }
                for name, summary in self.get_all_metrics().items()
            },
        }

        return json.dumps(data, indent=2, default=str)

    def reset_metrics(self) -> None:
        """Reset all metrics to initial state"""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()
            self._exploration_metrics = {
                "total_explorations": 0,
                "successful_explorations": 0,
                "failed_explorations": 0,
                "avg_exploration_duration": 0.0,
                "context_switches": 0,
                "model_invocations": 0,
                "trigger_detections": 0,
                "mode_changes": 0,
            }
            self._start_time = datetime.now()


class Timer:
    """Context manager for timing operations"""

    def __init__(self, metrics: ThinkingMetrics, name: str, labels: Optional[Dict[str, str]] = None):
        self.metrics = metrics
        self.name = name
        self.labels = labels or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics.record_timer(self.name, duration, self.labels)


# Global metrics instance
_global_metrics = None


def get_metrics() -> ThinkingMetrics:
    """Get the global metrics instance"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = ThinkingMetrics()
    return _global_metrics


def reset_global_metrics() -> None:
    """Reset the global metrics instance"""
    global _global_metrics
    _global_metrics = None
