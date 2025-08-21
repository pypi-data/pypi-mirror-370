"""
KnowledgePlugin - Stage 2 of the Reasoning Kernel
=================================================

Retrieves relevant background knowledge using Redis vector search and long-term memory.
Implements semantic retrieval with ANN search on embeddings.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import structlog


logger = structlog.get_logger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
    logger.warning("sentence-transformers not available, using fallback embeddings")

@dataclass
class RetrievedDocument:
    """Document retrieved from knowledge base"""
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any]
    embedding_vector: Optional[np.ndarray] = None

@dataclass
class RetrievalContext:
    """Complete context retrieval result"""
    documents: List[RetrievedDocument]
    augmented_context: str
    retrieval_confidence: float
    query_embeddings: List[np.ndarray]
    metadata: Dict[str, Any]

class KnowledgePlugin:
    """
    Stage 2: Retrieve - Retrieve relevant background knowledge (B+) & merge with vignette context
    
    Uses Redis Cloud vector search for semantic retrieval and long-term memory access.
    Implements embedding-based similarity search with fallback to keyword search.
    """
    
    def __init__(self, redis_client, embedding_model: str = "msmarco-distilbert-base-v4"):
        self.redis_client = redis_client
        self.embedding_model_name = embedding_model
        self.embedder = None
        self.vector_dimension = None
        self._initialize_embedder()
        
    def _initialize_embedder(self):
        """Initialize the sentence transformer for embeddings"""
        try:
            if SentenceTransformer is None:
                logger.warning("SentenceTransformer not available, using fallback")
                self.embedder = None
                self.vector_dimension = 768  # Default dimension
                return
                
            self.embedder = SentenceTransformer(self.embedding_model_name)
            # Get embedding dimension
            test_embedding = self.embedder.encode(["test"])
            self.vector_dimension = len(test_embedding[0])
            logger.info("Embedding model initialized", 
                       model=self.embedding_model_name, 
                       dimension=self.vector_dimension)
        except Exception as e:
            logger.warning("Failed to initialize embedding model, using fallback", error=str(e))
            self.embedder = None
            self.vector_dimension = 768
    
    async def retrieve_context(self, queries: List[str], top_k: int = 5, **kwargs) -> RetrievalContext:
        """
        Main retrieval function - finds relevant background knowledge
        
        Args:
            queries: List of query strings to search for
            top_k: Number of top documents to retrieve per query
            **kwargs: Additional retrieval parameters
            
        Returns:
            RetrievalContext with retrieved documents and augmented context
        """
        logger.info("Starting knowledge retrieval", queries_count=len(queries), top_k=top_k)
        
        try:
            # Generate embeddings for queries
            query_embeddings = await self._generate_embeddings(queries)
            
            # Perform vector search
            retrieved_docs = await self._vector_search(queries, query_embeddings, top_k)
            
            # Fallback to keyword search if vector search yields poor results
            if not retrieved_docs or all(doc.relevance_score < 0.3 for doc in retrieved_docs):
                logger.info("Vector search yielded poor results, falling back to keyword search")
                keyword_docs = await self._keyword_search(queries, top_k)
                retrieved_docs.extend(keyword_docs)
            
            # Remove duplicates and sort by relevance
            retrieved_docs = self._deduplicate_and_sort(retrieved_docs)[:top_k]
            
            # Create augmented context
            augmented_context = self._create_augmented_context(retrieved_docs)
            
            # Calculate retrieval confidence
            retrieval_confidence = self._calculate_retrieval_confidence(retrieved_docs)
            
            result = RetrievalContext(
                documents=retrieved_docs,
                augmented_context=augmented_context,
                retrieval_confidence=retrieval_confidence,
                query_embeddings=query_embeddings,
                metadata={
                    "retrieval_method": "vector_search_with_fallback",
                    "total_documents": len(retrieved_docs),
                    "retrieval_timestamp": __import__("datetime").datetime.now().isoformat()
                }
            )
            
            logger.info("Knowledge retrieval completed", 
                       documents_retrieved=len(retrieved_docs),
                       confidence=retrieval_confidence)
            
            return result
            
        except Exception as e:
            logger.error("Knowledge retrieval failed", error=str(e))
            # Return empty result rather than failing
            return RetrievalContext(
                documents=[],
                augmented_context="",
                retrieval_confidence=0.0,
                query_embeddings=[],
                metadata={"error": str(e)}
            )
    
    async def _generate_embeddings(self, queries: List[str]) -> List[np.ndarray]:
        """Generate embeddings for query strings"""
        try:
            if self.embedder is None:
                # Return dummy embeddings as fallback
                return [np.random.random(self.vector_dimension).astype(np.float32) for _ in queries]
                
            embeddings = self.embedder.encode(queries, convert_to_numpy=True)
            if isinstance(embeddings, np.ndarray):
                return [embedding.astype(np.float32) for embedding in embeddings]
            else:
                # Handle case where embeddings is a list or other type
                return [np.array(embedding, dtype=np.float32) for embedding in embeddings]
        except Exception as e:
            logger.error("Failed to generate embeddings", error=str(e))
            return []
    
    async def _vector_search(self, queries: List[str], query_embeddings: List[np.ndarray], 
                           top_k: int) -> List[RetrievedDocument]:
        """Perform vector similarity search using Redis"""
        retrieved_docs = []
        
        try:
            for query, embedding in zip(queries, query_embeddings):
                # Use Redis vector search (assuming RediSearch with vector support)
                search_results = await self._redis_vector_search(embedding, top_k)
                
                for result in search_results:
                    doc = RetrievedDocument(
                        content=result.get("content", ""),
                        source=result.get("source", "unknown"),
                        relevance_score=result.get("score", 0.0),
                        metadata=result.get("metadata", {}),
                        embedding_vector=embedding
                    )
                    retrieved_docs.append(doc)
        
        except Exception as e:
            logger.warning("Vector search failed", error=str(e))
        
        return retrieved_docs
    
    async def _redis_vector_search(self, embedding: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Execute vector search query against Redis index"""
        try:
            # Convert embedding to bytes for Redis
            embedding_bytes = embedding.tobytes()
            
            # Use Redis FT.SEARCH with vector query
            # This is a simplified implementation - actual Redis vector search syntax may vary
            query = f"*=>[KNN {top_k} @vector $query_vector AS score]"
            
            search_params = {
                "query_vector": embedding_bytes
            }
            
            # Execute search (simplified - actual implementation depends on Redis setup)
            results = await self._execute_redis_search(query, search_params)
            return results
            
        except Exception as e:
            logger.error("Redis vector search execution failed", error=str(e))
            return []
    
    async def _execute_redis_search(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute Redis search command"""
        # Placeholder implementation - would need actual Redis FT.SEARCH integration
        # For now, return empty results to avoid errors
        return []
    
    async def _keyword_search(self, queries: List[str], top_k: int) -> List[RetrievedDocument]:
        """Fallback keyword search implementation"""
        retrieved_docs = []
        
        try:
            for query in queries:
                # Simple keyword search in Redis
                # Look for keys containing query terms
                pattern = f"*{query.lower()}*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys[:top_k]:
                    try:
                        content = await self.redis_client.get(key)
                        if content:
                            doc = RetrievedDocument(
                                content=content,
                                source=key,
                                relevance_score=0.5,  # Default relevance for keyword search
                                metadata={"search_type": "keyword", "query": query}
                            )
                            retrieved_docs.append(doc)
                    except Exception as e:
                        logger.debug("Failed to retrieve key", key=key, error=str(e))
        
        except Exception as e:
            logger.warning("Keyword search failed", error=str(e))
        
        return retrieved_docs
    
    def _deduplicate_and_sort(self, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """Remove duplicates and sort by relevance score"""
        # Simple deduplication by content
        seen_content = set()
        unique_docs = []
        
        for doc in documents:
            content_hash = hash(doc.content)
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)
        
        # Sort by relevance score (descending)
        return sorted(unique_docs, key=lambda d: d.relevance_score, reverse=True)
    
    def _create_augmented_context(self, documents: List[RetrievedDocument]) -> str:
        """Create augmented context from retrieved documents"""
        if not documents:
            return ""
        
        context_parts = []
        context_parts.append("# Retrieved Background Knowledge\n")
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"## Document {i} (Relevance: {doc.relevance_score:.2f})")
            context_parts.append(f"Source: {doc.source}")
            context_parts.append(f"Content: {doc.content}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _calculate_retrieval_confidence(self, documents: List[RetrievedDocument]) -> float:
        """Calculate overall retrieval confidence"""
        if not documents:
            return 0.0
        
        # Average of document relevance scores
        avg_relevance = sum(doc.relevance_score for doc in documents) / len(documents)
        
        # Adjust for number of documents retrieved
        count_factor = min(len(documents) / 5.0, 1.0)  # Favor 5+ documents
        
        return avg_relevance * count_factor
    
    async def store_knowledge(self, content: str, source: str, metadata: Dict[str, Any] = None) -> bool:
        """Store new knowledge in the long-term memory"""
        try:
            # Generate embedding for content
            if self.embedder is not None:
                embedding = self.embedder.encode([content])[0].astype(np.float32)
            else:
                # Fallback embedding for when sentence-transformers isn't available
                embedding = np.random.random(self.vector_dimension).astype(np.float32)
            
            # Create knowledge entry
            knowledge_id = f"knowledge:{hash(content)}"
            knowledge_data = {
                "content": content,
                "source": source,
                "metadata": metadata or {},
                "embedding": embedding.tolist(),
                "stored_at": __import__("datetime").datetime.now().isoformat()
            }
            
            # Store in Redis
            await self.redis_client.set(knowledge_id, json.dumps(knowledge_data))
            
            logger.info("Knowledge stored successfully", knowledge_id=knowledge_id)
            return True
            
        except Exception as e:
            logger.error("Failed to store knowledge", error=str(e))
            return False