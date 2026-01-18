import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.rag.llm import (
    BaseLLM,
    OpenAILLM,
    ContextBuilder,
    RAGPipeline,
    RAGResponse,
)
from app.rag.retrieval import RetrievedChunk


class TestOpenAILLM:
    """Test cases for OpenAILLM"""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenAI client"""
        with patch("app.rag.llm.openai_llm.AsyncOpenAI") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def llm(self, mock_client):
        """Create OpenAILLM instance"""
        return OpenAILLM(
            api_key="test-key",
            model="gpt-4o-mini",
        )

    def test_initialization(self, mock_client):
        """Test LLM initialization"""
        llm = OpenAILLM(
            api_key="test-key",
            model="gpt-4o",
            temperature=0.5,
            max_tokens=1000,
        )
        assert llm.model_name == "gpt-4o"
        assert llm._temperature == 0.5
        assert llm._max_tokens == 1000

    @pytest.mark.asyncio
    async def test_generate(self, llm, mock_client):
        """Test text generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        result = await llm.generate("Test prompt")

        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_messages(self, llm, mock_client):
        """Test generation with message list"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]
        result = await llm.generate_with_messages(messages)

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_stream_generate(self, llm, mock_client):
        """Test streaming generation"""
        async def mock_stream():
            chunks = ["Hello", " ", "world", "!"]
            for chunk in chunks:
                mock_chunk = Mock()
                mock_chunk.choices = [Mock()]
                mock_chunk.choices[0].delta.content = chunk
                yield mock_chunk

        mock_client.chat.completions.create.return_value = mock_stream()

        result = ""
        async for chunk in llm.stream_generate("Test"):
            result += chunk

        assert result == "Hello world!"

    def test_model_name_property(self, llm):
        """Test model_name property"""
        assert llm.model_name == "gpt-4o-mini"


class TestContextBuilder:
    """Test cases for ContextBuilder"""

    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks"""
        return [
            RetrievedChunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                content="First chunk content",
                score=0.95,
                metadata={"page": 1},
            ),
            RetrievedChunk(
                chunk_id="chunk-2",
                document_id="doc-1",
                content="Second chunk content",
                score=0.90,
                metadata={"page": 2},
            ),
        ]

    def test_initialization(self):
        """Test context builder initialization"""
        builder = ContextBuilder(
            max_context_length=2000,
            include_metadata=True,
            include_sources=False,
        )
        assert builder.max_context_length == 2000
        assert builder.include_metadata is True
        assert builder.include_sources is False

    def test_build_context_with_chunks(self, sample_chunks):
        """Test building context from chunks"""
        builder = ContextBuilder()
        context = builder.build_context(sample_chunks, "test query")

        assert "First chunk content" in context
        assert "Second chunk content" in context

    def test_build_context_empty_chunks(self):
        """Test building context with empty chunks"""
        builder = ContextBuilder()
        context = builder.build_context([], "test query")

        assert context == "No relevant information found."

    def test_build_context_truncation(self):
        """Test context truncation"""
        builder = ContextBuilder(max_context_length=50)
        chunks = [
            RetrievedChunk("1", "doc-1", "A" * 100, 0.9, {}),
        ]
        
        context = builder.build_context(chunks)
        assert len(context) <= 100  # Should include prefix but truncate content

    def test_build_prompt(self, sample_chunks):
        """Test building complete prompt"""
        builder = ContextBuilder()
        prompt = builder.build_prompt("Test query", sample_chunks)

        assert "system" in prompt
        assert "user" in prompt
        assert "Context:" in prompt["user"]
        assert "Question: Test query" in prompt["user"]

    def test_build_messages(self, sample_chunks):
        """Test building message list"""
        builder = ContextBuilder()
        messages = builder.build_messages(
            "Test query",
            sample_chunks,
            system_prompt="Custom system prompt",
        )

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Custom system prompt"
        assert messages[1]["role"] == "user"

    def test_build_messages_with_history(self, sample_chunks):
        """Test building messages with conversation history"""
        builder = ContextBuilder()
        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]
        
        messages = builder.build_messages(
            "Test query",
            sample_chunks,
            conversation_history=history,
        )

        assert len(messages) == 4
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"


class TestRAGResponse:
    """Test cases for RAGResponse"""

    def test_creation(self):
        """Test RAGResponse creation"""
        response = RAGResponse(
            answer="Test answer",
            sources=[{"document_id": "doc-1"}],
            chunks_used=1,
            query="Test query",
        )
        assert response.answer == "Test answer"
        assert len(response.sources) == 1
        assert response.chunks_used == 1
        assert response.query == "Test query"


class TestRAGPipeline:
    """Test cases for RAGPipeline"""

    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM"""
        llm = AsyncMock()
        llm.generate_with_messages.return_value = "AI response"
        return llm

    @pytest.fixture
    def mock_retrieval(self):
        """Create mock retrieval pipeline"""
        from unittest.mock import Mock
        retrieval = Mock(spec=["retrieve", "get_cache_stats", "health_check"])
        retrieval.retrieve = AsyncMock(return_value=[
            RetrievedChunk("1", "doc-1", "Content", 0.9, {}),
        ])
        retrieval.get_cache_stats = Mock(return_value={"hits": 5, "misses": 2})
        retrieval.health_check = AsyncMock(return_value=True)
        return retrieval

    @pytest.fixture
    def pipeline(self, mock_llm, mock_retrieval):
        """Create RAG pipeline"""
        return RAGPipeline(
            llm=mock_llm,
            retrieval_pipeline=mock_retrieval,
        )

    def test_initialization(self, mock_llm, mock_retrieval):
        """Test pipeline initialization"""
        pipeline = RAGPipeline(
            llm=mock_llm,
            retrieval_pipeline=mock_retrieval,
            system_prompt="Custom prompt",
        )
        assert pipeline.llm is mock_llm
        assert pipeline.retrieval_pipeline is mock_retrieval
        assert pipeline.system_prompt == "Custom prompt"

    @pytest.mark.asyncio
    async def test_query(self, pipeline, mock_retrieval):
        """Test query processing"""
        response = await pipeline.query("Test query")

        assert isinstance(response, RAGResponse)
        assert response.answer == "AI response"
        assert response.query == "Test query"
        assert len(response.sources) == 1
        mock_retrieval.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_no_results(self, pipeline, mock_retrieval):
        """Test query with no retrieved chunks"""
        mock_retrieval.retrieve.return_value = []

        response = await pipeline.query("Test query")

        assert "couldn't find relevant information" in response.answer.lower()
        assert response.chunks_used == 0

    @pytest.mark.asyncio
    async def test_query_stream(self, pipeline, mock_llm):
        """Test streaming query"""
        async def mock_stream(prompt):
            yield "Hello"
            yield " world"

        mock_llm.stream_generate = mock_stream

        chunks = []
        async for chunk in pipeline.query_stream("Test query"):
            chunks.append(chunk)

        assert "".join(chunks) == "Hello world"

    @pytest.mark.asyncio
    async def test_query_with_history(self, pipeline, mock_llm):
        """Test query with conversation history"""
        history = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
        ]

        response = await pipeline.query_with_history("Test query", history)

        assert isinstance(response, RAGResponse)
        mock_llm.generate_with_messages.assert_called_once()
        
        call_messages = mock_llm.generate_with_messages.call_args[0][0]
        assert len(call_messages) == 4  # system, Q1, A1, current

    def test_get_cache_stats(self, pipeline, mock_retrieval):
        """Test getting cache stats"""
        stats = pipeline.get_cache_stats()
        assert stats == {"hits": 5, "misses": 2}
        # get_cache_stats is synchronous, so it should have been called directly
        assert mock_retrieval.get_cache_stats.called

    @pytest.mark.asyncio
    async def test_health_check(self, pipeline, mock_retrieval):
        """Test health check"""
        is_healthy = await pipeline.health_check()
        assert is_healthy is True
        mock_retrieval.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, pipeline, mock_retrieval):
        """Test health check failure"""
        mock_retrieval.health_check.return_value = False

        is_healthy = await pipeline.health_check()
        assert is_healthy is False


class TestBaseLLM:
    """Test cases for BaseLLM"""

    def test_cannot_instantiate_base(self):
        """Test that base class cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseLLM()
