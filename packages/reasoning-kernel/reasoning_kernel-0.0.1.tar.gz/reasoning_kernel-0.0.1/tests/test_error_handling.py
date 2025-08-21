"""
Comprehensive tests for the MSA Reasoning Kernel exception system.

Tests cover:
- Exception hierarchy and inheritance
- Error context tracking and correlation IDs
- Error categorization and severity levels
- User-friendly and developer messages
- HTTP status code mapping
- Error handling utilities and decorators
- Legacy exception compatibility
"""

import pytest
import uuid
from unittest.mock import patch

from reasoning_kernel.core.exceptions import (
    MSAError,
    ValidationError,
    SecurityError,
    TimeoutError,
    RateLimitError,
    MSAPipelineError,
    DatabaseError,
    ConfigurationError,
    ServiceError,
    ErrorContext,
    ErrorSeverity,
    ErrorCategory,
    ErrorHandler,
    handle_exceptions,
    # Legacy aliases
    DaytonaServiceError,
    StageExecutionError,
    StageValidationError,
    CircuitBreakerError,
    GracefulDegradationError,
)
from reasoning_kernel.core.constants import (
    ERROR_VALIDATION_FAILED,
    ERROR_TIMEOUT,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
)


class TestErrorContext:
    """Test error context functionality."""

    def test_error_context_creation(self):
        """Test creating error context with default values."""
        context = ErrorContext()

        assert context.correlation_id is not None
        assert len(context.correlation_id) == 36  # UUID4 length
        assert context.timestamp > 0
        assert context.operation is None
        assert context.user_id is None
        assert context.additional_data == {}

    def test_error_context_with_data(self):
        """Test creating error context with provided data."""
        context = ErrorContext(
            operation="test_operation", user_id="user123", session_id="session456", additional_data={"key": "value"}
        )

        assert context.operation == "test_operation"
        assert context.user_id == "user123"
        assert context.session_id == "session456"
        assert context.additional_data["key"] == "value"

    def test_error_context_to_dict(self):
        """Test converting error context to dictionary."""
        context = ErrorContext(operation="test_op", user_id="user123", additional_data={"test": "data"})

        result = context.to_dict()

        assert result["operation"] == "test_op"
        assert result["user_id"] == "user123"
        assert result["additional_data"]["test"] == "data"
        assert "correlation_id" in result
        assert "timestamp" in result


class TestMSAError:
    """Test base MSA error functionality."""

    def test_basic_msa_error(self):
        """Test creating basic MSA error."""
        error = MSAError("Test error message")

        assert str(error).startswith("[INTERNAL_SERVER_ERROR] Test error message")
        assert error.error_category == ErrorCategory.INTERNAL
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.http_status == HTTP_INTERNAL_SERVER_ERROR
        assert error.user_message == "An error occurred. Please try again later."
        assert not error.recoverable

    def test_msa_error_with_context(self):
        """Test MSA error with custom context."""
        context = ErrorContext(operation="test_op", user_id="user123")
        error = MSAError("Test error", context=context)

        assert error.context.operation == "test_op"
        assert error.context.user_id == "user123"

    def test_msa_error_to_dict(self):
        """Test converting MSA error to dictionary."""
        error = MSAError("Test error", error_code="TEST_ERROR", user_message="User friendly message", recoverable=True)

        result = error.to_dict()

        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "User friendly message"
        assert result["error"]["developer_message"] == "Test error"
        assert result["error"]["recoverable"] is True
        assert "correlation_id" in result["error"]

    @patch("reasoning_kernel.core.exceptions.logger")
    def test_msa_error_logging(self, mock_logger):
        """Test that MSA errors are automatically logged."""
        MSAError("Test error")

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "MSA Error: Test error" in call_args[0][0]


class TestSpecificExceptions:
    """Test specific exception types."""

    def test_validation_error(self):
        """Test ValidationError creation and properties."""
        field_errors = {"field1": ["error1", "error2"], "field2": ["error3"]}
        error = ValidationError("Validation failed", field_errors=field_errors)

        assert error.error_category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.LOW
        assert error.http_status == HTTP_BAD_REQUEST
        assert error.field_errors == field_errors
        assert error.error_code == ERROR_VALIDATION_FAILED

    def test_security_error(self):
        """Test SecurityError creation and properties."""
        error = SecurityError("Security violation detected")

        assert error.error_category == ErrorCategory.SECURITY
        assert error.severity == ErrorSeverity.HIGH
        assert "Access denied" in error.user_message

    def test_timeout_error(self):
        """Test TimeoutError creation and properties."""
        error = TimeoutError("Operation timed out", timeout_duration=30.0)

        assert error.error_category == ErrorCategory.TIMEOUT
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.timeout_duration == 30.0
        assert error.recoverable is True
        assert error.error_code == ERROR_TIMEOUT

    def test_rate_limit_error(self):
        """Test RateLimitError creation and properties."""
        error = RateLimitError("Rate limit exceeded", retry_after=60)

        assert error.error_category == ErrorCategory.RATE_LIMIT
        assert error.retry_after == 60
        assert error.recoverable is True

    def test_msa_pipeline_error(self):
        """Test MSAPipelineError creation and properties."""
        stage_data = {"stage_info": "test_data"}
        error = MSAPipelineError("Pipeline failed", stage="knowledge_extraction", stage_data=stage_data)

        assert error.error_category == ErrorCategory.MSA_PIPELINE
        assert error.stage == "knowledge_extraction"
        assert error.stage_data == stage_data
        assert error.recoverable is True

    def test_database_error(self):
        """Test DatabaseError creation and properties."""
        error = DatabaseError("Database connection failed", query="SELECT * FROM table")

        assert error.error_category == ErrorCategory.DATABASE
        assert error.query == "SELECT * FROM table"
        assert error.recoverable is True

    def test_service_error(self):
        """Test ServiceError creation and properties."""
        error = ServiceError("External service failed", service_name="external_api", service_endpoint="/api/v1/test")

        assert error.error_category == ErrorCategory.SERVICE
        assert error.service_name == "external_api"
        assert error.service_endpoint == "/api/v1/test"
        assert error.recoverable is True


class TestLegacyCompatibility:
    """Test legacy exception compatibility."""

    def test_legacy_aliases_exist(self):
        """Test that legacy exception aliases exist."""
        # These should not raise ImportError
        assert DaytonaServiceError is ServiceError
        assert StageExecutionError is MSAPipelineError
        assert StageValidationError is ValidationError
        assert CircuitBreakerError is ServiceError
        assert GracefulDegradationError is ServiceError

    def test_legacy_daytona_service_error(self):
        """Test DaytonaServiceError compatibility."""
        error = DaytonaServiceError("Daytona service failed")
        assert isinstance(error, ServiceError)
        assert error.error_category == ErrorCategory.SERVICE

    def test_legacy_stage_execution_error(self):
        """Test StageExecutionError compatibility."""
        error = StageExecutionError("Stage execution failed")
        assert isinstance(error, MSAPipelineError)
        assert error.error_category == ErrorCategory.MSA_PIPELINE


class TestErrorHandler:
    """Test error handling utilities."""

    def test_create_context(self):
        """Test creating error context using ErrorHandler."""
        context = ErrorHandler.create_context(
            operation="test_op", user_id="user123", component="test_component", custom_field="custom_value"
        )

        assert context.operation == "test_op"
        assert context.user_id == "user123"
        assert context.component == "test_component"
        assert context.additional_data["custom_field"] == "custom_value"

    def test_handle_validation_error_string(self):
        """Test handling validation error with string message."""
        error = ErrorHandler.handle_validation_error("Invalid input")

        assert isinstance(error, ValidationError)
        assert error.message == "Invalid input"
        assert error.field_errors == {}

    def test_handle_validation_error_dict(self):
        """Test handling validation error with field errors dictionary."""
        field_errors = {"email": ["Invalid format"], "age": ["Must be positive"]}
        error = ErrorHandler.handle_validation_error(field_errors)

        assert isinstance(error, ValidationError)
        assert error.message == "Validation failed"
        assert error.field_errors == field_errors

    def test_handle_timeout(self):
        """Test handling timeout error."""
        error = ErrorHandler.handle_timeout("database_query", 30.0)

        assert isinstance(error, TimeoutError)
        assert "database_query" in error.message
        assert error.timeout_duration == 30.0

    def test_handle_service_error(self):
        """Test handling service error."""
        cause = Exception("Connection failed")
        error = ErrorHandler.handle_service_error("external_api", "fetch_data", cause)

        assert isinstance(error, ServiceError)
        assert "external_api" in error.message
        assert "fetch_data" in error.message
        assert error.cause is cause

    def test_wrap_exception_value_error(self):
        """Test wrapping ValueError as ValidationError."""
        cause = ValueError("Invalid value")
        error = ErrorHandler.wrap_exception(cause)

        assert isinstance(error, ValidationError)
        assert error.cause is cause

    def test_wrap_exception_key_error(self):
        """Test wrapping KeyError as ConfigurationError."""
        cause = KeyError("missing_key")
        error = ErrorHandler.wrap_exception(cause)

        assert isinstance(error, ConfigurationError)
        assert error.cause is cause

    def test_wrap_exception_generic(self):
        """Test wrapping generic exception as MSAError."""
        cause = RuntimeError("Generic error")
        error = ErrorHandler.wrap_exception(cause)

        assert isinstance(error, MSAError)
        assert error.cause is cause


class TestExceptionDecorator:
    """Test exception handling decorator."""

    def test_handle_exceptions_decorator_success(self):
        """Test decorator with successful function execution."""

        @handle_exceptions(context_component="test_component")
        def successful_function(x, y):
            return x + y

        result = successful_function(2, 3)
        assert result == 5

    def test_handle_exceptions_decorator_msa_error(self):
        """Test decorator re-raises MSAError unchanged."""

        @handle_exceptions(context_component="test_component")
        def function_with_msa_error():
            raise ValidationError("Validation failed")

        with pytest.raises(ValidationError) as exc_info:
            function_with_msa_error()

        assert exc_info.value.message == "Validation failed"

    def test_handle_exceptions_decorator_generic_error(self):
        """Test decorator wraps generic exceptions."""

        @handle_exceptions(context_component="test_component")
        def function_with_generic_error():
            raise ValueError("Generic error")

        with pytest.raises(ValidationError) as exc_info:
            function_with_generic_error()

        assert "Generic error" in str(exc_info.value)
        assert exc_info.value.context.component == "test_component"
        assert exc_info.value.context.operation == "function_with_generic_error"

    def test_handle_exceptions_decorator_no_reraise(self):
        """Test decorator without reraising exceptions."""

        @handle_exceptions(reraise=False)
        def function_with_error():
            raise ValueError("Error message")

        result = function_with_error()
        assert isinstance(result, ValidationError)
        assert "Error message" in str(result)


class TestExceptionIntegration:
    """Integration tests for exception system."""

    def test_error_context_correlation_across_exceptions(self):
        """Test that error context can be passed between exceptions."""
        original_context = ErrorContext(operation="original_op", user_id="user123", session_id="session456")

        # Create first error with context
        first_error = ValidationError("First error", context=original_context)

        # Create second error using same context
        second_error = ServiceError("Second error", context=first_error.context)

        # Both errors should have same correlation ID
        assert first_error.context.correlation_id == second_error.context.correlation_id
        assert first_error.context.user_id == second_error.context.user_id
        assert first_error.context.session_id == second_error.context.session_id

    def test_error_chaining_with_cause(self):
        """Test error chaining with cause tracking."""
        original_error = ValueError("Original error")
        wrapped_error = ErrorHandler.wrap_exception(original_error, message_override="Wrapped error")

        assert wrapped_error.cause is original_error
        assert "Wrapped error" in wrapped_error.message

    @patch("reasoning_kernel.core.exceptions.logger")
    def test_comprehensive_error_logging(self, mock_logger):
        """Test comprehensive error logging with all fields."""
        context = ErrorContext(operation="test_operation", user_id="user123", component="test_component")

        MSAPipelineError("Pipeline stage failed", stage="knowledge_extraction", context=context, recoverable=True)

        # Verify logging was called
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args

        # Check log message
        assert "MSA Error: Pipeline stage failed" in call_args[0][0]

        # Check log data structure
        log_data = call_args[1]["extra"]
        assert log_data["error_class"] == "MSAPipelineError"
        assert log_data["error_category"] == "msa_pipeline"
        assert log_data["severity"] == "high"
        assert log_data["recoverable"] is True
        assert log_data["context"]["operation"] == "test_operation"
        assert log_data["context"]["user_id"] == "user123"
        assert log_data["context"]["component"] == "test_component"


# Performance and edge case tests
class TestExceptionPerformance:
    """Test exception system performance and edge cases."""

    def test_error_context_uuid_generation(self):
        """Test that error contexts generate valid UUIDs."""
        contexts = [ErrorContext() for _ in range(100)]
        correlation_ids = [ctx.correlation_id for ctx in contexts]

        # All should be valid UUIDs
        for cid in correlation_ids:
            uuid.UUID(cid)  # This will raise ValueError if invalid

        # All should be unique
        assert len(set(correlation_ids)) == 100

    def test_large_error_context_data(self):
        """Test error context with large additional data."""
        large_data = {"key_" + str(i): "value_" + str(i) for i in range(1000)}
        context = ErrorContext(additional_data=large_data)

        result_dict = context.to_dict()
        assert len(result_dict["additional_data"]) == 1000

    def test_error_serialization_edge_cases(self):
        """Test error serialization with edge case values."""
        error = MSAError("", retry_after=0, context=ErrorContext(additional_data={"none_value": None}))  # Empty message

        result = error.to_dict()
        assert result["error"]["retry_after"] == 0
        assert "correlation_id" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__])
