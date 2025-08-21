"""
Enhanced Test Configuration for MSA Reasoning Kernel

Configuration and setup for comprehensive testing framework expansion.
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# Test Configuration
TEST_CONFIG = {
    "framework": {
        "name": "MSA Reasoning Kernel Enhanced Testing Framework",
        "version": "1.0.0",
        "description": "Comprehensive testing framework with integration, performance, and benchmarking capabilities",
    },
    "environments": {
        "unit": {
            "parallel_execution": True,
            "max_workers": 4,
            "timeout": 300,  # 5 minutes
            "fail_fast": True,
            "verbose": True,
        },
        "integration": {
            "setup_timeout": 60,  # 1 minute
            "test_timeout": 180,  # 3 minutes
            "teardown_timeout": 30,  # 30 seconds
            "retry_flaky_tests": True,
            "max_retries": 2,
            "parallel_suites": False,  # Run suites sequentially for integration
        },
        "performance": {
            "warmup_iterations": 3,
            "benchmark_iterations": 10,
            "timeout_per_benchmark": 300,  # 5 minutes
            "memory_profiling": True,
            "performance_thresholds": {
                "orchestration": {
                    "sequential_fast": 0.5,  # seconds
                    "parallel_fast": 0.3,
                    "pipeline_mixed": 1.0,
                    "adaptive_mixed": 2.0,
                },
                "state_management": {
                    "rapid_updates": 0.01,  # per update
                    "state_queries": 0.005,  # per query
                    "checkpoint_ops": 0.1,  # per operation
                    "concurrent_access": 0.5,  # per batch
                },
                "communication": {
                    "direct_messages": 0.05,  # per message
                    "broadcast_messages": 0.2,  # per broadcast
                    "pipeline_messages": 0.3,  # per pipeline
                },
            },
        },
    },
    "reporting": {
        "output_directory": "test_reports",
        "formats": ["json", "html", "junit"],
        "detailed_logs": True,
        "performance_graphs": True,
        "coverage_report": True,
        "benchmark_comparison": True,
    },
    "components": {
        "orchestration": {
            "test_strategies": ["sequential", "parallel", "pipeline", "hierarchical", "adaptive"],
            "agent_configurations": ["fast", "medium", "slow", "mixed", "failing"],
            "load_test_sizes": [1, 5, 10, 20],
        },
        "state_management": {
            "test_scenarios": ["rapid_updates", "concurrent_access", "checkpoint_recovery", "state_persistence"],
            "data_sizes": ["small", "medium", "large"],
            "concurrency_levels": [1, 5, 10],
        },
        "communication": {
            "patterns": ["direct", "broadcast", "pipeline", "scatter_gather"],
            "network_conditions": ["normal", "high_latency", "packet_loss"],
            "message_sizes": ["small", "medium", "large"],
        },
        "api": {
            "endpoints": ["reasoning", "optimization", "documentation"],
            "load_test_concurrent_users": [1, 5, 10, 20],
            "response_time_thresholds": {
                "reasoning": 2.0,
                "optimization": 1.0,
                "documentation": 0.5,
            },
        },
    },
    "quality_gates": {
        "unit_tests": {
            "min_success_rate": 0.98,  # 98%
            "max_execution_time": 300,  # 5 minutes
            "required_coverage": 0.8,  # 80%
        },
        "integration_tests": {
            "min_success_rate": 0.95,  # 95%
            "max_execution_time": 900,  # 15 minutes
            "critical_paths_required": True,
        },
        "performance_tests": {
            "max_regression": 0.1,  # 10% performance regression
            "min_success_rate": 0.9,  # 90%
            "memory_usage_limit": 500,  # MB
            "throughput_requirements": {
                "orchestration": 10,  # operations per second
                "state_management": 100,
                "communication": 50,
            },
        },
    },
    "test_data": {
        "reasoning_scenarios": {
            "simple": 10,
            "complex": 5,
            "edge_cases": 3,
        },
        "agent_configurations": {
            "basic_agents": 5,
            "specialized_agents": 3,
            "failing_agents": 2,
        },
        "communication_patterns": {
            "direct_pairs": 10,
            "broadcast_groups": 5,
            "pipeline_chains": 3,
        },
    },
    "monitoring": {
        "metrics_collection": True,
        "real_time_monitoring": False,  # Disabled for testing
        "performance_profiling": True,
        "memory_tracking": True,
        "error_tracking": True,
    },
}

# Test Paths
TEST_PATHS = {
    "root": Path(__file__).parent,
    "framework": Path(__file__).parent / "framework",
    "unit": Path(__file__).parent / "unit",
    "integration": Path(__file__).parent / "integration",
    "performance": Path(__file__).parent / "performance",
    "reports": Path(__file__).parent.parent / "test_reports",
    "data": Path(__file__).parent / "data",
}


# Environment Variables
def get_test_environment() -> Dict[str, Any]:
    """Get test environment configuration."""

    return {
        "TESTING": True,
        "LOG_LEVEL": os.getenv("TEST_LOG_LEVEL", "INFO"),
        "REDIS_DISABLED": True,  # Disable Redis for most tests
        "STATE_PERSISTENCE_DISABLED": True,  # Use in-memory for testing
        "PERFORMANCE_PROFILING": os.getenv("ENABLE_PROFILING", "false").lower() == "true",
        "TEST_TIMEOUT": int(os.getenv("TEST_TIMEOUT", "1800")),  # 30 minutes default
        "PARALLEL_TESTS": os.getenv("PARALLEL_TESTS", "true").lower() == "true",
        "VERBOSE_OUTPUT": os.getenv("VERBOSE_TESTS", "false").lower() == "true",
    }


# Test Discovery
def discover_test_files() -> Dict[str, List[Path]]:
    """Discover all test files in the project."""

    test_files = {
        "unit": [],
        "integration": [],
        "performance": [],
    }

    # Unit tests (existing structure)
    if TEST_PATHS["unit"].exists():
        test_files["unit"] = list(TEST_PATHS["unit"].glob("test_*.py"))

    # Also check root tests directory for existing tests
    root_tests = TEST_PATHS["root"].glob("test_*.py")
    test_files["unit"].extend(root_tests)

    # Integration tests
    if TEST_PATHS["integration"].exists():
        test_files["integration"] = list(TEST_PATHS["integration"].glob("test_*.py"))

    # Performance tests
    if TEST_PATHS["performance"].exists():
        test_files["performance"] = list(TEST_PATHS["performance"].glob("test_*.py"))

    return test_files


# Quality Metrics
def get_quality_thresholds() -> Dict[str, Any]:
    """Get quality threshold configuration."""

    return {
        "code_coverage": {
            "minimum_total": 80.0,  # 80% overall coverage
            "minimum_new_code": 90.0,  # 90% coverage for new code
            "critical_modules": {
                "reasoning_kernel.agents": 85.0,
                "reasoning_kernel.core": 90.0,
                "reasoning_kernel.api": 75.0,
            },
        },
        "performance_benchmarks": {
            "orchestration_latency": {
                "p50": 0.5,  # 50th percentile < 500ms
                "p95": 2.0,  # 95th percentile < 2s
                "p99": 5.0,  # 99th percentile < 5s
            },
            "throughput_requirements": {
                "min_operations_per_second": 10,
                "target_operations_per_second": 50,
            },
            "memory_usage": {
                "max_heap_size": 512,  # MB
                "max_growth_rate": 0.1,  # 10% per operation
            },
        },
        "reliability": {
            "success_rate": 0.95,  # 95% success rate
            "error_rate": 0.05,  # Max 5% error rate
            "recovery_time": 30,  # Max 30s recovery time
        },
        "test_execution": {
            "max_total_time": 1800,  # 30 minutes
            "max_flaky_rate": 0.02,  # Max 2% flaky tests
            "required_environments": ["unit", "integration"],
            "optional_environments": ["performance", "load"],
        },
    }


# Test Fixtures Configuration
def get_fixture_config() -> Dict[str, Any]:
    """Get test fixtures configuration."""

    return {
        "mock_agents": {
            "count_per_type": {
                "basic": 5,
                "slow": 3,
                "failing": 2,
                "specialized": 3,
            },
            "response_times": {
                "fast": 0.01,
                "medium": 0.1,
                "slow": 0.5,
            },
            "failure_rates": {
                "reliable": 0.01,
                "unreliable": 0.1,
                "failing": 0.5,
            },
        },
        "test_data": {
            "reasoning_scenarios": 20,
            "communication_patterns": 10,
            "state_transitions": 15,
        },
        "environments": {
            "clean_state": True,
            "isolated_execution": True,
            "resource_cleanup": True,
        },
    }


# CI/CD Integration
def get_ci_config() -> Dict[str, Any]:
    """Get CI/CD configuration for automated testing."""

    return {
        "github_actions": {
            "test_matrix": {
                "python_versions": ["3.9", "3.10", "3.11"],
                "os_targets": ["ubuntu-latest", "macos-latest"],
                "test_categories": ["unit", "integration"],
            },
            "performance_tests": {
                "schedule": "daily",
                "environment": "ubuntu-latest",
                "python_version": "3.10",
            },
        },
        "quality_gates": {
            "required_checks": [
                "unit_tests_pass",
                "integration_tests_pass",
                "coverage_threshold_met",
                "no_critical_security_issues",
            ],
            "optional_checks": [
                "performance_regression_check",
                "documentation_updated",
                "changelog_updated",
            ],
        },
        "notifications": {
            "on_failure": ["slack", "email"],
            "on_success": ["slack"],
            "performance_alerts": ["email"],
        },
    }


# Export configuration
__all__ = [
    "TEST_CONFIG",
    "TEST_PATHS",
    "get_test_environment",
    "discover_test_files",
    "get_quality_thresholds",
    "get_fixture_config",
    "get_ci_config",
]
