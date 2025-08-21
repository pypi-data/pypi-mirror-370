"""
Rich terminal UI components for MSA Reasoning Engine CLI
"""
import json
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich import box


class UIManager:
    """Manager class for rich terminal UI components"""
    
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose
        self._progress: Optional[Progress] = None
        
    def print_header(self, text: str, style: str = "bold blue"):
        """Print a styled header"""
        self.console.print(f"\n[bold]{text}[/bold]", style=style)
        self.console.print("=" * len(text), style=style)
        
    def print_subheader(self, text: str, style: str = "bold cyan"):
        """Print a styled subheader"""
        self.console.print(f"\n{str(text)}", style=style)
        self.console.print("-" * len(str(text)), style=style)
        
    def print_info(self, message: str):
        """Print an info message"""
        self.console.print(f"ℹ️  {message}", style="blue")
        
    def print_success(self, message: str):
        """Print a success message"""
        self.console.print(f"✅ {message}", style="green")
        
    def print_warning(self, message: str):
        """Print a warning message"""
        self.console.print(f"⚠️  {message}", style="yellow")
        
    def print_error(self, message: str):
        """Print an error message"""
        self.console.print(f"❌ {message}", style="red")
        
    def print_debug(self, message: str):
        """Print a debug message (only in verbose mode)"""
        if self.verbose:
            self.console.print(f"🐛 {message}", style="magenta")
            
    def print_code(self, code: str, language: str = "python", theme: str = "monokai"):
        """Print syntax-highlighted code"""
        try:
            syntax = Syntax(code, language, theme=theme, line_numbers=True)
            self.console.print(syntax)
        except Exception as e:
            # Fallback to plain text if syntax highlighting fails
            self.print_warning(f"Could not highlight code: {e}")
            self.console.print(code)
            
    def print_markdown(self, markdown_text: str):
        """Print markdown-formatted text"""
        try:
            md = Markdown(markdown_text)
            self.console.print(md)
        except Exception as e:
            # Fallback to plain text if markdown rendering fails
            self.print_warning(f"Could not render markdown: {e}")
            self.console.print(markdown_text)
            
    def print_table(self, data: List[Dict[str, Any]], title: str = "", 
                   columns: Optional[List[str]] = None):
        """Print data as a formatted table"""
        if not data:
            self.print_warning("No data to display")
            return
            
        table = Table(title=title, box=box.ROUNDED, show_header=True)
        
        # Determine columns to display
        if columns is None:
            # Use all keys from the first row as columns
            columns = list(data[0].keys()) if data else []
            
        # Add columns to table
        for col in columns:
            table.add_column(col.replace("_", " ").title(), style="cyan")
            
        # Add rows to table
        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])
            
        self.console.print(table)
        
    def print_dict_as_table(self, data: Dict[str, Any], title: str = ""):
        """Print a dictionary as a key-value table"""
        if not data:
            self.print_warning("No data to display")
            return
            
        table = Table(title=title, box=box.ROUNDED, show_header=False)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")
        
        for key, value in data.items():
            # Format value for better display
            if isinstance(value, (dict, list)):
                formatted_value = json.dumps(value, indent=2, default=str)
            else:
                formatted_value = str(value)
            table.add_row(key.replace("_", " ").title(), formatted_value)
            
        self.console.print(table)
        
    def print_analysis_result(self, result: Dict[str, Any], format_type: str = "text"):
        """Print the analysis result with rich formatting"""
        if format_type == "json":
            # For JSON format, just pretty print the JSON
            formatted_json = json.dumps(result, indent=2, default=str)
            self.print_code(formatted_json, language="json")
            return
            
        # Text format with rich formatting
        self.print_header("MSA REASONING ENGINE - ANALYSIS RESULTS", "bold blue")
        
        # Session information
        session_id = result.get("session_id", "Unknown")
        timestamp = result.get("timestamp", "Unknown")
        
        info_table = Table(box=box.SIMPLE)
        info_table.add_column("Information", style="bold")
        info_table.add_column("Value")
        info_table.add_row("Session ID", session_id)
        info_table.add_row("Completed", timestamp)
        self.console.print(info_table)
        
        # Mode information
        mode = result.get("mode", "both")
        self.print_subheader(f"🧠 REASONING MODE: {mode.upper()}", "bold magenta")
        
        # Knowledge extraction results
        if "knowledge_extraction" in result:
            knowledge = result["knowledge_extraction"]
            entities = knowledge.get("entities", {})
            relationships = knowledge.get("relationships", [])
            causal_factors = knowledge.get("causal_factors", [])
            
            self.print_subheader("🔍 KNOWLEDGE EXTRACTION RESULTS", "bold yellow")
            
            knowledge_stats = [
                {"Metric": "Entities Extracted", "Value": len(entities) if isinstance(entities, dict) else 0},
                {"Metric": "Relationships Found", "Value": len(relationships)},
                {"Metric": "Causal Factors Identified", "Value": len(causal_factors)}
            ]
            self.print_table(knowledge_stats)
            
        # Confidence analysis
        if "confidence_analysis" in result:
            confidence = result["confidence_analysis"].get("overall_confidence", 0.0)
            self.print_subheader("📊 CONFIDENCE SCORE", "bold green")
            self.console.print(f"[bold]{confidence:.3f}[/bold]", style="green")
            
        # Detailed results in collapsible sections
        if "reasoning_chains" in result:
            self.print_subheader("🔗 REASONING CHAINS", "bold cyan")
            for chain in result["reasoning_chains"]:
                chain_name = chain.get("name", "Unnamed Chain")
                chain_confidence = chain.get("confidence", 0.0)
                chain_panel = Panel(
                    f"[bold]Confidence:[/bold] {chain_confidence:.3f}\n"
                    f"[bold]Steps:[/bold] {len(chain.get('steps', []))}",
                    title=chain_name,
                    border_style="cyan"
                )
                self.console.print(chain_panel)
                
        self.print_header("End of Analysis", "bold blue")
        
    def start_progress(self, description: str = "Processing..."):
        """Start a progress indicator"""
        if self._progress is None:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console,
                transient=True
            )
            self._progress.start()
            
        task_id = self._progress.add_task(description, total=100)
        return task_id
        
    def update_progress(self, task_id: Any, completed: float, description: str = ""):
        """Update progress indicator"""
        if self._progress:
            self._progress.update(task_id, completed=completed, description=description)
            
    def stop_progress(self):
        """Stop the progress indicator"""
        if self._progress:
            self._progress.stop()
            self._progress = None
            
    def print_streaming_output(self, output: str, is_error: bool = False):
        """Print streaming output with appropriate styling"""
        if is_error:
            self.console.print(f"[red]⚠️  {output}[/red]")
        else:
            self.console.print(f"[cyan]📡 {output}[/cyan]")
            
    def print_execution_result(self, result: Dict[str, Any]):
        """Print execution result with rich formatting"""
        self.print_header("Dayton Execution Results", "bold blue")
        
        # Basic execution info
        info_table = Table(box=box.SIMPLE)
        info_table.add_column("Metric", style="bold")
        info_table.add_column("Value")
        info_table.add_row("Exit Code", str(result.get("exit_code", "N/A")))
        info_table.add_row("Execution Time", f"{result.get('execution_time', 0.0):.2f} seconds")
        info_table.add_row("Status", result.get("status", {}).get("value", "N/A"))
        self.console.print(info_table)
        
        # Output section
        if result.get("stdout"):
            self.print_subheader("Output", "bold green")
            # Try to detect if it's code or regular text
            stdout = result["stdout"]
            if "\n" in stdout and (":" in stdout or "=" in stdout):
                # Likely code output
                self.print_code(stdout, language="python")
            else:
                # Regular text output
                self.console.print(stdout)
                
        # Errors section
        if result.get("stderr"):
            self.print_subheader("Errors", "bold red")
            self.console.print(result["stderr"], style="red")
            
        # PPL-specific results
        if result.get("inference_results"):
            self.print_subheader("Inference Results", "bold magenta")
            self.print_code(
                json.dumps(result["inference_results"], indent=2, default=str), 
                language="json"
            )
            
        # Validation errors
        if result.get("validation_errors"):
            self.print_subheader("Validation Errors", "bold yellow")
            for error in result["validation_errors"]:
                self.console.print(f"• {error}", style="yellow")
                
        self.print_header("End of Execution Results", "bold blue")


# Context manager for UI operations
class UIContext:
    """Context manager for UI operations"""
    
    def __init__(self, verbose: bool = False):
        self.ui = UIManager(verbose=verbose)
        self.task_id = None
        
    def __enter__(self):
        return self.ui
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.task_id:
            self.ui.stop_progress()