from typing import List, Optional, Dict, Any
import numpy as np
import redis.asyncio as redis
import json
import hashlib
from .base import BaseEmbeddingModel


class RedisEmbeddingCache:
    """Redis-based embedding cache for persistent caching"""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        embedding_model: Optional[BaseEmbeddingModel] = None,
        ttl: int = 86400,  # 24 hours
        key_prefix: str = "emb:",
    ):
        """Initialize Redis embedding cache

        Args:
            redis_url: Redis connection URL
            embedding_model: Underlying embedding model for cache misses
            ttl: Time-to-live for cached embeddings (seconds)
            key_prefix: Prefix for cache keys
        """
        self.redis_url = redis_url
        self._embedding_model = embedding_model
        self.ttl = ttl
        self.key_prefix = key_prefix
        
        self._hits = 0
        self._misses = 0
        self._size = 0
        self._redis_client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._redis_client is None:
            self._redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,
            )
        return self._redis_client

    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        return f"{self.key_prefix}{text_hash}"

    async def embed(
        self,
        texts: List[str],
        **kwargs
    ) -> np.ndarray:
        """Generate embeddings with caching

        Args:
            texts: List of text strings to embed
            **kwargs: Additional parameters

        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)

        client = await self._get_client()
        embeddings = []
        cache_keys = [self._generate_cache_key(text) for text in texts]
        indices_to_fetch = []

        # Try to get from cache
        for i, key in enumerate(cache_keys):
            cached_data = await client.get(key)
            if cached_data is not None:
                # Cache hit
                self._hits += 1
                embedding = np.frombuffer(cached_data, dtype=np.float32)
                embeddings.append(embedding)
            else:
                # Cache miss
                self._misses += 1
                indices_to_fetch.append((i, texts[i]))

        # Generate embeddings for cache misses
        if indices_to_fetch:
            miss_texts = [text for _, text in indices_to_fetch]
            if self._embedding_model is None:
                raise RuntimeError("Embedding model not set")
            miss_embeddings = await self._embedding_model.embed(miss_texts, **kwargs)
            
            # Store in cache
            for idx, (orig_idx, _) in enumerate(indices_to_fetch):
                key = cache_keys[orig_idx]
                embedding = miss_embeddings[idx]
                
                # Store as bytes
                await client.setex(
                    key,
                    self.ttl,
                    embedding.tobytes(),
                )
                
                self._size += 1
                embeddings.append(embedding)

        # Reorder embeddings to match input order
        ordered_embeddings = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for i, embedding in enumerate(embeddings):
            ordered_embeddings[i] = embedding

        return ordered_embeddings

    async def embed_query(self, text: str, **kwargs) -> np.ndarray:
        """Generate embedding for single query with caching

        Args:
            text: Query text
            **kwargs: Additional parameters

        Returns:
            numpy array of embedding
        """
        embeddings = await self.embed([text], **kwargs)
        return embeddings[0]

    async def clear(self) -> None:
        """Clear all cached embeddings"""
        client = await self._get_client()
        pattern = f"{self.key_prefix}*"
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await client.delete(*keys)
        
        self._size = 0

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": self._size,
            "hit_rate": self.hit_rate,
            "ttl": self.ttl,
        }

    async def reset_stats(self) -> None:
        """Reset cache statistics"""
        self._hits = 0
        self._misses = 0

    @property
    def dimension(self) -> int:
        """Return dimension of embeddings"""
        if self._embedding_model:
            return self._embedding_model.dimension
        return 1024  # Default for BGE-large-zh-v1.5
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
