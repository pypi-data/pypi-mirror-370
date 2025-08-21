"""
EvaluationAgent: Reasoning quality validation and performance assessment

This agent is responsible for:
- Validating reasoning quality and consistency
- Confidence scoring algorithms
- Result consistency checking
- Performance metrics collection
- Decision boundary analysis
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.utils.security import get_secure_logger
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function


logger = get_secure_logger(__name__)


class QualityMetric(Enum):
    """Quality metrics for evaluation"""

    COHERENCE = "coherence"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    UNCERTAINTY = "uncertainty"
    EXPLAINABILITY = "explainability"


@dataclass
class EvaluationRequest:
    """Request for reasoning evaluation"""

    reasoning_result: Dict[str, Any]
    ground_truth: Optional[Dict[str, Any]] = None
    evaluation_criteria: List[QualityMetric] = None
    context: Optional[str] = None
    reference_standards: Optional[Dict[str, Any]] = None


@dataclass
class QualityScore:
    """Individual quality score"""

    metric: QualityMetric
    score: float
    confidence: float
    explanation: str
    evidence: List[str]


@dataclass
class PerformanceMetrics:
    """Performance metrics for reasoning system"""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    execution_time: float
    memory_usage: float
    convergence_rate: float
    error_rate: float


@dataclass
class EvaluationResult:
    """Result of reasoning evaluation"""

    overall_quality_score: float
    quality_scores: List[QualityScore]
    performance_metrics: PerformanceMetrics
    consistency_analysis: Dict[str, Any]
    decision_boundaries: Dict[str, Any]
    recommendations: List[str]
    evaluation_confidence: float
    execution_time: float
    errors: List[str] = None


class EvaluationAgent(BaseReasoningAgent):
    """
    Agent for validating reasoning quality and assessing performance.

    This agent evaluates the quality of reasoning outputs using multiple
    criteria and provides detailed performance assessments.
    """

    def __init__(self, kernel: Kernel, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            "Evaluation",
            kernel,
            "Reasoning quality validation and assessment agent",
            "Validate reasoning quality and assess performance",
        )
        self.quality_thresholds = (
            config.get(
                "quality_thresholds",
                {
                    QualityMetric.COHERENCE: 0.7,
                    QualityMetric.CONSISTENCY: 0.8,
                    QualityMetric.COMPLETENESS: 0.6,
                    QualityMetric.ACCURACY: 0.8,
                    QualityMetric.RELEVANCE: 0.7,
                    QualityMetric.UNCERTAINTY: 0.5,
                    QualityMetric.EXPLAINABILITY: 0.6,
                },
            )
            if config
            else {}
        )

        self.weight_matrix = (
            config.get(
                "metric_weights",
                {
                    QualityMetric.COHERENCE: 0.15,
                    QualityMetric.CONSISTENCY: 0.20,
                    QualityMetric.COMPLETENESS: 0.15,
                    QualityMetric.ACCURACY: 0.20,
                    QualityMetric.RELEVANCE: 0.15,
                    QualityMetric.UNCERTAINTY: 0.10,
                    QualityMetric.EXPLAINABILITY: 0.05,
                },
            )
            if config
            else {}
        )

        # Performance benchmarks
        self.performance_benchmarks = {
            "execution_time_max": 60.0,  # seconds
            "memory_usage_max": 512.0,  # MB
            "accuracy_min": 0.8,
            "convergence_rate_min": 0.9,
        }

    async def _process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message through the evaluation pipeline"""
        try:
            reasoning_result = kwargs.get("reasoning_result", {"input": message})

            # Create evaluation request
            request = EvaluationRequest(
                reasoning_result=reasoning_result,
                context=message,
                evaluation_criteria=kwargs.get(
                    "evaluation_criteria",
                    [QualityMetric.COHERENCE, QualityMetric.CONSISTENCY],
                ),
            )

            # Perform evaluation
            result = await self.evaluate_reasoning(request)

            # Return formatted response
            if result.errors:
                return f"Evaluation failed: {', '.join(result.errors)}"
            else:
                return f"Evaluation completed with overall quality {result.overall_quality_score:.2f} and confidence {result.evaluation_confidence:.2f}"

        except Exception as e:
            return f"Error in evaluation: {str(e)}"

    @kernel_function(
        description="Evaluate reasoning quality and performance",
        name="evaluate_reasoning",
    )
    async def evaluate_reasoning(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Main evaluation function that assesses reasoning quality.

        Args:
            request: Evaluation request with reasoning results and criteria

        Returns:
            EvaluationResult with quality scores and performance metrics
        """
        start_time = datetime.now()
        errors = []

        try:
            logger.info("Starting comprehensive reasoning evaluation")

            # Step 1: Evaluate individual quality metrics
            quality_scores = await self._evaluate_quality_metrics(request)

            # Step 2: Calculate overall quality score
            overall_quality = self._calculate_overall_quality(quality_scores)

            # Step 3: Assess performance metrics
            performance_metrics = await self._assess_performance_metrics(request)

            # Step 4: Analyze consistency
            consistency_analysis = await self._analyze_consistency(request)

            # Step 5: Analyze decision boundaries
            decision_boundaries = await self._analyze_decision_boundaries(request)

            # Step 6: Generate recommendations
            recommendations = await self._generate_recommendations(
                quality_scores, performance_metrics, consistency_analysis
            )

            # Step 7: Calculate evaluation confidence
            evaluation_confidence = self._calculate_evaluation_confidence(
                quality_scores, performance_metrics
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            result = EvaluationResult(
                overall_quality_score=overall_quality,
                quality_scores=quality_scores,
                performance_metrics=performance_metrics,
                consistency_analysis=consistency_analysis,
                decision_boundaries=decision_boundaries,
                recommendations=recommendations,
                evaluation_confidence=evaluation_confidence,
                execution_time=execution_time,
                errors=errors,
            )

            logger.info(
                f"Evaluation completed: overall quality {overall_quality:.3f}, confidence {evaluation_confidence:.3f}"
            )
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Reasoning evaluation failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

            return EvaluationResult(
                overall_quality_score=0.0,
                quality_scores=[],
                performance_metrics=PerformanceMetrics(
                    accuracy=0,
                    precision=0,
                    recall=0,
                    f1_score=0,
                    execution_time=execution_time,
                    throughput=0,
                    error_rate=1.0
                ),
                consistency_analysis={},
                decision_boundaries={},
                recommendations=[],
                evaluation_confidence=0.0,
                execution_time=execution_time,
                errors=errors,
            )

    async def _evaluate_quality_metrics(
        self, request: EvaluationRequest
    ) -> List[QualityScore]:
        """Evaluate individual quality metrics"""
        quality_scores = []
        criteria = request.evaluation_criteria or list(QualityMetric)

        for metric in criteria:
            try:
                if metric == QualityMetric.COHERENCE:
                    score = await self._evaluate_coherence(request)
                elif metric == QualityMetric.CONSISTENCY:
                    score = await self._evaluate_consistency(request)
                elif metric == QualityMetric.COMPLETENESS:
                    score = await self._evaluate_completeness(request)
                elif metric == QualityMetric.ACCURACY:
                    score = await self._evaluate_accuracy(request)
                elif metric == QualityMetric.RELEVANCE:
                    score = await self._evaluate_relevance(request)
                elif metric == QualityMetric.UNCERTAINTY:
                    score = await self._evaluate_uncertainty(request)
                elif metric == QualityMetric.EXPLAINABILITY:
                    score = await self._evaluate_explainability(request)
                else:
                    # Default scoring for unknown metrics
                    score = QualityScore(
                        metric=metric,
                        score=0.5,
                        confidence=0.3,
                        explanation="Unknown metric - default scoring applied",
                        evidence=[],
                    )

                quality_scores.append(score)
                logger.debug(
                    f"Evaluated {metric.value}: score={score.score:.3f}, confidence={score.confidence:.3f}"
                )

            except Exception as e:
                logger.error(f"Failed to evaluate {metric.value}: {e}")
                # Add failed evaluation with low score
                quality_scores.append(
                    QualityScore(
                        metric=metric,
                        score=0.0,
                        confidence=0.0,
                        explanation=f"Evaluation failed: {str(e)}",
                        evidence=[],
                    )
                )

        return quality_scores

    async def _evaluate_coherence(self, request: EvaluationRequest) -> QualityScore:
        """Evaluate logical coherence of reasoning"""
        reasoning_result = request.reasoning_result

        # Check for logical flow and consistency in reasoning steps
        coherence_indicators = []

        # Check if reasoning follows logical sequence
        if "reasoning_steps" in reasoning_result:
            steps = reasoning_result["reasoning_steps"]
            if isinstance(steps, list) and len(steps) > 1:
                coherence_indicators.append("Sequential reasoning steps present")
            else:
                coherence_indicators.append("Missing or insufficient reasoning steps")

        # Check for contradictions
        content = str(reasoning_result)
        contradiction_keywords = ["but", "however", "contradicts", "inconsistent"]
        contradictions = sum(
            1 for keyword in contradiction_keywords if keyword in content.lower()
        )

        if contradictions == 0:
            coherence_indicators.append("No obvious contradictions detected")
        else:
            coherence_indicators.append(
                f"Potential contradictions detected: {contradictions}"
            )

        # Check for logical connectors
        logical_connectors = ["therefore", "because", "since", "thus", "consequently"]
        connector_count = sum(
            1 for connector in logical_connectors if connector in content.lower()
        )

        if connector_count > 2:
            coherence_indicators.append("Good use of logical connectors")
        else:
            coherence_indicators.append("Limited logical connectors")

        # Calculate coherence score
        base_score = 0.7  # Default coherence
        if contradictions == 0:
            base_score += 0.2
        if connector_count > 2:
            base_score += 0.1
        if "reasoning_steps" in reasoning_result:
            base_score += 0.1

        coherence_score = min(1.0, base_score)
        confidence = 0.8 if len(coherence_indicators) >= 3 else 0.6

        return QualityScore(
            metric=QualityMetric.COHERENCE,
            score=coherence_score,
            confidence=confidence,
            explanation="Coherence assessed based on logical flow, contradictions, and connectors",
            evidence=coherence_indicators,
        )

    async def _evaluate_consistency(self, request: EvaluationRequest) -> QualityScore:
        """Evaluate internal consistency of reasoning"""
        reasoning_result = request.reasoning_result

        consistency_checks = []

        # Check consistency of probability values
        if "probabilities" in reasoning_result:
            probs = reasoning_result["probabilities"]
            if isinstance(probs, dict):
                prob_values = [v for v in probs.values() if isinstance(v, (int, float))]
                if prob_values:
                    if all(0 <= p <= 1 for p in prob_values):
                        consistency_checks.append(
                            "Probability values within valid range"
                        )
                    else:
                        consistency_checks.append("Invalid probability values detected")

                    # Check if probabilities sum to reasonable values
                    total_prob = sum(prob_values)
                    if 0.8 <= total_prob <= 1.2:
                        consistency_checks.append(
                            "Probability distribution is normalized"
                        )
                    else:
                        consistency_checks.append(
                            f"Probability sum is {total_prob:.2f} (not normalized)"
                        )

        # Check consistency of confidence values
        if "confidence" in reasoning_result:
            confidence_val = reasoning_result["confidence"]
            if isinstance(confidence_val, (int, float)) and 0 <= confidence_val <= 1:
                consistency_checks.append("Confidence value is valid")
            else:
                consistency_checks.append("Invalid confidence value")

        # Check consistency between different result components
        if (
            "knowledge_extraction" in reasoning_result
            and "probabilistic_reasoning" in reasoning_result
        ):
            # Check if entities from knowledge extraction are used in probabilistic reasoning
            knowledge = reasoning_result["knowledge_extraction"]
            prob_reasoning = reasoning_result["probabilistic_reasoning"]

            if isinstance(knowledge, dict) and isinstance(prob_reasoning, dict):
                knowledge_entities = set(str(knowledge).lower().split())
                prob_entities = set(str(prob_reasoning).lower().split())
                overlap = len(knowledge_entities.intersection(prob_entities))

                if overlap > 3:
                    consistency_checks.append(
                        "Good alignment between knowledge and probabilistic reasoning"
                    )
                else:
                    consistency_checks.append(
                        "Limited alignment between reasoning components"
                    )

        # Calculate consistency score
        positive_checks = sum(
            1
            for check in consistency_checks
            if not any(
                neg in check.lower() for neg in ["invalid", "limited", "not", "missing"]
            )
        )
        total_checks = len(consistency_checks)

        if total_checks > 0:
            consistency_score = positive_checks / total_checks
        else:
            consistency_score = 0.5  # Default if no checks performed

        confidence = 0.9 if total_checks >= 3 else 0.7

        return QualityScore(
            metric=QualityMetric.CONSISTENCY,
            score=consistency_score,
            confidence=confidence,
            explanation="Consistency evaluated based on probability values, confidence, and component alignment",
            evidence=consistency_checks,
        )

    async def _evaluate_completeness(self, request: EvaluationRequest) -> QualityScore:
        """Evaluate completeness of reasoning"""
        reasoning_result = request.reasoning_result

        completeness_factors = []
        expected_components = [
            "knowledge_extraction",
            "probabilistic_reasoning",
            "confidence",
            "reasoning_steps",
            "conclusion",
            "evidence",
        ]

        present_components = []
        for component in expected_components:
            if component in reasoning_result:
                present_components.append(component)
                completeness_factors.append(f"Contains {component}")
            else:
                completeness_factors.append(f"Missing {component}")

        # Check depth of reasoning
        if "reasoning_steps" in reasoning_result:
            steps = reasoning_result["reasoning_steps"]
            if isinstance(steps, list):
                if len(steps) >= 3:
                    completeness_factors.append("Sufficient reasoning depth")
                else:
                    completeness_factors.append("Shallow reasoning depth")

        # Check for uncertainty quantification
        uncertainty_indicators = [
            "uncertainty",
            "confidence",
            "probability",
            "likelihood",
        ]
        uncertainty_present = any(
            indicator in str(reasoning_result).lower()
            for indicator in uncertainty_indicators
        )
        if uncertainty_present:
            completeness_factors.append("Uncertainty quantification present")
        else:
            completeness_factors.append("Missing uncertainty quantification")

        # Calculate completeness score
        component_score = len(present_components) / len(expected_components)
        depth_bonus = 0.1 if "Sufficient reasoning depth" in completeness_factors else 0
        uncertainty_bonus = 0.1 if uncertainty_present else 0

        completeness_score = min(1.0, component_score + depth_bonus + uncertainty_bonus)
        confidence = 0.85

        return QualityScore(
            metric=QualityMetric.COMPLETENESS,
            score=completeness_score,
            confidence=confidence,
            explanation=f"Completeness: {len(present_components)}/{len(expected_components)} components present",
            evidence=completeness_factors,
        )

    async def _evaluate_accuracy(self, request: EvaluationRequest) -> QualityScore:
        """Evaluate accuracy against ground truth (if available)"""
        reasoning_result = request.reasoning_result
        ground_truth = request.ground_truth

        accuracy_measures = []

        if ground_truth is None:
            # No ground truth available - use heuristic accuracy assessment
            accuracy_measures.append(
                "No ground truth available - using heuristic assessment"
            )

            # Check for realistic probability values
            if "probabilities" in reasoning_result:
                probs = reasoning_result["probabilities"]
                if isinstance(probs, dict):
                    prob_values = [
                        v for v in probs.values() if isinstance(v, (int, float))
                    ]
                    if prob_values:
                        # Check if probabilities are reasonable (not too extreme)
                        extreme_probs = sum(
                            1 for p in prob_values if p < 0.1 or p > 0.9
                        )
                        if extreme_probs / len(prob_values) < 0.5:
                            accuracy_measures.append(
                                "Probability values appear reasonable"
                            )
                        else:
                            accuracy_measures.append("Many extreme probability values")

            # Heuristic accuracy based on reasoning quality
            heuristic_accuracy = 0.7  # Default heuristic accuracy
            confidence = 0.5  # Low confidence without ground truth

        else:
            # Ground truth available - perform detailed accuracy assessment
            accuracy_measures.append("Ground truth available for accuracy assessment")

            # Compare key results
            accuracy_scores = []

            # Compare final conclusions
            if "conclusion" in reasoning_result and "conclusion" in ground_truth:
                result_conclusion = str(reasoning_result["conclusion"]).lower()
                truth_conclusion = str(ground_truth["conclusion"]).lower()

                # Simple text similarity (in production, use more sophisticated methods)
                common_words = set(result_conclusion.split()) & set(
                    truth_conclusion.split()
                )
                similarity = len(common_words) / max(
                    len(result_conclusion.split()), len(truth_conclusion.split())
                )
                accuracy_scores.append(similarity)
                accuracy_measures.append(f"Conclusion similarity: {similarity:.2f}")

            # Compare probability distributions
            if "probabilities" in reasoning_result and "probabilities" in ground_truth:
                result_probs = reasoning_result["probabilities"]
                truth_probs = ground_truth["probabilities"]

                if isinstance(result_probs, dict) and isinstance(truth_probs, dict):
                    # Calculate KL divergence or similar metric
                    common_keys = set(result_probs.keys()) & set(truth_probs.keys())
                    if common_keys:
                        differences = []
                        for key in common_keys:
                            diff = abs(result_probs[key] - truth_probs[key])
                            differences.append(diff)

                        avg_difference = sum(differences) / len(differences)
                        prob_accuracy = max(0, 1 - avg_difference)
                        accuracy_scores.append(prob_accuracy)
                        accuracy_measures.append(
                            f"Probability accuracy: {prob_accuracy:.2f}"
                        )

            # Calculate overall accuracy
            if accuracy_scores:
                heuristic_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                confidence = 0.9
            else:
                heuristic_accuracy = 0.5
                confidence = 0.3
                accuracy_measures.append(
                    "Limited comparable elements with ground truth"
                )

        return QualityScore(
            metric=QualityMetric.ACCURACY,
            score=heuristic_accuracy,
            confidence=confidence,
            explanation="Accuracy assessed against ground truth or using heuristic methods",
            evidence=accuracy_measures,
        )

    async def _evaluate_relevance(self, request: EvaluationRequest) -> QualityScore:
        """Evaluate relevance to the input context"""
        reasoning_result = request.reasoning_result
        context = request.context

        relevance_indicators = []

        if context is None:
            relevance_indicators.append("No context provided for relevance assessment")
            relevance_score = 0.6  # Default relevance
            confidence = 0.4
        else:
            # Extract key terms from context
            context_words = set(context.lower().split())
            result_text = str(reasoning_result).lower()
            result_words = set(result_text.split())

            # Calculate word overlap
            overlap = context_words & result_words
            overlap_ratio = len(overlap) / len(context_words) if context_words else 0

            relevance_indicators.append(f"Word overlap ratio: {overlap_ratio:.2f}")

            # Check if reasoning addresses the main context topics
            context_topics = [
                word for word in context_words if len(word) > 4
            ]  # Longer words as topics
            topic_coverage = sum(1 for topic in context_topics if topic in result_text)
            topic_ratio = topic_coverage / len(context_topics) if context_topics else 0

            relevance_indicators.append(f"Topic coverage: {topic_ratio:.2f}")

            # Calculate relevance score
            relevance_score = overlap_ratio * 0.6 + topic_ratio * 0.4
            confidence = 0.8

            if relevance_score > 0.7:
                relevance_indicators.append("High relevance to context")
            elif relevance_score > 0.4:
                relevance_indicators.append("Moderate relevance to context")
            else:
                relevance_indicators.append("Low relevance to context")

        return QualityScore(
            metric=QualityMetric.RELEVANCE,
            score=relevance_score,
            confidence=confidence,
            explanation="Relevance assessed based on context overlap and topic coverage",
            evidence=relevance_indicators,
        )

    async def _evaluate_uncertainty(self, request: EvaluationRequest) -> QualityScore:
        """Evaluate uncertainty quantification quality"""
        reasoning_result = request.reasoning_result

        uncertainty_factors = []

        # Check for explicit uncertainty measures
        uncertainty_keywords = [
            "uncertainty",
            "confidence",
            "probability",
            "likely",
            "uncertain",
            "possible",
        ]
        result_text = str(reasoning_result).lower()
        uncertainty_mentions = sum(
            1 for keyword in uncertainty_keywords if keyword in result_text
        )

        if uncertainty_mentions > 0:
            uncertainty_factors.append(
                f"Uncertainty mentioned {uncertainty_mentions} times"
            )
        else:
            uncertainty_factors.append("No explicit uncertainty quantification")

        # Check for confidence values
        confidence_present = False
        if "confidence" in reasoning_result:
            confidence_val = reasoning_result["confidence"]
            if isinstance(confidence_val, (int, float)) and 0 <= confidence_val <= 1:
                uncertainty_factors.append(f"Valid confidence value: {confidence_val}")
                confidence_present = True
            else:
                uncertainty_factors.append("Invalid confidence value")

        # Check for probability distributions
        prob_distributions = False
        if "probabilities" in reasoning_result:
            probs = reasoning_result["probabilities"]
            if isinstance(probs, dict) and len(probs) > 1:
                uncertainty_factors.append("Probability distribution provided")
                prob_distributions = True
            else:
                uncertainty_factors.append("Limited probability information")

        # Check for uncertainty bounds or intervals
        interval_keywords = ["range", "interval", "between", "from", "to"]
        interval_mentions = sum(
            1 for keyword in interval_keywords if keyword in result_text
        )

        if interval_mentions > 0:
            uncertainty_factors.append("Uncertainty bounds or intervals mentioned")
        else:
            uncertainty_factors.append("No uncertainty bounds provided")

        # Calculate uncertainty score
        base_score = 0.3  # Base uncertainty handling
        if uncertainty_mentions > 2:
            base_score += 0.2
        if confidence_present:
            base_score += 0.2
        if prob_distributions:
            base_score += 0.2
        if interval_mentions > 0:
            base_score += 0.1

        uncertainty_score = min(1.0, base_score)
        confidence = 0.8

        return QualityScore(
            metric=QualityMetric.UNCERTAINTY,
            score=uncertainty_score,
            confidence=confidence,
            explanation="Uncertainty assessment based on explicit quantification and probability handling",
            evidence=uncertainty_factors,
        )

    async def _evaluate_explainability(
        self, request: EvaluationRequest
    ) -> QualityScore:
        """Evaluate explainability and interpretability"""
        reasoning_result = request.reasoning_result

        explainability_factors = []

        # Check for reasoning steps
        if "reasoning_steps" in reasoning_result:
            steps = reasoning_result["reasoning_steps"]
            if isinstance(steps, list) and steps:
                explainability_factors.append(f"Reasoning steps provided: {len(steps)}")
            else:
                explainability_factors.append("No clear reasoning steps")
        else:
            explainability_factors.append("Missing reasoning steps")

        # Check for explanations or justifications
        explanation_keywords = [
            "because",
            "since",
            "therefore",
            "due to",
            "as a result",
            "explanation",
        ]
        result_text = str(reasoning_result).lower()
        explanation_count = sum(
            1 for keyword in explanation_keywords if keyword in result_text
        )

        if explanation_count > 0:
            explainability_factors.append(
                f"Explanatory language used {explanation_count} times"
            )
        else:
            explainability_factors.append("Limited explanatory language")

        # Check for evidence or supporting information
        if "evidence" in reasoning_result or "supporting_facts" in reasoning_result:
            explainability_factors.append("Supporting evidence provided")
        else:
            explainability_factors.append("No supporting evidence")

        # Check for clear structure and organization
        structured_elements = ["conclusion", "summary", "analysis", "findings"]
        structure_count = sum(
            1 for element in structured_elements if element in reasoning_result
        )

        if structure_count >= 2:
            explainability_factors.append("Well-structured output")
        else:
            explainability_factors.append("Limited structure")

        # Calculate explainability score
        base_score = 0.4  # Base explainability
        if "reasoning_steps" in reasoning_result:
            base_score += 0.3
        if explanation_count > 2:
            base_score += 0.2
        if structure_count >= 2:
            base_score += 0.1

        explainability_score = min(1.0, base_score)
        confidence = 0.75

        return QualityScore(
            metric=QualityMetric.EXPLAINABILITY,
            score=explainability_score,
            confidence=confidence,
            explanation="Explainability assessed based on reasoning steps, explanatory language, and structure",
            evidence=explainability_factors,
        )

    def _calculate_overall_quality(self, quality_scores: List[QualityScore]) -> float:
        """Calculate weighted overall quality score"""
        if not quality_scores:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for score in quality_scores:
            weight = self.weight_matrix.get(score.metric, 1.0 / len(quality_scores))
            weighted_sum += score.score * weight * score.confidence
            total_weight += weight * score.confidence

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _assess_performance_metrics(
        self, request: EvaluationRequest
    ) -> PerformanceMetrics:
        """Assess performance metrics of the reasoning system"""
        reasoning_result = request.reasoning_result

        # Extract or estimate performance metrics
        execution_time = reasoning_result.get(
            "execution_time", 30.0
        )  # Default 30 seconds
        memory_usage = reasoning_result.get("memory_usage", 256.0)  # Default 256 MB

        # Calculate accuracy based on quality scores (if available)
        accuracy = reasoning_result.get("accuracy", 0.8)  # Default accuracy

        # Estimate precision and recall (simplified)
        precision = accuracy * 0.9  # Precision usually slightly lower than accuracy
        recall = accuracy * 0.85  # Recall typically lower than precision

        # Calculate F1 score
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        # Convergence rate based on consistency
        convergence_rate = 0.9 if reasoning_result.get("converged", True) else 0.7

        # Error rate (inverse of accuracy)
        error_rate = 1.0 - accuracy

        return PerformanceMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            execution_time=execution_time,
            memory_usage=memory_usage,
            convergence_rate=convergence_rate,
            error_rate=error_rate,
        )

    async def _analyze_consistency(self, request: EvaluationRequest) -> Dict[str, Any]:
        """Analyze internal consistency of reasoning"""
        reasoning_result = request.reasoning_result

        consistency_analysis = {
            "internal_consistency": True,
            "consistency_score": 0.8,
            "inconsistencies": [],
            "consistency_checks": [],
        }

        # Check for numerical consistency
        numbers = []
        result_text = str(reasoning_result)
        import re

        number_matches = re.findall(r"\d+\.?\d*", result_text)

        for match in number_matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue

        if numbers:
            # Check for reasonable number ranges
            if all(0 <= n <= 1 for n in numbers if n <= 1):
                consistency_analysis["consistency_checks"].append(
                    "Probability values in valid range"
                )
            else:
                invalid_probs = [n for n in numbers if n > 1 or n < 0]
                if invalid_probs:
                    consistency_analysis["inconsistencies"].append(
                        f"Invalid probability values: {invalid_probs}"
                    )

        # Check logical consistency
        if "conclusion" in reasoning_result and "reasoning_steps" in reasoning_result:
            # Simple check: conclusion should be supported by reasoning steps
            conclusion = str(reasoning_result["conclusion"]).lower()
            steps_text = str(reasoning_result["reasoning_steps"]).lower()

            # Check if key terms from conclusion appear in reasoning steps
            conclusion_words = set(conclusion.split())
            steps_words = set(steps_text.split())
            overlap = conclusion_words & steps_words

            if len(overlap) > len(conclusion_words) * 0.3:
                consistency_analysis["consistency_checks"].append(
                    "Conclusion supported by reasoning steps"
                )
            else:
                consistency_analysis["inconsistencies"].append(
                    "Limited support for conclusion in reasoning steps"
                )

        # Update consistency score based on inconsistencies
        if consistency_analysis["inconsistencies"]:
            consistency_analysis["consistency_score"] *= 0.7
            consistency_analysis["internal_consistency"] = False

        return consistency_analysis

    async def _analyze_decision_boundaries(
        self, request: EvaluationRequest
    ) -> Dict[str, Any]:
        """Analyze decision boundaries and thresholds"""
        reasoning_result = request.reasoning_result

        decision_analysis = {
            "decision_points": [],
            "threshold_analysis": {},
            "boundary_clarity": 0.7,
            "decision_confidence": 0.8,
        }

        # Look for decision points in reasoning
        decision_keywords = ["decide", "choose", "select", "determine", "conclude"]
        result_text = str(reasoning_result).lower()

        for keyword in decision_keywords:
            if keyword in result_text:
                decision_analysis["decision_points"].append(
                    f"Decision keyword found: {keyword}"
                )

        # Analyze thresholds if probabilities are present
        if "probabilities" in reasoning_result:
            probs = reasoning_result["probabilities"]
            if isinstance(probs, dict):
                prob_values = [v for v in probs.values() if isinstance(v, (int, float))]
                if prob_values:
                    max_prob = max(prob_values)
                    min_prob = min(prob_values)
                    prob_range = max_prob - min_prob

                    decision_analysis["threshold_analysis"] = {
                        "max_probability": max_prob,
                        "min_probability": min_prob,
                        "probability_range": prob_range,
                        "clear_decision": max_prob
                        > 0.7,  # Clear decision if max prob > 0.7
                    }

                    # Update boundary clarity
                    if prob_range > 0.5:
                        decision_analysis["boundary_clarity"] = 0.9
                    elif prob_range > 0.3:
                        decision_analysis["boundary_clarity"] = 0.7
                    else:
                        decision_analysis["boundary_clarity"] = 0.5

        return decision_analysis

    async def _generate_recommendations(
        self,
        quality_scores: List[QualityScore],
        performance_metrics: PerformanceMetrics,
        consistency_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Quality-based recommendations
        for score in quality_scores:
            threshold = self.quality_thresholds.get(score.metric, 0.7)
            if score.score < threshold:
                if score.metric == QualityMetric.COHERENCE:
                    recommendations.append(
                        "Improve logical flow and reduce contradictions in reasoning"
                    )
                elif score.metric == QualityMetric.CONSISTENCY:
                    recommendations.append(
                        "Ensure probability values are normalized and components align"
                    )
                elif score.metric == QualityMetric.COMPLETENESS:
                    recommendations.append(
                        "Include more reasoning steps and uncertainty quantification"
                    )
                elif score.metric == QualityMetric.ACCURACY:
                    recommendations.append(
                        "Validate results against ground truth or domain expertise"
                    )
                elif score.metric == QualityMetric.RELEVANCE:
                    recommendations.append(
                        "Ensure reasoning addresses the input context more directly"
                    )
                elif score.metric == QualityMetric.UNCERTAINTY:
                    recommendations.append(
                        "Provide explicit confidence intervals and uncertainty bounds"
                    )
                elif score.metric == QualityMetric.EXPLAINABILITY:
                    recommendations.append(
                        "Add more detailed reasoning steps and explanatory language"
                    )

        # Performance-based recommendations
        if (
            performance_metrics.execution_time
            > self.performance_benchmarks["execution_time_max"]
        ):
            recommendations.append(
                "Optimize computation time - consider parallel processing or approximations"
            )

        if (
            performance_metrics.memory_usage
            > self.performance_benchmarks["memory_usage_max"]
        ):
            recommendations.append(
                "Reduce memory usage - implement streaming or batch processing"
            )

        if performance_metrics.accuracy < self.performance_benchmarks["accuracy_min"]:
            recommendations.append(
                "Improve model accuracy through better training data or algorithms"
            )

        # Consistency-based recommendations
        if not consistency_analysis.get("internal_consistency", True):
            recommendations.append(
                "Address internal inconsistencies identified in the analysis"
            )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Overall quality is good - consider minor refinements for specific use cases"
            )

        return recommendations

    def _calculate_evaluation_confidence(
        self,
        quality_scores: List[QualityScore],
        performance_metrics: PerformanceMetrics,
    ) -> float:
        """Calculate confidence in the evaluation itself"""
        if not quality_scores:
            return 0.0

        # Average confidence of individual quality scores
        avg_quality_confidence = sum(
            score.confidence for score in quality_scores
        ) / len(quality_scores)

        # Performance reliability factor
        performance_factor = 1.0
        if performance_metrics.execution_time > 0:
            performance_factor = min(
                1.0, 60.0 / performance_metrics.execution_time
            )  # Penalize very slow execution

        # Number of metrics evaluated factor
        completeness_factor = min(1.0, len(quality_scores) / len(QualityMetric))

        # Overall evaluation confidence
        evaluation_confidence = (
            avg_quality_confidence * performance_factor * completeness_factor
        )

        return min(1.0, max(0.0, evaluation_confidence))


# Export the agent class
__all__ = [
    "EvaluationAgent",
    "EvaluationRequest",
    "EvaluationResult",
    "QualityMetric",
    "QualityScore",
]
