"""
Centralized configuration management with pydantic-settings
This replaces the scattered configuration across the codebase with a unified approach.
"""

from enum import Enum
from typing import List, Optional

from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

# Load environment from .env files
from reasoning_kernel.core.env import load_project_dotenv


load_project_dotenv()


class EnvironmentType(str, Enum):
    """Application environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Centralized application settings with pydantic-settings validation"""

    # Application metadata
    app_name: str = Field("MSA Reasoning Engine", description="Application name")
    version: str = Field("1.0.0", description="Application version")
    environment: EnvironmentType = Field(EnvironmentType.DEVELOPMENT, description="Environment type")
    debug: bool = Field(False, description="Debug mode")
    development: bool = Field(False, description="Development mode")

    # AI Service Configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: str = Field("gpt-4o", description="Default OpenAI model")
    openai_embedding_model: str = Field("text-embedding-3-small", description="OpenAI embedding model")

    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(None, description="Azure OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(None, description="Azure OpenAI endpoint")
    azure_openai_deployment: Optional[str] = Field(None, description="Azure OpenAI deployment name")
    azure_openai_api_version: str = Field("2024-12-01-preview", description="Azure OpenAI API version")
    azure_embedding_deployment: Optional[str] = Field(None, description="Azure embedding deployment name")

    # Google AI / Gemini Configuration
    google_api_key: Optional[str] = Field(None, description="Google AI API key")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key (alias for google_api_key)")
    gemini_model: str = Field("gemini-2.5-pro", description="Default Gemini model")
    gemini_embedding_model: str = Field("text-embedding-004", description="Gemini embedding model")
    gemini_temperature: float = Field(0.7, ge=0.0, le=2.0, description="Gemini temperature")
    gemini_max_tokens: int = Field(8192, gt=0, description="Gemini max tokens")
    gemini_enable_thinking: bool = Field(True, description="Enable Gemini thinking mode")

    # Redis Configuration
    redis_url: Optional[str] = Field(None, description="Complete Redis URL")
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, ge=1, le=65535, description="Redis port")
    redis_password: Optional[str] = Field(None, description="Redis password")
    redis_db: int = Field(0, ge=0, description="Redis database number")
    redis_ssl: bool = Field(False, description="Use Redis SSL")
    redis_max_connections: int = Field(50, gt=0, description="Max Redis connections")
    redis_ttl_seconds: int = Field(3600, gt=0, description="Default Redis TTL")
    redis_memory_collection: str = Field("msa_knowledge", description="Memory collection name")

    # Daytona Sandbox Configuration
    daytona_api_key: Optional[str] = Field(None, description="Daytona API key")
    daytona_api_url: str = Field("https://app.daytona.io/api", description="Daytona API URL")
    daytona_target: str = Field("us", description="Daytona target region")
    daytona_workspace_id: Optional[str] = Field(None, description="Daytona workspace ID")
    daytona_proxy_url: Optional[str] = Field(None, description="Daytona proxy URL")
    daytona_cpu_limit: int = Field(2, ge=1, le=8, description="CPU cores limit")
    daytona_memory_limit_mb: int = Field(512, ge=256, le=8192, description="Memory limit in MB")
    daytona_execution_timeout: int = Field(30, gt=0, description="Code execution timeout")
    daytona_python_version: str = Field("3.12", description="Python version")
    daytona_enable_networking: bool = Field(False, description="Enable network access")

    # MSA Engine Settings
    max_reasoning_steps: int = Field(10, ge=1, le=100, description="Max reasoning steps")
    max_iterations: int = Field(5, ge=1, le=20, description="Max MSA iterations")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Confidence threshold")
    uncertainty_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Uncertainty threshold")
    probabilistic_samples: int = Field(1000, ge=100, le=10000, description="MCMC samples")
    numpyro_num_chains: int = Field(2, ge=1, le=8, description="NumPyro chain count")
    jax_enable_x64: bool = Field(True, description="Enable JAX 64-bit precision")

    # Performance settings
    reasoning_timeout: int = Field(300, gt=0, description="Reasoning timeout (seconds)")
    knowledge_extraction_timeout: int = Field(120, gt=0, description="Knowledge extraction timeout")
    probabilistic_synthesis_timeout: int = Field(180, gt=0, description="Synthesis timeout")

    # Feature flags
    enable_memory: bool = Field(True, description="Enable memory store")
    enable_plugins: bool = Field(True, description="Enable SK plugins")
    enable_caching: bool = Field(True, description="Enable result caching")
    enable_tracing: bool = Field(False, description="Enable OpenTelemetry tracing")

    # Security Configuration
    api_key_validation: bool = Field(True, description="Enable API key validation")
    rate_limiting: bool = Field(True, description="Enable rate limiting")
    encrypt_memory: bool = Field(False, description="Encrypt memory data")
    cors_origins: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins"
    )
    cors_enabled: bool = Field(True, description="Enable CORS")

    # Monitoring Configuration
    log_level: LogLevel = Field(LogLevel.INFO, description="Logging level")
    structured_logging: bool = Field(True, description="Enable structured logging")
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    enable_telemetry: bool = Field(False, description="Enable telemetry")
    enable_performance_monitoring: bool = Field(False, description="Enable performance monitoring")
    prometheus_port: int = Field(9090, ge=1024, le=65535, description="Prometheus metrics port")

    # External monitoring
    sentry_dsn: Optional[str] = Field(None, description="Sentry DSN")
    datadog_api_key: Optional[str] = Field(None, description="Datadog API key")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse CORS origins from various input formats"""
        if isinstance(v, str):
            # Handle single string values like "*" or comma-separated
            if v == "*":
                return ["*"]
            if "," in v:
                return [origin.strip() for origin in v.split(",")]
            return [v]
        if isinstance(v, list):
            return v
        return ["*"]  # fallback

    @field_validator("redis_url", mode="after")
    @classmethod
    def build_redis_url(cls, v, info):
        """Build Redis URL if not provided"""
        if v:
            return v

        # Build from components if available in the data
        data = info.data
        host = data.get("redis_host", "localhost")
        port = data.get("redis_port", 6379)
        password = data.get("redis_password")
        db = data.get("redis_db", 0)
        ssl = data.get("redis_ssl", False)

        scheme = "rediss" if ssl else "redis"
        auth = f":{password}@" if password else ""

        return f"{scheme}://{auth}{host}:{port}/{db}"

    @model_validator(mode="after")
    def validate_environment_settings(self):
        """Validate environment-specific settings"""
        # Set gemini_api_key as alias for google_api_key if provided
        if self.gemini_api_key and not self.google_api_key:
            self.google_api_key = self.gemini_api_key

        # Production environment validations
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.api_key_validation:
                import warnings

                warnings.warn("API key validation disabled in production")

            # Restrict CORS origins in production
            if "*" in self.cors_origins:
                import warnings

                warnings.warn("Wildcard CORS origins not recommended in production")

        return self

    @model_validator(mode="after")
    def validate_api_keys(self):
        """Ensure at least one AI service is configured"""
        has_openai = bool(self.openai_api_key)
        has_azure = bool(self.azure_openai_api_key and self.azure_openai_endpoint)
        has_google = bool(self.google_api_key or self.gemini_api_key)

        if not (has_openai or has_azure or has_google):
            # Only warn in non-testing environments
            if self.environment != EnvironmentType.TESTING:
                import warnings

                warnings.warn("No AI service API keys configured. Service functionality will be limited.")

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Support nested configuration through environment variables
        # e.g., AZURE_OPENAI_API_KEY maps to azure_openai_api_key
    )


# Factory functions for common configurations
def create_development_settings(**kwargs) -> Settings:
    """Create settings optimized for development"""
    defaults = {
        "environment": EnvironmentType.DEVELOPMENT,
        "debug": True,
        "development": True,
        "log_level": LogLevel.DEBUG,
        "api_key_validation": False,
        "rate_limiting": False,
        "enable_telemetry": False,
    }
    defaults.update(kwargs)
    return Settings(**defaults)


def create_production_settings(**kwargs) -> Settings:
    """Create settings optimized for production"""
    defaults = {
        "environment": EnvironmentType.PRODUCTION,
        "debug": False,
        "development": False,
        "log_level": LogLevel.INFO,
        "api_key_validation": True,
        "rate_limiting": True,
        "encrypt_memory": True,
        "enable_telemetry": True,
        "enable_metrics": True,
        "cors_origins": [],  # Must be explicitly configured
    }
    defaults.update(kwargs)
    return Settings(**defaults)


def create_testing_settings(**kwargs) -> Settings:
    """Create settings optimized for testing"""
    defaults = {
        "environment": EnvironmentType.TESTING,
        "debug": False,
        "development": False,
        "openai_api_key": "test-key",
        "azure_openai_api_key": "test-azure-key",
        "google_api_key": "test-google-key",
        "redis_url": "redis://localhost:6379/1",
        "log_level": LogLevel.WARNING,
        "api_key_validation": False,
        "rate_limiting": False,
        "enable_telemetry": False,
    }
    defaults.update(kwargs)
    return Settings(**defaults)


# Global settings instance
settings = Settings()

# Export commonly used items
__all__ = [
    "Settings",
    "EnvironmentType",
    "LogLevel",
    "settings",
    "create_development_settings",
    "create_production_settings",
    "create_testing_settings",
]
