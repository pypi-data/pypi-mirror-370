"""
Response Caching Middleware for MSA Reasoning Kernel

Provides intelligent response caching for API endpoints:
- Redis-backed response caching with TTL
- Request deduplication for identical queries
- Cache invalidation strategies
- Configurable cache keys and TTL per endpoint
- Compression support for large responses
- Cache hit/miss metrics
"""

import asyncio
import gzip
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from reasoning_kernel.services.redis_service import RedisMemoryService


logger = structlog.get_logger(__name__)


class CacheStrategy(Enum):
    """Cache strategy for different endpoint types"""

    AGGRESSIVE = "aggressive"  # Long TTL, cache everything
    MODERATE = "moderate"  # Medium TTL, cache most responses
    CONSERVATIVE = "conservative"  # Short TTL, cache only expensive operations
    DISABLED = "disabled"  # No caching


@dataclass
class CacheConfig:
    """Cache configuration for specific endpoints"""

    ttl_seconds: int = 300  # 5 minutes default
    strategy: CacheStrategy = CacheStrategy.MODERATE
    cache_post_requests: bool = False
    compress_response: bool = True
    min_response_size_for_compression: int = 1024
    exclude_headers: Optional[Set[str]] = None
    cache_key_includes: Optional[List[str]] = None  # Additional data to include in cache key

    def __post_init__(self):
        if self.exclude_headers is None:
            self.exclude_headers = {
                "authorization",
                "x-api-key",
                "cookie",
                "set-cookie",
                "x-request-id",
                "x-trace-id",
                "date",
                "server",
            }
        if self.cache_key_includes is None:
            self.cache_key_includes = []


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for intelligent response caching"""

    def __init__(
        self,
        app,
        redis_service: Optional[RedisMemoryService] = None,
        default_config: Optional[CacheConfig] = None,
        endpoint_configs: Optional[Dict[str, CacheConfig]] = None,
    ):
        super().__init__(app)
        self.redis_service = redis_service
        self.default_config = default_config or CacheConfig()
        self.endpoint_configs = endpoint_configs or {}

        # In-flight request deduplication
        self.in_flight_requests: Dict[str, asyncio.Event] = {}
        self.in_flight_responses: Dict[str, Dict[str, Any]] = {}

        # Metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_errors = 0

        # Initialize endpoint-specific configurations
        self._initialize_endpoint_configs()

    def _initialize_endpoint_configs(self):
        """Initialize default caching configurations for different endpoint types"""

        # Reasoning endpoints - moderate caching (expensive operations)
        reasoning_config = CacheConfig(
            ttl_seconds=600,  # 10 minutes
            strategy=CacheStrategy.MODERATE,
            cache_post_requests=True,
            compress_response=True,
            cache_key_includes=["reasoning_type", "model_version"],
        )

        # Health endpoints - aggressive caching (frequent checks)
        health_config = CacheConfig(
            ttl_seconds=60, strategy=CacheStrategy.AGGRESSIVE, compress_response=False  # 1 minute
        )

        # Admin endpoints - conservative caching (sensitive data)
        admin_config = CacheConfig(
            ttl_seconds=30, strategy=CacheStrategy.CONSERVATIVE, cache_post_requests=False  # 30 seconds
        )

        # Knowledge extraction - moderate caching
        knowledge_config = CacheConfig(
            ttl_seconds=900,  # 15 minutes
            strategy=CacheStrategy.MODERATE,
            cache_post_requests=True,
            compress_response=True,
        )

        # Apply configurations
        default_configs = {
            "/api/v1/reason": reasoning_config,
            "/api/v2/reasoning": reasoning_config,
            "/api/v1/extract-knowledge": knowledge_config,
            "/api/v1/health": health_config,
            "/api/v2/health": health_config,
            "/api/v1/admin": admin_config,
        }

        # Merge with user-provided configs
        for pattern, config in default_configs.items():
            if pattern not in self.endpoint_configs:
                self.endpoint_configs[pattern] = config

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch logic"""

        # Skip caching if Redis unavailable
        if not self.redis_service:
            return await call_next(request)

        try:
            return await self._handle_request(request, call_next)
        except Exception as e:
            logger.error("Cache middleware error", error=str(e))
            self.cache_errors += 1
            # Fallback to normal request processing
            return await call_next(request)

    async def _handle_request(self, request: Request, call_next: Callable) -> Response:
        """Handle request with caching logic"""

        # Get cache configuration for this endpoint
        cache_config = self._get_cache_config(request)

        # Skip caching if disabled
        if cache_config.strategy == CacheStrategy.DISABLED:
            return await call_next(request)

        # Skip caching for non-cacheable methods
        if request.method not in ["GET", "POST"] or (request.method == "POST" and not cache_config.cache_post_requests):
            return await call_next(request)

        # Generate cache key
        cache_key = await self._generate_cache_key(request, cache_config)

        # Try to get from cache
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            self.cache_hits += 1
            return self._deserialize_response(cached_response)

        # Check for in-flight request deduplication
        response = await self._handle_deduplication(cache_key, request, call_next, cache_config)

        return response

    def _get_cache_config(self, request: Request) -> CacheConfig:
        """Get cache configuration for the given request"""

        path = request.url.path

        # Check for exact matches first
        if path in self.endpoint_configs:
            return self.endpoint_configs[path]

        # Check for pattern matches
        for pattern, config in self.endpoint_configs.items():
            if path.startswith(pattern):
                return config

        return self.default_config

    async def _generate_cache_key(self, request: Request, config: CacheConfig) -> str:
        """Generate a unique cache key for the request"""

        # Base key components
        key_parts = [
            request.method,
            request.url.path,
        ]

        # Add query parameters (sorted for consistency)
        if request.query_params:
            sorted_params = sorted(request.query_params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            key_parts.append(query_string)

        # Add request body for POST requests (if caching enabled)
        if request.method == "POST" and config.cache_post_requests:
            try:
                # Read body and reset stream
                body = await request.body()
                if body:
                    # Hash the body to keep key size manageable
                    body_hash = hashlib.sha256(body).hexdigest()[:16]
                    key_parts.append(body_hash)

                # Reset request body stream for downstream processing
                request._body = body
            except Exception as e:
                logger.warning("Failed to read request body for caching", error=str(e))

        # Add custom includes from config
        for include in config.cache_key_includes or []:
            if hasattr(request.state, include):
                key_parts.append(str(getattr(request.state, include)))

        # Create final key
        raw_key = ":".join(key_parts)
        cache_key = f"response_cache:{hashlib.md5(raw_key.encode()).hexdigest()}"

        return cache_key

    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response from Redis"""

        if not self.redis_service:
            return None

        try:
            cached_data = await self.redis_service.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Failed to retrieve from cache", cache_key=cache_key, error=str(e))

        return None

    async def _handle_deduplication(
        self, cache_key: str, request: Request, call_next: Callable, config: CacheConfig
    ) -> Response:
        """Handle request deduplication for identical in-flight requests"""

        # Check if identical request is already in flight
        if cache_key in self.in_flight_requests:
            logger.info("Request deduplication hit", cache_key=cache_key)
            # Wait for the in-flight request to complete
            await self.in_flight_requests[cache_key].wait()

            # Return the cached response if available
            if cache_key in self.in_flight_responses:
                response_data = self.in_flight_responses.pop(cache_key)
                return self._deserialize_response(response_data)

        # Mark this request as in-flight
        self.in_flight_requests[cache_key] = asyncio.Event()

        try:
            # Process the request
            response = await call_next(request)

            # Cache successful responses
            if response.status_code < 400:
                await self._cache_response(cache_key, response, config)

                # Store for deduplication
                serialized = await self._serialize_response(response)
                self.in_flight_responses[cache_key] = serialized

            self.cache_misses += 1
            return response

        finally:
            # Mark request as complete and cleanup
            if cache_key in self.in_flight_requests:
                self.in_flight_requests[cache_key].set()
                del self.in_flight_requests[cache_key]

            # Cleanup deduplication cache after a short delay
            asyncio.create_task(self._cleanup_deduplication_cache(cache_key))

    async def _cleanup_deduplication_cache(self, cache_key: str, delay: int = 5):
        """Clean up deduplication cache after a delay"""
        await asyncio.sleep(delay)
        self.in_flight_responses.pop(cache_key, None)

    async def _cache_response(self, cache_key: str, response: Response, config: CacheConfig):
        """Cache the response in Redis"""

        if not self.redis_service:
            return

        try:
            # Serialize response
            serialized = await self._serialize_response(response)

            # Compress if configured and response is large enough
            cached_data = json.dumps(serialized)
            if config.compress_response and len(cached_data) >= config.min_response_size_for_compression:
                cached_data = gzip.compress(cached_data.encode()).decode("latin-1")
                serialized["_compressed"] = True

            # Store in Redis with TTL
            await self.redis_service.setex(
                cache_key,
                config.ttl_seconds,
                json.dumps(serialized) if not serialized.get("_compressed") else cached_data,
            )

            logger.debug("Response cached", cache_key=cache_key, ttl=config.ttl_seconds)

        except Exception as e:
            logger.warning("Failed to cache response", cache_key=cache_key, error=str(e))

    async def _serialize_response(self, response: Response) -> Dict[str, Any]:
        """Serialize response for caching"""

        # Read response body
        body = b""
        if hasattr(response, "body"):
            if isinstance(response.body, bytes):
                body = response.body
            else:
                try:
                    body = str(response.body).encode("utf-8")
                except Exception:
                    body = b""

        # Filter headers
        headers = {}
        exclude_headers = self.default_config.exclude_headers or set()
        for key, value in response.headers.items():
            if key.lower() not in exclude_headers:
                headers[key] = value

        return {
            "status_code": response.status_code,
            "headers": headers,
            "body": body.decode("utf-8") if body else "",
            "media_type": getattr(response, "media_type", "application/json"),
            "cached_at": datetime.now().isoformat(),
        }

    def _deserialize_response(self, cached_data: Dict[str, Any]) -> Response:
        """Deserialize cached response"""

        # Handle compression
        if cached_data.get("_compressed"):
            # Decompress data
            try:
                decompressed = gzip.decompress(cached_data["body"].encode("latin-1"))
                cached_data["body"] = decompressed.decode("utf-8")
            except Exception as e:
                logger.warning("Failed to decompress cached response", error=str(e))

        # Add cache headers
        headers = cached_data.get("headers", {})
        headers["X-Cache-Status"] = "HIT"
        headers["X-Cache-Timestamp"] = cached_data.get("cached_at", "")

        # Create response
        return Response(
            content=cached_data.get("body", ""),
            status_code=cached_data.get("status_code", 200),
            headers=headers,
            media_type=cached_data.get("media_type", "application/json"),
        )

    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""

        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests) if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_errors": self.cache_errors,
            "hit_rate": hit_rate,
            "in_flight_requests": len(self.in_flight_requests),
            "total_requests": total_requests,
        }

    async def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cached responses matching pattern"""

        if not self.redis_service:
            return

        try:
            if pattern:
                # Use Redis pattern matching to find and delete keys
                keys = await self.redis_service.keys(f"response_cache:*{pattern}*")
                if keys:
                    # Delete keys one by one since we don't have direct delete access
                    for key in keys:
                        await self.redis_service.setex(key, 1, "")  # Expire immediately
                    logger.info("Cache invalidated", pattern=pattern, keys_count=len(keys))
            else:
                # Clear all response cache
                keys = await self.redis_service.keys("response_cache:*")
                if keys:
                    # Delete keys one by one
                    for key in keys:
                        await self.redis_service.setex(key, 1, "")  # Expire immediately
                    logger.info("All response cache cleared", keys_count=len(keys))

        except Exception as e:
            logger.error("Cache invalidation failed", pattern=pattern, error=str(e))


# Cache configuration presets for common use cases
CACHE_PRESETS = {
    "reasoning": CacheConfig(
        ttl_seconds=600,  # 10 minutes
        strategy=CacheStrategy.MODERATE,
        cache_post_requests=True,
        compress_response=True,
        cache_key_includes=["model_version", "reasoning_type"],
    ),
    "health": CacheConfig(ttl_seconds=60, strategy=CacheStrategy.AGGRESSIVE, compress_response=False),  # 1 minute
    "knowledge": CacheConfig(
        ttl_seconds=900, strategy=CacheStrategy.MODERATE, cache_post_requests=True, compress_response=True  # 15 minutes
    ),
    "admin": CacheConfig(ttl_seconds=30, strategy=CacheStrategy.CONSERVATIVE, cache_post_requests=False),  # 30 seconds
}
