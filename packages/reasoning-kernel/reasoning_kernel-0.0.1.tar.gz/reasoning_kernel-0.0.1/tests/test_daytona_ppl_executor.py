"""
Test cases for DaytonaPPLExecutor

Tests cover:
- PPL program validation
- Environment setup
- Code execution in sandbox
- Result parsing and error handling
- Batch execution
"""

import unittest
from unittest.mock import Mock, AsyncMock

from reasoning_kernel.services.daytona_ppl_executor import (
    DaytonaPPLExecutor,
    PPLFramework,
    PPLExecutionConfig,
    PPLProgram,
)
from reasoning_kernel.services.daytona_service import (
    DaytonaService,
    ExecutionResult,
    SandboxStatus,
)


class TestDaytonaPPLExecutor(unittest.TestCase):
    """Test DaytonaPPLExecutor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_service = Mock(spec=DaytonaService)
        self.executor = DaytonaPPLExecutor(daytona_service=self.mock_service)

    def test_initialization(self):
        """Test executor initialization"""
        config = PPLExecutionConfig(framework=PPLFramework.NUMPYRO, max_execution_time=120.0, memory_limit_mb=2048)
        executor = DaytonaPPLExecutor(ppl_config=config)

        assert executor.ppl_config.framework == PPLFramework.NUMPYRO
        assert executor.ppl_config.max_execution_time == 120.0
        assert executor.ppl_config.memory_limit_mb == 2048

    def test_ppl_program_creation(self):
        """Test PPL program data structure"""
        program = PPLProgram(
            code="import numpyro\ndef main(): return {}",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
            input_data={"param": "value"},
        )

        assert program.code == "import numpyro\ndef main(): return {}"
        assert program.framework == PPLFramework.NUMPYRO
        assert program.entry_point == "main"
        assert program.input_data == {"param": "value"}

    def test_wrapper_script_generation(self):
        """Test execution wrapper script generation"""
        program = PPLProgram(
            code="def main():\n    return {'result': 'test'}",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
            input_data={"param": "value"},
        )

        wrapper = self.executor._create_execution_wrapper(program)

        assert "import json" in wrapper
        assert "import traceback" in wrapper
        assert program.code in wrapper
        assert f'"{program.framework.value}"' in wrapper
        assert f'"{program.entry_point}"' in wrapper
        assert "PPL_RESULT_START" in wrapper
        assert "PPL_RESULT_END" in wrapper

    def test_result_parsing_success(self):
        """Test parsing successful execution results"""
        output = """
Some initial output
PPL_RESULT_START
{"success": true, "result": {"posterior": [1, 2, 3]}, "execution_metadata": {"time": 1.5}}
PPL_RESULT_END
Some final output
"""

        base_result = ExecutionResult(
            exit_code=0,
            stdout=output,
            stderr="",
            execution_time=1.5,
            status=SandboxStatus.COMPLETED,
            resource_usage={"memory_mb": 256},
            metadata={},
        )

        ppl_result = self.executor._parse_ppl_results(base_result)

        assert ppl_result.exit_code == 0
        assert ppl_result.inference_results == {"posterior": [1, 2, 3]}
        assert ppl_result.execution_metadata == {"time": 1.5}

    def test_result_parsing_no_markers(self):
        """Test parsing when no structured markers present"""
        base_result = ExecutionResult(
            exit_code=1,
            stdout="Simple output without markers",
            stderr="Some error",
            execution_time=0.5,
            status=SandboxStatus.FAILED,
            resource_usage={},
            metadata={},
        )

        ppl_result = self.executor._parse_ppl_results(base_result)

        assert ppl_result.exit_code == 1
        assert ppl_result.stdout == "Simple output without markers"
        assert ppl_result.stderr == "Some error"
        assert ppl_result.inference_results is None


class TestAsyncPPLValidation(unittest.IsolatedAsyncioTestCase):
    """Test async PPL program validation"""

    async def asyncSetUp(self):
        """Set up async test fixtures"""
        self.mock_service = Mock(spec=DaytonaService)
        self.executor = DaytonaPPLExecutor(daytona_service=self.mock_service)

    async def test_valid_numpyro_program(self):
        """Test validation of valid NumPyro program"""
        program = PPLProgram(
            code="""
import numpyro
import jax.numpy as jnp

def main():
    return {"result": "success"}
""",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
        )

        errors = await self.executor.validate_ppl_program(program)
        assert len(errors) == 0

    async def test_invalid_syntax_program(self):
        """Test validation catches syntax errors"""
        program = PPLProgram(code="def invalid_function(:\n    pass", framework=PPLFramework.NUMPYRO)

        errors = await self.executor.validate_ppl_program(program)
        assert len(errors) > 0
        assert any("syntax error" in error.lower() for error in errors)

    async def test_dangerous_operations_detected(self):
        """Test validation catches dangerous operations"""
        program = PPLProgram(
            code="""
import os
import subprocess

def main():
    os.system("rm -rf /")
    return {}
""",
            framework=PPLFramework.NUMPYRO,
        )

        errors = await self.executor.validate_ppl_program(program)
        assert len(errors) > 0
        assert any("dangerous operation" in error.lower() for error in errors)

    async def test_missing_numpyro_import(self):
        """Test validation catches missing framework import"""
        program = PPLProgram(
            code="""
def main():
    return {"result": "no numpyro import"}
""",
            framework=PPLFramework.NUMPYRO,
        )

        errors = await self.executor.validate_ppl_program(program)
        assert len(errors) > 0
        assert any("numpyro" in error.lower() for error in errors)


class TestAsyncPPLExecution(unittest.IsolatedAsyncioTestCase):
    """Test async PPL program execution"""

    async def asyncSetUp(self):
        """Set up async test fixtures"""
        self.mock_service = Mock(spec=DaytonaService)
        config = PPLExecutionConfig(framework=PPLFramework.NUMPYRO, max_execution_time=60.0, memory_limit_mb=1024)
        self.executor = DaytonaPPLExecutor(daytona_service=self.mock_service, ppl_config=config)

    async def test_validation_failure(self):
        """Test execution stops on validation failure"""
        # Mock validation failure
        self.executor.validate_ppl_program = AsyncMock(return_value=["Missing numpyro import"])

        program = PPLProgram(code="def main(): return {}", framework=PPLFramework.NUMPYRO)

        result = await self.executor.execute_ppl_program(program)

        assert result.exit_code == 1
        assert result.status == SandboxStatus.FAILED
        assert len(result.validation_errors) > 0
        assert "validation failed" in result.stderr.lower()


def run_tests():
    """Run all tests"""
    print("Running DaytonaPPLExecutor tests...")

    # Run sync tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDaytonaPPLExecutor)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Run async tests
    async_suite = unittest.TestLoader().loadTestsFromTestCase(TestAsyncPPLValidation)
    async_result = runner.run(async_suite)

    exec_suite = unittest.TestLoader().loadTestsFromTestCase(TestAsyncPPLExecution)
    exec_result = runner.run(exec_suite)

    # Summary
    total_tests = result.testsRun + async_result.testsRun + exec_result.testsRun
    total_failures = len(result.failures) + len(async_result.failures) + len(exec_result.failures)
    total_errors = len(result.errors) + len(async_result.errors) + len(exec_result.errors)

    print("\n🧪 Test Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")

    if total_failures == 0 and total_errors == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
