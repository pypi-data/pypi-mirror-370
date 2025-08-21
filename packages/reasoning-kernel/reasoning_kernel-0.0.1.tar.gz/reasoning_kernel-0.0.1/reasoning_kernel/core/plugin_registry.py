"""
Plugin Registry System for Semantic Kernel Integration

This module implements a comprehensive plugin registration and management system
compatible with Semantic Kernel 1.35.3+, providing standardized plugin lifecycle
management, dependency resolution, and service integration.

Key Features:
- Plugin discovery and registration
- Dependency management and resolution
- Service lifecycle management
- Configuration validation
- Error handling and recovery
- Performance monitoring

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-16
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional, Type

# Semantic Kernel imports
from semantic_kernel import Kernel

from reasoning_kernel.core.error_handling import simple_log_error

# Internal imports


logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin status enumeration"""

    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginMetadata:
    """Metadata for plugin registration"""

    name: str
    version: str
    description: str
    author: str = "Unknown"
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    configuration_schema: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: PluginStatus = PluginStatus.UNREGISTERED


@dataclass
class PluginConfig:
    """Configuration for plugin instances"""

    enabled: bool = True
    auto_initialize: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout_seconds: float = 30.0
    retry_attempts: int = 3


class BasePlugin(ABC):
    """
    Base class for all Semantic Kernel plugins.

    Provides standardized plugin interface with lifecycle management,
    configuration handling, and error recovery.
    """

    def __init__(
        self,
        kernel: Kernel,
        config: PluginConfig,
        memory_store=None,
    ):
        """
        Initialize the base plugin.

        Args:
            kernel: Semantic Kernel instance
            config: Plugin configuration
            memory_store: Optional memory store
        """
        self.kernel = kernel
        self.config = config
        self.memory_store = memory_store
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Plugin state
        self._status = PluginStatus.REGISTERED
        self._initialization_time: Optional[datetime] = None
        self._error_count = 0
        self._last_error: Optional[str] = None

        # Initialize plugin
        if config.auto_initialize:
            self.initialize()

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin components"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown plugin and cleanup resources"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status information"""
        return {
            "name": self.metadata.name,
            "status": self._status.value,
            "initialization_time": self._initialization_time.isoformat() if self._initialization_time else None,
            "error_count": self._error_count,
            "last_error": self._last_error,
            "configuration": {
                "enabled": self.config.enabled,
                "priority": self.config.priority,
                "timeout_seconds": self.config.timeout_seconds,
            },
        }

    def _set_status(self, status: PluginStatus, error_message: Optional[str] = None) -> None:
        """Set plugin status with optional error message"""
        self._status = status
        if error_message:
            self._last_error = error_message
            self._error_count += 1
        self.logger.debug(f"Plugin {self.metadata.name} status changed to {status.value}")

    def _safe_execute(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with error handling"""
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            self._set_status(PluginStatus.ERROR, str(e))
            simple_log_error(self.logger, "plugin_operation", e, plugin_name=self.metadata.name)
            raise


class PluginRegistry:
    """
    Central registry for managing Semantic Kernel plugins.

    Provides plugin discovery, registration, dependency resolution,
    and lifecycle management.
    """

    def __init__(self, kernel: Kernel):
        """
        Initialize the plugin registry.

        Args:
            kernel: Semantic Kernel instance
        """
        self.kernel = kernel
        self.logger = logging.getLogger(f"{__name__}.Registry")

        # Plugin storage
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_configs: Dict[str, PluginConfig] = {}
        self._dependency_graph: Dict[str, List[str]] = {}

        # Registry state
        self._initialization_order: List[str] = []
        self._total_plugins = 0
        self._active_plugins = 0

        self.logger.info("PluginRegistry initialized")

    def register_plugin(self, plugin_class: Type[BasePlugin], config: Optional[PluginConfig] = None, **kwargs) -> str:
        """
        Register a plugin class with the registry.

        Args:
            plugin_class: Plugin class to register
            config: Optional plugin configuration
            **kwargs: Additional arguments for plugin initialization

        Returns:
            Plugin name for reference
        """
        # Create default config if not provided
        if config is None:
            config = PluginConfig()

        # Create plugin instance
        try:
            plugin_instance = plugin_class(kernel=self.kernel, config=config, **kwargs)

            plugin_name = plugin_instance.metadata.name

            # Check for duplicate registration
            if plugin_name in self._plugins:
                raise ValueError(f"Plugin {plugin_name} is already registered")

            # Store plugin and configuration
            self._plugins[plugin_name] = plugin_instance
            self._plugin_configs[plugin_name] = config

            # Build dependency graph
            self._build_dependency_graph(plugin_instance)

            # Update counters
            self._total_plugins += 1
            if plugin_instance._status == PluginStatus.ACTIVE:
                self._active_plugins += 1

            self.logger.info(f"Registered plugin: {plugin_name}")
            return plugin_name

        except Exception as e:
            simple_log_error(self.logger, "register_plugin", e, plugin_class=plugin_class.__name__)
            raise

    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin from the registry.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if plugin was unregistered, False if not found
        """
        if plugin_name not in self._plugins:
            return False

        try:
            # Shutdown plugin
            plugin = self._plugins[plugin_name]
            plugin.shutdown()

            # Remove from registry
            del self._plugins[plugin_name]
            del self._plugin_configs[plugin_name]

            # Update dependency graph
            if plugin_name in self._dependency_graph:
                del self._dependency_graph[plugin_name]

            # Remove from initialization order
            if plugin_name in self._initialization_order:
                self._initialization_order.remove(plugin_name)

            # Update counters
            self._total_plugins -= 1
            if plugin._status == PluginStatus.ACTIVE:
                self._active_plugins -= 1

            self.logger.info(f"Unregistered plugin: {plugin_name}")
            return True

        except Exception as e:
            simple_log_error(self.logger, "unregister_plugin", e, plugin_name=plugin_name)
            return False

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin instance by name"""
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """List all registered plugin names"""
        return list(self._plugins.keys())

    def get_plugins_by_capability(self, capability: str) -> List[BasePlugin]:
        """Get plugins that provide a specific capability"""
        matching_plugins = []
        for plugin in self._plugins.values():
            if capability in plugin.metadata.capabilities:
                matching_plugins.append(plugin)
        return matching_plugins

    def initialize_all_plugins(self) -> Dict[str, bool]:
        """
        Initialize all registered plugins in dependency order.

        Returns:
            Dictionary mapping plugin names to initialization success
        """
        results = {}

        # Resolve initialization order
        initialization_order = self._resolve_initialization_order()

        for plugin_name in initialization_order:
            try:
                plugin = self._plugins[plugin_name]
                if plugin._status == PluginStatus.REGISTERED:
                    plugin.initialize()
                    plugin._set_status(PluginStatus.ACTIVE)
                    self._active_plugins += 1
                results[plugin_name] = True

            except Exception as e:
                simple_log_error(self.logger, "initialize_plugin", e, plugin_name=plugin_name)
                results[plugin_name] = False

        self._initialization_order = initialization_order
        self.logger.info(f"Initialized {sum(results.values())}/{len(results)} plugins")

        return results

    def shutdown_all_plugins(self) -> None:
        """Shutdown all plugins in reverse initialization order"""
        shutdown_order = list(reversed(self._initialization_order))

        for plugin_name in shutdown_order:
            try:
                plugin = self._plugins[plugin_name]
                plugin.shutdown()
                plugin._set_status(PluginStatus.DISABLED)
                if plugin._status == PluginStatus.ACTIVE:
                    self._active_plugins -= 1

            except Exception as e:
                simple_log_error(self.logger, "shutdown_plugin", e, plugin_name=plugin_name)

        self.logger.info("All plugins shutdown completed")

    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and plugin information"""
        plugin_statuses = {}
        for name, plugin in self._plugins.items():
            plugin_statuses[name] = plugin.get_status()

        return {
            "total_plugins": self._total_plugins,
            "active_plugins": self._active_plugins,
            "initialization_order": self._initialization_order,
            "dependency_graph": self._dependency_graph,
            "plugins": plugin_statuses,
        }

    def _build_dependency_graph(self, plugin: BasePlugin) -> None:
        """Build dependency graph for plugin"""
        plugin_name = plugin.metadata.name
        dependencies = plugin.metadata.dependencies
        self._dependency_graph[plugin_name] = dependencies

    def _resolve_initialization_order(self) -> List[str]:
        """Resolve plugin initialization order based on dependencies"""
        # Simple topological sort implementation
        visited = set()
        temp_visited = set()
        order = []

        def visit(plugin_name: str):
            if plugin_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {plugin_name}")
            if plugin_name in visited:
                return

            temp_visited.add(plugin_name)

            # Visit dependencies first
            dependencies = self._dependency_graph.get(plugin_name, [])
            for dep in dependencies:
                if dep in self._plugins:
                    visit(dep)

            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            order.append(plugin_name)

        # Visit all plugins
        for plugin_name in self._plugins.keys():
            if plugin_name not in visited:
                visit(plugin_name)

        return order

    def register_kernel_functions(self) -> None:
        """Register all plugin kernel functions with the kernel"""
        for plugin_name, plugin in self._plugins.items():
            try:
                # Get all kernel functions from the plugin
                for attr_name in dir(plugin):
                    attr = getattr(plugin, attr_name)
                    if hasattr(attr, "__kernel_function__"):
                        # This is a kernel function, register it
                        self.kernel.add_function(plugin_name=plugin_name, function=attr)
                        self.logger.debug(f"Registered kernel function {attr_name} from {plugin_name}")

            except Exception as e:
                simple_log_error(self.logger, "register_kernel_functions", e, plugin_name=plugin_name)


# Factory function for creating plugin registry
def create_plugin_registry(kernel: Kernel) -> PluginRegistry:
    """
    Factory function to create a PluginRegistry instance.

    Args:
        kernel: Semantic Kernel instance

    Returns:
        Configured PluginRegistry instance
    """
    return PluginRegistry(kernel)


# Global plugin registry instance (will be initialized by the application)
_global_registry: Optional[PluginRegistry] = None


def get_global_registry() -> Optional[PluginRegistry]:
    """Get the global plugin registry instance"""
    return _global_registry


def set_global_registry(registry: PluginRegistry) -> None:
    """Set the global plugin registry instance"""
    global _global_registry
    _global_registry = registry


# Decorator for easy plugin registration
def register_plugin(
    name: str,
    version: str = "1.0.0",
    description: str = "",
    dependencies: List[str] = None,
    capabilities: List[str] = None,
    auto_register: bool = True,
):
    """
    Decorator for automatic plugin registration.

    Args:
        name: Plugin name
        version: Plugin version
        description: Plugin description
        dependencies: List of plugin dependencies
        capabilities: List of plugin capabilities
        auto_register: Whether to auto-register with global registry
    """

    def decorator(plugin_class: Type[BasePlugin]):
        # Add metadata to the class

        def metadata_property(self):
            return PluginMetadata(
                name=name,
                version=version,
                description=description,
                dependencies=dependencies or [],
                capabilities=capabilities or [],
            )

        plugin_class.metadata = property(metadata_property)

        # Auto-register if requested and global registry is available
        if auto_register and _global_registry:
            try:
                _global_registry.register_plugin(plugin_class)
            except Exception as e:
                logger.warning(f"Failed to auto-register plugin {name}: {e}")

        return plugin_class

    return decorator
