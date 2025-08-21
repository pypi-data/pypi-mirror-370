"""Example usage of the modernized KernelManager with current Semantic Kernel patterns.

This example demonstrates:
- Modern kernel initialization
- InMemoryStore usage (replacing deprecated VolatileMemoryStore)
- Direct embedding service integration
- Vector store collections for memory management
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Annotated

from semantic_kernel.data.vector import VectorStoreField, vectorstoremodel

from reasoning_kernel.core.kernel_manager import KernelManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@vectorstoremodel
@dataclass
class MemoryRecord:
    """Example memory record model for vector storage."""

    id: Annotated[str, VectorStoreField("key")]
    text: Annotated[str, VectorStoreField("data", is_full_text_indexed=True)]
    embedding: Annotated[list[float] | str | None, VectorStoreField("vector", dimensions=1536)] = None

    def __post_init__(self):
        """Auto-assign text to embedding field for vector generation."""
        if self.embedding is None:
            # The embedding service will convert this text to actual vectors
            self.embedding = self.text

async def main():
    """Demonstrate modern Semantic Kernel usage."""

    # Initialize kernel manager with configuration
    config = {
        "openai_api_key": "your-openai-api-key-here",
        "openai_model_id": "gpt-4",
        "embedding_model_id": "text-embedding-3-small",
    }

    kernel_manager = KernelManager(config)

    # Create kernel with modern patterns
    kernel = kernel_manager.create_kernel()  # noqa: F841
    logger.info(f"Created kernel with {len(kernel.services)} services")

    # Get memory collection using modern InMemoryStore
    collection = kernel_manager.get_memory_collection(MemoryRecord)

    if collection:
        # Ensure collection exists
        await collection.ensure_collection_exists()
        logger.info("Memory collection created successfully")

        # Example: Add a record to the collection
        sample_records = [  # noqa: F841
            MemoryRecord(
                id="1",
                text="Semantic Kernel is a powerful framework for AI applications",
            ),
            MemoryRecord(
                id="2",
                text="Vector stores provide efficient similarity search capabilities",
            ),
        ]
        logger.info(f"Prepared {len(sample_records)} sample records for demonstration")

        # In a real application, you would generate embeddings using the embedding service
        embedding_service = kernel_manager.get_service("embeddings")
        if embedding_service:
            logger.info("Embedding service available for vector generation")

        # Upsert records (in real usage, embeddings would be populated)
        # await collection.upsert(sample_records)
        logger.info("Example records prepared for insertion")

        # Example search (would require actual embeddings)
        # search_results = await collection.search("AI framework", top=2)
        logger.info("Search functionality available through collection")

    # Demonstrate kernel services
    chat_service = kernel_manager.get_service("chat_completion")
    if chat_service:
        logger.info("Chat completion service available")

    embedding_service = kernel_manager.get_service("embeddings")
    if embedding_service:
        logger.info("Embedding service available")

    memory_store = kernel_manager.get_service("memory_store")
    if memory_store:
        logger.info("Modern InMemoryStore available")

    logger.info("Modernized Semantic Kernel setup complete!")

if __name__ == "__main__":
    asyncio.run(main())
