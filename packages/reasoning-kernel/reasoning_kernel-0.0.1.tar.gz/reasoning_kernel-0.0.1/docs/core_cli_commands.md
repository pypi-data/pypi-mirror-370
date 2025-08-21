# Core CLI Commands for MSA Reasoning Kernel

This document provides an overview of the core CLI commands implemented for the MSA Reasoning Kernel.

## Commands Overview

The MSA Reasoning Kernel CLI provides several core commands for different reasoning tasks:

1. `chat` - Interactive reasoning session
2. `reason` - Single reasoning query processing
3. `analyze` - Document and code analysis
4. `session` - Session management
5. `history` - History management
6. `export` - Export functionality
7. `batch` - Batch processing
8. `config` - Configuration management
9. `wizard` - Interactive configuration wizard
10. `sandbox` - Secure code execution
11. `benchmark` - Performance benchmarking
12. `examples` - Example scenarios

## Command Details

### Chat Command

The `chat` command provides an interactive reasoning session where users can have a conversation with the MSA Reasoning Engine.

**Usage:**
```bash
msa chat [OPTIONS]
```

**Options:**
- `--verbose`, `-v`: Enable verbose logging
- `--session-id`, `-s`: Session ID for tracking
- `--model`, `-m`: Model to use for reasoning (default: gpt-4)

**Features:**
- Interactive loop for continuous reasoning
- Session tracking
- Rich UI with progress indicators
- Error handling and user feedback

### Reason Command

The `reason` command processes a single reasoning query using the MSA Reasoning Engine.

**Usage:**
```bash
msa reason [OPTIONS] [QUERY]
```

**Options:**
- `QUERY`: The query to reason about (optional)
- `--verbose`, `-v`: Enable verbose logging
- `--mode`: Reasoning mode (knowledge or both) (default: both)
- `--output`, `-o`: Output format (text or json) (default: text)
- `--session-id`, `-s`: Session ID for tracking
- `--file`, `-f`: Read query from file
- `--model`, `-m`: Model to use for reasoning (default: gpt-4)

**Features:**
- Single query processing
- File input support
- Multiple output formats
- Rich UI with progress indicators
- Error handling and user feedback

### Analyze Command

The `analyze` command provides document and code analysis capabilities.

**Usage:**
```bash
msa analyze [OPTIONS] [INPUT]
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

**Features:**
- Document and code analysis
- File input support
- Language-specific analysis
- Multiple output formats
- Rich UI with progress indicators
- Error handling and user feedback

## Integration with MSA Pipeline

All commands are integrated with the existing MSA pipeline components through the `MSACli` class and its `run_reasoning` method, which in turn calls the `MSAEngine.reason_about_scenario` method. This ensures that all commands leverage the full MSA reasoning capabilities including:

- Mode 1: LLM-powered knowledge retrieval
- Mode 2: Dynamic probabilistic model synthesis
- Confidence analysis
- Reasoning chain tracking

## Error Handling and User Feedback

All commands include comprehensive error handling and user feedback through the UIManager class, providing:

- Clear error messages
- Progress indicators
- Verbose logging options
- Rich UI formatting
- Graceful failure handling

## Testing

To test the commands, ensure you have:

1. Set up the required environment variables (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT)
2. Installed the MSA Reasoning Engine
3. Run the commands with various options and inputs

Example test commands:
```bash
# Test chat command
msa chat --verbose

# Test reason command
msa reason "What are the implications of climate change on global agriculture?" --output json

# Test analyze command with file input
msa analyze --file ./test_document.txt --type document