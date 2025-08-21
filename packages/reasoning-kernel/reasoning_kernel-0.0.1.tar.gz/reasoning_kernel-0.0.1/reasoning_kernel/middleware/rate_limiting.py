"""
Rate Limiting Middleware for MSA Reasoning Kernel

Provides comprehensive rate limiting for API endpoints:
- Per-IP rate limiting with sliding window
- Per-API-key rate limiting for authenticated requests
- Endpoint-specific rate limits
- Distributed rate limiting with Redis backend
- Graceful degradation when Redis unavailable
"""

import asyncio
from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
import hashlib
import time
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import Request
from fastapi import Response
from fastapi.responses import JSONResponse
from reasoning_kernel.core.logging_config import get_logger
import redis.asyncio as redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware


logger = get_logger(__name__)


class RateLimitType(Enum):
    """Rate limiting strategy types"""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""

    # Limit configuration
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000

    # Strategy
    strategy: RateLimitType = RateLimitType.SLIDING_WINDOW

    # Identifiers
    by_ip: bool = True
    by_api_key: bool = True
    by_user_id: bool = False

    # Behavior
    burst_allowance: float = 1.5  # Allow 150% of rate for short bursts
    block_duration_minutes: int = 15  # How long to block after limit exceeded


@dataclass
class EndpointLimits:
    """Endpoint-specific rate limits"""

    # Default limits for different endpoint types
    public_endpoints: RateLimitRule = field(
        default_factory=lambda: RateLimitRule(requests_per_minute=60, requests_per_hour=1000, requests_per_day=5000)
    )

    reasoning_endpoints: RateLimitRule = field(
        default_factory=lambda: RateLimitRule(requests_per_minute=30, requests_per_hour=500, requests_per_day=2000)
    )

    admin_endpoints: RateLimitRule = field(
        default_factory=lambda: RateLimitRule(requests_per_minute=100, requests_per_hour=2000, requests_per_day=20000)
    )

    health_endpoints: RateLimitRule = field(
        default_factory=lambda: RateLimitRule(requests_per_minute=120, requests_per_hour=5000, requests_per_day=50000)
    )


class SlidingWindowCounter:
    """In-memory sliding window rate limiter"""

    def __init__(self, window_size_minutes: int = 1):
        self.window_size = window_size_minutes * 60  # seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_until: Dict[str, float] = {}
        self.blocked_at: Dict[str, float] = {}

    def is_allowed(
        self, identifier: str, limit: int, current_time: Optional[float] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under sliding window"""
        if current_time is None:
            current_time = time.time()

        # If blocked, lift when whole window elapsed since block time; otherwise enforce until blocked_until
        if identifier in self.blocked_until:
            blocked_when = self.blocked_at.get(identifier, self.blocked_until[identifier])
            if current_time - blocked_when >= self.window_size:
                self.blocked_until.pop(identifier, None)
                self.blocked_at.pop(identifier, None)
            else:
                if current_time < self.blocked_until[identifier]:
                    remaining = self.blocked_until[identifier] - current_time
                    return False, {
                        "allowed": False,
                        "reason": "blocked",
                        "blocked_until": self.blocked_until[identifier],
                        "retry_after_seconds": remaining,
                    }
                self.blocked_until.pop(identifier, None)
                self.blocked_at.pop(identifier, None)

        # Slide window
        request_times = self.requests[identifier]
        cutoff_time = current_time - self.window_size
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()

        current_count = len(request_times)
        if current_count >= limit:
            self.blocked_until[identifier] = current_time + (15 * 60)
            self.blocked_at[identifier] = current_time
            return False, {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "current_count": current_count,
                "limit": limit,
                "window_size_seconds": self.window_size,
                "blocked_until": self.blocked_until[identifier],
                "retry_after_seconds": 15 * 60,
            }

        request_times.append(current_time)
        return True, {
            "allowed": True,
            "current_count": current_count + 1,
            "limit": limit,
            "remaining": limit - (current_count + 1),
            "window_size_seconds": self.window_size,
            "reset_time": current_time + self.window_size,
        }


class RedisRateLimiter:
    """Redis-backed distributed rate limiter"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_limiter = SlidingWindowCounter()

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis rate limiter initialized successfully")
        except Exception as e:
            logger.warning(f"Redis rate limiter initialization failed: {e}. Using in-memory fallback.")
            self.redis_client = None

    async def is_allowed(self, identifier: str, limit: int, window_seconds: int = 60) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed with Redis sliding window"""

        if self.redis_client is None:
            # Fall back to in-memory limiter
            return self.fallback_limiter.is_allowed(identifier, limit, time.time())

        try:
            current_time = time.time()
            window_key = f"rate_limit:{identifier}:{window_seconds}"

            # Use Redis pipeline for atomicity
            pipe = self.redis_client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(window_key, 0, current_time - window_seconds)

            # Count current entries
            pipe.zcard(window_key)

            # Add current request
            pipe.zadd(window_key, {str(current_time): current_time})

            # Set expiration
            pipe.expire(window_key, window_seconds * 2)

            results = await pipe.execute()
            current_count = results[1]

            if current_count >= limit:
                # Remove the request we just added since it's not allowed
                await self.redis_client.zrem(window_key, str(current_time))

                return False, {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "current_count": current_count,
                    "limit": limit,
                    "window_size_seconds": window_seconds,
                    "retry_after_seconds": window_seconds,
                    "backend": "redis",
                }

            return True, {
                "allowed": True,
                "current_count": current_count + 1,
                "limit": limit,
                "remaining": limit - (current_count + 1),
                "window_size_seconds": window_seconds,
                "reset_time": current_time + window_seconds,
                "backend": "redis",
            }

        except RedisError as e:
            logger.warning(f"Redis rate limiter error: {e}. Falling back to in-memory.")
            return self.fallback_limiter.is_allowed(identifier, limit)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""

    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_limiter = RedisRateLimiter(redis_url) if redis_url else None
        self.memory_limiter = SlidingWindowCounter()
        self.endpoint_limits = EndpointLimits()
        self.initialized = False

        # Endpoint patterns and their corresponding limits
        self.endpoint_patterns = {
            # Health endpoints
            r"/health.*": self.endpoint_limits.health_endpoints,
            r"/metrics": self.endpoint_limits.health_endpoints,
            # Admin endpoints
            r"/admin.*": self.endpoint_limits.admin_endpoints,
            r"/circuit-breakers.*": self.endpoint_limits.admin_endpoints,
            # Reasoning endpoints
            r"/reasoning.*": self.endpoint_limits.reasoning_endpoints,
            r"/msa.*": self.endpoint_limits.reasoning_endpoints,
            r"/execute.*": self.endpoint_limits.reasoning_endpoints,
            # Public endpoints (default)
            r".*": self.endpoint_limits.public_endpoints,
        }

    async def initialize_if_needed(self):
        """Initialize Redis limiter if configured"""
        if not self.initialized and self.redis_limiter:
            await self.redis_limiter.initialize()
            self.initialized = True

    def get_client_identifier(self, request: Request) -> Tuple[str, str]:
        """Extract client identifier for rate limiting"""

        # Try API key first (from header or query param)
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        if api_key:
            # Hash API key for privacy
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"api_key:{api_key_hash}", "api_key"

        # Try user ID from authentication context
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}", "user"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use first IP in chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}", "ip"

    def get_endpoint_limits(self, path: str) -> RateLimitRule:
        """Get rate limits for specific endpoint"""
        import re

        for pattern, limits in self.endpoint_patterns.items():
            if re.match(pattern, path):
                return limits

        # Default to public endpoint limits
        return self.endpoint_limits.public_endpoints

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""

        # Initialize Redis if needed
        await self.initialize_if_needed()

        # Skip rate limiting for certain internal requests
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)

        # Get client identifier
        client_id, id_type = self.get_client_identifier(request)

        # Get rate limits for this endpoint
        limits = self.get_endpoint_limits(request.url.path)

        # Check rate limit (using per-minute limit for this example)
        limiter = self.redis_limiter if self.redis_limiter and self.redis_limiter.redis_client else self.memory_limiter

        if isinstance(limiter, RedisRateLimiter):
            allowed, info = await limiter.is_allowed(client_id, limits.requests_per_minute, 60)
        else:
            allowed, info = limiter.is_allowed(client_id, limits.requests_per_minute)

        if not allowed:
            # Log rate limit violation
            logger.warning(
                f"Rate limit exceeded for {id_type}",
                client_id=client_id,
                path=request.url.path,
                method=request.method,
                info=info,
            )

            # Return rate limit error
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "type": "rate_limit_error",
                    "details": {
                        "limit": info.get("limit"),
                        "current_count": info.get("current_count"),
                        "window_size_seconds": info.get("window_size_seconds"),
                        "retry_after_seconds": info.get("retry_after_seconds"),
                        "identifier_type": id_type,
                    },
                },
                headers={
                    "Retry-After": str(int(info.get("retry_after_seconds", 60))),
                    "X-RateLimit-Limit": str(info.get("limit", 0)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(info.get("reset_time", time.time() + 60))),
                },
            )

        # Request is allowed, add rate limit headers
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(int(info.get("reset_time", time.time() + 60)))
        response.headers["X-RateLimit-Backend"] = info.get("backend", "memory")

        return response


# Factory function for easy middleware setup
def create_rate_limit_middleware(redis_url: Optional[str] = None) -> RateLimitMiddleware:
    """Create configured rate limiting middleware"""
    return RateLimitMiddleware(app=None, redis_url=redis_url)


# Rate limiting decorators for specific functions
def rate_limit(requests_per_minute: int = 60, requests_per_hour: int = 1000):
    """Decorator for function-level rate limiting"""

    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            # This would integrate with the middleware system
            # For now, it's a placeholder for future implementation
            return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            # This would integrate with the middleware system
            # For now, it's a placeholder for future implementation
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
