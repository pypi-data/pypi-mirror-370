# Reasoning Kernel Package Usage

## Installation

### Prerequisites

- Python 3.10+
- Azure OpenAI or Google AI Studio API access
- Redis (optional, for memory features)

### Installation Methods

#### One-Line Installation (Recommended)

For macOS and Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/Qredence/Reasoning-Kernel/main/setup/install.sh | bash
```

For Windows:
```cmd
curl -fsSL https://raw.githubusercontent.com/Qredence/Reasoning-Kernel/main/setup/install.bat -o install.bat
install.bat
```

#### Manual Installation

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

#### PyPI Installation (when available)

```bash
pip install reasoning-kernel[azure,google]
```

## Configuration

Set up your environment variables:

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

## Basic Usage

### Python SDK

```python
import asyncio
from reasoning_kernel.core.kernel_config import KernelManager
from reasoning_kernel.services.redis_service import create_redis_services
from reasoning_kernel.reasoning_kernel import ReasoningKernel, ReasoningConfig

async def main():
  # Initialize Semantic Kernel (uses Azure OpenAI env vars)
  km = KernelManager()
  await km.initialize()

  # Optional: Redis for memory (uses REDIS_URL or host/port)
  memory_service, _ = create_redis_services()

  # Initialize reasoning system
  rk = ReasoningKernel(kernel=km.kernel, redis_client=memory_service, config=ReasoningConfig())

  # Perform reasoning
  result = await rk.reason(
    "A factory machine has failed and production is stopped. "
    "Analyze the situation and suggest solutions."
  )

  print(result.success, result.overall_confidence)

asyncio.run(main())
```

### CLI Usage

```bash
# Basic reasoning
reasoning-kernel "Analyze supply chain disruption scenario"

# Use specific reasoning mode
reasoning-kernel --mode knowledge "Factory production failure analysis"

# Interactive mode
reasoning-kernel --interactive

# JSON output for automation
reasoning-kernel --output json "Market analysis request"
```

## Advanced Usage

### Using Different Reasoning Modes

The Reasoning Kernel supports different reasoning modes:

1. **Knowledge Mode**: Extracts knowledge from the scenario
2. **Both Mode**: Performs both knowledge extraction and probabilistic reasoning

```bash
# Knowledge mode only
reasoning-kernel --mode knowledge "Analyze market trends"

# Both modes (default)
reasoning-kernel --mode both "Analyze market trends"
```

### Interactive Mode

The interactive mode allows you to have a conversation with the reasoning engine:

```bash
reasoning-kernel --interactive
```

In interactive mode, you can enter scenarios to analyze complex decision-making situations. Type 'help' for commands and 'quit' to exit.

### Configuration Management

You can manage configuration through environment variables or configuration files. The system will automatically load configuration from a `.env` file in the project root if it exists.

### Memory Integration

The Reasoning Kernel can integrate with Redis for memory features. To enable this, ensure you have Redis running and set the `REDIS_URL` environment variable.

## API Reference

For detailed API documentation, please see:
- REST API reference: `docs/api/rest-api.md`
- Full API documentation: `docs/api/comprehensive-reference.mdx`

## Examples

See the examples directory for detailed usage examples:
- Gemini integration demo: `examples/gemini_integration_demo.py`
- MCP Redis example: `examples/mcp_redis_example.py`
- Redis world model integration: `examples/redis_world_model_integration_demo.py`
- MSA paper demo: `examples/msa_paper_demo.py`

## Troubleshooting

For common issues and troubleshooting tips, see:
- Common issues guide: `docs/troubleshooting/common-issues.mdx`
- Quick issues guide: `QUICK_ISSUES_GUIDE.md`

## Contributing

We welcome contributions! Please see our contributing guidelines in `CONTRIBUTING.md` and code of conduct in `CODE_OF_CONDUCT.md`.

## License

This project is licensed under the Apache-2.0 License. See `LICENSE` for details.