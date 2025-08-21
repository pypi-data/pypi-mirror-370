"""
Tests for enhanced security validation in request models
"""

import pytest
from pydantic import ValidationError

from reasoning_kernel.models.requests import (
    MSAReasoningRequest,
    validate_no_dangerous_patterns,
    sanitize_html_content,
    validate_context_depth,
)


class TestSecurityValidation:
    """Test security validation functions"""

    def test_validate_no_dangerous_patterns_safe(self):
        """Test safe content passes validation"""
        safe_content = "This is a normal scenario for testing the reasoning system"
        # Should not raise any exception
        validate_no_dangerous_patterns(safe_content, "test")

    def test_validate_no_dangerous_patterns_dangerous(self):
        """Test dangerous patterns are rejected"""
        dangerous_cases = [
            "eval('malicious_code')",
            "__import__('os')",
            "exec('rm -rf /')",
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "${dangerous_template}",
            "{{template_injection}}",
        ]

        for dangerous_content in dangerous_cases:
            with pytest.raises(ValueError, match="contains potentially dangerous content"):
                validate_no_dangerous_patterns(dangerous_content, "test")

    def test_sanitize_html_content(self):
        """Test HTML content sanitization"""
        test_cases = [
            ("Normal text", "Normal text"),
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("Hello <strong>World</strong>", "Hello &lt;strong&gt;World&lt;/strong&gt;"),
            ("<div onclick='evil()'>Content</div>", "&lt;div&gt;Content&lt;/div&gt;"),
            ("<iframe src='evil'></iframe>", ""),
            ("Text with <br> break", "Text with &lt;br&gt; break"),
        ]

        for input_html, expected in test_cases:
            result = sanitize_html_content(input_html)
            assert result == expected

    def test_validate_context_depth_valid(self):
        """Test valid context depth validation"""
        shallow_context = {"level1": {"level2": "value"}}
        # Should not raise any exception
        validate_context_depth(shallow_context)

    def test_validate_context_depth_too_deep(self):
        """Test context depth exceeding maximum (configured as 5)"""
        # Create nested dict exceeding MAX_CONTEXT_DEPTH (5) - needs 7 levels to fail
        deep_context = {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": {"level7": "too_deep"}}}}}}}

        with pytest.raises(ValueError, match="Context object depth exceeds maximum"):
            validate_context_depth(deep_context)


class TestMSAReasoningRequestValidation:
    """Test MSAReasoningRequest model validation"""

    def test_valid_request(self):
        """Test creation of valid request"""
        request = MSAReasoningRequest(scenario="Valid scenario for testing the reasoning system")

        assert request.scenario == "Valid scenario for testing the reasoning system"
        assert request.mode == "both"
        assert request.priority == "normal"
        assert request.max_execution_time == 300

    def test_scenario_too_short(self):
        """Test scenario minimum length validation"""
        with pytest.raises(ValidationError, match="at least 10 characters"):
            MSAReasoningRequest(scenario="Short")

    def test_scenario_too_long(self):
        """Test scenario maximum length validation"""
        long_scenario = "x" * 10001  # Exceeds MAX_SCENARIO_LENGTH
        with pytest.raises(ValidationError, match="at most 10000 characters"):
            MSAReasoningRequest(scenario=long_scenario)

    def test_scenario_dangerous_patterns(self):
        """Test dangerous patterns in scenario are rejected"""
        with pytest.raises(ValidationError, match="potentially dangerous content"):
            MSAReasoningRequest(scenario="Please eval('malicious_code') this scenario for me")

    def test_invalid_session_id(self):
        """Test invalid session ID format"""
        with pytest.raises(ValidationError, match="Session ID can only contain alphanumeric"):
            MSAReasoningRequest(scenario="Valid scenario for testing", session_id="invalid@session#id")

    def test_valid_session_id(self):
        """Test valid session ID formats"""
        valid_session_ids = ["session123", "test_session", "session-id-123", "SESSION_ID"]

        for session_id in valid_session_ids:
            request = MSAReasoningRequest(scenario="Valid scenario for testing", session_id=session_id)
            assert request.session_id == session_id

    def test_invalid_mode(self):
        """Test invalid mode validation"""
        with pytest.raises(ValidationError, match="Mode must be one of"):
            MSAReasoningRequest(scenario="Valid scenario", mode="invalid_mode")

    def test_invalid_priority(self):
        """Test invalid priority validation"""
        with pytest.raises(ValidationError, match="Priority must be one of"):
            MSAReasoningRequest(scenario="Valid scenario", priority="critical")  # Not in allowed priorities

    def test_execution_time_too_low(self):
        """Test execution time below minimum"""
        with pytest.raises(ValidationError, match="greater than or equal to 10"):
            MSAReasoningRequest(scenario="Valid scenario", max_execution_time=5)

    def test_execution_time_too_high(self):
        """Test execution time above maximum"""
        with pytest.raises(ValidationError, match="less than or equal to 1800"):
            MSAReasoningRequest(scenario="Valid scenario", max_execution_time=2000)

    def test_context_validation_safe(self):
        """Test context with safe content"""
        valid_context = {
            "topic": "machine learning",
            "constraints": ["accuracy > 0.8", "training_time < 24h"],
            "preferences": {"model_type": "neural_network"},
        }

        request = MSAReasoningRequest(scenario="Valid scenario", context=valid_context)

        assert request.context == valid_context

    def test_context_validation_dangerous(self):
        """Test context with dangerous patterns"""
        with pytest.raises(ValidationError, match="potentially dangerous content"):
            MSAReasoningRequest(scenario="Valid scenario", context={"safe_key": "value", "dangerous": "eval('code')"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
