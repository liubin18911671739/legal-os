from typing import List, Dict, Any, Optional
import logging
from .pipeline import RetrievalPipeline, RetrievalConfig, RetrievedChunk
from .bm25_indexer import BM25Indexer
from .rrf import reciprocal_rank_fusion, weighted_score_fusion
from .reranker import BGEReranker
import numpy as np

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retriever combining vector and BM25 search with reranking"""

    def __init__(
        self,
        vector_retriever: RetrievalPipeline,
        bm25_indexer: BM25Indexer,
        reranker: Optional[BGEReranker] = None,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        fusion_method: str = "rrf",
    ):
        """Initialize hybrid retriever

        Args:
            vector_retriever: Vector similarity retriever
            bm25_indexer: BM25 keyword retriever
            reranker: Optional reranker model
            vector_weight: Weight for vector results (for weighted fusion)
            bm25_weight: Weight for BM25 results (for weighted fusion)
            fusion_method: Fusion method ('rrf' or 'weighted')
        """
        self.vector_retriever = vector_retriever
        self.bm25_indexer = bm25_indexer
        self.reranker = reranker
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.fusion_method = fusion_method

    async def retrieve(
        self,
        query: str,
        config: Optional[RetrievalConfig] = None,
        use_reranker: bool = True,
    ) -> List[Dict[str, Any]]:
        """Retrieve using hybrid search

        Args:
            query: Search query
            config: Retrieval configuration
            use_reranker: Whether to use reranker

        Returns:
            List of retrieved documents with metadata
        """
        if config is None:
            config = RetrievalConfig()

        # Retrieve from both sources in parallel
        import asyncio
        
        # Vector retrieval
        vector_results = await self._retrieve_vector(query, config)
        
        # BM25 retrieval
        bm25_results = await self._retrieve_bm25(query, config.top_k)
        
        # Combine results using RRF
        combined_results = self._combine_results(
            vector_results,
            bm25_results,
        )
        
        # Rerank if enabled
        if use_reranker and self.reranker:
            combined_results = self.reranker.rerank(
                query=query,
                documents=combined_results,
                top_k=config.top_k,
            )
        
        # Convert to RetrievedChunk format for compatibility
        return self._convert_to_chunks(combined_results)

    async def _retrieve_vector(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> List[Dict[str, Any]]:
        """Retrieve using vector similarity

        Args:
            query: Search query
            config: Retrieval configuration

        Returns:
            List of vector search results
        """
        try:
            chunks = await self.vector_retriever.retrieve(query, config)
            
            # Convert to dict format
            results = [
                {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "score": chunk.score,
                    "source": "vector",
                    **chunk.metadata,
                }
                for chunk in chunks
            ]
            
            return results
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
            return []

    async def _retrieve_bm25(
        self,
        query: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Retrieve using BM25

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of BM25 search results
        """
        try:
            results = await self.bm25_indexer.search(query, top_k=top_k)
            
            # Normalize BM25 scores to [0, 1] range
            if results:
                scores = [r["score"] for r in results]
                max_score = max(scores)
                min_score = min(scores)
                score_range = max_score - min_score
                
                if score_range > 0:
                    for result in results:
                        result["score"] = (result["score"] - min_score) / score_range
                        result["source"] = "bm25"
                else:
                    for result in results:
                        result["score"] = 1.0
                        result["source"] = "bm25"
            
            return results
        except Exception as e:
            logger.error(f"BM25 retrieval failed: {e}")
            return []

    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Combine results from vector and BM25 retrieval

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search

        Returns:
            Combined results
        """
        if not vector_results and not bm25_results:
            return []

        if self.fusion_method == "weighted":
            # Use weighted score fusion
            combined = weighted_score_fusion(
                results_list=[vector_results, bm25_results],
                weights=[self.vector_weight, self.bm25_weight],
            )
        else:
            # Use reciprocal rank fusion (default)
            combined = reciprocal_rank_fusion(
                results_list=[vector_results, bm25_results],
                top_k=min(len(vector_results) + len(bm25_results), 20),
            )

        return combined

    def _convert_to_chunks(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Convert results to unified format

        Args:
            results: Combined results

        Returns:
            Results in standard format
        """
        return results

    async def retrieve_multiple(
        self,
        queries: List[str],
        config: Optional[RetrievalConfig] = None,
        use_reranker: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve for multiple queries

        Args:
            queries: List of search queries
            config: Retrieval configuration
            use_reranker: Whether to use reranker

        Returns:
            Dictionary mapping queries to results
        """
        results = {}
        
        for query in queries:
            retrieved = await self.retrieve(query, config, use_reranker)
            results[query] = retrieved
        
        return results

    async def get_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics

        Returns:
            Dictionary with stats
        """
        vector_stats = await self.vector_retrieval.pipeline.health_check()
        bm25_stats = await self.bm25_indexer.get_stats()
        
        return {
            "vector_retriever_healthy": vector_stats,
            "bm25_indexer_status": bm25_stats.get("status", "unknown"),
            "bm25_num_documents": bm25_stats.get("num_documents", 0),
            "fusion_method": self.fusion_method,
            "vector_weight": self.vector_weight,
            "bm25_weight": self.bm25_weight,
            "reranker_enabled": self.reranker is not None,
        }
