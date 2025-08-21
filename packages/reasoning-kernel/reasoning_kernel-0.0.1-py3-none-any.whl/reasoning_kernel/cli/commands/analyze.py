"""
Analyze command for MSA Reasoning Engine CLI
Provides document and code analysis capabilities
"""
import asyncio

import click
from reasoning_kernel.cli.core import MSACliContext, MSACli
from reasoning_kernel.cli.ui import UIManager


@click.command()
@click.argument("input", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--mode", "-m", type=click.Choice(["knowledge", "both"]), default="both", help="Analysis mode")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read input from file")
@click.option("--type", "-t", type=click.Choice(["document", "code"]), default="document", help="Input type")
@click.option("--language", "-l", help="Programming language for code analysis")
@click.pass_context
def analyze(ctx, input: str, verbose: bool, mode: str, output: str, session_id: str, file: str, type: str, language: str):
    """Analyze documents or code using the MSA Reasoning Engine"""
    # Initialize UI manager
    ui_manager = UIManager(verbose=verbose)
    
    # Read input from file if provided
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                input = f.read().strip()
        except Exception as e:
            ui_manager.print_error(f"Error reading file: {e}")
            return
    
    if not input:
        ui_manager.print_error("Please provide input to analyze")
        return

    # Run the analysis process
    asyncio.run(_run_analysis(input, verbose, mode, output, session_id, type, language))


async def _run_analysis(input: str, verbose: bool, mode: str, output: str, session_id: str, type: str, language: str):
    """Run the analysis process"""
    ui_manager = UIManager(verbose=verbose)
    
    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    msa_cli = None
    
    try:
        await cli_context.initialize()
        msa_cli = MSACli(cli_context)
        
        ui_manager.print_info(f"Analyzing {type}: {input[:100]}{'...' if len(input) > 100 else ''}")
        if language:
            ui_manager.print_info(f"Language: {language}")
        
        # Run analysis with progress indicator
        task_id = ui_manager.start_progress(f"Analyzing {type}...")
        try:
            # Update progress during analysis
            ui_manager.update_progress(task_id, 50, "Processing...")
            
            # Run reasoning
            result = await msa_cli.run_reasoning(
                scenario=input,
                mode=mode,
                output_format=output,
                session_id=session_id,
            )
            
            # Complete progress
            ui_manager.update_progress(task_id, 100, "Analysis complete!")
        finally:
            ui_manager.stop_progress()
        
        # Format and display output
        formatted_output = msa_cli.format_output(result, output)
        if output == "json":
            click.echo(formatted_output)
        else:
            ui_manager.print_analysis_result(result, output)
            
    except Exception as e:
        ui_manager.print_error(f"Analysis failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if cli_context:
            await cli_context.cleanup()