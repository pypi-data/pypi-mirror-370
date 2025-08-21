"""
MSA Pipeline Visualization Module

This module provides real-time visualization of the MSA pipeline execution
using ASCII art and rich terminal UI components.
"""

from typing import Any, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich import box

from reasoning_kernel.msa.pipeline.pipeline_stage import StageType, StageStatus, StageResult
from reasoning_kernel.msa.pipeline.msa_pipeline import PipelineExecutionResult


class PipelineVisualizer:
    """Visualizer for MSA pipeline execution"""
    
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose
        self.stage_icons = {
            StageType.KNOWLEDGE_EXTRACTION: "🔍",
            StageType.MODEL_SPECIFICATION: "📐",
            StageType.MODEL_SYNTHESIS: "⚙️",
            StageType.PROBABILISTIC_INFERENCE: "🎲",
            StageType.RESULT_INTEGRATION: "📊"
        }
        self.status_colors = {
            StageStatus.PENDING: "dim",
            StageStatus.RUNNING: "yellow",
            StageStatus.COMPLETED: "green",
            StageStatus.FAILED: "red",
            StageStatus.SKIPPED: "blue"
        }
        
    def _create_pipeline_diagram(self, stage_results: Dict[StageType, StageResult]) -> str:
        """Create ASCII art pipeline diagram"""
        diagram = []
        diagram.append("MSA Pipeline Execution Visualization")
        diagram.append("=" * 50)
        
        # Create visual representation of pipeline stages
        stage_order = [
            StageType.KNOWLEDGE_EXTRACTION,
            StageType.MODEL_SPECIFICATION,
            StageType.MODEL_SYNTHESIS,
            StageType.PROBABILISTIC_INFERENCE,
            StageType.RESULT_INTEGRATION
        ]
        
        for i, stage_type in enumerate(stage_order):
            stage_result = stage_results.get(stage_type)
            icon = self.stage_icons.get(stage_type, "❓")
            status = stage_result.status if stage_result else StageStatus.PENDING
            status_icon = self._get_status_icon(status)
            
            # Add stage to diagram
            stage_line = f"{status_icon} {icon} {stage_type.value.replace('_', ' ').title()}"
            
            # Add execution time if available
            if stage_result and stage_result.execution_time > 0:
                stage_line += f" ({stage_result.execution_time:.2f}s)"
                
            # Add error info if failed
            if status == StageStatus.FAILED and stage_result.error:
                stage_line += f" - ERROR: {stage_result.error[:50]}..."
                
            diagram.append(stage_line)
            
            # Add connector if not last stage
            if i < len(stage_order) - 1:
                diagram.append("    ↓")
                
        return "\n".join(diagram)
    
    def _get_status_icon(self, status: StageStatus) -> str:
        """Get icon for stage status"""
        status_icons = {
            StageStatus.PENDING: "○",
            StageStatus.RUNNING: "◔",
            StageStatus.COMPLETED: "●",
            StageStatus.FAILED: "✖",
            StageStatus.SKIPPED: "⊘"
        }
        return status_icons.get(status, "○")
    
    def _create_metrics_table(self, execution_result: PipelineExecutionResult) -> Table:
        """Create table with performance metrics"""
        table = Table(title="Performance Metrics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        # Add execution time
        if execution_result.total_execution_time > 0:
            table.add_row("Total Execution Time", f"{execution_result.total_execution_time:.2f} seconds")
        
        # Add stage completion stats
        completed_stages = len([r for r in execution_result.stage_results.values() 
                              if r.status == StageStatus.COMPLETED])
        total_stages = len(execution_result.stage_results)
        table.add_row("Stages Completed", f"{completed_stages}/{total_stages}")
        
        # Add confidence metrics if available
        if execution_result.final_result:
            confidence_data = execution_result.final_result.get("confidence_metrics", {})
            if confidence_data:
                overall_confidence = confidence_data.get("overall_confidence", 0.0)
                table.add_row("Overall Confidence", f"{overall_confidence:.3f}")
                
                # Add individual confidence scores
                for key, value in confidence_data.items():
                    if key != "overall_confidence" and isinstance(value, (int, float)):
                        table.add_row(f"  {key.replace('_', ' ').title()}", f"{value:.3f}")
        
        return table
    
    def _create_error_panel(self, execution_result: PipelineExecutionResult) -> Optional[Panel]:
        """Create panel for error visualization"""
        if execution_result.status == "failed" and execution_result.error:
            error_text = Text(execution_result.error, style="red")
            return Panel(error_text, title="Pipeline Error", border_style="red")
        return None
    
    def _create_confidence_visualization(self, execution_result: PipelineExecutionResult) -> Optional[Panel]:
        """Create confidence visualization"""
        if execution_result.final_result:
            confidence_data = execution_result.final_result.get("confidence_metrics", {})
            if confidence_data:
                # Create confidence visualization
                confidence_lines = []
                overall_confidence = confidence_data.get("overall_confidence", 0.0)
                
                # Create a simple bar visualization
                bar_length = 20
                filled_length = int(overall_confidence * bar_length)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                confidence_lines.append(f"Overall Confidence: [{bar}] {overall_confidence:.2%}")
                
                # Add individual confidence scores
                for key, value in confidence_data.items():
                    if key != "overall_confidence" and isinstance(value, (int, float)):
                        filled_length = int(value * bar_length)
                        bar = "█" * filled_length + "░" * (bar_length - filled_length)
                        confidence_lines.append(f"{key.replace('_', ' ').title()}: [{bar}] {value:.2%}")
                
                confidence_text = "\n".join(confidence_lines)
                return Panel(confidence_text, title="Confidence Metrics", border_style="green")
        return None
    
    def display_pipeline_status(self, execution_result: PipelineExecutionResult):
        """Display current pipeline status with visualization"""
        # Clear screen for better visualization
        self.console.clear()
        
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="pipeline", ratio=2),
            Layout(name="metrics", size=8),
            Layout(name="confidence", size=6),
            Layout(name="errors", size=4)
        )
        
        # Header
        layout["header"].update(
            Panel("MSA Pipeline Execution", style="bold blue", box=box.SIMPLE)
        )
        
        # Pipeline diagram
        pipeline_diagram = self._create_pipeline_diagram(execution_result.stage_results)
        layout["pipeline"].update(
            Panel(pipeline_diagram, title="Pipeline Progress", border_style="cyan")
        )
        
        # Metrics
        metrics_table = self._create_metrics_table(execution_result)
        layout["metrics"].update(metrics_table)
        
        # Confidence visualization
        confidence_panel = self._create_confidence_visualization(execution_result)
        if confidence_panel:
            layout["confidence"].update(confidence_panel)
        else:
            layout["confidence"].update(Panel("No confidence data available", title="Confidence Metrics"))
        
        # Error visualization
        error_panel = self._create_error_panel(execution_result)
        if error_panel:
            layout["errors"].update(error_panel)
        else:
            layout["errors"].update(Panel("No errors", title="Error Status", style="green"))
        
        # Print the layout
        self.console.print(layout)
    
    def update_stage_progress(self, stage_type: StageType, status: StageStatus, 
                             execution_time: float = 0.0, error: Optional[str] = None):
        """Update visualization for a specific stage"""
        status_text = f"{stage_type.value}: {status.value}"
        if execution_time > 0:
            status_text += f" ({execution_time:.2f}s)"
        if error:
            status_text += f" - ERROR: {error}"
            
        self.console.print(status_text, style=self.status_colors.get(status, "white"))
    
    def display_final_results(self, execution_result: PipelineExecutionResult):
        """Display final results with visualization"""
        self.console.clear()
        
        # Display completion message
        if execution_result.status == "completed":
            self.console.print("✅ Pipeline Execution Completed Successfully!", style="bold green")
        else:
            self.console.print("❌ Pipeline Execution Failed", style="bold red")
        
        # Display pipeline diagram
        pipeline_diagram = self._create_pipeline_diagram(execution_result.stage_results)
        self.console.print(Panel(pipeline_diagram, title="Final Pipeline Status", border_style="cyan"))
        
        # Display metrics
        metrics_table = self._create_metrics_table(execution_result)
        self.console.print(metrics_table)
        
        # Display confidence if available
        confidence_panel = self._create_confidence_visualization(execution_result)
        if confidence_panel:
            self.console.print(confidence_panel)
            
        # Display errors if any
        error_panel = self._create_error_panel(execution_result)
        if error_panel:
            self.console.print(error_panel)
            
        # Display summary
        summary_text = f"Execution completed in {execution_result.total_execution_time:.2f} seconds"
        self.console.print(Panel(summary_text, title="Summary", border_style="blue"))


class LivePipelineVisualizer:
    """Live updating pipeline visualizer"""
    
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose
        self.visualizer = PipelineVisualizer(verbose)
        self.live_display = None
        self.current_execution = None
        
    async def start_visualization(self, execution_result: PipelineExecutionResult):
        """Start live visualization"""
        self.current_execution = execution_result
        
        # Create initial display
        self.visualizer.display_pipeline_status(execution_result)
        
    async def update_visualization(self, execution_result: PipelineExecutionResult):
        """Update live visualization"""
        self.current_execution = execution_result
        self.visualizer.display_pipeline_status(execution_result)
        
    async def update_stage(self, stage_type: StageType, status: StageStatus, 
                          execution_time: float = 0.0, error: Optional[str] = None):
        """Update visualization for a specific stage"""
        if self.verbose:
            self.visualizer.update_stage_progress(stage_type, status, execution_time, error)
            
    async def finish_visualization(self, execution_result: PipelineExecutionResult):
        """Finish visualization and show final results"""
        self.visualizer.display_final_results(execution_result)


# Utility functions for integration with MSA pipeline

def create_visualizer(verbose: bool = False) -> PipelineVisualizer:
    """Create a pipeline visualizer instance"""
    return PipelineVisualizer(verbose)


def create_live_visualizer(verbose: bool = False) -> LivePipelineVisualizer:
    """Create a live pipeline visualizer instance"""
    return LivePipelineVisualizer(verbose)


async def visualize_pipeline_execution(pipeline, scenario: str, session_id: Optional[str] = None,
                                     user_context: Optional[Dict[str, Any]] = None,
                                     verbose: bool = False) -> PipelineExecutionResult:
    """Execute pipeline with visualization"""
    # Create visualizer
    visualizer = create_live_visualizer(verbose)
    
    # Execute pipeline with visualization
    execution_result = await pipeline.execute(scenario, session_id, user_context)
    
    # Update visualization with final results
    await visualizer.finish_visualization(execution_result)
    
    return execution_result