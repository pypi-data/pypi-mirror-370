"""
Test core MSA components initialization and basic functionality
"""

import pytest
from reasoning_kernel.core.kernel_config import KernelManager
from reasoning_kernel.msa.synthesis_engine import MSAEngine
from reasoning_kernel.msa.mode1_knowledge import KnowledgeExtractor
from reasoning_kernel.msa.mode2_probabilistic import ProbabilisticModelSynthesizer
from reasoning_kernel.msa.confidence_indicator import ConfidenceIndicator


class TestCoreComponents:
    """Test core MSA engine components"""
    
    def test_kernel_manager_creation(self):
        """Test KernelManager can be instantiated"""
        kernel_manager = KernelManager()
        assert kernel_manager is not None
        assert kernel_manager.kernel is None  # Before initialization
        assert kernel_manager.chat_service is None
        
    def test_msa_engine_creation(self):
        """Test MSAEngine can be instantiated"""
        kernel_manager = KernelManager()
        msa_engine = MSAEngine(kernel_manager)
        
        assert msa_engine is not None
        assert msa_engine.kernel_manager == kernel_manager
        assert msa_engine.knowledge_extractor is None  # Before initialization
        assert msa_engine.probabilistic_synthesizer is None
        assert msa_engine.confidence_indicator is None
        
    def test_knowledge_extractor_creation(self):
        """Test KnowledgeExtractor can be instantiated"""
        kernel_manager = KernelManager()
        extractor = KnowledgeExtractor(kernel_manager)
        
        assert extractor is not None
        assert extractor.kernel_manager == kernel_manager
        
    def test_probabilistic_synthesizer_creation(self):
        """Test ProbabilisticModelSynthesizer can be instantiated"""
        synthesizer = ProbabilisticModelSynthesizer()
        
        assert synthesizer is not None
        assert hasattr(synthesizer, 'executor')
        assert hasattr(synthesizer, 'models_cache')
        
    def test_confidence_indicator_creation(self):
        """Test ConfidenceIndicator can be instantiated"""
        indicator = ConfidenceIndicator()
        
        assert indicator is not None
        assert hasattr(indicator, 'config')
        assert hasattr(indicator, 'weights')
        
        # Test with custom config
        custom_config = {'component_weights': {'knowledge_extraction': 0.4}}
        indicator_custom = ConfidenceIndicator(custom_config)
        assert indicator_custom.config == custom_config


class TestComponentIntegration:
    """Test component integration without requiring external services"""
    
    def test_msa_engine_initialization_check(self):
        """Test MSAEngine initialization checks work correctly"""
        kernel_manager = KernelManager()
        msa_engine = MSAEngine(kernel_manager)
        
        # Test that uninitialized engine raises appropriate errors
        with pytest.raises(RuntimeError, match="MSA Engine not initialized"):
            import asyncio
            asyncio.run(msa_engine.reason_about_scenario("test scenario"))