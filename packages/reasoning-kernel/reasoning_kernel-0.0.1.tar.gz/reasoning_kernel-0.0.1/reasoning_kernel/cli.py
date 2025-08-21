"""
CLI entry point for MSA Reasoning Engine
This module provides the main entry point for the CLI, delegating to the new Click-based framework.
"""
from reasoning_kernel.cli.core import main as core_main

def main():
    """Main entry point for the CLI"""
    core_main()

if __name__ == "__main__":
    main()
