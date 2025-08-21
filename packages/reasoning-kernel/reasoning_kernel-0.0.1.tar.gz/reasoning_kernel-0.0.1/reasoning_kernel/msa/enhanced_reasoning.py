"""
Enhanced Reasoning with Neural Program Synthesis
Implements advanced MSA capabilities inspired by research paper 2507.12547
"""

import time
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

class EnhancedMSAReasoning:
    """
    Enhanced MSA reasoning that combines traditional Mode 1/Mode 2 with neural program synthesis
    for handling open-world scenarios and novel causal structures.
    """
    
    def __init__(self, msa_engine):
        self.msa_engine = msa_engine
        
    async def reason_with_neural_synthesis(self, 
                                         scenario: str,
                                         context: Optional[Dict[str, Any]] = None,
                                         synthesis_mode: str = "hybrid") -> Dict[str, Any]:
        """
        Enhanced reasoning using neural program synthesis approach from MSA paper.
        
        Args:
            scenario: The scenario to analyze
            context: Additional context including novel variables and causal structure
            synthesis_mode: "neural_only", "traditional", "hybrid"
            
        Returns:
            Enhanced reasoning results with neural program synthesis
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting enhanced MSA reasoning with {synthesis_mode} mode")
            
            # Phase 1: Enhanced Knowledge Extraction
            knowledge_base = await self.msa_engine.knowledge_extractor.extract_scenario_knowledge(scenario)
            
            if synthesis_mode in ["neural_only", "hybrid"]:
                # Phase 2a: Neural Program Synthesis
                logger.info("🧠 Applying neurally-guided program synthesis")
                neural_program = await self.msa_engine.neural_program_synthesizer.synthesize_probabilistic_program(
                    scenario, knowledge_base
                )
                
                # Analyze the synthesized program
                program_analysis = await self._analyze_synthesized_program(neural_program, context)
                
                if synthesis_mode == "neural_only":
                    # Use only neural synthesis results
                    reasoning_results = {
                        "approach": "neural_program_synthesis",
                        "knowledge_extraction": knowledge_base,
                        "neural_program": neural_program,
                        "program_analysis": program_analysis,
                        "traditional_synthesis": None
                    }
                else:
                    # Hybrid: combine neural synthesis with traditional approach
                    traditional_results = await self._run_traditional_synthesis(knowledge_base, context)
                    reasoning_results = await self._integrate_neural_and_traditional(
                        neural_program, traditional_results, knowledge_base, context
                    )
            else:
                # Traditional MSA approach only
                traditional_results = await self._run_traditional_synthesis(knowledge_base, context)
                reasoning_results = {
                    "approach": "traditional_msa",
                    "knowledge_extraction": knowledge_base,
                    "neural_program": None,
                    "traditional_synthesis": traditional_results,
                    "integration": None
                }
            
            # Enhanced analysis for open-world reasoning
            open_world_analysis = await self._analyze_open_world_capabilities(
                reasoning_results, scenario, context
            )
            
            # Novel variable handling assessment
            novel_variable_analysis = await self._analyze_novel_variable_handling(
                reasoning_results, context
            )
            
            # Causal structure learning evaluation
            causal_analysis = await self._analyze_causal_structure_learning(
                reasoning_results, context
            )
            
            processing_time = time.time() - start_time
            
            final_results = {
                "reasoning_results": reasoning_results,
                "enhanced_analysis": {
                    "open_world_reasoning": open_world_analysis,
                    "novel_variable_handling": novel_variable_analysis,
                    "causal_structure_learning": causal_analysis,
                    "synthesis_approach": synthesis_mode,
                    "processing_time": processing_time
                },
                "msa_paper_alignment": {
                    "neurally_guided_synthesis": synthesis_mode in ["neural_only", "hybrid"],
                    "open_world_adaptation": True,
                    "causal_modeling": len(knowledge_base.get("causal_factors", [])) > 0,
                    "novel_scenario_handling": context and context.get("scenario_type") == "model_olympics"
                },
                "success": True,
                "processing_time": processing_time
            }
            
            logger.info("✅ Enhanced MSA reasoning completed successfully")
            return final_results
            
        except Exception as e:
            logger.error(f"Enhanced MSA reasoning failed: {e}")
            processing_time = time.time() - start_time
            return {
                "reasoning_results": {},
                "enhanced_analysis": {},
                "msa_paper_alignment": {},
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }
    
    async def _run_traditional_synthesis(self, knowledge_base: Dict[str, Any], 
                                       context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run traditional MSA Mode 2 synthesis"""
        model_specs = await self.msa_engine.knowledge_extractor.generate_model_specifications(knowledge_base)
        synthesis_results = await self.msa_engine.probabilistic_synthesizer.synthesize_model(
            model_specs, context or {}
        )
        return synthesis_results
    
    async def _analyze_synthesized_program(self, neural_program: Dict[str, Any],
                                         context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the quality and capabilities of the synthesized program"""
        if not neural_program.get("success"):
            return {"quality": "poor", "analysis": "Program synthesis failed"}
        
        program_code = neural_program.get("program_code", "")
        program_structure = neural_program.get("program_structure", {})
        
        analysis = {
            "code_quality": {
                "has_priors": "numpyro.sample" in program_code,
                "has_observations": "obs=" in program_code,
                "has_dependencies": len(program_structure.get("causal_graph", [])) > 0,
                "code_length": len(program_code.split("\n"))
            },
            "model_structure": {
                "variables": len(program_structure.get("variables", [])),
                "causal_relationships": len(program_structure.get("causal_graph", [])),
                "uncertainty_sources": len(program_structure.get("uncertainties", [])),
                "model_type": program_structure.get("model_type", "unknown")
            },
            "complexity_assessment": {
                "structural_complexity": len(program_structure.get("causal_graph", [])),
                "variable_complexity": len(program_structure.get("variables", [])),
                "overall_complexity": "high" if len(program_structure.get("causal_graph", [])) > 3 else "moderate"
            }
        }
        
        return analysis
    
    async def _integrate_neural_and_traditional(self, neural_program: Dict[str, Any],
                                              traditional_results: Dict[str, Any],
                                              knowledge_base: Dict[str, Any],
                                              context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Integrate neural synthesis with traditional MSA synthesis"""
        
        integration = {
            "approach": "hybrid_neural_traditional",
            "knowledge_extraction": knowledge_base,
            "neural_program": neural_program,
            "traditional_synthesis": traditional_results,
            "integration_analysis": {
                "neural_success": neural_program.get("success", False),
                "traditional_success": traditional_results.get("success", False),
                "complementary_strengths": {
                    "neural_creativity": neural_program.get("success", False),
                    "traditional_reliability": traditional_results.get("success", False)
                },
                "integrated_confidence": self._calculate_integrated_confidence(
                    neural_program, traditional_results
                )
            },
            "reasoning_synthesis": await self._synthesize_reasoning_approaches(
                neural_program, traditional_results, context
            )
        }
        
        return integration
    
    async def _analyze_open_world_capabilities(self, reasoning_results: Dict[str, Any],
                                             scenario: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the system's open-world reasoning capabilities"""
        
        # Check if scenario contains novel elements
        novel_indicators = [
            "new", "novel", "unprecedented", "unfamiliar", "first time", 
            "never seen", "unknown", "unusual", "different"
        ]
        
        scenario_novelty = any(indicator in scenario.lower() for indicator in novel_indicators)
        
        # Check if context indicates novel variables
        novel_variables = context.get("novel_variables", []) if context else []
        
        # Assess adaptation capabilities
        has_neural_synthesis = reasoning_results.get("neural_program") is not None
        has_causal_modeling = len(reasoning_results.get("knowledge_extraction", {}).get("causal_factors", [])) > 0
        
        return {
            "scenario_novelty": scenario_novelty,
            "novel_variables_count": len(novel_variables),
            "adaptation_mechanisms": {
                "neural_program_synthesis": has_neural_synthesis,
                "causal_structure_learning": has_causal_modeling,
                "dynamic_model_creation": True  # MSA always creates models dynamically
            },
            "open_world_score": self._calculate_open_world_score(
                scenario_novelty, len(novel_variables), has_neural_synthesis, has_causal_modeling
            ),
            "reasoning_flexibility": "high" if has_neural_synthesis else "moderate"
        }
    
    async def _analyze_novel_variable_handling(self, reasoning_results: Dict[str, Any],
                                             context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well the system handles novel variables"""
        
        if not context or not context.get("novel_variables"):
            return {"no_novel_variables": True}
        
        novel_variables = context.get("novel_variables", [])
        extracted_entities = reasoning_results.get("knowledge_extraction", {}).get("entities", [])
        entity_names = [e.get("name", "").lower() for e in extracted_entities]
        
        # Check how many novel variables were captured
        detected_count = 0
        for novel_var in novel_variables:
            var_words = novel_var.lower().replace("_", " ").split()
            if any(word in " ".join(entity_names) for word in var_words):
                detected_count += 1
        
        detection_rate = detected_count / len(novel_variables) if novel_variables else 0
        
        return {
            "total_novel_variables": len(novel_variables),
            "detected_variables": detected_count,
            "detection_rate": detection_rate,
            "handling_quality": "excellent" if detection_rate > 0.8 else "good" if detection_rate > 0.5 else "needs_improvement",
            "variable_integration": {
                "in_knowledge_base": detected_count > 0,
                "in_causal_model": self._check_variables_in_causal_model(novel_variables, reasoning_results),
                "in_probabilistic_model": self._check_variables_in_probabilistic_model(novel_variables, reasoning_results)
            }
        }
    
    async def _analyze_causal_structure_learning(self, reasoning_results: Dict[str, Any],
                                               context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze causal structure learning capabilities"""
        
        knowledge_extraction = reasoning_results.get("knowledge_extraction", {})
        relationships = knowledge_extraction.get("relationships", [])
        causal_factors = knowledge_extraction.get("causal_factors", [])
        
        # Analyze expected vs learned causal structure
        expected_structure = context.get("causal_structure", "") if context else ""
        expected_relationships = len(expected_structure.split("->")) if expected_structure else 0
        
        return {
            "relationships_identified": len(relationships),
            "causal_factors_identified": len(causal_factors),
            "expected_causal_links": expected_relationships,
            "causal_learning_score": min(1.0, (len(relationships) + len(causal_factors)) / max(1, expected_relationships)),
            "causal_complexity": {
                "simple": expected_relationships <= 2,
                "moderate": 2 < expected_relationships <= 5,
                "complex": expected_relationships > 5
            },
            "structure_quality": self._assess_causal_structure_quality(relationships, causal_factors)
        }
    
    def _calculate_integrated_confidence(self, neural_program: Dict[str, Any],
                                       traditional_results: Dict[str, Any]) -> float:
        """Calculate confidence score for integrated reasoning"""
        neural_success = 1.0 if neural_program.get("success", False) else 0.0
        traditional_success = 1.0 if traditional_results.get("success", False) else 0.0
        
        # Weighted combination (neural synthesis gets higher weight for novelty)
        return (0.6 * neural_success + 0.4 * traditional_success)
    
    async def _synthesize_reasoning_approaches(self, neural_program: Dict[str, Any],
                                             traditional_results: Dict[str, Any],
                                             context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize insights from both reasoning approaches"""
        
        synthesis = {
            "combined_insights": [],
            "approach_strengths": {
                "neural_synthesis": [
                    "Creative program generation",
                    "Novel variable handling",
                    "Adaptive model structure"
                ] if neural_program.get("success") else [],
                "traditional_synthesis": [
                    "Reliable inference",
                    "Uncertainty quantification",
                    "Established model patterns"
                ] if traditional_results.get("success") else []
            },
            "complementary_value": neural_program.get("success", False) and traditional_results.get("success", False),
            "recommended_approach": "hybrid" if neural_program.get("success") and traditional_results.get("success") else
                                   "neural" if neural_program.get("success") else "traditional"
        }
        
        return synthesis
    
    def _calculate_open_world_score(self, scenario_novelty: bool, novel_vars_count: int,
                                   has_neural_synthesis: bool, has_causal_modeling: bool) -> float:
        """Calculate open-world reasoning capability score"""
        score = 0.0
        
        # Base score for scenario novelty handling
        if scenario_novelty:
            score += 0.3
        
        # Novel variables handling
        if novel_vars_count > 0:
            score += 0.2 + min(0.2, novel_vars_count * 0.05)
        
        # Advanced capabilities
        if has_neural_synthesis:
            score += 0.3
        
        if has_causal_modeling:
            score += 0.2
        
        return min(1.0, score)
    
    def _check_variables_in_causal_model(self, novel_variables: List[str],
                                       reasoning_results: Dict[str, Any]) -> bool:
        """Check if novel variables appear in causal relationships"""
        causal_factors = reasoning_results.get("knowledge_extraction", {}).get("causal_factors", [])
        causal_text = " ".join([str(cf) for cf in causal_factors]).lower()
        
        return any(var.lower().replace("_", " ") in causal_text for var in novel_variables)
    
    def _check_variables_in_probabilistic_model(self, novel_variables: List[str],
                                              reasoning_results: Dict[str, Any]) -> bool:
        """Check if novel variables appear in probabilistic model"""
        # Check both traditional and neural synthesis results
        traditional_vars = reasoning_results.get("traditional_synthesis", {}).get("model_structure", {}).get("variables", [])
        neural_vars = reasoning_results.get("neural_program", {}).get("program_structure", {}).get("variables", [])
        
        all_model_vars = traditional_vars + neural_vars
        model_var_names = [v.get("name", "").lower() for v in all_model_vars if isinstance(v, dict)]
        
        return any(var.lower().replace("_", " ") in " ".join(model_var_names) for var in novel_variables)
    
    def _assess_causal_structure_quality(self, relationships: List[Dict], causal_factors: List[Dict]) -> str:
        """Assess the quality of learned causal structure"""
        total_causal_elements = len(relationships) + len(causal_factors)
        
        if total_causal_elements >= 5:
            return "comprehensive"
        elif total_causal_elements >= 3:
            return "adequate"
        elif total_causal_elements >= 1:
            return "basic"
        else:
            return "insufficient"