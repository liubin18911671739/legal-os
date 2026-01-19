from typing import List, Dict, Any
import numpy as np
import logging

try:
    from FlagEmbedding import FlagReranker
except ImportError:
    FlagReranker = None

logger = logging.getLogger(__name__)


class BGEReranker:
    """BGE Reranker model for reranking retrieved documents"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: str = "cpu",
        batch_size: int = 32,
    ):
        """Initialize BGE reranker
        
        Args:
            model_name: Model name or path
            device: Device to load model on (cuda, cpu)
            batch_size: Batch size for reranking
        """
        if FlagReranker is None:
            raise ImportError(
                "FlagEmbedding is not installed. Install with: pip install FlagEmbedding"
            )

        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size

        logger.info(f"Loading BGE reranker: {model_name} on {device}")
        self.model = FlagReranker(
            model_name_or_path=model_name,
            device=device,
        )
        logger.info("BGE reranker loaded successfully")

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = None,
        return_scores: bool = True,
    ) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance

        Args:
            query: Query text
            documents: List of document dicts with 'content' field
            top_k: Number of top results to return
            return_scores: Whether to include rerank scores

        Returns:
            Reranked list of documents with original fields and 'rerank_score'
        """
        if not documents:
            return []

        # Extract document contents
        contents = [doc.get("content", "") for doc in documents]

        try:
            # Compute rerank scores
            scores = self.model.compute_score(
                [query] * len(contents),
                contents,
                batch_size=self.batch_size,
            )

            # Add scores to documents
            reranked_docs = []
            for doc, score in zip(documents, scores):
                reranked_doc = doc.copy()
                if return_scores:
                    reranked_doc["rerank_score"] = float(score)
                reranked_docs.append(reranked_doc)

            # Sort by rerank score (descending)
            reranked_docs.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)

            # Apply top_k limit
            if top_k is not None:
                reranked_docs = reranked_docs[:top_k]

            return reranked_docs

        except Exception as e:
            logger.error(f"Failed to rerank documents: {e}")
            # Return original documents on error
            return documents[:top_k] if top_k else documents

    def rerank_pairs(
        self,
        query: str,
        documents: List[str],
        top_k: int = None,
    ) -> List[Dict[str, str]]:
        """Rerank document texts (simplified version)

        Args:
            query: Query text
            documents: List of document texts
            top_k: Number of top results to return

        Returns:
            List of dicts with 'content' and 'score'
        """
        if not documents:
            return []

        try:
            # Compute scores
            scores = self.model.compute_score(
                [query] * len(documents),
                documents,
                batch_size=self.batch_size,
            )

            # Create result list
            results = [
                {"content": doc, "score": float(score)}
                for doc, score in zip(documents, scores)
            ]

            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)

            # Apply top_k limit
            if top_k is not None:
                results = results[:top_k]

            return results

        except Exception as e:
            logger.error(f"Failed to rerank pairs: {e}")
            return documents[:top_k] if top_k else documents

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information

        Returns:
            Dictionary with model details
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "batch_size": self.batch_size,
        }
