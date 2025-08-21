"""
LangExtract Plugin for Structured Information Extraction
========================================================

Uses langextract for extracting structured information from unstructured text
with precise source grounding and interactive visualization.
"""

from dataclasses import dataclass
from dataclasses import field
from typing import Any, Dict, List, Optional

import structlog


logger = structlog.get_logger(__name__)

try:
    from langextract import ExtractionConfig
    from langextract import LangExtract
    from langextract.models import Entity
    from langextract.models import ExtractionResult
    from langextract.models import Relationship
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    logger.warning("langextract not available, using fallback extraction")
    LANGEXTRACT_AVAILABLE = False
    
    # Fallback classes
    @dataclass
    class Entity:
        name: str
        type: str
        attributes: Dict[str, Any] = field(default_factory=dict)
        source_span: Optional[tuple] = None
    
    @dataclass
    class Relationship:
        source: str
        target: str
        type: str
        attributes: Dict[str, Any] = field(default_factory=dict)
        source_span: Optional[tuple] = None
    
    @dataclass
    class ExtractionResult:
        entities: List[Entity] = field(default_factory=list)
        relationships: List[Relationship] = field(default_factory=list)
        metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LangExtractConfig:
    """Configuration for LangExtract plugin"""
    model: str = "gpt-4"
    enable_source_grounding: bool = True
    enable_visualization: bool = True
    extraction_schema: Optional[Dict[str, Any]] = None
    confidence_threshold: float = 0.7
    max_entities: int = 50
    max_relationships: int = 100


class LangExtractPlugin:
    """
    Plugin for structured information extraction using langextract
    
    Provides:
    - Entity extraction with type classification
    - Relationship extraction with precise grounding
    - Source span tracking for transparency
    - Interactive visualization of extracted structures
    - Schema-based extraction for consistency
    """
    
    def __init__(self, config: Optional[LangExtractConfig] = None):
        self.config = config or LangExtractConfig()
        self.extractor = None
        
        if LANGEXTRACT_AVAILABLE:
            try:
                self._initialize_extractor()
                logger.info("LangExtract plugin initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LangExtract: {e}")
                self.extractor = None
        else:
            logger.info("Using fallback extraction (langextract not available)")
    
    def _initialize_extractor(self):
        """Initialize the LangExtract extractor"""
        if not LANGEXTRACT_AVAILABLE:
            return
            
        extraction_config = ExtractionConfig(
            model=self.config.model,
            enable_source_grounding=self.config.enable_source_grounding,
            confidence_threshold=self.config.confidence_threshold
        )
        
        self.extractor = LangExtract(config=extraction_config)
        
        # Set extraction schema if provided
        if self.config.extraction_schema:
            self.extractor.set_schema(self.config.extraction_schema)
    
    async def extract_structured_info(self, text: str, 
                                     schema: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        """
        Extract structured information from text
        
        Args:
            text: Input text to extract from
            schema: Optional extraction schema to override default
            
        Returns:
            ExtractionResult with entities, relationships, and metadata
        """
        logger.info("Starting structured extraction", text_length=len(text))
        
        if LANGEXTRACT_AVAILABLE and self.extractor:
            return await self._extract_with_langextract(text, schema)
        else:
            return await self._extract_with_fallback(text, schema)
    
    async def _extract_with_langextract(self, text: str, 
                                       schema: Optional[Dict[str, Any]]) -> ExtractionResult:
        """Extract using langextract library"""
        try:
            # Override schema if provided
            if schema:
                self.extractor.set_schema(schema)
            
            # Perform extraction
            result = await self.extractor.extract(text)
            
            # Filter by confidence threshold
            filtered_entities = [
                e for e in result.entities 
                if e.confidence >= self.config.confidence_threshold
            ][:self.config.max_entities]
            
            filtered_relationships = [
                r for r in result.relationships
                if r.confidence >= self.config.confidence_threshold  
            ][:self.config.max_relationships]
            
            # Create visualization if enabled
            if self.config.enable_visualization:
                visualization = await self._create_visualization(
                    filtered_entities, 
                    filtered_relationships
                )
                result.metadata['visualization'] = visualization
            
            logger.info("Extraction completed",
                       entities_count=len(filtered_entities),
                       relationships_count=len(filtered_relationships))
            
            return ExtractionResult(
                entities=filtered_entities,
                relationships=filtered_relationships,
                metadata=result.metadata
            )
            
        except Exception as e:
            logger.error(f"LangExtract extraction failed: {e}")
            return await self._extract_with_fallback(text, schema)
    
    async def _extract_with_fallback(self, text: str,
                                    schema: Optional[Dict[str, Any]]) -> ExtractionResult:
        """Fallback extraction using pattern matching and heuristics"""
        logger.info("Using fallback extraction method")
        
        entities = []
        relationships = []
        
        # Basic entity extraction using capitalized words and patterns
        import re

        # Extract potential entities (capitalized sequences)
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.finditer(entity_pattern, text)
        
        entity_map = {}
        for match in matches:
            name = match.group()
            if name not in entity_map:
                entity = Entity(
                    name=name,
                    type=self._classify_entity_type(name, text),
                    attributes={'confidence': 0.6},
                    source_span=(match.start(), match.end())
                )
                entities.append(entity)
                entity_map[name] = entity
        
        # Extract basic relationships using patterns
        relationship_patterns = [
            (r'(\w+)\s+(?:is|are|was|were)\s+(\w+)', 'is_a'),
            (r'(\w+)\s+(?:has|have|had)\s+(\w+)', 'has'),
            (r'(\w+)\s+(?:causes|caused|causing)\s+(\w+)', 'causes'),
            (r'(\w+)\s+(?:depends on|dependent on)\s+(\w+)', 'depends_on'),
            (r'(\w+)\s+(?:leads to|led to|leading to)\s+(\w+)', 'leads_to')
        ]
        
        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source = match.group(1)
                target = match.group(2)
                
                if source in entity_map and target in entity_map:
                    relationship = Relationship(
                        source=source,
                        target=target,
                        type=rel_type,
                        attributes={'confidence': 0.5},
                        source_span=(match.start(), match.end())
                    )
                    relationships.append(relationship)
        
        # Limit results
        entities = entities[:self.config.max_entities]
        relationships = relationships[:self.config.max_relationships]
        
        logger.info("Fallback extraction completed",
                   entities_count=len(entities),
                   relationships_count=len(relationships))
        
        return ExtractionResult(
            entities=entities,
            relationships=relationships,
            metadata={'extraction_method': 'fallback'}
        )
    
    def _classify_entity_type(self, name: str, context: str) -> str:
        """Simple entity type classification based on patterns"""
        name_lower = name.lower()
        context_lower = context.lower()
        
        # Check for common entity types
        if any(word in name_lower for word in ['company', 'corp', 'inc', 'ltd']):
            return 'ORGANIZATION'
        elif any(word in context_lower for word in ['person', 'people', 'individual']):
            return 'PERSON'
        elif any(word in name_lower for word in ['city', 'country', 'state']):
            return 'LOCATION'
        elif name[0].isdigit() or '$' in name:
            return 'VALUE'
        elif any(word in context_lower for word in ['product', 'service', 'platform']):
            return 'PRODUCT'
        else:
            return 'ENTITY'
    
    async def _create_visualization(self, entities: List[Entity], 
                                   relationships: List[Relationship]) -> Dict[str, Any]:
        """Create visualization data for extracted structure"""
        nodes = []
        edges = []
        
        # Create nodes from entities
        for entity in entities:
            nodes.append({
                'id': entity.name,
                'label': entity.name,
                'type': entity.type,
                'attributes': entity.attributes,
                'source_span': entity.source_span
            })
        
        # Create edges from relationships
        for rel in relationships:
            edges.append({
                'source': rel.source,
                'target': rel.target,
                'type': rel.type,
                'attributes': rel.attributes,
                'source_span': rel.source_span
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'layout': 'force-directed'
        }
    
    async def extract_with_grounding(self, text: str) -> Dict[str, Any]:
        """
        Extract information with precise source grounding
        
        Returns extraction results with exact character spans in source text
        """
        result = await self.extract_structured_info(text)
        
        grounded_result = {
            'entities': [],
            'relationships': [],
            'source_text': text
        }
        
        # Add grounding information for entities
        for entity in result.entities:
            grounded_entity = {
                'name': entity.name,
                'type': entity.type,
                'attributes': entity.attributes,
                'source_span': entity.source_span,
                'source_text': text[entity.source_span[0]:entity.source_span[1]] if entity.source_span else None
            }
            grounded_result['entities'].append(grounded_entity)
        
        # Add grounding information for relationships
        for rel in result.relationships:
            grounded_rel = {
                'source': rel.source,
                'target': rel.target,
                'type': rel.type,
                'attributes': rel.attributes,
                'source_span': rel.source_span,
                'source_text': text[rel.source_span[0]:rel.source_span[1]] if rel.source_span else None
            }
            grounded_result['relationships'].append(grounded_rel)
        
        logger.info("Extraction with grounding completed",
                   grounded_entities=len(grounded_result['entities']),
                   grounded_relationships=len(grounded_result['relationships']))
        
        return grounded_result
    
    def get_extraction_schema(self) -> Dict[str, Any]:
        """Get current extraction schema"""
        return self.config.extraction_schema or self._get_default_schema()
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """Get default extraction schema for MSA reasoning"""
        return {
            'entities': {
                'ACTOR': {'description': 'Person, organization, or agent'},
                'FACTOR': {'description': 'Variable or factor in reasoning'},
                'CONSTRAINT': {'description': 'Limitation or requirement'},
                'OUTCOME': {'description': 'Result or consequence'},
                'UNCERTAINTY': {'description': 'Unknown or uncertain element'}
            },
            'relationships': {
                'CAUSES': {'source': 'FACTOR', 'target': 'OUTCOME'},
                'CONSTRAINS': {'source': 'CONSTRAINT', 'target': 'FACTOR'},
                'DEPENDS_ON': {'source': 'OUTCOME', 'target': 'FACTOR'},
                'INFLUENCES': {'source': 'FACTOR', 'target': 'FACTOR'},
                'UNCERTAIN_ABOUT': {'source': 'ACTOR', 'target': 'UNCERTAINTY'}
            }
        }