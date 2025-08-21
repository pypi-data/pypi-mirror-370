"""
ParsingPlugin - Stage 1 of the Reasoning Kernel
==============================================

Transforms natural language vignettes into structured constraints (ΠO) and queries (ΠQ).
Uses Azure LLM models with Semantic Kernel orchestration.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
import json
from typing import Any, Dict, List

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
import structlog


logger = structlog.get_logger(__name__)


class ParsedElementType(Enum):
    CONSTRAINT = "constraint"
    QUERY = "query"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"


@dataclass
class ParsedElement:
    """Individual parsed element from vignette"""

    element_type: ParsedElementType
    content: str
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class ParsedVignette:
    """Complete parsing result"""

    constraints: List[ParsedElement]
    queries: List[ParsedElement]
    entities: List[ParsedElement]
    relationships: List[ParsedElement]
    raw_vignette: str
    parsing_confidence: float
    metadata: Dict[str, Any]


class ParsingPlugin:
    """
    Stage 1: Parse - Transform vignette into structured constraints (ΠO) & queries (ΠQ)

    Uses Azure LLM models for natural language understanding and structured extraction.
    Implements retry logic and validation according to PRD specifications.
    """

    def __init__(self, kernel: Kernel, redis_client=None):
        self.kernel = kernel
        self.redis_client = redis_client
        self.parsing_function = None
        self._initialize_parsing_function()

        # Initialize LangExtract plugin for enhanced extraction
        self.langextract_plugin = None
        try:
            from .langextract_plugin import LangExtractConfig
            from .langextract_plugin import LangExtractPlugin

            config = LangExtractConfig(
                enable_source_grounding=True, enable_visualization=True, confidence_threshold=0.7
            )
            self.langextract_plugin = LangExtractPlugin(config)
            logger.info("LangExtract plugin integrated for enhanced extraction")
        except Exception as e:
            logger.info(f"LangExtract not available, using standard extraction: {e}")

    def _initialize_parsing_function(self):
        """Initialize the semantic function for parsing"""
        parsing_prompt = """
        You are an expert at parsing natural language scenarios into structured elements.
        
        Parse the following vignette into structured components:
        
        INPUT: {{$vignette}}
        
        Extract and return a JSON object with:
        1. "constraints": List of factual constraints and limitations in the scenario
        2. "queries": List of questions or objectives that need to be answered
        3. "entities": List of key actors, objects, or concepts mentioned
        4. "relationships": List of interactions or connections between entities
        
        For each element, include:
        - "content": The actual text/description
        - "confidence": Your confidence in this extraction (0.0-1.0)
        - "metadata": Any additional context or properties
        
        Return valid JSON only, no additional text.
        
        Example output format:
        {
            "constraints": [
                {
                    "content": "Budget limit of $10,000",
                    "confidence": 0.95,
                    "metadata": {"type": "financial", "value": 10000}
                }
            ],
            "queries": [
                {
                    "content": "What is the best investment strategy?",
                    "confidence": 0.90,
                    "metadata": {"category": "decision", "priority": "high"}
                }
            ],
            "entities": [
                {
                    "content": "Investment portfolio",
                    "confidence": 0.88,
                    "metadata": {"type": "financial_instrument"}
                }
            ],
            "relationships": [
                {
                    "content": "Budget constrains investment options",
                    "confidence": 0.85,
                    "metadata": {"type": "constraint_relationship"}
                }
            ]
        }
        """

        try:
            # Try new SK method
            self.parsing_function = self.kernel.add_function(
                function_name="parse_vignette",
                plugin_name="ParsingPlugin",
                prompt=parsing_prompt,
            )
        except AttributeError:
            # Fallback for older SK versions
            from semantic_kernel.functions import kernel_function

            @kernel_function(name="parse_vignette")
            def parse_func(vignette: str) -> str:
                return parsing_prompt.format(vignette=vignette)

            self.parsing_function = parse_func

    async def parse_vignette(self, vignette: str, **kwargs) -> ParsedVignette:
        """
        Main parsing function - transforms vignette into structured elements

        Args:
            vignette: Natural language scenario text
            **kwargs: Additional parameters for parsing customization

        Returns:
            ParsedVignette object with structured elements
        """
        logger.info("Starting vignette parsing", vignette_length=len(vignette))

        try:
            # Prepare arguments
            arguments = KernelArguments(vignette=vignette)

            # Execute parsing with retry logic
            result = await self._execute_with_retry(arguments)

            # Parse and validate JSON response
            parsed_data = self._validate_parsing_result(result)

            # Convert to structured objects
            parsed_vignette = self._convert_to_parsed_vignette(vignette, parsed_data)

            # Store in Redis short-term memory if available
            if self.redis_client:
                await self._store_parsing_result(parsed_vignette)

            logger.info(
                "Vignette parsing completed successfully",
                constraints_count=len(parsed_vignette.constraints),
                queries_count=len(parsed_vignette.queries),
            )

            return parsed_vignette

        except Exception as e:
            logger.error("Vignette parsing failed", error=str(e))
            raise

    async def _execute_with_retry(self, arguments: KernelArguments, max_retries: int = 3) -> str:
        """Execute parsing with exponential backoff retry logic"""

        for attempt in range(max_retries):
            try:
                try:
                    result = await self.parsing_function.invoke(self.kernel, arguments)
                except AttributeError:
                    # Fallback invoke method
                    result = await self.kernel.invoke(self.parsing_function, arguments)
                return str(result)

            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                wait_time = 2**attempt  # Exponential backoff
                logger.warning(f"Parsing attempt {attempt + 1} failed, retrying in {wait_time}s", error=str(e))
                await asyncio.sleep(wait_time)

        raise Exception("All parsing attempts failed")

    def _validate_parsing_result(self, result: str) -> Dict[str, Any]:
        """Validate and parse JSON result from LLM"""
        try:
            # Clean up result if needed
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:-3].strip()
            elif result.startswith("```"):
                result = result[3:-3].strip()

            parsed_data = json.loads(result)

            # Validate required fields
            required_fields = ["constraints", "queries", "entities", "relationships"]
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = []

            return parsed_data

        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON result", result=result, error=str(e))
            # Return minimal valid structure
            return {"constraints": [], "queries": [], "entities": [], "relationships": []}

    def _convert_to_parsed_vignette(self, vignette: str, parsed_data: Dict[str, Any]) -> ParsedVignette:
        """Convert parsed JSON data to structured ParsedVignette object"""

        def create_elements(data: List[Dict], element_type: ParsedElementType) -> List[ParsedElement]:
            elements = []
            for item in data:
                if isinstance(item, dict) and "content" in item:
                    element = ParsedElement(
                        element_type=element_type,
                        content=item["content"],
                        confidence=item.get("confidence", 0.8),
                        metadata=item.get("metadata", {}),
                    )
                    elements.append(element)
            return elements

        constraints = create_elements(parsed_data.get("constraints", []), ParsedElementType.CONSTRAINT)
        queries = create_elements(parsed_data.get("queries", []), ParsedElementType.QUERY)
        entities = create_elements(parsed_data.get("entities", []), ParsedElementType.ENTITY)
        relationships = create_elements(parsed_data.get("relationships", []), ParsedElementType.RELATIONSHIP)

        # Calculate overall parsing confidence
        all_elements = constraints + queries + entities + relationships
        if all_elements:
            parsing_confidence = sum(e.confidence for e in all_elements) / len(all_elements)
        else:
            parsing_confidence = 0.5

        return ParsedVignette(
            constraints=constraints,
            queries=queries,
            entities=entities,
            relationships=relationships,
            raw_vignette=vignette,
            parsing_confidence=parsing_confidence,
            metadata={
                "total_elements": len(all_elements),
                "parsing_timestamp": __import__("datetime").datetime.now().isoformat(),
            },
        )

    async def _store_parsing_result(self, parsed_vignette: ParsedVignette):
        """Store parsing result in Redis short-term memory"""
        try:
            if self.redis_client:
                key = f"parsing:result:{hash(parsed_vignette.raw_vignette)}"
                data = {
                    "constraints": [
                        {"content": c.content, "confidence": c.confidence, "metadata": c.metadata}
                        for c in parsed_vignette.constraints
                    ],
                    "queries": [
                        {"content": q.content, "confidence": q.confidence, "metadata": q.metadata}
                        for q in parsed_vignette.queries
                    ],
                    "entities": [
                        {"content": e.content, "confidence": e.confidence, "metadata": e.metadata}
                        for e in parsed_vignette.entities
                    ],
                    "relationships": [
                        {"content": r.content, "confidence": r.confidence, "metadata": r.metadata}
                        for r in parsed_vignette.relationships
                    ],
                    "parsing_confidence": parsed_vignette.parsing_confidence,
                    "metadata": parsed_vignette.metadata,
                }

                await self.redis_client.setex(key, 3600, json.dumps(data))  # 1 hour TTL
                logger.debug("Parsing result stored in Redis", key=key)

        except Exception as e:
            logger.warning("Failed to store parsing result in Redis", error=str(e))
