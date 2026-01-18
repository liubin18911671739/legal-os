import pytest
import numpy as np
from unittest.mock import AsyncMock, Mock, patch
from app.rag.services.vector_store import (
    QdrantVectorStore,
    SearchResult,
)


class TestSearchResult:
    """Test cases for SearchResult dataclass"""

    def test_creation(self):
        """Test SearchResult creation"""
        result = SearchResult(
            id="123",
            score=0.95,
            payload={"text": "test"},
        )
        assert result.id == "123"
        assert result.score == 0.95
        assert result.payload == {"text": "test"}


class TestQdrantVectorStore:
    """Test cases for QdrantVectorStore"""

    @pytest.fixture
    def mock_client(self):
        """Mock Qdrant client"""
        with patch("app.rag.services.vector_store.QdrantClient") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def vector_store(self, mock_client):
        """Create QdrantVectorStore instance"""
        return QdrantVectorStore(
            url="http://localhost:6333",
            api_key="test-key",
        )

    def test_initialization(self, mock_client):
        """Test vector store initialization"""
        store = QdrantVectorStore(
            url="http://localhost:6333",
            api_key="test-key",
            prefer_grpc=True,
        )

        assert store.client is mock_client

    @pytest.mark.asyncio
    async def test_create_collection(self, vector_store, mock_client):
        """Test creating a collection"""
        await vector_store.create_collection(
            collection_name="test_collection",
            vector_size=1536,
            distance="cosine",
        )

        mock_client.create_collection.assert_called_once()
        call_args = mock_client.create_collection.call_args
        assert call_args.kwargs["collection_name"] == "test_collection"

    @pytest.mark.asyncio
    async def test_create_collection_euclidean_distance(self, vector_store, mock_client):
        """Test creating collection with euclidean distance"""
        await vector_store.create_collection(
            collection_name="test_collection",
            vector_size=1536,
            distance="euclid",
        )

        mock_client.create_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_collection_invalid_distance(self, vector_store):
        """Test creating collection with invalid distance metric"""
        with pytest.raises(ValueError, match="Invalid distance metric"):
            await vector_store.create_collection(
                collection_name="test_collection",
                vector_size=1536,
                distance="invalid",
            )

    @pytest.mark.asyncio
    async def test_delete_collection(self, vector_store, mock_client):
        """Test deleting a collection"""
        await vector_store.delete_collection("test_collection")

        mock_client.delete_collection.assert_called_once_with("test_collection")

    @pytest.mark.asyncio
    async def test_collection_exists_true(self, vector_store, mock_client):
        """Test collection exists returns True"""
        mock_collections = Mock()
        
        col1 = Mock()
        col1.name = "test_collection"
        col2 = Mock()
        col2.name = "other_collection"
        
        mock_collections.collections = [col1, col2]
        mock_client.get_collections.return_value = mock_collections

        exists = await vector_store.collection_exists("test_collection")
        
        assert mock_client.get_collections.called
        assert exists is True

    @pytest.mark.asyncio
    async def test_collection_exists_false(self, vector_store, mock_client):
        """Test collection exists returns False"""
        mock_collections = Mock()
        mock_collections.collections = [
            Mock(name="other_collection"),
        ]
        mock_client.get_collections.return_value = mock_collections

        exists = await vector_store.collection_exists("test_collection")
        assert exists is False

    @pytest.mark.asyncio
    async def test_add_points(self, vector_store, mock_client):
        """Test adding points to collection"""
        vectors = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        payloads = [{"text": "first"}, {"text": "second"}]
        ids = ["1", "2"]

        await vector_store.add_points(
            collection_name="test_collection",
            vectors=vectors,
            payloads=payloads,
            ids=ids,
        )

        mock_client.upsert.assert_called_once()
        call_args = mock_client.upsert.call_args
        assert call_args.kwargs["collection_name"] == "test_collection"
        assert len(call_args.kwargs["points"]) == 2

    @pytest.mark.asyncio
    async def test_add_points_mismatch_length(self, vector_store):
        """Test adding points with mismatched lengths"""
        vectors = np.array([[0.1, 0.2, 0.3]])
        payloads = [{"text": "first"}, {"text": "second"}]
        ids = ["1"]

        with pytest.raises(ValueError, match="vectors, payloads, and ids must have the same length"):
            await vector_store.add_points(
                collection_name="test_collection",
                vectors=vectors,
                payloads=payloads,
                ids=ids,
            )

    @pytest.mark.asyncio
    async def test_search(self, vector_store, mock_client):
        """Test searching similar vectors"""
        query_vector = np.array([0.1, 0.2, 0.3])
        
        mock_search_result = Mock()
        mock_search_result.id = "123"
        mock_search_result.score = 0.95
        mock_search_result.payload = {"text": "result"}
        
        mock_client.search.return_value = [mock_search_result]

        results = await vector_store.search(
            collection_name="test_collection",
            query_vector=query_vector,
            limit=5,
        )

        assert len(results) == 1
        assert results[0].id == "123"
        assert results[0].score == 0.95
        assert results[0].payload == {"text": "result"}

    @pytest.mark.asyncio
    async def test_search_with_filter(self, vector_store, mock_client):
        """Test searching with filter conditions"""
        query_vector = np.array([0.1, 0.2, 0.3])
        mock_client.search.return_value = []

        await vector_store.search(
            collection_name="test_collection",
            query_vector=query_vector,
            filter_conditions={"category": "legal"},
        )

        call_args = mock_client.search.call_args
        assert call_args.kwargs["query_filter"] is not None

    @pytest.mark.asyncio
    async def test_search_with_threshold(self, vector_store, mock_client):
        """Test searching with score threshold"""
        query_vector = np.array([0.1, 0.2, 0.3])
        mock_client.search.return_value = []

        await vector_store.search(
            collection_name="test_collection",
            query_vector=query_vector,
            score_threshold=0.8,
        )

        call_args = mock_client.search.call_args
        assert call_args.kwargs["score_threshold"] == 0.8

    @pytest.mark.asyncio
    async def test_delete_points(self, vector_store, mock_client):
        """Test deleting points by IDs"""
        ids = ["1", "2", "3"]

        await vector_store.delete_points(
            collection_name="test_collection",
            ids=ids,
        )

        mock_client.delete.assert_called_once_with(
            collection_name="test_collection",
            points_selector=ids,
        )

    @pytest.mark.asyncio
    async def test_get_collection_info(self, vector_store, mock_client):
        """Test getting collection information"""
        mock_info = Mock()
        mock_info.config.params.vectors.size = 1536
        mock_info.config.params.vectors.distance = "cosine"
        mock_info.points_count = 1000
        mock_client.get_collection.return_value = mock_info

        info = await vector_store.get_collection_info("test_collection")

        assert info["name"] == "test_collection"
        assert info["vector_size"] == 1536
        assert info["points_count"] == 1000
