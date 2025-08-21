"""
MSA Reasoning Kernel - Enhanced Testing Framework

Comprehensive testing infrastructure for the MSA Reasoning Kernel project.
Provides enhanced testing utilities, integration tests, performance benchmarks,
and automated test execution.
"""

__version__ = "1.0.0"
__author__ = "MSA Reasoning Kernel Team"

# Import main testing components
try:
    from .framework.enhanced_testing import (
        EnhancedTestCase,
        MockAgentFactory,
        TestDataGenerator,
        PerformanceTestSuite,
        IntegrationTestFramework,
    )
except ImportError:
    # Framework components not available
    pass

try:
    from .config import (
        TEST_CONFIG,
        TEST_PATHS,
        get_test_environment,
        get_quality_thresholds,
    )
except ImportError:
    # Configuration not available
    pass

# Test suite metadata
TESTING_FRAMEWORK_INFO = {
    "name": "MSA Reasoning Kernel Enhanced Testing Framework",
    "version": __version__,
    "components": [
        "Enhanced Testing Utilities",
        "Integration Test Framework",
        "Performance Benchmarking",
        "Automated Test Runner",
        "Test Configuration Management",
    ],
    "capabilities": [
        "Mock agent creation and management",
        "Test data generation",
        "Performance profiling and benchmarking",
        "Integration testing with orchestration components",
        "Comprehensive test reporting",
        "Automated test execution and scheduling",
    ],
}

__all__ = [
    "TESTING_FRAMEWORK_INFO",
    "EnhancedTestCase",
    "MockAgentFactory",
    "TestDataGenerator",
    "PerformanceTestSuite",
    "IntegrationTestFramework",
    "TEST_CONFIG",
    "TEST_PATHS",
    "get_test_environment",
    "get_quality_thresholds",
]
