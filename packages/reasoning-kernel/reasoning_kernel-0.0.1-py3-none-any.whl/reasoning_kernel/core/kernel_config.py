"""
Semantic Kernel configuration and management with plugin registry integration
"""

from datetime import datetime
import logging
from typing import Optional

from ..core.error_handling import simple_log_error

from reasoning_kernel.core.config import settings
from reasoning_kernel.core.plugin_registry import BasePlugin
from reasoning_kernel.core.plugin_registry import create_plugin_registry
from reasoning_kernel.core.plugin_registry import PluginConfig
from reasoning_kernel.core.plugin_registry import PluginMetadata
from reasoning_kernel.core.plugin_registry import PluginRegistry
from reasoning_kernel.core.plugin_registry import PluginStatus
from reasoning_kernel.core.plugin_registry import set_global_registry
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.core_plugins.math_plugin import MathPlugin
from semantic_kernel.core_plugins.time_plugin import TimePlugin
from semantic_kernel.functions import kernel_function


logger = logging.getLogger(__name__)


class KnowledgeExtractionPlugin(BasePlugin):
    """Custom plugin for knowledge extraction and reasoning"""

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return PluginMetadata(
            name="KnowledgeExtractionPlugin",
            version="1.0.0",
            description="Plugin for knowledge extraction and reasoning",
            author="Reasoning Kernel Team",
            capabilities=["knowledge_extraction", "relationship_analysis", "hypothesis_generation"],
        )

    def initialize(self) -> None:
        """Initialize plugin components"""
        self._initialization_time = datetime.now()
        self._set_status(PluginStatus.ACTIVE)
        self.logger.info("KnowledgeExtractionPlugin initialized")

    def shutdown(self) -> None:
        """Shutdown plugin and cleanup resources"""
        self._set_status(PluginStatus.DISABLED)
        self.logger.info("KnowledgeExtractionPlugin shutdown")

    @kernel_function(
        name="extract_knowledge", description="Extract relevant knowledge and facts from a given context or question"
    )
    def extract_knowledge(self, context: str) -> str:
        """Extract key knowledge points from context"""
        return f"Knowledge extraction for: {context}"

    @kernel_function(
        name="identify_relationships", description="Identify causal relationships and dependencies in a scenario"
    )
    def identify_relationships(self, scenario: str) -> str:
        """Identify relationships between entities in a scenario"""
        return f"Relationship analysis for: {scenario}"

    @kernel_function(
        name="generate_hypotheses", description="Generate possible hypotheses or explanations for a given situation"
    )
    def generate_hypotheses(self, situation: str) -> str:
        """Generate hypotheses for a situation"""
        return f"Hypothesis generation for: {situation}"


class KernelManager:
    """Manages Semantic Kernel initialization and configuration with plugin registry"""

    def __init__(self):
        self.kernel: Optional[Kernel] = None
        self.chat_service = None
        self.plugin_registry: Optional[PluginRegistry] = None
        self.memory_store = None

    async def initialize(self):
        """Initialize the Semantic Kernel with AI services and plugins"""
        try:
            self.kernel = Kernel()

            # Memory store deprecated - Vector Store abstractions recommended
            self.memory_store = None

            # Setup AI service (OpenAI or Azure OpenAI)
            await self._setup_ai_service()

            # Initialize plugin registry
            self.plugin_registry = create_plugin_registry(self.kernel)
            set_global_registry(self.plugin_registry)

            # Add core plugins
            self._add_core_plugins()

            # Add custom plugins with registry
            self._add_custom_plugins_with_registry()

            # Initialize all plugins
            plugin_results = self.plugin_registry.initialize_all_plugins()
            logger.info(f"Plugin initialization results: {plugin_results}")

            # Register kernel functions from plugins
            self.plugin_registry.register_kernel_functions()

            logger.info("Semantic Kernel initialized successfully with plugin registry")

        except Exception as e:
            simple_log_error(logger, "initialize", e)
            raise

    async def _setup_ai_service(self):
        """Setup AI service (Azure OpenAI only)"""
        if not self.kernel:
            raise RuntimeError("Kernel not initialized before setting up AI service")

        try:
            # Validate Azure OpenAI credentials
            if not settings.azure_openai_api_key:
                raise ValueError("AZURE_OPENAI_API_KEY is required")
            if not settings.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT is required")
            if not settings.azure_openai_deployment:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT is required")

            # Use Azure OpenAI only
            self.chat_service = AzureChatCompletion(
                service_id="azure_chat",
                deployment_name=settings.azure_openai_deployment,
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
            logger.info("Using Azure OpenAI service")

            self.kernel.add_service(self.chat_service)

        except Exception as e:
            simple_log_error(logger, "setup_ai_service", e)
            raise

    def _add_core_plugins(self):
        """Add core Semantic Kernel plugins"""
        if not self.kernel:
            raise RuntimeError("Kernel not initialized before adding core plugins")

        try:
            # Add time plugin for temporal reasoning
            self.kernel.add_plugin(TimePlugin(), plugin_name="time")

            # Add math plugin for calculations
            self.kernel.add_plugin(MathPlugin(), plugin_name="math")

            logger.info("Core plugins added successfully")

        except Exception as e:
            simple_log_error(logger, "add_core_plugins", e)
            raise

    def _add_custom_plugins(self):
        """Add custom plugins for MSA functionality (legacy method)"""
        if not self.kernel:
            raise RuntimeError("Kernel not initialized before adding custom plugins")

        try:
            # Add knowledge extraction plugin (legacy way)
            self.kernel.add_plugin(
                KnowledgeExtractionPlugin(kernel=self.kernel, config=PluginConfig(), memory_store=self.memory_store),
                plugin_name="knowledge_extraction",
            )

            logger.info("Custom plugins added successfully")

        except Exception as e:
            simple_log_error(logger, "add_custom_plugins", e)
            raise

    def _add_custom_plugins_with_registry(self):
        """Add custom plugins using the plugin registry system"""
        if not self.plugin_registry:
            raise RuntimeError("Plugin registry not initialized")

        try:
            # Register knowledge extraction plugin
            self.plugin_registry.register_plugin(
                KnowledgeExtractionPlugin,
                config=PluginConfig(enabled=True, auto_initialize=True, priority=1),
                memory_store=self.memory_store,
            )

            logger.info("Custom plugins registered with plugin registry")

        except Exception as e:
            simple_log_error(logger, "add_custom_plugins_with_registry", e)
            raise

    async def invoke_prompt(self, prompt: str, **kwargs) -> str:
        """Invoke a prompt using the kernel"""
        if not self.kernel:
            raise RuntimeError("Kernel not initialized")

        try:
            result = await self.kernel.invoke_prompt(prompt, **kwargs)
            return str(result)
        except Exception as e:
            simple_log_error(logger, "invoke_prompt", e)
            raise

    async def invoke_function(self, plugin_name: str, function_name: str, **kwargs) -> str:
        """Invoke a specific function from a plugin"""
        if not self.kernel:
            raise RuntimeError("Kernel not initialized")

        try:
            function = self.kernel.get_function(plugin_name, function_name)
            result = await function.invoke(self.kernel, **kwargs)
            return str(result)
        except Exception as e:
            simple_log_error(logger, "invoke_function", e, plugin_name=plugin_name, function_name=function_name)
            raise

    async def cleanup(self):
        """Cleanup kernel resources"""
        if self.kernel:
            # Perform any necessary cleanup
            logger.info("Kernel cleanup completed")
