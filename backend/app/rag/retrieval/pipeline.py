from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..embeddings import BaseEmbeddingModel, EmbeddingCache
from ..services import QdrantVectorStore, SearchResult


@dataclass
class RetrievedChunk:
    """Represents a retrieved chunk with metadata"""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]


class RetrievalConfig:
    """Configuration for retrieval pipeline"""

    def __init__(
        self,
        top_k: int = 5,
        score_threshold: float = 0.7,
        include_metadata: bool = True,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ):
        """Initialize retrieval configuration

        Args:
            top_k: Number of results to retrieve
            score_threshold: Minimum similarity score
            include_metadata: Whether to include metadata in results
            filter_conditions: Optional filter conditions for search
        """
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.include_metadata = include_metadata
        self.filter_conditions = filter_conditions


class RetrievalPipeline:
    """Pipeline for retrieving relevant document chunks"""

    def __init__(
        self,
        embedding_model: BaseEmbeddingModel,
        vector_store: QdrantVectorStore,
        collection_name: str,
        use_cache: bool = True,
        cache_size: int = 10000,
    ):
        """Initialize retrieval pipeline

        Args:
            embedding_model: Model for generating embeddings
            vector_store: Vector store for similarity search
            collection_name: Name of the collection to search
            use_cache: Whether to cache embeddings
            cache_size: Maximum size of embedding cache
        """
        if use_cache:
            self.embedding_model = EmbeddingCache(
                embedding_model=embedding_model,
                max_size=cache_size,
            )
        else:
            self.embedding_model = embedding_model

        self.vector_store = vector_store
        self.collection_name = collection_name

    async def retrieve(
        self,
        query: str,
        config: Optional[RetrievalConfig] = None,
    ) -> List[RetrievedChunk]:
        """Retrieve relevant chunks for a query

        Args:
            query: Query text
            config: Retrieval configuration

        Returns:
            List of retrieved chunks sorted by relevance
        """
        if config is None:
            config = RetrievalConfig()

        # Generate query embedding
        query_embedding = await self.embedding_model.embed_query(query)

        # Search vector store
        search_results = await self.vector_store.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=config.top_k,
            score_threshold=config.score_threshold,
            filter_conditions=config.filter_conditions,
        )

        # Convert to RetrievedChunk objects
        chunks = []
        for result in search_results:
            chunk = RetrievedChunk(
                chunk_id=result.payload.get("chunk_id", result.id),
                document_id=result.payload.get("document_id", ""),
                content=result.payload.get("content", ""),
                score=result.score,
                metadata=result.payload if config.include_metadata else {},
            )
            chunks.append(chunk)

        return chunks

    async def retrieve_multiple(
        self,
        queries: List[str],
        config: Optional[RetrievalConfig] = None,
    ) -> Dict[str, List[RetrievedChunk]]:
        """Retrieve chunks for multiple queries

        Args:
            queries: List of query texts
            config: Retrieval configuration

        Returns:
            Dictionary mapping queries to retrieved chunks
        """
        if config is None:
            config = RetrievalConfig()

        results = {}
        for query in queries:
            chunks = await self.retrieve(query, config)
            results[query] = chunks

        return results

    async def rerank(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        top_k: Optional[int] = None,
    ) -> List[RetrievedChunk]:
        """Rerank retrieved chunks (placeholder for future implementation)

        Args:
            query: Query text
            chunks: Retrieved chunks to rerank
            top_k: Number of top chunks to return

        Returns:
            Reranked list of chunks
        """
        # Placeholder: Currently just returns original order
        # Could implement cross-encoder reranking here
        if top_k is not None:
            return chunks[:top_k]
        return chunks

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get embedding cache statistics

        Returns:
            Dictionary with cache stats if cache is enabled, None otherwise
        """
        if isinstance(self.embedding_model, EmbeddingCache):
            stats = self.embedding_model.get_stats()
            return {
                "hits": stats.hits,
                "misses": stats.misses,
                "size": stats.size,
                "hit_rate": stats.hit_rate,
            }
        return None

    async def health_check(self) -> bool:
        """Check if the retrieval pipeline is healthy

        Returns:
            True if both embedding model and vector store are accessible
        """
        try:
            # Check vector store collection exists
            collection_exists = await self.vector_store.collection_exists(
                self.collection_name
            )
            return collection_exists
        except Exception:
            return False
