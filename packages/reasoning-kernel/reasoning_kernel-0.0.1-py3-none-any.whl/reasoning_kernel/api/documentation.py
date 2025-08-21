"""
OpenAPI Documentation Enhancement

Provides utilities for generating comprehensive OpenAPI documentation:
- Schema generation with examples
- Error response documentation
- Performance metadata
- API versioning information
- Interactive documentation features
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class APIStatus(str, Enum):
    """API endpoint status"""

    STABLE = "stable"
    BETA = "beta"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


class PerformanceLevel(str, Enum):
    """Expected performance levels"""

    FAST = "fast"  # < 100ms
    MODERATE = "moderate"  # 100ms - 1s
    SLOW = "slow"  # 1s - 10s
    BATCH = "batch"  # > 10s


class APIMetadata(BaseModel):
    """Extended metadata for API endpoints"""

    status: APIStatus = APIStatus.STABLE
    version_added: str = "1.0.0"
    version_deprecated: Optional[str] = None
    performance_level: PerformanceLevel = PerformanceLevel.MODERATE
    rate_limit: Optional[str] = None
    cache_ttl: Optional[int] = None
    requires_auth: bool = True
    cost_tier: Optional[str] = None  # For usage-based pricing

    # Usage information
    expected_request_size: Optional[str] = None
    expected_response_size: Optional[str] = None
    batch_supported: bool = False
    streaming_supported: bool = False

    # Dependencies and limitations
    external_dependencies: List[str] = Field(default_factory=list)
    known_limitations: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class APIDocumentationEnhancer:
    """Enhances FastAPI OpenAPI documentation with additional features"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.endpoint_metadata: Dict[str, APIMetadata] = {}
        self.common_errors = self._define_common_errors()

    def _define_common_errors(self) -> Dict[int, Dict[str, Any]]:
        """Define common error responses"""
        return {
            400: {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "VALIDATION_ERROR",
                            "message": "Invalid request parameters",
                            "details": {"field": "parameter_name", "issue": "required field missing"},
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
            401: {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "AUTHENTICATION_REQUIRED",
                            "message": "Valid API key required",
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
            403: {
                "description": "Forbidden",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "INSUFFICIENT_PERMISSIONS",
                            "message": "Access denied for this resource",
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
            404: {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "RESOURCE_NOT_FOUND",
                            "message": "The requested resource does not exist",
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
            429: {
                "description": "Rate Limit Exceeded",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "RATE_LIMIT_EXCEEDED",
                            "message": "Rate limit exceeded. Please try again later.",
                            "details": {"limit": "100/hour", "reset_time": "2025-01-27T11:00:00Z"},
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
            500: {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "INTERNAL_ERROR",
                            "message": "An internal server error occurred",
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
            503: {
                "description": "Service Unavailable",
                "content": {
                    "application/json": {
                        "schema": ErrorResponse.model_json_schema(),
                        "example": {
                            "error": "SERVICE_UNAVAILABLE",
                            "message": "Service temporarily unavailable. Please try again later.",
                            "details": {"retry_after": "60s"},
                            "request_id": "req_123456789",
                            "timestamp": "2025-01-27T10:30:00Z",
                        },
                    }
                },
            },
        }

    def add_endpoint_metadata(self, path: str, method: str, metadata: APIMetadata):
        """Add metadata for a specific endpoint"""
        key = f"{method.upper()}:{path}"
        self.endpoint_metadata[key] = metadata

    def add_reasoning_endpoint_metadata(self):
        """Add metadata for reasoning endpoints"""

        # Main reasoning endpoint
        self.add_endpoint_metadata(
            "/api/v1/reason",
            "POST",
            APIMetadata(
                status=APIStatus.STABLE,
                version_added="1.0.0",
                performance_level=PerformanceLevel.SLOW,
                rate_limit="30 requests/minute",
                cache_ttl=600,
                expected_request_size="1-10KB",
                expected_response_size="5-50KB",
                external_dependencies=["Azure OpenAI", "Redis"],
                known_limitations=[
                    "Complex reasoning scenarios may take 10-30 seconds",
                    "Token limits apply based on model context window",
                ],
            ),
        )

        # V2 reasoning endpoint
        self.add_endpoint_metadata(
            "/api/v2/reasoning/reason",
            "POST",
            APIMetadata(
                status=APIStatus.STABLE,
                version_added="2.0.0",
                performance_level=PerformanceLevel.MODERATE,
                rate_limit="60 requests/minute",
                cache_ttl=300,
                streaming_supported=True,
                expected_request_size="1-5KB",
                expected_response_size="2-20KB",
                external_dependencies=["Azure OpenAI", "Redis"],
                known_limitations=[
                    "Streaming responses require WebSocket connection",
                    "Maximum reasoning depth is 10 stages",
                ],
            ),
        )

        # Knowledge extraction
        self.add_endpoint_metadata(
            "/api/v1/extract-knowledge",
            "POST",
            APIMetadata(
                status=APIStatus.STABLE,
                version_added="1.0.0",
                performance_level=PerformanceLevel.MODERATE,
                rate_limit="100 requests/minute",
                cache_ttl=900,
                expected_request_size="0.5-5KB",
                expected_response_size="1-10KB",
                external_dependencies=["Azure OpenAI"],
                batch_supported=True,
            ),
        )

        # Health endpoints
        self.add_endpoint_metadata(
            "/api/v1/health",
            "GET",
            APIMetadata(
                status=APIStatus.STABLE,
                version_added="1.0.0",
                performance_level=PerformanceLevel.FAST,
                rate_limit="1000 requests/minute",
                cache_ttl=60,
                requires_auth=False,
                expected_response_size="< 1KB",
            ),
        )

    def enhance_openapi_schema(self) -> Dict[str, Any]:
        """Generate enhanced OpenAPI schema"""

        if not self.app.openapi_schema:
            openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description,
                routes=self.app.routes,
            )

            # Add custom extensions
            openapi_schema = self._add_custom_extensions(openapi_schema)

            # Add error responses to all endpoints
            self._add_error_responses(openapi_schema)

            # Add performance information
            self._add_performance_info(openapi_schema)

            # Add authentication information
            self._add_auth_info(openapi_schema)

            # Add examples
            self._add_comprehensive_examples(openapi_schema)

            self.app.openapi_schema = openapi_schema

        return self.app.openapi_schema

    def _add_custom_extensions(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Add custom OpenAPI extensions"""

        # Add API metadata
        schema["x-api-features"] = {
            "caching": "Redis-based response caching with configurable TTL",
            "rate_limiting": "Per-IP and per-API-key rate limiting",
            "batching": "Request batching for improved performance",
            "streaming": "WebSocket streaming for real-time updates",
            "monitoring": "Comprehensive metrics and health checks",
            "security": "API key authentication with role-based access",
        }

        # Add performance information
        schema["x-performance"] = {
            "response_times": {
                "fast": "< 100ms (health checks, cached responses)",
                "moderate": "100ms - 1s (knowledge extraction, simple reasoning)",
                "slow": "1s - 10s (complex reasoning, model synthesis)",
                "batch": "> 10s (batch processing, heavy computations)",
            },
            "throughput": {
                "health_endpoints": "1000+ req/min",
                "reasoning_endpoints": "30-60 req/min",
                "admin_endpoints": "100+ req/min",
            },
        }

        # Add infrastructure information
        schema["x-infrastructure"] = {
            "dependencies": {
                "azure_openai": "Primary LLM service for reasoning",
                "redis": "Caching and session management",
                "postgresql": "Persistent data storage",
            },
            "regions": ["US East", "EU West"],
            "availability": "99.9% uptime SLA",
        }

        return schema

    def _add_error_responses(self, schema: Dict[str, Any]):
        """Add common error responses to all endpoints"""

        if "paths" not in schema:
            return

        for path, path_data in schema["paths"].items():
            for method, method_data in path_data.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    if "responses" not in method_data:
                        method_data["responses"] = {}

                    # Add common error responses
                    for status_code, error_info in self.common_errors.items():
                        if str(status_code) not in method_data["responses"]:
                            method_data["responses"][str(status_code)] = error_info

    def _add_performance_info(self, schema: Dict[str, Any]):
        """Add performance information to endpoints"""

        if "paths" not in schema:
            return

        for path, path_data in schema["paths"].items():
            for method, method_data in path_data.items():
                method_key = f"{method.upper()}:{path}"

                if method_key in self.endpoint_metadata:
                    metadata = self.endpoint_metadata[method_key]

                    # Add performance extension
                    method_data["x-performance"] = {
                        "level": metadata.performance_level.value,
                        "cache_ttl": metadata.cache_ttl,
                        "expected_request_size": metadata.expected_request_size,
                        "expected_response_size": metadata.expected_response_size,
                        "external_dependencies": metadata.external_dependencies,
                    }

                    # Add rate limiting info
                    if metadata.rate_limit:
                        method_data["x-rate-limit"] = metadata.rate_limit

                    # Add feature flags
                    method_data["x-features"] = {
                        "batch_supported": metadata.batch_supported,
                        "streaming_supported": metadata.streaming_supported,
                        "requires_auth": metadata.requires_auth,
                    }

                    # Add limitations
                    if metadata.known_limitations:
                        method_data["x-limitations"] = metadata.known_limitations

    def _add_auth_info(self, schema: Dict[str, Any]):
        """Add authentication information"""

        # Add security schemes
        if "components" not in schema:
            schema["components"] = {}

        schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication. Get your key from the admin panel.",
            }
        }

        # Add security requirements to endpoints that need auth
        if "paths" not in schema:
            return

        for path, path_data in schema["paths"].items():
            for method, method_data in path_data.items():
                method_key = f"{method.upper()}:{path}"

                if method_key in self.endpoint_metadata:
                    metadata = self.endpoint_metadata[method_key]
                    if metadata.requires_auth:
                        method_data["security"] = [{"ApiKeyAuth": []}]

    def _add_comprehensive_examples(self, schema: Dict[str, Any]):
        """Add comprehensive examples to the schema"""

        examples = {
            "reasoning_request": {
                "scenario": "A chess player needs to decide their next move",
                "context": "Current board position: White King on e1, Black King on e8...",
                "reasoning_type": "strategic_analysis",
                "max_steps": 5,
            },
            "knowledge_extraction_request": {
                "text": "Quantum computing uses quantum bits that can exist in superposition",
                "extract_types": ["concepts", "relationships", "facts"],
            },
            "error_response_validation": {
                "error": "VALIDATION_ERROR",
                "message": "Missing required field: scenario",
                "details": {"field": "scenario", "issue": "required"},
                "request_id": "req_abc123",
                "timestamp": "2025-01-27T10:30:00Z",
            },
        }

        if "components" not in schema:
            schema["components"] = {}

        schema["components"]["examples"] = examples

    def generate_api_reference_markdown(self) -> str:
        """Generate comprehensive API reference in Markdown format"""

        md_content = [
            "# MSA Reasoning Kernel API Reference\n",
            f"Generated on: {datetime.now().isoformat()}\n",
            "## Overview\n",
            "The MSA Reasoning Kernel provides advanced AI reasoning capabilities through a RESTful API.\n",
            "### Key Features\n",
            "- Multi-stage reasoning pipeline\n",
            "- Knowledge extraction and synthesis\n",
            "- Real-time streaming responses\n",
            "- Comprehensive caching and rate limiting\n",
            "- Circuit breaker pattern for reliability\n\n",
            "## Authentication\n",
            "All API endpoints (except health checks) require authentication using an API key:\n",
            "```\n",
            "X-API-Key: your_api_key_here\n",
            "```\n\n",
            "## Rate Limits\n",
            "| Endpoint Type | Rate Limit | Burst Allowance |\n",
            "|---------------|------------|------------------|\n",
            "| Health | 1000/min | 1500/min |\n",
            "| Reasoning | 30/min | 45/min |\n",
            "| Knowledge | 100/min | 150/min |\n",
            "| Admin | 100/min | 150/min |\n\n",
            "## Response Caching\n",
            "Responses are cached based on request content with the following TTL:\n",
            "- Health endpoints: 1 minute\n",
            "- Reasoning endpoints: 10 minutes\n",
            "- Knowledge extraction: 15 minutes\n",
            "- Admin endpoints: 30 seconds\n\n",
        ]

        # Add endpoint documentation
        for endpoint_key, metadata in self.endpoint_metadata.items():
            method, path = endpoint_key.split(":", 1)
            md_content.extend(
                [
                    f"### {method} {path}\n",
                    f"**Status**: {metadata.status.value}\n",
                    f"**Performance**: {metadata.performance_level.value}\n",
                    f"**Rate Limit**: {metadata.rate_limit or 'None'}\n",
                    f"**Cache TTL**: {metadata.cache_ttl or 'No caching'}s\n",
                    f"**Authentication Required**: {'Yes' if metadata.requires_auth else 'No'}\n\n",
                ]
            )

            if metadata.external_dependencies:
                md_content.extend(
                    ["**Dependencies**:\n", *[f"- {dep}\n" for dep in metadata.external_dependencies], "\n"]
                )

            if metadata.known_limitations:
                md_content.extend(
                    ["**Limitations**:\n", *[f"- {limitation}\n" for limitation in metadata.known_limitations], "\n"]
                )

        return "".join(md_content)


def create_enhanced_docs(app: FastAPI) -> APIDocumentationEnhancer:
    """Create enhanced documentation for the FastAPI app"""

    enhancer = APIDocumentationEnhancer(app)
    enhancer.add_reasoning_endpoint_metadata()

    # Override the default OpenAPI generation
    def custom_openapi():
        return enhancer.enhance_openapi_schema()

    app.openapi = custom_openapi

    return enhancer
