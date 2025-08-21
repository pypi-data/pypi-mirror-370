"""
Core CLI framework for MSA Reasoning Engine using Click
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import click
from reasoning_kernel.core.env import load_project_dotenv
from reasoning_kernel.core.kernel_config import KernelManager
from reasoning_kernel.msa.synthesis_engine import MSAEngine

# Add new imports for Daytona integration
from reasoning_kernel.services.daytona_service import DaytonaService, SandboxConfig
from reasoning_kernel.services.daytona_ppl_executor import DaytonaPPLExecutor, PPLProgram, PPLFramework

# Add import for rich UI components
from reasoning_kernel.cli.ui import UIManager

# Add import for visualization
from reasoning_kernel.cli.visualization import visualize_pipeline_execution

# Add import for session management
from reasoning_kernel.cli.session import session_manager

# Add imports for export and batch processing
from reasoning_kernel.cli.batch import BatchProcessor

# Add imports for CoSci examples and benchmark commands
from reasoning_kernel.cli.examples import examples
from reasoning_kernel.cli.benchmark import benchmark

# Add import for wizard
from reasoning_kernel.cli.wizard import wizard

# Load environment variables from project root .env for CLI usage
load_project_dotenv(override=False)

# Configure structured logging before importing modules that use it
from reasoning_kernel.core.logging_config import configure_logging
configure_logging(level="INFO", json_logs=False)

# Add imports for new command modules (moved to bottom to avoid circular imports)
# Command modules will be imported locally in the function below

# Configure basic logging as fallback
logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class MSACliContext:
    """Context object for MSA CLI that holds shared state"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.kernel_manager: Optional[KernelManager] = None
        self.msa_engine: Optional[MSAEngine] = None
        self.session_counter = 0
        # Add Daytona service to context
        self.daytona_service: Optional[DaytonaService] = None
        self.ppl_executor: Optional[DaytonaPPLExecutor] = None
        # Add UI manager to context
        self.ui_manager: Optional[UIManager] = None
        # Add session manager to context
        self.session_manager = session_manager

    async def initialize(self):
        """Initialize the MSA components"""
        try:
            # Initialize UI manager
            self.ui_manager = UIManager(verbose=self.verbose)
            
            if self.verbose:
                self.ui_manager.print_info("Initializing MSA Reasoning Engine...")

            # Initialize Semantic Kernel
            self.kernel_manager = KernelManager()
            await self.kernel_manager.initialize()

            # Initialize MSA Engine
            self.msa_engine = MSAEngine(self.kernel_manager)
            await self.msa_engine.initialize()

            # Initialize Daytona service
            if self.verbose:
                self.ui_manager.print_info("Initializing Daytona sandbox service...")
            self.daytona_service = DaytonaService()
            self.ppl_executor = DaytonaPPLExecutor(self.daytona_service)
            
            if self.verbose:
                self.ui_manager.print_success("MSA Reasoning Engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MSA components: {e}")
            if self.ui_manager:
                self.ui_manager.print_error(f"Failed to initialize MSA components: {e}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.verbose and self.ui_manager:
                self.ui_manager.print_info("Cleaning up resources...")
                
            if self.msa_engine:
                await self.msa_engine.cleanup()
            if self.kernel_manager:
                await self.kernel_manager.cleanup()
                
            # Cleanup Daytona service
            if self.daytona_service:
                try:
                    await self.daytona_service.cleanup_sandbox()
                except Exception as e:
                    logger.warning(f"Error cleaning up Daytona sandbox: {e}")
                    if self.ui_manager:
                        self.ui_manager.print_warning(f"Error cleaning up Daytona sandbox: {e}")
                
            if self.verbose and self.ui_manager:
                self.ui_manager.print_success("Cleanup completed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
            if self.ui_manager:
                self.ui_manager.print_warning(f"Error during cleanup: {e}")


class MSACli:
    """Base CLI class for MSA Reasoning Engine"""

    def __init__(self, context: MSACliContext):
        self.context = context

    @staticmethod
    def _validate_environment(ui_manager: Optional[UIManager] = None):
        """Validate required environment variables"""
        required_keys = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
        ]
        missing_keys = [key for key in required_keys if not os.environ.get(key)]

        if missing_keys:
            if ui_manager:
                ui_manager.print_error(f"Missing required environment variables: {', '.join(missing_keys)}")
                ui_manager.print_info("Please set the following Azure OpenAI credentials:")
                for key in missing_keys:
                    ui_manager.console.print(f"   - {key}")
            else:
                click.echo(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
                click.echo("\n💡 Please set the following Azure OpenAI credentials:")
                for key in missing_keys:
                    click.echo(f"   - {key}")
            sys.exit(1)

    async def run_reasoning(
        self,
        scenario: str,
        mode: str = "both",
        output_format: str = "text",
        session_id: Optional[str] = None,
        visualize: bool = False,
    ) -> Dict[str, Any]:
        """Run MSA reasoning on a scenario"""
        if not self.context or not self.context.msa_engine:
            raise RuntimeError("MSA Engine not initialized.")

        # Generate session ID if not provided
        if not session_id:
            self.context.session_counter += 1
            session_id = f"cli-session-{self.context.session_counter}-{int(datetime.now().timestamp())}"

        try:
            ui_manager = self.context.ui_manager
            if ui_manager:
                if self.context.verbose:
                    ui_manager.print_info(f"Analyzing scenario: {scenario[:100]}{'...' if len(scenario) > 100 else ''}")
                    ui_manager.print_info(f"Mode: {mode}")
                    ui_manager.print_info(f"Session ID: {session_id}")
                    if visualize:
                        ui_manager.print_info("Pipeline visualization enabled")
            else:
                if self.context.verbose:
                    click.echo(f"🔄 Analyzing scenario: {scenario[:100]}{'...' if len(scenario) > 100 else ''}")
                    click.echo(f"🎯 Mode: {mode}")
                    click.echo(f"🆔 Session ID: {session_id}")
                    if visualize:
                        click.echo("👁️ Pipeline visualization enabled")

            if mode == "knowledge":
                if not self.context.msa_engine.knowledge_extractor:
                    raise RuntimeError("Knowledge extractor not available")
                result = await self.context.msa_engine.knowledge_extractor.extract_scenario_knowledge(scenario)
                result = {
                    "mode": "knowledge",
                    "scenario": scenario,
                    "session_id": session_id,
                    "knowledge_extraction": result,
                    "timestamp": datetime.now().isoformat(),
                }
            elif mode == "both":
                # Use visualization if requested
                if visualize and self.context.msa_engine.pipeline:
                    # Execute pipeline with visualization
                    execution_result = await visualize_pipeline_execution(
                        self.context.msa_engine.pipeline,
                        scenario=scenario,
                        session_id=session_id,
                        verbose=self.context.verbose
                    )
                    
                    # Convert execution result to dict for compatibility
                    result = {
                        "mode": "both",
                        "scenario": scenario,
                        "session_id": session_id,
                        "execution_result": execution_result.__dict__ if hasattr(execution_result, '__dict__') else str(execution_result),
                        "timestamp": datetime.now().isoformat(),
                    }
                    
                    # Add final result if available
                    if hasattr(execution_result, 'final_result') and execution_result.final_result:
                        result.update(execution_result.final_result)
                else:
                    result = await self.context.msa_engine.reason_about_scenario(
                        scenario=scenario, session_id=session_id
                    )
            else:
                raise ValueError(f"Invalid mode: {mode}")

            # Add query and result to session if session ID is provided
            if session_id and session_id != "cli-session-0-0":
                try:
                    session_manager.add_query_to_session(session_id, scenario, result)
                except Exception as e:
                    logger.warning(f"Failed to add query to session: {e}")
                    if ui_manager:
                        ui_manager.print_warning(f"Failed to track query in session: {e}")

            if ui_manager:
                if self.context.verbose:
                    ui_manager.print_success("Analysis completed successfully")
            else:
                if self.context.verbose:
                    click.echo("✅ Analysis completed successfully")

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            if self.context.ui_manager:
                self.context.ui_manager.print_error(f"Analysis failed: {str(e)}")
            raise

    def format_output(self, result: Dict[str, Any], format_type: str = "text") -> str:
        """Format the output for display"""
        if self.context.ui_manager:
            # For rich UI, we'll handle formatting in the UI manager
            return json.dumps(result, indent=2, default=str)
        
        # Fallback to original formatting if UI manager is not available
        if format_type == "json":
            return json.dumps(result, indent=2, default=str)
        
        # Text format
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("MSA REASONING ENGINE - ANALYSIS RESULTS".center(80))
        output_lines.append("=" * 80)
        
        session_id = result.get("session_id", "Unknown")
        timestamp = result.get("timestamp", "Unknown")
        
        output_lines.append(f"📋 Session ID: {session_id}")
        output_lines.append(f"🕐 Completed: {timestamp}")
        output_lines.append("")
        
        mode = result.get("mode", "both")
        output_lines.append(f"🧠 REASONING MODE: {mode.upper()}")
        
        if "knowledge_extraction" in result:
            knowledge = result["knowledge_extraction"]
            entities = knowledge.get("entities", {})
            relationships = knowledge.get("relationships", [])
            causal_factors = knowledge.get("causal_factors", [])
            
            output_lines.append("\n🔍 KNOWLEDGE EXTRACTION RESULTS:")
            output_lines.append(f"   • Entities extracted: {len(entities) if isinstance(entities, dict) else 0}")
            output_lines.append(f"   • Relationships found: {len(relationships)}")
            output_lines.append(f"   • Causal factors identified: {len(causal_factors)}")
        
        if "confidence_analysis" in result:
            confidence = result["confidence_analysis"].get("overall_confidence", 0.0)
            output_lines.append(f"\n📊 CONFIDENCE SCORE: {confidence:.3f}")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("End of Analysis".center(80))
        output_lines.append("=" * 80)
        
        return "\n".join(output_lines)


# Async command decorator
def async_command(f):
    """Decorator to run async functions in Click commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


# CLI Group and Commands
@click.group(invoke_without_command=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--interactive", "-i", is_flag=True, help="Start interactive mode")
@click.pass_context
def cli(ctx, verbose: bool, interactive: bool):
    """MSA Reasoning Engine CLI"""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["INTERACTIVE"] = interactive

    if ctx.invoked_subcommand is None:
        if interactive:
            ctx.invoke(interactive_mode)
        else:
            # Show help if no command is provided
            click.echo(ctx.get_help())


@cli.command()
@click.argument("scenario", required=False)
@click.option("--mode", "-m", type=click.Choice(["knowledge", "both"]), default="both", help="Reasoning mode")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read scenario from file")
@click.option("--visualize", "-vz", is_flag=True, help="Enable pipeline visualization")
@click.pass_context
@async_command
async def analyze(ctx, scenario: str, mode: str, output: str, session_id: str, file: str, visualize: bool):
    """Analyze a scenario using the MSA Reasoning Engine"""
    verbose = ctx.obj.get("VERBOSE", False)
    
    # Initialize UI manager
    ui_manager = UIManager(verbose=verbose)
    
    # Read scenario from file if provided
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                scenario = f.read().strip()
        except Exception as e:
            ui_manager.print_error(f"Error reading file: {e}")
            return
    
    if not scenario:
        ui_manager.print_error("Please provide a scenario to analyze")
        return

    # Validate environment
    MSACli._validate_environment(ui_manager)

    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    try:
        await cli_context.initialize()
        
        # Create CLI instance
        msa_cli = MSACli(cli_context)
        
        # Run reasoning with progress indicator
        task_id = ui_manager.start_progress("Analyzing scenario...")
        try:
            # Update progress during analysis
            ui_manager.update_progress(task_id, 50, "Processing...")
            
            # Run reasoning
            result = await msa_cli.run_reasoning(
                scenario=scenario,
                mode=mode,
                output_format=output,
                session_id=session_id,
                visualize=visualize,
            )
            
            # Complete progress
            ui_manager.update_progress(task_id, 100, "Analysis complete!")
        finally:
            ui_manager.stop_progress()
        
        # Format and display output
        formatted_output = msa_cli.format_output(result, output)
        click.echo(formatted_output)
                
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        ui_manager.print_error(f"Analysis failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        await cli_context.cleanup()


@cli.command()
def version():
    """Show the version of MSA Reasoning Engine"""
    from reasoning_kernel import __version__
    ui_manager = UIManager()
    ui_manager.print_success(f"MSA Reasoning Engine v{__version__}")


@cli.command()
@click.pass_context
def interactive_mode(ctx):
    """Start interactive mode"""
    verbose = ctx.obj.get("VERBOSE", False)
    
    # Validate environment
    ui_manager = UIManager(verbose=verbose)
    MSACli._validate_environment(ui_manager)
    
    # Run the interactive loop
    asyncio.run(_run_interactive_mode(verbose))


async def _run_interactive_mode(verbose: bool):
    """Run the interactive mode loop"""
    ui_manager = UIManager(verbose=verbose)
    ui_manager.print_success("Welcome to the MSA Reasoning Engine Interactive Mode")
    ui_manager.print_info("Enter scenarios to analyze complex decision-making situations")
    ui_manager.print_info("Type 'help' for commands, 'quit' to exit")
    ui_manager.print_info("Type 'visualize' to toggle pipeline visualization")
    ui_manager.console.print("-" * 50, style="dim")
    
    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    msa_cli = None
    visualize_enabled = False
    
    try:
        await cli_context.initialize()
        msa_cli = MSACli(cli_context)
        
        session_count = 0
        
        while True:
            try:
                prompt = f"\n[Session {session_count + 1}] 📝 Enter scenario (or command): "
                user_input = input(prompt).strip()
                
                if user_input.lower() in ["quit", "exit"]:
                    ui_manager.print_success("Goodbye!")
                    break
                elif user_input.lower() == "help":
                    ui_manager.print_info("Available commands:")
                    ui_manager.console.print("  quit/exit - Exit the interactive mode")
                    ui_manager.console.print("  help      - Show this help message")
                    ui_manager.console.print("  visualize - Toggle pipeline visualization")
                    ui_manager.console.print("  <scenario> - Analyze a scenario")
                    continue
                elif user_input.lower() == "visualize":
                    visualize_enabled = not visualize_enabled
                    ui_manager.print_info(f"Pipeline visualization {'enabled' if visualize_enabled else 'disabled'}")
                    continue
                elif not user_input:
                    ui_manager.print_warning("Please enter a scenario to analyze or a command")
                    continue
                
                # Process the scenario
                session_count += 1
                ui_manager.print_info("Processing your scenario...")
                
                # Run reasoning with progress indicator
                task_id = ui_manager.start_progress("Analyzing scenario...")
                try:
                    # Update progress during analysis
                    ui_manager.update_progress(task_id, 50, "Processing...")
                    
                    # Run reasoning
                    result = await msa_cli.run_reasoning(
                        scenario=user_input,
                        mode="both",
                        session_id=f"interactive-{session_count}",
                        visualize=visualize_enabled,
                    )
                    
                    # Complete progress
                    ui_manager.update_progress(task_id, 100, "Analysis complete!")
                finally:
                    ui_manager.stop_progress()
                
                # Format and display output
                ui_manager.print_analysis_result(result, "text")
                
            except KeyboardInterrupt:
                ui_manager.print_warning("Operation cancelled. Continuing...")
                continue
            except Exception as e:
                logger.error(f"Error processing scenario: {e}")
                ui_manager.print_error("An error occurred while processing your scenario. Continuing...")
                
    except Exception as e:
        logger.error(f"Failed to start interactive mode: {e}")
        ui_manager.print_error(f"Failed to start interactive mode: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if cli_context:
            await cli_context.cleanup()


# Additional command groups
@cli.group()
def config():
    """Configuration management commands"""
    pass


def _is_sensitive_key(key: str) -> bool:
    """Check if a configuration key is sensitive"""
    sensitive_words = ["API_KEY", "PASSWORD", "SECRET"]
    key_upper = key.upper()
    for word in sensitive_words:
        if word in key_upper:
            return True
    return False


def _should_mask_value(key: str, value: str) -> bool:
    """Check if a configuration value should be masked"""
    if not _is_sensitive_key(key):
        return False
    if not value:
        return False
    placeholder_values = ["your_azure_openai_key_here", "your_daytona_key_here"]
    return value not in placeholder_values


@config.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def show(verbose: bool):
    """Show current configuration"""
    ui_manager = UIManager(verbose=verbose)
    
    try:
        # Load configuration files
        import json
        import os
        
        # Get paths to config files
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_config_path = os.path.join(project_root, "config", "default_config.json")
        user_config_path = os.path.join(project_root, "config", "user_config.json")
        
        # Load default configuration
        default_config = {}
        if os.path.exists(default_config_path):
            try:
                with open(default_config_path, 'r') as f:
                    default_config = json.load(f)
            except Exception as e:
                ui_manager.print_warning(f"Could not load default config: {e}")
        
        # Load user configuration
        user_config = {}
        if os.path.exists(user_config_path):
            try:
                with open(user_config_path, 'r') as f:
                    user_config = json.load(f)
            except Exception as e:
                ui_manager.print_warning(f"Could not load user config: {e}")
        
        # Merge configurations (user config overrides default config)
        merged_config = {**default_config, **user_config}
        
        # Display configuration
        ui_manager.print_header("MSA Reasoning Engine Configuration")
        
        if not merged_config:
            ui_manager.print_warning("No configuration found")
            return
            
        # Hide sensitive information
        display_config = merged_config.copy()
        for key in display_config:
            if _should_mask_value(key, display_config[key]):
                display_config[key] = "********"  # Mask sensitive values
        
        ui_manager.print_dict_as_table(display_config, "Current Configuration")
            
        # Show config file locations
        ui_manager.print_subheader("Configuration Files")
        ui_manager.console.print(f"Default config: {default_config_path}")
        ui_manager.console.print(f"User config: {user_config_path}")
        
    except Exception as e:
        ui_manager.print_error(f"Error showing configuration: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


@config.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--file", type=click.Path(), help="Configuration file to modify")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def set(key: str, value: str, file: str, verbose: bool):
    """Set configuration values"""
    ui_manager = UIManager(verbose=verbose)
    
    try:
        import json
        import os
        
        # If no key/value provided, show help
        if not key:
            ui_manager.print_info("Usage: msa config set <key> <value>")
            ui_manager.print_info("Example: msa config set AZURE_OPENAI_DEPLOYMENT gpt-4-turbo")
            return
            
        # If no value provided, show current value
        if not value:
            # Load configuration
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = file or os.path.join(project_root, "config", "user_config.json")
            
            if not os.path.exists(config_path):
                ui_manager.print_error(f"Configuration file not found: {config_path}")
                return
                
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                ui_manager.print_error(f"Error reading configuration: {e}")
                return
                
            if key not in config:
                ui_manager.print_warning(f"Key '{key}' not found in configuration")
                return
                
            # Hide sensitive information
            display_value = config[key]
            if _should_mask_value(key, display_value):
                display_value = "********"  # Mask sensitive values
            
            ui_manager.print_info(f"{key} = {display_value}")
            return
        
        # Set the configuration value
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = file or os.path.join(project_root, "config", "user_config.json")
        
        # Load existing configuration
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                ui_manager.print_warning(f"Could not load existing config: {e}")
        else:
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(config_path)
            os.makedirs(config_dir, exist_ok=True)
        
        # Set the new value
        config[key] = value
        
        # Save configuration
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            ui_manager.print_success(f"Configuration updated: {key} = {value}")
        except Exception as e:
            ui_manager.print_error(f"Error saving configuration: {e}")
            return
            
        # Validate sensitive keys
        if _is_sensitive_key(key):
            ui_manager.print_warning("You've updated a sensitive configuration value. Make sure to keep it secure.")
            
    except Exception as e:
        ui_manager.print_error(f"Error setting configuration: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


@cli.group()
def model():
    """Model management commands"""
    pass


@model.command()
def list():
    """List available models"""
    ui_manager = UIManager()
    ui_manager.print_warning("Model listing is not yet implemented")


@model.command()
def info():
    """Show model information"""
    ui_manager = UIManager()
    ui_manager.print_warning("Model information is not yet implemented")


@cli.group()
def session():
    """Session management commands"""
    pass


@cli.group()
def history():
    """History tracking and search commands"""
    pass


@history.command()
@click.option("--limit", "-l", type=int, default=20, help="Number of history entries to show")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def list(limit: int, verbose: bool):
    """List recent history entries"""
    ui_manager = UIManager(verbose=verbose)
    try:
        history_data = session_manager.get_history(limit=limit)
        
        if not history_data or not history_data.get("queries"):
            ui_manager.print_info("No history found")
            return
        
        ui_manager.print_header("Recent History")
        
        # Display recent queries
        queries = history_data.get("queries", [])
        for i, query_entry in enumerate(queries, 1):
            ui_manager.console.print(f"{i}. {query_entry.get('query', 'Unknown')}")
            ui_manager.console.print(f"   Timestamp: {query_entry.get('timestamp', 'Unknown')}")
            if verbose and query_entry.get("result"):
                ui_manager.console.print(f"   Result preview: {str(query_entry['result'])[:100]}...")
            ui_manager.console.print("")
        
        ui_manager.print_info(f"Showing {len(queries)} of {len(history_data.get('queries', []))} total entries")
            
    except Exception as e:
        logger.error(f"Failed to list history: {e}")
        ui_manager.print_error(f"Failed to list history: {e}")


@history.command()
@click.argument("query_text", required=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def search(query_text: str, verbose: bool):
    """Search history for queries containing the given text"""
    ui_manager = UIManager(verbose=verbose)
    try:
        matching_queries = session_manager.search_history(query_text)
        
        if not matching_queries:
            ui_manager.print_info(f"No history entries found matching '{query_text}'")
            return
        
        ui_manager.print_header(f"Search Results for '{query_text}'")
        
        # Display matching queries
        for i, query_entry in enumerate(matching_queries, 1):
            ui_manager.console.print(f"{i}. {query_entry.get('query', 'Unknown')}")
            ui_manager.console.print(f"   Timestamp: {query_entry.get('timestamp', 'Unknown')}")
            if verbose and query_entry.get("result"):
                ui_manager.console.print(f"   Result preview: {str(query_entry['result'])[:100]}...")
            ui_manager.console.print("")
        
        ui_manager.print_info(f"Found {len(matching_queries)} matching entries")
            
    except Exception as e:
        logger.error(f"Failed to search history: {e}")
        ui_manager.print_error(f"Failed to search history: {e}")


@history.command()
@click.option("--force", "-f", is_flag=True, help="Force clearing without confirmation")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def clear(force: bool, verbose: bool):
    """Clear all history"""
    ui_manager = UIManager(verbose=verbose)
    try:
        # Confirm clearing unless force flag is used
        if not force:
            ui_manager.print_warning("Are you sure you want to clear all history?")
            confirmation = input("Type 'yes' to confirm: ").strip().lower()
            if confirmation != "yes":
                ui_manager.print_info("Clearing cancelled")
                return
        
        # Clear history file
        if os.path.exists(session_manager.history_file):
            # Create backup
            backup_file = session_manager.history_file + ".backup"
            import shutil
            shutil.copy2(session_manager.history_file, backup_file)
            
            # Reinitialize history file
            session_manager._initialize_history_file()
            
            ui_manager.print_success(f"History cleared successfully (backup saved to {backup_file})")
        else:
            ui_manager.print_info("No history file found to clear")
            
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        ui_manager.print_error(f"Failed to clear history: {e}")


@session.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def list(verbose: bool):
    """List saved sessions"""
    ui_manager = UIManager(verbose=verbose)
    try:
        sessions = session_manager.list_sessions()
        
        if not sessions:
            ui_manager.print_info("No sessions found")
            return
        
        ui_manager.print_header("Saved Sessions")
        
        # Format sessions for display
        session_data = []
        for session in sessions:
            session_data.append({
                "ID": session.get("id", "Unknown"),
                "Description": session.get("description", "No description"),
                "Created": session.get("created_at", "Unknown")
            })
        
        ui_manager.print_table(session_data)
        
        if verbose:
            ui_manager.print_info(f"Total sessions: {len(sessions)}")
            
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        ui_manager.print_error(f"Failed to list sessions: {e}")


@session.command()
@click.argument("session_id", required=True)
@click.option("--description", "-d", default="", help="Session description")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def create(session_id: str, description: str, verbose: bool):
    """Create a new session"""
    ui_manager = UIManager(verbose=verbose)
    try:
        # Check if session already exists
        existing_session = session_manager.load_session(session_id)
        if existing_session:
            ui_manager.print_warning(f"Session '{session_id}' already exists")
            return
        
        # Create new session
        created_id = session_manager.create_session(session_id, description)
        
        if created_id:
            ui_manager.print_success(f"Session '{created_id}' created successfully")
        else:
            ui_manager.print_error("Failed to create session")
            
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        ui_manager.print_error(f"Failed to create session: {e}")


@session.command()
@click.argument("session_id", required=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def load(session_id: str, verbose: bool):
    """Load a saved session"""
    ui_manager = UIManager(verbose=verbose)
    try:
        session_data = session_manager.load_session(session_id)
        
        if session_data:
            ui_manager.print_header(f"Session: {session_data.get('id', 'Unknown')}")
            
            # Display session metadata
            metadata = {
                "ID": session_data.get("id", "Unknown"),
                "Description": session_data.get("description", "No description"),
                "Created At": session_data.get("created_at", "Unknown"),
                "Query Count": len(session_data.get("queries", []))
            }
            ui_manager.print_dict_as_table(metadata, "Session Metadata")
            
            # Display recent queries if any
            queries = session_data.get("queries", [])
            if queries:
                ui_manager.print_subheader("Recent Queries")
                for i, query_entry in enumerate(queries[-5:], 1):  # Show last 5 queries
                    ui_manager.console.print(f"{i}. {query_entry.get('query', 'Unknown')}")
                    ui_manager.console.print(f"   Timestamp: {query_entry.get('timestamp', 'Unknown')}")
                    ui_manager.console.print("")
        else:
            ui_manager.print_error(f"Session '{session_id}' not found")
            
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        ui_manager.print_error(f"Failed to load session: {e}")


@session.command()
@click.argument("session_id", required=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
def delete(session_id: str, verbose: bool, force: bool):
    """Delete a saved session"""
    ui_manager = UIManager(verbose=verbose)
    try:
        # Check if session exists
        session_data = session_manager.load_session(session_id)
        if not session_data:
            ui_manager.print_error(f"Session '{session_id}' not found")
            return
        
        # Confirm deletion unless force flag is used
        if not force:
            ui_manager.print_warning(f"Are you sure you want to delete session '{session_id}'?")
            confirmation = input("Type 'yes' to confirm: ").strip().lower()
            if confirmation != "yes":
                ui_manager.print_info("Deletion cancelled")
                return
        
        # Delete session
        success = session_manager.delete_session(session_id)
        
        if success:
            ui_manager.print_success(f"Session '{session_id}' deleted successfully")
        else:
            ui_manager.print_error(f"Failed to delete session '{session_id}'")
            
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        ui_manager.print_error(f"Failed to delete session: {e}")


@session.command()
@click.argument("session_id", required=True)
@click.option("--output", "-o", required=True, help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "md", "pdf"]), default="json", help="Export format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def export(session_id: str, output: str, format: str, verbose: bool):
    """Export a session to specified format"""
    ui_manager = UIManager(verbose=verbose)
    try:
        success = session_manager.export_session(session_id, output, format)
        if success:
            ui_manager.print_success(f"Session '{session_id}' exported successfully to {output}")
        else:
            ui_manager.print_error(f"Failed to export session '{session_id}'")
    except Exception as e:
        logger.error(f"Failed to export session: {e}")
        ui_manager.print_error(f"Failed to export session: {e}")


# Add new export command group
@cli.group()
def export():
    """Export commands for sessions and history"""
    pass


@export.command()
@click.option("--output", "-o", required=True, help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "md", "pdf"]), default="json", help="Export format")
@click.option("--limit", "-l", type=int, help="Limit number of history entries")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def history(output: str, format: str, limit: int, verbose: bool):
    """Export history to specified format"""
    ui_manager = UIManager(verbose=verbose)
    try:
        success = session_manager.export_history(output, format, limit)
        if success:
            ui_manager.print_success(f"History exported successfully to {output}")
        else:
            ui_manager.print_error("Failed to export history")
    except Exception as e:
        logger.error(f"Failed to export history: {e}")
        ui_manager.print_error(f"Failed to export history: {e}")


# Add new batch command group
@cli.group()
def batch():
    """Batch processing commands"""
    pass


@batch.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", help="Output directory for results")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@async_command
async def process(input_file: str, output_dir: str, session_id: str, verbose: bool):
    """Process multiple queries in batch mode"""
    ui_manager = UIManager(verbose=verbose)
    try:
        # Create batch processor
        processor = BatchProcessor(verbose=verbose)
        
        # Load queries from file
        queries = processor.load_queries_from_file(input_file)
        
        # Process queries
        results = await processor.process_queries(queries, output_dir, session_id)
        
        ui_manager.print_success(f"Batch processing completed. Processed {len(results)} queries.")
        
        # Optionally save summary
        if output_dir:
            summary_file = os.path.join(output_dir, "batch_summary.json")
            summary_data = {
                "total_queries": len(queries),
                "successful_queries": len(results),
                "failed_queries": len(queries) - len(results),
                "output_directory": output_dir
            }
            try:
                with open(summary_file, 'w') as f:
                    json.dump(summary_data, f, indent=2)
                ui_manager.print_info(f"Batch summary saved to {summary_file}")
            except Exception as e:
                ui_manager.print_warning(f"Failed to save batch summary: {e}")
                
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        ui_manager.print_error(f"Batch processing failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# Add new sandbox command group for Daytona integration
@cli.group()
def sandbox():
    """Daytona sandbox operations for secure code execution"""
    pass


@sandbox.command(name="status")
@click.pass_context
@async_command
async def sandbox_status(ctx):
    """Check Daytona sandbox status"""
    verbose = ctx.obj.get("VERBOSE", False)
    
    # Initialize UI manager
    ui_manager = UIManager(verbose=verbose)
    
    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    try:
        await cli_context.initialize()
        
        if not cli_context.daytona_service:
            ui_manager.print_error("Daytona service not initialized")
            return
            
        # Get service status
        status_info = cli_context.daytona_service.get_status()
        
        # Display status information using rich formatting
        ui_manager.print_header("Daytona Sandbox Status")
        
        # Basic status info
        status_data = [
            {"Service": "Available", "Status": str(status_info.get('daytona_available', False))},
            {"Service": "Sandbox Active", "Status": str(status_info.get('sandbox_active', False))}
        ]
        ui_manager.print_table(status_data)
        
        # Sandbox details
        if status_info.get('current_sandbox'):
            ui_manager.print_subheader("Sandbox Details")
            sandbox_info = status_info['current_sandbox']
            ui_manager.print_dict_as_table({
                "ID": sandbox_info.get('id', 'unknown'),
                "Status": sandbox_info.get('status', 'unknown'),
                "Created At": sandbox_info.get('created_at', 'unknown'),
                "API Mode": str(sandbox_info.get('api_mode', False))
            })
        
        # Configuration
        ui_manager.print_subheader("Configuration")
        config_info = status_info.get('config', {})
        ui_manager.print_dict_as_table({
            "CPU Limit": f"{config_info.get('cpu_limit', 'N/A')} cores",
            "Memory Limit": f"{config_info.get('memory_limit_mb', 'N/A')} MB",
            "Execution Timeout": f"{config_info.get('execution_timeout', 'N/A')} seconds",
            "Security Validation": str(config_info.get('enable_ast_validation', True))
        })
        
        # Registry info
        ui_manager.print_subheader("Registry Information")
        registry_info = status_info.get('sandbox_registry', {})
        ui_manager.print_dict_as_table({
            "Active Sandboxes": registry_info.get('active_sandboxes', 0),
            "Total Sandboxes": registry_info.get('total_sandboxes', 0)
        })
        
    except Exception as e:
        logger.error(f"Failed to get sandbox status: {e}")
        ui_manager.print_error(f"Failed to get sandbox status: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await cli_context.cleanup()


@sandbox.command(name="execute")
@click.argument("code", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Execute code from file")
@click.option("--timeout", "-t", type=int, default=None, help="Execution timeout in seconds")
@click.option("--framework", type=click.Choice(["numpyro", "pyro", "tfp", "stan"]), 
              default="numpyro", help="PPL framework for execution")
@click.option("--entry-point", "-e", default="main", help="Entry point function name")
@click.option("--stream", "-s", is_flag=True, help="Stream output during execution")
@click.option("--cpu-limit", type=int, help="CPU limit for sandbox")
@click.option("--memory-limit", type=int, help="Memory limit in MB for sandbox")
@click.option("--no-validation", is_flag=True, help="Disable code security validation")
@click.pass_context
@async_command
async def sandbox_execute(ctx, code: str, file: str, timeout: int, framework: str, entry_point: str, 
                          stream: bool, cpu_limit: int, memory_limit: int, no_validation: bool):
    """Execute code in Daytona sandbox"""
    verbose = ctx.obj.get("VERBOSE", False)
    
    # Initialize UI manager
    ui_manager = UIManager(verbose=verbose)
    
    # Read code from file if provided
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            ui_manager.print_error(f"Error reading file: {e}")
            return
    
    if not code:
        ui_manager.print_error("Please provide code to execute")
        return

    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    try:
        await cli_context.initialize()
        
        if not cli_context.daytona_service or not cli_context.ppl_executor:
            ui_manager.print_error("Daytona service not initialized")
            return
            
        # Check if Daytona is available
        if not cli_context.daytona_service.is_available():
            ui_manager.print_warning("Daytona service not available. Using local execution fallback.")
        
        # Update sandbox configuration if provided
        if cpu_limit or memory_limit or no_validation or timeout:
            # Create new sandbox config with updated values
            current_config = cli_context.daytona_service.config
            new_config = SandboxConfig(
                cpu_limit=cpu_limit or current_config.cpu_limit,
                memory_limit_mb=memory_limit or current_config.memory_limit_mb,
                execution_timeout=timeout or current_config.execution_timeout,
                enable_ast_validation=not no_validation if no_validation else current_config.enable_ast_validation,
                python_version=current_config.python_version,
                enable_networking=current_config.enable_networking,
                allowed_imports=current_config.allowed_imports,
                api_call_timeout=current_config.api_call_timeout,
                sandbox_creation_timeout=current_config.sandbox_creation_timeout,
                code_execution_timeout=current_config.code_execution_timeout,
                cleanup_timeout=current_config.cleanup_timeout
            )
            
            # Update the Daytona service config
            cli_context.daytona_service.config = new_config
            cli_context.ppl_executor.ppl_config.max_execution_time = timeout or current_config.execution_timeout
            if cpu_limit:
                cli_context.ppl_executor.ppl_config.cpu_limit = float(cpu_limit)
            if memory_limit:
                cli_context.ppl_executor.ppl_config.memory_limit_mb = memory_limit
            
            if verbose:
                ui_manager.print_info("Updated sandbox configuration")
        
        # Create PPL program
        try:
            framework_enum = PPLFramework[framework.upper()]
        except KeyError:
            ui_manager.print_error(f"Invalid framework: {framework}")
            return
            
        program = PPLProgram(
            code=code,
            framework=framework_enum,
            entry_point=entry_point
        )
        
        if verbose:
            ui_manager.print_info(f"Executing code in Daytona sandbox with {framework} framework...")
            ui_manager.print_info(f"Entry point: {entry_point}")
            if timeout:
                ui_manager.print_info(f"Timeout: {timeout} seconds")
        
        # Execute program with streaming if requested
        if stream:
            ui_manager.print_info("Executing with streaming output...")
            # For streaming, we'll show progress indicators and partial output
            # This is a simplified implementation - in a real system, you'd have
            # actual streaming from the sandbox
            ui_manager.print_info("Execution started...")
            
            # In a real implementation, this would be replaced with actual streaming
            # For now, we'll simulate streaming by showing a progress indicator
            if verbose:
                ui_manager.print_info("Streaming output enabled")
                
        # Execute with progress indicator
        task_id = ui_manager.start_progress("Executing code...")
        try:
            ui_manager.update_progress(task_id, 50, "Running...")
            result = await cli_context.ppl_executor.execute_ppl_program(program)
            ui_manager.update_progress(task_id, 100, "Execution complete!")
        finally:
            ui_manager.stop_progress()
        
        # Display results using rich formatting
        ui_manager.print_execution_result(result)
        
    except Exception as e:
        logger.error(f"Failed to execute code: {e}")
        ui_manager.print_error(f"Failed to execute code: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await cli_context.cleanup()


@sandbox.command(name="monitor")
@click.pass_context
@async_command
async def sandbox_monitor(ctx):
    """Monitor sandbox resource usage"""
    verbose = ctx.obj.get("VERBOSE", False)
    
    # Initialize UI manager
    ui_manager = UIManager(verbose=verbose)
    
    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    try:
        await cli_context.initialize()
        
        if not cli_context.daytona_service:
            ui_manager.print_error("Daytona service not initialized")
            return
            
        # Get service status which includes resource information
        status_info = cli_context.daytona_service.get_status()
        
        # Display monitoring information using rich formatting
        ui_manager.print_header("Daytona Sandbox Monitoring")
        
        if status_info.get('current_sandbox'):
            sandbox_info = status_info['current_sandbox']
            ui_manager.print_dict_as_table({
                "Sandbox ID": sandbox_info.get('id', 'unknown'),
                "Status": sandbox_info.get('status', 'unknown')
            })
            
            # Get resource usage (placeholder for now)
            resource_usage = cli_context.daytona_service._get_resource_usage()
            ui_manager.print_subheader("Resource Usage")
            ui_manager.print_dict_as_table({
                "CPU Usage": f"{resource_usage.get('cpu_usage_percent', 0.0):.2f}%",
                "Memory Usage": f"{resource_usage.get('memory_usage_mb', 0.0):.2f} MB",
                "Execution Time": f"{resource_usage.get('execution_time_seconds', 0.0):.2f} seconds"
            })
        else:
            ui_manager.print_warning("No active sandbox to monitor")
        
    except Exception as e:
        logger.error(f"Failed to monitor sandbox: {e}")
        ui_manager.print_error(f"Failed to monitor sandbox: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await cli_context.cleanup()


@config.command()
@click.option("--daytona-api-key", help="Set Daytona API key")
@click.option("--daytona-api-url", help="Set Daytona API URL")
@click.option("--cpu-limit", type=int, help="Set default CPU limit for sandboxes")
@click.option("--memory-limit", type=int, help="Set default memory limit for sandboxes (MB)")
@click.option("--execution-timeout", type=int, help="Set default execution timeout (seconds)")
@click.option("--show", is_flag=True, help="Show current Daytona configuration")
def daytona(daytona_api_key, daytona_api_url, cpu_limit, memory_limit, execution_timeout, show):
    """Manage Daytona configuration settings"""
    ui_manager = UIManager()
    config_file = os.path.expanduser("~/.msa_config")
    
    # Load existing config
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
        except Exception as e:
            ui_manager.print_warning(f"Could not load existing config: {e}")
    
    if show:
        # Display current configuration using rich formatting
        ui_manager.print_header("Daytona Configuration")
        ui_manager.print_dict_as_table({
            "API Key": config.get('DAYTONA_API_KEY', 'Not set'),
            "API URL": config.get('DAYTONA_API_URL', 'Not set'),
            "CPU Limit": config.get('DAYTONA_CPU_LIMIT', 'Default'),
            "Memory Limit": config.get('DAYTONA_MEMORY_LIMIT', 'Default'),
            "Execution Timeout": config.get('DAYTONA_EXECUTION_TIMEOUT', 'Default')
        })
        return
    
    # Update configuration
    updated = False
    if daytona_api_key:
        config["DAYTONA_API_KEY"] = daytona_api_key
        updated = True
        ui_manager.print_success("Daytona API key updated")
        
    if daytona_api_url:
        config["DAYTONA_API_URL"] = daytona_api_url
        updated = True
        ui_manager.print_success("Daytona API URL updated")
        
    if cpu_limit:
        config["DAYTONA_CPU_LIMIT"] = cpu_limit
        updated = True
        ui_manager.print_success(f"CPU limit updated to {cpu_limit} cores")
        
    if memory_limit:
        config["DAYTONA_MEMORY_LIMIT"] = memory_limit
        updated = True
        ui_manager.print_success(f"Memory limit updated to {memory_limit} MB")
        
    if execution_timeout:
        config["DAYTONA_EXECUTION_TIMEOUT"] = execution_timeout
        updated = True
        ui_manager.print_success(f"Execution timeout updated to {execution_timeout} seconds")
    
    # Save configuration
    if updated:
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            ui_manager.print_success(f"Configuration saved to {config_file}")
        except Exception as e:
            ui_manager.print_error(f"Error saving configuration: {e}")
    elif not show:
        ui_manager.print_warning("No configuration changes specified. Use --show to view current settings.")


# Add CoSci examples command group
cli.add_command(examples)


# Add CoSci benchmark command group
cli.add_command(benchmark)

# Add wizard command group
cli.add_command(wizard)

# Add new command groups (imported locally to avoid circular imports)
def _add_command_groups():
    try:
        from reasoning_kernel.cli.commands.chat import chat
        from reasoning_kernel.cli.commands.reason import reason
        from reasoning_kernel.cli.commands.analyze import analyze
        cli.add_command(chat)
        cli.add_command(reason)
        cli.add_command(analyze)
    except ImportError as e:
        logger.warning(f"Failed to import command modules: {e}")

# Add command groups
_add_command_groups()


def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        ui_manager = UIManager()
        ui_manager.print_warning("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"MSA CLI failed: {e}")
        ui_manager = UIManager()
        ui_manager.print_error(f"MSA CLI failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()