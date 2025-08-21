"""
Caching & Optimization utilities for the Reasoning Kernel (TASK-026)

This package provides:
- Adaptive in-memory caches with TTL and LRU semantics
- Deduplication utilities for concurrent requests
- Simple async memoization primitives
- Hooks to emit metrics via app.monitoring.metrics
"""

from .cache import AdaptiveCache
from .cache import InflightDeduper
from .cache import LRUCache
from .cache import memoize_async
from .cache import TTLCache


__all__ = [
    "TTLCache",
    "LRUCache",
    "AdaptiveCache",
    "memoize_async",
    "InflightDeduper",
]
