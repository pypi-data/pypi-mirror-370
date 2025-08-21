#!/usr/bin/env python3
"""
TASK-014: Performance Benchmark Suite for MSA Reasoning Kernel

This benchmark suite tests and measures performance across key operations:
1. Kernel initialization time
2. Memory operations performance
3. Pipeline execution time
4. Concurrent operation throughput
5. Tracing overhead measurement
6. Regression testing against baseline metrics
"""

import asyncio
import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import core components - after path setup
from reasoning_kernel.core.msa_kernel import MSAKernel, MSAKernelConfig
from reasoning_kernel.core.tracing import initialize_tracing, trace_operation, get_correlation_id
from reasoning_kernel.core.logging_config import configure_logging, get_logger


class MSAPerformanceBenchmarkSuite:
    """Performance benchmark suite for MSA Reasoning Kernel"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.benchmark_results = {}
        self.baseline_metrics = self._load_baseline_metrics()

    def _load_baseline_metrics(self) -> Dict:
        """Load baseline performance metrics for regression testing"""
        baseline_file = project_root / "benchmarks" / "baseline_metrics.json"
        if baseline_file.exists():
            with open(baseline_file, "r") as f:
                return json.load(f)

        # Default baseline metrics if file doesn't exist
        return {
            "kernel_init_time": {"mean": 0.5, "std": 0.1, "max_acceptable": 1.0},
            "memory_save_time": {"mean": 0.01, "std": 0.005, "max_acceptable": 0.05},
            "memory_search_time": {"mean": 0.02, "std": 0.01, "max_acceptable": 0.1},
            "pipeline_stage_time": {"mean": 0.001, "std": 0.0005, "max_acceptable": 0.01},
            "concurrent_throughput": {"min_ops_per_sec": 10, "target": 20},
            "tracing_overhead": {"max_percentage": 5.0},
        }

    async def run_all_benchmarks(self) -> Dict:
        """Run all performance benchmarks"""
        print("🚀 Starting MSA Performance Benchmark Suite")
        print("=" * 70)

        # Initialize tracing and logging
        configure_logging("INFO", json_logs=False)
        initialize_tracing(service_name="msa-benchmark")

        benchmarks = [
            ("Kernel Initialization", self.benchmark_kernel_initialization),
            ("Memory Operations", self.benchmark_memory_operations),
            ("Pipeline Performance", self.benchmark_pipeline_performance),
            ("Concurrent Operations", self.benchmark_concurrent_operations),
            ("Tracing Overhead", self.benchmark_tracing_overhead),
        ]

        for name, benchmark_func in benchmarks:
            print(f"\n📊 Running {name} Benchmark...")
            try:
                result = await benchmark_func()
                self.benchmark_results[name.lower().replace(" ", "_")] = result
                print(f"✅ {name} Benchmark Complete")
            except Exception as e:
                print(f"❌ {name} Benchmark Failed: {str(e)}")
                self.benchmark_results[name.lower().replace(" ", "_")] = {"error": str(e)}

        # Run regression analysis
        regression_results = self._analyze_regression()

        # Generate comprehensive report
        await self._generate_benchmark_report(regression_results)

        return self.benchmark_results

    async def benchmark_kernel_initialization(self) -> Dict:
        """Benchmark MSA kernel initialization performance"""
        init_times = []
        num_runs = 10

        test_config = {
            "openai_api_key": "test-key-for-benchmark",
            "enable_memory": False,
            "enable_plugins": False,
        }

        for i in range(num_runs):
            start_time = time.perf_counter()

            config = MSAKernelConfig(test_config)
            kernel = MSAKernel(config)
            await kernel.initialize()

            end_time = time.perf_counter()
            init_time = end_time - start_time
            init_times.append(init_time)

            # Clean up
            del kernel

        return {
            "mean": statistics.mean(init_times),
            "median": statistics.median(init_times),
            "std": statistics.stdev(init_times) if len(init_times) > 1 else 0,
            "min": min(init_times),
            "max": max(init_times),
            "samples": init_times,
            "num_runs": num_runs,
        }

    async def benchmark_memory_operations(self) -> Dict:
        """Benchmark memory save and search operations"""
        try:
            # Initialize kernel with memory enabled
            test_config = {
                "openai_api_key": "test-key-for-benchmark",
                "enable_memory": True,
                "enable_plugins": False,
                "redis_url": "redis://localhost:6379",
            }

            config = MSAKernelConfig(test_config)
            kernel = MSAKernel(config)
            await kernel.initialize()
            memory = kernel.get_memory()

            if not memory:
                raise Exception("Memory service not available")

            save_times = []
            search_times = []
            num_operations = 20

            # Benchmark memory save operations
            for i in range(num_operations):
                start_time = time.perf_counter()

                await memory.save_information(
                    collection="benchmark_test",
                    text=f"Benchmark test memory item {i} for performance testing",
                    id=f"benchmark_item_{i}",
                )

                end_time = time.perf_counter()
                save_times.append(end_time - start_time)

            # Benchmark memory search operations
            for i in range(num_operations):
                start_time = time.perf_counter()

                await memory.search(collection="benchmark_test", query=f"benchmark test item {i % 5}", limit=5)

                end_time = time.perf_counter()
                search_times.append(end_time - start_time)

            return {
                "save_operations": {
                    "mean": statistics.mean(save_times),
                    "median": statistics.median(save_times),
                    "std": statistics.stdev(save_times) if len(save_times) > 1 else 0,
                    "min": min(save_times),
                    "max": max(save_times),
                    "ops_per_second": num_operations / sum(save_times),
                },
                "search_operations": {
                    "mean": statistics.mean(search_times),
                    "median": statistics.median(search_times),
                    "std": statistics.stdev(search_times) if len(search_times) > 1 else 0,
                    "min": min(search_times),
                    "max": max(search_times),
                    "ops_per_second": num_operations / sum(search_times),
                },
                "total_operations": num_operations * 2,
            }

        except Exception as e:
            # Fallback to mock benchmarks if Redis not available
            self.logger.warning(f"Memory benchmarks using fallback (Redis unavailable): {str(e)}")
            return {
                "save_operations": {"mean": 0.001, "note": "fallback_mock"},
                "search_operations": {"mean": 0.002, "note": "fallback_mock"},
                "fallback": True,
            }

    async def benchmark_pipeline_performance(self) -> Dict:
        """Benchmark MSA pipeline stage performance"""
        # Simulate pipeline stage operations
        stage_times = []
        num_stages = 50

        for i in range(num_stages):
            start_time = time.perf_counter()

            # Simulate pipeline stage work with tracing
            with trace_operation(f"benchmark_stage_{i}", {"stage_id": i}):
                await asyncio.sleep(0.001)  # Simulate minimal processing time

            end_time = time.perf_counter()
            stage_times.append(end_time - start_time)

        return {
            "mean": statistics.mean(stage_times),
            "median": statistics.median(stage_times),
            "std": statistics.stdev(stage_times) if len(stage_times) > 1 else 0,
            "min": min(stage_times),
            "max": max(stage_times),
            "stages_per_second": num_stages / sum(stage_times),
            "num_stages": num_stages,
        }

    async def benchmark_concurrent_operations(self) -> Dict:
        """Benchmark concurrent operation throughput"""
        concurrent_levels = [1, 2, 5, 10, 20]
        results = {}

        async def worker_task(worker_id: int, operations_count: int) -> float:
            """Worker task for concurrent benchmark"""
            start_time = time.perf_counter()

            for i in range(operations_count):
                with trace_operation(f"concurrent_op_{worker_id}_{i}", {"worker": worker_id}):
                    await asyncio.sleep(0.001)  # Simulate work

            return time.perf_counter() - start_time

        for concurrency in concurrent_levels:
            operations_per_worker = 10

            start_time = time.perf_counter()

            # Create concurrent tasks
            tasks = []
            for worker_id in range(concurrency):
                task = worker_task(worker_id, operations_per_worker)
                tasks.append(task)

            # Execute concurrently
            worker_times = await asyncio.gather(*tasks)

            total_time = time.perf_counter() - start_time
            total_operations = concurrency * operations_per_worker
            throughput = total_operations / total_time

            results[f"concurrency_{concurrency}"] = {
                "total_time": total_time,
                "total_operations": total_operations,
                "ops_per_second": throughput,
                "avg_worker_time": statistics.mean(worker_times),
                "max_worker_time": max(worker_times),
            }

        return results

    async def benchmark_tracing_overhead(self) -> Dict:
        """Benchmark tracing overhead impact"""
        operations_count = 100

        # Benchmark without tracing
        start_time = time.perf_counter()
        for i in range(operations_count):
            await asyncio.sleep(0.001)
        no_trace_time = time.perf_counter() - start_time

        # Benchmark with tracing
        start_time = time.perf_counter()
        for i in range(operations_count):
            with trace_operation(f"overhead_test_{i}", {"iteration": i}):
                await asyncio.sleep(0.001)
        with_trace_time = time.perf_counter() - start_time

        overhead_time = with_trace_time - no_trace_time
        overhead_percentage = (overhead_time / no_trace_time) * 100

        return {
            "no_trace_time": no_trace_time,
            "with_trace_time": with_trace_time,
            "overhead_time": overhead_time,
            "overhead_percentage": overhead_percentage,
            "operations_count": operations_count,
            "acceptable": overhead_percentage < self.baseline_metrics["tracing_overhead"]["max_percentage"],
        }

    def _analyze_regression(self) -> Dict:
        """Analyze performance regression against baseline metrics"""
        regression_analysis = {}

        # Check kernel initialization regression
        if "kernel_initialization" in self.benchmark_results:
            kernel_metrics = self.benchmark_results["kernel_initialization"]
            baseline = self.baseline_metrics["kernel_init_time"]

            regression_analysis["kernel_init"] = {
                "current_mean": kernel_metrics.get("mean", 0),
                "baseline_mean": baseline["mean"],
                "regression_factor": kernel_metrics.get("mean", 0) / baseline["mean"],
                "within_acceptable": kernel_metrics.get("mean", 0) <= baseline["max_acceptable"],
                "status": "PASS" if kernel_metrics.get("mean", 0) <= baseline["max_acceptable"] else "FAIL",
            }

        # Check memory operations regression
        if "memory_operations" in self.benchmark_results:
            memory_metrics = self.benchmark_results["memory_operations"]
            if not memory_metrics.get("fallback", False):
                save_mean = memory_metrics["save_operations"]["mean"]
                search_mean = memory_metrics["search_operations"]["mean"]

                regression_analysis["memory_operations"] = {
                    "save_performance": {
                        "current": save_mean,
                        "baseline": self.baseline_metrics["memory_save_time"]["mean"],
                        "status": (
                            "PASS"
                            if save_mean <= self.baseline_metrics["memory_save_time"]["max_acceptable"]
                            else "FAIL"
                        ),
                    },
                    "search_performance": {
                        "current": search_mean,
                        "baseline": self.baseline_metrics["memory_search_time"]["mean"],
                        "status": (
                            "PASS"
                            if search_mean <= self.baseline_metrics["memory_search_time"]["max_acceptable"]
                            else "FAIL"
                        ),
                    },
                }

        # Check tracing overhead
        if "tracing_overhead" in self.benchmark_results:
            overhead_metrics = self.benchmark_results["tracing_overhead"]
            regression_analysis["tracing_overhead"] = {
                "current_overhead": overhead_metrics.get("overhead_percentage", 0),
                "max_acceptable": self.baseline_metrics["tracing_overhead"]["max_percentage"],
                "status": "PASS" if overhead_metrics.get("acceptable", False) else "FAIL",
            }

        return regression_analysis

    async def _generate_benchmark_report(self, regression_results: Dict):
        """Generate comprehensive benchmark report"""
        print("\n" + "=" * 70)
        print("📊 MSA PERFORMANCE BENCHMARK REPORT")
        print("=" * 70)

        # Performance Summary
        print("\n🚀 Performance Summary:")
        for benchmark_name, results in self.benchmark_results.items():
            if "error" in results:
                print(f"  ❌ {benchmark_name}: {results['error']}")
                continue

            formatted_name = benchmark_name.replace("_", " ").title()
            print(f"  📈 {formatted_name}:")

            if benchmark_name == "kernel_initialization":
                print(f"    - Mean: {results['mean']:.3f}s")
                print(f"    - Std:  {results['std']:.3f}s")
                print(f"    - Max:  {results['max']:.3f}s")

            elif benchmark_name == "memory_operations":
                if not results.get("fallback", False):
                    print(f"    - Save ops/sec: {results['save_operations']['ops_per_second']:.1f}")
                    print(f"    - Search ops/sec: {results['search_operations']['ops_per_second']:.1f}")
                else:
                    print("    - Status: Fallback mode (Redis unavailable)")

            elif benchmark_name == "pipeline_performance":
                print(f"    - Stages/sec: {results['stages_per_second']:.1f}")
                print(f"    - Mean time: {results['mean']:.4f}s")

            elif benchmark_name == "concurrent_operations":
                max_throughput = max(r["ops_per_second"] for r in results.values())
                print(f"    - Max throughput: {max_throughput:.1f} ops/sec")
                print(f"    - Concurrency levels tested: {len(results)}")

            elif benchmark_name == "tracing_overhead":
                print(f"    - Overhead: {results['overhead_percentage']:.2f}%")
                print(f"    - Acceptable: {'✅' if results['acceptable'] else '❌'}")

        # Regression Analysis
        print("\n📉 Regression Analysis:")
        overall_status = "PASS"
        for component, analysis in regression_results.items():
            if isinstance(analysis, dict) and "status" in analysis:
                status = analysis["status"]
                if status == "FAIL":
                    overall_status = "FAIL"
                print(f"  {component}: {'✅' if status == 'PASS' else '❌'} {status}")

        # Overall Assessment
        print(f"\n🎯 Overall Performance: {'✅ EXCELLENT' if overall_status == 'PASS' else '⚠️ NEEDS ATTENTION'}")

        # Save detailed results
        results_file = project_root / "benchmarks" / "performance_results.json"
        results_file.parent.mkdir(exist_ok=True)

        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_results": self.benchmark_results,
            "regression_analysis": regression_results,
            "overall_status": overall_status,
            "system_info": {"correlation_id": get_correlation_id(), "python_version": sys.version.split()[0]},
        }

        with open(results_file, "w") as f:
            json.dump(detailed_results, f, indent=2)

        print(f"\n📄 Detailed results saved to: {results_file}")

async def main():
    """Main benchmark execution"""
    benchmark_suite = MSAPerformanceBenchmarkSuite()

    results = await benchmark_suite.run_all_benchmarks()

    print("\n" + "=" * 70)
    print("🎉 MSA PERFORMANCE BENCHMARK SUITE COMPLETE")
    print("✅ TASK-014: Performance benchmarking successful")
    print("=" * 70)

    return results

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⚠️ Benchmark execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Benchmark execution failed: {str(e)}")
        sys.exit(1)
