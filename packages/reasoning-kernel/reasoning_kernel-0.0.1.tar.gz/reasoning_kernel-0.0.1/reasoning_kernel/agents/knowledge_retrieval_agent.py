"""
KnowledgeRetrievalAgent: Semantic search and knowledge retrieval

This agent is responsible for:
- Retrieving relevant knowledge from Redis and other memory systems
- Semantic search capabilities with embedding-based similarity
- Relevance scoring and ranking of retrieved knowledge
- Integration with memory systems and knowledge bases
- Knowledge filtering and validation
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.services.redis_service import RedisMemoryService
from reasoning_kernel.utils.security import get_secure_logger
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function


logger = get_secure_logger(__name__)


@dataclass
class RetrievalRequest:
    """Request for knowledge retrieval"""

    query: str
    context: Optional[str] = None
    max_results: int = 10
    min_relevance_score: float = 0.5
    knowledge_types: Optional[List[str]] = (
        None  # ["entities", "relationships", "facts", "procedures"]
    )
    time_range: Optional[Tuple[datetime, datetime]] = None
    filters: Optional[Dict[str, Any]] = None


@dataclass
class KnowledgeItem:
    """Individual piece of retrieved knowledge"""

    id: str
    content: str
    knowledge_type: str
    relevance_score: float
    confidence: float
    source: str
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime


@dataclass
class RetrievalResult:
    """Result of knowledge retrieval"""

    query: str
    knowledge_items: List[KnowledgeItem]
    total_found: int
    retrieval_time: float
    aggregated_confidence: float
    semantic_clusters: List[Dict[str, Any]]
    relevance_distribution: Dict[str, int]
    errors: List[str] = None


class KnowledgeRetrievalAgent(BaseReasoningAgent):
    """
    Agent for retrieving relevant knowledge from memory systems.

    This agent provides sophisticated semantic search capabilities
    with relevance scoring and knowledge validation.
    """

    def __init__(
        self,
        kernel: Kernel,
        redis_service: Optional[RedisMemoryService] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            "KnowledgeRetrieval",
            kernel,
            "Semantic search and knowledge retrieval agent",
            "Retrieve relevant knowledge from memory systems",
        )
        self.redis_service = redis_service
        self.default_max_results = config.get("max_results", 20) if config else 20
        self.embedding_dimension = (
            config.get("embedding_dimension", 768) if config else 768
        )
        self.similarity_threshold = (
            config.get("similarity_threshold", 0.7) if config else 0.7
        )
        self.cache_enabled = config.get("cache_enabled", True) if config else True

        # Knowledge type weights for scoring
        self.knowledge_type_weights = {
            "entities": 1.0,
            "relationships": 0.9,
            "facts": 0.8,
            "procedures": 0.7,
            "examples": 0.6,
            "metadata": 0.3,
        }

    async def _process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message through the knowledge retrieval pipeline"""
        try:
            # Create retrieval request
            request = RetrievalRequest(
                query=message,
                max_results=kwargs.get("max_results", self.default_max_results),
                min_relevance_score=kwargs.get("min_relevance_score", 0.5),
            )

            # Perform retrieval
            result = await self.retrieve_knowledge(request)

            # Return formatted response
            if result.errors:
                return f"Knowledge retrieval failed: {', '.join(result.errors)}"
            else:
                return f"Retrieved {len(result.knowledge_items)} knowledge items with confidence {result.aggregated_confidence:.2f}"

        except Exception as e:
            return f"Error in knowledge retrieval: {str(e)}"

    @kernel_function(
        description="Retrieve relevant knowledge based on query and context",
        name="retrieve_knowledge",
    )
    async def retrieve_knowledge(self, request: RetrievalRequest) -> RetrievalResult:
        """
        Main retrieval function that finds relevant knowledge.

        Args:
            request: Retrieval request with query and filtering options

        Returns:
            RetrievalResult with ranked and filtered knowledge items
        """
        start_time = datetime.now()
        errors = []

        try:
            logger.info(
                f"Starting knowledge retrieval for query: {request.query[:100]}..."
            )

            # Step 1: Generate query embedding
            query_embedding = await self._generate_query_embedding(
                request.query, request.context
            )

            # Step 2: Perform semantic search across knowledge bases
            raw_results = await self._semantic_search(query_embedding, request)

            # Step 3: Score and rank results
            scored_results = await self._score_and_rank_results(raw_results, request)

            # Step 4: Filter results based on criteria
            filtered_results = self._filter_results(scored_results, request)

            # Step 5: Validate knowledge quality
            validated_results = await self._validate_knowledge_items(filtered_results)

            # Step 6: Create semantic clusters
            semantic_clusters = await self._create_semantic_clusters(validated_results)

            # Step 7: Calculate aggregated metrics
            aggregated_confidence, relevance_distribution = (
                self._calculate_aggregated_metrics(validated_results)
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            result = RetrievalResult(
                query=request.query,
                knowledge_items=validated_results[: request.max_results],
                total_found=len(raw_results),
                retrieval_time=execution_time,
                aggregated_confidence=aggregated_confidence,
                semantic_clusters=semantic_clusters,
                relevance_distribution=relevance_distribution,
                errors=errors,
            )

            logger.info(
                f"Knowledge retrieval completed: {len(validated_results)} items, confidence: {aggregated_confidence:.3f}"
            )
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Knowledge retrieval failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

            return RetrievalResult(
                query=request.query,
                knowledge_items=[],
                total_found=0,
                retrieval_time=execution_time,
                aggregated_confidence=0.0,
                semantic_clusters=[],
                relevance_distribution={},
                errors=errors,
            )

    async def _generate_query_embedding(
        self, query: str, context: Optional[str] = None
    ) -> np.ndarray:
        """Generate embedding for the query (with optional context)"""
        try:
            # Combine query with context if provided
            full_query = f"{context} {query}" if context else query

            # Use kernel to generate embedding (simplified - would use actual embedding service)
            prompt = f"""
            Generate a semantic embedding for this query. The embedding should capture
            the key concepts and intent for knowledge retrieval:
            
            Query: {full_query}
            
            Return a JSON array of {self.embedding_dimension} normalized float values.
            """

            await self.kernel.invoke_function(
                plugin_name="llm", function_name="generate_text", prompt=prompt
            )

            # For simulation, generate a pseudo-embedding based on query characteristics
            embedding = self._generate_pseudo_embedding(full_query)

            logger.debug(f"Generated embedding with dimension {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            # Return random embedding as fallback
            # Return secure random embedding as fallback
            return self._secure_random_floats(self.embedding_dimension)

    def _generate_pseudo_embedding(self, text: str) -> np.ndarray:
        """Generate a pseudo-embedding based on text characteristics"""
        # Create deterministic embedding based on text content
        # This is a simplified version - in production, use actual embedding models

        # Initialize with text hash for consistency
        import hashlib

        text_hash = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
        np.random.seed(text_hash % (2**32))

        # Generate base embedding
        embedding = np.random.normal(0, 1, self.embedding_dimension)

        # Add features based on text characteristics
        words = text.lower().split()

        # Length feature
        if len(words) > 10:
            embedding[:10] += 0.5

        # Question feature
        if any(w in words for w in ["what", "how", "why", "when", "where", "who"]):
            embedding[10:20] += 0.3

        # Technical terms feature
        technical_terms = ["model", "algorithm", "data", "analysis", "system", "method"]
        if any(term in words for term in technical_terms):
            embedding[20:30] += 0.4

        # Normalize embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    async def _semantic_search(
        self, query_embedding: np.ndarray, request: RetrievalRequest
    ) -> List[Dict[str, Any]]:
        """Perform semantic search across knowledge bases"""
        logger.debug("Performing semantic search across knowledge bases")

        raw_results = []

        # Search Redis memory if available
        if self.redis_service:
            redis_results = await self._search_redis_knowledge(query_embedding, request)
            raw_results.extend(redis_results)

        # Search other knowledge sources (simulated)
        other_sources = await self._search_other_sources(query_embedding, request)
        raw_results.extend(other_sources)

        logger.debug(f"Found {len(raw_results)} raw knowledge items")
        return raw_results

    async def _search_redis_knowledge(
        self, query_embedding: np.ndarray, request: RetrievalRequest
    ) -> List[Dict[str, Any]]:
        """Search knowledge stored in Redis"""
        try:
            # Simulate Redis vector search
            # In production, this would use Redis vector similarity search

            simulated_knowledge = [
                {
                    "id": f"redis_item_{i}",
                    "content": f"Knowledge item {i} related to: {request.query}",
                    "type": "facts",
                    "embedding": np.random.random(self.embedding_dimension),
                    "source": "redis_memory",
                    "metadata": {"confidence": 0.8, "last_updated": datetime.now()},
                    "created_at": datetime.now(),
                }
                for i in range(5)  # Simulate 5 Redis results
            ]

            # Calculate similarity scores
            results = []
            for item in simulated_knowledge:
                similarity = np.dot(query_embedding, item["embedding"])
                if similarity >= request.min_relevance_score:
                    item["similarity"] = float(similarity)
                    results.append(item)

            return results

        except Exception as e:
            logger.error(f"Redis search failed: {e}")
            return []

    async def _search_other_sources(
        self, query_embedding: np.ndarray, request: RetrievalRequest
    ) -> List[Dict[str, Any]]:
        """Search other knowledge sources"""
        # Simulate additional knowledge sources
        sources = ["knowledge_graph", "document_store", "external_apis"]
        all_results = []

        for source in sources:
            try:
                # Simulate source-specific search
                source_results = [
                    {
                        "id": f"{source}_item_{i}",
                        "content": f"Knowledge from {source}: {request.query} analysis {i}",
                        "type": np.random.choice(
                            ["entities", "relationships", "facts", "procedures"]
                        ),
                        "embedding": np.random.random(self.embedding_dimension),
                        "source": source,
                        "metadata": {"confidence": np.random.uniform(0.6, 0.9)},
                        "created_at": datetime.now(),
                    }
                    for i in range(3)  # 3 results per source
                ]

                # Calculate similarities and filter
                for item in source_results:
                    similarity = np.dot(query_embedding, item["embedding"])
                    if similarity >= request.min_relevance_score:
                        item["similarity"] = float(similarity)
                        all_results.append(item)

            except Exception as e:
                logger.error(f"Search in {source} failed: {e}")
                continue

        return all_results

    async def _score_and_rank_results(
        self, raw_results: List[Dict[str, Any]], request: RetrievalRequest
    ) -> List[Dict[str, Any]]:
        """Score and rank results based on multiple criteria"""
        for item in raw_results:
            # Base similarity score
            base_score = item.get("similarity", 0.0)

            # Knowledge type weight
            knowledge_type = item.get("type", "facts")
            type_weight = self.knowledge_type_weights.get(knowledge_type, 0.5)

            # Recency bonus (newer knowledge gets slight boost)
            created_at = item.get("created_at", datetime.now())
            days_old = (datetime.now() - created_at).days
            recency_factor = max(0.5, 1.0 - (days_old / 365.0))  # Decay over a year

            # Source reliability weight
            source_weights = {
                "redis_memory": 1.0,
                "knowledge_graph": 0.9,
                "document_store": 0.8,
                "external_apis": 0.7,
            }
            source_weight = source_weights.get(item.get("source", ""), 0.5)

            # Metadata confidence
            metadata_confidence = item.get("metadata", {}).get("confidence", 0.5)

            # Calculate final score
            final_score = (
                base_score * 0.4  # Similarity weight: 40%
                + type_weight * 0.2  # Type weight: 20%
                + recency_factor * 0.1  # Recency weight: 10%
                + source_weight * 0.15  # Source weight: 15%
                + metadata_confidence * 0.15  # Metadata confidence: 15%
            )

            item["final_score"] = final_score

        # Sort by final score (descending)
        ranked_results = sorted(
            raw_results, key=lambda x: x["final_score"], reverse=True
        )

        logger.debug(f"Ranked {len(ranked_results)} results by composite score")
        return ranked_results

    def _filter_results(
        self, scored_results: List[Dict[str, Any]], request: RetrievalRequest
    ) -> List[Dict[str, Any]]:
        """Filter results based on request criteria"""
        filtered = scored_results

        # Filter by knowledge types if specified
        if request.knowledge_types:
            filtered = [
                item for item in filtered if item.get("type") in request.knowledge_types
            ]

        # Filter by time range if specified
        if request.time_range:
            start_time, end_time = request.time_range
            filtered = [
                item
                for item in filtered
                if start_time <= item.get("created_at", datetime.now()) <= end_time
            ]

        # Apply custom filters if specified
        if request.filters:
            for filter_key, filter_value in request.filters.items():
                if filter_key == "min_confidence":
                    filtered = [
                        item
                        for item in filtered
                        if item.get("metadata", {}).get("confidence", 0) >= filter_value
                    ]
                elif filter_key == "source":
                    filtered = [
                        item for item in filtered if item.get("source") == filter_value
                    ]
                # Add more custom filters as needed

        logger.debug(f"Filtered to {len(filtered)} results after applying criteria")
        return filtered

    async def _validate_knowledge_items(
        self, filtered_results: List[Dict[str, Any]]
    ) -> List[KnowledgeItem]:
        """Validate and convert raw results to KnowledgeItem objects"""
        validated_items = []

        for item in filtered_results:
            try:
                # Extract and validate required fields
                knowledge_item = KnowledgeItem(
                    id=item.get("id", "unknown"),
                    content=item.get("content", ""),
                    knowledge_type=item.get("type", "unknown"),
                    relevance_score=item.get("final_score", 0.0),
                    confidence=item.get("metadata", {}).get("confidence", 0.5),
                    source=item.get("source", "unknown"),
                    metadata=item.get("metadata", {}),
                    created_at=item.get("created_at", datetime.now()),
                    last_accessed=datetime.now(),
                )

                # Additional validation
                if self._is_valid_knowledge_item(knowledge_item):
                    validated_items.append(knowledge_item)
                else:
                    logger.debug(
                        f"Filtered out invalid knowledge item: {knowledge_item.id}"
                    )

            except Exception as e:
                logger.warning(f"Failed to validate knowledge item: {e}")
                continue

        logger.debug(f"Validated {len(validated_items)} knowledge items")
        return validated_items

    def _is_valid_knowledge_item(self, item: KnowledgeItem) -> bool:
        """Check if a knowledge item meets quality criteria"""
        # Content length check
        if len(item.content.strip()) < 10:
            return False

        # Relevance score check
        if item.relevance_score < 0.1:
            return False

        # Confidence check
        if item.confidence < 0.3:
            return False

        # Content quality check (no empty or meaningless content)
        meaningless_patterns = ["lorem ipsum", "test content", "placeholder"]
        content_lower = item.content.lower()
        if any(pattern in content_lower for pattern in meaningless_patterns):
            return False

        return True

    async def _create_semantic_clusters(
        self, knowledge_items: List[KnowledgeItem]
    ) -> List[Dict[str, Any]]:
        """Group knowledge items into semantic clusters"""
        if len(knowledge_items) < 2:
            return []

        # Simple clustering based on knowledge types and content similarity
        clusters = {}

        for item in knowledge_items:
            # Use knowledge type as primary clustering dimension
            cluster_key = item.knowledge_type

            if cluster_key not in clusters:
                clusters[cluster_key] = {
                    "cluster_id": cluster_key,
                    "cluster_name": f"{cluster_key.title()} Knowledge",
                    "items": [],
                    "avg_relevance": 0.0,
                    "avg_confidence": 0.0,
                }

            clusters[cluster_key]["items"].append(
                {
                    "id": item.id,
                    "content": item.content[:100] + "..."
                    if len(item.content) > 100
                    else item.content,
                    "relevance_score": item.relevance_score,
                    "confidence": item.confidence,
                }
            )

        # Calculate cluster statistics
        cluster_list = []
        for cluster in clusters.values():
            items = cluster["items"]
            cluster["avg_relevance"] = sum(
                item["relevance_score"] for item in items
            ) / len(items)
            cluster["avg_confidence"] = sum(item["confidence"] for item in items) / len(
                items
            )
            cluster["item_count"] = len(items)
            cluster_list.append(cluster)

        # Sort clusters by average relevance
        cluster_list.sort(key=lambda x: x["avg_relevance"], reverse=True)

        logger.debug(f"Created {len(cluster_list)} semantic clusters")
        return cluster_list

    def _calculate_aggregated_metrics(
        self, knowledge_items: List[KnowledgeItem]
    ) -> Tuple[float, Dict[str, int]]:
        """Calculate aggregated confidence and relevance distribution"""
        if not knowledge_items:
            return 0.0, {}

        # Weighted average confidence (weighted by relevance score)
        total_weighted_confidence = sum(
            item.confidence * item.relevance_score for item in knowledge_items
        )
        total_relevance = sum(item.relevance_score for item in knowledge_items)
        aggregated_confidence = (
            total_weighted_confidence / total_relevance if total_relevance > 0 else 0.0
        )

        # Relevance distribution (binned)
        relevance_bins = {"high": 0, "medium": 0, "low": 0}
        for item in knowledge_items:
            if item.relevance_score >= 0.8:
                relevance_bins["high"] += 1
            elif item.relevance_score >= 0.5:
                relevance_bins["medium"] += 1
            else:
                relevance_bins["low"] += 1

        return float(aggregated_confidence), relevance_bins

    @kernel_function(
        description="Search for specific entities or relationships",
        name="search_entities",
    )
    async def search_entities(
        self, entity_query: str, entity_type: Optional[str] = None
    ) -> List[KnowledgeItem]:
        """
        Search for specific entities or relationships in the knowledge base.

        Args:
            entity_query: Query for entities (e.g., "companies in tech sector")
            entity_type: Optional specific entity type to filter by

        Returns:
            List of knowledge items representing entities/relationships
        """
        logger.info(f"Searching for entities: {entity_query}")

        # Create specialized request for entity search
        request = RetrievalRequest(
            query=entity_query,
            max_results=50,  # More results for entity search
            min_relevance_score=0.3,  # Lower threshold for entity search
            knowledge_types=["entities", "relationships"]
            if not entity_type
            else [entity_type],
        )

        # Perform retrieval
        result = await self.retrieve_knowledge(request)

        # Filter and enhance entity results
        entity_items = []
        for item in result.knowledge_items:
            # Enhance entity metadata
            enhanced_metadata = item.metadata.copy()
            enhanced_metadata["entity_type"] = item.knowledge_type
            enhanced_metadata["query_match"] = entity_query

            entity_item = KnowledgeItem(
                id=item.id,
                content=item.content,
                knowledge_type=item.knowledge_type,
                relevance_score=item.relevance_score,
                confidence=item.confidence,
                source=item.source,
                metadata=enhanced_metadata,
                created_at=item.created_at,
                last_accessed=datetime.now(),
            )
            entity_items.append(entity_item)

        logger.info(f"Found {len(entity_items)} entities for query: {entity_query}")
        return entity_items

    @kernel_function(
        description="Update knowledge access patterns and relevance feedback",
        name="update_knowledge_feedback",
    )
    async def update_knowledge_feedback(
        self, knowledge_id: str, feedback: Dict[str, Any]
    ) -> bool:
        """
        Update knowledge item with usage feedback to improve future retrieval.

        Args:
            knowledge_id: ID of the knowledge item
            feedback: Feedback data (relevance, usefulness, corrections, etc.)

        Returns:
            True if update was successful
        """
        try:
            logger.info(f"Updating knowledge feedback for item: {knowledge_id}")

            # In production, this would update the actual knowledge store
            # For now, simulate the update

            feedback_data = {
                "knowledge_id": knowledge_id,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback.get("type", "relevance"),
            }

            # Store feedback in Redis if available
            if self.redis_service:
                feedback_key = f"knowledge_feedback:{knowledge_id}"
                await self.redis_service.store_data(feedback_key, feedback_data)

            # Update internal metrics (simulated)
            logger.debug(
                f"Updated feedback for knowledge item {knowledge_id}: {feedback}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update knowledge feedback: {e}")
            return False


# Export the agent class
__all__ = [
    "KnowledgeRetrievalAgent",
    "RetrievalRequest",
    "RetrievalResult",
    "KnowledgeItem",
]
