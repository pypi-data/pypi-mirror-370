"""Kernel Manager for Semantic Kernel 1.35.3+.

Modernized to use current Semantic Kernel patterns:
- Uses InMemoryStore instead of deprecated VolatileMemoryStore
- Direct service registration with kernel.add_service()
- Removed deprecated SemanticTextMemory and TextMemoryPlugin
- Modern memory management through vector stores and embedding services
"""

import logging
from typing import Any, Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.connectors.in_memory import InMemoryStore
from semantic_kernel.core_plugins import ConversationSummaryPlugin
from semantic_kernel.core_plugins import HttpPlugin
from semantic_kernel.core_plugins import MathPlugin
from semantic_kernel.core_plugins import TextPlugin
from semantic_kernel.core_plugins import TimePlugin
from semantic_kernel.core_plugins import WebSearchEnginePlugin
from semantic_kernel.core_plugins.wait_plugin import WaitPlugin
from semantic_kernel.prompt_template.prompt_template_config import (
    PromptTemplateConfig,
)

from reasoning_kernel.core.error_handling import simple_log_error


logger = logging.getLogger(__name__)


class KernelManager:
    """Manager for Semantic Kernel initialization and configuration."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the kernel manager.

        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._kernel: Optional[Kernel] = None
        self._services: Dict[str, Any] = {}

    def create_kernel(self) -> Kernel:
        """Create and configure a new kernel instance.

        Returns:
            Configured Kernel instance
        """
        logger.info("Creating new Semantic Kernel instance")

        # Create kernel
        kernel = Kernel()

        # Register AI services
        self._register_ai_services(kernel)

        # Register memory services
        self._register_memory_services(kernel)

        # Register core plugins
        self._register_core_plugins(kernel)

        self._kernel = kernel
        logger.info("Kernel created and configured successfully")

        return kernel

    def _register_ai_services(self, kernel: Kernel) -> None:
        """Register AI services with the kernel.

        Args:
            kernel: Kernel instance
        """
        # Check for Azure OpenAI configuration
        if self._config.get("use_azure_openai"):
            service = AzureChatCompletion(
                deployment_name=self._config.get("azure_deployment_name"),
                endpoint=self._config.get("azure_endpoint"),
                api_key=self._config.get("azure_api_key"),
                api_version=self._config.get("azure_api_version", "2024-02-15-preview"),
                service_id="chat_completion",
            )
            kernel.add_service(service)
            self._services["chat_completion"] = service
            logger.info("Registered Azure OpenAI chat completion service")

        # Default to OpenAI
        elif self._config.get("openai_api_key"):
            service = OpenAIChatCompletion(
                ai_model_id=self._config.get("openai_model_id", "gpt-4"),
                api_key=self._config.get("openai_api_key"),
                org_id=self._config.get("openai_org_id"),
                service_id="chat_completion",
            )
            kernel.add_service(service)
            self._services["chat_completion"] = service
            logger.info("Registered OpenAI chat completion service")
        else:
            logger.warning("No AI service configuration found")

    def _register_memory_services(self, kernel: Kernel) -> None:
        """Register memory services with the kernel.

        Args:
            kernel: Kernel instance
        """
        # Create modern in-memory vector store
        memory_store = InMemoryStore()

        # Create embeddings service (support OpenAI and Azure OpenAI)
        embeddings_service = None
        if self._config.get("use_azure_openai") and self._config.get("azure_api_key"):
            embeddings_service = AzureTextEmbedding(
                service_id="embedding",
                deployment_name=self._config.get("azure_embedding_deployment_name", "text-embedding-3-large"),
                endpoint=self._config.get("azure_endpoint"),
                api_key=self._config.get("azure_api_key"),
                api_version=self._config.get("azure_api_version", "2024-02-15-preview"),
            )
        elif self._config.get("openai_api_key"):
            embeddings_service = OpenAITextEmbedding(
                service_id="embedding",
                ai_model_id=self._config.get("embedding_model_id", "text-embedding-3-large"),
                api_key=self._config.get("openai_api_key"),
                org_id=self._config.get("openai_org_id"),
            )

        # Register embedding service with kernel for modern usage pattern
        if embeddings_service:
            kernel.add_service(embeddings_service)

            # Store references for internal use
            self._services["memory_store"] = memory_store
            self._services["embeddings"] = embeddings_service
            logger.info("Registered modern in-memory store and embeddings services")
        else:
            logger.warning("No embedding service configuration found")

    def _register_core_plugins(self, kernel: Kernel) -> None:
        """Register core plugins with the kernel.

        Args:
            kernel: Kernel instance
        """
        # Register built-in plugins
        # Prepare minimal prompt template config for conversation summary
        conv_config = PromptTemplateConfig(
            name="conversation_summary", template="{{input}}", template_format="semantic-kernel"
        )
        plugins = {
            "conversation": ConversationSummaryPlugin(conv_config),
            "http": HttpPlugin(),
            "math": MathPlugin(),
            "text": TextPlugin(),
            "time": TimePlugin(),
            "wait": WaitPlugin(),
            # Note: TextMemoryPlugin is deprecated - modern memory management
            # is handled through vector stores and embedding services registered above
        }

        # Add web search if configured
        if self._config.get("bing_api_key"):
            plugins["web_search"] = WebSearchEnginePlugin(self._config.get("bing_api_key"))

        for plugin_name, plugin in plugins.items():
            kernel.add_plugin(plugin, plugin_name)
            logger.info(f"Registered plugin: {plugin_name}")

        logger.info("Core plugins registered with modern memory services")

        # Register reasoning kernel specific plugins
        self._register_reasoning_plugins(kernel)

    def _register_reasoning_plugins(self, kernel: Kernel) -> None:
        """Register reasoning kernel specific plugins.

        Args:
            kernel: Kernel instance
        """
        try:
            # Register basic plugins that don't have complex dependencies
            basic_plugins = self._register_basic_reasoning_plugins(kernel)

            # Register advanced plugins with dependencies (if all components are ready)
            self._register_advanced_reasoning_plugins(kernel, basic_plugins)

        except ImportError as e:
            logger.warning(f"Some reasoning plugins could not be imported: {e}")
        except Exception as e:
            simple_log_error(logger, "register_reasoning_plugins", e)

    def _register_basic_reasoning_plugins(self, kernel: Kernel) -> dict:
        """Register basic reasoning plugins without complex dependencies."""
        plugins_registered = {}

        try:
            # Import and register basic plugins
            from ..plugins import InferencePlugin
            from ..plugins.langextract_plugin import LangExtractPlugin

            # These plugins have simple or no dependencies
            basic_plugins = {
                "inference": InferencePlugin(),  # Takes optional sandbox_config
                "langextract": LangExtractPlugin(),  # Takes optional config
            }

            for plugin_name, plugin in basic_plugins.items():
                kernel.add_plugin(plugin, plugin_name)
                plugins_registered[plugin_name] = plugin
                logger.info(f"Registered basic reasoning plugin: {plugin_name}")

        except Exception as e:
            logger.warning(f"Error registering basic plugins: {e}")

        return plugins_registered

    def _register_advanced_reasoning_plugins(self, kernel: Kernel, basic_plugins: dict) -> None:
        """Register advanced reasoning plugins that have dependencies."""
        try:
            # Import plugins that need kernel or other dependencies
            from ..plugins import KnowledgePlugin
            from ..plugins import ParsingPlugin
            from ..plugins import SynthesisPlugin

            # Get Redis client if available
            redis_client = self._services.get("redis_client")

            # Register plugins that need kernel
            kernel_plugins = {
                "parsing": ParsingPlugin(kernel=kernel, redis_client=redis_client),
                "synthesis": SynthesisPlugin(kernel=kernel),
            }

            # Register knowledge plugin if redis is available
            if redis_client:
                kernel_plugins["knowledge"] = KnowledgePlugin(redis_client=redis_client)

            for plugin_name, plugin in kernel_plugins.items():
                kernel.add_plugin(plugin, plugin_name)
                logger.info(f"Registered advanced reasoning plugin: {plugin_name}")

            # Note: Complex plugins like ThinkingExplorationPlugin, SampleEfficientLearningPlugin,
            # and MSAThinkingIntegrationPlugin require hierarchical managers and multiple dependencies.
            # These will be registered separately when the full system is initialized.
            logger.info("Advanced reasoning plugins with kernel dependencies registered")

        except Exception as e:
            logger.warning(f"Error registering advanced plugins: {e}")

    def get_kernel(self) -> Optional[Kernel]:
        """Get the current kernel instance.

        Returns:
            Kernel instance or None
        """
        return self._kernel

    def get_service(self, service_id: str) -> Optional[Any]:
        """Get a registered service by ID.

        Args:
            service_id: Service identifier

        Returns:
            Service instance or None
        """
        return self._services.get(service_id)

    def get_memory_collection(self, record_type: type, collection_name: Optional[str] = None):
        """Get a memory collection from the InMemoryStore.

        Args:
            record_type: The type of record to store in the collection
            collection_name: Optional collection name, defaults to record_type.__name__

        Returns:
            Collection instance or None if memory store not available
        """
        memory_store = self._services.get("memory_store")
        if memory_store:
            return memory_store.get_collection(record_type=record_type)
        else:
            logger.warning("Memory store not available - ensure kernel is created with proper configuration")
            return None

    def add_custom_plugin(self, kernel: Kernel, plugin: object, plugin_name: str) -> None:
        """Add a custom plugin to the kernel.

        Args:
            kernel: Kernel instance
            plugin: Plugin instance
            plugin_name: Name for the plugin
        """
        kernel.add_plugin(plugin, plugin_name)
        logger.info(f"Added custom plugin: {plugin_name}")

    def configure_from_env(self) -> None:
        """Configure the manager from environment variables."""
        import os

        from dotenv import load_dotenv

        load_dotenv()

        # OpenAI configuration
        self._config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
        self._config["openai_model_id"] = os.getenv("OPENAI_MODEL_ID", "gpt-4")
        self._config["openai_org_id"] = os.getenv("OPENAI_ORG_ID")
        self._config["embedding_model_id"] = os.getenv("EMBEDDING_MODEL_ID", "text-embedding-ada-002")

        # Azure OpenAI configuration
        self._config["use_azure_openai"] = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
        self._config["azure_deployment_name"] = os.getenv("AZURE_DEPLOYMENT_NAME")
        self._config["azure_endpoint"] = os.getenv("AZURE_ENDPOINT")
        self._config["azure_api_key"] = os.getenv("AZURE_API_KEY")
        self._config["azure_api_version"] = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")

        # Other services
        self._config["bing_api_key"] = os.getenv("BING_API_KEY")

        logger.info("Configuration loaded from environment variables")
