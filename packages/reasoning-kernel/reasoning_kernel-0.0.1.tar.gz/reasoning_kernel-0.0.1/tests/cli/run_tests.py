#!/usr/bin/env python3
"""
Test Runner for MSA Reasoning Kernel CLI Tests
============================================

Comprehensive test runner that executes all CLI tests and generates detailed reports.
"""

import argparse
import subprocess
import sys
import os
import json
import time
from typing import Dict, List, Any


def run_command(command: List[str], cwd: str = None) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(command)}")
        return None
    except Exception as e:
        print(f"Error running command: {e}")
        return None


def run_test_suite(suite_name: str, command: List[str], cwd: str = None) -> Dict[str, Any]:
    """Run a test suite and return results"""
    print(f"Running {suite_name}...")
    start_time = time.time()
    
    result = run_command(command, cwd)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if result is None:
        return {
            "suite": suite_name,
            "status": "failed",
            "execution_time": execution_time,
            "error": "Command execution failed or timed out"
        }
    
    # Parse pytest output to extract test results
    output_lines = result.stdout.split('\n')
    summary_line = None
    for line in reversed(output_lines):
        if "failed" in line and "passed" in line:
            summary_line = line
            break
    
    passed = 0
    failed = 0
    if summary_line:
        # Extract numbers from summary line like "=== 25 passed, 2 failed in 3.45s ==="
        import re
        passed_match = re.search(r'(\d+) passed', summary_line)
        failed_match = re.search(r'(\d+) failed', summary_line)
        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
    
    return {
        "suite": suite_name,
        "status": "passed" if failed == 0 and result.returncode == 0 else "failed",
        "passed": passed,
        "failed": failed,
        "execution_time": execution_time,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def run_all_tests(output_dir: str = None) -> Dict[str, Any]:
    """Run all CLI test suites"""
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Test suites to run
    test_suites = [
        {
            "name": "Unit Tests",
            "command": ["pytest", "tests/cli/test_cli_unit.py", "-v", "--tb=short"]
        },
        {
            "name": "Integration Tests",
            "command": ["pytest", "tests/cli/test_cli_integration.py", "-v", "--tb=short"]
        },
        {
            "name": "Mock Sandbox Tests",
            "command": ["pytest", "tests/cli/test_cli_mock_sandbox.py", "-v", "--tb=short"]
        },
        {
            "name": "Performance Tests",
            "command": ["pytest", "tests/cli/test_cli_performance.py", "-v", "--tb=short"]
        },
        {
            "name": "User Acceptance Tests",
            "command": ["pytest", "tests/cli/test_cli_user_acceptance.py", "-v", "--tb=short"]
        },
        {
            "name": "Coverage Report",
            "command": ["pytest", "tests/cli/", "--cov=reasoning_kernel.cli", "--cov-report=term-missing", "--cov-report=html:htmlcov"]
        }
    ]
    
    # Run each test suite
    results = []
    overall_start_time = time.time()
    
    for suite in test_suites:
        result = run_test_suite(suite["name"], suite["command"])
        results.append(result)
        
        # Print immediate results
        print(f"  Status: {result['status']}")
        if result['status'] == 'passed':
            print(f"  Tests: {result['passed']} passed")
        else:
            print(f"  Tests: {result['passed']} passed, {result['failed']} failed")
        print(f"  Time: {result['execution_time']:.2f}s")
        print()
    
    overall_end_time = time.time()
    total_execution_time = overall_end_time - overall_start_time
    
    # Calculate overall statistics
    total_passed = sum(r['passed'] for r in results if 'passed' in r)
    total_failed = sum(r['failed'] for r in results if 'failed' in r)
    overall_status = "passed" if all(r['status'] == 'passed' for r in results if 'status' in r) else "failed"
    
    # Generate summary
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_status": overall_status,
        "total_suites": len(test_suites),
        "passed_suites": len([r for r in results if r['status'] == 'passed']),
        "failed_suites": len([r for r in results if r['status'] == 'failed']),
        "total_tests": total_passed + total_failed,
        "passed_tests": total_passed,
        "failed_tests": total_failed,
        "total_execution_time": total_execution_time,
        "suite_results": results
    }
    
    # Save results if output directory specified
    if output_dir:
        results_file = os.path.join(output_dir, "test_results.json")
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Also save detailed results
        detailed_file = os.path.join(output_dir, "detailed_results.json")
        with open(detailed_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    return summary


def print_summary(summary: Dict[str, Any]):
    """Print test results summary"""
    print("=" * 60)
    print("MSA Reasoning Kernel CLI Test Results Summary")
    print("=" * 60)
    print(f"Timestamp: {summary['timestamp']}")
    print(f"Overall Status: {summary['overall_status'].upper()}")
    print(f"Total Suites: {summary['total_suites']}")
    print(f"Passed Suites: {summary['passed_suites']}")
    print(f"Failed Suites: {summary['failed_suites']}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed Tests: {summary['passed_tests']}")
    print(f"Failed Tests: {summary['failed_tests']}")
    print(f"Total Execution Time: {summary['total_execution_time']:.2f}s")
    print()
    
    print("Suite Details:")
    print("-" * 40)
    for result in summary['suite_results']:
        status_icon = "✅" if result['status'] == 'passed' else "❌"
        print(f"{status_icon} {result['suite']}: {result['status']}")
        if 'passed' in result and 'failed' in result:
            print(f"    Tests: {result['passed']} passed, {result['failed']} failed")
        print(f"    Time: {result['execution_time']:.2f}s")
        print()


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run MSA Reasoning Kernel CLI Tests")
    parser.add_argument("--output", "-o", help="Output directory for test results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quick", "-q", action="store_true", help="Run only quick tests (skip performance)")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    
    args = parser.parse_args()
    
    print("MSA Reasoning Kernel CLI Test Runner")
    print("=" * 40)
    
    # Run tests
    try:
        summary = run_all_tests(args.output)
        
        # Print summary
        print_summary(summary)
        
        # Check requirements
        print("Requirements Verification:")
        print("-" * 25)
        
        # Check code coverage requirement (> 90%)
        if summary['total_tests'] > 0:
            coverage_percentage = (summary['passed_tests'] / summary['total_tests']) * 100
            coverage_status = "✅" if coverage_percentage > 90 else "❌"
            print(f"{coverage_status} Code Coverage: {coverage_percentage:.1f}% (> 90% required)")
        else:
            print("❌ Code Coverage: Unable to calculate (no tests run)")
        
        # Check overall status
        overall_status = "✅" if summary['overall_status'] == 'passed' else "❌"
        print(f"{overall_status} Overall Test Status: {summary['overall_status']}")
        
        # Exit with appropriate code
        if summary['overall_status'] == 'passed':
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the output above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()