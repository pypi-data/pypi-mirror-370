"""
Updated Kernel Manager with Redis Cloud Integration

This module provides a modernized kernel manager that uses Redis Cloud
as the unified backend for vector storage and caching.
"""

from datetime import datetime
from datetime import UTC
import logging
import os
from typing import Any, Dict, List, Optional

from reasoning_kernel.services.redis_vector_service import RedisVectorService
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding

from reasoning_kernel.core.error_handling import simple_log_error


logger = logging.getLogger(__name__)


class ModernKernelManager:
    """
    Modern Kernel Manager with Redis Cloud integration

    Features:
    - Unified Redis Cloud backend for vectors and caching
    - Modern Semantic Kernel 1.35.3+ patterns
    - Integrated vector search capabilities
    - Service registration with dependency management
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.kernel = Kernel()
        self.redis_service: Optional[RedisVectorService] = None
        self._services = {}
        self._plugins = {}
        self._initialized = False

        logger.info("Modern Kernel Manager initialized")

    async def initialize(self) -> Kernel:
        """Initialize the kernel with all services and plugins"""
        if self._initialized:
            return self.kernel

        try:
            # 1. Initialize AI services
            await self._setup_ai_services()

            # 2. Initialize Redis vector service
            await self._setup_redis_service()

            # 3. Register core plugins
            await self._register_plugins()

            self._initialized = True
            logger.info("Modern Kernel Manager fully initialized")

            return self.kernel

        except Exception as e:
            simple_log_error(logger, "initialize_kernel", e)
            raise

    async def _setup_ai_services(self):
        """Set up AI services (Chat Completion and Embeddings)"""
        # Chat completion service
        chat_service = OpenAIChatCompletion(
            ai_model_id=self.config.get("openai_model_id", "gpt-4"), api_key=self.config["openai_api_key"]
        )
        self.kernel.add_service(chat_service)
        self._services["chat_completion"] = chat_service

        # Embedding service - currently only OpenAI supported
        embedding_model = self.config.get("embedding_model_id", "text-embedding-3-small")

        # Use OpenAI embeddings (Google AI embeddings require additional setup)
        embedding_service = OpenAITextEmbedding(ai_model_id=embedding_model, api_key=self.config["openai_api_key"])

        self.kernel.add_service(embedding_service)
        self._services["embeddings"] = embedding_service

        logger.info("AI services configured: OpenAI chat completion and embedding services initialized")

    async def _setup_redis_service(self):
        """Set up Redis vector service"""
        redis_connection = self.config.get("redis_url") or os.environ.get("REDIS_URL")

        if not redis_connection:
            logger.warning("No Redis connection string provided - vector storage disabled")
            return

        # Initialize Redis vector service with embedding generator
        embeddings_service = self._services.get("embeddings")
        if not embeddings_service:
            logger.warning("No embeddings service available for Redis vector service")
            return

        self.redis_service = RedisVectorService(
            connection_string=redis_connection, embedding_generator=embeddings_service
        )

        # Initialize Redis collections
        await self.redis_service.initialize()

        logger.info("Redis vector service initialized")

    async def _register_plugins(self):
        """Register core plugins with the kernel"""
        try:
            # 1. Conversation Summary Plugin (modern pattern)
            # Skip for now - requires prompt template configuration
            logger.info("Skipping ConversationSummaryPlugin - requires additional configuration")

            # 2. Register reasoning plugins if available
            await self._register_reasoning_plugins()

            logger.info(f"Registered {len(self._plugins)} plugins")

        except Exception as e:
            simple_log_error(logger, "register_plugins", e)
            # Don't fail completely - some plugins might still work

    async def _register_reasoning_plugins(self):
        """Register reasoning-specific plugins"""
        try:
            # Try to import and register reasoning plugins
            from reasoning_kernel.plugins.thinking_exploration_plugin import (
                ThinkingExplorationPlugin,
            )

            # Create plugin with kernel - let it handle its own Redis integration
            exploration_plugin = ThinkingExplorationPlugin(kernel=self.kernel)

            self.kernel.add_plugin(exploration_plugin, "ThinkingExploration")
            self._plugins["thinking_exploration"] = exploration_plugin

            logger.info("Reasoning plugins registered successfully")

        except ImportError as e:
            logger.info(f"Reasoning plugins not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to register reasoning plugins: {e}")

    # Vector operations using Redis service
    async def store_reasoning_pattern(
        self,
        question: str,
        reasoning_steps: str,
        final_answer: str,
        pattern_type: str = "general",
        confidence: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store a reasoning pattern in Redis vector store"""
        if not self.redis_service:
            logger.warning("Redis service not available - cannot store reasoning pattern")
            return None

        try:
            return await self.redis_service.store_reasoning_pattern(
                pattern_type=pattern_type,
                question=question,
                reasoning_steps=reasoning_steps,
                final_answer=final_answer,
                confidence_score=confidence,
                context=context,
            )
        except Exception as e:
            simple_log_error(logger, "store_reasoning_pattern", e)
            return None

    async def search_similar_reasoning(self, query: str, limit: int = 5) -> list:
        """Search for similar reasoning patterns"""
        if not self.redis_service:
            logger.warning("Redis service not available - cannot search patterns")
            return []

        try:
            return await self.redis_service.similarity_search(
                collection_name="reasoning", query_text=query, limit=limit
            )
        except Exception as e:
            simple_log_error(logger, "search_reasoning_patterns", e)
            return []

    async def store_world_model(
        self,
        model_type: str,
        state_data: Dict[str, Any],
        confidence: float = 0.0,
        context_keys: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Store a world model in Redis vector store"""
        if not self.redis_service:
            logger.warning("Redis service not available - cannot store world model")
            return None

        try:
            return await self.redis_service.store_world_model(
                model_type=model_type, state_data=state_data, confidence=confidence, context_keys=context_keys
            )
        except Exception as e:
            simple_log_error(logger, "store_world_model", e)
            return None

    # Service access methods
    def get_chat_service(self):
        """Get the chat completion service"""
        return self._services.get("chat_completion")

    def get_embedding_service(self):
        """Get the embedding service"""
        return self._services.get("embeddings")

    def get_redis_service(self) -> Optional[RedisVectorService]:
        """Get the Redis vector service"""
        return self.redis_service

    def get_plugin(self, plugin_name: str):
        """Get a registered plugin by name"""
        return self._plugins.get(plugin_name)

    # Utility methods
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            "timestamp": datetime.now(UTC).isoformat(),
            "kernel_initialized": self._initialized,
            "services": list(self._services.keys()),
            "plugins": list(self._plugins.keys()),
        }

        # Add Redis stats if available
        if self.redis_service:
            try:
                redis_stats = {}
                # Get stats for each collection
                for collection_name in ["reasoning", "world_models", "explorations"]:
                    collection_stats = await self.redis_service.get_collection_stats(collection_name)
                    redis_stats[collection_name] = collection_stats
                stats["redis_collections"] = redis_stats
            except Exception as e:
                stats["redis_error"] = str(e)

        return stats

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of all services"""
        health = {"timestamp": datetime.now(UTC).isoformat(), "overall_status": "unknown", "services": {}}

        # Check kernel
        health["services"]["kernel"] = {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
        }

        # Check Redis service
        if self.redis_service:
            try:
                health_check = await self.redis_service.health_check()
                health["services"]["redis"] = {
                    "status": health_check.get("status", "unknown"),
                    "collections": health_check.get("collections", []),
                }
            except Exception as e:
                health["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        else:
            health["services"]["redis"] = {"status": "disabled", "reason": "No Redis connection configured"}

        # Determine overall status
        service_statuses = [s.get("status") for s in health["services"].values()]
        if all(s == "healthy" for s in service_statuses if s not in ["disabled"]):
            health["overall_status"] = "healthy"
        elif any(s == "unhealthy" for s in service_statuses):
            health["overall_status"] = "unhealthy"
        else:
            health["overall_status"] = "degraded"

        return health

    async def close(self):
        """Clean up resources"""
        try:
            if self.redis_service:
                await self.redis_service.close()

            self._services.clear()
            self._plugins.clear()
            self._initialized = False

            logger.info("Modern Kernel Manager closed")

        except Exception as e:
            simple_log_error(logger, "close_kernel_manager", e)

    def __del__(self):
        """Cleanup on object destruction"""
        if hasattr(self, "_initialized") and self._initialized:
            logger.warning("ModernKernelManager was not explicitly closed")


# Factory functions for easy instantiation
def create_redis_kernel(
    openai_api_key: str,
    redis_url: str,
    openai_model_id: str = "gpt-4",
    embedding_model_id: str = "text-embedding-3-small",
    **kwargs,
) -> ModernKernelManager:
    """
    Factory function to create a kernel with Redis Cloud backend

    Args:
        openai_api_key: OpenAI API key
        redis_url: Redis Cloud connection string
        openai_model_id: OpenAI model for chat completion
        embedding_model_id: Model for embeddings
        **kwargs: Additional configuration

    Returns:
        Configured ModernKernelManager
    """
    config = {
        "openai_api_key": openai_api_key,
        "redis_url": redis_url,
        "openai_model_id": openai_model_id,
        "embedding_model_id": embedding_model_id,
        **kwargs,
    }

    return ModernKernelManager(config)


def create_google_redis_kernel(
    google_api_key: str,
    openai_api_key: str,
    redis_url: str,
    openai_model_id: str = "gpt-4",
    google_embedding_model: str = "models/text-embedding-004",
    **kwargs,
) -> ModernKernelManager:
    """
    Factory function to create a kernel with Google embeddings and Redis backend

    Args:
        google_api_key: Google AI API key
        openai_api_key: OpenAI API key for chat
        redis_url: Redis Cloud connection string
        openai_model_id: OpenAI model for chat completion
        google_embedding_model: Google model for embeddings
        **kwargs: Additional configuration

    Returns:
        Configured ModernKernelManager
    """
    config = {
        "openai_api_key": openai_api_key,
        "google_api_key": google_api_key,
        "redis_url": redis_url,
        "openai_model_id": openai_model_id,
        "embedding_model_id": google_embedding_model,
        **kwargs,
    }

    return ModernKernelManager(config)
