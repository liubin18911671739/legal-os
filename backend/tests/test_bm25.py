import pytest
from app.rag.retrieval import BM25Indexer, ChineseTokenizer


@pytest.mark.asyncio
class TestBM25Indexer:
    """Test cases for BM25Indexer"""

    @pytest.fixture
    def tokenizer(self):
        """Create Chinese tokenizer"""
        return ChineseTokenizer()

    @pytest.fixture
    def indexer(self, tokenizer):
        """Create BM25 indexer"""
        return BM25Indexer(
            tokenizer=tokenizer,
            redis_url="redis://localhost:6379/15",  # Different DB for tests
        )

    @pytest.mark.asyncio
    async def test_tokenization(self, tokenizer):
        """Test Chinese text tokenization"""
        text = "合同条款规定了双方的权利和义务"
        tokens = tokenizer.tokenize(text)
        
        assert len(tokens) > 0
        assert "合同" in tokens
        assert "条款" in tokens
        assert "权利" in tokens
        assert "义务" in tokens
        # Stop words should be removed
        assert "了" not in tokens
        assert "和" not in tokens

    @pytest.mark.asyncio
    async def test_build_index(self, indexer):
        """Test building BM25 index"""
        documents = [
            ("doc1", "合同第一条：甲方提供产品和服务"),
            ("doc2", "合同第二条：乙方支付货款"),
            ("doc3", "违约责任：如果一方违约，应承担相应责任"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        
        assert await indexer.get_stats()["num_documents"] == 3

    @pytest.mark.asyncio
    async def test_search(self, indexer):
        """Test BM25 search"""
        documents = [
            ("doc1", "合同第一条：甲方提供产品和服务"),
            ("doc2", "合同第二条：乙方支付货款"),
            ("doc3", "违约责任：如果一方违约，应承担相应责任"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        
        # Search for relevant document
        results = await indexer.search("违约责任", top_k=3)
        
        assert len(results) > 0
        # Most relevant should be about "违约责任"
        assert results[0]["document_id"] == "doc3"
        assert results[0]["score"] > 0

    @pytest.mark.asyncio
    async def test_search_multiple_terms(self, indexer):
        """Test search with multiple terms"""
        documents = [
            ("doc1", "甲方提供产品"),
            ("doc2", "乙方支付货款"),
            ("doc3", "甲方和乙方签订合同"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        
        # Search with multiple terms
        results = await indexer.search("甲方 乙方", top_k=3)
        
        assert len(results) > 0
        # doc3 should be most relevant (contains both terms)
        assert results[0]["document_id"] == "doc3"

    @pytest.mark.asyncio
    async def test_add_document(self, indexer):
        """Test adding a single document"""
        documents = [
            ("doc1", "第一条：甲方提供产品"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        assert await indexer.get_stats()["num_documents"] == 1

        # Add new document
        await indexer.add_document("doc2", "第二条：乙方支付货款")
        assert await indexer.get_stats()["num_documents"] == 2

        # Search for new document
        results = await indexer.search("乙方", top_k=5)
        assert len(results) > 0
        assert any(r["document_id"] == "doc2" for r in results)

    @pytest.mark.asyncio
    async def test_delete_document(self, indexer):
        """Test deleting a document"""
        documents = [
            ("doc1", "第一条：甲方提供产品"),
            ("doc2", "第二条：乙方支付货款"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        assert await indexer.get_stats()["num_documents"] == 2

        # Delete document
        deleted = await indexer.delete_document("doc1")
        assert deleted is True
        assert await indexer.get_stats()["num_documents"] == 1

        # Verify search doesn't return deleted document
        results = await indexer.search("产品", top_k=5)
        assert not any(r["document_id"] == "doc1" for r in results)

    @pytest.mark.asyncio
    async def test_clear_index(self, indexer):
        """Test clearing index"""
        documents = [
            ("doc1", "第一条：甲方提供产品"),
            ("doc2", "第二条：乙方支付货款"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        assert await indexer.get_stats()["num_documents"] == 2

        # Clear index
        await indexer.clear()
        assert await indexer.get_stats()["num_documents"] == 0

    @pytest.mark.asyncio
    async def test_empty_query(self, indexer):
        """Test search with empty query"""
        documents = [
            ("doc1", "第一条：甲方提供产品"),
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        
        # Search with empty query
        results = await indexer.search("", top_k=5)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_ranking(self, indexer):
        """Test result ranking"""
        documents = [
            ("doc1", "合同条款：提供产品"),  # Partial match
            ("doc2", "合同条款规定提供产品和服务"),  # Better match
            ("doc3", "违约责任条款"),  # Different topic
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        
        # Search
        results = await indexer.search("合同条款", top_k=3)
        
        # Should return 3 results
        assert len(results) == 3
        
        # doc2 should be most relevant (more complete match)
        assert results[0]["document_id"] == "doc2"

    @pytest.mark.asyncio
    async def test_top_k_limit(self, indexer):
        """Test top_k limit"""
        documents = [
            (f"doc{i}", f"文档{i}内容") for i in range(10)
        ]
        
        await indexer.build_index(documents, load_from_redis=False)
        
        # Search with different top_k values
        for top_k in [1, 3, 5]:
            results = await indexer.search("文档", top_k=top_k)
            assert len(results) <= top_k
