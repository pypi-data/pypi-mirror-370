"""
High-performance caches for reasoning workloads (TASK-026)

Design goals:
- Thread-safe writes (via RLock) with low overhead reads
- TTL eviction + LRU policy for hotsets
- Metrics hooks (hits/misses/evictions) using app.monitoring.metrics
- Async memoization and in-flight dedupe to prevent thundering herds
"""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
import threading
import time
from typing import (
    Awaitable,
    Callable,
    Dict,
    Generic,
    Hashable,
    Optional,
    Protocol,
    TypeVar,
)


class MetricsLike(Protocol):
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None: ...
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None: ...


def _get_metrics() -> MetricsLike:
    """Return a metrics instance if monitoring is available, else a no-op."""
    try:
        from reasoning_kernel.monitoring.metrics import get_metrics as _gm  # type: ignore

        return _gm()
    except Exception:

        class _N:
            def increment_counter(self, *a, **k):
                pass

            def set_gauge(self, *a, **k):
                pass

        return _N()


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


@dataclass
class _Entry(Generic[V]):
    value: V
    ts: float  # last touch
    ttl: Optional[float]


class TTLCache(Generic[K, V]):
    """Simple TTL cache with O(1) access and lazy expiry."""

    _metrics: MetricsLike

    def __init__(self, default_ttl: Optional[float] = None, maxsize: Optional[int] = None):
        self._default_ttl = default_ttl
        self._maxsize = maxsize
        self._data: Dict[K, _Entry[V]] = {}
        self._lock = threading.RLock()
        self._metrics = _get_metrics()

    def _expired(self, e: _Entry[V]) -> bool:
        if e.ttl is None:
            return False
        return (time.time() - e.ts) > e.ttl

    def get(self, key: K) -> Optional[V]:
        with self._lock:
            e = self._data.get(key)
            if not e:
                self._metrics.increment_counter("cache.ttl.miss")
                return None
            if self._expired(e):
                self._metrics.increment_counter("cache.ttl.expired")
                del self._data[key]
                return None
            self._metrics.increment_counter("cache.ttl.hit")
            return e.value

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        with self._lock:
            eff_ttl = ttl if ttl is not None else self._default_ttl
            self._data[key] = _Entry(value=value, ts=time.time(), ttl=eff_ttl)
            self._metrics.increment_counter("cache.ttl.set")
            if self._maxsize and len(self._data) > self._maxsize:
                # arbitrary eviction (oldest by ts)
                k_old = min(self._data.items(), key=lambda kv: kv[1].ts)[0]
                del self._data[k_old]
                self._metrics.increment_counter("cache.ttl.evicted")

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            self._metrics.increment_counter("cache.ttl.cleared")


class LRUCache(Generic[K, V]):
    """LRU cache with optional TTL per entry."""

    _metrics: MetricsLike

    def __init__(self, maxsize: int = 1024, default_ttl: Optional[float] = None):
        self._maxsize = maxsize
        self._default_ttl = default_ttl
        self._od: OrderedDict[K, _Entry[V]] = OrderedDict()
        self._lock = threading.RLock()
        self._metrics = _get_metrics()

    def _expired(self, e: _Entry[V]) -> bool:
        if e.ttl is None:
            return False
        return (time.time() - e.ts) > e.ttl

    def get(self, key: K) -> Optional[V]:
        with self._lock:
            e = self._od.get(key)
            if not e:
                self._metrics.increment_counter("cache.lru.miss")
                return None
            if self._expired(e):
                del self._od[key]
                self._metrics.increment_counter("cache.lru.expired")
                return None
            # move to end (most recent)
            e.ts = time.time()
            self._od.move_to_end(key)
            self._metrics.increment_counter("cache.lru.hit")
            return e.value

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        with self._lock:
            eff_ttl = ttl if ttl is not None else self._default_ttl
            self._od[key] = _Entry(value=value, ts=time.time(), ttl=eff_ttl)
            self._od.move_to_end(key)
            self._metrics.increment_counter("cache.lru.set")
            if len(self._od) > self._maxsize:
                self._od.popitem(last=False)
                self._metrics.increment_counter("cache.lru.evicted")

    def clear(self) -> None:
        with self._lock:
            self._od.clear()
            self._metrics.increment_counter("cache.lru.cleared")


class AdaptiveCache(Generic[K, V]):
    """Composite cache: small hotset LRU + TTL backing.

    Fast path: LRU; fallback: TTL; on hit in TTL, promote to LRU.
    """

    _metrics: MetricsLike

    def __init__(self, lru_size: int = 256, ttl_default: Optional[float] = 300.0):
        self._lru = LRUCache[K, V](maxsize=lru_size, default_ttl=ttl_default)
        self._ttl = TTLCache[K, V](default_ttl=ttl_default)
        self._metrics = _get_metrics()

    def get(self, key: K) -> Optional[V]:
        v = self._lru.get(key)
        if v is not None:
            return v
        v = self._ttl.get(key)
        if v is not None:
            self._lru.set(key, v)
            self._metrics.increment_counter("cache.adaptive.promote")
        else:
            self._metrics.increment_counter("cache.adaptive.miss")
        return v

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        self._lru.set(key, value, ttl)
        self._ttl.set(key, value, ttl)
        self._metrics.increment_counter("cache.adaptive.set")

    def clear(self) -> None:
        self._lru.clear()
        self._ttl.clear()
        self._metrics.increment_counter("cache.adaptive.cleared")


class InflightDeduper(Generic[K, V]):
    """Deduplicate concurrent async calls for the same key.

    Use to prevent thundering herds on identical expensive operations.
    """

    def __init__(self):
        self._futures: Dict[K, asyncio.Future[V]] = {}
        self._lock = asyncio.Lock()

    async def run(self, key: K, coro_factory: Callable[[], Awaitable[V]]) -> V:
        async with self._lock:
            if key in self._futures:
                return await self._futures[key]
            fut = asyncio.ensure_future(coro_factory())
            self._futures[key] = fut
        try:
            return await fut
        finally:
            async with self._lock:
                self._futures.pop(key, None)


F = TypeVar("F")


def memoize_async(cache: Optional[AdaptiveCache[K, V]] = None, key_fn: Optional[Callable[..., K]] = None):
    """Async memoization decorator using AdaptiveCache.

    Example:
        cache = AdaptiveCache[str, Any]()

        @memoize_async(cache, key_fn=lambda q: q)
        async def fetch(q: str) -> dict:
            ...
    """
    cache_obj = cache or AdaptiveCache()

    def decorator(func: Callable[..., Awaitable[V]]):
        def _make_key(args, kwargs):
            if key_fn:
                return key_fn(*args, **kwargs)
            return (args, tuple(sorted(kwargs.items())))  # basic fallback

        async def wrapper(*args, **kwargs) -> V:
            k = _make_key(args, kwargs)
            v = cache_obj.get(k)  # type: ignore[arg-type]
            if v is not None:
                return v
            res = await func(*args, **kwargs)
            cache_obj.set(k, res)  # type: ignore[arg-type]
            return res

        return wrapper

    return decorator
