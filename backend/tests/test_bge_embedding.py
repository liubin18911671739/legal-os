import pytest
import numpy as np
from app.rag.embeddings import BGEEmbeddingModel


@pytest.mark.asyncio
class TestBGEEmbeddingModel:
    """Test cases for BGEEmbeddingModel"""

    @pytest.fixture
    def model(self):
        """Create BGE embedding model instance"""
        return BGEEmbeddingModel(
            model_name="BAAI/bge-large-zh-v1.5",
            device="cpu",
        )

    @pytest.mark.asyncio
    async def test_initialization(self, model):
        """Test model initialization"""
        assert model.dimension == 1024
        assert model.model_name is not None
        assert model._device == "cpu"

    @pytest.mark.asyncio
    async def test_embed_empty_list(self, model):
        """Test embedding empty list"""
        embeddings = await model.embed([])
        assert embeddings.shape == (0, 1024)

    @pytest.mark.asyncio
    async def test_embed_single_text(self, model):
        """Test embedding single text"""
        text = "这是一个测试句子"
        embeddings = await model.embed([text])
        
        assert embeddings.shape == (1, 1024)
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, model):
        """Test embedding multiple texts"""
        texts = [
            "第一个文本",
            "第二个文本",
            "第三个文本",
        ]
        embeddings = await model.embed(texts)
        
        assert embeddings.shape == (3, 1024)
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()
        
        # Check that embeddings are different
        assert not np.allclose(embeddings[0], embeddings[1])
        assert not np.allclose(embeddings[1], embeddings[2])

    @pytest.mark.asyncio
    async def test_embed_query(self, model):
        """Test embedding query"""
        query = "查询关键词"
        embedding = await model.embed_query(query)
        
        assert embedding.shape == (1024,)
        assert not np.isnan(embedding).any()
        assert not np.isinf(embedding).any()

    @pytest.mark.asyncio
    async def test_embeddings_are_normalized(self, model):
        """Test that embeddings are normalized by default"""
        texts = ["测试文本"]
        embeddings = await model.embed(texts)
        
        # Check normalization (norm should be ~1.0)
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)

    @pytest.mark.asyncio
    async def test_batch_size_parameter(self, model):
        """Test batch size parameter"""
        texts = ["文本1", "文本2", "文本3", "文本4", "文本5"]
        
        # Test with different batch sizes
        for batch_size in [1, 2, 5]:
            embeddings = await model.embed(texts, batch_size=batch_size)
            assert embeddings.shape == (5, 1024)

    @pytest.mark.asyncio
    async def test_embedding_similarity(self, model):
        """Test that similar texts have similar embeddings"""
        texts = [
            "合同条款",
            "合同的规定",
            "天空是蓝色的",  # Unrelated
        ]
        embeddings = await model.embed(texts)
        
        # Calculate cosine similarities
        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim_0_1 = cosine_sim(embeddings[0], embeddings[1])
        sim_0_2 = cosine_sim(embeddings[0], embeddings[2])
        sim_1_2 = cosine_sim(embeddings[1], embeddings[2])
        
        # Related texts should have higher similarity
        assert sim_0_1 > 0.7
        assert sim_0_1 > sim_0_2
        assert sim_0_1 > sim_1_2

    @pytest.mark.asyncio
    async def test_get_model_info(self, model):
        """Test getting model information"""
        info = model.get_model_info()
        
        assert "model_name" in info
        assert "dimension" in info
        assert "device" in info
        assert "max_seq_length" in info
        assert "normalize" in info
        assert "batch_size" in info
        
        assert info["dimension"] == 1024
        assert info["device"] == "cpu"

    @pytest.mark.asyncio
    async def test_long_text_handling(self, model):
        """Test handling of long texts"""
        long_text = "测试" * 1000  # Long text
        embedding = await model.embed_query(long_text)
        
        assert embedding.shape == (1024,)
        assert not np.isnan(embedding).any()
