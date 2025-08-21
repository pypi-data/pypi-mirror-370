"""
Enhanced Testing Framework

Core testing utilities and framework for comprehensive testing of the
MSA Reasoning Kernel project.
"""

__version__ = "1.0.0"

# Import main framework components
try:
    from .enhanced_testing import (
        EnhancedTestCase,
        MockAgentFactory,
        TestDataGenerator,
        PerformanceTestSuite,
        IntegrationTestFramework,
        performance_test,
        integration_test,
    )

    __all__ = [
        "EnhancedTestCase",
        "MockAgentFactory",
        "TestDataGenerator",
        "PerformanceTestSuite",
        "IntegrationTestFramework",
        "performance_test",
        "integration_test",
    ]

except ImportError:
    # Framework components not available
    __all__ = []
