from typing import Optional, Dict
from dataclasses import dataclass
import hashlib
import json
import numpy as np
from .base import BaseEmbeddingModel


@dataclass
class CacheStats:
    """Statistics for embedding cache"""
    hits: int = 0
    misses: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class EmbeddingCache:
    """Simple in-memory cache for embeddings"""

    def __init__(
        self,
        embedding_model: BaseEmbeddingModel,
        max_size: int = 10000,
    ):
        """Initialize embedding cache

        Args:
            embedding_model: Underlying embedding model
            max_size: Maximum number of cached embeddings
        """
        self.model = embedding_model
        self.max_size = max_size
        self._cache: Dict[str, np.ndarray] = {}
        self._stats = CacheStats()

    def _generate_key(self, text: str, **kwargs) -> str:
        """Generate cache key from text and parameters

        Args:
            text: Input text
            **kwargs: Additional parameters

        Returns:
            Cache key string
        """
        data = {"text": text, **kwargs}
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def embed(
        self,
        texts: list[str],
        use_cache: bool = True,
        **kwargs
    ) -> np.ndarray:
        """Generate embeddings with caching

        Args:
            texts: List of text strings to embed
            use_cache: Whether to use cache
            **kwargs: Additional parameters

        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([]).reshape(0, self.model.dimension)

        embeddings = []
        texts_to_embed = []
        indices_to_cache = []

        for i, text in enumerate(texts):
            if use_cache:
                key = self._generate_key(text, **kwargs)
                if key in self._cache:
                    embeddings.append((i, self._cache[key]))
                    self._stats.hits += 1
                else:
                    texts_to_embed.append(text)
                    indices_to_cache.append(i)
                    self._stats.misses += 1
            else:
                texts_to_embed.append(text)
                indices_to_cache.append(i)

        if texts_to_embed:
            new_embeddings = await self.model.embed(texts_to_embed, **kwargs)
            
            for idx, (orig_idx, embedding) in enumerate(
                zip(indices_to_cache, new_embeddings)
            ):
                if use_cache:
                    key = self._generate_key(texts_to_embed[idx], **kwargs)
                    self._add_to_cache(key, embedding)
                embeddings.append((orig_idx, embedding))

        embeddings.sort(key=lambda x: x[0])
        return np.array([emb for _, emb in embeddings])

    async def embed_query(
        self,
        text: str,
        use_cache: bool = True,
        **kwargs
    ) -> np.ndarray:
        """Generate embedding for query with caching

        Args:
            text: Query text
            use_cache: Whether to use cache
            **kwargs: Additional parameters

        Returns:
            Embedding vector
        """
        if use_cache:
            key = self._generate_key(text, **kwargs)
            if key in self._cache:
                self._stats.hits += 1
                return self._cache[key]
            self._stats.misses += 1

        embedding = await self.model.embed_query(text, **kwargs)

        if use_cache:
            key = self._generate_key(text, **kwargs)
            self._add_to_cache(key, embedding)

        return embedding

    def _add_to_cache(self, key: str, embedding: np.ndarray) -> None:
        """Add embedding to cache with size management

        Args:
            key: Cache key
            embedding: Embedding vector
        """
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        self._cache[key] = embedding.copy()
        self._stats.size = len(self._cache)

    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if self._cache:
            self._cache.pop(next(iter(self._cache)))

    def clear(self) -> None:
        """Clear all cached embeddings"""
        self._cache.clear()
        self._stats = CacheStats()

    def get_stats(self) -> CacheStats:
        """Get cache statistics

        Returns:
            CacheStats object
        """
        self._stats.size = len(self._cache)
        return self._stats

    @property
    def dimension(self) -> int:
        """Return embedding dimension"""
        return self.model.dimension

    @property
    def model_name(self) -> str:
        """Return model name"""
        return self.model.model_name
