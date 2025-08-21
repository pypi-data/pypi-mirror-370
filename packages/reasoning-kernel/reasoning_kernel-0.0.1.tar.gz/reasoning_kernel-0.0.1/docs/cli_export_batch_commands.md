# MSA Reasoning Engine CLI - Export and Batch Processing Commands

This document describes the export and batch processing functionality available in the MSA Reasoning Engine CLI.

## Export Commands

The export functionality allows you to export session data and history in various formats including JSON, Markdown, and PDF.

### Session Export

Export a specific session to a file in your preferred format:

```bash
reasoning-kernel session export <session_id> --output <output_file> --format <json|md|pdf>
```

Example:
```bash
reasoning-kernel session export my-session-123 --output results.json --format json
reasoning-kernel session export my-session-123 --output results.md --format md
reasoning-kernel session export my-session-123 --output results.pdf --format pdf
```

### History Export

Export your entire history or a limited number of recent entries:

```bash
reasoning-kernel export history --output <output_file> --format <json|md|pdf> [--limit <number>]
```

Example:
```bash
reasoning-kernel export history --output history.json --format json
reasoning-kernel export history --output recent_history.md --format md --limit 10
```

## Batch Processing Commands

The batch processing functionality allows you to process multiple queries in a single command, which is especially useful for analyzing large datasets or running repetitive tasks.

### Batch Process

Process multiple queries from a file:

```bash
reasoning-kernel batch process <input_file> [--output-dir <directory>] [--session-id <session_id>]
```

The input file should be in JSON format:

Example JSON input file format:
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

Example usage:
```bash
reasoning-kernel batch process queries.json --output-dir ./results --session-id batch-session-001
```

## Supported Formats

### JSON
JSON format provides a complete, structured representation of the data that can be easily parsed by other applications.

### Markdown
Markdown format provides a human-readable document that can be easily converted to other formats or viewed directly in text editors and browsers.

### PDF
PDF format provides a portable document that preserves formatting across different platforms. Note that PDF export requires the WeasyPrint library to be installed:

```bash
pip install weasyprint
```

## Error Handling and Feedback

All commands provide detailed error messages and feedback through the CLI's rich UI components. Verbose mode can be enabled with the `-v` flag for additional debugging information.

## Additional Commands

### Session Management

Manage reasoning sessions:

```bash
# List sessions
reasoning-kernel session list

# Create a new session
reasoning-kernel session create my-session "My analysis session"

# Load a session
reasoning-kernel session load my-session

# Delete a session
reasoning-kernel session delete my-session
```

### History Management

Manage reasoning history:

```bash
# List recent history entries
reasoning-kernel history list --limit 10

# Search history
reasoning-kernel history search "climate change"

# Clear history
reasoning-kernel history clear --force
```

### Configuration

Manage configuration:

```bash
# Show current configuration
reasoning-kernel config show

# Set configuration values
reasoning-kernel config set log_level INFO

# Configure Daytona settings
reasoning-kernel config daytona --show
```

### Wizard

Run the interactive configuration wizard:

```bash
reasoning-kernel wizard run
```

### Sandbox

Execute code in secure sandbox:

```bash
# Check sandbox status
reasoning-kernel sandbox status

# Execute code
reasoning-kernel sandbox execute --code "print('Hello, World!')"

# Monitor sandbox resources
reasoning-kernel sandbox monitor
```

### Benchmark

Run performance benchmarks:

```bash
# List available benchmarks
reasoning-kernel benchmark list

# Run a benchmark
reasoning-kernel benchmark run reasoning-complexity
```

### Examples

Run example scenarios:

```bash
# List available examples
reasoning-kernel examples list

# Run an example
reasoning-kernel examples run basic-reasoning

# Download examples repository
reasoning-kernel examples download
```

## Examples

### Export a session to all formats:
```bash
reasoning-kernel session export my-session-123 --output results.json --format json
reasoning-kernel session export my-session-123 --output results.md --format md
reasoning-kernel session export my-session-123 --output results.pdf --format pdf
```

### Process a batch of queries:
```bash
reasoning-kernel batch process examples/batch_queries.json --output-dir ./batch_results --session-id batch-run-001
```

### Export recent history:
```bash
reasoning-kernel export history --output recent_history.md --format md --limit 5