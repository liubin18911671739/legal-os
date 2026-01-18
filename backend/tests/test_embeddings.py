import pytest
import numpy as np
from unittest.mock import AsyncMock, Mock, patch
from app.rag.embeddings import OpenAIEmbeddingModel, BaseEmbeddingModel


class TestOpenAIEmbeddingModel:
    """Test cases for OpenAIEmbeddingModel"""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenAI client"""
        with patch("app.rag.embeddings.openai_embedding.AsyncOpenAI") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def embedding_model(self, mock_client):
        """Create OpenAIEmbeddingModel instance"""
        return OpenAIEmbeddingModel(
            api_key="test-key",
            model="text-embedding-3-small",
        )

    def test_initialization(self, mock_client):
        """Test model initialization"""
        model = OpenAIEmbeddingModel(
            api_key="test-key",
            model="text-embedding-3-large",
            dimension=1024,
        )

        assert model.model_name == "text-embedding-3-large"
        assert model.dimension == 1024

    @pytest.mark.asyncio
    async def test_embed_empty_list(self, embedding_model):
        """Test embedding empty text list"""
        result = await embedding_model.embed([])
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (0, 1536)

    @pytest.mark.asyncio
    async def test_embed_single_text(self, embedding_model, mock_client):
        """Test embedding single text"""
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response

        texts = ["Hello, world!"]
        result = await embedding_model.embed(texts)

        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 1536)
        mock_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, embedding_model, mock_client):
        """Test embedding multiple texts"""
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536),
            Mock(embedding=[0.3] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response

        texts = ["First text", "Second text", "Third text"]
        result = await embedding_model.embed(texts)

        assert isinstance(result, np.ndarray)
        assert result.shape == (3, 1536)
        mock_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_with_custom_dimension(self, mock_client):
        """Test embedding with custom dimension"""
        model = OpenAIEmbeddingModel(
            api_key="test-key",
            model="text-embedding-3-small",
            dimension=512,
        )

        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 512)]
        mock_client.embeddings.create.return_value = mock_response

        result = await model.embed(["test"])

        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 512)
        call_args = mock_client.embeddings.create.call_args
        assert call_args.kwargs["dimensions"] == 512

    @pytest.mark.asyncio
    async def test_embed_query(self, embedding_model, mock_client):
        """Test embedding single query"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        result = await embedding_model.embed_query("Query text")

        assert isinstance(result, np.ndarray)
        assert result.shape == (1536,)

    @pytest.mark.asyncio
    async def test_embed_error_handling(self, embedding_model, mock_client):
        """Test error handling in embed method"""
        mock_client.embeddings.create.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to generate embeddings"):
            await embedding_model.embed(["test"])

    def test_model_name_property(self, embedding_model):
        """Test model_name property"""
        assert embedding_model.model_name == "text-embedding-3-small"

    def test_dimension_property_default(self, embedding_model):
        """Test dimension property with default model"""
        assert embedding_model.dimension == 1536

    def test_dimension_property_custom(self):
        """Test dimension property with custom dimension"""
        model = OpenAIEmbeddingModel(
            api_key="test-key",
            model="text-embedding-3-small",
            dimension=256,
        )
        assert model.dimension == 256

    def test_dimension_property_large_model(self, mock_client):
        """Test dimension property for large model"""
        model = OpenAIEmbeddingModel(
            api_key="test-key",
            model="text-embedding-3-large",
        )
        assert model.dimension == 3072


class TestBaseEmbeddingModel:
    """Test cases for BaseEmbeddingModel abstract class"""

    def test_cannot_instantiate_base(self):
        """Test that base class cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseEmbeddingModel()
