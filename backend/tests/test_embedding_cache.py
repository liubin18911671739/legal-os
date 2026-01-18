import pytest
import numpy as np
from unittest.mock import AsyncMock
from app.rag.embeddings import EmbeddingCache, BaseEmbeddingModel, CacheStats


class MockEmbeddingModel(BaseEmbeddingModel):
    """Mock embedding model for testing"""

    def __init__(self, dimension=1536):
        self._dimension = dimension
        self._model_name = "mock-model"
        self._embed_count = 0

    async def embed(self, texts, **kwargs):
        """Return mock embeddings"""
        self._embed_count += 1
        return np.random.randn(len(texts), self._dimension)

    async def embed_query(self, text, **kwargs):
        """Return mock query embedding"""
        self._embed_count += 1
        return np.random.randn(self._dimension)

    @property
    def dimension(self):
        return self._dimension

    @property
    def model_name(self):
        return self._model_name


class TestEmbeddingCache:
    """Test cases for EmbeddingCache"""

    @pytest.fixture
    def mock_model(self):
        """Create mock embedding model"""
        return MockEmbeddingModel()

    @pytest.fixture
    def cache(self, mock_model):
        """Create embedding cache"""
        return EmbeddingCache(
            embedding_model=mock_model,
            max_size=100,
        )

    @pytest.mark.asyncio
    async def test_initialization(self, mock_model):
        """Test cache initialization"""
        cache = EmbeddingCache(
            embedding_model=mock_model,
            max_size=1000,
        )

        assert cache.dimension == 1536
        assert cache.model_name == "mock-model"
        assert len(cache._cache) == 0

    @pytest.mark.asyncio
    async def test_embed_empty_list(self, cache):
        """Test embedding empty list"""
        result = await cache.embed([])
        assert isinstance(result, np.ndarray)
        assert result.shape == (0, 1536)

    @pytest.mark.asyncio
    async def test_embed_first_time_miss(self, cache):
        """Test first embed is a cache miss"""
        texts = ["Hello, world!"]
        result = await cache.embed(texts)

        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 1536)
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 1

    @pytest.mark.asyncio
    async def test_embed_cache_hit(self, cache):
        """Test subsequent embed is a cache hit"""
        texts = ["Hello, world!"]
        
        await cache.embed(texts)
        stats = cache.get_stats()
        assert stats.misses == 1

        await cache.embed(texts)
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1

    @pytest.mark.asyncio
    async def test_embed_multiple_texts_mixed(self, cache):
        """Test embedding multiple texts with mixed cache hits/misses"""
        texts1 = ["First", "Second", "Third"]
        await cache.embed(texts1)

        texts2 = ["First", "Fourth", "Third"]
        await cache.embed(texts2)

        stats = cache.get_stats()
        assert stats.hits == 2  # First and Third cached
        assert stats.misses == 4  # First, Second, Third, Fourth

    @pytest.mark.asyncio
    async def test_embed_query_miss(self, cache):
        """Test query embedding miss"""
        result = await cache.embed_query("Query text")
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (1536,)
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 1

    @pytest.mark.asyncio
    async def test_embed_query_hit(self, cache):
        """Test query embedding hit"""
        await cache.embed_query("Query text")
        stats = cache.get_stats()
        assert stats.misses == 1

        await cache.embed_query("Query text")
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1

    @pytest.mark.asyncio
    async def test_cache_disabled(self, mock_model):
        """Test embedding with cache disabled"""
        cache = EmbeddingCache(mock_model, max_size=10)
        
        texts = ["Test"]
        await cache.embed(texts, use_cache=True)
        stats = cache.get_stats()
        assert stats.misses == 1

        await cache.embed(texts, use_cache=False)
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 1  # Cache disabled, so stats not updated

    @pytest.mark.asyncio
    async def test_cache_eviction(self, mock_model):
        """Test cache eviction when max size is reached"""
        cache = EmbeddingCache(mock_model, max_size=3)
        
        texts = ["A", "B", "C"]
        await cache.embed(texts)
        stats = cache.get_stats()
        assert stats.size == 3

        await cache.embed(["D"])
        stats = cache.get_stats()
        assert stats.size == 3  # One item evicted

    @pytest.mark.asyncio
    async def test_clear_cache(self, cache):
        """Test clearing the cache"""
        texts = ["A", "B", "C"]
        await cache.embed(texts)
        
        cache.clear()
        stats = cache.get_stats()
        assert stats.size == 0
        assert stats.hits == 0
        assert stats.misses == 0

    @pytest.mark.asyncio
    async def test_hit_rate(self, cache):
        """Test hit rate calculation"""
        assert cache.get_stats().hit_rate == 0.0

        await cache.embed(["A"])
        assert cache.get_stats().hit_rate == 0.0

        await cache.embed(["A"])
        assert cache.get_stats().hit_rate == 0.5

        await cache.embed(["A"])
        assert cache.get_stats().hit_rate == 0.6666666666666666

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, cache):
        """Test cache key generation"""
        text1 = "Hello, world!"
        text2 = "Hello, world!"
        text3 = "hello, WORLD!"

        await cache.embed([text1])
        stats = cache.get_stats()
        assert stats.misses == 1

        await cache.embed([text2])
        stats = cache.get_stats()
        assert stats.hits == 1

        await cache.embed([text3])
        stats = cache.get_stats()
        assert stats.misses == 2

    @pytest.mark.asyncio
    async def test_embed_with_params(self, cache):
        """Test embedding with different parameters"""
        await cache.embed(["test"], model_param="value1")
        stats = cache.get_stats()
        assert stats.misses == 1

        await cache.embed(["test"], model_param="value1")
        stats = cache.get_stats()
        assert stats.hits == 1

        await cache.embed(["test"], model_param="value2")
        stats = cache.get_stats()
        assert stats.misses == 2

    def test_properties(self, mock_model):
        """Test cache properties"""
        cache = EmbeddingCache(mock_model)
        assert cache.dimension == 1536
        assert cache.model_name == "mock-model"


class TestCacheStats:
    """Test cases for CacheStats"""

    def test_initialization(self):
        """Test stats initialization"""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.size == 0
        assert stats.hit_rate == 0.0

    def test_hit_rate_with_hits(self):
        """Test hit rate with hits"""
        stats = CacheStats(hits=7, misses=3)
        assert stats.hit_rate == 0.7

    def test_hit_rate_only_hits(self):
        """Test hit rate with only hits"""
        stats = CacheStats(hits=10, misses=0)
        assert stats.hit_rate == 1.0

    def test_hit_rate_no_requests(self):
        """Test hit rate with no requests"""
        stats = CacheStats()
        assert stats.hit_rate == 0.0
