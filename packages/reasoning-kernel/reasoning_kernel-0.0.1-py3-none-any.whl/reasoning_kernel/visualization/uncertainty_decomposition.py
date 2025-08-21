"""
Uncertainty Decomposition System
===============================

Breaks down uncertainty into specific components and suggests data collection strategies.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Simple fallback for basic statistics
    class np:
        @staticmethod
        def std(data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            return variance ** 0.5
        
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        @staticmethod
        def sqrt(x):
            return x ** 0.5
import structlog


logger = structlog.get_logger(__name__)

@dataclass
class UncertaintyComponent:
    """Represents a component of uncertainty"""
    name: str
    contribution: float  # Percentage contribution to total uncertainty
    category: str  # 'aleatory', 'epistemic', 'model', 'data'
    description: str
    reducible: bool  # Whether this uncertainty can be reduced
    reduction_strategy: Optional[str] = None
    confidence: float = 0.8

@dataclass
class UncertaintyDecomposition:
    """Complete uncertainty analysis"""
    total_uncertainty: float
    components: List[UncertaintyComponent]
    dominant_sources: List[str]
    reduction_recommendations: List[str]
    confidence_intervals: Dict[str, Tuple[float, float]]

class UncertaintyAnalyzer:
    """Analyzes and decomposes uncertainty in reasoning results"""
    
    def __init__(self):
        self.component_categories = {
            'aleatory': 'Inherent randomness in the system',
            'epistemic': 'Uncertainty due to lack of knowledge',
            'model': 'Uncertainty from model assumptions and limitations',
            'data': 'Uncertainty from data quality and quantity issues'
        }
    
    def decompose_uncertainty(self, reasoning_result: Dict[str, Any]) -> UncertaintyDecomposition:
        """Decompose uncertainty from reasoning results"""
        
        # Extract uncertainty information from different stages
        stage_uncertainties = self._extract_stage_uncertainties(reasoning_result)
        
        # Analyze uncertainty components
        components = self._analyze_uncertainty_components(reasoning_result, stage_uncertainties)
        
        # Calculate total uncertainty
        total_uncertainty = self._calculate_total_uncertainty(components)
        
        # Identify dominant sources
        dominant_sources = self._identify_dominant_sources(components)
        
        # Generate reduction recommendations
        recommendations = self._generate_reduction_recommendations(components)
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(reasoning_result)
        
        decomposition = UncertaintyDecomposition(
            total_uncertainty=total_uncertainty,
            components=components,
            dominant_sources=dominant_sources,
            reduction_recommendations=recommendations,
            confidence_intervals=confidence_intervals
        )
        
        logger.info("Uncertainty decomposition completed",
                   total_uncertainty=total_uncertainty,
                   num_components=len(components),
                   dominant_sources=len(dominant_sources))
        
        return decomposition
    
    def _extract_stage_uncertainties(self, reasoning_result: Dict[str, Any]) -> Dict[str, float]:
        """Extract uncertainty measures from each reasoning stage"""
        stage_uncertainties = {}
        
        # Parse stage uncertainty
        if 'parsing_result' in reasoning_result:
            parse_confidence = reasoning_result['parsing_result'].get('confidence', 0.8)
            stage_uncertainties['parsing'] = 1.0 - parse_confidence
        
        # Retrieval stage uncertainty
        if 'retrieval_result' in reasoning_result:
            retrieval_confidence = reasoning_result['retrieval_result'].get('confidence', 0.5)
            stage_uncertainties['retrieval'] = 1.0 - retrieval_confidence
        
        # Graph stage uncertainty
        if 'graph_result' in reasoning_result:
            graph_confidence = reasoning_result['graph_result'].get('confidence', 0.7)
            stage_uncertainties['graph'] = 1.0 - graph_confidence
        
        # Synthesis stage uncertainty
        if 'synthesis_result' in reasoning_result:
            synthesis_confidence = reasoning_result['synthesis_result'].get('confidence', 0.9)
            stage_uncertainties['synthesis'] = 1.0 - synthesis_confidence
        
        # Inference stage uncertainty
        if 'inference_result' in reasoning_result:
            inference_result = reasoning_result['inference_result']
            if 'samples' in inference_result:
                # Calculate uncertainty from posterior samples
                samples = inference_result['samples']
                if samples:
                    # Use coefficient of variation as uncertainty measure
                    std_dev = np.std(samples)
                    mean_val = np.mean(samples)
                    if mean_val != 0:
                        stage_uncertainties['inference'] = abs(std_dev / mean_val)
                    else:
                        stage_uncertainties['inference'] = std_dev
            else:
                inference_confidence = inference_result.get('confidence', 0.5)
                stage_uncertainties['inference'] = 1.0 - inference_confidence
        
        return stage_uncertainties
    
    def _analyze_uncertainty_components(self, reasoning_result: Dict[str, Any], 
                                      stage_uncertainties: Dict[str, float]) -> List[UncertaintyComponent]:
        """Analyze and categorize uncertainty components"""
        components = []
        
        # Data quality uncertainty (epistemic)
        data_quality_uncertainty = self._assess_data_quality_uncertainty(reasoning_result)
        if data_quality_uncertainty > 0.01:
            components.append(UncertaintyComponent(
                name="Data Quality",
                contribution=data_quality_uncertainty * 100,
                category="data",
                description="Uncertainty from data completeness, accuracy, and reliability",
                reducible=True,
                reduction_strategy="Collect higher quality data, validate existing data sources",
                confidence=0.9
            ))
        
        # Model uncertainty (epistemic)
        model_uncertainty = self._assess_model_uncertainty(reasoning_result)
        if model_uncertainty > 0.01:
            components.append(UncertaintyComponent(
                name="Model Assumptions",
                contribution=model_uncertainty * 100,
                category="model",
                description="Uncertainty from model structure and assumptions",
                reducible=True,
                reduction_strategy="Test alternative model structures, validate assumptions",
                confidence=0.8
            ))
        
        # Parameter uncertainty (epistemic)
        param_uncertainty = stage_uncertainties.get('inference', 0.1)
        if param_uncertainty > 0.01:
            components.append(UncertaintyComponent(
                name="Parameter Estimation",
                contribution=param_uncertainty * 100,
                category="epistemic",
                description="Uncertainty in estimated parameters and relationships",
                reducible=True,
                reduction_strategy="Collect more data, improve estimation methods",
                confidence=0.85
            ))
        
        # Knowledge uncertainty (epistemic)
        knowledge_uncertainty = stage_uncertainties.get('retrieval', 0.2)
        if knowledge_uncertainty > 0.01:
            components.append(UncertaintyComponent(
                name="Knowledge Gaps",
                contribution=knowledge_uncertainty * 100,
                category="epistemic",
                description="Uncertainty from incomplete domain knowledge",
                reducible=True,
                reduction_strategy="Expand knowledge base, consult domain experts",
                confidence=0.7
            ))
        
        # Measurement uncertainty (aleatory)
        measurement_uncertainty = self._assess_measurement_uncertainty(reasoning_result)
        if measurement_uncertainty > 0.01:
            components.append(UncertaintyComponent(
                name="Measurement Error",
                contribution=measurement_uncertainty * 100,
                category="aleatory",
                description="Inherent uncertainty in measurements and observations",
                reducible=False,
                reduction_strategy="Use more precise measurement instruments",
                confidence=0.9
            ))
        
        # Structural uncertainty (model)
        structural_uncertainty = stage_uncertainties.get('graph', 0.15)
        if structural_uncertainty > 0.01:
            components.append(UncertaintyComponent(
                name="Causal Structure",
                contribution=structural_uncertainty * 100,
                category="model",
                description="Uncertainty about causal relationships and dependencies",
                reducible=True,
                reduction_strategy="Conduct controlled experiments, gather expert knowledge",
                confidence=0.75
            ))
        
        # Normalize contributions to sum to 100%
        total_contribution = sum(comp.contribution for comp in components)
        if total_contribution > 0:
            for comp in components:
                comp.contribution = (comp.contribution / total_contribution) * 100
        
        # Sort by contribution
        components.sort(key=lambda x: x.contribution, reverse=True)
        
        return components
    
    def _assess_data_quality_uncertainty(self, reasoning_result: Dict[str, Any]) -> float:
        """Assess uncertainty from data quality issues"""
        base_uncertainty = 0.1
        
        # Check for missing data indicators
        if 'data_quality' in reasoning_result:
            quality_score = reasoning_result['data_quality'].get('score', 0.8)
            return (1.0 - quality_score) * 0.3
        
        # Estimate from retrieval results
        if 'retrieval_result' in reasoning_result:
            docs_found = reasoning_result['retrieval_result'].get('documents_found', 0)
            if docs_found == 0:
                return 0.4  # High uncertainty with no supporting data
            elif docs_found < 3:
                return 0.2  # Moderate uncertainty with limited data
            else:
                return 0.05  # Low uncertainty with sufficient data
        
        return base_uncertainty
    
    def _assess_model_uncertainty(self, reasoning_result: Dict[str, Any]) -> float:
        """Assess uncertainty from model structure and assumptions"""
        base_uncertainty = 0.15
        
        # Check synthesis complexity
        if 'synthesis_result' in reasoning_result:
            synthesis = reasoning_result['synthesis_result']
            code_complexity = len(synthesis.get('code', '').split('\n'))
            
            # More complex models generally have higher uncertainty
            if code_complexity > 100:
                return 0.25
            elif code_complexity > 50:
                return 0.2
            else:
                return 0.1
        
        return base_uncertainty
    
    def _assess_measurement_uncertainty(self, reasoning_result: Dict[str, Any]) -> float:
        """Assess inherent measurement uncertainty"""
        # This would typically be domain-specific
        # For now, use a conservative estimate
        return 0.05
    
    def _calculate_total_uncertainty(self, components: List[UncertaintyComponent]) -> float:
        """Calculate total uncertainty from components"""
        # Use root sum of squares for independent uncertainties
        total_variance = sum((comp.contribution / 100) ** 2 for comp in components)
        return np.sqrt(total_variance)
    
    def _identify_dominant_sources(self, components: List[UncertaintyComponent], 
                                 threshold: float = 20.0) -> List[str]:
        """Identify uncertainty sources that contribute more than threshold percentage"""
        return [comp.name for comp in components if comp.contribution >= threshold]
    
    def _generate_reduction_recommendations(self, components: List[UncertaintyComponent]) -> List[str]:
        """Generate recommendations for reducing uncertainty"""
        recommendations = []
        
        # Sort components by contribution and reducibility
        reducible_components = [comp for comp in components if comp.reducible]
        reducible_components.sort(key=lambda x: x.contribution, reverse=True)
        
        for comp in reducible_components[:5]:  # Top 5 reducible sources
            if comp.reduction_strategy:
                recommendations.append(
                    f"Reduce {comp.name} uncertainty ({comp.contribution:.1f}%): {comp.reduction_strategy}"
                )
        
        # Add general recommendations
        total_epistemic = sum(comp.contribution for comp in components if comp.category == 'epistemic')
        if total_epistemic > 50:
            recommendations.append(
                f"High epistemic uncertainty ({total_epistemic:.1f}%) - Focus on data collection and knowledge gathering"
            )
        
        total_model = sum(comp.contribution for comp in components if comp.category == 'model')
        if total_model > 30:
            recommendations.append(
                f"Significant model uncertainty ({total_model:.1f}%) - Consider alternative model structures"
            )
        
        return recommendations
    
    def _calculate_confidence_intervals(self, reasoning_result: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for key variables"""
        intervals = {}
        
        # Extract from inference results if available
        if 'inference_result' in reasoning_result:
            inference = reasoning_result['inference_result']
            if 'posterior_summary' in inference:
                summary = inference['posterior_summary']
                for var_name, stats in summary.items():
                    if isinstance(stats, dict) and 'mean' in stats:
                        mean = stats['mean']
                        std = stats.get('std', mean * 0.1)
                        # 95% confidence interval
                        intervals[var_name] = (mean - 1.96 * std, mean + 1.96 * std)
        
        # Add overall confidence interval
        overall_confidence = reasoning_result.get('confidence', 0.5)
        overall_uncertainty = 1.0 - overall_confidence
        intervals['overall_result'] = (
            overall_confidence - overall_uncertainty,
            min(1.0, overall_confidence + overall_uncertainty)
        )
        
        return intervals
    
    def export_for_visualization(self, decomposition: UncertaintyDecomposition) -> Dict[str, Any]:
        """Export uncertainty decomposition for visualization"""
        
        return {
            'total_uncertainty': decomposition.total_uncertainty,
            'uncertainty_breakdown': [
                {
                    'name': comp.name,
                    'contribution': comp.contribution,
                    'category': comp.category,
                    'description': comp.description,
                    'reducible': comp.reducible,
                    'reduction_strategy': comp.reduction_strategy,
                    'color': self._get_category_color(comp.category)
                }
                for comp in decomposition.components
            ],
            'dominant_sources': decomposition.dominant_sources,
            'recommendations': decomposition.reduction_recommendations,
            'confidence_intervals': {
                var: {'lower': ci[0], 'upper': ci[1]}
                for var, ci in decomposition.confidence_intervals.items()
            },
            'category_summary': {
                category: sum(comp.contribution for comp in decomposition.components 
                            if comp.category == category)
                for category in ['aleatory', 'epistemic', 'model', 'data']
            }
        }
    
    def _get_category_color(self, category: str) -> str:
        """Get color for uncertainty category"""
        colors = {
            'aleatory': '#e74c3c',    # Red - inherent uncertainty
            'epistemic': '#3498db',   # Blue - knowledge uncertainty  
            'model': '#f39c12',       # Orange - model uncertainty
            'data': '#27ae60'         # Green - data uncertainty
        }
        return colors.get(category, '#95a5a6')