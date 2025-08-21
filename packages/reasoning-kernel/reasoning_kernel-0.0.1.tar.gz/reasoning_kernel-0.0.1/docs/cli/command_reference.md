# MSA Reasoning Kernel CLI Command Reference

This document provides detailed information about all available commands in the MSA Reasoning Kernel CLI, including their options, usage examples, and detailed descriptions.

## Table of Contents

1. [Core Commands](#core-commands)
   - [chat](#chat)
   - [reason](#reason)
   - [analyze](#analyze)
2. [Session Management](#session-management)
   - [session list](#session-list)
   - [session create](#session-create)
   - [session load](#session-load)
   - [session delete](#session-delete)
   - [session export](#session-export)
3. [History Management](#history-management)
   - [history list](#history-list)
   - [history search](#history-search)
   - [history clear](#history-clear)
4. [Export Commands](#export-commands)
   - [export history](#export-history)
5. [Batch Processing](#batch-processing)
   - [batch process](#batch-process)
6. [Configuration](#configuration)
   - [config show](#config-show)
   - [config set](#config-set)
   - [config daytona](#config-daytona)
7. [Wizard](#wizard)
   - [wizard run](#wizard-run)
8. [Sandbox](#sandbox)
   - [sandbox status](#sandbox-status)
   - [sandbox execute](#sandbox-execute)
   - [sandbox monitor](#sandbox-monitor)
9. [Benchmark](#benchmark)
   - [benchmark list](#benchmark-list)
   - [benchmark run](#benchmark-run)
   - [benchmark compare](#benchmark-compare)
10. [Examples](#examples-1)
    - [examples list](#examples-list)
    - [examples run](#examples-run)
    - [examples download](#examples-download)

## Core Commands

### chat

Start an interactive chat session with the reasoning engine.

```bash
reasoning-kernel chat [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging
- `--session-id`, `-s`: Session ID for tracking

**Description:**
The chat command provides an interactive reasoning session where users can have a conversation with the MSA Reasoning Engine. This is useful for extended reasoning sessions where you want to explore different aspects of a problem or have a dialogue with the system.

**Examples:**

```bash
# Start a basic chat session
reasoning-kernel chat

# Start a chat session with verbose logging
reasoning-kernel chat --verbose

# Start a chat session with a specific session ID
reasoning-kernel chat --session-id my-analysis-session
```

### reason

Process a single reasoning query using the MSA Reasoning Engine.

```bash
reasoning-kernel reason [OPTIONS] [QUERY]
```

**Options:**

- `QUERY`: The query to reason about (optional)
- `--verbose`, `-v`: Enable verbose logging
- `--mode`: Reasoning mode (knowledge or both) (default: both)
- `--output`, `-o`: Output format (text or json) (default: text)
- `--session-id`, `-s`: Session ID for tracking
- `--file`, `-f`: Read query from file
- `--model`, `-m`: Model to use for reasoning (default: gpt-4)

**Description:**
The reason command processes a single reasoning query using the MSA Reasoning Engine. It supports both knowledge-based reasoning and probabilistic model synthesis, depending on the mode selected.

**Examples:**

```bash
# Process a simple query
reasoning-kernel reason "What are the implications of climate change on global agriculture?"

# Process a query with knowledge mode only
reasoning-kernel reason --mode knowledge "Explain the benefits of renewable energy sources"

# Process a query with JSON output
reasoning-kernel reason --output json "Evaluate the risks of artificial intelligence in healthcare"

# Process a query from a file
reasoning-kernel reason --file query.txt

# Process a query with a specific session ID
reasoning-kernel reason --session-id my-session "Analyze market trends"
```

### analyze

Analyze documents or code using the MSA Reasoning Engine.

```bash
reasoning-kernel analyze [OPTIONS] [INPUT]
```

**Options:**

- `INPUT`: The input to analyze (optional)
- `--verbose`, `-v`: Enable verbose logging
- `--mode`: Analysis mode (knowledge or both) (default: both)
- `--output`, `-o`: Output format (text or json) (default: text)
- `--session-id`, `-s`: Session ID for tracking
- `--file`, `-f`: Read input from file
- `--type`, `-t`: Input type (document or code) (default: document)
- `--language`, `-l`: Programming language for code analysis

**Description:**
The analyze command provides document and code analysis capabilities. It can analyze text documents for insights, summarize content, or analyze code for potential issues, best practices, and improvements.

**Examples:**

```bash
# Analyze a document
reasoning-kernel analyze "This is the content of my document to analyze"

# Analyze a document from a file
reasoning-kernel analyze --file document.txt --type document

# Analyze Python code
reasoning-kernel analyze --file script.py --type code --language python

# Analyze code with JSON output
reasoning-kernel analyze --file app.js --type code --language javascript --output json
```

## Session Management

### session list

List all saved sessions.

```bash
reasoning-kernel session list [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Lists all saved reasoning sessions, showing their IDs, descriptions, and creation timestamps.

**Examples:**

```bash
# List all sessions
reasoning-kernel session list

# List sessions with verbose information
reasoning-kernel session list --verbose
```

### session create

Create a new session.

```bash
reasoning-kernel session create [OPTIONS] SESSION_ID [DESCRIPTION]
```

**Options:**

- `SESSION_ID`: Unique identifier for the session
- `DESCRIPTION`: Optional description of the session
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Creates a new reasoning session with the specified ID and optional description. Sessions are used to group related reasoning queries and maintain context.

**Examples:**

```bash
# Create a new session
reasoning-kernel session create my-analysis-session

# Create a new session with a description
reasoning-kernel session create my-analysis-session "Q1 2025 business analysis"
```

### session load

Load a saved session.

```bash
reasoning-kernel session load [OPTIONS] SESSION_ID
```

**Options:**

- `SESSION_ID`: ID of the session to load
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Loads a previously saved session, making it active for subsequent reasoning operations.

**Examples:**

```bash
# Load a session
reasoning-kernel session load my-analysis-session
```

### session delete

Delete a saved session.

```bash
reasoning-kernel session delete [OPTIONS] SESSION_ID
```

**Options:**

- `SESSION_ID`: ID of the session to delete
- `--verbose`, `-v`: Enable verbose logging
- `--force`: Force deletion without confirmation

**Description:**
Deletes a saved session and all associated data. Use with caution as this operation cannot be undone.

**Examples:**

```bash
# Delete a session
reasoning-kernel session delete my-old-session

# Force delete a session without confirmation
reasoning-kernel session delete --force my-old-session
```

### session export

Export a session to a specified format.

```bash
reasoning-kernel session export [OPTIONS] SESSION_ID --output OUTPUT --format FORMAT
```

**Options:**

- `SESSION_ID`: ID of the session to export
- `--output`: Output file path
- `--format`: Output format (json, md, or pdf)
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Exports a session's data to a file in the specified format. This is useful for sharing results or archiving sessions.

**Examples:**

```bash
# Export session to JSON
reasoning-kernel session export my-session --output results.json --format json

# Export session to Markdown
reasoning-kernel session export my-session --output results.md --format md

# Export session to PDF
reasoning-kernel session export my-session --output results.pdf --format pdf
```

## History Management

### history list

List recent history entries.

```bash
reasoning-kernel history list [OPTIONS]
```

**Options:**

- `--limit`: Maximum number of entries to show (default: 10)
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Lists recent reasoning queries and their results from your history. This helps you review past analyses and find previous work.

**Examples:**

```bash
# List recent history entries
reasoning-kernel history list

# List last 20 history entries
reasoning-kernel history list --limit 20
```

### history search

Search history for queries containing specific text.

```bash
reasoning-kernel history search [OPTIONS] QUERY_TEXT
```

**Options:**

- `QUERY_TEXT`: Text to search for in history
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Searches your history for queries that contain the specified text. This is useful for finding previous analyses on similar topics.

**Examples:**

```bash
# Search for history entries containing "climate change"
reasoning-kernel history search "climate change"

# Search for entries about "market analysis"
reasoning-kernel history search "market analysis"
```

### history clear

Clear all history.

```bash
reasoning-kernel history clear [OPTIONS]
```

**Options:**

- `--force`: Force clearing without confirmation
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Clears all entries from your reasoning history. Use with caution as this operation cannot be undone.

**Examples:**

```bash
# Clear history (requires confirmation)
reasoning-kernel history clear

# Force clear history without confirmation
reasoning-kernel history clear --force
```

## Export Commands

### export history

Export history to a specified format.

```bash
reasoning-kernel export history [OPTIONS] --output OUTPUT --format FORMAT
```

**Options:**

- `--output`: Output file path
- `--format`: Output format (json, md, or pdf)
- `--limit`: Maximum number of entries to export
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Exports your reasoning history to a file in the specified format. This is useful for creating reports or sharing your work with others.

**Examples:**

```bash
# Export entire history to JSON
reasoning-kernel export history --output history.json --format json

# Export recent 10 entries to Markdown
reasoning-kernel export history --output recent_history.md --format md --limit 10

# Export recent 5 entries to PDF
reasoning-kernel export history --output recent_history.pdf --format pdf --limit 5
```

## Batch Processing

### batch process

Process multiple queries in batch mode.

```bash
reasoning-kernel batch process [OPTIONS] INPUT_FILE
```

**Options:**

- `INPUT_FILE`: Path to the input file containing queries
- `--output-dir`: Directory to save results (default: current directory)
- `--session-id`: Session ID for tracking
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Processes multiple queries from a file in batch mode. This is especially useful for analyzing large datasets or running repetitive tasks. The input file can be in JSON format.

**Examples:**

```bash
# Process batch queries
reasoning-kernel batch process queries.json

# Process batch queries with output directory
reasoning-kernel batch process queries.json --output-dir ./results

# Process batch queries with session tracking
reasoning-kernel batch process queries.json --session-id batch-run-001
```

## Configuration

### config show

Show current configuration.

```bash
reasoning-kernel config show [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Displays the current configuration settings for the MSA Reasoning Kernel CLI.

**Examples:**

```bash
# Show current configuration
reasoning-kernel config show

# Show configuration with verbose details
reasoning-kernel config show --verbose
```

### config set

Set configuration values.

```bash
reasoning-kernel config set [OPTIONS] KEY VALUE
```

**Options:**

- `KEY`: Configuration key to set
- `VALUE`: Value to set for the key
- `--file`: Configuration file to modify
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Sets configuration values for the MSA Reasoning Kernel CLI. This allows you to modify settings without changing environment variables.

**Examples:**

```bash
# Set a configuration value
reasoning-kernel config set log_level INFO

# Set a configuration value in a specific file
reasoning-kernel config set --file ./config.json max_tokens 2000
```

### config daytona

Configure Daytona settings.

```bash
reasoning-kernel config daytona [OPTIONS]
```

**Options:**

- `--daytona-api-key`: Daytona API key
- `--daytona-api-url`: Daytona API URL
- `--cpu-limit`: CPU limit for sandbox execution
- `--memory-limit`: Memory limit for sandbox execution
- `--execution-timeout`: Execution timeout for sandbox
- `--show`: Show current Daytona configuration
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Configures Daytona sandbox settings for secure code execution.

**Examples:**

```bash
# Show current Daytona configuration
reasoning-kernel config daytona --show

# Set Daytona API key
reasoning-kernel config daytona --daytona-api-key your-api-key
```

## Wizard

### wizard run

Run the interactive configuration wizard.

```bash
reasoning-kernel wizard run [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Runs the interactive configuration wizard to help set up your environment, including Azure OpenAI, Daytona, Redis, and PostgreSQL connections.

**Examples:**

```bash
# Run the configuration wizard
reasoning-kernel wizard run

# Run the configuration wizard with verbose logging
reasoning-kernel wizard run --verbose
```

## Sandbox

### sandbox status

Check Daytona sandbox status.

```bash
reasoning-kernel sandbox status [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Checks the status of the Daytona sandbox environment for secure code execution.

**Examples:**

```bash
# Check sandbox status
reasoning-kernel sandbox status
```

### sandbox execute

Execute code in Daytona sandbox.

```bash
reasoning-kernel sandbox execute [OPTIONS]
```

**Options:**

- `--code`: Code to execute directly
- `--file`: File containing code to execute
- `--timeout`: Execution timeout in seconds
- `--framework`: Framework to use (python, nodejs, etc.)
- `--entry-point`: Entry point function name
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Executes code securely in the Daytona sandbox environment.

**Examples:**

```bash
# Execute code directly
reasoning-kernel sandbox execute --code "print('Hello, World!')"

# Execute code from a file
reasoning-kernel sandbox execute --file script.py

# Execute with timeout
reasoning-kernel sandbox execute --file script.py --timeout 30
```

### sandbox monitor

Monitor sandbox resource usage.

```bash
reasoning-kernel sandbox monitor [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Monitors resource usage of the Daytona sandbox environment.

**Examples:**

```bash
# Monitor sandbox resources
reasoning-kernel sandbox monitor
```

## Benchmark

### benchmark list

List available CoSci benchmarks.

```bash
reasoning-kernel benchmark list [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Lists available benchmarks from the MSA CoSci 2025 repository.

**Examples:**

```bash
# List available benchmarks
reasoning-kernel benchmark list
```

### benchmark run

Run a specific CoSci benchmark.

```bash
reasoning-kernel benchmark run [OPTIONS] BENCHMARK_NAME
```

**Options:**

- `BENCHMARK_NAME`: Name of the benchmark to run
- `--iterations`: Number of iterations to run (default: 1)
- `--output`: Output file for results
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Runs a specific benchmark from the MSA CoSci 2025 repository.

**Examples:**

```bash
# Run a benchmark
reasoning-kernel benchmark run reasoning-complexity

# Run a benchmark with multiple iterations
reasoning-kernel benchmark run reasoning-complexity --iterations 5
```

### benchmark compare

Run benchmark and compare with existing results.

```bash
reasoning-kernel benchmark compare [OPTIONS] BENCHMARK_NAME
```

**Options:**

- `BENCHMARK_NAME`: Name of the benchmark to run
- `--iterations`: Number of iterations to run (default: 1)
- `--output`: Output file for results
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Runs a benchmark and compares the results with existing benchmark data.

**Examples:**

```bash
# Compare benchmark results
reasoning-kernel benchmark compare reasoning-complexity
```

## Examples

### examples list

List available CoSci examples.

```bash
reasoning-kernel examples list [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Lists available examples from the MSA CoSci 2025 repository.

**Examples:**

```bash
# List available examples
reasoning-kernel examples list
```

### examples run

Run a specific CoSci example.

```bash
reasoning-kernel examples run [OPTIONS] EXAMPLE_NAME
```

**Options:**

- `EXAMPLE_NAME`: Name of the example to run
- `--stream`: Stream output in real-time
- `--verbose`, `-v`: Enable verbose logging

**Description:**
Runs a specific example from the MSA CoSci 2025 repository.

**Examples:**

```bash
# Run an example
reasoning-kernel examples run basic-reasoning

# Run an example with streaming output
reasoning-kernel examples run basic-reasoning --stream
```

### examples download

Download or update the CoSci repository.

```bash
reasoning-kernel examples download [OPTIONS]
```

**Options:**

- `--verbose`, `-v`: Enable verbose logging

**Description:**
Downloads or updates the MSA CoSci 2025 repository containing examples and benchmarks.

**Examples:**

```bash
# Download or update examples repository
reasoning-kernel examples download
