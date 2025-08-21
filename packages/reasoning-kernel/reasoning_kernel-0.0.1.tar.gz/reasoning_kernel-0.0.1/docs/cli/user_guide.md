# MSA Reasoning Kernel CLI User Guide

This guide provides comprehensive instructions for installing, configuring, and using the MSA Reasoning Kernel CLI. The CLI offers powerful reasoning capabilities through a simple command-line interface.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Basic Usage](#basic-usage)
4. [Core Commands](#core-commands)
5. [Advanced Features](#advanced-features)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.10+ (3.13+ not yet supported due to dependency compatibility)
- Azure OpenAI or Google AI Studio API access
- Redis (optional, for memory features)

### One-Line Installation (Recommended)

For macOS and Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Qredence/Reasoning-Kernel/main/setup/install.sh | bash
```

For Windows:

```cmd
curl -fsSL https://raw.githubusercontent.com/Qredence/Reasoning-Kernel/main/setup/install.bat -o install.bat
install.bat
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Qredence/Reasoning-Kernel.git
cd Reasoning-Kernel

# Install with Semantic Kernel support
uv venv && source .venv/bin/activate
uv pip install -e ".[azure,google]"

# Alternative: Install with pip
pip install -e ".[azure,google]"
```

### Verifying Installation

After installation, verify that the CLI is working:

```bash
reasoning-kernel --version
```

This should display the version information for the MSA Reasoning Kernel.

## Configuration

### Environment Variables

Set up your environment variables for the CLI to work properly:

```bash
# Azure OpenAI (Recommended)
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"
export AZURE_OPENAI_API_VERSION="2024-12-01-preview"

# Google AI (Alternative)
export GOOGLE_AI_API_KEY="your-key"

# Optional: Redis for memory
export REDIS_URL="redis://localhost:6379"
```

### Configuration Wizard

The CLI includes an interactive configuration wizard to help set up your environment:

```bash
reasoning-kernel wizard run
```

This will guide you through setting up Azure OpenAI, Daytona, Redis, and PostgreSQL connections.

## Basic Usage

### Interactive Mode

Start an interactive reasoning session:

```bash
reasoning-kernel --interactive
```

### Single Query Processing

Process a single reasoning query:

```bash
reasoning-kernel "Analyze supply chain disruption scenario"
```

### Using Specific Reasoning Modes

Use specific reasoning modes for different types of analysis:

```bash
# Knowledge-based reasoning only
reasoning-kernel --mode knowledge "Factory production failure analysis"

# Both knowledge and probabilistic reasoning
reasoning-kernel --mode both "Market analysis request"
```

### JSON Output

For automation and integration with other tools, use JSON output:

```bash
reasoning-kernel --output json "Market analysis request"
```

## Core Commands

### Chat Command

Start an interactive chat session with the reasoning engine:

```bash
reasoning-kernel chat [OPTIONS]
```

Options:
- `--verbose`, `-v`: Enable verbose logging
- `--session-id`, `-s`: Session ID for tracking
- `--model`, `-m`: Model to use for reasoning (default: gpt-4)

### Reason Command

Process a single reasoning query:

```bash
reasoning-kernel reason [OPTIONS] [QUERY]
```

Options:
- `QUERY`: The query to reason about (optional)
- `--verbose`, `-v`: Enable verbose logging
- `--mode`: Reasoning mode (knowledge or both) (default: both)
- `--output`, `-o`: Output format (text or json) (default: text)
- `--session-id`, `-s`: Session ID for tracking
- `--file`, `-f`: Read query from file
- `--model`, `-m`: Model to use for reasoning (default: gpt-4)

### Analyze Command

Analyze documents or code:

```bash
reasoning-kernel analyze [OPTIONS] [INPUT]
```

Options:
- `INPUT`: The input to analyze (optional)
- `--verbose`, `-v`: Enable verbose logging
- `--mode`: Analysis mode (knowledge or both) (default: both)
- `--output`, `-o`: Output format (text or json) (default: text)
- `--session-id`, `-s`: Session ID for tracking
- `--file`, `-f`: Read input from file
- `--type`, `-t`: Input type (document or code) (default: document)
- `--language`, `-l`: Programming language for code analysis

## Advanced Features

### Session Management

Manage reasoning sessions with the session command:

```bash
# List saved sessions
reasoning-kernel session list

# Create a new session
reasoning-kernel session create my-session "My analysis session"

# Load a saved session
reasoning-kernel session load my-session

# Delete a session
reasoning-kernel session delete my-session

# Export a session
reasoning-kernel session export my-session --output results.json --format json
```

### History Management

View and manage your reasoning history:

```bash
# List recent history entries
reasoning-kernel history list --limit 10

# Search history for specific queries
reasoning-kernel history search "climate change"

# Clear all history
reasoning-kernel history clear --force

# Export history
reasoning-kernel export history --output history.json --format json
```

### Batch Processing

Process multiple queries in batch mode:

```bash
reasoning-kernel batch process queries.json --output-dir ./results --session-id batch-session-001
```

The input file should be in JSON format:

```json
{
  "queries": [
    {
      "id": "query-1",
      "query": "Analyze the impact of climate change on global agriculture",
      "mode": "both"
    },
    {
      "id": "query-2",
      "query": "Explain the benefits of renewable energy sources",
      "mode": "knowledge"
    }
  ]
}
```

### Export Functionality

Export session data and history in various formats:

```bash
# Export a session to JSON
reasoning-kernel session export my-session --output results.json --format json

# Export a session to Markdown
reasoning-kernel session export my-session --output results.md --format md

# Export a session to PDF
reasoning-kernel session export my-session --output results.pdf --format pdf

# Export recent history
reasoning-kernel export history --output recent_history.md --format md --limit 5
```

## Examples

### Basic Reasoning

```bash
# Simple query
reasoning-kernel "What are the implications of artificial intelligence in healthcare?"

# With specific mode
reasoning-kernel --mode both "Analyze the risks and benefits of cloud computing for small businesses"

# With JSON output
reasoning-kernel --output json "Explain quantum computing concepts"
```

### Document Analysis

```bash
# Analyze a document file
reasoning-kernel analyze --file document.txt --type document

# Analyze code
reasoning-kernel analyze --file script.py --type code --language python
```

### Interactive Session

```bash
# Start interactive mode with a specific session
reasoning-kernel --interactive --session-id my-analysis-session
```

### Batch Processing

Create a batch queries file (queries.json):

```json
{
  "queries": [
    {
      "id": "business-1",
      "query": "Analyze market trends for renewable energy investments in 2025",
      "mode": "both"
    },
    {
      "id": "business-2",
      "query": "Evaluate the impact of remote work on urban real estate markets",
      "mode": "knowledge"
    }
  ]
}
```

Process the batch:

```bash
reasoning-kernel batch process queries.json --output-dir ./business_analysis --session-id business-q1-2025
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your Azure OpenAI or Google AI API keys are correctly set in environment variables
   - Verify that your endpoint and deployment names are correct

2. **Connection Issues**
   - Check your internet connection
   - Verify that your API endpoints are accessible
   - Ensure Redis is running if you're using memory features

3. **Model Not Found**
   - Check that your model deployment exists in Azure OpenAI
   - Verify the model name in your configuration

### Getting Help

For help with any command, use the `--help` flag:

```bash
reasoning-kernel --help
reasoning-kernel reason --help
reasoning-kernel analyze --help
```

### Verbose Logging

Enable verbose logging to get more detailed information about what the CLI is doing:

```bash
reasoning-kernel --verbose "Your query here"
reasoning-kernel -v reason "Your query here"
```

### Reporting Issues

If you encounter issues, please check the GitHub repository for known issues or to report a new one. Include the following information:

- CLI version (`reasoning-kernel --version`)
- Error message
- Steps to reproduce
- Environment information (OS, Python version, etc.)