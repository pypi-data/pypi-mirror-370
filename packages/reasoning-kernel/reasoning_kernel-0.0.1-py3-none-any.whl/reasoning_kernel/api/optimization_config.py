"""
API Optimization Configuration

Centralized configuration for all API optimization features:
- Response caching settings
- Rate limiting configuration
- Request batching parameters
- Performance monitoring
- Documentation enhancement
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Set
import os


class OptimizationLevel(str, Enum):
    """API optimization levels"""

    MINIMAL = "minimal"  # Basic optimizations only
    BALANCED = "balanced"  # Recommended for most use cases
    AGGRESSIVE = "aggressive"  # Maximum performance optimizations
    CUSTOM = "custom"  # Custom configuration


@dataclass
class CacheSettings:
    """Cache configuration settings"""

    enabled: bool = True
    default_ttl: int = 300  # 5 minutes
    compress_responses: bool = True
    compression_threshold: int = 1024  # bytes

    # TTL settings per endpoint type
    health_ttl: int = 60  # 1 minute
    reasoning_ttl: int = 600  # 10 minutes
    knowledge_ttl: int = 900  # 15 minutes
    admin_ttl: int = 30  # 30 seconds

    # Request deduplication
    enable_deduplication: bool = True
    deduplication_window: int = 5  # seconds

    # Cache warming
    enable_warming: bool = False
    warm_popular_endpoints: bool = True


@dataclass
class RateLimitSettings:
    """Rate limiting configuration"""

    enabled: bool = True

    # Global limits
    global_requests_per_minute: int = 1000
    global_requests_per_hour: int = 10000

    # Per-endpoint limits (requests per minute)
    health_limit: int = 1000
    reasoning_limit: int = 30
    knowledge_limit: int = 100
    admin_limit: int = 100

    # Burst allowance (multiplier of base limit)
    burst_multiplier: float = 1.5

    # Block duration when limit exceeded (minutes)
    block_duration: int = 15

    # Rate limiting strategy
    use_sliding_window: bool = True
    use_token_bucket: bool = False


@dataclass
class BatchingSettings:
    """Request batching configuration"""

    enabled: bool = True
    max_batch_size: int = 10
    max_wait_time: float = 0.1  # 100ms

    # Endpoints that support batching
    batchable_endpoints: Set[str] = field(
        default_factory=lambda: {"/api/v1/extract-knowledge", "/api/v2/knowledge/extract"}
    )


@dataclass
class AsyncSettings:
    """Async optimization settings"""

    # Connection pooling
    max_connections: int = 100
    max_connections_per_host: int = 20
    connection_timeout: float = 10.0
    read_timeout: float = 30.0

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_multiplier: float = 2.0

    # Timeout settings
    default_timeout: float = 30.0
    reasoning_timeout: float = 60.0
    batch_timeout: float = 120.0

    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60.0


@dataclass
class MonitoringSettings:
    """Performance monitoring configuration"""

    enabled: bool = True
    collect_metrics: bool = True
    metrics_interval: int = 60  # seconds

    # Response time tracking
    track_response_times: bool = True
    response_time_buckets: List[float] = field(default_factory=lambda: [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0])

    # Cache metrics
    track_cache_performance: bool = True
    track_rate_limit_metrics: bool = True

    # Error tracking
    track_error_rates: bool = True
    alert_on_high_error_rate: bool = True
    error_rate_threshold: float = 0.05  # 5%


@dataclass
class CompressionSettings:
    """Response compression configuration"""

    enabled: bool = True
    compression_level: int = 6  # gzip compression level (1-9)
    min_size: int = 1024  # minimum response size to compress

    # MIME types to compress
    compressible_types: Set[str] = field(
        default_factory=lambda: {"application/json", "text/plain", "text/html", "application/xml", "text/xml"}
    )


@dataclass
class SecuritySettings:
    """API security optimization settings"""

    # Request validation
    strict_validation: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB

    # Headers
    security_headers: bool = True
    cors_enabled: bool = True

    # API key settings
    api_key_cache_ttl: int = 300  # 5 minutes
    validate_ip_whitelist: bool = True


class APIOptimizationConfig:
    """Centralized API optimization configuration"""

    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.BALANCED):
        self.optimization_level = optimization_level
        self.cache = CacheSettings()
        self.rate_limiting = RateLimitSettings()
        self.batching = BatchingSettings()
        self.async_settings = AsyncSettings()
        self.monitoring = MonitoringSettings()
        self.compression = CompressionSettings()
        self.security = SecuritySettings()

        # Apply optimization level presets
        self._apply_optimization_level()

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _apply_optimization_level(self):
        """Apply settings based on optimization level"""

        if self.optimization_level == OptimizationLevel.MINIMAL:
            # Minimal optimizations - focus on stability
            self.cache.enabled = True
            self.cache.default_ttl = 60
            self.cache.compress_responses = False
            self.cache.enable_deduplication = False
            self.cache.enable_warming = False

            self.rate_limiting.enabled = True
            self.rate_limiting.reasoning_limit = 10  # Conservative

            self.batching.enabled = False
            self.compression.enabled = False

        elif self.optimization_level == OptimizationLevel.BALANCED:
            # Balanced - good performance with reasonable resource usage
            # Use default settings (already configured above)
            pass

        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            # Aggressive optimizations - maximum performance
            self.cache.default_ttl = 900  # 15 minutes
            self.cache.reasoning_ttl = 1800  # 30 minutes
            self.cache.enable_deduplication = True
            self.cache.enable_warming = True

            self.rate_limiting.reasoning_limit = 60  # Higher limit
            self.rate_limiting.knowledge_limit = 200
            self.rate_limiting.burst_multiplier = 2.0

            self.batching.enabled = True
            self.batching.max_batch_size = 20

            self.compression.enabled = True
            self.compression.compression_level = 9  # Maximum compression

            self.async_settings.max_connections = 200
            self.async_settings.max_connections_per_host = 50

    def _apply_env_overrides(self):
        """Apply environment variable overrides"""

        # Cache settings
        cache_enabled = os.getenv("API_CACHE_ENABLED")
        if cache_enabled:
            self.cache.enabled = cache_enabled.lower() == "true"

        cache_ttl = os.getenv("API_CACHE_DEFAULT_TTL")
        if cache_ttl:
            self.cache.default_ttl = int(cache_ttl)

        # Rate limiting
        rate_limit_enabled = os.getenv("API_RATE_LIMIT_ENABLED")
        if rate_limit_enabled:
            self.rate_limiting.enabled = rate_limit_enabled.lower() == "true"

        reasoning_limit = os.getenv("API_REASONING_RATE_LIMIT")
        if reasoning_limit:
            self.rate_limiting.reasoning_limit = int(reasoning_limit)

        # Batching
        batching_enabled = os.getenv("API_BATCHING_ENABLED")
        if batching_enabled:
            self.batching.enabled = batching_enabled.lower() == "true"

        batch_size = os.getenv("API_BATCH_SIZE")
        if batch_size:
            self.batching.max_batch_size = int(batch_size)

        # Compression
        compression_enabled = os.getenv("API_COMPRESSION_ENABLED")
        if compression_enabled:
            self.compression.enabled = compression_enabled.lower() == "true"

    def get_endpoint_cache_config(self, path: str) -> Dict[str, Any]:
        """Get cache configuration for specific endpoint"""

        if not self.cache.enabled:
            return {"enabled": False}

        # Determine TTL based on endpoint type
        ttl = self.cache.default_ttl

        if "/health" in path:
            ttl = self.cache.health_ttl
        elif "/reason" in path or "/reasoning" in path:
            ttl = self.cache.reasoning_ttl
        elif "/extract-knowledge" in path or "/knowledge" in path:
            ttl = self.cache.knowledge_ttl
        elif "/admin" in path:
            ttl = self.cache.admin_ttl

        return {
            "enabled": True,
            "ttl": ttl,
            "compress": self.cache.compress_responses,
            "compression_threshold": self.cache.compression_threshold,
            "deduplicate": self.cache.enable_deduplication,
        }

    def get_endpoint_rate_limit(self, path: str) -> Dict[str, Any]:
        """Get rate limit configuration for specific endpoint"""

        if not self.rate_limiting.enabled:
            return {"enabled": False}

        # Determine limit based on endpoint type
        limit = self.rate_limiting.global_requests_per_minute

        if "/health" in path:
            limit = self.rate_limiting.health_limit
        elif "/reason" in path or "/reasoning" in path:
            limit = self.rate_limiting.reasoning_limit
        elif "/extract-knowledge" in path or "/knowledge" in path:
            limit = self.rate_limiting.knowledge_limit
        elif "/admin" in path:
            limit = self.rate_limiting.admin_limit

        return {
            "enabled": True,
            "requests_per_minute": limit,
            "burst_allowance": int(limit * self.rate_limiting.burst_multiplier),
            "block_duration": self.rate_limiting.block_duration,
        }

    def is_endpoint_batchable(self, path: str) -> bool:
        """Check if endpoint supports batching"""
        return self.batching.enabled and path in self.batching.batchable_endpoints

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            "enabled": self.monitoring.enabled,
            "collect_metrics": self.monitoring.collect_metrics,
            "metrics_interval": self.monitoring.metrics_interval,
            "track_response_times": self.monitoring.track_response_times,
            "response_time_buckets": self.monitoring.response_time_buckets,
            "track_cache_performance": self.monitoring.track_cache_performance,
            "track_rate_limit_metrics": self.monitoring.track_rate_limit_metrics,
            "track_error_rates": self.monitoring.track_error_rates,
            "error_rate_threshold": self.monitoring.error_rate_threshold,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "optimization_level": self.optimization_level.value,
            "cache": {
                "enabled": self.cache.enabled,
                "default_ttl": self.cache.default_ttl,
                "compress_responses": self.cache.compress_responses,
                "enable_deduplication": self.cache.enable_deduplication,
                "enable_warming": self.cache.enable_warming,
            },
            "rate_limiting": {
                "enabled": self.rate_limiting.enabled,
                "reasoning_limit": self.rate_limiting.reasoning_limit,
                "knowledge_limit": self.rate_limiting.knowledge_limit,
                "burst_multiplier": self.rate_limiting.burst_multiplier,
            },
            "batching": {
                "enabled": self.batching.enabled,
                "max_batch_size": self.batching.max_batch_size,
                "max_wait_time": self.batching.max_wait_time,
            },
            "compression": {
                "enabled": self.compression.enabled,
                "compression_level": self.compression.compression_level,
                "min_size": self.compression.min_size,
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "collect_metrics": self.monitoring.collect_metrics,
                "metrics_interval": self.monitoring.metrics_interval,
            },
        }


# Global configuration instance
def get_api_optimization_level() -> OptimizationLevel:
    """Get optimization level from environment"""
    level_str = os.getenv("API_OPTIMIZATION_LEVEL", "balanced").lower()

    level_map = {
        "minimal": OptimizationLevel.MINIMAL,
        "balanced": OptimizationLevel.BALANCED,
        "aggressive": OptimizationLevel.AGGRESSIVE,
        "custom": OptimizationLevel.CUSTOM,
    }

    return level_map.get(level_str, OptimizationLevel.BALANCED)


# Create global configuration instance
api_config = APIOptimizationConfig(get_api_optimization_level())
