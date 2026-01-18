from typing import List, Dict, Tuple, Optional
import math
import numpy as np
from rank_bm25 import BM25Okapi
from .tokenizer import ChineseTokenizer
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)


class BM25Indexer:
    """BM25 indexer for Chinese text with Redis persistence"""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        tokenizer: ChineseTokenizer = None,
        k1: float = 1.5,
        b: float = 0.75,
        index_key: str = "bm25:index",
        metadata_key: str = "bm25:metadata",
    ):
        """Initialize BM25 indexer

        Args:
            redis_url: Redis connection URL
            tokenizer: Chinese tokenizer (defaults to new instance)
            k1: BM25 k1 parameter (controls term frequency saturation)
            b: BM25 b parameter (controls document length normalization)
            index_key: Redis key for storing index
            metadata_key: Redis key for storing document metadata
        """
        self.redis_url = redis_url
        self.tokenizer = tokenizer or ChineseTokenizer()
        self.k1 = k1
        self.b = b
        self.index_key = index_key
        self.metadata_key = metadata_key
        
        self._bm25: Optional[BM25Okapi] = None
        self._documents: List[str] = []
        self._document_ids: List[str] = []
        self._doc_lengths: List[int] = []
        self._redis_client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._redis_client is None:
            self._redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis_client

    async def build_index(
        self,
        documents: List[Tuple[str, str]],
        load_from_redis: bool = True,
    ) -> None:
        """Build BM25 index from documents

        Args:
            documents: List of (document_id, document_text) tuples
            load_from_redis: Try to load from Redis first
        """
        # Try to load from Redis
        if load_from_redis:
            loaded = await self._load_from_redis()
            if loaded:
                logger.info("BM25 index loaded from Redis")
                return

        # Tokenize documents
        logger.info(f"Building BM25 index for {len(documents)} documents")
        tokenized_docs = []
        self._document_ids = []
        self._doc_lengths = []

        for doc_id, text in documents:
            tokens = self.tokenizer.tokenize(text)
            tokenized_docs.append(tokens)
            self._document_ids.append(doc_id)
            self._doc_lengths.append(len(tokens))

        # Create BM25 index
        self._documents = [text for _, text in documents]
        self._bm25 = BM25Okapi(tokenized_docs, k1=self.k1, b=self.b)

        # Save to Redis
        await self._save_to_redis()
        logger.info("BM25 index built and saved to Redis")

    async def _save_to_redis(self) -> None:
        """Save index and metadata to Redis"""
        client = await self._get_client()

        # Save document IDs
        await client.hset(
            f"{self.metadata_key}:ids",
            mapping={str(i): doc_id for i, doc_id in enumerate(self._document_ids)}
        )

        # Save document lengths
        await client.hset(
            f"{self.metadata_key}:lengths",
            mapping={str(i): str(length) for i, length in enumerate(self._doc_lengths)}
        )

        # Save documents
        await client.hset(
            f"{self.metadata_key}:docs",
            mapping={str(i): doc for i, doc in enumerate(self._documents)}
        )

        # Save metadata
        avg_length = sum(self._doc_lengths) / len(self._doc_lengths) if self._doc_lengths else 0
        metadata = {
            "num_docs": len(self._documents),
            "avg_doc_length": avg_length,
            "k1": self.k1,
            "b": self.b,
        }
        await client.hset(self.metadata_key, mapping=metadata)

    async def _load_from_redis(self) -> bool:
        """Load index from Redis

        Returns:
            True if loaded successfully
        """
        try:
            client = await self._get_client()

            # Load metadata
            metadata = await client.hgetall(self.metadata_key)
            if not metadata:
                return False

            num_docs = int(metadata.get("num_docs", 0))
            if num_docs == 0:
                return False

            # Load document IDs
            ids_dict = await client.hgetall(f"{self.metadata_key}:ids")
            self._document_ids = [
                ids_dict[str(i)]
                for i in range(num_docs)
                if str(i) in ids_dict
            ]

            # Load document lengths
            lengths_dict = await client.hgetall(f"{self.metadata_key}:lengths")
            self._doc_lengths = [
                int(lengths_dict[str(i)])
                for i in range(num_docs)
                if str(i) in lengths_dict
            ]

            # Load documents
            docs_dict = await client.hgetall(f"{self.metadata_key}:docs")
            self._documents = [
                docs_dict[str(i)]
                for i in range(num_docs)
                if str(i) in docs_dict
            ]

            # Rebuild BM25 index
            tokenized_docs = [
                self.tokenizer.tokenize(doc)
                for doc in self._documents
            ]
            self._bm25 = BM25Okapi(tokenized_docs, k1=self.k1, b=self.b)

            return True

        except Exception as e:
            logger.error(f"Failed to load BM25 index from Redis: {e}")
            return False

    async def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Dict[str, any]]:
        """Search using BM25

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of results with document_id and score
        """
        if self._bm25 is None:
            logger.warning("BM25 index not built")
            return []

        # Tokenize query
        query_tokens = self.tokenizer.tokenize(query)
        if not query_tokens:
            return []

        # Search
        scores = self._bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Format results
        results = []
        for idx in top_indices:
            score = scores[idx]
            if score <= 0:
                continue
            
            if idx < len(self._document_ids):
                results.append({
                    "document_id": self._document_ids[idx],
                    "score": float(score),
                    "rank": int(np.where(scores == score)[0][0]),
                })

        return results

    async def add_document(
        self,
        document_id: str,
        text: str,
    ) -> None:
        """Add a single document to index

        Args:
            document_id: Document identifier
            text: Document text
        """
        if self._bm25 is None:
            await self.build_index([(document_id, text)], load_from_redis=False)
        else:
            # Add to existing index
            self._document_ids.append(document_id)
            self._documents.append(text)
            tokens = self.tokenizer.tokenize(text)
            self._doc_lengths.append(len(tokens))

            # Rebuild index (simplified - in production, use incremental updates)
            tokenized_docs = [
                self.tokenizer.tokenize(doc)
                for doc in self._documents
            ]
            self._bm25 = BM25Okapi(tokenized_docs, k1=self.k1, b=self.b)
            
            # Save to Redis
            await self._save_to_redis()

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from index

        Args:
            document_id: Document ID to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            # Find document index
            try:
                idx = self._document_ids.index(document_id)
            except ValueError:
                return False

            # Remove from lists
            self._document_ids.pop(idx)
            self._documents.pop(idx)
            self._doc_lengths.pop(idx)

            # Rebuild index
            tokenized_docs = [
                self.tokenizer.tokenize(doc)
                for doc in self._documents
            ]
            self._bm25 = BM25Okapi(tokenized_docs, k1=self.k1, b=self.b)

            # Update Redis
            await self._save_to_redis()
            return True

        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    async def get_stats(self) -> Dict[str, any]:
        """Get index statistics

        Returns:
            Dictionary with index stats
        """
        if self._bm25 is None:
            return {
                "num_documents": 0,
                "avg_doc_length": 0,
                "k1": self.k1,
                "b": self.b,
                "status": "not_built",
            }

        avg_length = sum(self._doc_lengths) / len(self._doc_lengths) if self._doc_lengths else 0

        return {
            "num_documents": len(self._documents),
            "avg_doc_length": avg_length,
            "k1": self.k1,
            "b": self.b,
            "status": "ready",
        }

    async def clear(self) -> None:
        """Clear index"""
        self._bm25 = None
        self._documents = []
        self._document_ids = []
        self._doc_lengths = []

        # Clear Redis
        client = await self._get_client()
        await client.delete(f"{self.metadata_key}:ids")
        await client.delete(f"{self.metadata_key}:lengths")
        await client.delete(f"{self.metadata_key}:docs")
        await client.delete(self.metadata_key)
