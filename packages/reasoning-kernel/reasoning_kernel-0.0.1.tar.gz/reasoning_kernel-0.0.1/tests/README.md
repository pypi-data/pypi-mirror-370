# Unified Reasoning Pipeline Tests

This directory contains comprehensive tests for the MSA (Model Synthesis Architecture) reasoning pipeline.

## Test Coverage

### Core Pipeline Tests (`test_reasoning_unified_pipeline.py`)

The unified pipeline test suite contains **31 test cases** organized into 3 test classes:

#### TestUnifiedPipeline (22 tests)
- **Pipeline Structure & Callbacks**: Validates 5-stage pipeline execution and callback mechanisms
- **End-to-End Success**: Tests complete successful pipeline execution
- **Stage Failure Handling**: Tests each stage failure (parse, retrieve, graph, synthesize, infer)
- **Error Recovery**: Tests partial execution and error propagation
- **Configuration Testing**: Custom configurations and edge cases
- **Input Validation**: Empty, large, and special character inputs
- **Concurrency**: Multiple pipeline executions
- **Data Handling**: Additional parameters and session tracking

#### TestReasoningConfiguration (3 tests)
- **Default Configuration**: Validates default settings
- **Custom Configuration**: Tests custom parameter values  
- **Fallback Models**: Tests fallback model initialization

#### TestPipelineRobustness (6 tests)
- **Timeout Simulation**: Tests timeout handling
- **Memory Pressure**: Tests resource constraint handling
- **Network Failures**: Tests external dependency failures
- **Partial Recovery**: Tests graceful degradation
- **Invalid Config**: Tests robustness with invalid settings
- **Callback Isolation**: Tests that callback failures don't crash pipeline

## Test Design Principles

### Deterministic Testing
- **No External Dependencies**: All tests use mocking to avoid dependency on external services
- **Consistent Results**: Tests produce the same results across environments
- **Fast Execution**: All 31 tests complete in ~0.07 seconds

### CI/CD Ready
- **Isolation**: Tests don't depend on external APIs, databases, or services
- **Resource Efficient**: Minimal memory and CPU usage
- **Error Handling**: Comprehensive error scenario coverage
- **Cross-Platform**: Compatible with different operating systems

### Coverage Areas
- ✅ **Success Paths**: Complete pipeline execution scenarios
- ✅ **Error Paths**: Each stage failure and recovery
- ✅ **Edge Cases**: Empty input, malformed data, extreme values
- ✅ **Configuration**: Default and custom settings
- ✅ **Concurrency**: Multiple simultaneous executions
- ✅ **Callbacks**: Event handling and error isolation
- ✅ **Robustness**: Timeout, memory, and network failure scenarios

## Running Tests

### Basic Execution
```bash
# Run all pipeline tests
pytest tests/test_reasoning_unified_pipeline.py -v

# Run specific test class
pytest tests/test_reasoning_unified_pipeline.py::TestUnifiedPipeline -v

# Run with timing information
pytest tests/test_reasoning_unified_pipeline.py --durations=10
```

### CI Integration
```bash
# Suitable for CI pipelines
pytest tests/test_reasoning_unified_pipeline.py --tb=short --quiet
```

## Test Architecture

### Mock Strategy
- **Comprehensive Mocking**: All external dependencies (semantic_kernel, structlog, redis, etc.) are mocked
- **Realistic Behavior**: Mocks simulate realistic pipeline execution with configurable results
- **Error Injection**: Tests can inject errors at any stage to validate error handling

### Async Testing
- **Native Async Support**: Uses pytest-asyncio for proper async test execution
- **Callback Testing**: Validates async callback mechanisms
- **Concurrent Execution**: Tests multiple simultaneous pipeline runs

### Data Validation
- **Result Structure**: Validates ReasoningResult structure and content
- **Confidence Metrics**: Tests confidence calculation and bounds
- **Timing Information**: Validates execution timing tracking
- **Error Messages**: Validates error propagation and messaging

## Maintenance

### Adding New Tests
1. Follow the existing pattern in `TestUnifiedPipeline`
2. Use `_create_mock_pipeline_execution()` helper for consistent mocking
3. Test both success and failure scenarios
4. Ensure tests are deterministic and don't require external services

### Mock Updates
If the pipeline structure changes:
1. Update mock data classes (`MockParseResult`, etc.)
2. Update `_create_mock_pipeline_execution()` helper
3. Verify all tests still pass with the new structure

This test suite ensures the MSA reasoning pipeline is robust, reliable, and ready for production use.