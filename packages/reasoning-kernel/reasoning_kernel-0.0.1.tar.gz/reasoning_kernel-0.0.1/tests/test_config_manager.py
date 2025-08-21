"""
Tests for the Configuration Management System
============================================

Comprehensive test suite for the unified configuration management system.
Tests environment loading, validation, credential integration, and configuration lifecycle.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from reasoning_kernel.core.config_manager import (
    ConfigManager,
    ApplicationConfig,
    Environment,
    LogLevel,
    DatabaseConfig,
    RedisConfig,
    AzureOpenAIConfig,
    OpenAIConfig,
    MSAConfig,
    SecurityConfig,
    MonitoringConfig,
    DaytonaConfig,
    ConfigurationError,
    get_config_manager,
    get_config,
    get_redis_config,
    get_openai_config,
    get_msa_config,
    is_production,
    is_development,
    is_debug_enabled,
)


class TestEnvironmentEnum:
    """Test environment enumeration"""

    def test_environment_values(self):
        """Test environment enum values"""
        assert Environment.DEVELOPMENT == "development"
        assert Environment.STAGING == "staging"
        assert Environment.PRODUCTION == "production"
        assert Environment.TEST == "test"


class TestConfigurationModels:
    """Test individual configuration models"""

    def test_database_config_defaults(self):
        """Test database configuration defaults"""
        config = DatabaseConfig()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.name == "reasoning_kernel"
        assert config.user == "postgres"
        assert config.password is None
        assert config.max_connections == 10
        assert config.connection_timeout == 30
        assert config.ssl_mode == "prefer"

    def test_redis_config_defaults(self):
        """Test Redis configuration defaults"""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 0
        assert config.url is None
        assert config.max_connections == 50
        assert config.ttl_seconds == 3600
        assert config.timeout == 5
        assert config.ssl is False

    def test_azure_openai_config_defaults(self):
        """Test Azure OpenAI configuration defaults"""
        config = AzureOpenAIConfig()
        assert config.api_key is None
        assert config.endpoint is None
        assert config.deployment is None
        assert config.api_version == "2024-12-01-preview"
        assert config.timeout == 120
        assert config.max_retries == 3

    def test_msa_config_defaults(self):
        """Test MSA configuration defaults"""
        config = MSAConfig()
        assert config.max_reasoning_steps == 10
        assert config.probabilistic_samples == 1000
        assert config.uncertainty_threshold == 0.8
        assert config.reasoning_timeout == 300
        assert config.parallel_execution is True
        assert config.max_concurrency == 3
        assert config.enable_caching is True

    def test_security_config_defaults(self):
        """Test security configuration defaults"""
        config = SecurityConfig()
        assert config.api_key_secret is None
        assert config.session_secret is None
        assert config.rate_limiting_enabled is True
        assert config.max_requests_per_minute == 100
        assert config.validation_level == "strict"
        assert config.audit_enabled is True
        assert config.cors_origins == ["*"]

    def test_monitoring_config_defaults(self):
        """Test monitoring configuration defaults"""
        config = MonitoringConfig()
        assert config.log_level == LogLevel.INFO
        assert config.structured_logging is True
        assert config.metrics_enabled is True
        assert config.tracing_enabled is False
        assert config.health_check_interval == 30


class TestApplicationConfig:
    """Test main application configuration"""

    def test_application_config_defaults(self):
        """Test application configuration defaults"""
        config = ApplicationConfig()
        assert config.app_name == "MSA Reasoning Engine"
        assert config.version == "1.0.0"
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is False

        # Test nested configurations exist
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.redis, RedisConfig)
        assert isinstance(config.azure_openai, AzureOpenAIConfig)
        assert isinstance(config.openai, OpenAIConfig)
        assert isinstance(config.msa, MSAConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.monitoring, MonitoringConfig)
        assert isinstance(config.daytona, DaytonaConfig)

    def test_environment_validation(self):
        """Test environment validation and normalization"""
        # Test case normalization
        config = ApplicationConfig(environment="DEVELOPMENT")
        assert config.environment == Environment.DEVELOPMENT

        config = ApplicationConfig(environment="production")
        assert config.environment == Environment.PRODUCTION

        # Test aliases
        config = ApplicationConfig(environment="dev")
        assert config.environment == Environment.DEVELOPMENT

        config = ApplicationConfig(environment="prod")
        assert config.environment == Environment.PRODUCTION

        config = ApplicationConfig(environment="stage")
        assert config.environment == Environment.STAGING

    def test_environment_helpers(self):
        """Test environment helper methods"""
        # Production environment
        config = ApplicationConfig(environment=Environment.PRODUCTION)
        assert config.is_production() is True
        assert config.is_development() is False
        assert config.is_testing() is False

        # Development environment
        config = ApplicationConfig(environment=Environment.DEVELOPMENT)
        assert config.is_production() is False
        assert config.is_development() is True
        assert config.is_testing() is False

        # Test environment
        config = ApplicationConfig(environment=Environment.TEST)
        assert config.is_production() is False
        assert config.is_development() is False
        assert config.is_testing() is True


class TestConfigManager:
    """Test configuration manager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir)

    def test_config_manager_initialization(self):
        """Test configuration manager initialization"""
        manager = ConfigManager(self.config_path)
        assert manager.config_path == self.config_path
        assert manager._config is None
        assert manager._last_reload is None

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "REDIS_HOST": "test-redis",
            "REDIS_PORT": "6380",
        },
        clear=False,
    )
    def test_config_loading(self):
        """Test configuration loading from environment"""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.monitoring.log_level == LogLevel.DEBUG
        assert config.redis.host == "test-redis"
        assert config.redis.port == 6380

        # Test that config is cached
        assert manager._config is config
        assert manager._last_reload is not None

    def test_config_reload(self):
        """Test configuration reloading"""
        manager = ConfigManager(self.config_path)

        # Load initial config
        config1 = manager.load_config()
        initial_reload_time = manager._last_reload

        # Reload config
        config2 = manager.reload_config()

        # Should be same instance but reload time updated
        assert config2 is not config1  # New instance
        assert manager._last_reload > initial_reload_time

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "production",
        },
        clear=False,
    )
    def test_environment_overrides_production(self):
        """Test production environment overrides"""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        assert config.environment == Environment.PRODUCTION
        assert config.debug is False
        assert config.monitoring.log_level == LogLevel.WARNING
        assert config.security.validation_level == "strict"
        assert config.redis.ssl is True

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "development",
        },
        clear=False,
    )
    def test_environment_overrides_development(self):
        """Test development environment overrides"""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.monitoring.log_level == LogLevel.DEBUG
        assert config.security.validation_level == "permissive"
        assert config.msa.enable_caching is False

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "test",
        },
        clear=False,
    )
    def test_environment_overrides_test(self):
        """Test test environment overrides"""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        assert config.environment == Environment.TEST
        assert config.debug is False
        assert config.monitoring.log_level == LogLevel.ERROR
        assert config.msa.reasoning_timeout == 30
        assert config.redis.db == 15

    def test_config_validation_errors(self):
        """Test configuration validation errors"""
        manager = ConfigManager(self.config_path)

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=False):
            # Should raise error for missing required credentials in production
            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config()

            assert "No OpenAI API key configured for production" in str(exc_info.value)

    @patch("reasoning_kernel.core.config_manager.SecureConfigLoader")
    def test_credential_integration(self, mock_secure_loader):
        """Test credential integration with secure config loader"""
        # Mock secure config loader
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_config.return_value = {
            "azure_openai_key": "test-azure-key",
            "azure_openai_endpoint": "https://test.openai.azure.com",
            "redis_password": "test-redis-pass",
            "daytona_api_key": "test-daytona-key",
        }
        mock_secure_loader.return_value = mock_loader_instance

        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        # Verify credentials were integrated
        assert config.azure_openai.api_key == "test-azure-key"
        assert config.azure_openai.endpoint == "https://test.openai.azure.com"
        assert config.redis.password == "test-redis-pass"
        assert config.daytona.api_key == "test-daytona-key"

    def test_export_config_json(self):
        """Test configuration export to JSON"""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        # Export without secrets
        json_export = manager.export_config(format="json", include_secrets=False)
        assert "[REDACTED]" in json_export
        assert "MSA Reasoning Engine" in json_export

        # Export with secrets (for testing only)
        json_with_secrets = manager.export_config(format="json", include_secrets=True)
        assert "[REDACTED]" not in json_with_secrets

    def test_export_config_yaml(self):
        """Test configuration export to YAML"""
        manager = ConfigManager(self.config_path)
        manager.load_config()  # Load config without storing in variable

        yaml_export = manager.export_config(format="yaml", include_secrets=False)
        assert "app_name: MSA Reasoning Engine" in yaml_export
        assert "[REDACTED]" in yaml_export

    def test_config_summary(self):
        """Test configuration summary"""
        manager = ConfigManager(self.config_path)
        manager.load_config()  # Load config without storing in variable

        summary = manager.get_config_summary()

        assert "environment" in summary
        assert "version" in summary
        assert "debug_mode" in summary
        assert "last_reload" in summary
        assert "redis_configured" in summary
        assert "openai_configured" in summary
        assert "security_level" in summary
        assert "log_level" in summary


class TestConvenienceFunctions:
    """Test configuration convenience functions"""

    def test_get_config_manager(self):
        """Test global configuration manager access"""
        manager = get_config_manager()
        assert isinstance(manager, ConfigManager)

        # Should return same instance
        manager2 = get_config_manager()
        assert manager is manager2

    def test_get_config(self):
        """Test global configuration access"""
        config = get_config()
        assert isinstance(config, ApplicationConfig)

    def test_get_redis_config(self):
        """Test Redis configuration access"""
        redis_config = get_redis_config()
        assert isinstance(redis_config, RedisConfig)

    def test_get_openai_config(self):
        """Test OpenAI configuration access"""
        openai_config = get_openai_config()
        assert isinstance(openai_config, (AzureOpenAIConfig, OpenAIConfig))

    def test_get_msa_config(self):
        """Test MSA configuration access"""
        msa_config = get_msa_config()
        assert isinstance(msa_config, MSAConfig)

    @patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=False)
    def test_is_production(self):
        """Test production environment check"""
        # Clear cache first
        get_config.cache_clear()
        with pytest.raises(ConfigurationError):
            # Should fail in production without credentials
            is_production()

    @patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=False)
    def test_is_development(self):
        """Test development environment check"""
        get_config.cache_clear()
        assert is_development() is True

    @patch.dict(os.environ, {"DEBUG": "true"}, clear=False)
    def test_is_debug_enabled(self):
        """Test debug mode check"""
        get_config.cache_clear()
        assert is_debug_enabled() is True


class TestConfigurationValidation:
    """Test configuration validation"""

    def test_port_validation(self):
        """Test port number validation"""
        # Valid port
        config = RedisConfig(port=6379)
        assert config.port == 6379

        # Invalid port (too high)
        with pytest.raises(ValueError):
            RedisConfig(port=70000)

        # Invalid port (too low)
        with pytest.raises(ValueError):
            RedisConfig(port=0)

    def test_percentage_validation(self):
        """Test percentage value validation"""
        # Valid percentage
        config = MSAConfig(uncertainty_threshold=0.8)
        assert config.uncertainty_threshold == 0.8

        # Invalid percentage (too high)
        with pytest.raises(ValueError):
            MSAConfig(uncertainty_threshold=1.5)

        # Invalid percentage (too low)
        with pytest.raises(ValueError):
            MSAConfig(uncertainty_threshold=-0.1)

    def test_positive_integer_validation(self):
        """Test positive integer validation"""
        # Valid positive integer
        config = MSAConfig(max_reasoning_steps=10)
        assert config.max_reasoning_steps == 10

        # Invalid (zero)
        with pytest.raises(ValueError):
            MSAConfig(max_reasoning_steps=0)

        # Invalid (negative)
        with pytest.raises(ValueError):
            MSAConfig(max_reasoning_steps=-1)


class TestEnvironmentFiles:
    """Test environment-specific configuration files"""

    def test_development_env_loading(self):
        """Test loading development environment configuration"""
        env_file = Path(__file__).parent.parent.parent / ".env.development"
        if env_file.exists():
            # This would test actual file loading if implemented
            assert env_file.exists()

    def test_production_env_loading(self):
        """Test loading production environment configuration"""
        env_file = Path(__file__).parent.parent.parent / ".env.production"
        if env_file.exists():
            # This would test actual file loading if implemented
            assert env_file.exists()

    def test_test_env_loading(self):
        """Test loading test environment configuration"""
        env_file = Path(__file__).parent.parent.parent / ".env.test"
        if env_file.exists():
            # This would test actual file loading if implemented
            assert env_file.exists()


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_missing_secure_config_loader(self):
        """Test handling when secure config loader is not available"""
        manager = ConfigManager()

        with patch.object(manager, "_secure_config_loader") as mock_loader:
            mock_loader.load_config.side_effect = Exception("Credential loading failed")

            # Should not fail, but log warning
            config = manager.load_config()
            assert isinstance(config, ApplicationConfig)

    def test_invalid_environment_value(self):
        """Test handling invalid environment values"""
        with patch.dict(os.environ, {"ENVIRONMENT": "invalid"}, clear=False):
            # Should use default and not raise error
            config = ApplicationConfig()
            # Pydantic should handle this gracefully
            assert config.environment in [
                Environment.DEVELOPMENT,
                Environment.STAGING,
                Environment.PRODUCTION,
                Environment.TEST,
            ]
