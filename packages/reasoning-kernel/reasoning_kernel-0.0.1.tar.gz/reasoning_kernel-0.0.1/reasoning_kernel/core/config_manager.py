"""
Unified Configuration Management System
======================================

Centralized configuration management for the MSA Reasoning Kernel.
Provides environment-specific configurations, validation, hot-reload capabilities,
and integration with existing credential management systems.

Features:
- Environment-specific configurations (dev/staging/prod)
- Type-safe configuration with Pydantic models
- Configuration validation and error reporting
- Hot-reload capabilities for development
- Secure credential integration
- Configuration change monitoring
- Default value management
- Configuration export/import utilities
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import yaml
from enum import Enum
from datetime import datetime
from functools import lru_cache

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import structlog

from reasoning_kernel.core.constants import (
    DEFAULT_CACHE_TTL,
    MAX_CACHE_TTL,
    DEFAULT_REASONING_TIMEOUT,
    MAX_EXECUTION_TIMEOUT,
    DEFAULT_INFERENCE_SAMPLES,
    MAX_INFERENCE_SAMPLES,
    MIN_INFERENCE_SAMPLES,
    MAX_RETRY_ATTEMPTS,
)
from reasoning_kernel.security.credential_manager import SecureConfigLoader
from reasoning_kernel.core.error_handling import simple_log_error

logger = structlog.get_logger(__name__)


class Environment(str, Enum):
    """Supported runtime environments"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(str, Enum):
    """Supported logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """Database configuration settings"""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port", ge=1, le=65535)
    name: str = Field(default="reasoning_kernel", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: Optional[str] = Field(default=None, description="Database password")
    max_connections: int = Field(default=10, ge=1, le=100)
    connection_timeout: int = Field(default=30, ge=5, le=300)
    ssl_mode: str = Field(default="prefer", description="SSL connection mode")


class RedisConfig(BaseModel):
    """Redis configuration settings"""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port", ge=1, le=65535)
    password: Optional[str] = Field(default=None, description="Redis password")
    db: int = Field(default=0, description="Redis database number", ge=0, le=15)
    url: Optional[str] = Field(default=None, description="Complete Redis URL")
    max_connections: int = Field(default=50, ge=5, le=200)
    ttl_seconds: int = Field(default=DEFAULT_CACHE_TTL, ge=60, le=MAX_CACHE_TTL)
    timeout: int = Field(default=5, ge=1, le=30)
    ssl: bool = Field(default=False, description="Enable SSL connection")


class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration settings"""

    api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    deployment: Optional[str] = Field(default=None, description="Model deployment name")
    api_version: str = Field(default="2024-12-01-preview", description="API version")
    timeout: int = Field(default=120, ge=10, le=600)
    max_retries: int = Field(default=MAX_RETRY_ATTEMPTS, ge=1, le=10)


class OpenAIConfig(BaseModel):
    """Standard OpenAI configuration settings"""

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(default="gpt-4", description="Default model name")
    timeout: int = Field(default=120, ge=10, le=600)
    max_retries: int = Field(default=MAX_RETRY_ATTEMPTS, ge=1, le=10)


class MSAConfig(BaseModel):
    """MSA Engine configuration settings"""

    max_reasoning_steps: int = Field(default=10, ge=1, le=50)
    probabilistic_samples: int = Field(
        default=DEFAULT_INFERENCE_SAMPLES, ge=MIN_INFERENCE_SAMPLES, le=MAX_INFERENCE_SAMPLES
    )
    uncertainty_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    reasoning_timeout: int = Field(default=DEFAULT_REASONING_TIMEOUT, ge=30, le=MAX_EXECUTION_TIMEOUT)
    parallel_execution: bool = Field(default=True, description="Enable parallel pipeline execution")
    max_concurrency: int = Field(default=3, ge=1, le=8)
    enable_caching: bool = Field(default=True, description="Enable result caching")


class SecurityConfig(BaseModel):
    """Security configuration settings"""

    api_key_secret: Optional[str] = Field(default=None, description="API key encryption secret")
    session_secret: Optional[str] = Field(default=None, description="Session signing secret")
    rate_limiting_enabled: bool = Field(default=True, description="Enable rate limiting")
    max_requests_per_minute: int = Field(default=100, ge=1, le=10000)
    validation_level: str = Field(default="strict", description="Input validation level")
    audit_enabled: bool = Field(default=True, description="Enable security auditing")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration"""

    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    structured_logging: bool = Field(default=True, description="Enable structured logging")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    tracing_enabled: bool = Field(default=False, description="Enable distributed tracing")
    health_check_interval: int = Field(default=30, ge=10, le=300)


class DaytonaConfig(BaseModel):
    """Daytona sandbox configuration"""

    api_key: Optional[str] = Field(default=None, description="Daytona API key")
    api_url: str = Field(default="https://api.daytona.io/v1", description="Daytona API URL")
    timeout: int = Field(default=30, ge=5, le=300)
    max_sandboxes: int = Field(default=5, ge=1, le=20)
    default_memory: str = Field(default="2GB", description="Default sandbox memory")
    default_cpu: str = Field(default="1", description="Default sandbox CPU")


class ApplicationConfig(BaseSettings):
    """
    Main application configuration combining all subsystems.

    This is the primary configuration class that brings together all
    configuration subsystems into a single, validated configuration object.
    """

    # Application metadata
    app_name: str = Field(default="MSA Reasoning Engine", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Runtime environment")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Configuration subsystems
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    azure_openai: AzureOpenAIConfig = Field(default_factory=AzureOpenAIConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    msa: MSAConfig = Field(default_factory=MSAConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    daytona: DaytonaConfig = Field(default_factory=DaytonaConfig)

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        # Enable environment variable reading
        validate_default=True,
    )

    @validator("environment", pre=True)
    def validate_environment(cls, v):
        """Validate and normalize environment value"""
        if isinstance(v, str):
            v = v.lower()
            if v in ["dev", "develop"]:
                return Environment.DEVELOPMENT
            elif v in ["stage", "staging"]:
                return Environment.STAGING
            elif v in ["prod", "production"]:
                return Environment.PRODUCTION
            elif v in ["test", "testing"]:
                return Environment.TEST

        # Validate against enum values
        try:
            return Environment(v)
        except ValueError:
            # Default to development for invalid values
            return Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT

    def is_testing(self) -> bool:
        """Check if running in test environment"""
        return self.environment == Environment.TEST


class ConfigManager:
    """
    Central configuration manager providing configuration lifecycle management.

    Features:
    - Environment-specific configuration loading
    - Configuration validation and error reporting
    - Hot-reload capabilities for development
    - Configuration change monitoring
    - Integration with credential management
    - Configuration export/import utilities
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd()
        self._config: Optional[ApplicationConfig] = None
        self._secure_config_loader = SecureConfigLoader()
        self._last_reload = None
        self._watchers = []

    @property
    def config(self) -> ApplicationConfig:
        """Get current configuration, loading if necessary"""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def load_config(self, reload: bool = False) -> ApplicationConfig:
        """
        Load configuration from environment and files.

        Args:
            reload: Force reload even if already loaded

        Returns:
            Validated application configuration
        """
        if self._config is not None and not reload:
            return self._config

        try:
            # Load base configuration from environment
            config = ApplicationConfig()

            # Integrate with credential manager for sensitive values
            self._integrate_credentials(config)

            # Apply environment-specific overrides
            self._apply_environment_overrides(config)

            # Validate configuration
            self._validate_configuration(config)

            self._config = config
            self._last_reload = datetime.now()

            logger.info(
                "Configuration loaded successfully",
                environment=config.environment.value,
                version=config.version,
                debug_mode=config.debug,
            )

            return config

        except Exception as e:
            simple_log_error(logger, "load_config", e)
            raise ConfigurationError(f"Configuration loading failed: {e}") from e

    def _integrate_credentials(self, config: ApplicationConfig) -> None:
        """Integrate secure credential management"""
        try:
            # Load credentials from secure config loader
            secure_config = self._secure_config_loader.load_config()

            # Azure OpenAI credentials
            if not config.azure_openai.api_key:
                config.azure_openai.api_key = secure_config.get("azure_openai_key")
            if not config.azure_openai.endpoint:
                config.azure_openai.endpoint = secure_config.get("azure_openai_endpoint")
            if not config.azure_openai.deployment:
                config.azure_openai.deployment = secure_config.get("azure_openai_deployment")

            # OpenAI credentials
            if not config.openai.api_key:
                # Fallback to Azure key if standard OpenAI not configured
                config.openai.api_key = secure_config.get("openai_api_key") or secure_config.get("azure_openai_key")

            # Redis credentials
            if not config.redis.password:
                config.redis.password = secure_config.get("redis_password")

            # Daytona credentials
            if not config.daytona.api_key:
                config.daytona.api_key = secure_config.get("daytona_api_key")

            # Note: Security secrets are handled by environment variables
            # and don't need to be loaded from secure config

        except Exception as e:
            simple_log_error(logger, "integrate_credentials", e)

    def _apply_environment_overrides(self, config: ApplicationConfig) -> None:
        """Apply environment-specific configuration overrides"""
        env = config.environment

        if env == Environment.PRODUCTION:
            # Production overrides
            config.debug = False
            config.monitoring.log_level = LogLevel.WARNING
            config.security.validation_level = "strict"
            config.redis.ssl = True

        elif env == Environment.DEVELOPMENT:
            # Development overrides
            config.debug = True
            config.monitoring.log_level = LogLevel.DEBUG
            config.security.validation_level = "permissive"
            config.msa.enable_caching = False  # Disable caching in dev for testing

        elif env == Environment.TEST:
            # Test overrides
            config.debug = False
            config.monitoring.log_level = LogLevel.ERROR
            config.msa.reasoning_timeout = 30  # Faster tests
            config.redis.db = 15  # Use separate test database

    def _validate_configuration(self, config: ApplicationConfig) -> None:
        """Validate configuration for completeness and correctness"""
        errors = []
        warnings = []

        # Check required credentials in production
        if config.is_production():
            if not config.azure_openai.api_key and not config.openai.api_key:
                errors.append("No OpenAI API key configured for production")
            if not config.security.api_key_secret:
                errors.append("No API key secret configured for production")
            if not config.security.session_secret:
                errors.append("No session secret configured for production")

        # Validate Redis configuration
        if config.redis.url and (config.redis.host != "localhost" or config.redis.port != 6379):
            warnings.append("Both Redis URL and host/port specified, URL will take precedence")

        # Validate MSA settings
        if config.msa.max_concurrency > 8:
            warnings.append("High concurrency setting may impact performance")

        # Log validation results
        if errors:
            error_msg = "; ".join(errors)
            simple_log_error(logger, "validate_configuration", error_msg, errors=errors)
            raise ConfigurationError(f"Configuration validation failed: {error_msg}")

        if warnings:
            logger.warning("Configuration validation warnings", warnings=warnings)

    def reload_config(self) -> ApplicationConfig:
        """Reload configuration from sources"""
        logger.info("Reloading configuration")
        return self.load_config(reload=True)

    async def watch_config_changes(self, callback=None):
        """Watch for configuration file changes and auto-reload"""
        if not self.config.is_development():
            logger.info("Configuration watching disabled in non-development environment")
            return

        # Implementation would use file system watchers
        # This is a placeholder for the hot-reload capability
        logger.info("Configuration file watching started")

    def export_config(self, format: str = "json", include_secrets: bool = False) -> str:
        """Export current configuration to string format"""
        config_dict = self.config.dict()

        if not include_secrets:
            # Remove sensitive fields
            sensitive_fields = [
                "azure_openai.api_key",
                "openai.api_key",
                "redis.password",
                "daytona.api_key",
                "security.api_key_secret",
                "security.session_secret",
            ]

            for field_path in sensitive_fields:
                parts = field_path.split(".")
                current = config_dict
                for part in parts[:-1]:
                    if part in current:
                        current = current[part]
                if parts[-1] in current:
                    current[parts[-1]] = "[REDACTED]"

        if format.lower() == "yaml":
            return yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
        else:
            return json.dumps(config_dict, indent=2, default=str)

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration state"""
        return {
            "environment": self.config.environment.value,
            "version": self.config.version,
            "debug_mode": self.config.debug,
            "last_reload": self._last_reload.isoformat() if self._last_reload else None,
            "redis_configured": bool(self.config.redis.url or self.config.redis.host),
            "openai_configured": bool(self.config.azure_openai.api_key or self.config.openai.api_key),
            "daytona_configured": bool(self.config.daytona.api_key),
            "security_level": self.config.security.validation_level,
            "log_level": self.config.monitoring.log_level.value,
        }


class ConfigurationError(Exception):
    """Configuration-related errors"""

    pass


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


@lru_cache(maxsize=1)
def get_config() -> ApplicationConfig:
    """Get the current application configuration (cached)"""
    return get_config_manager().config


# Convenience functions for common configuration access patterns
def get_redis_config() -> RedisConfig:
    """Get Redis configuration"""
    return get_config().redis


def get_openai_config() -> Union[AzureOpenAIConfig, OpenAIConfig]:
    """Get OpenAI configuration (Azure preferred)"""
    config = get_config()
    if config.azure_openai.api_key:
        return config.azure_openai
    return config.openai


def get_msa_config() -> MSAConfig:
    """Get MSA engine configuration"""
    return get_config().msa


def is_production() -> bool:
    """Check if running in production environment"""
    return get_config().is_production()


def is_development() -> bool:
    """Check if running in development environment"""
    return get_config().is_development()


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return get_config().debug
