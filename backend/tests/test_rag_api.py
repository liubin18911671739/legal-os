import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock
from app.api.rag_routes import router, rag_service
from app.rag.llm import RAGPipeline, RAGResponse
from app.rag.retrieval import RetrievedChunk


class TestQueryEndpoint:
    """Test cases for query endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = Mock(spec=RAGPipeline)
        pipeline.query = AsyncMock()
        pipeline.query_stream = AsyncMock()
        pipeline.health_check = AsyncMock(return_value=True)
        pipeline.get_cache_stats = Mock(return_value=None)
        return pipeline

    def test_query_success(self, client, mock_pipeline):
        """Test successful query"""
        mock_pipeline.query.return_value = RAGResponse(
            answer="Test answer",
            sources=[{"document_id": "doc-1", "chunk_id": "chunk-1", "score": 0.9}],
            chunks_used=1,
            query="test query",
        )
        rag_service.set_pipeline(mock_pipeline)

        response = client.post(
            "/api/v1/query",
            json={"query": "test query", "top_k": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Test answer"
        assert data["chunks_used"] == 1
        assert len(data["sources"]) == 1

    def test_query_invalid_request(self, client, mock_pipeline):
        """Test query with invalid request"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.post(
            "/api/v1/query",
            json={"query": ""},  # Empty query
        )

        assert response.status_code == 422  # Validation error

    def test_query_pipeline_not_initialized(self, client):
        """Test query when pipeline not initialized"""
        rag_service.set_pipeline(None)

        response = client.post(
            "/api/v1/query",
            json={"query": "test query"},
        )

        assert response.status_code == 503


class TestStreamQueryEndpoint:
    """Test cases for streaming query endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = Mock(spec=RAGPipeline)
        pipeline.query = AsyncMock()
        pipeline.query_stream = AsyncMock()
        pipeline.health_check = AsyncMock(return_value=True)
        pipeline.get_cache_stats = Mock(return_value=None)
        return pipeline

    def test_query_stream_success(self, client, mock_pipeline):
        """Test successful streaming query"""
        async def mock_stream(query, config):
            yield "Hello"
            yield " world"

        mock_pipeline.query_stream = mock_stream
        rag_service.set_pipeline(mock_pipeline)

        response = client.post(
            "/api/v1/query/stream",
            json={"query": "test query"},
        )

        assert response.status_code == 200
        assert b"Hello world" in response.content


class TestDocumentUploadEndpoint:
    """Test cases for document upload endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = Mock(spec=RAGPipeline)
        return pipeline

    def test_upload_success(self, client, mock_pipeline):
        """Test successful document upload"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.post(
            "/api/v1/documents/upload",
            json={
                "content": "Test document content",
                "filename": "test.txt",
                "title": "Test Document",
                "document_type": "text",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "uploaded"

    def test_upload_invalid_request(self, client, mock_pipeline):
        """Test upload with invalid request"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.post(
            "/api/v1/documents/upload",
            json={
                "filename": "test.txt",
                # Missing required 'content' field
            },
        )

        assert response.status_code == 422


class TestListDocumentsEndpoint:
    """Test cases for list documents endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = Mock(spec=RAGPipeline)
        return pipeline

    def test_list_documents(self, client, mock_pipeline):
        """Test listing documents"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert data["total"] == 0

    def test_list_documents_with_filters(self, client, mock_pipeline):
        """Test listing documents with filters"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.get(
            "/api/v1/documents?document_type=legal&limit=5"
        )

        assert response.status_code == 200


class TestDeleteDocumentEndpoint:
    """Test cases for delete document endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = Mock(spec=RAGPipeline)
        return pipeline

    def test_delete_success(self, client, mock_pipeline):
        """Test successful document deletion"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.delete("/api/v1/documents/doc-123")

        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == "doc-123"
        assert data["status"] == "deleted"


class TestHealthCheckEndpoint:
    """Test cases for health check endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = Mock(spec=RAGPipeline)
        pipeline.health_check = AsyncMock(return_value=True)
        pipeline.get_cache_stats = Mock(return_value={"hits": 10, "misses": 5})
        return pipeline

    def test_health_healthy(self, client, mock_pipeline):
        """Test health check when healthy"""
        rag_service.set_pipeline(mock_pipeline)

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["retrieval_healthy"] is True
        assert data["cache_stats"] is not None

    def test_health_unhealthy(self, client, mock_pipeline):
        """Test health check when unhealthy"""
        mock_pipeline.health_check = AsyncMock(return_value=False)
        rag_service.set_pipeline(mock_pipeline)

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["retrieval_healthy"] is False
