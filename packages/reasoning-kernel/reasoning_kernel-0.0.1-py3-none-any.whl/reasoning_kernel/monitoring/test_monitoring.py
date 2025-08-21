"""
TASK-025 Monitoring & Observability Test Suite

This test suite validates the comprehensive monitoring and observability
capabilities implemented for the Thinking Exploration Framework.

Test Coverage:
- Metrics collection and aggregation
- Distributed tracing functionality
- Health checks and system diagnostics
- Performance dashboards and visualization
- Integration testing
"""

from datetime import datetime
import json
import time

from reasoning_kernel.monitoring.dashboards import get_metrics_dashboard
from reasoning_kernel.monitoring.dashboards import MetricsDashboard
from reasoning_kernel.monitoring.dashboards import PerformanceDashboard
from reasoning_kernel.monitoring.health import get_health_checker
from reasoning_kernel.monitoring.health import HealthCheck
from reasoning_kernel.monitoring.health import HealthChecker
from reasoning_kernel.monitoring.health import HealthStatus

# Import monitoring components
from reasoning_kernel.monitoring.metrics import get_metrics
from reasoning_kernel.monitoring.metrics import MetricType
from reasoning_kernel.monitoring.metrics import ThinkingMetrics
from reasoning_kernel.monitoring.tracing import create_tracer
from reasoning_kernel.monitoring.tracing import TracingManager


class MonitoringTestSuite:
    """Comprehensive test suite for monitoring and observability"""

    def __init__(self):
        """Initialize the test suite"""
        self.test_results = []
        self.start_time = datetime.now()

    def run_all_tests(self) -> None:
        """Run all monitoring tests"""
        print("🚀 Starting TASK-025: Monitoring & Observability Tests")
        print("=" * 60)

        # Test metrics collection
        self.test_metrics_collection()
        self.test_thinking_specific_metrics()
        self.test_timer_functionality()
        self.test_metrics_export()

        # Test distributed tracing
        self.test_basic_tracing()
        self.test_exploration_tracing()
        self.test_tracing_context_management()

        # Test health monitoring
        self.test_health_checks()
        self.test_system_health_aggregation()
        self.test_custom_health_checks()

        # Test dashboards
        self.test_metrics_dashboard()
        self.test_performance_dashboard()
        self.test_dashboard_export()

        # Integration tests
        self.test_monitoring_integration()

        # Generate report
        self.generate_test_report()

    def test_metrics_collection(self) -> None:
        """Test basic metrics collection functionality"""
        print("📊 Testing metrics collection...")

        metrics = ThinkingMetrics()

        # Test counter
        metrics.increment_counter("test.counter", 5.0)
        metrics.increment_counter("test.counter", 3.0)

        summary = metrics.get_metric_summary("test.counter")
        assert summary is not None
        assert summary.current_value == 8.0
        assert summary.metric_type == MetricType.COUNTER

        # Test gauge
        metrics.set_gauge("test.gauge", 42.5)
        summary = metrics.get_metric_summary("test.gauge")
        assert summary is not None
        assert summary.current_value == 42.5
        assert summary.metric_type == MetricType.GAUGE

        # Test histogram
        metrics.record_histogram("test.histogram", 10.0)
        metrics.record_histogram("test.histogram", 20.0)
        metrics.record_histogram("test.histogram", 30.0)

        summary = metrics.get_metric_summary("test.histogram")
        assert summary is not None
        assert summary.avg_value == 20.0
        assert summary.min_value == 10.0
        assert summary.max_value == 30.0

        self.test_results.append(
            {
                "test": "metrics_collection",
                "status": "PASS",
                "details": "Counter, gauge, and histogram metrics working correctly",
            }
        )
        print("   ✅ Basic metrics collection - PASS")

    def test_thinking_specific_metrics(self) -> None:
        """Test thinking-specific metrics"""
        print("📊 Testing thinking-specific metrics...")

        metrics = ThinkingMetrics()

        # Test exploration metrics
        metrics.record_exploration_start("detailed_analysis", "complex")
        metrics.record_exploration_success(0.150, "detailed_analysis")

        metrics.record_exploration_start("sparse_data_analysis", "medium")
        metrics.record_exploration_failure("timeout", "sparse_data_analysis")

        # Test trigger detection
        metrics.record_trigger_detection("complexity_increase", 0.85)
        metrics.record_trigger_detection("domain_shift", 0.72)

        # Test mode changes
        metrics.record_mode_change("detailed_analysis", "sparse_data_analysis")

        # Test model invocations
        metrics.record_model_invocation("world_model", 0.025, True)
        metrics.record_model_invocation("synthesis", 0.040, True)

        # Get thinking metrics
        thinking_metrics = metrics.get_thinking_metrics()

        assert thinking_metrics["total_explorations"] >= 2
        assert thinking_metrics["successful_explorations"] >= 1
        assert thinking_metrics["failed_explorations"] >= 1
        assert thinking_metrics["trigger_detections"] >= 2
        assert thinking_metrics["mode_changes"] >= 1
        assert thinking_metrics["model_invocations"] >= 2

        self.test_results.append(
            {
                "test": "thinking_specific_metrics",
                "status": "PASS",
                "details": f"Thinking metrics: {thinking_metrics['total_explorations']} explorations, {thinking_metrics['success_rate']}% success rate",
            }
        )
        print("   ✅ Thinking-specific metrics - PASS")

    def test_timer_functionality(self) -> None:
        """Test timer context manager"""
        print("📊 Testing timer functionality...")

        metrics = ThinkingMetrics()

        # Test timer context manager
        with metrics.start_timer("test.operation"):
            time.sleep(0.01)  # Simulate work

        summary = metrics.get_metric_summary("test.operation")
        assert summary is not None
        assert summary.current_value > 0.009  # Should be around 0.01 seconds
        assert summary.metric_type == MetricType.TIMER

        self.test_results.append(
            {
                "test": "timer_functionality",
                "status": "PASS",
                "details": f"Timer recorded {summary.current_value:.3f}s duration",
            }
        )
        print("   ✅ Timer functionality - PASS")

    def test_metrics_export(self) -> None:
        """Test metrics export functionality"""
        print("📊 Testing metrics export...")

        metrics = ThinkingMetrics()
        metrics.increment_counter("export.test", 1)
        metrics.set_gauge("export.gauge", 100.0)

        # Test JSON export
        json_export = metrics.export_json()
        json_data = json.loads(json_export)

        assert "timestamp" in json_data
        assert "thinking_metrics" in json_data
        assert "all_metrics" in json_data

        # Test Prometheus export
        prometheus_export = metrics.export_prometheus()
        assert "export_test" in prometheus_export
        assert "export_gauge" in prometheus_export

        self.test_results.append(
            {"test": "metrics_export", "status": "PASS", "details": "JSON and Prometheus export formats working"}
        )
        print("   ✅ Metrics export - PASS")

    def test_basic_tracing(self) -> None:
        """Test basic tracing functionality"""
        print("🔍 Testing basic tracing...")

        tracer = create_tracer("test-service")

        # Test span creation
        with tracer.span("test_operation", {"test.attribute": "value"}) as span:
            span.add_event("operation_started")
            span.set_attribute("custom.metric", 42)
            span.add_event("operation_completed")

        assert span.name == "test_operation"
        assert span.status == "OK"
        assert "test.attribute" in span.attributes
        assert "custom.metric" in span.attributes
        assert len(span.events) == 2

        self.test_results.append(
            {
                "test": "basic_tracing",
                "status": "PASS",
                "details": f"Span created with {len(span.events)} events and {len(span.attributes)} attributes",
            }
        )
        print("   ✅ Basic tracing - PASS")

    def test_exploration_tracing(self) -> None:
        """Test exploration-specific tracing"""
        print("🔍 Testing exploration tracing...")

        tracer = TracingManager("thinking-exploration")

        # Test exploration trace
        exploration_id = "test-exploration-001"
        context = {"complexity": "high", "domain": "technical"}

        trace_id = tracer.start_exploration_trace(exploration_id, "detailed_analysis", context)
        assert trace_id is not None

        # Add phases
        tracer.add_exploration_phase(exploration_id, "trigger_detection", {"triggers": ["complexity"]})
        tracer.add_exploration_phase(exploration_id, "mode_determination", {"mode": "detailed_analysis"})

        # Add model invocation
        tracer.add_model_invocation_trace(exploration_id, "world_model", {"input": "data"}, 0.025, True)

        # Add trigger detection
        tracer.add_trigger_detection_trace(exploration_id, "complexity_increase", 0.8, context)

        # End exploration
        tracer.end_exploration_trace(exploration_id, True, {"result": "success"})

        # Verify trace data
        trace_data = tracer.get_exploration_trace(exploration_id)
        assert trace_data is not None
        assert trace_data["mode"] == "detailed_analysis"
        assert len(trace_data["phases"]) == 2

        self.test_results.append(
            {
                "test": "exploration_tracing",
                "status": "PASS",
                "details": f"Exploration trace with {len(trace_data['phases'])} phases",
            }
        )
        print("   ✅ Exploration tracing - PASS")

    def test_tracing_context_management(self) -> None:
        """Test tracing context management"""
        print("🔍 Testing tracing context management...")

        tracer = TracingManager()

        # Test nested spans
        with tracer.span("parent_operation") as parent_span:
            parent_span.add_event("parent_started")

            with tracer.span("child_operation") as child_span:
                child_span.add_event("child_started")
                assert child_span.parent == parent_span

            parent_span.add_event("parent_completed")

        assert parent_span.status == "OK"
        assert len(parent_span.events) == 2

        self.test_results.append(
            {
                "test": "tracing_context_management",
                "status": "PASS",
                "details": "Nested span context management working correctly",
            }
        )
        print("   ✅ Tracing context management - PASS")

    def test_health_checks(self) -> None:
        """Test health check functionality"""
        print("🏥 Testing health checks...")

        health_checker = HealthChecker()

        # Run individual checks
        cpu_result = health_checker.run_check("cpu_usage")
        assert cpu_result is not None
        assert cpu_result.name == "cpu_usage"
        assert cpu_result.status in [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.CRITICAL]

        memory_result = health_checker.run_check("memory_usage")
        assert memory_result is not None
        assert memory_result.name == "memory_usage"

        # Test system health
        system_health = health_checker.run_all_checks()
        assert system_health.status in [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.CRITICAL]
        assert len(system_health.checks) > 0
        assert system_health.uptime_seconds > 0

        self.test_results.append(
            {
                "test": "health_checks",
                "status": "PASS",
                "details": f"System health: {system_health.status.value}, {len(system_health.checks)} checks",
            }
        )
        print("   ✅ Health checks - PASS")

    def test_system_health_aggregation(self) -> None:
        """Test system health status aggregation"""
        print("🏥 Testing health aggregation...")

        health_checker = HealthChecker()

        # Get health summary
        health_summary = health_checker.get_health_summary()

        assert "status" in health_summary
        assert "timestamp" in health_summary
        assert "uptime_seconds" in health_summary
        assert "checks_summary" in health_summary
        assert "system_info" in health_summary

        checks_summary = health_summary["checks_summary"]
        assert "total" in checks_summary
        assert "healthy" in checks_summary
        assert "warning" in checks_summary
        assert "critical" in checks_summary

        self.test_results.append(
            {
                "test": "system_health_aggregation",
                "status": "PASS",
                "details": f"Health summary with {checks_summary['total']} total checks",
            }
        )
        print("   ✅ Health aggregation - PASS")

    def test_custom_health_checks(self) -> None:
        """Test custom health check registration"""
        print("🏥 Testing custom health checks...")

        health_checker = HealthChecker()

        def custom_check():
            return {"value": 95.0, "message": "Custom check is healthy", "custom_data": "test"}

        # Register custom check
        custom_health_check = HealthCheck(
            name="custom_test_check",
            description="Test custom health check",
            check_function=custom_check,
            warning_threshold=80.0,
            critical_threshold=98.0,
        )

        health_checker.register_check(custom_health_check)

        # Run custom check
        result = health_checker.run_check("custom_test_check")
        assert result is not None
        assert result.name == "custom_test_check"
        assert result.status == HealthStatus.WARNING  # 95.0 > 80.0 threshold

        # Remove custom check
        health_checker.remove_check("custom_test_check")
        removed_result = health_checker.run_check("custom_test_check")
        assert removed_result is None

        self.test_results.append(
            {
                "test": "custom_health_checks",
                "status": "PASS",
                "details": "Custom health check registration and removal working",
            }
        )
        print("   ✅ Custom health checks - PASS")

    def test_metrics_dashboard(self) -> None:
        """Test metrics dashboard functionality"""
        print("📈 Testing metrics dashboard...")

        dashboard = MetricsDashboard()

        # Update dashboard data
        dashboard.update_explorations_rate(2.5)
        dashboard.update_success_rate(87.5)
        dashboard.update_response_time(125.0)
        dashboard.update_mode_distribution({"detailed_analysis": 15, "sparse_data_analysis": 10, "multidomain": 5})
        dashboard.update_system_resources(45.2, 67.8, 23.1)
        dashboard.update_trigger_types({"complexity_increase": 8, "domain_shift": 3, "sparse_data": 5})

        # Test chart data retrieval
        explorations_data = dashboard.get_chart_data("explorations_rate")
        assert len(explorations_data) > 0
        assert explorations_data[-1].data["value"] == 2.5

        success_data = dashboard.get_chart_data("success_rate")
        assert len(success_data) > 0
        assert success_data[-1].data["value"] == 87.5

        # Test dashboard export
        dashboard_json = dashboard.export_dashboard_json()
        dashboard_data = json.loads(dashboard_json)

        assert "timestamp" in dashboard_data
        assert "charts" in dashboard_data
        assert len(dashboard_data["charts"]) > 0

        self.test_results.append(
            {
                "test": "metrics_dashboard",
                "status": "PASS",
                "details": f"Dashboard with {len(dashboard_data['charts'])} charts working",
            }
        )
        print("   ✅ Metrics dashboard - PASS")

    def test_performance_dashboard(self) -> None:
        """Test performance dashboard functionality"""
        print("📈 Testing performance dashboard...")

        perf_dashboard = PerformanceDashboard()

        # Record performance snapshots
        for i in range(5):
            metrics = {
                "explorations_per_second": 2.0 + (i * 0.1),
                "success_rate": 85.0 + (i * 2.0),
                "avg_exploration_duration": 0.120 + (i * 0.005),
            }
            perf_dashboard.record_performance_snapshot(metrics)

        # Test performance trends
        trends = perf_dashboard.get_performance_trends(hours=1)

        assert "trends" in trends
        assert "success_rate" in trends["trends"]
        assert "avg_exploration_duration" in trends["trends"]

        # Test performance report
        report = perf_dashboard.generate_performance_report()
        assert "TASK-025" in report
        assert "Performance Trends" in report

        self.test_results.append(
            {
                "test": "performance_dashboard",
                "status": "PASS",
                "details": "Performance dashboard tracking and reporting working",
            }
        )
        print("   ✅ Performance dashboard - PASS")

    def test_dashboard_export(self) -> None:
        """Test dashboard export functionality"""
        print("📈 Testing dashboard export...")

        dashboard = get_metrics_dashboard()

        # Test HTML export
        html_dashboard = dashboard.generate_html_dashboard()

        assert "<!DOCTYPE html>" in html_dashboard
        assert "Thinking Exploration Dashboard" in html_dashboard
        assert "chart.js" in html_dashboard
        assert "dashboard-grid" in html_dashboard

        self.test_results.append(
            {
                "test": "dashboard_export",
                "status": "PASS",
                "details": f"HTML dashboard export ({len(html_dashboard)} chars) working",
            }
        )
        print("   ✅ Dashboard export - PASS")

    def test_monitoring_integration(self) -> None:
        """Test integration between monitoring components"""
        print("🔧 Testing monitoring integration...")

        # Test global instances
        metrics = get_metrics()
        tracer = create_tracer()
        health_checker = get_health_checker()
        dashboard = get_metrics_dashboard()

        assert metrics is not None
        assert tracer is not None
        assert health_checker is not None
        assert dashboard is not None

        # Test monitoring workflow
        exploration_id = "integration-test"

        # Start exploration with monitoring
        metrics.record_exploration_start("detailed_analysis", "complex")
        trace_id = tracer.start_exploration_trace(exploration_id, "detailed_analysis", {"test": True})

        # Simulate exploration phases
        with metrics.start_timer("exploration.phase.trigger_detection"):
            tracer.add_exploration_phase(exploration_id, "trigger_detection", {"triggers": ["test"]})
            metrics.record_trigger_detection("test_trigger", 0.9)

        with metrics.start_timer("exploration.phase.model_invocation"):
            tracer.add_model_invocation_trace(exploration_id, "world_model", {"test": True}, 0.025, True)
            metrics.record_model_invocation("world_model", 0.025, True)

        # End exploration
        metrics.record_exploration_success(0.150, "detailed_analysis")
        tracer.end_exploration_trace(exploration_id, True, {"result": "success"})

        # Update dashboard
        thinking_metrics = metrics.get_thinking_metrics()
        dashboard.update_success_rate(thinking_metrics["success_rate"])
        dashboard.update_explorations_rate(thinking_metrics["explorations_per_second"])

        # Verify integration
        assert thinking_metrics["total_explorations"] > 0
        assert trace_id is not None

        health_summary = health_checker.get_health_summary()
        assert health_summary["status"] in ["healthy", "warning", "critical"]

        self.test_results.append(
            {
                "test": "monitoring_integration",
                "status": "PASS",
                "details": "End-to-end monitoring workflow integration working",
            }
        )
        print("   ✅ Monitoring integration - PASS")

    def generate_test_report(self) -> None:
        """Generate comprehensive test report"""
        duration = (datetime.now() - self.start_time).total_seconds()
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        total_tests = len(self.test_results)

        print("\n" + "=" * 60)
        print("🎯 TASK-025: Monitoring & Observability Test Results")
        print("=" * 60)
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        print("\n📋 Test Details:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"   {status_icon} {result['test']}: {result['details']}")

        print(f"\n🚀 TASK-025 Status: {'COMPLETE' if passed_tests == total_tests else 'INCOMPLETE'}")

        if passed_tests == total_tests:
            print("\n🎉 All monitoring and observability tests passed!")
            print("📈 Features implemented:")
            print("   • Comprehensive metrics collection")
            print("   • Distributed tracing with OpenTelemetry patterns")
            print("   • Health checks and system diagnostics")
            print("   • Real-time performance dashboards")
            print("   • JSON and Prometheus export formats")
            print("   • HTML dashboard generation")
            print("   • Integration between all components")
            print("\n✅ Ready for TASK-026: Caching & Optimization")


if __name__ == "__main__":
    test_suite = MonitoringTestSuite()
    test_suite.run_all_tests()
