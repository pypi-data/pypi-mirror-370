"""
Unit tests for enhanced Daytona service with retry logic and error handling.

Tests cover:
- Retry mechanisms with exponential backoff and jitter
- Structured error handling and custom exceptions
- Timeout handling for different operations
- Transient failure scenarios
- Error recovery and fallback mechanisms
"""

import asyncio
import os
import pytest
import time
from unittest.mock import Mock, patch

import sys

sys.path.append("/home/runner/work/Reasoning-Kernel/Reasoning-Kernel")

from reasoning_kernel.services.daytona_service import (
    DaytonaService,
    SandboxConfig,
    RetryConfig,
    SandboxStatus,
    ExecutionResult,
    DaytonaServiceError,
    DaytonaAPIError,
    DaytonaSandboxError,
    DaytonaTimeoutError,
    DaytonaConnectionError,
    DaytonaValidationError,
    with_retry,
)


class TestDaytonaExceptions:
    """Test custom exception classes and their structured error handling"""

    def test_base_exception_creation(self):
        """Test base DaytonaServiceError creation with details"""
        error = DaytonaServiceError("Test error", {"key": "value"})
        assert error.message == "Test error"
        assert error.details == {"key": "value"}
        assert isinstance(error.timestamp, float)
        assert error.timestamp > 0

    def test_api_error_creation(self):
        """Test DaytonaAPIError with status code and response body"""
        error = DaytonaAPIError("API failed", status_code=500, response_body="Internal error")
        assert error.message == "API failed"
        assert error.status_code == 500
        assert error.response_body == "Internal error"
        assert error.details["status_code"] == 500
        assert error.details["response_body"] == "Internal error"

    def test_sandbox_error_creation(self):
        """Test DaytonaSandboxError with sandbox context"""
        error = DaytonaSandboxError("Sandbox failed", sandbox_id="test-123", operation="create")
        assert error.message == "Sandbox failed"
        assert error.sandbox_id == "test-123"
        assert error.operation == "create"

    def test_timeout_error_creation(self):
        """Test DaytonaTimeoutError with timeout context"""
        error = DaytonaTimeoutError("Operation timed out", timeout_seconds=30.0, operation="execute")
        assert error.message == "Operation timed out"
        assert error.timeout_seconds == 30.0
        assert error.operation == "execute"

    def test_connection_error_creation(self):
        """Test DaytonaConnectionError with connection context"""
        error = DaytonaConnectionError("Connection failed", endpoint="api.daytona.io", retry_count=3)
        assert error.message == "Connection failed"
        assert error.endpoint == "api.daytona.io"
        assert error.retry_count == 3

    def test_validation_error_creation(self):
        """Test DaytonaValidationError with validation details"""
        validation_errors = ["Invalid code", "Missing imports"]
        error = DaytonaValidationError("Validation failed", validation_errors=validation_errors)
        assert error.message == "Validation failed"
        assert error.validation_errors == validation_errors


class TestRetryConfiguration:
    """Test retry configuration and behavior"""

    def test_default_retry_config(self):
        """Test default retry configuration values"""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter_factor == 0.1
        assert DaytonaConnectionError in config.retry_on_exceptions
        assert DaytonaAPIError in config.retry_on_exceptions
        assert DaytonaTimeoutError in config.retry_on_exceptions

    def test_custom_retry_config(self):
        """Test custom retry configuration"""
        config = RetryConfig(max_attempts=5, base_delay=2.0, max_delay=120.0, exponential_base=3.0, jitter_factor=0.2)
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter_factor == 0.2


class TestRetryDecorator:
    """Test the retry decorator with various scenarios"""

    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self):
        """Test that successful operations don't trigger retries"""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3))
        async def successful_operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_operation()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Test retry behavior on connection errors"""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.01))
        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise DaytonaConnectionError("Connection failed")
            return "success after retries"

        result = await failing_operation()
        assert result == "success after retries"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded"""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=2, base_delay=0.01))
        async def always_failing_operation():
            nonlocal call_count
            call_count += 1
            raise DaytonaAPIError("API always fails", status_code=500)

        with pytest.raises(DaytonaAPIError) as exc_info:
            await always_failing_operation()

        assert call_count == 2
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["retry_attempts"] == 2

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self):
        """Test that non-retryable exceptions fail immediately"""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3))
        async def non_retryable_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")

        with pytest.raises(ValueError):
            await non_retryable_error()

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test that exponential backoff timing is approximately correct"""
        call_times = []

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.1, jitter_factor=0.0))
        async def timing_test():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise DaytonaConnectionError("Test timing")
            return "success"

        start_time = time.time()
        await timing_test()

        # Check timing between calls (accounting for some variance)
        assert len(call_times) == 3
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        # First delay should be ~0.1s, second delay should be ~0.2s
        assert 0.08 <= delay1 <= 0.15  # Allow some variance
        assert 0.18 <= delay2 <= 0.25


class TestSandboxConfiguration:
    """Test sandbox configuration with enhanced features"""

    def test_default_config(self):
        """Test default sandbox configuration"""
        config = SandboxConfig()
        assert config.cpu_limit == 2
        assert config.memory_limit_mb == 512
        assert config.execution_timeout == 30
        assert config.api_call_timeout == 30.0
        assert config.sandbox_creation_timeout == 60.0
        assert config.code_execution_timeout == 300.0
        assert config.cleanup_timeout == 30.0
        assert isinstance(config.retry_config, RetryConfig)
        assert len(config.allowed_imports) > 0

    def test_custom_config(self):
        """Test custom sandbox configuration"""
        custom_retry = RetryConfig(max_attempts=5)
        config = SandboxConfig(cpu_limit=4, memory_limit_mb=1024, api_call_timeout=60.0, retry_config=custom_retry)
        assert config.cpu_limit == 4
        assert config.memory_limit_mb == 1024
        assert config.api_call_timeout == 60.0
        assert config.retry_config.max_attempts == 5


class TestDaytonaServiceInitialization:
    """Test Daytona service initialization and client setup"""

    def test_initialization_without_api_key(self):
        """Test service initialization when API key is not available"""
        with patch.dict(os.environ, {}, clear=True):
            service = DaytonaService()
            assert not service.daytona_available
            assert service.daytona_client is None
            assert service.api_key is None

    def test_initialization_with_invalid_api_key(self):
        """Test service initialization with invalid API key"""
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "short"}, clear=True):
            with pytest.raises(DaytonaValidationError) as exc_info:
                DaytonaService()

            assert "Invalid API key format" in str(exc_info.value)
            assert "API key must be at least 10 characters long" in exc_info.value.validation_errors

    def test_initialization_with_valid_api_key(self):
        """Test service initialization with valid API key"""
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "valid_api_key_123"}, clear=True):
            with patch("reasoning_kernel.services.daytona_service.DaytonaService._initialize_client"):
                service = DaytonaService()
                assert service.api_key == "valid_api_key_123"

    def test_initialization_with_connection_error(self):
        """Test service initialization when connection fails"""
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "valid_api_key_123"}, clear=True):
            with patch("reasoning_kernel.services.daytona_service.Daytona") as mock_daytona:
                mock_daytona.side_effect = ConnectionError("Network error")

                with pytest.raises(DaytonaConnectionError) as exc_info:
                    DaytonaService()

                assert "Failed to initialize Daytona client" in str(exc_info.value)


class TestSandboxOperations:
    """Test sandbox creation, execution, and cleanup operations"""

    @pytest.fixture
    def service_with_api_key(self):
        """Create a service instance with valid API key for testing"""
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "test_api_key_123"}, clear=True):
            with patch("reasoning_kernel.services.daytona_service.DaytonaService._initialize_client"):
                service = DaytonaService()
                service.daytona_available = True
                service.use_sdk = False
                return service

    @pytest.mark.asyncio
    async def test_sandbox_creation_success(self, service_with_api_key):
        """Test successful sandbox creation"""
        service = service_with_api_key

        # Mock the API response
        mock_sandbox_data = {"id": "test_sandbox_123", "status": "ready", "created_at": time.time()}

        with patch.object(service, "_create_sandbox_via_api", return_value=mock_sandbox_data):
            result = await service.create_sandbox()

            assert result is True
            assert service.current_sandbox == mock_sandbox_data
            assert "test_sandbox_123" in service.sandbox_registry

    @pytest.mark.asyncio
    async def test_sandbox_creation_with_timeout(self, service_with_api_key):
        """Test sandbox creation timeout handling"""
        service = service_with_api_key
        service.config.sandbox_creation_timeout = 0.1

        async def slow_creation():
            await asyncio.sleep(0.2)  # Longer than timeout
            return {"id": "test"}

        with patch.object(service, "_create_sandbox_via_api", side_effect=slow_creation):
            with pytest.raises(DaytonaTimeoutError) as exc_info:
                await service.create_sandbox()

            assert exc_info.value.operation == "create_sandbox_api"
            assert exc_info.value.timeout_seconds == 0.1

    @pytest.mark.asyncio
    async def test_sandbox_creation_with_retries(self, service_with_api_key):
        """Test sandbox creation with retry on transient failures"""
        service = service_with_api_key
        service.config.retry_config = RetryConfig(max_attempts=3, base_delay=0.01)

        call_count = 0

        async def failing_then_succeeding_creation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise DaytonaAPIError("Transient API error", status_code=503)
            return {"id": "test_sandbox_retry", "status": "ready", "created_at": time.time()}

        with patch.object(service, "_create_sandbox_via_api", side_effect=failing_then_succeeding_creation):
            result = await service.create_sandbox()

            assert result is True
            assert call_count == 3
            assert service.current_sandbox["id"] == "test_sandbox_retry"

    @pytest.mark.asyncio
    async def test_code_execution_success(self, service_with_api_key):
        """Test successful code execution"""
        service = service_with_api_key
        service.current_sandbox = {"id": "test_sandbox"}
        service.daytona_client = Mock()

        # Mock execution response
        mock_response = Mock()
        mock_response.exit_code = 0
        mock_response.result = "Hello, World!"

        service.current_sandbox = Mock()
        service.current_sandbox.process.code_run.return_value = mock_response
        service.current_sandbox.id = "test_sandbox"

        result = await service.execute_code("print('Hello, World!')")

        assert isinstance(result, ExecutionResult)
        assert result.exit_code == 0
        assert result.stdout == "Hello, World!"
        assert result.status == SandboxStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_code_execution_validation_error(self, service_with_api_key):
        """Test code execution with validation errors"""
        service = service_with_api_key

        # Test empty code
        result = await service.execute_code("")
        assert isinstance(result, ExecutionResult)
        assert result.exit_code == 1
        assert "Code cannot be empty" in result.stderr

    @pytest.mark.asyncio
    async def test_code_execution_timeout(self, service_with_api_key):
        """Test code execution timeout handling"""
        service = service_with_api_key
        service.current_sandbox = {"id": "test_sandbox"}
        service.daytona_client = Mock()
        service.config.code_execution_timeout = 0.1

        async def slow_execution():
            await asyncio.sleep(0.2)  # Longer than timeout
            return Mock(exit_code=0, result="slow result")

        with patch.object(service, "_execute_in_daytona_core", side_effect=slow_execution):
            with pytest.raises(DaytonaTimeoutError) as exc_info:
                await service.execute_code("time.sleep(10)")

            assert exc_info.value.operation == "execute_code"

    @pytest.mark.asyncio
    async def test_local_execution_fallback(self, service_with_api_key):
        """Test fallback to local execution when Daytona is unavailable"""
        service = service_with_api_key
        service.daytona_client = None
        service.current_sandbox = None

        # Mock subprocess for local execution
        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = ("Hello, World!", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = await service.execute_code("print('Hello, World!')")

            assert isinstance(result, ExecutionResult)
            assert result.exit_code == 0
            assert result.stdout == "Hello, World!"
            assert result.metadata["sandbox_type"] == "local_fallback"

    @pytest.mark.asyncio
    async def test_cleanup_success(self, service_with_api_key):
        """Test successful sandbox cleanup"""
        service = service_with_api_key
        service.current_sandbox = {"id": "test_sandbox", "delete": Mock()}

        result = await service.cleanup_sandbox()

        assert result is True
        assert service.current_sandbox is None

    @pytest.mark.asyncio
    async def test_cleanup_timeout(self, service_with_api_key):
        """Test cleanup timeout handling"""
        service = service_with_api_key
        service.current_sandbox = {"id": "test_sandbox"}
        service.config.cleanup_timeout = 0.1

        async def slow_cleanup():
            await asyncio.sleep(0.2)  # Longer than timeout

        with patch.object(service, "_cleanup_sandbox_core", side_effect=slow_cleanup):
            with pytest.raises(DaytonaTimeoutError) as exc_info:
                await service.cleanup_sandbox()

            assert exc_info.value.operation == "cleanup_sandbox"


class TestTransientFailureScenarios:
    """Test various transient failure scenarios and recovery mechanisms"""

    @pytest.fixture
    def service_with_simulated_failures(self):
        """Create a service with simulated failure environment"""
        with patch.dict(
            os.environ, {"DAYTONA_API_KEY": "test_api_key_123", "DAYTONA_SIMULATE_FAILURES": "true"}, clear=True
        ):
            with patch("reasoning_kernel.services.daytona_service.DaytonaService._initialize_client"):
                service = DaytonaService()
                service.daytona_available = True
                service.use_sdk = False
                return service

    @pytest.mark.asyncio
    async def test_intermittent_api_failures(self, service_with_simulated_failures):
        """Test handling of intermittent API failures"""
        service = service_with_simulated_failures
        service.config.retry_config = RetryConfig(max_attempts=5, base_delay=0.01)

        # Simulate API that fails sometimes but eventually succeeds
        call_count = 0

        async def intermittent_api():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise DaytonaAPIError("Service unavailable", status_code=503)
            return {"id": f"sandbox_success_{call_count}", "status": "ready", "created_at": time.time()}

        with patch.object(service, "_create_sandbox_via_api", side_effect=intermittent_api):
            result = await service.create_sandbox()

            assert result is True
            assert call_count == 3
            assert "sandbox_success_3" in service.current_sandbox["id"]

    @pytest.mark.asyncio
    async def test_network_connection_issues(self, service_with_simulated_failures):
        """Test handling of network connection issues"""
        service = service_with_simulated_failures
        service.config.retry_config = RetryConfig(max_attempts=4, base_delay=0.01)

        call_count = 0

        async def network_issues():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise DaytonaConnectionError("Network timeout", endpoint="api.daytona.io")
            return {"id": "network_recovery_success", "status": "ready", "created_at": time.time()}

        with patch.object(service, "_create_sandbox_via_api", side_effect=network_issues):
            result = await service.create_sandbox()

            assert result is True
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_service_overload_recovery(self, service_with_simulated_failures):
        """Test recovery from service overload scenarios"""
        service = service_with_simulated_failures
        service.config.retry_config = RetryConfig(max_attempts=6, base_delay=0.01, max_delay=0.1)

        failure_count = 0

        async def overload_scenario():
            nonlocal failure_count
            failure_count += 1

            # Simulate service overload with rate limiting
            if failure_count <= 4:
                status_code = 429 if failure_count <= 2 else 503
                raise DaytonaAPIError(f"Service overloaded (attempt {failure_count})", status_code=status_code)

            return {"id": "overload_recovery", "status": "ready", "created_at": time.time()}

        with patch.object(service, "_create_sandbox_via_api", side_effect=overload_scenario):
            result = await service.create_sandbox()

            assert result is True
            assert failure_count == 5
            assert service.current_sandbox["id"] == "overload_recovery"


class TestHealthCheckAndMonitoring:
    """Test health check and monitoring features"""

    @pytest.fixture
    def configured_service(self):
        """Create a properly configured service for health testing"""
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "test_api_key_123"}, clear=True):
            with patch("reasoning_kernel.services.daytona_service.DaytonaService._initialize_client"):
                service = DaytonaService()
                service.daytona_available = True
                service.api_key = "test_api_key_123"
                return service

    @pytest.mark.asyncio
    async def test_health_check_healthy_service(self, configured_service):
        """Test health check on a healthy service"""
        service = configured_service

        health_result = await service.health_check()

        assert health_result["overall_status"] == "healthy"
        assert health_result["service"] == "DaytonaService"
        assert health_result["version"] == "enhanced_v1.0"
        assert health_result["api_connection"] == "available"
        assert health_result["authentication"] == "configured"
        assert "check_duration" in health_result
        assert isinstance(health_result["check_duration"], float)

    def test_get_status_comprehensive(self, configured_service):
        """Test comprehensive status reporting"""
        service = configured_service
        service.current_sandbox = {"id": "test_sandbox", "status": "active", "created_at": time.time()}

        status = service.get_status()

        assert status["daytona_available"] is True
        assert status["sandbox_active"] is True
        assert "enhanced_features" in status
        assert status["enhanced_features"]["retry_logic"] is True
        assert status["enhanced_features"]["structured_errors"] is True
        assert status["enhanced_features"]["timeout_handling"] is True
        assert status["enhanced_features"]["jitter_backoff"] is True
        assert "current_sandbox" in status
        assert status["current_sandbox"]["id"] == "test_sandbox"

    def test_error_statistics(self, configured_service):
        """Test error statistics reporting"""
        service = configured_service

        stats = service.get_error_statistics()

        assert stats["error_tracking_enabled"] is True
        assert "DaytonaServiceError" in stats["structured_exceptions"]
        assert "DaytonaAPIError" in stats["structured_exceptions"]
        assert "DaytonaSandboxError" in stats["structured_exceptions"]
        assert "DaytonaTimeoutError" in stats["structured_exceptions"]
        assert "DaytonaConnectionError" in stats["structured_exceptions"]
        assert "DaytonaValidationError" in stats["structured_exceptions"]
        assert stats["retry_configuration"] is not None


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_complete_sandbox_lifecycle(self):
        """Test complete sandbox lifecycle with error handling"""
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "integration_test_key"}, clear=True):
            with patch("reasoning_kernel.services.daytona_service.DaytonaService._initialize_client"):
                service = DaytonaService()
                service.daytona_available = True
                service.use_sdk = False

                # Mock successful operations
                mock_sandbox = {"id": "integration_test", "status": "ready", "created_at": time.time()}

                async def mock_create():
                    return mock_sandbox

                with patch.object(service, "_create_sandbox_via_api", side_effect=mock_create):
                    # Test sandbox creation
                    created = await service.create_sandbox()
                    assert created is True
                    assert service.current_sandbox == mock_sandbox

                    # Test health check
                    health = await service.health_check()
                    assert health["overall_status"] == "healthy"

                    # Test cleanup
                    with patch.object(service, "_cleanup_sandbox_core"):
                        cleaned = await service.cleanup_sandbox()
                        assert cleaned is True
                        assert service.current_sandbox is None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
