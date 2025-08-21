"""
Security utilities for the Reasoning Kernel application.

This module provides security-focused utilities including:
- Secure logging functions to prevent log injection attacks
- Input sanitization for user-provided data
- Secure random number generation utilities
"""

from functools import wraps
import logging
import re
import secrets
from typing import Any, Dict, Union
import uuid


class SecureLogger:
    """
    Secure logging utility that prevents log injection attacks by sanitizing user inputs.

    This class wraps the standard Python logging module and ensures that all user-provided
    data is properly sanitized before being logged.
    """

    # Characters that can be used for log injection attacks
    # Matches control characters and ANSI escape sequences (e.g., \x1b[31m)
    LOG_INJECTION_PATTERNS = re.compile(
        r"(?:[\r\n\t\x00-\x1f\x7f-\x9f]|"  # Control characters
        r"\x1b\[[0-9;]*[A-Za-z])"  # ANSI escape sequences
    )
    LOG_INJECTION_PATTERNS = re.compile(
        r"(?:[\r\n\t\x00-\x1f\x7f-\x9f]|"  # Control characters
        r"\x1b\[[0-9;]*[A-Za-z])"  # ANSI escape sequences
    )

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @staticmethod
    def sanitize_input(value: Any) -> str:
        """
        Sanitize user input to prevent log injection attacks.

        Args:
            value: The input value to sanitize (any type will be converted to string)

        Returns:
            Sanitized string safe for logging
        """
        if value is None:
            return "None"

        # Convert to string
        str_value = str(value)

        # Replace potentially dangerous characters with safe alternatives
        sanitized = SecureLogger.LOG_INJECTION_PATTERNS.sub("_", str_value)

        # Truncate very long strings to prevent log flooding
        if len(sanitized) > 1000:
            sanitized = sanitized[:997] + "..."

        return sanitized

    def _log_with_sanitization(self, level: int, msg: str, *args, **kwargs):
        """Internal method to log with automatic sanitization of arguments."""
        # Sanitize all positional arguments
        sanitized_args = tuple(self.sanitize_input(arg) for arg in args)

        # Sanitize keyword arguments
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["exc_info", "stack_info", "stacklevel", "extra"]:
                sanitized_kwargs[key] = self.sanitize_input(value)
            else:
                sanitized_kwargs[key] = value

        # Log with sanitized data
        self.logger.log(level, msg, *sanitized_args, **sanitized_kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log an info message with automatic input sanitization."""
        self._log_with_sanitization(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message with automatic input sanitization."""
        self._log_with_sanitization(logging.WARNING, msg, *args, **kwargs)

    def warn(self, msg: str, *args, **kwargs):
        """Log a warning message with automatic input sanitization (alias for warning)."""
        self.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log an error message with automatic input sanitization."""
        self._log_with_sanitization(logging.ERROR, msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        """Log an exception message with automatic input sanitization."""
        kwargs["exc_info"] = True
        self._log_with_sanitization(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message with automatic input sanitization."""
        self._log_with_sanitization(logging.CRITICAL, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message with automatic input sanitization."""
        self._log_with_sanitization(logging.DEBUG, msg, *args, **kwargs)

    def log_structured(self, level: int, message: str, **fields):
        """
        Log a structured message with field sanitization.

        Args:
            level: Logging level
            message: Main log message
            **fields: Additional structured fields to log
        """
        sanitized_fields = {
            key: self.sanitize_input(value) for key, value in fields.items()
        }

        # Create structured log entry
        structured_msg = f"{message} | " + " | ".join(
            f"{key}={value}" for key, value in sanitized_fields.items()
        )

        self.logger.log(level, structured_msg)


def get_secure_logger(name: str) -> SecureLogger:
    """
    Get a secure logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        SecureLogger instance
    """
    return SecureLogger(logging.getLogger(name))


def secure_log_decorator(func):
    """
    Decorator to automatically wrap function calls with secure logging.

    This decorator can be applied to functions that need logging and will
    automatically sanitize any logged data.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_secure_logger(func.__module__)
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {str(e)}")
            raise

    return wrapper


class SecureRandom:
    """
    Cryptographically secure random number generation utilities.

    This class provides secure alternatives to standard random number generation
    that should be used for security-sensitive operations.
    """

    @staticmethod
    def generate_session_id() -> str:
        """Generate a cryptographically secure session ID."""
        return f"session_{secrets.token_urlsafe(16)}"

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a cryptographically secure token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_uuid() -> str:
        """Generate a UUID v4 (random UUID)."""
        return str(uuid.uuid4())

    @staticmethod
    def secure_randint(min_val: int, max_val: int) -> int:
        """Generate a cryptographically secure random integer in range [min_val, max_val]."""
        return secrets.randbelow(max_val - min_val + 1) + min_val

    @staticmethod
    def secure_randfloat() -> float:
        """Generate a cryptographically secure random float in range [0.0, 1.0)."""
        return secrets.randbelow(_UINT32_MAX_PLUS_ONE) / _UINT32_MAX_PLUS_ONE


def sanitize_user_input(input_data: Union[str, Dict, Any]) -> Union[str, Dict, Any]:
    """
    General-purpose input sanitization function.

    Args:
        input_data: User input data to sanitize

    Returns:
        Sanitized data safe for processing and logging
    """
    if isinstance(input_data, str):
        return SecureLogger.sanitize_input(input_data)
    elif isinstance(input_data, dict):
        return {key: sanitize_user_input(value) for key, value in input_data.items()}
    elif isinstance(input_data, (list, tuple)):
        return type(input_data)(sanitize_user_input(item) for item in input_data)
    else:
        return SecureLogger.sanitize_input(input_data)


# Export commonly used functions
__all__ = [
    "SecureLogger",
    "get_secure_logger",
    "secure_log_decorator",
    "SecureRandom",
    "sanitize_user_input",
]
