"""
MSA CoSci 2025 Examples CLI Commands

This module provides CLI commands for managing and running MSA CoSci 2025 examples.
"""
import subprocess
import sys
from pathlib import Path

import click
from reasoning_kernel.cli.ui import UIManager


# Default repository URL for MSA CoSci 2025 data
COSCI_REPO_URL = "https://github.com/lio-wong/msa-cogsci-2025-data.git"
COSCI_REPO_DIR = Path.home() / ".msa" / "cogsci-2025-data"


class CoSciExamplesManager:
    """Manager for MSA CoSci 2025 examples"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.ui = UIManager(verbose=verbose)
        self.repo_dir = COSCI_REPO_DIR
        
    def ensure_repo_exists(self) -> bool:
        """Ensure the CoSci repository exists, cloning it if necessary"""
        if not self.repo_dir.exists():
            self.ui.print_info(f"CoSci repository not found at {self.repo_dir}")
            return self.download_repository()
        return True
    
    def download_repository(self) -> bool:
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
    
    def list_examples(self) -> list:
        """List available CoSci examples"""
        if not self.ensure_repo_exists():
            return []
            
        examples_dir = self.repo_dir / "examples"
        if not examples_dir.exists():
            self.ui.print_warning(f"Examples directory not found at {examples_dir}")
            return []
            
        examples = []
        for item in examples_dir.iterdir():
            if item.is_file() and item.suffix in [".py", ".json", ".md"]:
                # Get file info
                stat = item.stat()
                examples.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.repo_dir)),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            elif item.is_dir():
                # For directories, list the main file
                main_file = item / "main.py"
                if main_file.exists():
                    stat = main_file.stat()
                    examples.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.repo_dir)),
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
                    
        return sorted(examples, key=lambda x: x["name"])
    
    def run_example(self, example_name: str, stream_output: bool = False) -> dict:
        """Run a specific CoSci example"""
        if not self.ensure_repo_exists():
            return {"success": False, "error": "Repository not available"}
            
        # Find the example file
        example_path = None
        examples_dir = self.repo_dir / "examples"
        
        # Check direct file match
        direct_file = examples_dir / example_name
        if direct_file.exists():
            example_path = direct_file
        else:
            # Check for directory with main.py
            dir_path = examples_dir / example_name
            if dir_path.exists() and dir_path.is_dir():
                main_file = dir_path / "main.py"
                if main_file.exists():
                    example_path = main_file
        
        if not example_path or not example_path.exists():
            return {"success": False, "error": f"Example '{example_name}' not found"}
            
        try:
            self.ui.print_info(f"Running example: {example_name}")
            
            # Run the example
            if example_path.suffix == ".py":
                if stream_output:
                    # Stream output in real-time
                    process = subprocess.Popen(
                        [sys.executable, str(example_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        cwd=self.repo_dir
                    )
                    
                    stdout_lines = []
                    stderr_lines = []
                    
                    # Stream output
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            self.ui.print_streaming_output(output.strip())
                            stdout_lines.append(output)
                    
                    # Capture any remaining stderr
                    stderr_output = process.stderr.read()
                    if stderr_output:
                        self.ui.print_streaming_output(stderr_output.strip(), is_error=True)
                        stderr_lines.append(stderr_output)
                        
                    return_code = process.poll()
                else:
                    # Run without streaming
                    result = subprocess.run(
                        [sys.executable, str(example_path)],
                        capture_output=True,
                        text=True,
                        cwd=self.repo_dir
                    )
                    return_code = result.returncode
                    stdout_lines = result.stdout.split('\n') if result.stdout else []
                    stderr_lines = result.stderr.split('\n') if result.stderr else []
                
                return {
                    "success": return_code == 0,
                    "example": example_name,
                    "return_code": return_code,
                    "stdout": '\n'.join(stdout_lines) if stdout_lines else "",
                    "stderr": '\n'.join(stderr_lines) if stderr_lines else "",
                    "path": str(example_path)
                }
            else:
                # For non-Python files, just show content
                with open(example_path, 'r') as f:
                    content = f.read()
                return {
                    "success": True,
                    "example": example_name,
                    "content": content,
                    "path": str(example_path)
                }
                
        except Exception as e:
            self.ui.print_error(f"Error running example: {e}")
            return {"success": False, "error": str(e)}


# CLI Commands
@click.group()
def examples():
    """MSA CoSci 2025 Examples Management"""
    pass


@examples.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def list(verbose: bool):
    """List available CoSci examples"""
    ui = UIManager(verbose=verbose)
    
    try:
        manager = CoSciExamplesManager(verbose=verbose)
        examples_list = manager.list_examples()
        
        if not examples_list:
            ui.print_warning("No examples found")
            return
            
        ui.print_header("Available CoSci Examples")
        example_data = []
        for example in examples_list:
            example_data.append({
                "Name": example["name"],
                "Path": example["path"],
                "Size": f"{example['size']} bytes"
            })
        
        ui.print_table(example_data)
        ui.print_info(f"Total examples: {len(examples_list)}")
        
    except Exception as e:
        ui.print_error(f"Error listing examples: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


@examples.command()
@click.argument("example_name")
@click.option("--stream", "-s", is_flag=True, help="Stream output during execution")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def run(example_name: str, stream: bool, verbose: bool):
    """Run a specific CoSci example"""
    ui = UIManager(verbose=verbose)
    
    try:
        manager = CoSciExamplesManager(verbose=verbose)
        result = manager.run_example(example_name, stream_output=stream)
        
        if result["success"]:
            ui.print_success(f"Example '{example_name}' completed successfully")
            
            if "stdout" in result and result["stdout"]:
                ui.print_subheader("Output")
                ui.console.print(result["stdout"])
                
            if "stderr" in result and result["stderr"]:
                ui.print_subheader("Errors")
                ui.console.print(result["stderr"], style="red")
                
            if "content" in result:
                ui.print_subheader("Content")
                ui.print_code(result["content"])
        else:
            ui.print_error(f"Example '{example_name}' failed")
            if "error" in result:
                ui.print_error(result["error"])
                
    except Exception as e:
        ui.print_error(f"Error running example: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


@examples.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def download(verbose: bool):
    """Download or update the CoSci repository"""
    ui = UIManager(verbose=verbose)
    
    try:
        manager = CoSciExamplesManager(verbose=verbose)
        if manager.download_repository():
            ui.print_success("CoSci repository is ready")
        else:
            ui.print_error("Failed to download/update repository")
            
    except Exception as e:
        ui.print_error(f"Error downloading repository: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    examples()