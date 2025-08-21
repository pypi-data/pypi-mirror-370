"""
Security Configuration and Integration Module for MSA Reasoning Kernel

Provides centralized security configuration and integration:
- Security middleware orchestration
- Configuration management
- Security headers setup
- CORS configuration
- Security monitoring
- Integration with FastAPI
"""

from dataclasses import dataclass
from dataclasses import field
import os
from typing import Any, Dict, List, Optional, Set

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.middleware.rate_limiting import RateLimitMiddleware
from reasoning_kernel.security.api_key_manager import APIKeyManager
from reasoning_kernel.security.audit_logging import AuditLogger
from reasoning_kernel.security.audit_logging import AuditMiddleware
from reasoning_kernel.security.request_validation import (
    create_relaxed_validation_middleware,
)
from reasoning_kernel.security.request_validation import (
    create_strict_validation_middleware,
)
from reasoning_kernel.security.request_validation import (
    RequestValidationMiddleware,
)
from reasoning_kernel.security.request_validation import ValidationRule
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware


logger = get_logger(__name__)


@dataclass
class SecurityConfig:
    """Comprehensive security configuration"""

    # Environment
    environment: str = "production"
    debug_mode: bool = False

    # API Security
    api_key_enabled: bool = True
    api_key_redis_url: str = "redis://localhost:6379/1"
    require_api_key_for_all: bool = False  # If True, all endpoints require API key

    # Rate Limiting
    rate_limiting_enabled: bool = True
    rate_limiting_redis_url: str = "redis://localhost:6379/0"

    # Request Validation
    request_validation_enabled: bool = True
    validation_level: str = "strict"  # "strict" or "relaxed"

    # Audit Logging
    audit_logging_enabled: bool = True
    audit_redis_url: str = "redis://localhost:6379/2"
    audit_file_path: Optional[str] = "logs/audit.jsonl"

    # HTTPS and Security Headers
    force_https: bool = True
    allowed_hosts: Set[str] = field(default_factory=lambda: {"*"})
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "strict"

    # CORS Configuration
    cors_enabled: bool = True
    cors_allow_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_allow_headers: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = False

    # Content Security Policy
    content_security_policy: Optional[str] = None

    # Security Headers
    security_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
    )

    # Endpoint Security
    public_endpoints: Set[str] = field(
        default_factory=lambda: {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}
    )
    admin_endpoints: Set[str] = field(default_factory=lambda: {"/admin", "/circuit-breakers", "/api-keys"})

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create configuration from environment variables"""

        def get_bool(key: str, default: bool) -> bool:
            value = os.getenv(key, "").lower()
            if value in ("true", "1", "yes", "on"):
                return True
            elif value in ("false", "0", "no", "off"):
                return False
            return default

        def get_list(key: str, default: List[str]) -> List[str]:
            value = os.getenv(key, "")
            if value:
                return [item.strip() for item in value.split(",")]
            return default

        def get_set(key: str, default: Set[str]) -> Set[str]:
            return set(get_list(key, list(default)))

        return cls(
            environment=os.getenv("ENVIRONMENT", "production"),
            debug_mode=get_bool("DEBUG", False),
            # API Security
            api_key_enabled=get_bool("API_KEY_ENABLED", True),
            api_key_redis_url=os.getenv("API_KEY_REDIS_URL", "redis://localhost:6379/1"),
            require_api_key_for_all=get_bool("REQUIRE_API_KEY_ALL", False),
            # Rate Limiting
            rate_limiting_enabled=get_bool("RATE_LIMITING_ENABLED", True),
            rate_limiting_redis_url=os.getenv("RATE_LIMITING_REDIS_URL", "redis://localhost:6379/0"),
            # Request Validation
            request_validation_enabled=get_bool("REQUEST_VALIDATION_ENABLED", True),
            validation_level=os.getenv("VALIDATION_LEVEL", "strict"),
            # Audit Logging
            audit_logging_enabled=get_bool("AUDIT_LOGGING_ENABLED", True),
            audit_redis_url=os.getenv("AUDIT_REDIS_URL", "redis://localhost:6379/2"),
            audit_file_path=os.getenv("AUDIT_FILE_PATH", "logs/audit.jsonl"),
            # HTTPS and Security
            force_https=get_bool("FORCE_HTTPS", True),
            allowed_hosts=get_set("ALLOWED_HOSTS", {"*"}),
            session_cookie_secure=get_bool("SESSION_COOKIE_SECURE", True),
            # CORS
            cors_enabled=get_bool("CORS_ENABLED", True),
            cors_allow_origins=get_list("CORS_ALLOW_ORIGINS", ["*"]),
            cors_allow_methods=get_list("CORS_ALLOW_METHODS", ["GET", "POST", "PUT", "DELETE"]),
            cors_allow_headers=get_list("CORS_ALLOW_HEADERS", ["*"]),
            cors_allow_credentials=get_bool("CORS_ALLOW_CREDENTIALS", False),
            # CSP
            content_security_policy=os.getenv("CONTENT_SECURITY_POLICY"),
            # Public/Admin endpoints
            public_endpoints=get_set("PUBLIC_ENDPOINTS", {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}),
            admin_endpoints=get_set("ADMIN_ENDPOINTS", {"/admin", "/circuit-breakers", "/api-keys"}),
        )


class SecurityHeadersMiddleware:
    """Middleware for adding security headers"""

    def __init__(self, app, security_headers: Dict[str, str], csp: Optional[str] = None):
        self.app = app
        self.security_headers = security_headers
        self.csp = csp

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                # Add security headers
                for name, value in self.security_headers.items():
                    headers[name.encode()] = value.encode()

                # Add CSP header if configured
                if self.csp:
                    headers[b"content-security-policy"] = self.csp.encode()

                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)


class SecurityManager:
    """Central security management for the application"""

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig.from_env()
        self.api_key_manager: Optional[APIKeyManager] = None
        self.audit_logger: Optional[AuditLogger] = None
        self.initialized = False

    async def initialize(self):
        """Initialize security components"""
        if self.initialized:
            return

        logger.info("Initializing security manager...")

        # Initialize API key manager
        if self.config.api_key_enabled:
            self.api_key_manager = APIKeyManager(self.config.api_key_redis_url)
            await self.api_key_manager.initialize()
            logger.info("API key manager initialized")

        # Initialize audit logger
        if self.config.audit_logging_enabled:
            self.audit_logger = AuditLogger(
                redis_url=self.config.audit_redis_url, file_path=self.config.audit_file_path
            )
            await self.audit_logger.initialize()
            logger.info("Audit logger initialized")

        self.initialized = True
        logger.info("Security manager initialization complete")

    def configure_app(self, app: FastAPI):
        """Configure FastAPI application with security middleware"""

        logger.info("Configuring application security...")

        # Add security middleware in correct order (reverse of execution order)

        # 1. HTTPS Redirect (if enabled and not in debug mode)
        if self.config.force_https and not self.config.debug_mode:
            app.add_middleware(HTTPSRedirectMiddleware)
            logger.info("HTTPS redirect middleware added")

        # 2. Trusted Host middleware
        if self.config.allowed_hosts and "*" not in self.config.allowed_hosts:
            app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(self.config.allowed_hosts))
            logger.info(f"Trusted host middleware added: {self.config.allowed_hosts}")

        # 3. Security Headers middleware
        app.add_middleware(
            SecurityHeadersMiddleware,
            security_headers=self.config.security_headers,
            csp=self.config.content_security_policy,
        )
        logger.info("Security headers middleware added")

        # 4. CORS middleware (if enabled)
        if self.config.cors_enabled:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_allow_origins,
                allow_credentials=self.config.cors_allow_credentials,
                allow_methods=self.config.cors_allow_methods,
                allow_headers=self.config.cors_allow_headers,
            )
            logger.info("CORS middleware added")

        # 5. Session middleware (for admin functionality)
        session_secret = os.getenv("SESSION_SECRET", "change-me-in-production")
        if session_secret == "change-me-in-production" and self.config.environment == "production":
            logger.warning("Default session secret detected in production environment!")

        # Starlette's SessionMiddleware doesn't accept 'secure' and 'httponly' kwargs; they are set via cookie params.
        app.add_middleware(
            SessionMiddleware,
            secret_key=session_secret,
            session_cookie="session",
            max_age=3600,  # 1 hour
            same_site=self.config.session_cookie_samesite,
        )
        logger.info("Session middleware added")

        # 6. Request Validation middleware
        if self.config.request_validation_enabled:
            if self.config.validation_level == "strict":
                validation_middleware = create_strict_validation_middleware()
            else:
                validation_middleware = create_relaxed_validation_middleware()

            # Add custom rules for admin endpoints
            admin_rule = ValidationRule(
                max_request_size_mb=1.0,
                enable_sql_injection_check=True,
                enable_xss_check=True,
                enable_path_traversal_check=True,
                enable_command_injection_check=True,
            )

            for endpoint in self.config.admin_endpoints:
                validation_middleware.add_endpoint_rule(f"{endpoint}.*", admin_rule)

            app.add_middleware(RequestValidationMiddleware, validation_rules=validation_middleware.rules)
            logger.info(f"Request validation middleware added ({self.config.validation_level} mode)")

        # 7. Rate Limiting middleware
        if self.config.rate_limiting_enabled:
            app.add_middleware(RateLimitMiddleware, redis_url=self.config.rate_limiting_redis_url)
            logger.info("Rate limiting middleware added")

        # 8. Audit Logging middleware (outermost for complete request tracking)
        if self.config.audit_logging_enabled and self.audit_logger:
            app.add_middleware(AuditMiddleware, audit_logger=self.audit_logger)
            logger.info("Audit logging middleware added")

        # Add security-related exception handlers
        self._add_exception_handlers(app)

        logger.info("Application security configuration complete")

    def _add_exception_handlers(self, app: FastAPI):
        """Add security-related exception handlers"""

        @app.exception_handler(HTTPException)
        async def security_http_exception_handler(request: Request, exc: HTTPException):
            """Handle HTTP exceptions with security logging"""

            # Log security-relevant HTTP errors
            if exc.status_code in [401, 403, 429]:
                if self.audit_logger:
                    from reasoning_kernel.security.audit_logging import (
                        AuditEventType,
                    )
                    from reasoning_kernel.security.audit_logging import (
                        AuditSeverity,
                    )

                    event_type = {
                        401: AuditEventType.AUTH_FAILURE,
                        403: AuditEventType.ACCESS_DENIED,
                        429: AuditEventType.RATE_LIMIT_EXCEEDED,
                    }.get(exc.status_code, AuditEventType.API_ERROR)

                    await self.audit_logger.log_event(
                        {
                            "event_type": event_type,
                            "severity": AuditSeverity.MEDIUM,
                            "message": f"HTTP {exc.status_code}: {exc.detail}",
                            "client_ip": self._get_client_ip(request),
                            "endpoint": request.url.path,
                            "method": request.method,
                            "details": {"status_code": exc.status_code, "detail": exc.detail},
                        }
                    )

            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail, "type": "http_error", "status_code": exc.status_code},
            )

        @app.exception_handler(Exception)
        async def security_general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions with security logging"""

            if self.audit_logger:
                from reasoning_kernel.security.audit_logging import (
                    AuditEventType,
                )
                from reasoning_kernel.security.audit_logging import (
                    AuditSeverity,
                )

                await self.audit_logger.log_event(
                    {
                        "event_type": AuditEventType.API_ERROR,
                        "severity": AuditSeverity.HIGH,
                        "message": f"Unhandled exception: {str(exc)}",
                        "client_ip": self._get_client_ip(request),
                        "endpoint": request.url.path,
                        "method": request.method,
                        "details": {"exception_type": type(exc).__name__, "exception_message": str(exc)},
                    }
                )

            # Don't expose internal error details in production
            if self.config.debug_mode:
                detail = str(exc)
            else:
                detail = "Internal server error"

            return JSONResponse(
                status_code=500, content={"error": detail, "type": "internal_error", "status_code": 500}
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def create_default_admin_key(self) -> Optional[str]:
        """Create default admin API key for initial setup"""

        if not self.api_key_manager:
            return None

        try:
            from reasoning_kernel.security.api_key_manager import (
                APIKeyPermissions,
            )
            from reasoning_kernel.security.api_key_manager import UserRole

            # Check if any admin keys exist
            existing_keys = await self.api_key_manager.list_api_keys()
            admin_keys = [k for k in existing_keys if k.user_role == UserRole.ADMIN]

            if admin_keys:
                logger.info("Admin API keys already exist")
                return None

            # Create admin permissions
            admin_permissions = APIKeyPermissions(
                can_access_reasoning=True,
                can_access_msa=True,
                can_access_admin=True,
                can_access_health=True,
                can_read=True,
                can_write=True,
                can_delete=True,
                max_concurrent_requests=100,
            )

            # Create admin API key
            api_key, metadata = await self.api_key_manager.create_api_key(
                name="Default Admin Key",
                description="Initial admin API key for system setup",
                user_role=UserRole.ADMIN,
                permissions=admin_permissions,
                expires_in_days=365,  # 1 year expiration
            )

            logger.info(f"Created default admin API key: {metadata.key_id}")
            return api_key

        except Exception as e:
            logger.error(f"Failed to create default admin API key: {e}")
            return None

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security configuration status"""

        return {
            "environment": self.config.environment,
            "security_features": {
                "api_key_enabled": self.config.api_key_enabled,
                "rate_limiting_enabled": self.config.rate_limiting_enabled,
                "request_validation_enabled": self.config.request_validation_enabled,
                "audit_logging_enabled": self.config.audit_logging_enabled,
                "https_enforced": self.config.force_https,
                "cors_enabled": self.config.cors_enabled,
            },
            "validation_level": self.config.validation_level,
            "public_endpoints": list(self.config.public_endpoints),
            "admin_endpoints": list(self.config.admin_endpoints),
            "security_headers": list(self.config.security_headers.keys()),
            "initialized": self.initialized,
        }


# Global security manager instance
security_manager = SecurityManager()


# Convenience function for FastAPI integration
async def setup_security(app: FastAPI, config: Optional[SecurityConfig] = None) -> SecurityManager:
    """Setup security for FastAPI application"""

    global security_manager

    if config:
        security_manager = SecurityManager(config)

    # Initialize security components
    await security_manager.initialize()

    # Configure the application
    security_manager.configure_app(app)

    # Create default admin key if needed
    admin_key = await security_manager.create_default_admin_key()
    if admin_key:
        logger.warning(f"🔑 Default Admin API Key Created: {admin_key}")
        logger.warning("⚠️  Please save this key securely and create additional admin keys before revoking this one!")

    return security_manager


# Development helper function
def create_development_config() -> SecurityConfig:
    """Create security configuration suitable for development"""

    return SecurityConfig(
        environment="development",
        debug_mode=True,
        force_https=False,
        cors_allow_origins=["*"],
        cors_allow_credentials=True,
        validation_level="relaxed",
        session_cookie_secure=False,
        allowed_hosts={"*"},
    )


# Production helper function
def create_production_config() -> SecurityConfig:
    """Create security configuration suitable for production"""

    return SecurityConfig(
        environment="production",
        debug_mode=False,
        force_https=True,
        require_api_key_for_all=True,
        validation_level="strict",
        session_cookie_secure=True,
        cors_allow_origins=[],  # Must be explicitly configured
        cors_allow_credentials=False,
        allowed_hosts=set(),  # Must be explicitly configured
    )
