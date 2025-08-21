"""
Reason command for MSA Reasoning Engine CLI
Provides single reasoning query processing
"""
import asyncio

import click
from reasoning_kernel.cli.core import MSACliContext, MSACli
from reasoning_kernel.cli.ui import UIManager


@click.command()
@click.argument("query", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--mode", type=click.Choice(["knowledge", "both"]), default="both", help="Reasoning mode")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read query from file")
@click.option("--model", "-m", default="gpt-4", help="Model to use for reasoning")
@click.pass_context
def reason(ctx, query: str, verbose: bool, mode: str, output: str, session_id: str, file: str, model: str):
    """Process a single reasoning query using the MSA Reasoning Engine"""
    # Initialize UI manager
    ui_manager = UIManager(verbose=verbose)
    
    # Read query from file if provided
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                query = f.read().strip()
        except Exception as e:
            ui_manager.print_error(f"Error reading file: {e}")
            return
    
    if not query:
        ui_manager.print_error("Please provide a query to reason about")
        return

    # Run the reasoning process
    asyncio.run(_run_reasoning(query, verbose, mode, output, session_id, model))


async def _run_reasoning(query: str, verbose: bool, mode: str, output: str, session_id: str, model: str):
    """Run the reasoning process"""
    ui_manager = UIManager(verbose=verbose)
    
    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    msa_cli = None
    
    try:
        await cli_context.initialize()
        msa_cli = MSACli(cli_context)
        
        ui_manager.print_info(f"Processing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        # Run reasoning with progress indicator
        task_id = ui_manager.start_progress("Reasoning about query...")
        try:
            # Update progress during analysis
            ui_manager.update_progress(task_id, 50, "Processing...")
            
            # Run reasoning
            result = await msa_cli.run_reasoning(
                scenario=query,
                mode=mode,
                output_format=output,
                session_id=session_id,
            )
            
            # Complete progress
            ui_manager.update_progress(task_id, 100, "Reasoning complete!")
        finally:
            ui_manager.stop_progress()
        
        # Format and display output
        formatted_output = msa_cli.format_output(result, output)
        if output == "json":
            click.echo(formatted_output)
        else:
            ui_manager.print_analysis_result(result, output)
            
    except Exception as e:
        ui_manager.print_error(f"Reasoning failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if cli_context:
            await cli_context.cleanup()