"""Utility functions for logging to avoid circular imports."""

import logging


def simple_log_error(logger, operation_name: str, error: Exception, **kwargs):
    """
    Simple function to log an error with structured logging.
    
    Args:
        logger: Logger instance (supports both logging.Logger and structlog)
        operation_name: Name of the operation that failed
        error: Exception that occurred
        **kwargs: Additional context to include in the log
    """
    try:
        # Try structured logging first
        error_info = {
            "operation": operation_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            **kwargs
        }
        logger.error("Operation failed", **error_info)
    except Exception:
        # Fallback to basic logging
        error_info = {
            "operation": operation_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            **kwargs
        }
        logger.error(f"Operation failed: {operation_name} - {error_info}")