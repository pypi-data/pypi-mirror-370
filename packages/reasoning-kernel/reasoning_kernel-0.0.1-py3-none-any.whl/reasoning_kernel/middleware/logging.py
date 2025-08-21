"""FastAPI middleware for request logging with correlation IDs."""

import time
from typing import Callable
import uuid

from fastapi import Request
from fastapi import Response
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.core.logging_config import request_context
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request correlation IDs and log requests/responses."""

    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("request")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging and correlation ID."""
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Extract basic request info
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_host = getattr(request.client, "host", "unknown") if request.client else "unknown"
        
        start_time = time.time()
        
        # Set request context for all logs within this request
        with request_context(
            request_id=request_id,
            method=method,
            path=path,
            endpoint=path,
            client_host=client_host
        ):
            # Log request start
            self.logger.info(
                "Request started",
                method=method,
                url=url,
                path=path,
                client_host=client_host,
                user_agent=request.headers.get("User-Agent", "unknown")
            )
            
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Log successful response
                self.logger.info(
                    "Request completed",
                    status_code=response.status_code,
                    duration=duration,
                    response_size=response.headers.get("Content-Length", "unknown")
                )
                
                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
                
                return response
                
            except Exception as e:
                # Calculate duration for failed requests
                duration = time.time() - start_time
                
                # Log error response
                self.logger.error(
                    "Request failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration=duration
                )
                
                raise