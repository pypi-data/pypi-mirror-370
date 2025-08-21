"""
Chat command for MSA Reasoning Engine CLI
Provides an interactive reasoning session with enhanced features
"""
import asyncio

import click
from reasoning_kernel.cli.core import MSACliContext, MSACli
from reasoning_kernel.cli.ui import UIManager
from reasoning_kernel.cli.session import session_manager


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--model", "-m", default="gpt-4", help="Model to use for reasoning")
@click.pass_context
def chat(ctx, verbose: bool, session_id: str, model: str):
    """Start an interactive chat session for reasoning"""
    # Run the interactive chat loop
    asyncio.run(_run_chat_mode(verbose, session_id, model))


async def _run_chat_mode(verbose: bool, session_id: str, model: str):
    """Run the interactive chat mode loop"""
    ui_manager = UIManager(verbose=verbose)
    ui_manager.print_success("Welcome to the MSA Reasoning Engine Chat Mode")
    ui_manager.print_info("Enter scenarios to analyze complex decision-making situations")
    ui_manager.print_info("Type 'help' for commands, 'quit' to exit")
    ui_manager.console.print("-" * 50, style="dim")
    
    # Initialize CLI context
    cli_context = MSACliContext(verbose=verbose)
    msa_cli = None
    
    try:
        await cli_context.initialize()
        msa_cli = MSACli(cli_context)
        
        session_count = 0
        
        while True:
            try:
                prompt = f"\n[Chat Session {session_count + 1}] 📝 Enter your query (or command): "
                user_input = input(prompt).strip()
                
                if user_input.lower() in ["quit", "exit"]:
                    ui_manager.print_success("Goodbye!")
                    break
                elif user_input.lower() == "help":
                    ui_manager.print_info("Available commands:")
                    ui_manager.console.print("  quit/exit - Exit the chat mode")
                    ui_manager.console.print("  help      - Show this help message")
                    ui_manager.console.print("  <query>   - Analyze a query")
                    ui_manager.console.print("  history   - Show session history")
                    continue
                elif user_input.lower() == "history":
                    # Show session history
                    try:
                        history_data = session_manager.get_history(limit=10)
                        if history_data and history_data.get("queries"):
                            ui_manager.print_header("Recent History")
                            queries = history_data.get("queries", [])
                            for i, query_entry in enumerate(queries, 1):
                                ui_manager.console.print(f"{i}. {query_entry.get('query', 'Unknown')}")
                                ui_manager.console.print(f"   Timestamp: {query_entry.get('timestamp', 'Unknown')}")
                                ui_manager.console.print("")
                        else:
                            ui_manager.print_info("No history found")
                    except Exception as e:
                        ui_manager.print_error(f"Failed to retrieve history: {e}")
                    continue
                elif not user_input:
                    ui_manager.print_warning("Please enter a query to analyze or a command")
                    continue
                
                # Process the query
                session_count += 1
                ui_manager.print_info("Processing your query...")
                
                # Run reasoning with progress indicator
                task_id = ui_manager.start_progress("Analyzing query...")
                try:
                    # Update progress during analysis
                    ui_manager.update_progress(task_id, 50, "Processing...")
                    
                    # Run reasoning
                    result = await msa_cli.run_reasoning(
                        scenario=user_input,
                        mode="both",
                        session_id=session_id or f"chat-{session_count}",
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
                ui_manager.print_error(f"An error occurred while processing your query: {e}")
                
    except Exception as e:
        ui_manager.print_error(f"Failed to start chat mode: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        if cli_context:
            await cli_context.cleanup()