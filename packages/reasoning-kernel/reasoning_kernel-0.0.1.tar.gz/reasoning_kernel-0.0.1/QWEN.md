# Reasoning Kernel - Qwen Context

## Project Overview

The **Reasoning Kernel** is an advanced AI reasoning system built on Microsoft Semantic Kernel, implementing the **Model Synthesis Architecture (MSA)**. It's designed for open-world cognitive reasoning with a plugin-based modular architecture and enterprise-grade orchestration.

### Core Technologies

- **Microsoft Semantic Kernel** - Core orchestration framework
- **Python 3.10+** - Primary language
- **FastAPI** - Web framework for REST APIs
- **NumPyro** - Probabilistic programming with JAX
- **Redis** - Memory storage and caching
- **Azure OpenAI / Google Gemini** - AI model providers

### Key Features

- **🧠 SK-Native Architecture**: Built entirely on Microsoft Semantic Kernel patterns
- **🔌 Plugin Ecosystem**: Modular reasoning capabilities as SK plugins
- **📋 Intelligent Planning**: SK planners for complex reasoning orchestration
- **💾 Multi-Tier Memory**: Redis/PostgreSQL integration via SK memory abstractions
- **🎯 MSA Pipeline**: Five-stage reasoning process as plugin chains
- **🌐 Multi-Model Support**: Azure OpenAI, Google Gemini, and local models
- **⚡ Production Ready**: FastAPI, streaming, and enterprise deployment

## Architecture

### Model Synthesis Architecture (MSA)

The system implements a five-stage reasoning pipeline:

1. **Parse**: Transform natural language into structured representations
2. **Retrieve**: Gather relevant background knowledge from memory
3. **Graph**: Build causal dependency graphs
4. **Synthesize**: Generate probabilistic programs (NumPyro)
5. **Infer**: Execute models and compute results

### Semantic Kernel Native Design

All reasoning capabilities are implemented as Semantic Kernel agents and plugins:

- **Agent Layer**: SK Chat Completion Agents for orchestration
- **Plugin Layer**: Business logic and reasoning implementations
- **Memory Layer**: Redis-based short/long-term memory with embeddings
- **Execution Layer**: Secure sandbox for code execution
- **API Layer**: External interfaces and endpoints

## Project Structure

```
reasoning_kernel/
├── adapters/           # Interface adapters
├── agents/             # Semantic Kernel agents
├── api/                # REST API endpoints
├── cli/                # Command-line interface
├── core/               # Core configuration and utilities
├── integrations/       # Third-party service integrations
├── middleware/         # FastAPI middleware
├── models/             # Data models and schemas
├── msa/                # MSA-specific implementations
├── plugins/            # Semantic Kernel plugins
├── schemas/            # Pydantic data schemas
├── services/           # Business services
├── static/             # Static web assets
├── utils/              # Utility functions
└── visualization/      # Visualization tools
```

## Installation & Setup

### Prerequisites

- Python 3.10+ (3.13+ not yet supported)
- Azure OpenAI or Google AI Studio API access
- Redis (optional, for memory features)

### Installation

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

### Configuration

Set environment variables:

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

## Usage

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

## Development

### Running the Server

```bash
# Install in development mode
pip install -e .

# Start with hot reload
uvicorn reasoning_kernel.main:app --host 0.0.0.0 --port 5000 --reload
```

### Code Quality

```bash
# Format code
black reasoning_kernel/
isort reasoning_kernel/

# Type checking
mypy reasoning_kernel/
```

## Testing

Tests are designed to be deterministic and don't require external services:

```bash
# Run all pipeline tests
pytest tests/test_reasoning_unified_pipeline.py -v
```

## Documentation

Key documentation files:

- Core concepts: `docs/core_concepts.md`
- Full system overview: `docs/full-system.md`
- MSA framework: `docs/architecture/msa-framework.md`
- Semantic Kernel architecture: `docs/architecture/semantic-kernel-architecture.md`

## Key Components

### Main Entry Points

- `reasoning_kernel/main.py` - FastAPI application and server
- `reasoning_kernel/cli.py` - Command-line interface
- `reasoning_kernel/reasoning_kernel.py` - Main orchestrator

### Core Configuration

- `reasoning_kernel/core/config.py` - Application settings
- Environment variables control all configuration

### Plugins

- `ParsingPlugin` - Transform natural language to structured data
- `KnowledgePlugin` - Retrieve and manage background knowledge
- `SynthesisPlugin` - Generate probabilistic programs
- `InferencePlugin` - Execute models and compute results

## Contributing

The project welcomes contributions. Key areas for contribution:

1. New plugins for different reasoning capabilities
2. Additional AI model integrations
3. Performance improvements
4. Documentation enhancements
5. Bug fixes and test coverage

## License

This project is licensed under the Apache-2.0 License.
