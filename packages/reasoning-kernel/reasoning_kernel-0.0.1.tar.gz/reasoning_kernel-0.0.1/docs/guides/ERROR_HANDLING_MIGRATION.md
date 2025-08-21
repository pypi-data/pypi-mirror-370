# Error Handling Migration Examples

This document demonstrates how to migrate existing error handling patterns to use the standardized MSA exception system.

Examples show:

- Before: Generic exception handling
- After: Standardized MSA error handling  
- Best practices for error context and logging

## Example 1: Generic Exception to Specific MSA Error

### Before: Generic exception handling

```python
def old_api_endpoint():
    try:
        # Some API logic
        result = process_request(data)
        return result
    except Exception as e:
        logger.error("API error occurred", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
```

### After: Standardized MSA error handling

```python
from reasoning_kernel.core.exceptions import APIError, ErrorHandler, handle_exceptions

@handle_exceptions(context_component="api_endpoint")
def new_api_endpoint():
    try:
        # Some API logic
        result = process_request(data)
        return result
    except ValueError as e:
        # Specific validation error
        raise ErrorHandler.wrap_exception(e, message_override="Invalid request data")
    except ConnectionError as e:
        # Service error
        raise ErrorHandler.handle_service_error("external_api", "process_request", cause=e)
```

## Example 2: WebSocket Error Handling Migration

### Before: Generic WebSocket error handling (from streaming_endpoints.py)

```python
async def old_send_stage_update(self, session_id: str, stage_data: Dict[str, Any]):
    """Send stage update to connected client"""
    if session_id in self.active_connections:
        websocket = self.active_connections[session_id]
        try:
            await websocket.send_json({
                "type": "stage_update",
                "timestamp": datetime.now().isoformat(),
                **stage_data
            })
        except Exception as e:
            logger.error("Failed to send stage update", 
                       session_id=session_id, 
                       error=str(e))
```

### After: Standardized WebSocket error handling

```python
from reasoning_kernel.core.exceptions import APIError, ErrorContext, ErrorHandler

async def new_send_stage_update(self, session_id: str, stage_data: Dict[str, Any]):
    """Send stage update to connected client"""
    if session_id in self.active_connections:
        websocket = self.active_connections[session_id]
        
        # Create error context for tracking
        context = ErrorHandler.create_context(
            operation="send_stage_update",
            session_id=session_id,
            component="streaming_websocket"
        )
        
        try:
            await websocket.send_json({
                "type": "stage_update",
                "timestamp": datetime.now().isoformat(),
                **stage_data
            })
        except ConnectionError as e:
            # Network/WebSocket specific error
            raise APIError(
                f"Failed to send stage update to session {session_id}",
                api_endpoint="websocket_send",
                context=context,
                cause=e,
                recoverable=True,
                user_message="Connection lost. Please refresh your browser."
            )
        except Exception as e:
            # Unexpected error - wrap it
            raise ErrorHandler.wrap_exception(e, context=context)
```

## Example 3: MSA Pipeline Error Handling

### Before: Pipeline stage error handling

```python
class OldKnowledgeExtractionStage:
    def execute(self, input_data):
        try:
            # Knowledge extraction logic
            return self.extract_knowledge(input_data)
        except (json.JSONDecodeError, Exception) as e:
            logger.error("Knowledge extraction failed", error=str(e))
            raise
```

### After: Standardized MSA pipeline error handling

```python
from reasoning_kernel.core.exceptions import MSAPipelineError, ErrorContext

class NewKnowledgeExtractionStage:
    def execute(self, input_data):
        context = ErrorHandler.create_context(
            operation="knowledge_extraction",
            component="msa_pipeline"
        )
        
        try:
            # Knowledge extraction logic
            return self.extract_knowledge(input_data)
        except json.JSONDecodeError as e:
            # Specific JSON parsing error
            raise MSAPipelineError(
                "Failed to parse JSON input in knowledge extraction stage",
                stage="knowledge_extraction",
                stage_data={"input_type": type(input_data).__name__},
                context=context,
                cause=e,
                user_message="Invalid input format. Please check your data."
            )
        except Exception as e:
            # Generic pipeline error
            raise MSAPipelineError(
                f"Knowledge extraction stage failed: {str(e)}",
                stage="knowledge_extraction",
                context=context,
                cause=e
            )
```

## Best Practices Summary

1. **Always use specific exception types when possible:**
   - ValidationError for input validation issues
   - TimeoutError for operation timeouts
   - ServiceError for external service failures
   - MSAPipelineError for MSA pipeline stage failures

2. **Always include error context:**
   - operation: What operation was being performed
   - component: Which component/module the error originated from
   - user_id/session_id: For user-specific error tracking

3. **Set appropriate error properties:**
   - recoverable: True if the error can be retried
   - retry_after: Seconds to wait before retry (for rate limits)
   - user_message: Human-friendly error message

4. **Chain exceptions properly:**
   - Always include the original exception as 'cause'
   - This preserves the full error stack for debugging

5. **Use the ErrorHandler utility class:**
   - For creating error contexts
   - For wrapping generic exceptions
   - For common error patterns

6. **Consider using the @handle_exceptions decorator:**
   - For functions that need automatic error wrapping
   - Reduces boilerplate error handling code
   - Ensures consistent error context
