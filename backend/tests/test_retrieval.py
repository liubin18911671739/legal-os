import pytest
from unittest.mock import AsyncMock, Mock, patch
import numpy as np
from app.rag.retrieval import (
    RetrievalPipeline,
    RetrievalConfig,
    RetrievedChunk,
)


class TestRetrievedChunk:
    """Test cases for RetrievedChunk dataclass"""

    def test_creation(self):
        """Test RetrievedChunk creation"""
        chunk = RetrievedChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            content="Test content",
            score=0.95,
            metadata={"page": 1},
        )
        assert chunk.chunk_id == "chunk-1"
        assert chunk.document_id == "doc-1"
        assert chunk.content == "Test content"
        assert chunk.score == 0.95
        assert chunk.metadata == {"page": 1}


class TestRetrievalConfig:
    """Test cases for RetrievalConfig"""

    def test_default_values(self):
        """Test config with default values"""
        config = RetrievalConfig()
        assert config.top_k == 5
        assert config.score_threshold == 0.7
        assert config.include_metadata is True
        assert config.filter_conditions is None

    def test_custom_values(self):
        """Test config with custom values"""
        config = RetrievalConfig(
            top_k=10,
            score_threshold=0.8,
            include_metadata=False,
            filter_conditions={"document_type": "legal"},
        )
        assert config.top_k == 10
        assert config.score_threshold == 0.8
        assert config.include_metadata is False
        assert config.filter_conditions == {"document_type": "legal"}


class TestRetrievalPipeline:
    """Test cases for RetrievalPipeline"""

    @pytest.fixture
    def mock_embedding_model(self):
        """Create mock embedding model"""
        model = AsyncMock()
        model.embed_query.return_value = np.random.randn(1536)
        return model

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store"""
        store = AsyncMock()
        
        mock_result = Mock()
        mock_result.id = "point-1"
        mock_result.score = 0.95
        mock_result.payload = {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "content": "Test content",
        }
        
        store.search.return_value = [mock_result]
        store.collection_exists.return_value = True
        return store

    @pytest.fixture
    def pipeline(self, mock_embedding_model, mock_vector_store):
        """Create retrieval pipeline"""
        return RetrievalPipeline(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store,
            collection_name="test_collection",
            use_cache=False,
        )

    def test_initialization(self, mock_embedding_model, mock_vector_store):
        """Test pipeline initialization"""
        pipeline = RetrievalPipeline(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store,
            collection_name="test_collection",
            use_cache=False,
        )
        
        assert pipeline.embedding_model is mock_embedding_model
        assert pipeline.vector_store is mock_vector_store
        assert pipeline.collection_name == "test_collection"

    def test_initialization_with_cache(self, mock_embedding_model, mock_vector_store):
        """Test pipeline initialization with cache"""
        pipeline = RetrievalPipeline(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store,
            collection_name="test_collection",
            use_cache=True,
            cache_size=1000,
        )
        
        assert hasattr(pipeline.embedding_model, '_cache')

    @pytest.mark.asyncio
    async def test_retrieve(self, pipeline, mock_vector_store):
        """Test retrieving chunks"""
        query = "test query"
        
        chunks = await pipeline.retrieve(query)
        
        assert len(chunks) == 1
        assert isinstance(chunks[0], RetrievedChunk)
        assert chunks[0].chunk_id == "chunk-1"
        assert chunks[0].score == 0.95
        assert pipeline.embedding_model.embed_query.called

    @pytest.mark.asyncio
    async def test_retrieve_with_config(self, pipeline, mock_vector_store):
        """Test retrieving with custom config"""
        config = RetrievalConfig(top_k=10, score_threshold=0.8)
        query = "test query"
        
        chunks = await pipeline.retrieve(query, config)
        
        call_args = mock_vector_store.search.call_args
        assert call_args.kwargs["limit"] == 10
        assert call_args.kwargs["score_threshold"] == 0.8

    @pytest.mark.asyncio
    async def test_retrieve_with_filter(self, pipeline, mock_vector_store):
        """Test retrieving with filter conditions"""
        config = RetrievalConfig(filter_conditions={"document_type": "legal"})
        query = "test query"
        
        await pipeline.retrieve(query, config)
        
        call_args = mock_vector_store.search.call_args
        assert call_args.kwargs["filter_conditions"] == {"document_type": "legal"}

    @pytest.mark.asyncio
    async def test_retrieve_multiple_queries(self, pipeline):
        """Test retrieving for multiple queries"""
        queries = ["query 1", "query 2", "query 3"]
        
        results = await pipeline.retrieve_multiple(queries)
        
        assert len(results) == 3
        assert all(isinstance(results[q], list) for q in queries)

    @pytest.mark.asyncio
    async def test_rerank(self, pipeline):
        """Test reranking chunks"""
        query = "test query"
        chunks = [
            RetrievedChunk("1", "doc-1", "content 1", 0.9, {}),
            RetrievedChunk("2", "doc-1", "content 2", 0.8, {}),
            RetrievedChunk("3", "doc-1", "content 3", 0.7, {}),
        ]
        
        reranked = await pipeline.rerank(query, chunks)
        
        assert len(reranked) == 3
        assert reranked[0].chunk_id == "1"
        assert reranked[2].chunk_id == "3"

    @pytest.mark.asyncio
    async def test_rerank_with_top_k(self, pipeline):
        """Test reranking with top_k limit"""
        query = "test query"
        chunks = [
            RetrievedChunk("1", "doc-1", "content 1", 0.9, {}),
            RetrievedChunk("2", "doc-1", "content 2", 0.8, {}),
            RetrievedChunk("3", "doc-1", "content 3", 0.7, {}),
        ]
        
        reranked = await pipeline.rerank(query, chunks, top_k=2)
        
        assert len(reranked) == 2

    def test_get_cache_stats_without_cache(self, pipeline):
        """Test getting cache stats when cache is disabled"""
        stats = pipeline.get_cache_stats()
        assert stats is None

    def test_get_cache_stats_with_cache(self, mock_embedding_model, mock_vector_store):
        """Test getting cache stats when cache is enabled"""
        pipeline = RetrievalPipeline(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store,
            collection_name="test_collection",
            use_cache=True,
        )
        
        stats = pipeline.get_cache_stats()
        assert stats is not None
        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats
        assert "hit_rate" in stats

    @pytest.mark.asyncio
    async def test_health_check_success(self, pipeline, mock_vector_store):
        """Test health check when collection exists"""
        mock_vector_store.collection_exists.return_value = True
        
        is_healthy = await pipeline.health_check()
        
        assert is_healthy is True
        mock_vector_store.collection_exists.assert_called_once_with("test_collection")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, pipeline, mock_vector_store):
        """Test health check when collection doesn't exist"""
        mock_vector_store.collection_exists.return_value = False
        
        is_healthy = await pipeline.health_check()
        
        assert is_healthy is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self, pipeline, mock_vector_store):
        """Test health check on exception"""
        mock_vector_store.collection_exists.side_effect = Exception("Connection error")
        
        is_healthy = await pipeline.health_check()
        
        assert is_healthy is False
