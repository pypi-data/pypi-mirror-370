"""
Application configuration using environment variables
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


def get_env_with_fallback(
    primary_key: str, fallback_key: str, default: str = ""
) -> str:
    """Get environment variable with fallback to another key"""
    return os.getenv(primary_key, os.getenv(fallback_key, default))


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application metadata
    version: str = os.getenv("APP_VERSION", "1.0.0")
    app_name: str = "MSA Reasoning Engine"

    # Azure OpenAI Configuration (required)
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
    )

    # OpenAI (non-Azure) compatibility fields expected by tests
    # These may mirror Azure settings if standard OpenAI not used
    openai_api_key: str = get_env_with_fallback(
        "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", default=""
    )
    openai_model: str = get_env_with_fallback(
        "OPENAI_MODEL", "AZURE_OPENAI_DEPLOYMENT", default=""
    )

    # Application Settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    development: bool = os.getenv("DEVELOPMENT", "false").lower() == "true"
    # Explicit environment name used by runtime guards (e.g., CORS wildcard restriction)
    # Expected values: "development", "staging", "production" (case-insensitive)
    environment: str = os.getenv("ENVIRONMENT", "development")

    # MSA Engine Settings
    max_reasoning_steps: int = int(os.getenv("MAX_REASONING_STEPS", "10"))
    probabilistic_samples: int = int(os.getenv("PROBABILISTIC_SAMPLES", "1000"))
    uncertainty_threshold: float = float(os.getenv("UNCERTAINTY_THRESHOLD", "0.8"))

    # Redis Configuration
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_ttl_seconds: int = int(os.getenv("REDIS_TTL_SECONDS", "3600"))
    redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")  # Comma-separated list

    # Pydantic v2 Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
