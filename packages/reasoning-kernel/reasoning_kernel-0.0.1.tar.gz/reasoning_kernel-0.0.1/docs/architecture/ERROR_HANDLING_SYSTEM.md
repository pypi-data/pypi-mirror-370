# Error Handling Standardization System

## Overview

The MSA Reasoning Kernel implements a comprehensive, structured exception hierarchy that replaces scattered custom exceptions with a centralized, consistent error handling system.

## Features

- **Hierarchical Exception Structure**: Organized exception classes for better error categorization
- **Error Context Tracking**: Correlation IDs and contextual information for debugging
- **User-Friendly Messages**: Separate messages for users and developers
- **Integration Support**: Built-in logging and monitoring system integration
- **Recovery Guidance**: Support for error recovery and graceful degradation
- **Legacy Compatibility**: Seamless migration from existing custom exceptions

## Exception Hierarchy

```
MSAError (Base Exception)
├── ValidationError
├── SecurityError  
├── AuthenticationError
├── AuthorizationError
├── TimeoutError
├── RateLimitError
├── APIError
├── MSAPipelineError
├── DatabaseError
├── CacheError
├── ConfigurationError
└── ServiceError
```

## Core Components

### 1. Base MSAError Class

All exceptions inherit from `MSAError`, providing:

- **Error Code**: Standardized error identification
- **Error Category**: Classification for handling logic
- **Severity Level**: Priority for logging and alerting
- **HTTP Status Mapping**: Automatic HTTP response codes
- **Error Context**: Correlation IDs and tracking information
- **User Messages**: Human-friendly error descriptions
- **Recovery Information**: Whether errors are recoverable and retry timing

### 2. ErrorContext

Provides contextual information for error tracking:

```python
@dataclass
class ErrorContext:
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    operation: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
```

### 3. ErrorHandler Utility Class

Provides helper methods for common error handling patterns:

- `create_context()`: Create error context with provided information
- `handle_validation_error()`: Standardized validation error creation
- `handle_timeout()`: Timeout error with duration tracking
- `handle_service_error()`: External service failure handling
- `wrap_exception()`: Convert generic exceptions to MSA errors

### 4. Exception Decorator

The `@handle_exceptions` decorator provides automatic error wrapping:

```python
@handle_exceptions(context_component="data_processing")
def process_data(data):
    # Function logic here
    # Any unhandled exceptions are automatically wrapped
```

## Exception Types

### ValidationError

- **Purpose**: Input validation failures
- **Category**: VALIDATION
- **Severity**: LOW
- **HTTP Status**: 400 Bad Request
- **Special Features**: Field-specific error collection

### SecurityError

- **Purpose**: Security violations
- **Category**: SECURITY  
- **Severity**: HIGH
- **HTTP Status**: 403 Forbidden
- **Use Cases**: Access control violations, security policy breaches

### TimeoutError

- **Purpose**: Operation timeouts
- **Category**: TIMEOUT
- **Severity**: MEDIUM
- **HTTP Status**: 500 Internal Server Error
- **Special Features**: Timeout duration tracking, automatic recovery flag

### MSAPipelineError

- **Purpose**: MSA pipeline stage failures
- **Category**: MSA_PIPELINE
- **Severity**: HIGH
- **Special Features**: Stage identification, stage-specific data

### ServiceError

- **Purpose**: External service failures
- **Category**: SERVICE
- **Severity**: MEDIUM
- **HTTP Status**: 503 Service Unavailable
- **Special Features**: Service name and endpoint tracking

## Error Context and Correlation

Every error includes contextual information for tracking and debugging:

- **Correlation ID**: Unique identifier linking related operations
- **Timestamp**: When the error occurred
- **Operation**: What operation was being performed
- **Component**: Which system component generated the error
- **User/Session IDs**: For user-specific error tracking
- **Additional Data**: Custom contextual information

## Integration with Logging

Errors are automatically logged with structured data:

```python
{
    "error_class": "ValidationError",
    "error_code": "VALIDATION_FAILED", 
    "error_category": "validation",
    "severity": "low",
    "message": "User input validation failed",
    "user_message": "Please check your input and try again",
    "correlation_id": "abc123-def456-ghi789",
    "context": {
        "operation": "validate_user_input",
        "component": "api_endpoint",
        "user_id": "user123"
    }
}
```

## Migration Strategy

### Phase 1: Core System Implementation ✅

- [x] Create central exception hierarchy
- [x] Implement ErrorContext and correlation tracking
- [x] Build ErrorHandler utility class
- [x] Create comprehensive test suite
- [x] Document migration examples

### Phase 2: Legacy Exception Migration (Current)

- [ ] Update existing custom exceptions to use central system
- [ ] Migrate scattered exception handling to standardized patterns
- [ ] Update imports across codebase
- [ ] Validate error handling with integration tests

### Phase 3: Enhanced Error Handling

- [ ] Implement error recovery patterns
- [ ] Add circuit breaker integration
- [ ] Create error monitoring and alerting
- [ ] Build error analytics dashboard

## Usage Examples

### Basic Exception Creation

```python
from reasoning_kernel.core.exceptions import ValidationError, ErrorHandler

# Create validation error with field errors
field_errors = {"email": ["Invalid format"], "age": ["Must be positive"]}
error = ValidationError("Validation failed", field_errors=field_errors)
```

### With Error Context

```python
from reasoning_kernel.core.exceptions import ErrorHandler, MSAPipelineError

# Create context
context = ErrorHandler.create_context(
    operation="knowledge_extraction",
    user_id="user123",
    component="msa_pipeline"
)

# Use context in error
error = MSAPipelineError(
    "Pipeline stage failed",
    stage="knowledge_extraction",
    context=context
)
```

### Using ErrorHandler Utilities

```python
# Wrap generic exception
try:
    risky_operation()
except ValueError as e:
    raise ErrorHandler.wrap_exception(e, context=context)

# Handle service error
error = ErrorHandler.handle_service_error(
    "external_api", 
    "fetch_data",
    cause=original_exception
)
```

### Using Exception Decorator

```python
@handle_exceptions(context_component="data_processor")
def process_complex_data(data):
    # Any unhandled exception is automatically wrapped
    # with proper context tracking
    return complex_processing(data)
```

## Error Response Format

API errors are serialized to a standard format:

```json
{
    "error": {
        "code": "VALIDATION_FAILED",
        "category": "validation",
        "severity": "low", 
        "message": "Please check your input and try again",
        "developer_message": "User input validation failed",
        "correlation_id": "abc123-def456-ghi789",
        "timestamp": 1629123456.789,
        "recoverable": true,
        "retry_after": null
    }
}
```

## Testing

The system includes comprehensive tests covering:

- Exception hierarchy and inheritance
- Error context tracking and correlation IDs
- Error categorization and severity levels
- User-friendly and developer messages
- HTTP status code mapping
- Error handling utilities and decorators
- Legacy exception compatibility
- Performance and edge cases

Run tests with:

```bash
python -m pytest tests/test_error_handling.py -v
```

## Monitoring and Alerting

Errors are categorized by severity for monitoring:

- **CRITICAL**: Immediate attention required, system stability at risk
- **HIGH**: Significant functionality impacted, requires prompt attention
- **MEDIUM**: Standard operational errors, monitor for patterns
- **LOW**: Minor issues, primarily for debugging and improvement

## Best Practices

1. **Use Specific Exception Types**: Choose the most appropriate exception class
2. **Include Error Context**: Always provide operation and component information
3. **Set Appropriate Properties**: Configure recovery flags and user messages
4. **Chain Exceptions**: Preserve original exception details with `cause`
5. **Leverage Utilities**: Use ErrorHandler methods for common patterns
6. **Consider Decorators**: Use `@handle_exceptions` for automatic wrapping
7. **Test Error Paths**: Include error handling in unit and integration tests

## Performance Considerations

- Error context creation is lightweight with UUID generation
- Logging is asynchronous to avoid blocking operations
- Exception chaining preserves full stack traces
- Structured logging enables efficient monitoring queries

## Future Enhancements

- **Error Recovery Patterns**: Automatic retry and circuit breaker integration
- **Enhanced Monitoring**: Real-time error analytics and alerting
- **Error Aggregation**: Pattern detection and root cause analysis
- **User Experience**: Contextual error guidance and recovery suggestions

## Legacy Compatibility

The system maintains compatibility with existing custom exceptions:

```python
# Legacy aliases for seamless migration
DaytonaServiceError = ServiceError
StageExecutionError = MSAPipelineError
StageValidationError = ValidationError
CircuitBreakerError = ServiceError
GracefulDegradationError = ServiceError
```

This allows gradual migration while maintaining existing functionality.
