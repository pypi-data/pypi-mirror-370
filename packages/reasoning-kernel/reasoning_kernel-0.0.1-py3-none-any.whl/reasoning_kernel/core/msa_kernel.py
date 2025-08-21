"""
MSA Kernel - Dedicated Semantic Kernel configuration for Model Synthesis Architecture

This module provides a specialized kernel configuration optimized for MSA operations,
including proper service registration, memory store integration, and plugin management.
"""

import logging
from typing import Any, Dict, Optional

from reasoning_kernel.adapters.simple_redis_memory_adapter import (
    SimpleRedisMemoryAdapter,
)
from reasoning_kernel.core.settings import settings
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.core_plugins import MathPlugin
from semantic_kernel.core_plugins import TimePlugin
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory

from reasoning_kernel.core.error_handling import simple_log_error


logger = logging.getLogger(__name__)


class MSAKernelConfig:
    """Configuration class for MSA Kernel setup"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Service configuration - use centralized settings with config override
        self.chat_model_id = self.config.get("chat_model_id", settings.openai_model)
        self.embedding_model_id = self.config.get("embedding_model_id", settings.openai_embedding_model)

        # API keys from centralized settings with config override
        self.openai_api_key = self.config.get("openai_api_key") or settings.openai_api_key
        self.google_api_key = self.config.get("google_api_key") or settings.google_api_key

        # Redis configuration from centralized settings
        self.redis_url = self.config.get("redis_url") or settings.redis_url
        self.redis_index_name = self.config.get("redis_index_name", "msa-knowledge-base")

        # MSA-specific settings from centralized configuration
        self.enable_memory = self.config.get("enable_memory", settings.enable_memory)
        self.enable_plugins = self.config.get("enable_plugins", settings.enable_plugins)
        self.memory_collection_name = self.config.get("memory_collection_name", settings.redis_memory_collection)


class MSAKernel:
    """
    Specialized Semantic Kernel for Model Synthesis Architecture

    Features:
    - Optimized for MSA workflow stages
    - Redis memory store integration
    - Core SK plugins (Math, Time, Text)
    - Service management for chat completion and embeddings
    - MSA-specific configurations
    """

    def __init__(self, config: Optional[MSAKernelConfig] = None):
        self.config = config or MSAKernelConfig()
        self.kernel = Kernel()
        self.memory: Optional[SemanticTextMemory] = None

        # Service tracking
        self._chat_service = None
        self._embedding_service = None
        self._redis_service = None

        # Initialization state
        self._initialized = False
        self._plugins_registered = False

        logger.info("MSAKernel initialized with configuration")

    async def initialize(self) -> Kernel:
        """Initialize the MSA kernel with all required services"""
        if self._initialized:
            return self.kernel

        try:
            # Register chat completion service
            await self._register_chat_service()

            # Register embedding service
            await self._register_embedding_service()

            # Setup memory store if enabled
            if self.config.enable_memory:
                await self._setup_memory_store()

            # Register core plugins
            if self.config.enable_plugins:
                await self._register_plugins()

            self._initialized = True
            logger.info("MSAKernel successfully initialized")

            return self.kernel

        except Exception as e:
            simple_log_error(logger, "initialize_msa_kernel", e)
            raise

    async def _register_chat_service(self):
        """Register chat completion service"""
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key is required for chat completion service")

        # Use OpenAI for now - can be extended to support Google AI when available
        self._chat_service = OpenAIChatCompletion(
            service_id="msa_chat",
            ai_model_id=self.config.chat_model_id,
            api_key=self.config.openai_api_key,
        )

        self.kernel.add_service(self._chat_service)
        logger.info(f"Chat service registered: {self.config.chat_model_id}")

    async def _register_embedding_service(self):
        """Register text embedding service"""
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key is required for embedding service")

        self._embedding_service = OpenAITextEmbedding(
            service_id="msa_embeddings",
            ai_model_id=self.config.embedding_model_id,
            api_key=self.config.openai_api_key,
        )

        self.kernel.add_service(self._embedding_service)
        logger.info(f"Embedding service registered: {self.config.embedding_model_id}")

    async def _setup_memory_store(self):
        """Setup Redis memory store for knowledge retrieval"""
        try:
            # Ensure embedding service exists
            if self._embedding_service is None:
                raise ValueError("Embedding service must be initialized before memory store")

            # Ensure redis_url is not None
            redis_url = self.config.redis_url or "redis://localhost:6379"

            # Create simple Redis memory adapter
            redis_memory_adapter = SimpleRedisMemoryAdapter(redis_url=redis_url)

            # Create semantic text memory with Redis backend
            self.memory = SemanticTextMemory(
                storage=redis_memory_adapter,
                embeddings_generator=self._embedding_service,
            )

            logger.info("Memory store configured with Redis backend successfully")

        except Exception as e:
            logger.warning(f"Failed to setup Redis memory store: {e}")
            logger.info("Memory store deprecated - Vector Store abstractions recommended")

            # Memory store deprecated - use Vector Store abstractions instead
            self.memory = None

    async def _register_plugins(self):
        """Register core SK plugins for MSA operations"""
        try:
            # Math plugin for numerical computations
            math_plugin = MathPlugin()
            self.kernel.add_plugin(math_plugin, plugin_name="math")

            # Time plugin for temporal operations
            time_plugin = TimePlugin()
            self.kernel.add_plugin(time_plugin, plugin_name="time")

            self._plugins_registered = True
            logger.info("Core plugins registered: Math, Time")

        except Exception as e:
            simple_log_error(logger, "register_plugins", e)
            raise

    def get_memory(self) -> Optional[SemanticTextMemory]:
        """Get the semantic text memory instance"""
        return self.memory

    def get_kernel(self) -> Kernel:
        """Get the configured kernel instance"""
        return self.kernel

    def is_initialized(self) -> bool:
        """Check if kernel is fully initialized"""
        return self._initialized

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about registered services"""
        return {
            "chat_service": {
                "service_id": "msa_chat",
                "model_id": self.config.chat_model_id,
                "available": self._chat_service is not None,
            },
            "embedding_service": {
                "service_id": "msa_embeddings",
                "model_id": self.config.embedding_model_id,
                "available": self._embedding_service is not None,
            },
            "memory_store": {
                "type": "redis",
                "url": self.config.redis_url,
                "available": self._redis_service is not None,
            },
            "plugins": {
                "registered": self._plugins_registered,
                "available": ["math", "time"] if self._plugins_registered else [],
            },
            "initialized": self._initialized,
        }


async def create_msa_kernel(config: Optional[Dict[str, Any]] = None) -> MSAKernel:
    """
    Factory function to create and initialize an MSA kernel

    Args:
        config: Optional configuration dictionary

    Returns:
        Initialized MSAKernel instance
    """
    kernel_config = MSAKernelConfig(config)
    msa_kernel = MSAKernel(kernel_config)
    await msa_kernel.initialize()
    return msa_kernel


# For backwards compatibility and easy importing
async def create_default_msa_kernel() -> MSAKernel:
    """Create MSA kernel with default configuration"""
    return await create_msa_kernel()
