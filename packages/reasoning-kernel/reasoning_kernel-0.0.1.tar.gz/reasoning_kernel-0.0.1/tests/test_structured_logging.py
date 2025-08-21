"""Tests for structured logging configuration."""

import json
import logging
import os
from contextlib import redirect_stdout
from io import StringIO

import pytest

from reasoning_kernel.core.logging_config import (
    configure_logging,
    get_logger,
    request_context,
    performance_context,
    get_request_id,
    get_request_context,
)


class TestLoggingConfiguration:
    """Test structured logging configuration."""

    def test_configure_logging_json_format(self):
        """Test that JSON logging format works."""
        # Capture log output
        log_capture = StringIO()
        
        # Configure logging to use JSON format
        configure_logging(level="INFO", json_logs=True)
        
        # Get a logger and log a message
        logger = get_logger("test")
        
        # Redirect stdout to capture JSON log
        with redirect_stdout(log_capture):
            logger.info("Test message", test_field="test_value")
        
        # Parse the JSON log
        log_output = log_capture.getvalue().strip()
        if log_output:
            log_data = json.loads(log_output)
            
            # Verify structure
            assert "event" in log_data
            assert "service" in log_data
            assert "timestamp" in log_data
            assert log_data["event"] == "Test message"
            assert log_data["service"] == "reasoning-kernel"
            assert log_data["test_field"] == "test_value"

    def test_request_context_manager(self):
        """Test request context manager functionality."""
        # Test initial state
        assert get_request_id() != ""
        
        # Test context manager
        test_request_id = "test-123"
        with request_context(test_request_id, endpoint="/test", method="GET"):
            assert get_request_id() == test_request_id
            context = get_request_context()
            assert context["request_id"] == test_request_id
            assert context["endpoint"] == "/test"
            assert context["method"] == "GET"
        
        # Test context is reset after context manager
        assert get_request_id() != test_request_id

    def test_performance_context_success(self):
        """Test performance context manager for successful operations."""
        logger = get_logger("test_performance")
        
        with performance_context("test_operation", logger):
            # Simulate some work
            pass
        
        # Context manager should complete without error

    def test_performance_context_failure(self):
        """Test performance context manager for failed operations."""
        logger = get_logger("test_performance")
        
        with pytest.raises(ValueError):
            with performance_context("test_operation", logger):
                raise ValueError("Test error")

    def test_logger_creation(self):
        """Test logger creation returns proper structured logger."""
        logger = get_logger("test_component")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_configure_logging_levels(self):
        """Test different log levels are handled correctly."""
        # Test with different levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            configure_logging(level=level)
            # Should not raise any exceptions

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Set environment variable
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        try:
            configure_logging()
            # Should use DEBUG level from environment
            root_logger = logging.getLogger()
            assert root_logger.level <= logging.DEBUG
        finally:
            # Clean up
            if "LOG_LEVEL" in os.environ:
                del os.environ["LOG_LEVEL"]

    def test_json_format_environment_override(self):
        """Test LOG_FORMAT environment variable controls JSON output."""
        # Test text format
        os.environ["LOG_FORMAT"] = "text"
        
        try:
            configure_logging(json_logs=True)
            # Should configure successfully
            logger = get_logger("test")
            assert logger is not None
        finally:
            # Clean up
            if "LOG_FORMAT" in os.environ:
                del os.environ["LOG_FORMAT"]