"""
Test configuration and environment setup
"""

from reasoning_kernel.core.config import settings


class TestConfiguration:
    """Test application configuration"""
    
    def test_settings_exist(self):
        """Test that settings object exists and has required attributes"""
        assert settings is not None
        
        # Test that key configuration attributes exist
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'development')
        
        # Test Redis configuration
        assert hasattr(settings, 'redis_host')
        assert hasattr(settings, 'redis_port')
        assert hasattr(settings, 'redis_db')
        assert hasattr(settings, 'redis_ttl_seconds')
        
        # Test OpenAI configuration attributes
        assert hasattr(settings, 'openai_api_key')
        assert hasattr(settings, 'openai_model')
        
        # Test Azure OpenAI configuration attributes
        assert hasattr(settings, 'azure_openai_api_key')
        assert hasattr(settings, 'azure_openai_endpoint')
        assert hasattr(settings, 'azure_openai_deployment')
        
    def test_redis_defaults(self):
        """Test Redis configuration defaults"""
        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379
        assert settings.redis_db == 0
        assert isinstance(settings.redis_ttl_seconds, int)
        assert settings.redis_ttl_seconds > 0
        
    def test_msa_configuration(self):
        """Test MSA-specific configuration"""
        assert hasattr(settings, 'max_reasoning_steps')
        assert hasattr(settings, 'probabilistic_samples')
        assert hasattr(settings, 'uncertainty_threshold')
        
        # Test reasonable defaults
        assert settings.max_reasoning_steps > 0
        assert settings.probabilistic_samples > 0
        assert 0.0 <= settings.uncertainty_threshold <= 1.0