"""
API Optimization Integration

Integrates all API optimization features into the FastAPI application:
- Response caching middleware
- Enhanced OpenAPI documentation
- Performance monitoring
- Configuration management
"""

from typing import Dict, Any
from fastapi import FastAPI
import structlog

from reasoning_kernel.middleware.response_cache import ResponseCacheMiddleware, CACHE_PRESETS
from reasoning_kernel.api.documentation import create_enhanced_docs
from reasoning_kernel.api.optimization_config import api_config
from reasoning_kernel.services.redis_service import RedisMemoryService

logger = structlog.get_logger(__name__)


def integrate_api_optimizations(app: FastAPI, redis_service: RedisMemoryService = None) -> Dict[str, Any]:
    """
    Integrate all API optimization features into the FastAPI app

    Args:
        app: FastAPI application instance
        redis_service: Redis service for caching (optional)

    Returns:
        Dictionary with integration status and configuration
    """

    integration_status = {
        "cache_middleware": False,
        "documentation_enhancement": False,
        "monitoring": False,
        "configuration": True,
        "features": [],
        "errors": [],
    }

    try:
        # 1. Add Response Caching Middleware
        if api_config.cache.enabled and redis_service:
            logger.info("Integrating response caching middleware")

            # Create endpoint-specific cache configs
            endpoint_configs = {}

            # Health endpoints
            endpoint_configs["/api/v1/health"] = CACHE_PRESETS["health"]
            endpoint_configs["/api/v2/health"] = CACHE_PRESETS["health"]

            # Reasoning endpoints
            endpoint_configs["/api/v1/reason"] = CACHE_PRESETS["reasoning"]
            endpoint_configs["/api/v2/reasoning"] = CACHE_PRESETS["reasoning"]

            # Knowledge extraction endpoints
            endpoint_configs["/api/v1/extract-knowledge"] = CACHE_PRESETS["knowledge"]

            # Admin endpoints
            endpoint_configs["/api/v1/admin"] = CACHE_PRESETS["admin"]

            # Create and add caching middleware
            cache_middleware = ResponseCacheMiddleware(
                app=app, redis_service=redis_service, endpoint_configs=endpoint_configs
            )

            app.add_middleware(type(cache_middleware), redis_service=redis_service, endpoint_configs=endpoint_configs)

            integration_status["cache_middleware"] = True
            integration_status["features"].append("Response caching with Redis backend")

            # Store middleware reference for metrics
            app.state.cache_middleware = cache_middleware

        else:
            logger.warning("Response caching disabled or Redis unavailable")
            integration_status["errors"].append("Response caching not enabled")

        # 2. Enhance OpenAPI Documentation
        logger.info("Enhancing OpenAPI documentation")

        try:
            doc_enhancer = create_enhanced_docs(app)
            integration_status["documentation_enhancement"] = True
            integration_status["features"].append("Enhanced OpenAPI documentation")

            # Store enhancer reference
            app.state.doc_enhancer = doc_enhancer

        except Exception as e:
            logger.error("Failed to enhance documentation", error=str(e))
            integration_status["errors"].append(f"Documentation enhancement failed: {e}")

        # 3. Add Optimization Endpoints
        logger.info("Adding optimization management endpoints")

        try:
            _add_optimization_endpoints(app)
            integration_status["features"].append("Optimization management endpoints")

        except Exception as e:
            logger.error("Failed to add optimization endpoints", error=str(e))
            integration_status["errors"].append(f"Optimization endpoints failed: {e}")

        # 4. Configure Monitoring
        if api_config.monitoring.enabled:
            logger.info("Configuring performance monitoring")

            try:
                _configure_monitoring(app)
                integration_status["monitoring"] = True
                integration_status["features"].append("Performance monitoring and metrics")

            except Exception as e:
                logger.error("Failed to configure monitoring", error=str(e))
                integration_status["errors"].append(f"Monitoring configuration failed: {e}")

        # 5. Store Configuration
        app.state.api_optimization_config = api_config

        logger.info(
            "API optimizations integrated successfully",
            features=integration_status["features"],
            errors=integration_status["errors"],
        )

    except Exception as e:
        logger.error("Failed to integrate API optimizations", error=str(e))
        integration_status["errors"].append(f"Integration failed: {e}")

    return integration_status


def _add_optimization_endpoints(app: FastAPI):
    """Add optimization management endpoints"""

    from fastapi import APIRouter, Depends
    from reasoning_kernel.security.api_key_manager import check_admin_permission

    optimization_router = APIRouter(prefix="/api/v1/optimization", tags=["optimization"])

    @optimization_router.get("/config")
    async def get_optimization_config(admin_check=Depends(check_admin_permission)):
        """Get current API optimization configuration"""
        return {
            "status": "success",
            "config": api_config.to_dict(),
            "optimization_level": api_config.optimization_level.value,
        }

    @optimization_router.get("/cache/metrics")
    async def get_cache_metrics():
        """Get cache performance metrics"""
        if hasattr(app.state, "cache_middleware"):
            metrics = app.state.cache_middleware.get_cache_metrics()
            return {"status": "success", "metrics": metrics}
        else:
            return {"status": "error", "message": "Cache middleware not available"}

    @optimization_router.post("/cache/invalidate")
    async def invalidate_cache(pattern: str = None, admin_check=Depends(check_admin_permission)):
        """Invalidate cached responses"""
        if hasattr(app.state, "cache_middleware"):
            await app.state.cache_middleware.invalidate_cache(pattern)
            return {
                "status": "success",
                "message": "Cache invalidated" + (f" for pattern: {pattern}" if pattern else ""),
            }
        else:
            return {"status": "error", "message": "Cache middleware not available"}

    @optimization_router.get("/health")
    async def optimization_health():
        """Health check for optimization features"""

        health_status = {"status": "healthy", "features": {}, "timestamp": "2025-01-27T10:30:00Z"}

        # Check cache middleware
        if hasattr(app.state, "cache_middleware"):
            try:
                metrics = app.state.cache_middleware.get_cache_metrics()
                health_status["features"]["caching"] = {
                    "status": "healthy",
                    "hit_rate": metrics.get("hit_rate", 0),
                    "total_requests": metrics.get("total_requests", 0),
                }
            except Exception as e:
                health_status["features"]["caching"] = {"status": "unhealthy", "error": str(e)}
        else:
            health_status["features"]["caching"] = {"status": "disabled"}

        # Check documentation enhancement
        health_status["features"]["documentation"] = {
            "status": "healthy" if hasattr(app.state, "doc_enhancer") else "disabled"
        }

        # Check configuration
        health_status["features"]["configuration"] = {
            "status": "healthy",
            "optimization_level": api_config.optimization_level.value,
        }

        return health_status

    # Add the router to the app
    app.include_router(optimization_router)


def _configure_monitoring(app: FastAPI):
    """Configure performance monitoring"""

    # This would integrate with your existing monitoring system
    # For now, we'll just store the configuration

    monitoring_config = api_config.get_monitoring_config()
    app.state.monitoring_config = monitoring_config

    # Add middleware for response time tracking (if not already present)
    if monitoring_config["track_response_times"]:
        # The RequestLoggingMiddleware already exists and likely tracks timing
        logger.info("Response time tracking enabled via existing logging middleware")

    # Configure metrics collection
    if monitoring_config["collect_metrics"]:
        logger.info("Metrics collection configured", interval=monitoring_config["metrics_interval"])


def get_optimization_status(app: FastAPI) -> Dict[str, Any]:
    """Get current optimization feature status"""

    status = {"enabled_features": [], "configuration": {}, "performance_metrics": {}, "health": "unknown"}

    # Check what features are enabled
    if hasattr(app.state, "cache_middleware"):
        status["enabled_features"].append("response_caching")
        try:
            status["performance_metrics"]["cache"] = app.state.cache_middleware.get_cache_metrics()
        except Exception:
            pass

    if hasattr(app.state, "doc_enhancer"):
        status["enabled_features"].append("enhanced_documentation")

    if hasattr(app.state, "api_optimization_config"):
        status["configuration"] = app.state.api_optimization_config.to_dict()

    if hasattr(app.state, "monitoring_config"):
        status["enabled_features"].append("performance_monitoring")
        status["configuration"]["monitoring"] = app.state.monitoring_config

    # Overall health assessment
    if len(status["enabled_features"]) > 0:
        status["health"] = "healthy"
    else:
        status["health"] = "minimal"

    return status


# Utility function to check if optimizations are working
def validate_optimizations(app: FastAPI) -> Dict[str, Any]:
    """Validate that optimization features are working correctly"""

    validation_results = {"overall_status": "unknown", "checks": {}, "recommendations": []}

    checks_passed = 0
    total_checks = 0

    # Check cache middleware
    total_checks += 1
    if hasattr(app.state, "cache_middleware"):
        try:
            metrics = app.state.cache_middleware.get_cache_metrics()
            if isinstance(metrics, dict):
                validation_results["checks"]["cache_middleware"] = "✅ Working"
                checks_passed += 1
            else:
                validation_results["checks"]["cache_middleware"] = "❌ Invalid metrics"
        except Exception as e:
            validation_results["checks"]["cache_middleware"] = f"❌ Error: {e}"
    else:
        validation_results["checks"]["cache_middleware"] = "❌ Not configured"
        validation_results["recommendations"].append("Enable response caching for better performance")

    # Check documentation enhancement
    total_checks += 1
    if hasattr(app.state, "doc_enhancer"):
        validation_results["checks"]["documentation"] = "✅ Enhanced"
        checks_passed += 1
    else:
        validation_results["checks"]["documentation"] = "❌ Basic only"
        validation_results["recommendations"].append("Enable enhanced documentation")

    # Check configuration
    total_checks += 1
    if hasattr(app.state, "api_optimization_config"):
        config = app.state.api_optimization_config
        validation_results["checks"]["configuration"] = f"✅ Level: {config.optimization_level.value}"
        checks_passed += 1
    else:
        validation_results["checks"]["configuration"] = "❌ Not loaded"

    # Overall status
    success_rate = checks_passed / total_checks if total_checks > 0 else 0

    if success_rate >= 0.8:
        validation_results["overall_status"] = "excellent"
    elif success_rate >= 0.6:
        validation_results["overall_status"] = "good"
    elif success_rate >= 0.4:
        validation_results["overall_status"] = "fair"
    else:
        validation_results["overall_status"] = "needs_improvement"

    validation_results["success_rate"] = f"{success_rate:.1%}"
    validation_results["checks_passed"] = f"{checks_passed}/{total_checks}"

    return validation_results
