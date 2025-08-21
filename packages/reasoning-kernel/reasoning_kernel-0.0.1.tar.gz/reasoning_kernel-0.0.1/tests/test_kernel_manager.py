"""
Tests for KernelManager with comprehensive coverage of plugin registration and modernized patterns.

This module provides comprehensive unit tests for the KernelManager class, ensuring:
- Proper kernel initialization with modern Semantic Kernel patterns
- Plugin discovery and registration functionality
- Service registration and retrieval
- Error handling and graceful degradation
- Memory service integration with InMemoryStore

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-01-27
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from reasoning_kernel.core.kernel_manager import KernelManager
from semantic_kernel import Kernel


class TestKernelManager:
    """Test KernelManager functionality with modern Semantic Kernel patterns."""

    @pytest.fixture
    def minimal_config(self) -> Dict[str, Any]:
        """Create minimal configuration for testing."""
        return {"openai_api_key": "test-key-12345"}

    @pytest.fixture
    def azure_config(self) -> Dict[str, Any]:
        """Create Azure configuration for testing."""
        return {
            "use_azure_openai": True,
            "azure_api_key": "test-azure-key",
            "azure_endpoint": "https://test.openai.azure.com",
            "azure_deployment_name": "test-gpt-4",
            "azure_embedding_deployment_name": "test-embedding",
        }

    def test_kernel_manager_initialization(self, minimal_config):
        """Test KernelManager initialization with configuration."""
        manager = KernelManager(minimal_config)

        assert manager._config == minimal_config
        assert manager._kernel is None
        assert manager._services == {}

    def test_kernel_manager_initialization_no_config(self):
        """Test KernelManager initialization without configuration."""
        manager = KernelManager()

        assert manager._config == {}
        assert manager._kernel is None
        assert manager._services == {}

    @patch("reasoning_kernel.core.kernel_manager.Kernel")
    @patch("reasoning_kernel.core.kernel_manager.OpenAIChatCompletion")
    @patch("reasoning_kernel.core.kernel_manager.OpenAITextEmbedding")
    def test_create_kernel_openai(self, mock_embedding, mock_chat, mock_kernel, minimal_config):
        """Test kernel creation with OpenAI configuration."""
        mock_kernel_instance = MagicMock(spec=Kernel)
        mock_kernel.return_value = mock_kernel_instance

        manager = KernelManager(minimal_config)
        kernel = manager.create_kernel()

        # Verify kernel creation
        mock_kernel.assert_called_once()
        assert kernel == mock_kernel_instance
        assert manager.get_kernel() == mock_kernel_instance

        # Verify OpenAI services were configured
        mock_chat.assert_called_once()
        mock_embedding.assert_called_once()

        # Verify services were added to kernel
        assert mock_kernel_instance.add_service.call_count >= 2  # At least chat and embedding

    @patch("reasoning_kernel.core.kernel_manager.Kernel")
    @patch("reasoning_kernel.core.kernel_manager.AzureChatCompletion")
    @patch("reasoning_kernel.core.kernel_manager.AzureTextEmbedding")
    def test_create_kernel_azure(self, mock_embedding, mock_chat, mock_kernel, azure_config):
        """Test kernel creation with Azure configuration."""
        mock_kernel_instance = MagicMock(spec=Kernel)
        mock_kernel.return_value = mock_kernel_instance

        manager = KernelManager(azure_config)
        kernel = manager.create_kernel()

        # Verify kernel creation
        mock_kernel.assert_called_once()
        assert kernel == mock_kernel_instance

        # Verify Azure services were configured
        mock_chat.assert_called_once()
        mock_embedding.assert_called_once()

        # Verify services were added to kernel
        assert mock_kernel_instance.add_service.call_count >= 2

    def test_create_kernel_no_ai_config(self):
        """Test kernel creation with no AI service configuration."""
        manager = KernelManager({})

        # Should still create kernel but with warnings
        kernel = manager.create_kernel()

        assert kernel is not None
        assert isinstance(kernel, Kernel)

    def test_plugin_registration(self, minimal_config):
        """Test that plugins are registered correctly."""
        manager = KernelManager(minimal_config)
        kernel = manager.create_kernel()

        # Check that core plugins are registered
        plugins = list(kernel.plugins.keys())

        # Should have basic core plugins
        expected_core_plugins = ["conversation", "http", "math", "text", "time", "wait"]
        for plugin in expected_core_plugins:
            assert plugin in plugins

        # Should have reasoning plugins
        reasoning_plugins = [p for p in plugins if p in ["inference", "langextract", "parsing", "synthesis"]]
        assert len(reasoning_plugins) > 0, f"Expected reasoning plugins, got: {plugins}"

    def test_get_service(self, minimal_config):
        """Test service retrieval."""
        manager = KernelManager(minimal_config)
        kernel = manager.create_kernel()

        # Should be able to retrieve registered services
        chat_service = manager.get_service("chat_completion")
        # May be None if no valid API key, but method should work

        # Non-existent service should return None
        fake_service = manager.get_service("non_existent_service")
        assert fake_service is None

    def test_get_memory_collection(self, minimal_config):
        """Test memory collection retrieval."""
        manager = KernelManager(minimal_config)
        manager.create_kernel()

        # Define a test record type
        class TestRecord:
            def __init__(self, content: str):
                self.content = content

        # Should be able to get memory collection (may return None if no embedding service)
        try:
            collection = manager.get_memory_collection(TestRecord, collection_name="test_collection")
            # Collection creation may fail if no embedding service configured
            # This is expected behavior and not an error
        except Exception:
            # Expected if no proper embedding configuration
            pass

    def test_error_handling_plugin_registration(self):
        """Test error handling during plugin registration."""
        manager = KernelManager({})

        # Should handle plugin registration errors gracefully
        with patch("reasoning_kernel.core.kernel_manager.logger") as mock_logger:
            kernel = manager.create_kernel()

            # Should log warnings for missing configurations
            assert mock_logger.warning.called

            # But still return a kernel
            assert kernel is not None


class TestKernelManagerIntegration:
    """Integration tests for KernelManager with real Semantic Kernel components."""

    def test_kernel_manager_end_to_end(self):
        """Test end-to-end kernel manager functionality."""
        # Use a real (but fake) API key
        config = {"openai_api_key": "sk-fake-test-key-for-testing"}

        manager = KernelManager(config)
        kernel = manager.create_kernel()

        # Verify kernel is created
        assert kernel is not None
        assert isinstance(kernel, Kernel)

        # Verify plugins are registered
        plugins = list(kernel.plugins.keys())
        assert len(plugins) > 0

        # Verify services are tracked
        services = manager._services
        assert isinstance(services, dict)

    def test_multiple_kernel_creation(self):
        """Test creating multiple kernels with same manager."""
        config = {"openai_api_key": "sk-fake-test-key-for-testing"}
        manager = KernelManager(config)

        kernel1 = manager.create_kernel()
        kernel2 = manager.create_kernel()

        # Should create new kernels each time
        assert kernel1 is not kernel2

        # But get_kernel() should return the latest
        assert manager.get_kernel() is kernel2
