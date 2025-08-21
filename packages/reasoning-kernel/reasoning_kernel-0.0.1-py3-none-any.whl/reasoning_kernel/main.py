"""
Main FastAPI application entry point for MSA Reasoning Engine
"""

import asyncio
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from reasoning_kernel.api.admin_endpoints import router as admin_router
from reasoning_kernel.api.health_endpoints import router as health_router
from reasoning_kernel.api.memory_endpoints import router as memory_router
from reasoning_kernel.api.redis_endpoints import router as redis_router
from reasoning_kernel.core.env import load_project_dotenv

# Security imports
from reasoning_kernel.security.security_manager import SecurityConfig
from reasoning_kernel.security.security_manager import setup_security
from reasoning_kernel.security.security_manager import security_manager
import uvicorn


# Ensure environment variables are loaded from the project root .env consistently
load_project_dotenv(override=False)
# Optional routers (may not be present in all environments)
try:
    from reasoning_kernel.api.confidence_endpoints import (
        confidence_router,  # type: ignore
    )
except Exception:
    confidence_router = None  # type: ignore

try:
    from reasoning_kernel.api.annotation_endpoints import (
        router as annotation_router,
    )  # type: ignore
except Exception:
    annotation_router = None  # type: ignore

from reasoning_kernel.api.endpoints import router
from reasoning_kernel.api.model_olympics import router as model_olympics_router
from reasoning_kernel.core.config import settings
from reasoning_kernel.core.kernel_config import KernelManager
from reasoning_kernel.core.logging_config import configure_logging
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.database.connection import init_database
from reasoning_kernel.middleware.logging import RequestLoggingMiddleware
from reasoning_kernel.msa.synthesis_engine import MSAEngine
from reasoning_kernel.services.redis_service import create_redis_services


configure_logging(settings.log_level)
logger = get_logger(__name__)

# Import v2 API and reasoning kernel (with fallbacks for missing dependencies)
try:
    from reasoning_kernel.api.v2.reasoning_endpoints import router as v2_router
    from reasoning_kernel.reasoning_kernel import ReasoningConfig
    from reasoning_kernel.reasoning_kernel import ReasoningKernel

    REASONING_KERNEL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Reasoning Kernel not available due to missing dependencies: {e}")
    REASONING_KERNEL_AVAILABLE = False
    ReasoningKernel = None
    v2_router = None

# Global instances
kernel_manager = None
msa_engine = None
reasoning_kernel = None
redis_memory_service = None
redis_retrieval_service = None
db_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    global kernel_manager, msa_engine, reasoning_kernel, redis_memory_service, redis_retrieval_service, db_manager

    logger.info("🚀 Starting MSA Reasoning Engine...")

    try:
        # Initialize Security System
        logger.info("🔒 Initializing security system...")
        security_config = SecurityConfig.from_env()
        await setup_security(app, security_config)
        logger.info("✅ Security system initialized")

        # Parse Redis URL if provided
        if settings.redis_url:
            from urllib.parse import urlparse

            # Clean the Redis URL in case it contains the export command
            redis_url_clean = settings.redis_url
            if "export" in redis_url_clean and "redis://" in redis_url_clean:
                # Extract just the URL from the export command
                import re

                match = re.search(r"redis://[^\s\'\"]+", redis_url_clean)
                if match:
                    redis_url_clean = match.group(0)

            parsed = urlparse(redis_url_clean)
            redis_host = parsed.hostname or settings.redis_host
            redis_port = parsed.port or settings.redis_port
            redis_password = parsed.password or settings.redis_password
            # Extract database number from path if present (default to 0 if not specified)
            try:
                redis_db = (
                    int(parsed.path.lstrip("/"))
                    if parsed.path and parsed.path != "/" and parsed.path.lstrip("/").isdigit()
                    else settings.redis_db
                )
            except (ValueError, AttributeError):
                redis_db = settings.redis_db
            logger.info(f"Using Redis Cloud: {redis_host}:{redis_port}")
        else:
            redis_host = settings.redis_host
            redis_port = settings.redis_port
            redis_password = settings.redis_password
            redis_db = settings.redis_db

        # Initialize Redis services
        redis_memory_service, redis_retrieval_service = create_redis_services(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            ttl_seconds=settings.redis_ttl_seconds,
            max_connections=settings.redis_max_connections,
        )
        logger.info("✅ Redis services initialized")

        # Initialize PostgreSQL database
        db_manager = init_database()
        logger.info("✅ PostgreSQL database initialized")

        # Initialize Semantic Kernel
        kernel_manager = KernelManager()
        await kernel_manager.initialize()
        logger.info("✅ Semantic Kernel initialized")

        # Initialize MSA Engine with Redis services
        msa_engine = MSAEngine(
            kernel_manager,
            memory_service=redis_memory_service,
            retrieval_service=redis_retrieval_service,
        )
        await msa_engine.initialize()
        logger.info("✅ MSA Engine initialized")

        # Initialize Reasoning Kernel (v2) if available
        if REASONING_KERNEL_AVAILABLE and ReasoningKernel:
            try:
                if kernel_manager.kernel:
                    reasoning_kernel = ReasoningKernel(
                        kernel=kernel_manager.kernel,
                        redis_client=redis_memory_service,
                        config=ReasoningConfig(),
                    )
                    logger.info("✅ Reasoning Kernel (v2) initialized")

                    # Set global instance for v2 API endpoints
                    try:
                        from reasoning_kernel.api.v2 import reasoning_endpoints

                        reasoning_endpoints.reasoning_kernel = reasoning_kernel
                    except ImportError:
                        logger.warning("v2 reasoning endpoints not available")
                else:
                    logger.warning("Kernel not available, skipping Reasoning Kernel initialization")
                    reasoning_kernel = None

            except Exception as e:
                logger.warning(f"Failed to initialize Reasoning Kernel: {e}")
                reasoning_kernel = None
        else:
            logger.info("Reasoning Kernel (v2) not available - using v1 MSA Engine only")
            reasoning_kernel = None

        # Store in app state for access in endpoints
        app.state.kernel_manager = kernel_manager
        app.state.msa_engine = msa_engine
        app.state.reasoning_kernel = reasoning_kernel
        app.state.redis_memory = redis_memory_service
        app.state.redis_retrieval = redis_retrieval_service
        app.state.db_manager = db_manager
        app.state.security_manager = security_manager

        logger.info("🎯 MSA Reasoning Engine ready for requests")

    except Exception as e:
        logger.error(f"❌ Failed to initialize MSA Engine: {e}")
        raise

    yield

    # Cleanup
    logger.info("🔄 Shutting down MSA Reasoning Engine...")
    if msa_engine:
        await msa_engine.cleanup()
    if kernel_manager:
        await kernel_manager.cleanup()
    if db_manager:
        db_manager.cleanup()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Model Synthesis Architecture for dynamic AI reasoning with Semantic Kernel and NumPyro",
    version=settings.version,
    lifespan=lifespan,
)

# Note: Security middleware (CORS, rate limiting, etc.) is configured in lifespan
# via the security manager, which handles all security concerns comprehensively

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include API routes
app.include_router(router, prefix="/api/v1")

app.include_router(health_router, prefix="/api/v1")
app.include_router(redis_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(admin_router)  # Admin endpoints have their own prefix
if confidence_router is not None:
    app.include_router(confidence_router)

# Include Model Olympics endpoints (MSA paper enhancement)
app.include_router(model_olympics_router)

# Include v2 API router if available (Reasoning Kernel upgrade)
if REASONING_KERNEL_AVAILABLE and v2_router:
    app.include_router(v2_router)

    # Add Daytona endpoints to v2 API
    try:
        from reasoning_kernel.api.v2.daytona_endpoints import (
            router as daytona_router,
        )

        app.include_router(daytona_router, prefix="/api/v2")

        # Add v2 health endpoints
        from reasoning_kernel.api.v2.health_endpoints import (
            router as v2_health_router,
        )

        app.include_router(v2_health_router, prefix="/api/v2")

        # Add visualization and learning endpoints
        from reasoning_kernel.api.v2.visualization_endpoints import (
            router as v2_visualization_router,
        )

        app.include_router(v2_visualization_router, prefix="/api/v2")

        # Add probability visualization endpoints
        from reasoning_kernel.api.v2.probability_visualization_endpoints import (
            router as prob_viz_router,
        )

        app.include_router(prob_viz_router)

        # Add WebSocket streaming endpoints for real-time updates
        try:
            from reasoning_kernel.api.v2.streaming_endpoints import (
                router as streaming_router,
            )

            app.include_router(streaming_router)
            logger.info("✅ WebSocket streaming endpoints registered")
        except Exception as e:
            logger.warning(f"WebSocket streaming unavailable: {e}")

        logger.info("✅ v2 API endpoints registered (including visualization and learning)")
    except Exception as e:
        logger.info(f"✅ v2 API endpoints registered (Daytona unavailable: {e})")
else:
    logger.info("v2 API not available - only v1 endpoints active")

if annotation_router is not None:
    app.include_router(annotation_router)

# Mount static files for chat interface (serve from reasoning_kernel/static)
if os.path.exists("reasoning_kernel/static"):
    app.mount("/static", StaticFiles(directory="reasoning_kernel/static"), name="static")


@app.get("/")
async def root():
    """Root returns system info (JSON) for tests & clients."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "operational",
        "description": "Model Synthesis Architecture for dynamic AI reasoning",
        "modes": {
            "mode1": "LLM-powered knowledge retrieval (Semantic Kernel)",
            "mode2": "Dynamic probabilistic model synthesis (NumPyro)",
            "neural_synthesis": "Neurally-guided program synthesis (MSA paper enhancement)",
        },
    }


@app.get("/ui")
async def ui():
    """Serve the real-time streaming interface HTML (moved from root)"""
    return FileResponse("reasoning_kernel/static/realtime-streaming.html", media_type="text/html")


@app.get("/onboarding")
async def onboarding():
    """Serve the onboarding wizard HTML"""
    return FileResponse("reasoning_kernel/static/onboarding.html", media_type="text/html")


@app.get("/probability-visualization")
async def probability_visualization():
    """Serve the probability visualization interface"""
    return FileResponse("reasoning_kernel/static/probability-visualization.html", media_type="text/html")


@app.get("/api")
async def api_root():
    """API root endpoint with system information"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": "Model Synthesis Architecture for dynamic AI reasoning",
        "status": "operational",
        "modes": {
            "mode1": "LLM-powered knowledge retrieval (Semantic Kernel)",
            "mode2": "Dynamic probabilistic model synthesis (NumPyro)",
            "neural_synthesis": "Neurally-guided program synthesis (MSA paper enhancement)",
        },
        "features": {
            "model_olympics": "Sports vignettes for testing novel causal reasoning",
            "neural_program_synthesis": "LLM-generated probabilistic programs",
            "open_world_reasoning": "Handling completely novel scenarios",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "kernel_initialized": hasattr(app.state, "kernel_manager") and app.state.kernel_manager is not None,
        "msa_initialized": hasattr(app.state, "msa_engine") and app.state.msa_engine is not None,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with structured logging"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred while processing your request",
            "type": type(exc).__name__,
        },
    )


def main():
    """Main entry point for CLI usage"""
    from reasoning_kernel.cli import main as cli_main

    # Run the CLI
    asyncio.run(cli_main())


def run_server():
    """Run the FastAPI server"""
    uvicorn.run(
        "reasoning_kernel.main:app",
        host="0.0.0.0",
        port=5000,
        reload=os.getenv("DEVELOPMENT", "false").lower() == "true",
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
