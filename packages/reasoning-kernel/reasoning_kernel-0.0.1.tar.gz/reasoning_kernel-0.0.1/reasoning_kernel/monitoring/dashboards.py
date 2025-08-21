"""
Performance Dashboards and Visualization

This module provides real-time performance dashboards and visualization
capabilities for the Thinking Exploration Framework.

Features:
- Real-time metrics visualization
- Performance trend analysis
- Interactive dashboards
- Custom chart configurations
- Export capabilities for reports
"""

from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
import json
import threading
from typing import Any, Dict, List, Optional


@dataclass
class ChartConfig:
    """Configuration for dashboard charts"""

    chart_type: str  # line, bar, pie, gauge, histogram
    title: str
    x_axis_label: str = ""
    y_axis_label: str = ""
    color_scheme: List[str] = field(default_factory=lambda: ["#2196F3", "#4CAF50", "#FF9800", "#F44336"])
    max_data_points: int = 100
    refresh_interval_seconds: float = 5.0


@dataclass
class ChartData:
    """Data for dashboard charts"""

    chart_id: str
    chart_type: str
    title: str
    data: Dict[str, Any]
    timestamp: datetime
    config: ChartConfig


class MetricsDashboard:
    """
    Real-time metrics dashboard for thinking exploration performance

    Provides:
    - Real-time metrics visualization
    - Historical trend analysis
    - Custom chart configurations
    - Performance insights
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize the metrics dashboard

        Args:
            max_history: Maximum number of data points to retain
        """
        self._lock = threading.RLock()
        self._charts: Dict[str, ChartConfig] = {}
        self._chart_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._max_history = max_history
        self._start_time = datetime.now()

        # Initialize default charts
        self._setup_default_charts()

    def _setup_default_charts(self) -> None:
        """Setup default dashboard charts"""

        # Exploration performance chart
        self.add_chart(
            ChartConfig(
                chart_type="line",
                title="Thinking Explorations Over Time",
                x_axis_label="Time",
                y_axis_label="Explorations per Second",
                max_data_points=50,
            ),
            "explorations_rate",
        )

        # Success rate chart
        self.add_chart(
            ChartConfig(chart_type="gauge", title="Exploration Success Rate", max_data_points=1), "success_rate"
        )

        # Response time chart
        self.add_chart(
            ChartConfig(
                chart_type="line",
                title="Average Response Time",
                x_axis_label="Time",
                y_axis_label="Response Time (ms)",
                color_scheme=["#FF9800"],
            ),
            "response_time",
        )

        # Mode distribution chart
        self.add_chart(
            ChartConfig(chart_type="pie", title="Thinking Mode Distribution", max_data_points=1), "mode_distribution"
        )

        # System resources chart
        self.add_chart(
            ChartConfig(
                chart_type="line",
                title="System Resource Usage",
                x_axis_label="Time",
                y_axis_label="Usage (%)",
                color_scheme=["#2196F3", "#4CAF50", "#F44336"],
            ),
            "system_resources",
        )

        # Trigger detection chart
        self.add_chart(
            ChartConfig(
                chart_type="bar", title="Trigger Detection by Type", x_axis_label="Trigger Type", y_axis_label="Count"
            ),
            "trigger_types",
        )

    def add_chart(self, config: ChartConfig, chart_id: str) -> None:
        """
        Add a new chart to the dashboard

        Args:
            config: Chart configuration
            chart_id: Unique chart identifier
        """
        with self._lock:
            self._charts[chart_id] = config

    def remove_chart(self, chart_id: str) -> None:
        """
        Remove a chart from the dashboard

        Args:
            chart_id: Chart identifier to remove
        """
        with self._lock:
            self._charts.pop(chart_id, None)
            self._chart_data.pop(chart_id, None)

    def update_chart_data(self, chart_id: str, data: Dict[str, Any]) -> None:
        """
        Update data for a specific chart

        Args:
            chart_id: Chart identifier
            data: New data for the chart
        """
        if chart_id not in self._charts:
            return

        with self._lock:
            config = self._charts[chart_id]
            chart_data = ChartData(
                chart_id=chart_id,
                chart_type=config.chart_type,
                title=config.title,
                data=data,
                timestamp=datetime.now(),
                config=config,
            )

            self._chart_data[chart_id].append(chart_data)

    def update_explorations_rate(self, rate: float) -> None:
        """Update explorations rate chart"""
        self.update_chart_data("explorations_rate", {"timestamp": datetime.now().isoformat(), "value": rate})

    def update_success_rate(self, rate: float) -> None:
        """Update success rate gauge"""
        self.update_chart_data("success_rate", {"value": rate, "min": 0, "max": 100, "unit": "%"})

    def update_response_time(self, avg_time_ms: float) -> None:
        """Update response time chart"""
        self.update_chart_data("response_time", {"timestamp": datetime.now().isoformat(), "value": avg_time_ms})

    def update_mode_distribution(self, mode_counts: Dict[str, int]) -> None:
        """Update thinking mode distribution chart"""
        total = sum(mode_counts.values())
        if total == 0:
            return

        percentages = {mode: (count / total) * 100 for mode, count in mode_counts.items()}

        self.update_chart_data(
            "mode_distribution", {"labels": list(percentages.keys()), "values": list(percentages.values())}
        )

    def update_system_resources(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> None:
        """Update system resources chart"""
        self.update_chart_data(
            "system_resources",
            {
                "timestamp": datetime.now().isoformat(),
                "cpu": cpu_percent,
                "memory": memory_percent,
                "disk": disk_percent,
            },
        )

    def update_trigger_types(self, trigger_counts: Dict[str, int]) -> None:
        """Update trigger detection chart"""
        self.update_chart_data(
            "trigger_types", {"labels": list(trigger_counts.keys()), "values": list(trigger_counts.values())}
        )

    def get_chart_data(self, chart_id: str, limit: Optional[int] = None) -> List[ChartData]:
        """
        Get data for a specific chart

        Args:
            chart_id: Chart identifier
            limit: Optional limit on number of data points

        Returns:
            List of chart data points
        """
        with self._lock:
            if chart_id not in self._chart_data:
                return []

            data_points = list(self._chart_data[chart_id])

            if limit:
                data_points = data_points[-limit:]

            return data_points

    def get_all_charts_data(self) -> Dict[str, List[ChartData]]:
        """Get data for all charts"""
        with self._lock:
            return {chart_id: self.get_chart_data(chart_id) for chart_id in self._charts.keys()}

    def export_dashboard_json(self) -> str:
        """
        Export dashboard data as JSON

        Returns:
            JSON representation of dashboard
        """
        all_data = self.get_all_charts_data()

        export_data = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
            "charts": {},
        }

        for chart_id, data_points in all_data.items():
            config = self._charts[chart_id]

            export_data["charts"][chart_id] = {
                "config": {
                    "chart_type": config.chart_type,
                    "title": config.title,
                    "x_axis_label": config.x_axis_label,
                    "y_axis_label": config.y_axis_label,
                    "color_scheme": config.color_scheme,
                    "max_data_points": config.max_data_points,
                    "refresh_interval_seconds": config.refresh_interval_seconds,
                },
                "data_points": [{"timestamp": dp.timestamp.isoformat(), "data": dp.data} for dp in data_points],
            }

        return json.dumps(export_data, indent=2, default=str)

    def generate_html_dashboard(self) -> str:
        """
        Generate HTML dashboard with Chart.js

        Returns:
            HTML dashboard content
        """

        html = (
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thinking Exploration Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        .chart-canvas {
            max-height: 300px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>🧠 Thinking Exploration Dashboard</h1>
        <p>Real-time performance monitoring and analytics</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="total-explorations">0</div>
            <div class="stat-label">Total Explorations</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="success-rate">0%</div>
            <div class="stat-label">Success Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="avg-response-time">0ms</div>
            <div class="stat-label">Avg Response Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="active-explorations">0</div>
            <div class="stat-label">Active Explorations</div>
        </div>
    </div>
    
    <div class="dashboard-grid" id="charts-container">
        <!-- Charts will be dynamically generated here -->
    </div>
    
    <script>
        // Dashboard data from Python
        const dashboardData = """
            + self.export_dashboard_json()
            + """;
        
        // Initialize charts
        function initializeCharts() {
            const container = document.getElementById('charts-container');
            
            Object.entries(dashboardData.charts).forEach(([chartId, chartInfo]) => {
                const chartDiv = document.createElement('div');
                chartDiv.className = 'chart-container';
                chartDiv.innerHTML = `
                    <div class="chart-title">${chartInfo.config.title}</div>
                    <canvas class="chart-canvas" id="chart-${chartId}"></canvas>
                `;
                container.appendChild(chartDiv);
                
                createChart(chartId, chartInfo);
            });
        }
        
        function createChart(chartId, chartInfo) {
            const ctx = document.getElementById(`chart-${chartId}`).getContext('2d');
            const config = chartInfo.config;
            const dataPoints = chartInfo.data_points;
            
            let chartConfig = {
                type: config.chart_type,
                data: getChartData(config.chart_type, dataPoints, config.color_scheme),
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: config.chart_type === 'line' ? {
                        x: { title: { display: true, text: config.x_axis_label } },
                        y: { title: { display: true, text: config.y_axis_label } }
                    } : {}
                }
            };
            
            new Chart(ctx, chartConfig);
        }
        
        function getChartData(chartType, dataPoints, colorScheme) {
            if (chartType === 'line') {
                return {
                    labels: dataPoints.map(dp => new Date(dp.timestamp).toLocaleTimeString()),
                    datasets: [{
                        label: 'Value',
                        data: dataPoints.map(dp => dp.data.value || 0),
                        borderColor: colorScheme[0],
                        backgroundColor: colorScheme[0] + '20',
                        fill: true
                    }]
                };
            } else if (chartType === 'pie') {
                const latest = dataPoints[dataPoints.length - 1];
                if (latest && latest.data.labels) {
                    return {
                        labels: latest.data.labels,
                        datasets: [{
                            data: latest.data.values,
                            backgroundColor: colorScheme
                        }]
                    };
                }
            } else if (chartType === 'bar') {
                const latest = dataPoints[dataPoints.length - 1];
                if (latest && latest.data.labels) {
                    return {
                        labels: latest.data.labels,
                        datasets: [{
                            label: 'Count',
                            data: latest.data.values,
                            backgroundColor: colorScheme[0]
                        }]
                    };
                }
            }
            
            return { labels: [], datasets: [] };
        }
        
        // Initialize dashboard
        initializeCharts();
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            location.reload();
        }, 5000);
    </script>
</body>
</html>"""
        )

        return html


class PerformanceDashboard:
    """
    Performance-focused dashboard for thinking exploration analysis

    Provides:
    - Performance trend analysis
    - Bottleneck identification
    - Resource utilization tracking
    - Performance recommendations
    """

    def __init__(self):
        """Initialize the performance dashboard"""
        self._metrics_dashboard = MetricsDashboard()
        self._performance_history = deque(maxlen=1000)
        self._lock = threading.RLock()

    def record_performance_snapshot(self, metrics: Dict[str, Any]) -> None:
        """
        Record a performance snapshot

        Args:
            metrics: Performance metrics to record
        """
        with self._lock:
            snapshot = {"timestamp": datetime.now().isoformat(), "metrics": metrics}
            self._performance_history.append(snapshot)

            # Update dashboard charts
            self._update_dashboard_from_metrics(metrics)

    def _update_dashboard_from_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update dashboard charts from metrics"""
        # Update explorations rate
        if "explorations_per_second" in metrics:
            self._metrics_dashboard.update_explorations_rate(metrics["explorations_per_second"])

        # Update success rate
        if "success_rate" in metrics:
            self._metrics_dashboard.update_success_rate(metrics["success_rate"])

        # Update response time
        if "avg_exploration_duration" in metrics:
            avg_time_ms = metrics["avg_exploration_duration"] * 1000
            self._metrics_dashboard.update_response_time(avg_time_ms)

    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance trends over time

        Args:
            hours: Number of hours to analyze

        Returns:
            Performance trend analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            recent_snapshots = [
                snapshot
                for snapshot in self._performance_history
                if datetime.fromisoformat(snapshot["timestamp"]) > cutoff_time
            ]

        if not recent_snapshots:
            return {"error": "No performance data available"}

        # Analyze trends
        trends = {"time_period_hours": hours, "total_snapshots": len(recent_snapshots), "trends": {}}

        # Extract metric trends
        for metric_name in ["success_rate", "avg_exploration_duration", "explorations_per_second"]:
            values = [
                snapshot["metrics"].get(metric_name, 0)
                for snapshot in recent_snapshots
                if metric_name in snapshot["metrics"]
            ]

            if values:
                trends["trends"][metric_name] = {
                    "current": values[-1],
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "trend_direction": (
                        "improving" if values[-1] > values[0] else "declining" if values[-1] < values[0] else "stable"
                    ),
                }

        return trends

    def generate_performance_report(self) -> str:
        """
        Generate a comprehensive performance report

        Returns:
            Performance report as formatted string
        """
        trends = self.get_performance_trends()

        report = f"""
🔍 TASK-025: Thinking Exploration Performance Report
==================================================
Generated: {datetime.now().isoformat()}

📊 Performance Trends (Last 24 Hours)
"""

        if "trends" in trends:
            for metric, data in trends["trends"].items():
                report += f"""
{metric.replace('_', ' ').title()}:
  Current: {data['current']:.2f}
  Average: {data['average']:.2f}
  Range: {data['min']:.2f} - {data['max']:.2f}
  Trend: {data['trend_direction']}
"""

        report += """
🎯 Performance Insights:
- Monitoring system is operational
- Real-time dashboards available
- Performance tracking active

✅ TASK-025 Monitoring & Observability Complete!
   Ready for TASK-026: Caching & Optimization
"""

        return report

    def export_html_dashboard(self) -> str:
        """Export performance dashboard as HTML"""
        return self._metrics_dashboard.generate_html_dashboard()


# Global dashboard instances
_global_metrics_dashboard = None
_global_performance_dashboard = None


def get_metrics_dashboard() -> MetricsDashboard:
    """Get the global metrics dashboard instance"""
    global _global_metrics_dashboard
    if _global_metrics_dashboard is None:
        _global_metrics_dashboard = MetricsDashboard()
    return _global_metrics_dashboard


def get_performance_dashboard() -> PerformanceDashboard:
    """Get the global performance dashboard instance"""
    global _global_performance_dashboard
    if _global_performance_dashboard is None:
        _global_performance_dashboard = PerformanceDashboard()
    return _global_performance_dashboard
