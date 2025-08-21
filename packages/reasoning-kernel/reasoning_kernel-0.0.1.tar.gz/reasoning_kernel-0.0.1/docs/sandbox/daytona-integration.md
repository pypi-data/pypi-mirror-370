# Daytona Code Sandbox Integration

## Overview

The MSA Reasoning Engine now includes complete integration with Daytona Cloud for secure, isolated code execution. This integration provides:

- **Secure Code Execution**: Isolated sandbox environments with no outbound network access
- **Resource Limits**: CPU, memory, and execution time constraints
- **Security Validation**: AST-based code analysis to prevent dangerous operations
- **Local Fallback**: Development-friendly fallback when Daytona Cloud is unavailable

## Architecture

### Components

1. **DaytonaService** (`app/services/daytona_service.py`)
   - Core service managing Daytona SDK integration
   - Handles sandbox creation, code execution, and cleanup
   - Provides security validation and resource monitoring

2. **InferencePlugin Integration** (`app/plugins/inference_plugin.py`)
   - Updated to use DaytonaService for probabilistic program execution
   - Maintains compatibility with the MSA reasoning pipeline
   - Supports both Daytona Cloud and local fallback execution

3. **API Endpoints** (`app/api/v2/daytona_endpoints.py`)
   - RESTful API for sandbox management and code execution
   - Status monitoring and configuration endpoints
   - Integration testing capabilities

### Security Features

- **AST Validation**: Static analysis prevents dangerous imports and function calls
- **Resource Limits**: Configurable CPU, memory, and execution timeouts
- **Isolated Environment**: No network access, limited file system access
- **Allowed Imports**: Whitelist of permitted Python modules

## Setup Instructions

### 1. Get Daytona API Key

1. Visit [Daytona Dashboard](https://app.daytona.io/dashboard/keys)
2. Create a new API key
3. Save the key securely (it won't be shown again)

### 2. Configure Environment

Set the environment variable:

```bash
export DAYTONA_API_KEY="your-api-key-here"
```

### 3. Restart Application

The MSA Reasoning Engine will automatically detect the API key and enable Daytona Cloud integration.

## API Endpoints

### GET /api/v2/daytona/status

Get current Daytona service status

**Response:**

```json
{
  "daytona_available": true,
  "sandbox_active": false,
  "config": {
    "cpu_limit": 2,
    "memory_limit_mb": 512,
    "execution_timeout": 30,
    "python_version": "3.11"
  },
  "api_key_configured": true,
  "service_status": "operational"
}
```

### POST /api/v2/daytona/execute

Execute code in Daytona sandbox

**Request:**

```json
{
  "code": "print('Hello World')",
  "timeout": 30,
  "config": {
    "cpu_limit": 2,
    "memory_limit_mb": 512
  }
}
```

**Response:**

```json
{
  "exit_code": 0,
  "stdout": "Hello World\n",
  "stderr": "",
  "execution_time": 0.123,
  "status": "completed",
  "resource_usage": {
    "cpu_usage_percent": 12.5,
    "memory_usage_mb": 45.2
  },
  "metadata": {
    "sandbox_type": "daytona",
    "sandbox_id": "sb_123456"
  }
}
```

### POST /api/v2/daytona/test

Run a predefined test to verify Daytona integration

### POST /api/v2/daytona/sandbox/create

Create a new sandbox instance

### DELETE /api/v2/daytona/sandbox

Clean up current sandbox

### GET /api/v2/daytona/config

Get current sandbox configuration

### PUT /api/v2/daytona/config

Update sandbox configuration

## Integration with MSA Pipeline

The Daytona integration is seamlessly incorporated into the MSA reasoning pipeline:

1. **Stage 5 (Infer)**: Probabilistic programs are executed in Daytona sandboxes
2. **Security**: All generated code undergoes AST validation
3. **Resource Management**: Execution limits prevent runaway computations
4. **Fallback**: Local execution ensures development continuity

### Usage in Reasoning Pipeline

```python
from reasoning_kernel.reasoning_kernel import ReasoningKernel
from reasoning_kernel.core.kernel_config import get_kernel_config

# Initialize reasoning kernel (automatically uses Daytona)
kernel, redis_client = await get_kernel_config()
reasoning_kernel = ReasoningKernel(kernel, redis_client)

# Execute reasoning (Stage 5 uses Daytona sandbox)
result = await reasoning_kernel.reason(
    "A coin is flipped 20 times with 14 heads observed"
)

print(f"Inference confidence: {result.overall_confidence}")
print(f"Execution secure: {result.success}")
```

## Configuration Options

### Sandbox Configuration

```python
from reasoning_kernel.services.daytona_service import SandboxConfig

config = SandboxConfig(
    cpu_limit=2,                    # CPU cores
    memory_limit_mb=512,            # RAM in MB
    execution_timeout=30,           # Timeout in seconds
    temp_storage_mb=50,             # Storage in MB
    python_version="3.11",          # Python version
    enable_networking=False,        # Network access
    enable_ast_validation=True,     # Security validation
    allowed_imports=[               # Permitted modules
        "numpy", "scipy", "jax", "numpyro",
        "pandas", "matplotlib", "json", "math"
    ]
)
```

### Security Settings

The system includes comprehensive security measures:

- **Blocked Operations**: File I/O, network access, subprocess execution
- **Dangerous Functions**: `exec`, `eval`, `open`, `__import__` are prohibited
- **Import Restrictions**: Only whitelisted modules are allowed
- **Resource Limits**: CPU and memory usage are constrained

## Development Mode

When Daytona Cloud is unavailable (no API key or connection issues), the system automatically falls back to local execution:

- **Less Secure**: Local execution with basic restrictions
- **Development Friendly**: Immediate feedback without cloud dependency
- **Timeout Enforcement**: Local timeouts still apply
- **Logging**: Clear indication of fallback mode in logs

## Monitoring and Logging

The integration provides comprehensive logging:

```
2025-08-11 14:52:32 [info] Daytona service initialized successfully
2025-08-11 14:52:32 [info] Sandbox initialized config={'cpu_limit': 2, ...}
```

Status indicators:

- ✅ Daytona Cloud integration active
- ⚠️ Using local fallback execution (less secure)
- ❌ Service unavailable

## Troubleshooting

### Common Issues

1. **"Daytona SDK not available"**
   - Solution: Ensure `daytona_sdk` package is installed
   - Command: `pip install daytona_sdk`

2. **"API key not configured"**
   - Solution: Set `DAYTONA_API_KEY` environment variable
   - Check: API key is valid and not expired

3. **"Security validation failed"**
   - Solution: Review code for dangerous imports or function calls
   - Check: Ensure only whitelisted modules are used

4. **"Execution timeout"**
   - Solution: Increase timeout in configuration
   - Check: Code efficiency and resource usage

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import structlog
structlog.configure(level=logging.DEBUG)
```

## Performance Considerations

- **Sandbox Creation**: ~2-3 seconds overhead per sandbox
- **Code Execution**: Similar to local execution once sandbox is ready
- **Resource Limits**: Balance between security and performance
- **Local Fallback**: Faster development iteration without cloud roundtrip

## Future Enhancements

Planned improvements include:

1. **Persistent Sandboxes**: Reuse sandboxes across multiple executions
2. **Custom Environments**: Pre-configured environments with specific dependencies
3. **Result Caching**: Cache execution results for identical code
4. **Enhanced Monitoring**: Resource usage dashboards and alerts
5. **Batch Execution**: Execute multiple programs in parallel

## Testing

Run the integration tests:

```bash
# Basic functionality test
python simple_daytona_demo.py

# API endpoint tests
curl -X GET http://localhost:5000/api/v2/daytona/status
curl -X POST http://localhost:5000/api/v2/daytona/test

# Full reasoning pipeline test
python -m pytest tests/test_daytona_integration.py
```
