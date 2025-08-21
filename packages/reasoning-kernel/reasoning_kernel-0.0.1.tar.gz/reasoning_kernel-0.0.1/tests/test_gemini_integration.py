"""
Test GEMINI integration functionality and configuration
"""

import pytest
import os
from unittest.mock import patch

from reasoning_kernel.reasoning_kernel import ReasoningConfig

class TestGeminiIntegration:
    """Test GEMINI model integration with the reasoning engine"""

    def test_default_gemini_models(self):
        """Test that default configuration uses GEMINI models"""
        config = ReasoningConfig()
        
        assert config.parse_model == "gemini-2.5-pro"
        assert config.synthesis_model == "gemini-2.5-pro"
        assert config.graph_model == "phi-4-reasoning"  # phi-4-reasoning is used for the graph stage because, as of now, GEMINI models do not provide the required graph reasoning capabilities; this specialized model is integrated to ensure optimal performance for graph-based reasoning tasks, even within the GEMINI integration theme.

    def test_custom_gemini_models(self):
        """Test custom GEMINI model configuration"""
        config = ReasoningConfig(
            parse_model="gemini-2.5-flash",
            synthesis_model="gemini-1.5-pro"
        )
        
        assert config.parse_model == "gemini-2.5-flash"
        assert config.synthesis_model == "gemini-1.5-pro"

    def test_fallback_models_configuration(self):
        """Test fallback model configuration for reliability"""
        config = ReasoningConfig(
            fallback_models={
                "parse": "gemini-1.5-pro",
                "synthesis": "gemini-1.5-flash"
            }
        )
        
        assert config.fallback_models["parse"] == "gemini-1.5-pro"
        assert config.fallback_models["synthesis"] == "gemini-1.5-flash"

    @patch.dict(os.environ, {
        'GOOGLE_AI_API_KEY': 'test_api_key_123',
        'GOOGLE_AI_GEMINI_MODEL_ID': 'gemini-2.5-pro',
        'GOOGLE_AI_EMBEDDING_MODEL_ID': 'text-embedding-004'
    })
    def test_environment_configuration(self):
        """Test that environment variables are properly loaded"""
        # Note: This tests the pattern, actual env loading happens in semantic kernel
        
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        model_id = os.getenv('GOOGLE_AI_GEMINI_MODEL_ID')
        embedding_model = os.getenv('GOOGLE_AI_EMBEDDING_MODEL_ID')
        
        assert api_key == 'test_api_key_123'
        assert model_id == 'gemini-2.5-pro'
        assert embedding_model == 'text-embedding-004'

    def test_performance_configuration(self):
        """Test GEMINI-optimized performance settings"""
        config = ReasoningConfig(
            parse_model="gemini-2.5-flash",  # Faster variant
            synthesis_model="gemini-2.5-pro", # High quality
            timeout_per_stage=180,  # Reasonable timeout for GEMINI
            enable_thinking_mode=True,
            thinking_detail_level="detailed"
        )
        
        assert config.timeout_per_stage == 180
        assert config.enable_thinking_mode is True
        assert config.thinking_detail_level == "detailed"

    def test_gemini_model_variants(self):
        """Test that various GEMINI model names are supported"""
        valid_models = [
            "gemini-2.5-pro",
            "gemini-2.5-flash", 
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
        
        for model in valid_models:
            config = ReasoningConfig(
                parse_model=model,
                synthesis_model=model
            )
            assert config.parse_model == model
            assert config.synthesis_model == model

    def test_production_configuration(self):
        """Test production-ready GEMINI configuration"""
        production_config = ReasoningConfig(
            parse_model="gemini-2.5-pro",
            synthesis_model="gemini-2.5-pro",
            max_retries=2,
            timeout_per_stage=300,
            enable_parallel_processing=True,
            fallback_models={
                "parse": "gemini-2.5-flash",
                "synthesis": "gemini-1.5-pro"
            }
        )
        
        assert production_config.max_retries == 2
        assert production_config.timeout_per_stage == 300
        assert production_config.enable_parallel_processing is True
        assert production_config.fallback_models is not None

    @pytest.mark.asyncio
    async def test_reasoning_config_serialization(self):
        """Test that GEMINI configurations can be serialized/deserialized"""
        from dataclasses import asdict
        
        config = ReasoningConfig(
            parse_model="gemini-2.5-pro",
            synthesis_model="gemini-2.5-flash",
            thinking_detail_level="moderate"
        )
        
        config_dict = asdict(config)
        
        assert config_dict["parse_model"] == "gemini-2.5-pro"
        assert config_dict["synthesis_model"] == "gemini-2.5-flash"
        assert config_dict["thinking_detail_level"] == "moderate"

    def test_domain_specific_configurations(self):
        """Test domain-specific GEMINI model configurations"""
        
        # Finance analysis configuration
        finance_config = ReasoningConfig(
            parse_model="gemini-2.5-pro",
            synthesis_model="gemini-2.5-pro",
            inference_samples=2000,  # Higher precision for financial models
            thinking_detail_level="detailed"
        )
        
        # Manufacturing optimization configuration
        manufacturing_config = ReasoningConfig(
            parse_model="gemini-2.5-flash",  # Faster for operational decisions
            synthesis_model="gemini-2.5-pro",  # Detailed for optimization
            timeout_per_stage=120,  # Faster response required
            enable_parallel_processing=True
        )
        
        assert finance_config.inference_samples == 2000
        assert finance_config.thinking_detail_level == "detailed"
        
        assert manufacturing_config.parse_model == "gemini-2.5-flash"
        assert manufacturing_config.timeout_per_stage == 120

class TestGeminiDocumentationExamples:
    """Test that code examples from GEMINI.md documentation work correctly"""

    def test_basic_configuration_example(self):
        """Test the basic configuration example from documentation"""
        config = ReasoningConfig(
            parse_model="gemini-2.5-pro",
            synthesis_model="gemini-2.5-pro",
            graph_model="phi-4-reasoning",
            inference_samples=1000
        )
        
        assert config.parse_model == "gemini-2.5-pro"
        assert config.synthesis_model == "gemini-2.5-pro"
        assert config.inference_samples == 1000

    def test_custom_variants_example(self):
        """Test the custom variants example from documentation"""
        config = ReasoningConfig(
            parse_model="gemini-2.5-flash",
            synthesis_model="gemini-2.5-pro",
            fallback_models={
                "parse": "gemini-1.5-pro",
                "synthesis": "gemini-1.5-pro"
            }
        )
        
        assert config.parse_model == "gemini-2.5-flash"
        assert config.synthesis_model == "gemini-2.5-pro"
        assert "parse" in config.fallback_models
        assert "synthesis" in config.fallback_models

    def test_ensemble_configuration_example(self):
        """Test the ensemble configuration example from documentation"""
        ensemble_config = ReasoningConfig(
            parse_model="gemini-2.5-pro",
            synthesis_model="gemini-2.5-pro",
            fallback_models={
                "parse": "gemini-2.5-flash",
                "synthesis": "gemini-1.5-pro"
            },
            max_retries=3,
            enable_parallel_processing=True
        )
        
        assert ensemble_config.max_retries == 3
        assert ensemble_config.enable_parallel_processing is True
        assert ensemble_config.fallback_models is not None