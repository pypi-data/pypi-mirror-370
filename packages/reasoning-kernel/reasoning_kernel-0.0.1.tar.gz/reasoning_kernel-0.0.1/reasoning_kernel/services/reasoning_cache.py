"""
ReasoningCache - Dedicated caching layer for MSA Reasoning Kernel

This module implements a comprehensive caching system that integrates:
- Multi-tier caching (in-memory LRU + Redis backend)
- TTL-based cache invalidation
- Cache warming strategies
- Hit/miss ratio monitoring
- MSA-specific cache patterns
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
import time
from typing import Any, Dict, List, Optional, TypeVar, Union

from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.core.tracing import trace_operation
from reasoning_kernel.optimization.cache import AdaptiveCache
from reasoning_kernel.services.redis_service import RedisMemoryService


logger = get_logger(__name__)

T = TypeVar("T")


class CacheLevel(Enum):
    """Cache level priorities for different data types"""

    CRITICAL = "critical"  # Hot data: reasoning patterns, active sessions
    IMPORTANT = "important"  # Frequently accessed: embeddings, model results
    NORMAL = "normal"  # Standard data: knowledge entities, pipeline results
    LOW = "low"  # Cold data: archived sessions, debug info


class CacheStrategy(Enum):
    """Cache eviction and retention strategies"""

    LRU = "lru"  # Least Recently Used
    TTL = "ttl"  # Time To Live based
    ADAPTIVE = "adaptive"  # Hybrid LRU + TTL with promotion
    WARMING = "warming"  # Proactive cache warming


@dataclass
class CacheConfig:
    """Configuration for ReasoningCache"""

    # Memory cache settings
    memory_cache_size: int = 1024
    default_ttl_seconds: int = 1800  # 30 minutes

    # TTL configurations for different cache levels
    critical_ttl: int = 3600  # 1 hour
    important_ttl: int = 1800  # 30 minutes
    normal_ttl: int = 900  # 15 minutes
    low_ttl: int = 300  # 5 minutes

    # Redis backend settings
    redis_enabled: bool = True
    redis_url: Optional[str] = None
    redis_prefix: str = "reasoning_cache:"

    # Cache warming settings
    enable_warming: bool = True
    warming_queries: List[str] = field(
        default_factory=lambda: ["common_reasoning_patterns", "frequent_model_results", "active_sessions"]
    )

    # Performance monitoring
    enable_metrics: bool = True
    metrics_collection_interval: int = 60  # seconds


@dataclass
class CacheStats:
    """Cache performance statistics"""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired: int = 0
    warming_hits: int = 0

    # Performance metrics
    avg_hit_time_ms: float = 0.0
    avg_miss_time_ms: float = 0.0
    cache_size: int = 0
    redis_size: int = 0

    # Hit rate calculations
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0

    @property
    def effective_hit_rate(self) -> float:
        """Hit rate including warmed cache hits"""
        total = self.hits + self.misses + self.warming_hits
        effective_hits = self.hits + self.warming_hits
        return (effective_hits / total) if total > 0 else 0.0


class ReasoningCache:
    """
    Multi-tier caching system for MSA Reasoning Kernel

    Features:
    - Adaptive in-memory cache with LRU + TTL
    - Redis backend for persistence and sharing
    - Cache warming for common patterns
    - MSA-specific cache key patterns
    - Performance monitoring and metrics
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.stats = CacheStats()

        # Initialize multi-tier caches
        self._memory_cache = AdaptiveCache[str, Any](
            lru_size=self.config.memory_cache_size, ttl_default=float(self.config.default_ttl_seconds)
        )

        # Redis backend (initialized lazily)
        self._redis_service: Optional[RedisMemoryService] = None
        self._redis_available = False

        # Cache warming state
        self._warming_enabled = self.config.enable_warming
        self._warming_in_progress = set()

        # Metrics collection
        self._last_metrics_collection = time.time()

        logger.info("ReasoningCache initialized with multi-tier architecture")

    async def initialize(self):
        """Initialize Redis backend and perform initial setup"""
        if self.config.redis_enabled:
            try:
                # Create RedisMemoryService with proper parameters
                self._redis_service = RedisMemoryService(
                    host="localhost", port=6379, ttl_seconds=self.config.default_ttl_seconds
                )
                # Test connection with a simple get operation
                await self._redis_service.get("__test_connection__")
                self._redis_available = True
                logger.info("Redis backend initialized successfully")

                # Start cache warming if enabled
                if self._warming_enabled:
                    asyncio.create_task(self._warm_cache())

            except Exception as e:
                logger.warning(f"Redis backend unavailable: {e}")
                self._redis_available = False
        else:
            logger.info("Redis backend disabled by configuration")

    async def get(
        self, key: str, cache_level: CacheLevel = CacheLevel.NORMAL, default: Optional[T] = None
    ) -> Optional[T]:
        """
        Retrieve value from cache with multi-tier lookup

        Lookup order: Memory Cache -> Redis -> Return default
        """
        start_time = time.perf_counter()

        try:
            with trace_operation("cache.get", {"key": key, "level": cache_level.value}):
                # Try memory cache first
                value = self._memory_cache.get(key)
                if value is not None:
                    self.stats.hits += 1
                    self._update_hit_time(start_time)
                    return value

                # Try Redis cache if available
                if self._redis_available and self._redis_service:
                    redis_key = f"{self.config.redis_prefix}{key}"
                    redis_value = await self._redis_service.get(redis_key)

                    if redis_value is not None:
                        # Promote to memory cache
                        ttl = self._get_ttl_for_level(cache_level)
                        self._memory_cache.set(key, redis_value, ttl=float(ttl))

                        self.stats.hits += 1
                        self._update_hit_time(start_time)
                        return redis_value

                # Cache miss
                self.stats.misses += 1
                self._update_miss_time(start_time)
                return default

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats.misses += 1
            return default

    async def set(
        self,
        key: str,
        value: Union[dict, List[float]],
        cache_level: CacheLevel = CacheLevel.NORMAL,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Store value in cache with multi-tier persistence

        Storage: Memory Cache + Redis (if available)
        """
        try:
            with trace_operation("cache.set", {"key": key, "level": cache_level.value}):
                effective_ttl = ttl or self._get_ttl_for_level(cache_level)

                # Store in memory cache
                self._memory_cache.set(key, value, ttl=float(effective_ttl))

                # Store in Redis if available
                if self._redis_available and self._redis_service:
                    redis_key = f"{self.config.redis_prefix}{key}"
                    await self._redis_service.setex(redis_key, effective_ttl, value)

                return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from all cache tiers"""
        try:
            with trace_operation("cache.delete", {"key": key}):
                # Remove from memory cache
                self._memory_cache.clear()  # Simple approach, could be optimized

                # Remove from Redis if available
                if self._redis_available and self._redis_service:
                    redis_key = f"{self.config.redis_prefix}{key}"
                    # Use the underlying Redis client to delete
                    if hasattr(self._redis_service, "async_redis_client") and self._redis_service.async_redis_client:
                        await self._redis_service.async_redis_client.delete(redis_key)

                return True

        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries, optionally matching a pattern"""
        try:
            with trace_operation("cache.clear", {"pattern": pattern or "all"}):
                # Clear memory cache
                self._memory_cache.clear()

                # Clear Redis if available
                if self._redis_available and self._redis_service and hasattr(self._redis_service, "async_redis_client"):
                    redis_client = self._redis_service.async_redis_client
                    if redis_client:
                        if pattern:
                            search_pattern = f"{self.config.redis_prefix}{pattern}"
                        else:
                            search_pattern = f"{self.config.redis_prefix}*"

                        keys = await redis_client.keys(search_pattern)
                        if keys:
                            await redis_client.delete(*keys)

                # Reset stats
                self.stats = CacheStats()

                return True

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    # MSA-specific cache operations

    async def cache_reasoning_result(
        self, session_id: str, stage: str, result: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache MSA pipeline stage results"""
        key = f"reasoning_result:{session_id}:{stage}"
        return await self.set(key, result, CacheLevel.IMPORTANT, ttl)

    async def get_reasoning_result(self, session_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached MSA pipeline stage results"""
        key = f"reasoning_result:{session_id}:{stage}"
        return await self.get(key, CacheLevel.IMPORTANT)

    async def cache_model_result(
        self, model_name: str, input_hash: str, result: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache probabilistic model execution results"""
        key = f"model_result:{model_name}:{input_hash}"
        return await self.set(key, result, CacheLevel.CRITICAL, ttl)

    async def get_model_result(self, model_name: str, input_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached model results"""
        key = f"model_result:{model_name}:{input_hash}"
        return await self.get(key, CacheLevel.CRITICAL)

    async def cache_embedding(self, text_hash: str, embedding: List[float], ttl: Optional[int] = None) -> bool:
        """Cache text embeddings for reuse"""
        key = f"embedding:{text_hash}"
        return await self.set(key, embedding, CacheLevel.IMPORTANT, ttl)

    async def get_embedding(self, text_hash: str) -> Optional[List[float]]:
        """Retrieve cached embeddings"""
        key = f"embedding:{text_hash}"
        return await self.get(key, CacheLevel.IMPORTANT)

    # Cache warming and optimization

    async def warm_common_patterns(self, patterns: Optional[List[str]] = None) -> int:
        """Warm cache with commonly used reasoning patterns"""
        if not self._warming_enabled:
            return 0

        patterns = patterns or self.config.warming_queries
        warmed_count = 0

        try:
            with trace_operation("cache.warm_patterns", {"pattern_count": len(patterns)}):
                for pattern in patterns:
                    if pattern in self._warming_in_progress:
                        continue

                    self._warming_in_progress.add(pattern)

                    try:
                        # This would be customized based on actual patterns
                        await self._warm_pattern(pattern)
                        warmed_count += 1

                    except Exception as e:
                        logger.warning(f"Failed to warm pattern {pattern}: {e}")

                    finally:
                        self._warming_in_progress.discard(pattern)

                logger.info(f"Cache warming completed: {warmed_count} patterns loaded")
                return warmed_count

        except Exception as e:
            logger.error(f"Cache warming error: {e}")
            return warmed_count

    async def _warm_pattern(self, pattern: str):
        """Warm cache for a specific pattern"""
        # This would be implemented based on actual pattern types
        # For now, just a placeholder that could be extended
        if pattern == "common_reasoning_patterns":
            # Pre-load frequent reasoning templates
            logger.debug("Warming common reasoning patterns")
        elif pattern == "frequent_model_results":
            # Pre-load commonly used model outputs
            logger.debug("Warming frequent model results")
        elif pattern == "active_sessions":
            # Pre-load recently active session data
            logger.debug("Warming active sessions")

    async def _warm_cache(self):
        """Background task for periodic cache warming"""
        while self._warming_enabled:
            try:
                await self.warm_common_patterns()
                await asyncio.sleep(300)  # Warm every 5 minutes
            except Exception as e:
                logger.error(f"Cache warming background task error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error

    # Cache monitoring and metrics

    def get_stats(self) -> CacheStats:
        """Get current cache statistics"""
        # Update cache sizes
        self.stats.cache_size = len(self._memory_cache._lru._od)
        return self.stats

    async def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed cache performance metrics"""
        stats = self.get_stats()

        metrics = {
            "performance": {
                "hit_rate": stats.hit_rate,
                "effective_hit_rate": stats.effective_hit_rate,
                "avg_hit_time_ms": stats.avg_hit_time_ms,
                "avg_miss_time_ms": stats.avg_miss_time_ms,
            },
            "counters": {
                "hits": stats.hits,
                "misses": stats.misses,
                "evictions": stats.evictions,
                "expired": stats.expired,
                "warming_hits": stats.warming_hits,
            },
            "capacity": {
                "memory_cache_size": stats.cache_size,
                "redis_cache_size": stats.redis_size,
                "memory_cache_limit": self.config.memory_cache_size,
            },
            "configuration": {
                "redis_enabled": self._redis_available,
                "warming_enabled": self._warming_enabled,
                "default_ttl_seconds": self.config.default_ttl_seconds,
            },
            "timestamp": datetime.now().isoformat(),
        }

        return metrics

    async def optimize_cache(self) -> Dict[str, Any]:
        """Perform cache optimization and cleanup"""
        optimization_stats = {
            "cleaned_expired": 0,
            "promoted_items": 0,
            "memory_saved_mb": 0.0,
        }

        try:
            with trace_operation("cache.optimize"):
                # This would implement actual optimization logic
                # For now, just return stats placeholder
                logger.info("Cache optimization completed")

        except Exception as e:
            logger.error(f"Cache optimization error: {e}")

        return optimization_stats

    # Helper methods

    def _get_ttl_for_level(self, level: CacheLevel) -> int:
        """Get TTL in seconds based on cache level"""
        ttl_mapping = {
            CacheLevel.CRITICAL: self.config.critical_ttl,
            CacheLevel.IMPORTANT: self.config.important_ttl,
            CacheLevel.NORMAL: self.config.normal_ttl,
            CacheLevel.LOW: self.config.low_ttl,
        }
        return ttl_mapping.get(level, self.config.default_ttl_seconds)

    def _update_hit_time(self, start_time: float):
        """Update average hit time metrics"""
        duration_ms = (time.perf_counter() - start_time) * 1000
        # Simple moving average (could be improved)
        if self.stats.avg_hit_time_ms == 0:
            self.stats.avg_hit_time_ms = duration_ms
        else:
            self.stats.avg_hit_time_ms = (self.stats.avg_hit_time_ms + duration_ms) / 2

    def _update_miss_time(self, start_time: float):
        """Update average miss time metrics"""
        duration_ms = (time.perf_counter() - start_time) * 1000
        # Simple moving average (could be improved)
        if self.stats.avg_miss_time_ms == 0:
            self.stats.avg_miss_time_ms = duration_ms
        else:
            self.stats.avg_miss_time_ms = (self.stats.avg_miss_time_ms + duration_ms) / 2

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup resources if needed
        pass


# Factory function for easy instantiation
def create_reasoning_cache(config: Optional[CacheConfig] = None) -> ReasoningCache:
    """Create and return a configured ReasoningCache instance"""
    return ReasoningCache(config)


# Convenience functions for common cache configurations
def create_production_cache(redis_url: str) -> ReasoningCache:
    """Create a production-optimized cache configuration"""
    config = CacheConfig(
        memory_cache_size=2048,
        redis_enabled=True,
        redis_url=redis_url,
        critical_ttl=7200,  # 2 hours
        important_ttl=3600,  # 1 hour
        normal_ttl=1800,  # 30 minutes
        enable_warming=True,
    )
    return ReasoningCache(config)


def create_development_cache(redis_url: Optional[str] = None) -> ReasoningCache:
    """Create a development-optimized cache configuration"""
    config = CacheConfig(
        memory_cache_size=512,
        redis_enabled=bool(redis_url),
        redis_url=redis_url,
        critical_ttl=1800,  # 30 minutes
        important_ttl=900,  # 15 minutes
        normal_ttl=300,  # 5 minutes
        enable_warming=False,  # Disabled for development
    )
    return ReasoningCache(config)
