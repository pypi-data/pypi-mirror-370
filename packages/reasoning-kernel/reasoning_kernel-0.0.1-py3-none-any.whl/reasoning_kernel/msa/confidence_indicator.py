"""
Probabilistic Model Confidence Indicator

This module provides confidence scoring for MSA reasoning chains based on:
- Knowledge extraction completeness and quality
- Probabilistic model synthesis success and coherence
- Uncertainty quantification reliability
- Integration consistency between modes
"""

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level categories"""

    VERY_HIGH = "very_high"  # 0.9-1.0
    HIGH = "high"  # 0.7-0.89
    MEDIUM = "medium"  # 0.5-0.69
    LOW = "low"  # 0.3-0.49
    VERY_LOW = "very_low"  # 0.0-0.29


@dataclass
class ConfidenceMetrics:
    """Detailed confidence metrics breakdown"""

    overall_score: float
    confidence_level: ConfidenceLevel

    # Component scores
    knowledge_extraction_score: float
    model_synthesis_score: float
    uncertainty_quantification_score: float
    integration_coherence_score: float

    # Detailed metrics
    completeness_metrics: Dict[str, Any]
    reliability_metrics: Dict[str, Any]
    consistency_metrics: Dict[str, Any]

    # Explanations
    confidence_explanation: str
    improvement_suggestions: List[str]
    risk_factors: List[str]


class ConfidenceIndicator:
    """
    Calculates confidence scores for MSA reasoning chains
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.weights = self.config.get(
            "component_weights",
            {
                "knowledge_extraction": 0.3,
                "model_synthesis": 0.25,
                "uncertainty_quantification": 0.25,
                "integration_coherence": 0.2,
            },
        )

    def calculate_confidence(
        self, reasoning_data: Dict[str, Any], chain_metadata: Optional[Dict[str, Any]] = None
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence metrics for a reasoning chain

        Args:
            reasoning_data: Complete reasoning chain data
            chain_metadata: Optional metadata about processing

        Returns:
            ConfidenceMetrics with detailed scoring and explanations
        """
        try:
            logger.info("Calculating confidence metrics for reasoning chain")

            # Extract components
            knowledge_base = reasoning_data.get("knowledge_base", {})
            model_specs = reasoning_data.get("model_specs", {})
            synthesis_results = reasoning_data.get("synthesis_results", {})
            final_reasoning = reasoning_data.get("final_reasoning", {})

            # Calculate component scores
            knowledge_score = self._score_knowledge_extraction(knowledge_base, final_reasoning)
            synthesis_score = self._score_model_synthesis(model_specs, synthesis_results)
            uncertainty_score = self._score_uncertainty_quantification(synthesis_results)
            coherence_score = self._score_integration_coherence(knowledge_base, synthesis_results, final_reasoning)

            # Calculate weighted overall score
            overall_score = (
                knowledge_score * self.weights["knowledge_extraction"]
                + synthesis_score * self.weights["model_synthesis"]
                + uncertainty_score * self.weights["uncertainty_quantification"]
                + coherence_score * self.weights["integration_coherence"]
            )

            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_score)

            # Generate detailed metrics
            completeness_metrics = self._analyze_completeness(reasoning_data)
            reliability_metrics = self._analyze_reliability(reasoning_data, chain_metadata)
            consistency_metrics = self._analyze_consistency(reasoning_data)

            # Generate explanations
            confidence_explanation = self._generate_confidence_explanation(
                overall_score, knowledge_score, synthesis_score, uncertainty_score, coherence_score
            )

            improvement_suggestions = self._generate_improvement_suggestions(
                knowledge_score, synthesis_score, uncertainty_score, coherence_score
            )

            risk_factors = self._identify_risk_factors(reasoning_data)

            return ConfidenceMetrics(
                overall_score=overall_score,
                confidence_level=confidence_level,
                knowledge_extraction_score=knowledge_score,
                model_synthesis_score=synthesis_score,
                uncertainty_quantification_score=uncertainty_score,
                integration_coherence_score=coherence_score,
                completeness_metrics=completeness_metrics,
                reliability_metrics=reliability_metrics,
                consistency_metrics=consistency_metrics,
                confidence_explanation=confidence_explanation,
                improvement_suggestions=improvement_suggestions,
                risk_factors=risk_factors,
            )

        except Exception as e:
            logger.error(f"Error calculating confidence metrics: {e}")
            return self._create_fallback_metrics(f"Error in confidence calculation: {e}")

    def _score_knowledge_extraction(self, knowledge_base: Dict[str, Any], final_reasoning: Dict[str, Any]) -> float:
        """Score the quality and completeness of knowledge extraction"""
        score = 0.0
        max_score = 1.0

        try:
            # Check entity extraction completeness
            entities = knowledge_base.get("entities", [])
            relationships = knowledge_base.get("relationships", [])
            causal_factors = knowledge_base.get("causal_factors", [])

            # Base score from entity count and quality
            if entities:
                entity_score = min(len(entities) / 10, 0.4)  # Up to 0.4 for entities
                score += entity_score

                # Quality check - entities should have names and descriptions
                quality_score = sum(1 for e in entities if e.get("name") and e.get("description")) / len(entities)
                score += quality_score * 0.2

            # Relationship extraction
            if relationships:
                rel_score = min(len(relationships) / 8, 0.2)
                score += rel_score

            # Causal factor identification
            if causal_factors:
                causal_score = min(len(causal_factors) / 5, 0.2)
                score += causal_score

            # Final reasoning quality (from Mode 1 integration)
            insights = final_reasoning.get("key_insights", {})
            if insights:
                primary_entities = insights.get("primary_entities", [])
                if primary_entities:
                    score += 0.2

            return min(score, max_score)

        except Exception as e:
            logger.warning(f"Error scoring knowledge extraction: {e}")
            return 0.5  # Default moderate score

    def _score_model_synthesis(self, model_specs: Dict[str, Any], synthesis_results: Dict[str, Any]) -> float:
        """Score the success and quality of probabilistic model synthesis"""
        score = 0.0
        max_score = 1.0

        try:
            # Check if model synthesis succeeded
            if synthesis_results.get("success", False):
                score += 0.5  # Base score for success

                # Check model structure quality
                model_structure = synthesis_results.get("model_structure", {})
                if model_structure:
                    score += 0.2

                # Check predictions quality
                predictions = synthesis_results.get("predictions", {})
                if predictions:
                    score += 0.2

                # Check if model specs were generated
                variables = model_specs.get("variables", [])
                if variables:
                    variable_score = min(len(variables) / 8, 0.1)
                    score += variable_score

            else:
                # Partial credit if model specs were generated despite synthesis failure
                variables = model_specs.get("variables", [])
                if variables:
                    score += 0.2
                dependencies = model_specs.get("dependencies", [])
                if dependencies:
                    score += 0.1

            return min(score, max_score)

        except Exception as e:
            logger.warning(f"Error scoring model synthesis: {e}")
            return 0.3  # Lower default for synthesis issues

    def _score_uncertainty_quantification(self, synthesis_results: Dict[str, Any]) -> float:
        """Score the quality of uncertainty quantification"""
        score = 0.0
        max_score = 1.0

        try:
            uncertainty_analysis = synthesis_results.get("uncertainty_analysis", {})

            if uncertainty_analysis:
                # Check for different types of uncertainty
                epistemic = uncertainty_analysis.get("epistemic_uncertainty", {})
                aleatory = uncertainty_analysis.get("aleatory_uncertainty", {})
                total = uncertainty_analysis.get("total_uncertainty", {})

                if epistemic:
                    score += 0.3
                if aleatory:
                    score += 0.3
                if total:
                    score += 0.2

                # Check for overall assessment
                overall = uncertainty_analysis.get("overall_assessment", {})
                if overall:
                    score += 0.2
            else:
                # Check if synthesis failed but uncertainty was still assessed
                if not synthesis_results.get("success", False):
                    score += 0.1  # Minimal credit for attempting uncertainty assessment

            return min(score, max_score)

        except Exception as e:
            logger.warning(f"Error scoring uncertainty quantification: {e}")
            return 0.2

    def _score_integration_coherence(
        self, knowledge_base: Dict[str, Any], synthesis_results: Dict[str, Any], final_reasoning: Dict[str, Any]
    ) -> float:
        """Score how well the modes are integrated in final reasoning"""
        score = 0.0
        max_score = 1.0

        try:
            # Check if final reasoning exists
            summary = final_reasoning.get("summary", "")
            recommendations = final_reasoning.get("recommendations", [])
            insights = final_reasoning.get("key_insights", {})

            if summary:
                score += 0.3

            if recommendations:
                rec_score = min(len(recommendations) / 5, 0.3)
                score += rec_score

            if insights:
                # Check for integration of both modes
                entities = insights.get("primary_entities", [])
                relationships = insights.get("critical_relationships", 0)
                factors = insights.get("high_impact_factors", [])

                if entities:
                    score += 0.1
                if relationships and relationships > 0:
                    score += 0.1
                if factors:
                    score += 0.1

                # Check for model confidence integration
                model_confidence = insights.get("model_confidence_score", 0)
                if model_confidence > 0:
                    score += 0.1

            return min(score, max_score)

        except Exception as e:
            logger.warning(f"Error scoring integration coherence: {e}")
            return 0.4

    def _determine_confidence_level(self, overall_score: float) -> ConfidenceLevel:
        """Determine confidence level category from score"""
        if overall_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif overall_score >= 0.7:
            return ConfidenceLevel.HIGH
        elif overall_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif overall_score >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _analyze_completeness(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze completeness of reasoning components"""
        knowledge_base = reasoning_data.get("knowledge_base", {})

        return {
            "entities_extracted": len(knowledge_base.get("entities", [])),
            "relationships_identified": len(knowledge_base.get("relationships", [])),
            "causal_factors_found": len(knowledge_base.get("causal_factors", [])),
            "constraints_identified": len(knowledge_base.get("constraints", [])),
            "model_synthesis_attempted": reasoning_data.get("synthesis_results", {}).get("success") is not None,
            "final_reasoning_generated": bool(reasoning_data.get("final_reasoning", {}).get("summary")),
        }

    def _analyze_reliability(
        self, reasoning_data: Dict[str, Any], metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze reliability indicators"""
        synthesis_results = reasoning_data.get("synthesis_results", {})

        reliability = {
            "model_synthesis_success": synthesis_results.get("success", False),
            "processing_completed": True,  # If we have data, processing completed
            "error_free_execution": not reasoning_data.get("error"),
        }

        if metadata:
            reliability.update(
                {
                    "processing_time_reasonable": metadata.get("processing_time_seconds", 0) < 300,
                    "memory_usage_normal": True,  # Could be enhanced with actual metrics
                }
            )

        return reliability

    def _analyze_consistency(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency between components"""
        knowledge_base = reasoning_data.get("knowledge_base", {})
        final_reasoning = reasoning_data.get("final_reasoning", {})

        # Check if entities mentioned in final reasoning match extracted entities
        extracted_entities = [e.get("name", "").lower() for e in knowledge_base.get("entities", [])]
        summary = final_reasoning.get("summary", "").lower()

        entity_consistency = 0
        if extracted_entities and summary:
            mentioned_count = sum(1 for entity in extracted_entities if entity in summary)
            entity_consistency = mentioned_count / len(extracted_entities) if extracted_entities else 0

        return {
            "entity_mention_consistency": entity_consistency,
            "recommendations_align_with_knowledge": len(final_reasoning.get("recommendations", [])) > 0,
            "uncertainty_acknowledged": bool(final_reasoning.get("uncertainty_assessment", {})),
        }

    def _generate_confidence_explanation(
        self, overall: float, knowledge: float, synthesis: float, uncertainty: float, coherence: float
    ) -> str:
        """Generate human-readable confidence explanation"""
        level = self._determine_confidence_level(overall)

        explanations = {
            ConfidenceLevel.VERY_HIGH: "The reasoning shows very high confidence with strong knowledge extraction, successful model synthesis, and coherent integration.",
            ConfidenceLevel.HIGH: "The reasoning demonstrates high confidence with good knowledge extraction and mostly successful analysis.",
            ConfidenceLevel.MEDIUM: "The reasoning shows moderate confidence with adequate knowledge extraction but some limitations in model synthesis or integration.",
            ConfidenceLevel.LOW: "The reasoning has low confidence due to incomplete knowledge extraction or failed model synthesis.",
            ConfidenceLevel.VERY_LOW: "The reasoning has very low confidence with significant issues in knowledge extraction, model synthesis, or integration.",
        }

        base_explanation = explanations[level]

        # Add specific component insights
        details = []
        if knowledge < 0.5:
            details.append("knowledge extraction was limited")
        if synthesis < 0.3:
            details.append("probabilistic model synthesis failed")
        if uncertainty < 0.3:
            details.append("uncertainty quantification was incomplete")
        if coherence < 0.4:
            details.append("integration between reasoning modes was weak")

        if details:
            base_explanation += f" Specifically: {', '.join(details)}."

        return base_explanation

    def _generate_improvement_suggestions(
        self, knowledge: float, synthesis: float, uncertainty: float, coherence: float
    ) -> List[str]:
        """Generate suggestions for improving confidence"""
        suggestions = []

        if knowledge < 0.6:
            suggestions.append("Enhance scenario description with more specific details and context")
            suggestions.append("Provide additional domain-specific information for better entity extraction")

        if synthesis < 0.4:
            suggestions.append("Simplify the probabilistic model structure for better synthesis")
            suggestions.append("Provide more quantitative constraints and relationships")

        if uncertainty < 0.4:
            suggestions.append("Include explicit uncertainty ranges and confidence intervals")
            suggestions.append("Specify known vs unknown factors more clearly")

        if coherence < 0.5:
            suggestions.append("Ensure knowledge extraction and probabilistic analysis address the same aspects")
            suggestions.append("Provide more structured reasoning steps and clear conclusions")

        return suggestions

    def _identify_risk_factors(self, reasoning_data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors affecting confidence"""
        risks = []

        synthesis_results = reasoning_data.get("synthesis_results", {})
        if not synthesis_results.get("success", False):
            risks.append("Probabilistic model synthesis failed, limiting quantitative analysis")

        knowledge_base = reasoning_data.get("knowledge_base", {})
        if len(knowledge_base.get("entities", [])) < 3:
            risks.append("Limited entity extraction may indicate scenario complexity or ambiguity")

        if not reasoning_data.get("final_reasoning", {}).get("uncertainty_assessment"):
            risks.append("Missing uncertainty assessment reduces confidence in recommendations")

        final_reasoning = reasoning_data.get("final_reasoning", {})
        if len(final_reasoning.get("recommendations", [])) < 2:
            risks.append("Limited recommendations suggest incomplete analysis")

        return risks

    def _create_fallback_metrics(self, error_message: str) -> ConfidenceMetrics:
        """Create fallback metrics when calculation fails"""
        return ConfidenceMetrics(
            overall_score=0.1,
            confidence_level=ConfidenceLevel.VERY_LOW,
            knowledge_extraction_score=0.1,
            model_synthesis_score=0.1,
            uncertainty_quantification_score=0.1,
            integration_coherence_score=0.1,
            completeness_metrics={"error": True},
            reliability_metrics={"error": True},
            consistency_metrics={"error": True},
            confidence_explanation=f"Confidence calculation failed: {error_message}",
            improvement_suggestions=["Fix underlying reasoning system issues"],
            risk_factors=["System error affects all confidence metrics"],
        )
