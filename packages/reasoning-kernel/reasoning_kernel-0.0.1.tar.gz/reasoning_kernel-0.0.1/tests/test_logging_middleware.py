"""Tests for request logging middleware."""


import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from reasoning_kernel.middleware.logging import RequestLoggingMiddleware


@pytest.fixture
def app_with_middleware():
    """Create FastAPI app with logging middleware for testing."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    return app


@pytest.fixture
def client(app_with_middleware):
    """Create test client."""
    return TestClient(app_with_middleware)


class TestRequestLoggingMiddleware:
    """Test request logging middleware functionality."""

    def test_successful_request_adds_request_id(self, client):
        """Test that successful requests get X-Request-ID header."""
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] != ""

    def test_custom_request_id_preserved(self, client):
        """Test that custom X-Request-ID header is preserved."""
        custom_id = "custom-request-123"
        response = client.get("/test", headers={"X-Request-ID": custom_id})
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    def test_error_request_handling(self, client):
        """Test that error requests are handled properly."""
        with pytest.raises(Exception):
            # The middleware should let the exception propagate
            # but should log it appropriately
            client.get("/error")

    def test_middleware_creates_logger(self):
        """Test that middleware creates proper logger instance."""
        app = FastAPI()
        middleware = RequestLoggingMiddleware(app)
        
        assert middleware.logger is not None
        assert hasattr(middleware.logger, "info")
        assert hasattr(middleware.logger, "error")

    def test_request_context_extraction(self, client):
        """Test that request context is properly extracted."""
        # This is more of an integration test to ensure the middleware
        # doesn't break the application flow
        response = client.get("/test", headers={
            "User-Agent": "test-agent",
            "X-Request-ID": "test-123"
        })
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == "test-123"