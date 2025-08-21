"""
MSA Synthesis Engine - Orchestrates Mode 1 and Mode 2 for complete reasoning
"""

from datetime import datetime
import logging
import time
from typing import Any, Dict, List, Optional

from reasoning_kernel.core.kernel_config import KernelManager
from reasoning_kernel.msa.confidence_indicator import ConfidenceIndicator
from reasoning_kernel.msa.mode1_knowledge import KnowledgeExtractor
from reasoning_kernel.msa.mode2_probabilistic import (
    ProbabilisticModelSynthesizer,
)
from reasoning_kernel.msa.neural_program_synthesis import (
    NeuralProgramSynthesizer,
)
from reasoning_kernel.utils.reasoning_chains import ReasoningChain


logger = logging.getLogger(__name__)


class MSAEngine:
    """
    Main MSA Engine that orchestrates both modes of reasoning:
    - Mode 1: LLM-powered knowledge retrieval
    - Mode 2: Dynamic probabilistic model synthesis
    """

    def __init__(
        self,
        kernel_manager: KernelManager,
        memory_service: Optional[Any] = None,
        retrieval_service: Optional[Any] = None,
    ):
        self.kernel_manager = kernel_manager
        self.memory_service = memory_service
        self.retrieval_service = retrieval_service
        self.knowledge_extractor = None
        self.probabilistic_synthesizer = None
        self.neural_program_synthesizer = None
        self.confidence_indicator = None
        self.reasoning_chain = None
        self.active_sessions = {}

    async def initialize(self):
        """Initialize the MSA Engine components"""
        try:
            logger.info("Initializing MSA Engine components...")

            # Initialize Mode 1: Knowledge Extractor
            self.knowledge_extractor = KnowledgeExtractor(self.kernel_manager)
            logger.info("✅ Mode 1 (Knowledge Extractor) initialized")

            # Initialize Mode 2: Probabilistic Synthesizer
            self.probabilistic_synthesizer = ProbabilisticModelSynthesizer()
            logger.info("✅ Mode 2 (Probabilistic Synthesizer) initialized")

            # Initialize Neural Program Synthesizer (MSA paper enhancement)
            self.neural_program_synthesizer = NeuralProgramSynthesizer(self.kernel_manager)
            logger.info("✅ Neural Program Synthesizer initialized")

            # Initialize Confidence Indicator
            self.confidence_indicator = ConfidenceIndicator()
            logger.info("✅ Confidence Indicator initialized")

            # Initialize Reasoning Chain tracker
            self.reasoning_chain = ReasoningChain()
            logger.info("✅ Reasoning Chain tracker initialized")

            logger.info("🎯 MSA Engine initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize MSA Engine: {e}")
            raise

    async def reason_about_scenario(
        self, scenario: str, session_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main reasoning method that orchestrates both modes

        Args:
            scenario: The scenario or question to reason about
            session_id: Optional session ID for tracking
            context: Optional additional context or constraints

        Returns:
            Complete reasoning results with explanations
        """
        # Check if engine is properly initialized
        if not self.knowledge_extractor:
            raise RuntimeError("MSA Engine not initialized. Call initialize() first.")
        if not self.probabilistic_synthesizer:
            raise RuntimeError("Probabilistic Synthesizer not initialized. Call initialize() first.")
        if not self.neural_program_synthesizer:
            raise RuntimeError("Neural Program Synthesizer not initialized. Call initialize() first.")
        if not self.confidence_indicator:
            raise RuntimeError("Confidence Indicator not initialized. Call initialize() first.")

        start_time = time.time()
        session_id = session_id or f"session_{int(time.time())}"

        try:
            logger.info(f"Starting MSA reasoning for session {session_id}")

            # Check for similar reasoning chains in Redis
            if self.retrieval_service:
                similar_chains = await self.retrieval_service.find_similar_reasoning_chains(
                    current_chain={"scenario": scenario, "context": context}, limit=3
                )
                if similar_chains:
                    logger.info(f"📚 Found {len(similar_chains)} similar reasoning chains in memory")
                    # Use similar chains as additional context
                    if context is None:
                        context = {}
                    context["similar_chains"] = similar_chains

            # Initialize reasoning chain for this session
            reasoning_chain = ReasoningChain(session_id)
            reasoning_chain.start_reasoning(scenario, context)

            # Store active session
            self.active_sessions[session_id] = {
                "start_time": datetime.now(),
                "scenario": scenario,
                "status": "processing",
            }

            # Phase 1: Knowledge Extraction (Mode 1)
            logger.info("🔍 Phase 1: Knowledge Extraction (Mode 1)")
            reasoning_chain.add_step("knowledge_extraction", "Starting knowledge extraction using LLM")

            knowledge_base = await self.knowledge_extractor.extract_scenario_knowledge(scenario)
            reasoning_chain.add_step("knowledge_extracted", "Knowledge extraction completed", knowledge_base)

            # Generate model specifications
            model_specs = await self.knowledge_extractor.generate_model_specifications(knowledge_base)
            reasoning_chain.add_step("model_specs_generated", "Model specifications generated", model_specs)

            # Phase 2: Probabilistic Model Synthesis (Mode 2)
            logger.info("🧮 Phase 2: Probabilistic Model Synthesis (Mode 2)")
            reasoning_chain.add_step("probabilistic_synthesis", "Starting probabilistic model synthesis")

            scenario_data = context or {}
            synthesis_results = await self.probabilistic_synthesizer.synthesize_model(model_specs, scenario_data)
            reasoning_chain.add_step("synthesis_completed", "Probabilistic synthesis completed", synthesis_results)

            # Phase 3: Integration and Final Reasoning
            logger.info("🔗 Phase 3: Integration and Final Reasoning")
            final_reasoning = await self._integrate_results(
                knowledge_base, synthesis_results, scenario, reasoning_chain
            )

            # Phase 4: Calculate Confidence Metrics
            logger.info("📊 Phase 4: Confidence Analysis")
            reasoning_chain.add_step("confidence_analysis", "Calculating confidence metrics")

            confidence_data = {
                "knowledge_base": knowledge_base,
                "model_specs": model_specs,
                "synthesis_results": synthesis_results,
                "final_reasoning": final_reasoning,
            }

            processing_time = time.time() - start_time
            metadata = {
                "processing_time_seconds": processing_time,
                "mode1_entities": len(knowledge_base.get("entities", [])),
                "mode2_variables": len(model_specs.get("variables", [])),
                "session_id": session_id,
            }

            confidence_metrics = self.confidence_indicator.calculate_confidence(confidence_data, metadata)

            # Add confidence metrics to final reasoning
            final_reasoning["confidence_metrics"] = {
                "overall_score": confidence_metrics.overall_score,
                "confidence_level": confidence_metrics.confidence_level.value,
                "knowledge_extraction_score": confidence_metrics.knowledge_extraction_score,
                "model_synthesis_score": confidence_metrics.model_synthesis_score,
                "uncertainty_quantification_score": confidence_metrics.uncertainty_quantification_score,
                "integration_coherence_score": confidence_metrics.integration_coherence_score,
                "completeness_metrics": confidence_metrics.completeness_metrics,
                "reliability_metrics": confidence_metrics.reliability_metrics,
                "consistency_metrics": confidence_metrics.consistency_metrics,
                "confidence_explanation": confidence_metrics.confidence_explanation,
                "improvement_suggestions": confidence_metrics.improvement_suggestions,
                "risk_factors": confidence_metrics.risk_factors,
            }

            reasoning_chain.add_step(
                "confidence_calculated",
                "Confidence analysis completed",
                {
                    "overall_score": confidence_metrics.overall_score,
                    "confidence_level": confidence_metrics.confidence_level.value,
                },
            )

            # Complete reasoning chain
            reasoning_chain.complete_reasoning(final_reasoning, processing_time)

            # Update session status
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["processing_time"] = processing_time

            # Store reasoning chain in Redis and PostgreSQL if available
            if self.memory_service:
                chain_data = {
                    "scenario": scenario,
                    "context": context,
                    "chain": reasoning_chain.get_chain(),
                    "knowledge_base": knowledge_base,
                    "model_specs": model_specs,
                    "synthesis_results": synthesis_results,
                    "final_reasoning": final_reasoning,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat(),
                }
                await self.memory_service.store_reasoning_chain(
                    chain_id=session_id, chain_data=chain_data, ttl=3600 * 24  # Store for 24 hours
                )
                logger.info(f"💾 Stored reasoning chain in Redis: {session_id}")

                # Also save to PostgreSQL for long-term storage
                await self._save_to_postgresql(session_id, scenario, chain_data, processing_time)

                # Store knowledge entities in Redis
                for entity in knowledge_base.get("entities", []):
                    await self.memory_service.store_knowledge(
                        knowledge_type="entity",
                        knowledge_id=f"{session_id}_{entity.get('name', 'unknown')}",
                        knowledge_data=entity,
                        tags=[scenario[:30], entity.get("type", "unknown")],
                        ttl=3600 * 24 * 7,  # Store for 7 days
                    )

                # Store session data
                await self.memory_service.create_session(
                    session_id=session_id,
                    session_data={
                        "scenario": scenario,
                        "status": "completed",
                        "processing_time": processing_time,
                        "summary": final_reasoning.get("summary", ""),
                        "confidence": confidence_metrics.overall_score,
                        "confidence_level": confidence_metrics.confidence_level.value,
                    },
                )

            # Compile final response
            response = {
                "session_id": session_id,
                "scenario": scenario,
                "reasoning_chain": reasoning_chain.get_chain(),
                "knowledge_base": knowledge_base,
                "model_specifications": model_specs,
                "probabilistic_analysis": synthesis_results,
                "final_reasoning": final_reasoning,
                "metadata": {
                    "processing_time_seconds": processing_time,
                    "mode1_entities": len(knowledge_base.get("entities", [])),
                    "mode2_variables": len(model_specs.get("variables", [])),
                    "uncertainty_level": synthesis_results.get("uncertainty_analysis", {})
                    .get("overall_assessment", {})
                    .get("uncertainty_level", "unknown"),
                    "model_confidence": confidence_metrics.overall_score,
                    "confidence_level": confidence_metrics.confidence_level.value,
                    "timestamp": datetime.now().isoformat(),
                },
                "success": True,
            }

            logger.info(f"✅ MSA reasoning completed for session {session_id} in {processing_time:.2f}s")
            return response

        except Exception as e:
            sanitized_session_id = session_id.replace("\r", "").replace("\n", "")
            logger.error(f"❌ MSA reasoning failed for session {sanitized_session_id}: {e}")

            # Update session status
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["status"] = "failed"
                self.active_sessions[session_id]["error"] = str(e)

            return {
                "session_id": session_id,
                "scenario": scenario,
                "error": str(e),
                "error_type": type(e).__name__,
                "metadata": {
                    "processing_time_seconds": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                },
                "success": False,
            }

    async def _integrate_results(
        self,
        knowledge_base: Dict[str, Any],
        synthesis_results: Dict[str, Any],
        original_scenario: str,
        reasoning_chain: ReasoningChain,
    ) -> Dict[str, Any]:
        """
        Integrate results from both modes to generate final reasoning
        """
        try:
            reasoning_chain.add_step("integration", "Integrating Mode 1 and Mode 2 results")

            # Extract key insights
            entities = knowledge_base.get("entities", [])
            relationships = knowledge_base.get("relationships", [])
            causal_factors = knowledge_base.get("causal_factors", [])

            uncertainty_analysis = synthesis_results.get("uncertainty_analysis", {})
            predictions = synthesis_results.get("predictions", {})

            # Generate integrated reasoning using LLM
            integration_prompt = f"""
            You are an expert reasoning system. Integrate the following analysis to provide comprehensive reasoning about the scenario.
            
            Original Scenario: {original_scenario}
            
            Mode 1 Knowledge Analysis:
            - Entities identified: {len(entities)}
            - Key relationships: {len(relationships)}
            - Causal factors: {len(causal_factors)}
            
            Mode 2 Probabilistic Analysis:
            - Model confidence: {uncertainty_analysis.get('overall_assessment', {}).get('model_confidence', 'unknown')}
            - Uncertainty level: {uncertainty_analysis.get('overall_assessment', {}).get('uncertainty_level', 'unknown')}
            - Variables modeled: {list(predictions.get('predictive_distributions', {}).keys())}
            
            Provide a comprehensive reasoning response that:
            1. Summarizes the key findings from both analysis modes
            2. Explains the causal relationships and their implications
            3. Discusses the uncertainty and confidence in the analysis
            4. Provides actionable insights or recommendations
            5. Identifies any limitations or areas requiring additional information
            
            Format your response as clear, structured reasoning that a decision-maker could use.
            """

            integrated_reasoning_text = await self.kernel_manager.invoke_prompt(integration_prompt)

            # Create structured final reasoning
            final_reasoning = {
                "summary": integrated_reasoning_text,
                "key_insights": {
                    "primary_entities": [e.get("name", "") for e in entities[:5]],
                    "critical_relationships": len([r for r in relationships if r.get("strength") == "strong"]),
                    "high_impact_factors": [
                        f.get("factor", "") for f in causal_factors if f.get("probability") == "high"
                    ],
                    "model_confidence_score": uncertainty_analysis.get("overall_assessment", {}).get(
                        "model_confidence", 0.0
                    ),
                },
                "recommendations": await self._generate_recommendations(
                    knowledge_base, synthesis_results, original_scenario
                ),
                "uncertainty_assessment": {
                    "overall_level": uncertainty_analysis.get("overall_assessment", {}).get(
                        "uncertainty_level", "unknown"
                    ),
                    "confidence_score": uncertainty_analysis.get("overall_assessment", {}).get("model_confidence", 0.0),
                    "key_uncertainties": list(uncertainty_analysis.get("epistemic_uncertainty", {}).keys())[:5],
                },
                "reasoning_quality": {
                    "knowledge_extraction_completeness": min(100, len(entities) * 20),  # Simple heuristic
                    "model_synthesis_success": synthesis_results.get("success", False),
                    "integration_coherence": "high" if len(integrated_reasoning_text) > 200 else "moderate",
                },
            }

            reasoning_chain.add_step("integration_completed", "Results integration completed", final_reasoning)
            return final_reasoning

        except Exception as e:
            logger.error(f"Failed to integrate results: {e}")
            return {"summary": f"Integration failed: {str(e)}", "error": str(e), "partial_results": True}

    async def _generate_recommendations(
        self, knowledge_base: Dict[str, Any], synthesis_results: Dict[str, Any], scenario: str
    ) -> List[str]:
        """Generate actionable recommendations based on the analysis"""
        try:
            prompt = f"""
            Based on the analysis of this scenario: {scenario}
            
            Key findings:
            - Entities: {[e.get('name') for e in knowledge_base.get('entities', [])[:3]]}
            - Critical factors: {[f.get('factor') for f in knowledge_base.get('causal_factors', []) if f.get('probability') == 'high'][:3]}
            - Model confidence: {synthesis_results.get('uncertainty_analysis', {}).get('overall_assessment', {}).get('model_confidence', 0)}
            
            Generate 3-5 specific, actionable recommendations. Return as a simple list, one recommendation per line.
            """

            recommendations_text = await self.kernel_manager.invoke_prompt(prompt)
            recommendations = [line.strip() for line in recommendations_text.split("\n") if line.strip()]

            return recommendations[:5]  # Limit to 5 recommendations

        except Exception as e:
            logger.warning(f"Failed to generate recommendations: {e}")
            return ["Further analysis recommended due to processing limitations."]

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a reasoning session"""
        return self.active_sessions.get(session_id)

    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active reasoning sessions"""
        return [
            {
                "session_id": sid,
                "status": info["status"],
                "start_time": info["start_time"].isoformat(),
                "scenario_preview": info["scenario"][:100] + "..." if len(info["scenario"]) > 100 else info["scenario"],
            }
            for sid, info in self.active_sessions.items()
        ]

    async def _save_to_postgresql(
        self, session_id: str, scenario: str, chain_data: Dict[str, Any], processing_time: float
    ):
        """Save reasoning chain to PostgreSQL for long-term storage"""
        try:
            # Import here to avoid circular dependencies
            import json

            from reasoning_kernel.database.connection import get_db_manager
            from reasoning_kernel.database.models import (
                ReasoningChain as DBReasoningChain,
            )
            from reasoning_kernel.database.models import KnowledgeEntity
            from reasoning_kernel.database.models import Session

            db_manager = get_db_manager()
            with next(db_manager.get_db()) as db:
                # Create or update session
                db_session = db.query(Session).filter_by(id=session_id).first()
                if not db_session:
                    db_session = Session(id=session_id, user_id="default_user", purpose="reasoning", status="completed")
                    db.add(db_session)
                    db.commit()

                # Store reasoning chain with proper field mapping
                knowledge_base = chain_data.get("knowledge_base", {})
                synthesis_results = chain_data.get("synthesis_results", {})
                final_reasoning = chain_data.get("final_reasoning", {})

                db_chain = DBReasoningChain(
                    id=session_id,
                    session_id=session_id,
                    scenario=scenario,
                    # Mode 1 outputs
                    mode1_entities=json.dumps(knowledge_base.get("entities", [])),
                    mode1_relationships=json.dumps(knowledge_base.get("relationships", [])),
                    mode1_causal_factors=json.dumps(knowledge_base.get("causal_factors", [])),
                    mode1_constraints=json.dumps(knowledge_base.get("constraints", [])),
                    mode1_domain_knowledge=json.dumps(knowledge_base.get("domain_knowledge", [])),
                    # Mode 2 outputs
                    mode2_model_structure=json.dumps(chain_data.get("model_specs", {})),
                    mode2_predictions=json.dumps(synthesis_results.get("predictions", {})),
                    mode2_uncertainties=json.dumps(synthesis_results.get("uncertainty_analysis", {})),
                    mode2_success=str(synthesis_results.get("success", False)),
                    # Final reasoning
                    final_summary=final_reasoning.get("summary", ""),
                    final_insights=json.dumps(final_reasoning.get("insights", {})),
                    final_recommendations=json.dumps(final_reasoning.get("recommendations", [])),
                    final_uncertainty=json.dumps(final_reasoning.get("uncertainty_assessment", {})),
                    # Metadata
                    reasoning_steps=json.dumps(chain_data.get("chain", [])),
                    total_duration_ms=int(processing_time * 1000),
                )
                db.add(db_chain)

                # Store knowledge entities
                for entity in knowledge_base.get("entities", []):
                    db_entity = KnowledgeEntity(
                        entity_type="entity",
                        name=entity.get("name", "unknown"),
                        description=entity.get("description", ""),
                        properties=json.dumps(entity),
                    )
                    db.add(db_entity)

                db.commit()
                logger.info(f"✅ Saved reasoning chain to PostgreSQL: {session_id}")

        except Exception as e:
            logger.error(f"Failed to save to PostgreSQL: {e}")
            # Don't fail the entire operation if PostgreSQL save fails

    async def cleanup(self):
        """Cleanup MSA Engine resources"""
        try:
            if self.probabilistic_synthesizer:
                await self.probabilistic_synthesizer.cleanup()

            # Clear active sessions
            self.active_sessions.clear()

            logger.info("MSA Engine cleanup completed")

        except Exception as e:
            logger.error(f"Error during MSA Engine cleanup: {e}")
