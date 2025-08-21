"""
Unified error handling utilities for the Reasoning Kernel.

This module provides centralized error handling with:
- Structured logging with context
- Secure input sanitization
- Performance tracking
- Standardized error responses
"""

from contextlib import contextmanager
import logging
import time
import traceback
from typing import Any, Dict, Optional
import structlog

from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.core.logging_utils import simple_log_error
from reasoning_kernel.utils.security import sanitize_user_input, SecureLogger


class UnifiedErrorHandler:
    """
    Centralized error handler with structured logging and secure input handling.
    """

    def __init__(self, service_name: str = "reasoning-kernel"):
        self.service_name = service_name
        self.logger = get_logger(f"{service_name}.error_handler")
        self.secure_logger = SecureLogger(logging.getLogger(f"{service_name}.secure"))

    @contextmanager
    def handle_errors(
        self,
        operation: str,
        logger: Optional[structlog.stdlib.BoundLogger] = None,
        secure_logging: bool = False,
        include_performance: bool = False,
        **context
    ):
        """
        Context manager for unified error handling.

        Args:
            operation: Name of the operation being performed
            logger: Specific logger to use (optional)
            secure_logging: Whether to use secure logging to prevent injection
            include_performance: Whether to track performance metrics
            **context: Additional context to include in logs
        """
        log = logger or self.logger
        start_time = time.time() if include_performance else None

        if include_performance:
            log.info("Operation started", operation=operation, start_time=start_time, **context)

        try:
            yield log
            if include_performance:
                duration = time.time() - start_time
                log.info("Operation completed", operation=operation, duration=duration, status="success", **context)
        except Exception as e:
            # Sanitize context for secure logging
            sanitized_context = {}
            if secure_logging:
                for key, value in context.items():
                    sanitized_context[key] = sanitize_user_input(value)
            else:
                sanitized_context = context

            # Add performance metrics if tracking
            error_context = {
                "operation": operation,
                "error_type": type(e).__name__,
                "error_message": str(e) if not secure_logging else sanitize_user_input(str(e)),
                "traceback": traceback.format_exc() if not secure_logging else "Traceback sanitized for security",
                **sanitized_context
            }

            if include_performance and start_time:
                error_context["duration"] = time.time() - start_time

            # Use appropriate logger based on security requirements
            if secure_logging:
                self.secure_logger.error("Operation failed", **error_context)
            else:
                log.error("Operation failed", **error_context)

            raise

    def log_error(
        self,
        error: Exception,
        operation: str,
        logger: Optional[structlog.stdlib.BoundLogger] = None,
        secure_logging: bool = False,
        **context
    ) -> Dict[str, Any]:
        """
        Log an error with structured context.

        Args:
            error: The exception that occurred
            operation: Name of the operation where the error occurred
            logger: Specific logger to use (optional)
            secure_logging: Whether to use secure logging to prevent injection
            **context: Additional context to include in logs

        Returns:
            Dictionary with error details
        """
        log = logger or self.logger

        # Sanitize context for secure logging
        sanitized_context = {}
        if secure_logging:
            for key, value in context.items():
                sanitized_context[key] = sanitize_user_input(value)
        else:
            sanitized_context = context

        error_details = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error) if not secure_logging else sanitize_user_input(str(error)),
            "traceback": traceback.format_exc() if not secure_logging else "Traceback sanitized for security",
            **sanitized_context
        }

        # Use appropriate logger based on security requirements
        if secure_logging:
            self.secure_logger.error("Error occurred", **error_details)
        else:
            log.error("Error occurred", **error_details)

        return error_details

    def create_error_response(
        self,
        error: Exception,
        operation: str,
        user_message: str = "An error occurred while processing your request",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error: The exception that occurred
            operation: Name of the operation where the error occurred
            user_message: Message to show to the user
            error_code: Internal error code
            status_code: HTTP status code
            include_details: Whether to include detailed error information

        Returns:
            Dictionary with standardized error response
        """
        error_response = {
            "status": "error",
            "message": user_message,
            "error_code": error_code,
            "status_code": status_code,
            "operation": operation
        }

        if include_details:
            error_response.update({
                "error_type": type(error).__name__,
                "error_details": str(error),
                "timestamp": time.time()
            })

        return error_response

    def wrap_function(self, func, operation: str = None, secure_logging: bool = False):
        """
        Decorator to wrap functions with unified error handling.

        Args:
            func: Function to wrap
            operation: Name of the operation (defaults to function name)
            secure_logging: Whether to use secure logging

        Returns:
            Wrapped function with error handling
        """
        operation_name = operation or func.__name__

        def wrapper(*args, **kwargs):
            with self.handle_errors(operation_name, secure_logging=secure_logging):
                return func(*args, **kwargs)
        return wrapper


# Global instance for easy access
error_handler = UnifiedErrorHandler()


def handle_errors(
    operation: str,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
    secure_logging: bool = False,
    include_performance: bool = False,
    **context
):
    """
    Context manager for unified error handling.

    Args:
        operation: Name of the operation being performed
        logger: Specific logger to use (optional)
        secure_logging: Whether to use secure logging to prevent injection
        include_performance: Whether to track performance metrics
        **context: Additional context to include in logs
    """
    return error_handler.handle_errors(
        operation=operation,
        logger=logger,
        secure_logging=secure_logging,
        include_performance=include_performance,
        **context
    )


def log_error(
    error: Exception,
    operation: str,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
    secure_logging: bool = False,
    **context
) -> Dict[str, Any]:
    """
    Log an error with structured context.

    Args:
        error: The exception that occurred
        operation: Name of the operation where the error occurred
        logger: Specific logger to use (optional)
        secure_logging: Whether to use secure logging to prevent injection
        **context: Additional context to include in logs

    Returns:
        Dictionary with error details
    """
    return error_handler.log_error(
        error=error,
        operation=operation,
        logger=logger,
        secure_logging=secure_logging,
        **context
    )


def create_error_response(
    error: Exception,
    operation: str,
    user_message: str = "An error occurred while processing your request",
    error_code: str = "INTERNAL_ERROR",
    status_code: int = 500,
    include_details: bool = False
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error: The exception that occurred
        operation: Name of the operation where the error occurred
        user_message: Message to show to the user
        error_code: Internal error code
        status_code: HTTP status code
        include_details: Whether to include detailed error information

    Returns:
        Dictionary with standardized error response
    """
    return error_handler.create_error_response(
        error=error,
        operation=operation,
        user_message=user_message,
        error_code=error_code,
        status_code=status_code,
        include_details=include_details
    )


def simple_log_error(logger: logging.Logger, operation_name: str, error: Exception, **kwargs):
    """
    Simple function to log an error with structured logging.
    
    Args:
        logger: Logger instance
        operation_name: Name of the operation that failed
        error: Exception that occurred
        **kwargs: Additional context to include in the log
    """
    error_info = {
        "operation": operation_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        **kwargs
    }
    
    # Remove 'operation' from error_info to avoid passing it as a keyword argument to logger.error()
    error_info.pop("operation", None)
    
    logger.error(f"Operation failed: {operation_name}", **error_info)


# Export main classes and functions
__all__ = [
    "UnifiedErrorHandler",
    "error_handler",
    "handle_errors",
    "log_error",
    "create_error_response",
    "simple_log_error"
]