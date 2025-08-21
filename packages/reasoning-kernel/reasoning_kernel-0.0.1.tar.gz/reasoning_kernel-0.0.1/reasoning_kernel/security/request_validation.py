"""
Enhanced Request Validation Middleware for MSA Reasoning Kernel

Provides comprehensive request validation and sanitization:
- Input validation and sanitization
- Request size limits
- Content type validation
- Parameter validation
- SQL injection prevention
- XSS prevention
- Path traversal protection
"""

from dataclasses import dataclass
import html
import json
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import unquote

import bleach
from fastapi import Request
from fastapi.responses import JSONResponse
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.security.audit_logging import audit_logger
from reasoning_kernel.security.audit_logging import AuditEventType
from reasoning_kernel.security.audit_logging import AuditSeverity
from starlette.middleware.base import BaseHTTPMiddleware


logger = get_logger(__name__)


@dataclass
class ValidationRule:
    """Request validation rule configuration"""

    # Size limits
    max_request_size_mb: float = 10.0
    max_json_depth: int = 10
    max_array_length: int = 1000
    max_string_length: int = 10000

    # Content validation
    allowed_content_types: Set[str] = None
    required_headers: Set[str] = None

    # Security validation
    enable_sql_injection_check: bool = True
    enable_xss_check: bool = True
    enable_path_traversal_check: bool = True
    enable_command_injection_check: bool = True

    # Parameter validation
    max_query_params: int = 50
    max_path_params: int = 10
    max_header_size: int = 8192

    def __post_init__(self):
        if self.allowed_content_types is None:
            self.allowed_content_types = {
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain",
            }

        if self.required_headers is None:
            self.required_headers = set()


class SecurityValidator:
    """Security-focused input validation"""

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(?i)\bunion\s+select\b",
        r"(?i)\bselect\s+.*\bfrom\b",
        r"(?i)\binsert\s+into\b",
        r"(?i)\bdelete\s+from\b",
        r"(?i)\bdrop\s+table\b",
        r"(?i)\bupdate\s+.*\bset\b",
        r"(?i);\s*(drop|delete|insert|update|select)",
        r"(?i)\b(exec|execute)\b",
        r"(?i)\bsp_\w+",
        r"(?i)\bxp_\w+",
        r"--[^\r\n]*",
        r"/\*.*?\*/",
        r"(?i)\bunion\b.*\ball\b.*\bselect\b",
        r"(?i)\bor\s+1\s*=\s*1\b",
        r"(?i)\bor\s+\w+\s*=\s*\w+\b",
        r"(?i)'\s*(or|and)\s*'[^']*'\s*=\s*'",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"(?i)<script[^>]*>.*?</script>",
        r"(?i)<iframe[^>]*>.*?</iframe>",
        r"(?i)<object[^>]*>.*?</object>",
        r"(?i)<embed[^>]*>.*?</embed>",
        r"(?i)<link[^>]*>",
        r"(?i)<meta[^>]*>",
        r"(?i)<style[^>]*>.*?</style>",
        r"(?i)javascript:",
        r"(?i)vbscript:",
        r"(?i)data:text/html",
        r"(?i)on\w+\s*=\s*['\"][^'\"]*['\"]",
        r"(?i)expression\s*\(",
        r"(?i)url\s*\(\s*['\"]?javascript:",
        r"(?i)<[^>]*\s+on\w+\s*=",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\.[\\/]",
        r"[\\/]\.\.[\\/]",
        r"\.\.[\\/]\.\.[\\/]",
        r"~[\\/]",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"\.\.%2f",
        r"\.\.%5c",
        r"%252e%252e%252f",
        r"..%252f",
        r"..%255c",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"(?i)\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ping|nslookup|dig|curl|wget)\b",
        r"(?i)\b(rm|mv|cp|mkdir|rmdir|chmod|chown)\b",
        r"(?i)\b(sh|bash|zsh|csh|ksh|dash|fish)\b",
        r"(?i)\b(python|perl|ruby|php|node|java|gcc|g\+\+|make)\b",
        r"(?i)\b(sudo|su|passwd|mount|umount)\b",
        r"(?i)\b(nc|netcat|telnet|ssh|ftp|sftp)\b",
    ]

    @classmethod
    def check_sql_injection(cls, text: str) -> List[str]:
        """Check for SQL injection patterns"""
        violations = []

        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text):
                violations.append(f"SQL injection pattern detected: {pattern}")

        return violations

    @classmethod
    def check_xss(cls, text: str) -> List[str]:
        """Check for XSS patterns"""
        violations = []

        # Decode URL encoding first
        decoded_text = unquote(text)

        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, decoded_text):
                violations.append(f"XSS pattern detected: {pattern}")

        return violations

    @classmethod
    def check_path_traversal(cls, text: str) -> List[str]:
        """Check for path traversal patterns"""
        violations = []

        # Check both original and URL-decoded text
        texts_to_check = [text, unquote(text)]

        for check_text in texts_to_check:
            for pattern in cls.PATH_TRAVERSAL_PATTERNS:
                if re.search(pattern, check_text):
                    violations.append(f"Path traversal pattern detected: {pattern}")

        return violations

    @classmethod
    def check_command_injection(cls, text: str) -> List[str]:
        """Check for command injection patterns"""
        violations = []

        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                violations.append(f"Command injection pattern detected: {pattern}")

        return violations

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML content"""
        # Allow only safe HTML tags and attributes
        allowed_tags = ["p", "br", "strong", "em", "u", "ol", "ul", "li", "h1", "h2", "h3", "h4", "h5", "h6"]
        allowed_attributes = {}

        return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    @classmethod
    def sanitize_string(cls, text: str, max_length: int = 10000) -> str:
        """General string sanitization"""
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]

        # HTML escape
        text = html.escape(text)

        # Remove null bytes
        text = text.replace("\x00", "")

        return text


class RequestSizeValidator:
    """Validates request size limits"""

    @staticmethod
    async def validate_request_size(request: Request, max_size_bytes: int) -> bool:
        """Validate total request size"""
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                size = int(content_length)
                return size <= max_size_bytes
            except ValueError:
                return False

        # If no content-length header, we'll check during body reading
        return True

    @staticmethod
    def validate_json_structure(
        data: Any, max_depth: int = 10, max_array_length: int = 1000, current_depth: int = 0
    ) -> List[str]:
        """Validate JSON structure limits"""
        violations = []

        if current_depth > max_depth:
            violations.append(f"JSON depth exceeds limit: {max_depth}")
            return violations

        if isinstance(data, dict):
            for key, value in data.items():
                violations.extend(
                    RequestSizeValidator.validate_json_structure(value, max_depth, max_array_length, current_depth + 1)
                )

        elif isinstance(data, list):
            if len(data) > max_array_length:
                violations.append(f"Array length exceeds limit: {max_array_length}")

            for item in data:
                violations.extend(
                    RequestSizeValidator.validate_json_structure(item, max_depth, max_array_length, current_depth + 1)
                )

        return violations


class ContentValidator:
    """Validates request content and format"""

    @staticmethod
    def validate_content_type(request: Request, allowed_types: Set[str]) -> bool:
        """Validate request content type"""
        content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()

        if not content_type and request.method in ["GET", "DELETE", "HEAD"]:
            return True  # No content type required for these methods

        return content_type in allowed_types

    @staticmethod
    def validate_required_headers(request: Request, required_headers: Set[str]) -> List[str]:
        """Validate required headers are present"""
        missing_headers = []

        for header in required_headers:
            if header.lower() not in [h.lower() for h in request.headers.keys()]:
                missing_headers.append(header)

        return missing_headers


class ParameterValidator:
    """Validates request parameters"""

    @staticmethod
    def validate_query_params(request: Request, max_params: int, max_value_length: int) -> List[str]:
        """Validate query parameters"""
        violations = []

        query_params = dict(request.query_params)

        if len(query_params) > max_params:
            violations.append(f"Too many query parameters: {len(query_params)} > {max_params}")

        for key, value in query_params.items():
            if len(str(value)) > max_value_length:
                violations.append(f"Query parameter '{key}' value too long: {len(value)} > {max_value_length}")

        return violations

    @staticmethod
    def validate_path_params(request: Request, max_params: int) -> List[str]:
        """Validate path parameters"""
        violations = []

        path_params = getattr(request, "path_params", {})

        if len(path_params) > max_params:
            violations.append(f"Too many path parameters: {len(path_params)} > {max_params}")

        return violations


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Comprehensive request validation middleware"""

    def __init__(self, app, validation_rules: Optional[ValidationRule] = None):
        super().__init__(app)
        self.rules = validation_rules or ValidationRule()
        self.security_validator = SecurityValidator()

        # Endpoint-specific rules can be added here
        self.endpoint_rules: Dict[str, ValidationRule] = {}

    def add_endpoint_rule(self, endpoint_pattern: str, rule: ValidationRule):
        """Add endpoint-specific validation rule"""
        self.endpoint_rules[endpoint_pattern] = rule

    def get_validation_rule(self, endpoint: str) -> ValidationRule:
        """Get validation rule for endpoint"""
        for pattern, rule in self.endpoint_rules.items():
            if re.match(pattern, endpoint):
                return rule
        return self.rules

    async def dispatch(self, request: Request, call_next):
        """Process request with comprehensive validation"""

        try:
            # Get validation rules for this endpoint
            endpoint = request.url.path
            rules = self.get_validation_rule(endpoint)

            # Validate request
            violations = await self._validate_request(request, rules)

            if violations:
                # Log security violation
                await audit_logger.log_security_event(
                    AuditEventType.SECURITY_VIOLATION,
                    message="Request validation failed",
                    client_ip=self._get_client_ip(request),
                    details={"violations": violations, "endpoint": endpoint, "method": request.method},
                )

                # Return validation error
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Request validation failed",
                        "message": "The request contains invalid or potentially malicious content",
                        "type": "validation_error",
                        "violations": violations[:10],  # Limit exposure
                    },
                )

            # Process request
            response = await call_next(request)
            return response

        except Exception as e:
            logger.error(f"Request validation middleware error: {e}")

            # Log the error but don't block the request
            await audit_logger.log_event(
                {
                    "event_type": AuditEventType.API_ERROR,
                    "severity": AuditSeverity.HIGH,
                    "message": f"Validation middleware error: {str(e)}",
                    "client_ip": self._get_client_ip(request),
                    "details": {"error": str(e)},
                }
            )

            # Continue with request
            return await call_next(request)

    async def _validate_request(self, request: Request, rules: ValidationRule) -> List[str]:
        """Perform comprehensive request validation"""
        violations = []

        # 1. Size validation
        max_size_bytes = int(rules.max_request_size_mb * 1024 * 1024)
        if not await RequestSizeValidator.validate_request_size(request, max_size_bytes):
            violations.append(f"Request size exceeds limit: {rules.max_request_size_mb}MB")

        # 2. Content type validation
        if not ContentValidator.validate_content_type(request, rules.allowed_content_types):
            content_type = request.headers.get("content-type", "none")
            violations.append(f"Invalid content type: {content_type}")

        # 3. Required headers validation
        missing_headers = ContentValidator.validate_required_headers(request, rules.required_headers)
        if missing_headers:
            violations.extend([f"Missing required header: {h}" for h in missing_headers])

        # 4. Parameter validation
        violations.extend(
            ParameterValidator.validate_query_params(request, rules.max_query_params, rules.max_string_length)
        )
        violations.extend(ParameterValidator.validate_path_params(request, rules.max_path_params))

        # 5. Header size validation
        for name, value in request.headers.items():
            if len(f"{name}: {value}") > rules.max_header_size:
                violations.append(f"Header too large: {name}")

        # 6. Security validation on URL and parameters
        url_path = request.url.path
        query_string = str(request.query_params)

        if rules.enable_sql_injection_check:
            violations.extend(self.security_validator.check_sql_injection(url_path))
            violations.extend(self.security_validator.check_sql_injection(query_string))

        if rules.enable_xss_check:
            violations.extend(self.security_validator.check_xss(url_path))
            violations.extend(self.security_validator.check_xss(query_string))

        if rules.enable_path_traversal_check:
            violations.extend(self.security_validator.check_path_traversal(url_path))
            violations.extend(self.security_validator.check_path_traversal(query_string))

        if rules.enable_command_injection_check:
            violations.extend(self.security_validator.check_command_injection(url_path))
            violations.extend(self.security_validator.check_command_injection(query_string))

        # 7. Body validation (if present)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Try to read body for validation
                body = await request.body()
                if body:
                    violations.extend(await self._validate_body(body, rules))

                # Re-create request body for downstream processing
                # Note: This is a simplified approach; in production you might use
                # a different strategy to avoid consuming the body twice
                request._body = body

            except Exception as e:
                violations.append(f"Failed to read request body: {str(e)}")

        return violations

    async def _validate_body(self, body: bytes, rules: ValidationRule) -> List[str]:
        """Validate request body content"""
        violations = []

        try:
            # Check body size
            if len(body) > rules.max_request_size_mb * 1024 * 1024:
                violations.append(f"Body size exceeds limit: {rules.max_request_size_mb}MB")
                return violations  # Don't process further if too large

            # Try to parse as JSON for structure validation
            try:
                json_data = json.loads(body.decode("utf-8"))
                violations.extend(
                    RequestSizeValidator.validate_json_structure(
                        json_data, rules.max_json_depth, rules.max_array_length
                    )
                )

                # Validate JSON content security
                json_str = json.dumps(json_data)
                violations.extend(self._validate_text_security(json_str, rules))

            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON, validate as text
                try:
                    text_content = body.decode("utf-8")
                    violations.extend(self._validate_text_security(text_content, rules))
                except UnicodeDecodeError:
                    # Binary content - skip text-based security checks
                    pass

        except Exception as e:
            violations.append(f"Body validation error: {str(e)}")

        return violations

    def _validate_text_security(self, text: str, rules: ValidationRule) -> List[str]:
        """Validate text content for security issues"""
        violations = []

        if rules.enable_sql_injection_check:
            violations.extend(self.security_validator.check_sql_injection(text))

        if rules.enable_xss_check:
            violations.extend(self.security_validator.check_xss(text))

        if rules.enable_path_traversal_check:
            violations.extend(self.security_validator.check_path_traversal(text))

        if rules.enable_command_injection_check:
            violations.extend(self.security_validator.check_command_injection(text))

        return violations

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# Factory functions for different validation levels
def create_strict_validation_middleware() -> RequestValidationMiddleware:
    """Create middleware with strict validation rules"""
    rules = ValidationRule(
        max_request_size_mb=5.0,
        max_json_depth=5,
        max_array_length=500,
        max_string_length=5000,
        max_query_params=20,
        enable_sql_injection_check=True,
        enable_xss_check=True,
        enable_path_traversal_check=True,
        enable_command_injection_check=True,
    )
    return RequestValidationMiddleware(app=None, validation_rules=rules)


def create_relaxed_validation_middleware() -> RequestValidationMiddleware:
    """Create middleware with relaxed validation rules"""
    rules = ValidationRule(
        max_request_size_mb=50.0,
        max_json_depth=15,
        max_array_length=5000,
        max_string_length=50000,
        max_query_params=100,
        enable_sql_injection_check=True,
        enable_xss_check=True,
        enable_path_traversal_check=True,
        enable_command_injection_check=False,  # May interfere with code execution endpoints
    )
    return RequestValidationMiddleware(app=None, validation_rules=rules)


# Input sanitization utilities
class InputSanitizer:
    """Utility class for input sanitization"""

    @staticmethod
    def sanitize_for_storage(data: Any) -> Any:
        """Sanitize data for safe storage"""
        if isinstance(data, str):
            return SecurityValidator.sanitize_string(data)
        elif isinstance(data, dict):
            return {key: InputSanitizer.sanitize_for_storage(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer.sanitize_for_storage(item) for item in data]
        else:
            return data

    @staticmethod
    def sanitize_for_display(data: Any) -> Any:
        """Sanitize data for safe display"""
        if isinstance(data, str):
            return SecurityValidator.sanitize_html(data)
        elif isinstance(data, dict):
            return {key: InputSanitizer.sanitize_for_display(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer.sanitize_for_display(item) for item in data]
        else:
            return data
