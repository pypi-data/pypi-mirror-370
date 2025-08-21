"""
Problem Parser Stage - MSA Stage 1

Parses natural language problems into structured format with variables,
constraints, and queries. Uses Semantic Kernel with Gemini 2.5 Pro.
"""

import json
import logging
from typing import Any, Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.contents import AuthorRole
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.functions import kernel_function

from .protocols import ParsedProblem


logger = logging.getLogger(__name__)


class ProblemParser:
    """Stage 1: Parse natural language problems into structured format"""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self._setup_prompt_templates()

    def _setup_prompt_templates(self):
        """Setup prompt templates for problem parsing"""
        self.parsing_template = """
        Analyze this problem and extract all variables that should be modeled probabilistically.
        
        Problem: {problem}
        Context: {context}
        
        For each variable, determine:
        1. Variable name (valid Python identifier)
        2. Variable type (continuous, discrete, categorical, binary)
        3. Possible values or range
        4. Dependencies on other variables
        5. Prior knowledge or constraints
        
        Also identify:
        - Constraints between variables
        - Queries that need to be answered
        - Problem type (classification, prediction, causal_inference, etc.)
        
        Return as JSON with this exact structure:
        {{
            "variables": {{
                "variable_name": {{
                    "type": "continuous|discrete|categorical|binary",
                    "range": [min, max] or ["option1", "option2"],
                    "dependencies": ["var1", "var2"],
                    "description": "brief description",
                    "prior": "suggested prior distribution"
                }}
            }},
            "constraints": [
                {{
                    "type": "equality|inequality|logical",
                    "expression": "mathematical expression",
                    "variables": ["var1", "var2"],
                    "description": "constraint description"
                }}
            ],
            "queries": [
                "What is the probability that...",
                "Given evidence X, what is Y?"
            ],
            "problem_type": "classification|regression|causal_inference|prediction",
            "confidence": 0.8,
            "reasoning": "Brief explanation of the analysis"
        }}
        """

    async def parse_problem(self, problem: str, context: Optional[str] = None) -> ParsedProblem:
        """Parse natural language problem into structured format"""
        try:
            # Format the parsing prompt
            prompt = self.parsing_template.format(problem=problem, context=context or "No additional context provided")

            # Get chat service from kernel
            chat_service = self.kernel.get_service(type=None)  # Gets default chat service

            # Create chat message
            messages = [ChatMessageContent(role=AuthorRole.USER, content=prompt)]

            # Get response
            response = await chat_service.complete_chat_async(messages)
            response_text = str(response)

            # Parse JSON response
            parsed_json = self._extract_json_from_response(response_text)

            # Create ParsedProblem object
            result = ParsedProblem(
                variables=parsed_json.get("variables", {}),
                constraints=parsed_json.get("constraints", []),
                queries=parsed_json.get("queries", []),
                problem_type=parsed_json.get("problem_type", "unknown"),
                confidence=parsed_json.get("confidence", 0.5),
                metadata={
                    "original_problem": problem,
                    "context": context,
                    "reasoning": parsed_json.get("reasoning", ""),
                    "parsing_timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
                },
            )

            logger.info(f"Successfully parsed problem with {len(result.variables)} variables")
            return result

        except Exception as e:
            logger.error(f"Error parsing problem: {e}")
            # Return minimal fallback result
            return ParsedProblem(
                variables={},
                constraints=[],
                queries=[],
                problem_type="unknown",
                confidence=0.0,
                metadata={"error": str(e), "original_problem": problem},
            )

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response, handling markdown code blocks"""
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract from markdown code blocks
            if "```json" in response_text:
                json_part = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_part)
            elif "```" in response_text:
                json_part = response_text.split("```")[1].split("```")[0].strip()
                return json.loads(json_part)
            else:
                # Fallback: try to find JSON-like content
                import re

                json_pattern = r"\{.*\}"
                matches = re.findall(json_pattern, response_text, re.DOTALL)
                if matches:
                    return json.loads(matches[0])
                else:
                    raise ValueError("No valid JSON found in response")

    @kernel_function(name="parse_problem", description="Parse natural language problem into structured format")
    async def kernel_parse_problem(self, problem: str, context: Optional[str] = None) -> str:
        """Kernel function wrapper for problem parsing"""
        result = await self.parse_problem(problem, context)
        return json.dumps(
            {
                "variables": result.variables,
                "constraints": result.constraints,
                "queries": result.queries,
                "problem_type": result.problem_type,
                "confidence": result.confidence,
            },
            indent=2,
        )


# Export the class
__all__ = ["ProblemParser"]
