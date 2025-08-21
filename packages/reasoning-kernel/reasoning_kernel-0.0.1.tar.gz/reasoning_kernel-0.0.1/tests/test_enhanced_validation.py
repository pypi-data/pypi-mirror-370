"""
Comprehensive tests for enhanced input validation and security features
======================================================================

Tests the security validation, HTML sanitization, and comprehensive input
validation implemented in the request models.
"""

import pytest
from pydantic import ValidationError

from reasoning_kernel.models.requests import (
    MSAReasoningRequest,
    KnowledgeExtractionRequest,
    ProbabilisticModelRequest,
    SessionStatusRequest,
    validate_no_dangerous_patterns,
    validate_context_depth,
    sanitize_html_content,
)
from reasoning_kernel.core.constants import (
    MAX_SCENARIO_LENGTH,
    MAX_SESSION_ID_LENGTH,
    MODE_BOTH,
    MODE_KNOWLEDGE,
    PRIORITY_NORMAL,
    PRIORITY_HIGH,
)


class TestSecurityValidation:
    """Test security validation functions"""

    def test_validate_no_dangerous_patterns_safe_content(self):
        """Test that safe content passes validation"""
        safe_content = "This is a normal scenario about business analysis"
        result = validate_no_dangerous_patterns(safe_content, "test_field")
        assert result == safe_content

    def test_validate_no_dangerous_patterns_dangerous_content(self):
        """Test that dangerous patterns are caught"""
        dangerous_patterns = [
            "eval('malicious code')",
            "exec('harmful command')",
            "__import__('os')",
            "os.system('rm -rf /')",
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "SELECT * FROM users",
            "UNION SELECT password FROM users",
            "DROP TABLE users",
            "' OR '1'='1",
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(
                ValueError, match="contains potentially dangerous content|contains potential SQL injection"
            ):
                validate_no_dangerous_patterns(pattern, "test_field")

    def test_sanitize_html_content(self):
        """Test HTML content sanitization"""
        test_cases = [
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("Hello <strong>World</strong>", "Hello &lt;strong&gt;World&lt;/strong&gt;"),
            ("<div onclick='evil()'>Content</div>", "&lt;div onclick='evil()'&gt;Content&lt;/div&gt;"),
            ("Normal text", "Normal text"),
            ("<iframe src='evil'></iframe>", "&lt;iframe src='evil'&gt;&lt;/iframe&gt;"),
            ("Text with <br> break", "Text with &lt;br&gt; break"),
        ]

        for input_html, expected in test_cases:
            result = sanitize_html_content(input_html)
            assert result == expected

    def test_validate_context_depth_valid(self):
        """Test valid context depth validation"""
        valid_contexts = [
            {"key": "value"},
            {"nested": {"level2": {"level3": "value"}}},
            {"array": [1, 2, 3]},
            {"mixed": {"nested": [{"deep": "value"}]}},
        ]

        for context in valid_contexts:
            # Should not raise any exception
            validate_context_depth(context)

    def test_validate_context_depth_too_deep(self):
        """Test context depth exceeding maximum"""
        # Create nested dict exceeding MAX_CONTEXT_DEPTH
        deep_context = {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": "too_deep"}}}}}}

        with pytest.raises(ValueError, match="Context object depth exceeds maximum"):
            validate_context_depth(deep_context)

    def test_validate_context_depth_too_many_keys(self):
        """Test context with too many keys"""
        large_context = {f"key_{i}": f"value_{i}" for i in range(100)}  # Exceeds MAX_CONTEXT_KEYS (50)

        with pytest.raises(ValueError, match="Context object has too many keys"):
            validate_context_depth(large_context)

    def test_validate_context_depth_dangerous_content(self):
        """Test context with dangerous content"""
        dangerous_context = {"safe_key": "safe_value", "dangerous_key": "eval('malicious')"}

        with pytest.raises(ValueError, match="contains potentially dangerous content"):
            validate_context_depth(dangerous_context)


class TestMSAReasoningRequestValidation:
    """Test MSAReasoningRequest validation"""

    def test_valid_request(self):
        """Test valid MSA reasoning request"""
        valid_request = {
            "scenario": "Analyze the business impact of implementing a new CRM system",
            "session_id": "session_123",
            "context": {"department": "sales", "budget": 50000},
            "mode": MODE_KNOWLEDGE,
            "priority": PRIORITY_NORMAL,
            "max_execution_time": 300,
        }

        request = MSAReasoningRequest(**valid_request)
        assert request.scenario == "Analyze the business impact of implementing a new CRM system"
        assert request.session_id == "session_123"
        assert request.mode == MODE_KNOWLEDGE
        assert request.priority == PRIORITY_NORMAL

    def test_scenario_too_short(self):
        """Test scenario below minimum length"""
        with pytest.raises(ValidationError, match="at least 10 characters"):
            MSAReasoningRequest(scenario="Short")

    def test_scenario_too_long(self):
        """Test scenario exceeding maximum length"""
        long_scenario = "A" * (MAX_SCENARIO_LENGTH + 1)
        with pytest.raises(ValidationError, match="at most 10000 characters"):
            MSAReasoningRequest(scenario=long_scenario)

    def test_scenario_with_dangerous_content(self):
        """Test scenario with dangerous patterns"""
        with pytest.raises(ValidationError, match="contains potentially dangerous content"):
            MSAReasoningRequest(scenario="Please eval('malicious_code') this scenario")

    def test_scenario_html_sanitization(self):
        """Test HTML content in scenario is sanitized"""
        request = MSAReasoningRequest(
            scenario="This is a <script>alert('xss')</script> safe scenario with <strong>emphasis</strong>"
        )
        # Script should be removed, strong tag should remain
        assert "<script>" not in request.scenario
        assert "<strong>emphasis</strong>" in request.scenario

    def test_invalid_session_id_characters(self):
        """Test session ID with invalid characters"""
        with pytest.raises(ValidationError, match="only contain alphanumeric characters"):
            MSAReasoningRequest(scenario="Valid scenario for testing", session_id="invalid@session#id")

    def test_valid_session_id_patterns(self):
        """Test valid session ID patterns"""
        valid_ids = ["session123", "session-123", "session_123", "Session_ID-789"]

        for session_id in valid_ids:
            request = MSAReasoningRequest(scenario="Valid scenario for testing", session_id=session_id)
            assert request.session_id == session_id

    def test_invalid_mode(self):
        """Test invalid reasoning mode"""
        with pytest.raises(ValidationError, match="Mode must be one of"):
            MSAReasoningRequest(scenario="Valid scenario", mode="invalid_mode")

    def test_invalid_priority(self):
        """Test invalid priority level"""
        with pytest.raises(ValidationError, match="Priority must be one of"):
            MSAReasoningRequest(scenario="Valid scenario", priority="critical")  # Not in allowed priorities

    def test_execution_time_limits(self):
        """Test execution time validation"""
        # Test minimum limit
        with pytest.raises(ValidationError, match="greater than or equal to 10"):
            MSAReasoningRequest(scenario="Valid scenario", max_execution_time=5)

        # Test maximum limit
        with pytest.raises(ValidationError, match="less than or equal to 1800"):
            MSAReasoningRequest(scenario="Valid scenario", max_execution_time=2000)

    def test_high_priority_execution_time_validation(self):
        """Test that high priority requests have reasonable execution times"""
        with pytest.raises(ValidationError, match="High priority requests should have shorter execution times"):
            MSAReasoningRequest(
                scenario="Valid scenario",
                priority=PRIORITY_HIGH,
                max_execution_time=700,  # Exceeds 600 seconds for high priority
            )

    def test_context_validation(self):
        """Test context object validation"""
        # Test valid context
        valid_context = {
            "department": "engineering",
            "constraints": ["budget", "timeline"],
            "metrics": {"accuracy": 0.95, "performance": "high"},
        }

        request = MSAReasoningRequest(scenario="Valid scenario", context=valid_context)
        assert request.context == valid_context

        # Test context with dangerous content
        with pytest.raises(ValidationError, match="contains potentially dangerous content"):
            MSAReasoningRequest(scenario="Valid scenario", context={"safe_key": "value", "dangerous": "eval('code')"})


class TestKnowledgeExtractionRequestValidation:
    """Test KnowledgeExtractionRequest validation"""

    def test_valid_request(self):
        """Test valid knowledge extraction request"""
        request = KnowledgeExtractionRequest(
            scenario="Extract knowledge from this business scenario",
            extract_types=["entities", "relationships", "constraints"],
        )
        assert len(request.extract_types) == 3
        assert "entities" in request.extract_types

    def test_invalid_extract_types(self):
        """Test invalid extract types"""
        with pytest.raises(ValidationError, match="Invalid extract type"):
            KnowledgeExtractionRequest(scenario="Valid scenario", extract_types=["invalid_type", "entities"])

    def test_extract_types_must_be_strings(self):
        """Test that extract types must be strings"""
        with pytest.raises(ValidationError, match="Extract type must be a string"):
            KnowledgeExtractionRequest(scenario="Valid scenario", extract_types=[123, "entities"])


class TestProbabilisticModelRequestValidation:
    """Test ProbabilisticModelRequest validation"""

    def test_valid_request(self):
        """Test valid probabilistic model request"""
        model_specs = {
            "variables": ["temperature", "humidity"],
            "distributions": {"temperature": "normal", "humidity": "beta"},
        }

        request = ProbabilisticModelRequest(
            model_specifications=model_specs, inference_samples=2000, inference_chains=6, random_seed=42
        )

        assert request.inference_samples == 2000
        assert request.inference_chains == 6
        assert request.random_seed == 42

    def test_empty_model_specifications(self):
        """Test empty model specifications"""
        with pytest.raises(ValidationError, match="Model specifications cannot be empty"):
            ProbabilisticModelRequest(model_specifications={})

    def test_inference_samples_limits(self):
        """Test inference samples validation limits"""
        model_specs = {"variables": ["x"]}

        # Test minimum
        with pytest.raises(ValidationError, match="greater than or equal to 100"):
            ProbabilisticModelRequest(model_specifications=model_specs, inference_samples=50)

        # Test maximum
        with pytest.raises(ValidationError, match="less than or equal to 5000"):
            ProbabilisticModelRequest(model_specifications=model_specs, inference_samples=6000)

    def test_inference_chains_limits(self):
        """Test inference chains validation limits"""
        model_specs = {"variables": ["x"]}

        # Test minimum
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            ProbabilisticModelRequest(model_specifications=model_specs, inference_chains=0)

        # Test maximum
        with pytest.raises(ValidationError, match="less than or equal to 8"):
            ProbabilisticModelRequest(model_specifications=model_specs, inference_chains=10)


class TestSessionStatusRequestValidation:
    """Test SessionStatusRequest validation"""

    def test_valid_request(self):
        """Test valid session status request"""
        request = SessionStatusRequest(session_id="valid_session_123", include_details=True)
        assert request.session_id == "valid_session_123"
        assert request.include_details is True

    def test_empty_session_id(self):
        """Test empty session ID"""
        with pytest.raises(ValidationError, match="Session ID cannot be empty"):
            SessionStatusRequest(session_id="")

    def test_invalid_session_id_characters(self):
        """Test session ID with invalid characters"""
        with pytest.raises(ValidationError, match="only contain alphanumeric characters"):
            SessionStatusRequest(session_id="invalid@session")


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    def test_complete_reasoning_workflow(self):
        """Test a complete reasoning workflow with all validation"""
        # Step 1: Knowledge extraction
        knowledge_request = KnowledgeExtractionRequest(
            scenario="A company wants to implement a new employee performance management system",
            extract_types=["entities", "relationships", "constraints", "domain_knowledge"],
        )
        assert knowledge_request.scenario is not None

        # Step 2: MSA reasoning
        reasoning_request = MSAReasoningRequest(
            scenario=knowledge_request.scenario,
            session_id="workflow_session_001",
            context={
                "company_size": "medium",
                "current_system": "manual_reviews",
                "timeline": "6_months",
                "budget_range": "50k_100k",
            },
            mode=MODE_BOTH,
            priority=PRIORITY_HIGH,
            max_execution_time=300,  # 5 minutes for high priority
        )
        assert reasoning_request.session_id == "workflow_session_001"

        # Step 3: Probabilistic model
        probabilistic_request = ProbabilisticModelRequest(
            model_specifications={
                "variables": ["adoption_rate", "performance_improvement", "cost_savings"],
                "distributions": {
                    "adoption_rate": {"type": "beta", "params": [2, 5]},
                    "performance_improvement": {"type": "normal", "params": [0.15, 0.05]},
                    "cost_savings": {"type": "gamma", "params": [2, 10000]},
                },
                "dependencies": {
                    "performance_improvement": ["adoption_rate"],
                    "cost_savings": ["adoption_rate", "performance_improvement"],
                },
            },
            observations={"adoption_rate": 0.8},
            inference_samples=3000,
            inference_chains=4,
            random_seed=123,
        )
        assert probabilistic_request.inference_samples == 3000

        # Step 4: Session status check
        status_request = SessionStatusRequest(session_id="workflow_session_001", include_details=True)
        assert status_request.session_id == reasoning_request.session_id

    def test_security_edge_cases(self):
        """Test various security edge cases"""
        # Test nested dangerous patterns
        with pytest.raises(ValidationError):
            MSAReasoningRequest(
                scenario="Analyze this scenario",
                context={"data": {"nested": {"dangerous": "SELECT password FROM users WHERE id=1"}}},
            )

        # Test mixed content with HTML and dangerous patterns
        with pytest.raises(ValidationError):
            MSAReasoningRequest(scenario="<p>Normal text</p> but also eval('dangerous')")

        # Test boundary conditions
        max_length_scenario = "A" * MAX_SCENARIO_LENGTH
        request = MSAReasoningRequest(scenario=max_length_scenario)
        assert len(request.scenario) == MAX_SCENARIO_LENGTH


@pytest.fixture
def sample_requests():
    """Fixture providing sample valid requests for testing"""
    return {
        "msa_request": MSAReasoningRequest(
            scenario="Evaluate the impact of remote work on team productivity",
            session_id="test_session_001",
            mode=MODE_BOTH,
            priority=PRIORITY_NORMAL,
        ),
        "knowledge_request": KnowledgeExtractionRequest(
            scenario="Extract insights from quarterly sales performance data",
            extract_types=["entities", "relationships", "temporal_patterns"],
        ),
        "probabilistic_request": ProbabilisticModelRequest(
            model_specifications={
                "variables": ["sales_volume", "customer_satisfaction"],
                "priors": {"sales_volume": "normal", "customer_satisfaction": "beta"},
            }
        ),
        "status_request": SessionStatusRequest(session_id="test_session_001", include_details=False),
    }


def test_requests_interoperability(sample_requests):
    """Test that all request types work together properly"""
    # Verify all requests are valid
    for req_name, request in sample_requests.items():
        assert request is not None
        if hasattr(request, "session_id") and request.session_id:
            # Session IDs should be consistent
            assert isinstance(request.session_id, str)
            assert len(request.session_id) <= MAX_SESSION_ID_LENGTH


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
