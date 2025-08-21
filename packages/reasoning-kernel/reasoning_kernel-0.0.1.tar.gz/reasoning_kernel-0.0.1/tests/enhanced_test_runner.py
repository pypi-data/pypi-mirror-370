#!/usr/bin/env python3
"""
Enhanced Test Runner for MSA Reasoning Kernel

Comprehensive test runner that executes unit tests, integration tests,
performance benchmarks, and generates detailed reports.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test framework imports with error handling
try:
    from tests.framework.enhanced_testing import (
        EnhancedTestCase,
        IntegrationTestFramework,
        PerformanceTestSuite,
    )
except ImportError as e:
    print(f"Warning: Could not import enhanced testing framework: {e}")
    EnhancedTestCase = None
    IntegrationTestFramework = None
    PerformanceTestSuite = None

# Test suites with error handling
try:
    from tests.integration.test_simplified_integration import (
        TestBasicOrchestrationIntegration,
        TestPerformanceIntegration,
        TestErrorHandlingIntegration,
        TestEndToEndWorkflow,
    )
except ImportError as e:
    print(f"Warning: Could not import integration tests: {e}")
    TestBasicOrchestrationIntegration = None
    TestPerformanceIntegration = None
    TestErrorHandlingIntegration = None
    TestEndToEndWorkflow = None

try:
    from tests.performance.test_benchmarks import (
        ComponentBenchmarkSuite,
    )
except ImportError as e:
    print(f"Warning: Could not import performance benchmarks: {e}")
    ComponentBenchmarkSuite = None

try:
    from reasoning_kernel.utils.security import get_secure_logger

    logger = get_secure_logger(__name__)
except ImportError as e:
    print(f"Warning: Could not import secure logger: {e}")
    # Create a simple logger fallback
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class EnhancedTestRunner:
    """Enhanced test runner with comprehensive reporting."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("test_reports")
        self.output_dir.mkdir(exist_ok=True)

        self.results = {
            "summary": {},
            "unit_tests": {},
            "integration_tests": {},
            "performance_tests": {},
            "benchmarks": {},
            "errors": [],
            "recommendations": [],
        }

        self.start_time = datetime.now()

        # Initialize framework components with error handling
        if IntegrationTestFramework:
            self.test_framework = IntegrationTestFramework()
        else:
            self.test_framework = None

        if PerformanceTestSuite:
            self.performance_suite = PerformanceTestSuite()
        else:
            self.performance_suite = None

    async def run_all_tests(self, test_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all specified test types."""

        test_types = test_types or ["unit", "integration", "performance"]

        logger.info(f"Starting comprehensive test run: {test_types}")

        try:
            # Run unit tests
            if "unit" in test_types:
                await self._run_unit_tests()

            # Run integration tests
            if "integration" in test_types:
                await self._run_integration_tests()

            # Run performance tests
            if "performance" in test_types:
                await self._run_performance_tests()

            # Generate summary
            self._generate_summary()

            # Generate recommendations
            self._generate_recommendations()

            # Save results
            await self._save_results()

            logger.info("Test run completed successfully")

        except Exception as e:
            logger.error(f"Test run failed: {e}")
            self.results["errors"].append(f"Test run failure: {str(e)}")
            raise

        return self.results

    async def _run_unit_tests(self):
        """Run existing unit tests."""
        logger.info("Running unit tests...")

        try:
            # Import and run existing test cases

            # Change to project root
            project_root = Path(__file__).parent.parent
            os.chdir(project_root)

            # Run pytest on existing tests
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-v",
                    "--tb=short",
                    "--maxfail=10",
                    "-x",  # Stop on first failure
                    "--json-report",
                    f"--json-report-file={self.output_dir / 'unit_test_results.json'}",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            self.results["unit_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": time.time() - self.start_time.timestamp(),
            }

            # Parse JSON report if available
            json_report_path = self.output_dir / "unit_test_results.json"
            if json_report_path.exists():
                with open(json_report_path) as f:
                    json_report = json.load(f)
                    self.results["unit_tests"]["detailed_results"] = json_report

            logger.info(f"Unit tests completed with return code: {result.returncode}")

        except subprocess.TimeoutExpired:
            self.results["unit_tests"] = {"status": "timeout", "error": "Unit tests timed out after 300 seconds"}
            logger.error("Unit tests timed out")

        except Exception as e:
            self.results["unit_tests"] = {"status": "error", "error": str(e)}
            logger.error(f"Unit test execution failed: {e}")

    async def _run_integration_tests(self):
        """Run integration tests."""
        logger.info("Running integration tests...")

        integration_results = {
            "status": "running",
            "tests": {},
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
        }

        try:
            # Set up integration environment
            environment = await self.test_framework.setup_integration_environment()

            # Test suites to run
            test_suites = [
                ("basic_orchestration", TestBasicOrchestrationIntegration()),
                ("performance_integration", TestPerformanceIntegration()),
                ("error_handling", TestErrorHandlingIntegration()),
                ("end_to_end", TestEndToEndWorkflow()),
            ]

            for suite_name, suite_instance in test_suites:
                suite_results = await self._run_integration_suite(suite_instance, environment, suite_name)
                integration_results["tests"][suite_name] = suite_results
                integration_results["total_tests"] += suite_results.get("total", 0)
                integration_results["passed_tests"] += suite_results.get("passed", 0)
                integration_results["failed_tests"] += suite_results.get("failed", 0)

            integration_results["status"] = "completed"

            # Cleanup environment
            await self.test_framework.teardown_integration_environment(environment)

        except Exception as e:
            integration_results["status"] = "error"
            integration_results["error"] = str(e)
            logger.error(f"Integration tests failed: {e}")

        self.results["integration_tests"] = integration_results

    async def _run_integration_suite(
        self, suite_instance, environment: Dict[str, Any], suite_name: str
    ) -> Dict[str, Any]:
        """Run a specific integration test suite."""

        suite_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": {},
            "execution_time": 0.0,
        }

        start_time = time.perf_counter()

        # Get test methods from suite
        test_methods = [method for method in dir(suite_instance) if method.startswith("test_")]
        suite_results["total"] = len(test_methods)

        for test_method_name in test_methods:
            test_method = getattr(suite_instance, test_method_name)

            try:
                logger.info(f"Running {suite_name}.{test_method_name}")

                # Create test case
                test_case = EnhancedTestCase(f"{suite_name}.{test_method_name}", "integration")

                # Run test with framework
                metrics = await self.test_framework.run_integration_test(test_case, lambda env: test_method(env))

                suite_results["tests"][test_method_name] = {
                    "status": "passed",
                    "execution_time": metrics.execution_time,
                    "assertions_passed": metrics.assertions_passed,
                    "assertions_failed": metrics.assertions_failed,
                }
                suite_results["passed"] += 1

            except Exception as e:
                logger.error(f"Test {suite_name}.{test_method_name} failed: {e}")
                suite_results["tests"][test_method_name] = {
                    "status": "failed",
                    "error": str(e),
                }
                suite_results["failed"] += 1

        suite_results["execution_time"] = time.perf_counter() - start_time
        return suite_results

    async def _run_performance_tests(self):
        """Run performance tests and benchmarks."""
        logger.info("Running performance tests and benchmarks...")

        performance_results = {
            "status": "running",
            "benchmarks": {},
            "performance_tests": {},
        }

        try:
            # Set up environment for performance testing
            environment = await self.test_framework.setup_integration_environment()

            # Run component benchmarks
            benchmark_suite = ComponentBenchmarkSuite()

            # Run orchestration benchmarks
            orchestration_benchmarks = await benchmark_suite.run_orchestration_benchmarks(environment)
            performance_results["benchmarks"]["orchestration"] = [
                {
                    "test_name": b.test_name,
                    "avg_time": b.avg_time,
                    "median_time": b.median_time,
                    "p95_time": b.p95_time,
                    "success_rate": b.success_rate,
                    "throughput": b.throughput,
                    "iterations": b.iterations,
                }
                for b in orchestration_benchmarks
            ]

            # Run state management benchmarks
            state_benchmarks = await benchmark_suite.run_state_management_benchmarks(environment)
            performance_results["benchmarks"]["state_management"] = [
                {
                    "test_name": b.test_name,
                    "avg_time": b.avg_time,
                    "success_rate": b.success_rate,
                    "throughput": b.throughput,
                    "iterations": b.iterations,
                }
                for b in state_benchmarks
            ]

            # Run communication benchmarks
            communication_benchmarks = await benchmark_suite.run_communication_benchmarks(environment)
            performance_results["benchmarks"]["communication"] = [
                {
                    "test_name": b.test_name,
                    "avg_time": b.avg_time,
                    "success_rate": b.success_rate,
                    "throughput": b.throughput,
                    "iterations": b.iterations,
                }
                for b in communication_benchmarks
            ]

            # Generate performance report
            report = benchmark_suite.generate_performance_report()
            performance_results["report"] = report

            performance_results["status"] = "completed"

            # Cleanup
            await self.test_framework.teardown_integration_environment(environment)

        except Exception as e:
            performance_results["status"] = "error"
            performance_results["error"] = str(e)
            logger.error(f"Performance tests failed: {e}")

        self.results["performance_tests"] = performance_results

    def _generate_summary(self):
        """Generate test run summary."""

        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()

        # Count tests
        unit_tests = self.results.get("unit_tests", {})
        integration_tests = self.results.get("integration_tests", {})
        performance_tests = self.results.get("performance_tests", {})

        summary = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_execution_time": total_time,
            "unit_tests": {
                "status": unit_tests.get("status", "not_run"),
                "return_code": unit_tests.get("return_code"),
            },
            "integration_tests": {
                "status": integration_tests.get("status", "not_run"),
                "total": integration_tests.get("total_tests", 0),
                "passed": integration_tests.get("passed_tests", 0),
                "failed": integration_tests.get("failed_tests", 0),
            },
            "performance_tests": {
                "status": performance_tests.get("status", "not_run"),
                "benchmarks_run": len(performance_tests.get("benchmarks", {})),
            },
            "overall_status": self._determine_overall_status(),
        }

        self.results["summary"] = summary

        # Log summary
        logger.info("Test Run Summary:")
        logger.info(f"  Total execution time: {total_time:.1f}s")
        logger.info(f"  Unit tests: {summary['unit_tests']['status']}")
        logger.info(
            f"  Integration tests: {summary['integration_tests']['passed']}/{summary['integration_tests']['total']} passed"
        )
        logger.info(f"  Performance benchmarks: {summary['performance_tests']['benchmarks_run']} completed")
        logger.info(f"  Overall status: {summary['overall_status']}")

    def _determine_overall_status(self) -> str:
        """Determine overall test run status."""

        unit_status = self.results.get("unit_tests", {}).get("status", "not_run")
        integration_status = self.results.get("integration_tests", {}).get("status", "not_run")
        performance_status = self.results.get("performance_tests", {}).get("status", "not_run")

        if any(status == "error" for status in [unit_status, integration_status, performance_status]):
            return "error"

        if any(status == "failed" for status in [unit_status, integration_status, performance_status]):
            return "failed"

        if unit_status == "passed" and integration_status == "completed" and performance_status == "completed":
            return "passed"

        return "partial"

    def _generate_recommendations(self):
        """Generate recommendations based on test results."""

        recommendations = []

        # Unit test recommendations
        unit_tests = self.results.get("unit_tests", {})
        if unit_tests.get("status") == "failed":
            recommendations.append("Fix failing unit tests before proceeding with development")
        elif unit_tests.get("status") == "timeout":
            recommendations.append("Optimize unit test performance - tests are taking too long")

        # Integration test recommendations
        integration_tests = self.results.get("integration_tests", {})
        if integration_tests.get("failed_tests", 0) > 0:
            recommendations.append(f"Address {integration_tests['failed_tests']} failing integration tests")

        # Performance recommendations
        performance_tests = self.results.get("performance_tests", {})
        if "report" in performance_tests and "recommendations" in performance_tests["report"]:
            recommendations.extend(performance_tests["report"]["recommendations"])

        # General recommendations
        if len(self.results.get("errors", [])) > 0:
            recommendations.append("Review and address test execution errors")

        self.results["recommendations"] = recommendations

    async def _save_results(self):
        """Save test results to files."""

        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")

        # Save comprehensive results
        results_file = self.output_dir / f"comprehensive_test_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save summary report
        summary_file = self.output_dir / f"test_summary_{timestamp}.json"
        with open(summary_file, "w") as f:
            json.dump(self.results["summary"], f, indent=2, default=str)

        # Save performance report if available
        if "performance_tests" in self.results and "report" in self.results["performance_tests"]:
            perf_file = self.output_dir / f"performance_report_{timestamp}.json"
            with open(perf_file, "w") as f:
                json.dump(self.results["performance_tests"]["report"], f, indent=2, default=str)

        logger.info(f"Test results saved to {self.output_dir}")
        logger.info(f"  Comprehensive results: {results_file}")
        logger.info(f"  Summary: {summary_file}")


async def main():
    """Main entry point for enhanced test runner."""

    parser = argparse.ArgumentParser(description="Enhanced Test Runner for MSA Reasoning Kernel")
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "integration", "performance", "all"],
        default=["all"],
        help="Test types to run (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("test_reports"),
        help="Output directory for test reports (default: test_reports)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.INFO)

    # Determine test types
    test_types = args.types
    if "all" in test_types:
        test_types = ["unit", "integration", "performance"]

    # Run tests
    runner = EnhancedTestRunner(args.output_dir)

    try:
        results = await runner.run_all_tests(test_types)

        # Print summary
        print("\n" + "=" * 60)
        print("ENHANCED TEST RUN SUMMARY")
        print("=" * 60)

        summary = results["summary"]
        print(f"Execution time: {summary['total_execution_time']:.1f}s")
        print(f"Overall status: {summary['overall_status'].upper()}")

        if summary["unit_tests"]["status"] != "not_run":
            print(f"Unit tests: {summary['unit_tests']['status'].upper()}")

        if summary["integration_tests"]["status"] != "not_run":
            it = summary["integration_tests"]
            print(f"Integration tests: {it['passed']}/{it['total']} passed")

        if summary["performance_tests"]["status"] != "not_run":
            pt = summary["performance_tests"]
            print(f"Performance benchmarks: {pt['benchmarks_run']} completed")

        # Print recommendations
        if results.get("recommendations"):
            print("\nRECOMMENDations:")
            for i, rec in enumerate(results["recommendations"][:5], 1):
                print(f"  {i}. {rec}")

        print(f"\nDetailed results saved to: {args.output_dir}")

        # Exit with appropriate code
        if summary["overall_status"] in ["passed", "partial"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nTest run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
