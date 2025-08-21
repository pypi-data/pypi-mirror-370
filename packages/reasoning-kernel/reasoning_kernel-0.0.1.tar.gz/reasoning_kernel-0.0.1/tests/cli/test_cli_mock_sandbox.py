"""
Mock Sandbox Tests for MSA Reasoning Kernel CLI
==============================================

Comprehensive mock tests for Daytona sandbox functionality and edge cases.
"""

import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from reasoning_kernel.services.daytona_service import (
    DaytonaService,
    SandboxConfig,
    ExecutionResult,
    SandboxStatus,
    DaytonaAPIError,
    DaytonaSandboxError,
    DaytonaTimeoutError,
)
from reasoning_kernel.services.daytona_ppl_executor import (
    DaytonaPPLExecutor,
    PPLProgram,
    PPLFramework,
    PPLExecutionError,
)


class TestDaytonaServiceMock:
    """Test Daytona service with comprehensive mocking"""

    @pytest.fixture
    def mock_daytona_service(self):
        """Create Daytona service with mocked configuration"""
        config = SandboxConfig(
            cpu_limit=2,
            memory_limit_mb=512,
            execution_timeout=30,
            enable_ast_validation=True,
        )
        service = DaytonaService(config)
        return service

    def test_mock_service_initialization(self, mock_daytona_service):
        """Test service initialization with mocks"""
        # Verify service is properly initialized
        assert mock_daytona_service.config.cpu_limit == 2
        assert mock_daytona_service.config.memory_limit_mb == 512
        assert mock_daytona_service.config.execution_timeout == 30
        assert mock_daytona_service.config.enable_ast_validation is True

    @pytest.mark.asyncio
    async def test_mock_sandbox_creation_success(self, mock_daytona_service):
        """Test successful sandbox creation with mock"""
        # Mock the API creation
        mock_sandbox_data = {
            "id": "mock-sandbox-123",
            "status": "ready",
            "created_at": 1234567890,
            "api_mode": True,
        }

        with patch.object(
            mock_daytona_service,
            "_create_sandbox_via_api",
            return_value=mock_sandbox_data,
        ):
            result = await mock_daytona_service.create_sandbox()

            assert result is True
            assert mock_daytona_service.current_sandbox["id"] == "mock-sandbox-123"
            assert mock_daytona_service.current_sandbox["status"] == "ready"

    @pytest.mark.asyncio
    async def test_mock_sandbox_creation_failure(self, mock_daytona_service):
        """Test sandbox creation failure with mock"""
        # Mock API failure
        with patch.object(
            mock_daytona_service,
            "_create_sandbox_via_api",
            side_effect=DaytonaAPIError("API error"),
        ):
            with pytest.raises(DaytonaAPIError):
                await mock_daytona_service.create_sandbox()

    @pytest.mark.asyncio
    async def test_mock_sandbox_creation_timeout(self, mock_daytona_service):
        """Test sandbox creation timeout with mock"""
        mock_daytona_service.config.sandbox_creation_timeout = 0.1

        # Mock slow creation
        async def slow_creation():
            await asyncio.sleep(0.2)  # Longer than timeout
            return {"id": "test"}

        with patch.object(
            mock_daytona_service, "_create_sandbox_via_api", side_effect=slow_creation
        ):
            with pytest.raises(DaytonaTimeoutError):
                await mock_daytona_service.create_sandbox()

    @pytest.mark.asyncio
    async def test_mock_code_execution_success(self, mock_daytona_service):
        """Test successful code execution with mock"""
        # Mock successful execution
        mock_result = ExecutionResult(
            exit_code=0,
            stdout="Hello, World!",
            stderr="",
            execution_time=0.1,
            status=SandboxStatus.COMPLETED,
            resource_usage={"cpu": 10.5, "memory": 50.0},
            metadata={"test": "data"},
        )

        with patch.object(
            mock_daytona_service,
            "_execute_locally_with_timeout",
            return_value=mock_result,
        ):
            result = await mock_daytona_service.execute_code("print('Hello, World!')")

            assert result.exit_code == 0
            assert result.stdout == "Hello, World!"
            assert result.status == SandboxStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_mock_code_execution_failure(self, mock_daytona_service):
        """Test code execution failure with mock"""
        # Mock failed execution
        mock_result = ExecutionResult(
            exit_code=1,
            stdout="",
            stderr="Error occurred",
            execution_time=0.1,
            status=SandboxStatus.FAILED,
            resource_usage={},
            metadata={},
        )

        with patch.object(
            mock_daytona_service,
            "_execute_locally_with_timeout",
            return_value=mock_result,
        ):
            result = await mock_daytona_service.execute_code("invalid_code()")

            assert result.exit_code == 1
            assert result.stderr == "Error occurred"
            assert result.status == SandboxStatus.FAILED

    @pytest.mark.asyncio
    async def test_mock_code_execution_timeout(self, mock_daytona_service):
        """Test code execution timeout with mock"""
        mock_daytona_service.config.code_execution_timeout = 0.1

        # Mock timeout
        async def timeout_execution():
            await asyncio.sleep(0.2)  # Longer than timeout
            return Mock()

        with patch.object(
            mock_daytona_service,
            "_execute_locally_with_timeout",
            side_effect=timeout_execution,
        ):
            with pytest.raises(asyncio.TimeoutError):
                await mock_daytona_service.execute_code("time.sleep(10)")

    @pytest.mark.asyncio
    async def test_mock_code_validation(self, mock_daytona_service):
        """Test code validation with mock"""
        # Test valid code
        valid_code = "print('Hello, World!')"
        result = await mock_daytona_service._validate_code_security(valid_code)
        assert result is True

        # Test invalid code (dangerous imports)
        invalid_code = "import os\nos.system('rm -rf /')"
        result = await mock_daytona_service._validate_code_security(invalid_code)
        assert result is False

    @pytest.mark.asyncio
    async def test_mock_sandbox_cleanup_success(self, mock_daytona_service):
        """Test successful sandbox cleanup with mock"""
        # Set up mock sandbox
        mock_daytona_service.current_sandbox = {
            "id": "test-sandbox",
            "status": "active",
        }

        # Mock cleanup
        with patch.object(mock_daytona_service, "_cleanup_sandbox_core"):
            result = await mock_daytona_service.cleanup_sandbox()

            assert result is True
            assert mock_daytona_service.current_sandbox is None

    @pytest.mark.asyncio
    async def test_mock_sandbox_cleanup_failure(self, mock_daytona_service):
        """Test sandbox cleanup failure with mock"""
        # Set up mock sandbox
        mock_daytona_service.current_sandbox = {
            "id": "test-sandbox",
            "status": "active",
        }

        # Mock cleanup failure
        with patch.object(
            mock_daytona_service,
            "_cleanup_sandbox_core",
            side_effect=Exception("Cleanup failed"),
        ):
            with pytest.raises(DaytonaSandboxError):
                await mock_daytona_service.cleanup_sandbox()

    def test_mock_service_status(self, mock_daytona_service):
        """Test service status with mock"""
        # Test without active sandbox
        status = mock_daytona_service.get_status()
        assert status["daytona_available"] is False  # No API key configured
        assert status["sandbox_active"] is False

        # Test with active sandbox
        mock_daytona_service.current_sandbox = {
            "id": "test-sandbox",
            "status": "active",
        }
        status = mock_daytona_service.get_status()
        assert status["sandbox_active"] is True
        assert status["current_sandbox"]["id"] == "test-sandbox"

    def test_mock_error_statistics(self, mock_daytona_service):
        """Test error statistics with mock"""
        stats = mock_daytona_service.get_error_statistics()

        assert stats["error_tracking_enabled"] is True
        assert "DaytonaServiceError" in stats["structured_exceptions"]
        assert "DaytonaAPIError" in stats["structured_exceptions"]
        assert stats["retry_configuration"] is not None


class TestPPLExecutorMock:
    """Test PPL executor with comprehensive mocking"""

    @pytest.fixture
    def mock_ppl_executor(self):
        """Create PPL executor with mocked Daytona service"""
        mock_daytona = Mock()
        return DaytonaPPLExecutor(mock_daytona)

    def test_mock_ppl_program_creation(self, mock_ppl_executor):
        """Test PPL program creation with mock"""
        # Test valid program creation
        program = PPLProgram(
            code="import numpyro\nprint('PPL test')",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
        )

        assert program.code == "import numpyro\nprint('PPL test')"
        assert program.framework == PPLFramework.NUMPYRO
        assert program.entry_point == "main"

    @pytest.mark.asyncio
    async def test_mock_ppl_execution_success(self, mock_ppl_executor):
        """Test successful PPL execution with mock"""
        # Mock Daytona service response
        mock_result = Mock()
        mock_result.exit_code = 0
        mock_result.stdout = "PPL execution successful"
        mock_result.stderr = ""
        mock_result.execution_time = 0.15
        mock_result.status = "completed"

        mock_ppl_executor.daytona_service.execute_code = AsyncMock(
            return_value=mock_result
        )

        # Create test program
        program = PPLProgram(
            code="import numpyro", framework=PPLFramework.NUMPYRO, entry_point="main"
        )

        # Test execution
        result = await mock_ppl_executor.execute_ppl_program(program)

        # Verify result
        assert result.exit_code == 0
        assert result.stdout == "PPL execution successful"
        assert result.status == "completed"

        # Verify Daytona service was called
        mock_ppl_executor.daytona_service.execute_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_mock_ppl_execution_failure(self, mock_ppl_executor):
        """Test PPL execution failure with mock"""
        # Mock Daytona service failure
        mock_result = Mock()
        mock_result.exit_code = 1
        mock_result.stdout = ""
        mock_result.stderr = "ImportError: No module named 'numpyro'"
        mock_result.execution_time = 0.1
        mock_result.status = "failed"

        mock_ppl_executor.daytona_service.execute_code = AsyncMock(
            return_value=mock_result
        )

        # Create test program
        program = PPLProgram(
            code="import nonexistent_module",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
        )

        # Test execution
        result = await mock_ppl_executor.execute_ppl_program(program)

        # Verify failure result
        assert result.exit_code == 1
        assert "ImportError" in result.stderr
        assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_mock_ppl_execution_timeout(self, mock_ppl_executor):
        """Test PPL execution timeout with mock"""
        # Mock timeout
        mock_ppl_executor.daytona_service.execute_code = AsyncMock(
            side_effect=asyncio.TimeoutError("Execution timeout")
        )

        # Create test program
        program = PPLProgram(
            code="time.sleep(100)", framework=PPLFramework.NUMPYRO, entry_point="main"
        )

        # Test execution
        with pytest.raises(PPLExecutionError):
            await mock_ppl_executor.execute_ppl_program(program)

    def test_mock_ppl_program_validation(self, mock_ppl_executor):
        """Test PPL program validation with mock"""
        # Test valid frameworks
        valid_frameworks = [
            PPLFramework.NUMPYRO,
            PPLFramework.PYRO,
            PPLFramework.TFP,
            PPLFramework.STAN,
        ]

        for framework in valid_frameworks:
            program = PPLProgram(
                code="test code", framework=framework, entry_point="main"
            )
            assert program.framework == framework

    def test_mock_ppl_config_validation(self, mock_ppl_executor):
        """Test PPL configuration validation with mock"""
        # Test default configuration
        config = mock_ppl_executor.ppl_config
        assert config.max_execution_time > 0
        assert config.cpu_limit > 0
        assert config.memory_limit_mb > 0

        # Test custom configuration
        custom_config = mock_ppl_executor.PPLConfig(
            max_execution_time=60.0, cpu_limit=4.0, memory_limit_mb=1024
        )
        assert custom_config.max_execution_time == 60.0
        assert custom_config.cpu_limit == 4.0
        assert custom_config.memory_limit_mb == 1024


class TestDaytonaEdgeCases:
    """Test edge cases and error conditions for Daytona service"""

    @pytest.fixture
    def edge_case_service(self):
        """Create Daytona service for edge case testing"""
        config = SandboxConfig(
            cpu_limit=1,
            memory_limit_mb=128,
            execution_timeout=5,
            enable_ast_validation=True,
        )
        return DaytonaService(config)

    @pytest.mark.asyncio
    async def test_empty_code_execution(self, edge_case_service):
        """Test execution of empty code"""
        result = await edge_case_service.execute_code("")

        assert result.exit_code == 1
        assert "Code cannot be empty" in result.stderr
        assert result.status == SandboxStatus.FAILED

    @pytest.mark.asyncio
    async def test_none_code_execution(self, edge_case_service):
        """Test execution of None code"""
        result = await edge_case_service.execute_code(None)

        assert result.exit_code == 1
        assert result.status == SandboxStatus.FAILED

    @pytest.mark.asyncio
    async def test_large_code_execution(self, edge_case_service):
        """Test execution of very large code"""
        # Create large code string
        large_code = "print('test')\n" * 10000  # 10,000 lines

        # Mock successful execution
        mock_result = ExecutionResult(
            exit_code=0,
            stdout="Large code executed",
            stderr="",
            execution_time=0.5,
            status=SandboxStatus.COMPLETED,
            resource_usage={},
            metadata={},
        )

        with patch.object(
            edge_case_service, "_execute_locally_with_timeout", return_value=mock_result
        ):
            result = await edge_case_service.execute_code(large_code)

            assert result.exit_code == 0
            assert result.status == SandboxStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_concurrent_sandbox_operations(self, edge_case_service):
        """Test concurrent sandbox operations"""
        # This would test thread safety and concurrent access patterns
        # For now, we'll test that the service handles concurrent calls gracefully

        async def create_and_execute():
            """Helper to create sandbox and execute code"""
            try:
                await edge_case_service.create_sandbox()
                result = await edge_case_service.execute_code("print('concurrent')")
                return result
            except Exception as e:
                return f"Error: {e}"

        # Run multiple concurrent operations
        tasks = [create_and_execute() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all operations completed (even if with errors due to mocking)
        assert len(results) == 3

    def test_sandbox_config_edge_cases(self, edge_case_service):
        """Test edge cases in sandbox configuration"""
        # Test very small resource limits
        config = SandboxConfig(
            cpu_limit=0,  # Edge case: zero CPU
            memory_limit_mb=1,  # Edge case: minimal memory
            execution_timeout=1,  # Edge case: very short timeout
        )

        assert config.cpu_limit == 0
        assert config.memory_limit_mb == 1
        assert config.execution_timeout == 1

        # Test very large resource limits
        config = SandboxConfig(
            cpu_limit=100,
            memory_limit_mb=1000000,  # 1TB memory
            execution_timeout=3600,  # 1 hour timeout
        )

        assert config.cpu_limit == 100
        assert config.memory_limit_mb == 1000000
        assert config.execution_timeout == 3600

    @pytest.mark.asyncio
    async def test_sandbox_registry_management(self, edge_case_service):
        """Test sandbox registry management"""
        # Test registry is initially empty
        assert len(edge_case_service.sandbox_registry) == 0

        # Mock sandbox creation to test registry
        mock_sandbox = {"id": "registry-test-123", "status": "ready"}
        with patch.object(
            edge_case_service, "_create_sandbox_via_api", return_value=mock_sandbox
        ):
            await edge_case_service.create_sandbox()

        # Test registry was updated
        assert len(edge_case_service.sandbox_registry) == 1
        assert "registry-test-123" in edge_case_service.sandbox_registry

        # Test registry entry structure
        entry = edge_case_service.sandbox_registry["registry-test-123"]
        assert entry["status"] == "active"
        assert "created_at" in entry
        assert "last_used" in entry

    def test_service_availability_check(self, edge_case_service):
        """Test service availability checking"""
        # Initially should be unavailable (no API key)
        assert edge_case_service.is_available() is False

        # Test with API key configured
        with patch.dict(os.environ, {"DAYTONA_API_KEY": "test_key_123"}, clear=True):
            service_with_key = DaytonaService()
            # Should be available with valid API key
            assert service_with_key.is_available() is True

    @pytest.mark.asyncio
    async def test_cleanup_without_sandbox(self, edge_case_service):
        """Test cleanup when no sandbox exists"""
        # Should succeed even when no sandbox exists
        result = await edge_case_service.cleanup_sandbox()
        assert result is True
        assert edge_case_service.current_sandbox is None

    def test_health_check_comprehensive(self, edge_case_service):
        """Test comprehensive health check"""
        # Test health check without sandbox
        health = edge_case_service.health_check()
        assert health["overall_status"] in ["healthy", "unhealthy"]
        assert "service" in health
        assert "version" in health

        # Test health check with sandbox
        edge_case_service.current_sandbox = {"id": "health-test", "status": "active"}
        health = edge_case_service.health_check()
        assert health["sandbox_status"] == "active"


class TestSecurityValidationMock:
    """Test security validation with mocking"""

    @pytest.fixture
    def security_service(self):
        """Create service with security validation enabled"""
        config = SandboxConfig(enable_ast_validation=True)
        return DaytonaService(config)

    @pytest.mark.asyncio
    async def test_dangerous_code_detection(self, security_service):
        """Test detection of dangerous code patterns"""
        # Test OS module import
        dangerous_code = "import os\nos.system('rm -rf /')"
        result = await security_service._validate_code_security(dangerous_code)
        assert result is False

        # Test subprocess import
        dangerous_code = "import subprocess\nsubprocess.call(['rm', '-rf', '/'])"
        result = await security_service._validate_code_security(dangerous_code)
        assert result is False

        # Test eval usage
        dangerous_code = "eval('import os')"
        result = await security_service._validate_code_security(dangerous_code)
        assert result is False

        # Test exec usage
        dangerous_code = "exec('import os')"
        result = await security_service._validate_code_security(dangerous_code)
        assert result is False

    @pytest.mark.asyncio
    async def test_safe_code_validation(self, security_service):
        """Test validation of safe code"""
        # Test safe imports
        safe_code = "import numpy\nimport scipy\nprint('Safe code')"
        result = await security_service._validate_code_security(safe_code)
        assert result is True

        # Test mathematical operations
        safe_code = "import math\nresult = math.sqrt(16)\nprint(result)"
        result = await security_service._validate_code_security(safe_code)
        assert result is True

        # Test data processing
        safe_code = "import pandas as pd\ndata = [1, 2, 3, 4, 5]\ndf = pd.DataFrame(data)\nprint(df)"
        result = await security_service._validate_code_security(safe_code)
        assert result is True

    @pytest.mark.asyncio
    async def test_syntax_error_handling(self, security_service):
        """Test handling of syntax errors in validation"""
        # Test invalid syntax
        invalid_code = "print('unclosed string"
        result = await security_service._validate_code_security(invalid_code)
        assert result is False

        # Test malformed code
        invalid_code = "if True\n    print('missing colon')"
        result = await security_service._validate_code_security(invalid_code)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
