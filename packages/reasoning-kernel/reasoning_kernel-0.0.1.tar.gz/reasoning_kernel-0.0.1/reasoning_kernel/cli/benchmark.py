"""
MSA CoSci 2025 Benchmark CLI Commands

This module provides CLI commands for running MSA CoSci 2025 benchmarks.
"""
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import numpy as np
from reasoning_kernel.cli.ui import UIManager
from reasoning_kernel.visualization.probability_visualizer import (
    InteractiveProbabilityVisualizer,
    VisualizationConfig,
    VisualizationType
)


# Default repository URL for MSA CoSci 2025 data
COSCI_REPO_URL = "https://github.com/lio-wong/msa-cogsci-2025-data.git"
COSCI_REPO_DIR = Path.home() / ".msa" / "cogsci-2025-data"


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test"""
    test_name: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""
    suite_name: str
    results: List[BenchmarkResult]
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    @property
    def duration_stats(self) -> Dict[str, float]:
        """Calculate duration statistics"""
        if not self.results:
            return {}
            
        durations = [r.duration_ms for r in self.results if r.success]
        if not durations:
            return {}
            
        return {
            "min_ms": min(durations),
            "max_ms": max(durations),
            "mean_ms": np.mean(durations),
            "median_ms": np.median(durations),
            "stdev_ms": np.std(durations) if len(durations) > 1 else 0.0,
        }
        
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if not self.results:
            return 0.0
        return (sum(1 for r in self.results if r.success) / len(self.results)) * 100


class CoSciBenchmarkManager:
    """Manager for MSA CoSci 2025 benchmarks"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.ui = UIManager(verbose=verbose)
        self.repo_dir = COSCI_REPO_DIR
        self.visualizer = InteractiveProbabilityVisualizer()
        
    def ensure_repo_exists(self) -> bool:
        """Ensure the CoSci repository exists, cloning it if necessary"""
        if not self.repo_dir.exists():
            self.ui.print_info(f"CoSci repository not found at {self.repo_dir}")
            return self._download_repository()
        return True
    
    def _download_repository(self) -> bool:
        """Download or update the CoSci repository"""
        try:
            if not self.repo_dir.exists():
                self.ui.print_info(f"Cloning CoSci repository from {COSCI_REPO_URL}")
                self.repo_dir.parent.mkdir(parents=True, exist_ok=True)
                result = subprocess.run(
                    ["git", "clone", COSCI_REPO_URL, str(self.repo_dir)],
                    capture_output=True,
                    text=True,
                    cwd=Path.home()
                )
                if result.returncode != 0:
                    self.ui.print_error(f"Failed to clone repository: {result.stderr}")
                    return False
                self.ui.print_success("Repository cloned successfully")
            else:
                self.ui.print_info("Updating existing CoSci repository")
                result = subprocess.run(
                    ["git", "pull"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_dir
                )
                if result.returncode != 0:
                    self.ui.print_error(f"Failed to update repository: {result.stderr}")
                    return False
                self.ui.print_success("Repository updated successfully")
            return True
        except Exception as e:
            self.ui.print_error(f"Error managing repository: {e}")
            return False
    
    def discover_benchmarks(self) -> List[str]:
        """Discover available CoSci benchmarks"""
        if not self.ensure_repo_exists():
            return []
            
        benchmarks_dir = self.repo_dir / "benchmarks"
        if not benchmarks_dir.exists():
            self.ui.print_warning(f"Benchmarks directory not found at {benchmarks_dir}")
            return []
            
        benchmarks = []
        for item in benchmarks_dir.iterdir():
            if item.is_file() and item.suffix == ".py":
                benchmarks.append(item.stem)
            elif item.is_dir() and (item / "benchmark.py").exists():
                benchmarks.append(item.name)
                
        return sorted(benchmarks)
    
    def run_benchmark(self, benchmark_name: str, iterations: int = 1) -> BenchmarkSuite:
        """Run a specific CoSci benchmark"""
        if not self.ensure_repo_exists():
            return BenchmarkSuite(
                suite_name=benchmark_name,
                results=[],
                started_at=datetime.now()
            )
            
        # Find the benchmark file
        benchmark_path = None
        benchmarks_dir = self.repo_dir / "benchmarks"
        
        # Check direct file match
        direct_file = benchmarks_dir / f"{benchmark_name}.py"
        if direct_file.exists():
            benchmark_path = direct_file
        else:
            # Check for directory with benchmark.py
            dir_path = benchmarks_dir / benchmark_name
            if dir_path.exists() and dir_path.is_dir():
                benchmark_file = dir_path / "benchmark.py"
                if benchmark_file.exists():
                    benchmark_path = benchmark_file
        
        if not benchmark_path or not benchmark_path.exists():
            error_result = BenchmarkResult(
                test_name=benchmark_name,
                duration_ms=0,
                success=False,
                error_message=f"Benchmark '{benchmark_name}' not found"
            )
            return BenchmarkSuite(
                suite_name=benchmark_name,
                results=[error_result],
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
            
        # Run the benchmark multiple times
        results = []
        started_at = datetime.now()
        
        try:
            self.ui.print_info(f"Running benchmark: {benchmark_name} ({iterations} iterations)")
            
            for i in range(iterations):
                if iterations > 1:
                    self.ui.print_info(f"  Iteration {i+1}/{iterations}")
                
                start_time = time.perf_counter()
                
                try:
                    # Run the benchmark
                    result = subprocess.run(
                        [sys.executable, str(benchmark_path)],
                        capture_output=True,
                        text=True,
                        cwd=self.repo_dir,
                        timeout=300  # 5 minute timeout
                    )
                    
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    results.append(BenchmarkResult(
                        test_name=f"{benchmark_name}_iter_{i+1}",
                        duration_ms=duration_ms,
                        success=result.returncode == 0,
                        error_message=result.stderr if result.returncode != 0 else None,
                        metadata={
                            "iteration": i+1,
                            "return_code": result.returncode,
                            "stdout_size": len(result.stdout),
                            "stderr_size": len(result.stderr)
                        }
                    ))
                    
                except subprocess.TimeoutExpired:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    results.append(BenchmarkResult(
                        test_name=f"{benchmark_name}_iter_{i+1}",
                        duration_ms=duration_ms,
                        success=False,
                        error_message="Benchmark timed out after 5 minutes"
                    ))
                    
                except Exception as e:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    results.append(BenchmarkResult(
                        test_name=f"{benchmark_name}_iter_{i+1}",
                        duration_ms=duration_ms,
                        success=False,
                        error_message=str(e)
                    ))
                    
            completed_at = datetime.now()
            return BenchmarkSuite(
                suite_name=benchmark_name,
                results=results,
                started_at=started_at,
                completed_at=completed_at
            )
                
        except Exception as e:
            self.ui.print_error(f"Error running benchmark: {e}")
            error_result = BenchmarkResult(
                test_name=benchmark_name,
                duration_ms=0,
                success=False,
                error_message=str(e)
            )
            return BenchmarkSuite(
                suite_name=benchmark_name,
                results=[error_result],
                started_at=started_at,
                completed_at=datetime.now()
            )
    
    def visualize_results(self, suite: BenchmarkSuite, output_path: Optional[str] = None):
        """Visualize benchmark results"""
        try:
            if not suite.results:
                self.ui.print_warning("No results to visualize")
                return
                
            # Prepare data for visualization
            durations = [r.duration_ms for r in suite.results if r.success]
            success_rates = [100.0 if r.success else 0.0 for r in suite.results]
            
            if not durations:
                self.ui.print_warning("No successful results to visualize")
                return
                
            # Create visualization configuration
            config = VisualizationConfig(
                visualization_type=VisualizationType.PROBABILITY_DISTRIBUTION,
                width=800,
                height=600,
                interactive=True,
                show_confidence_intervals=True
            )
            
            # Create distribution visualization
            distributions = {
                "Execution Time (ms)": durations,
                "Success Rate (%)": success_rates
            }
            
            viz_data = self.visualizer.create_probability_distribution_visualization(
                distributions, config
            )
            
            # Display summary statistics
            self.ui.print_header("Benchmark Results Visualization")
            
            if suite.duration_stats:
                stats_data = [
                    {"Metric": "Min Duration", "Value": f"{suite.duration_stats['min_ms']:.2f} ms"},
                    {"Metric": "Max Duration", "Value": f"{suite.duration_stats['max_ms']:.2f} ms"},
                    {"Metric": "Mean Duration", "Value": f"{suite.duration_stats['mean_ms']:.2f} ms"},
                    {"Metric": "Median Duration", "Value": f"{suite.duration_stats['median_ms']:.2f} ms"},
                    {"Metric": "Std Dev Duration", "Value": f"{suite.duration_stats['stdev_ms']:.2f} ms"},
                    {"Metric": "Success Rate", "Value": f"{suite.success_rate:.1f}%"}
                ]
                self.ui.print_table(stats_data)
            
            # If output path is specified, save visualization data
            if output_path:
                viz_output_path = Path(output_path)
                viz_output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save as JSON
                with open(viz_output_path.with_suffix('.json'), 'w') as f:
                    json.dump(viz_data, f, indent=2)
                    
                # Save summary statistics
                summary_data = {
                    "suite_name": suite.suite_name,
                    "started_at": suite.started_at.isoformat(),
                    "completed_at": suite.completed_at.isoformat() if suite.completed_at else None,
                    "duration_stats": suite.duration_stats,
                    "success_rate": suite.success_rate,
                    "total_iterations": len(suite.results),
                    "successful_iterations": sum(1 for r in suite.results if r.success)
                }
                
                with open(viz_output_path.with_suffix('.summary.json'), 'w') as f:
                    json.dump(summary_data, f, indent=2)
                    
                self.ui.print_success(f"Visualization data saved to {viz_output_path.with_suffix('.json')}")
                self.ui.print_success(f"Summary saved to {viz_output_path.with_suffix('.summary.json')}")
                
        except Exception as e:
            self.ui.print_error(f"Error visualizing results: {e}")


# CLI Commands
@click.group()
def benchmark():
    """MSA CoSci 2025 Benchmark Commands"""
    pass


@benchmark.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def list(verbose: bool):
    """List available CoSci benchmarks"""
    ui = UIManager(verbose=verbose)
    
    try:
        manager = CoSciBenchmarkManager(verbose=verbose)
        benchmarks = manager.discover_benchmarks()
        
        if not benchmarks:
            ui.print_warning("No benchmarks found")
            return
            
        ui.print_header("Available CoSci Benchmarks")
        benchmark_data = [{"Name": b} for b in benchmarks]
        ui.print_table(benchmark_data)
        ui.print_info(f"Total benchmarks: {len(benchmarks)}")
        
    except Exception as e:
        ui.print_error(f"Error listing benchmarks: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


@benchmark.command()
@click.argument("benchmark_name")
@click.option("--iterations", "-i", default=1, help="Number of iterations to run")
@click.option("--output", "-o", help="Output path for visualization data")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def run(benchmark_name: str, iterations: int, output: str, verbose: bool):
    """Run a specific CoSci benchmark"""
    ui = UIManager(verbose=verbose)
    
    try:
        manager = CoSciBenchmarkManager(verbose=verbose)
        suite = manager.run_benchmark(benchmark_name, iterations)
        
        # Display results
        ui.print_header(f"Benchmark Results: {suite.suite_name}")
        
        if suite.completed_at:
            duration = (suite.completed_at - suite.started_at).total_seconds()
            ui.print_info(f"Total execution time: {duration:.2f} seconds")
            
        ui.print_info(f"Success rate: {suite.success_rate:.1f}%")
        
        if suite.duration_stats:
            stats_data = [
                {"Metric": "Min Duration", "Value": f"{suite.duration_stats['min_ms']:.2f} ms"},
                {"Metric": "Max Duration", "Value": f"{suite.duration_stats['max_ms']:.2f} ms"},
                {"Metric": "Mean Duration", "Value": f"{suite.duration_stats['mean_ms']:.2f} ms"},
                {"Metric": "Median Duration", "Value": f"{suite.duration_stats['median_ms']:.2f} ms"},
                {"Metric": "Std Dev Duration", "Value": f"{suite.duration_stats['stdev_ms']:.2f} ms"}
            ]
            ui.print_table(stats_data)
        
        # Show individual results
        if suite.results:
            ui.print_subheader("Individual Results")
            result_data = []
            for result in suite.results:
                result_data.append({
                    "Test": result.test_name,
                    "Duration (ms)": f"{result.duration_ms:.2f}",
                    "Success": "✅" if result.success else "❌",
                    "Error": result.error_message[:50] if result.error_message else ""
                })
            ui.print_table(result_data)
        
        # Visualize results
        manager.visualize_results(suite, output)
        
    except Exception as e:
        ui.print_error(f"Error running benchmark: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


@benchmark.command()
@click.argument("benchmark_name")
@click.option("--iterations", "-i", default=1, help="Number of iterations to run")
@click.option("--output", "-o", help="Output path for visualization data")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def compare(benchmark_name: str, iterations: int, output: str, verbose: bool):
    """Run benchmark and compare with existing results"""
    ui = UIManager(verbose=verbose)
    
    try:
        manager = CoSciBenchmarkManager(verbose=verbose)
        suite = manager.run_benchmark(benchmark_name, iterations)
        
        # Display comparison with previous results if available
        ui.print_header(f"Benchmark Comparison: {suite.suite_name}")
        
        # For now, just show current results
        # In a real implementation, this would compare with historical data
        if suite.duration_stats:
            stats_data = [
                {"Metric": "Current Min Duration", "Value": f"{suite.duration_stats['min_ms']:.2f} ms"},
                {"Metric": "Current Max Duration", "Value": f"{suite.duration_stats['max_ms']:.2f} ms"},
                {"Metric": "Current Mean Duration", "Value": f"{suite.duration_stats['mean_ms']:.2f} ms"},
                {"Metric": "Current Median Duration", "Value": f"{suite.duration_stats['median_ms']:.2f} ms"},
                {"Metric": "Current Success Rate", "Value": f"{suite.success_rate:.1f}%"}
            ]
            ui.print_table(stats_data)
        
        # Visualize results
        manager.visualize_results(suite, output)
        
        ui.print_info("Note: Comparison with historical data not implemented in this version")
        
    except Exception as e:
        ui.print_error(f"Error running benchmark comparison: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    benchmark()