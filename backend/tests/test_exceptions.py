import pytest
from app.core.exceptions import (
    RAGException,
    RetrievalException,
    EmbeddingException,
    VectorStoreException,
    DocumentProcessingException,
    PipelineNotInitializedError,
    ConfigurationError,
    RateLimitError,
    TimeoutError as RAGTimeoutError,
    ValidationError,
    ContextTooLongError,
)


class TestRAGExceptions:
    """Test cases for custom RAG exceptions"""

    def test_base_exception(self):
        """Test base RAG exception"""
        with pytest.raises(RAGException):
            raise RAGException("Test error")

    def test_retrieval_exception(self):
        """Test retrieval exception"""
        with pytest.raises(RetrievalException):
            raise RetrievalException("Retrieval failed")

    def test_embedding_exception(self):
        """Test embedding exception"""
        with pytest.raises(EmbeddingException):
            raise EmbeddingException("Embedding failed")

    def test_vector_store_exception(self):
        """Test vector store exception"""
        with pytest.raises(VectorStoreException):
            raise VectorStoreException("Vector store error")

    def test_document_processing_exception(self):
        """Test document processing exception"""
        with pytest.raises(DocumentProcessingException):
            raise DocumentProcessingException("Processing failed")

    def test_pipeline_not_initialized_error(self):
        """Test pipeline not initialized error"""
        with pytest.raises(PipelineNotInitializedError):
            raise PipelineNotInitializedError("Pipeline not ready")

    def test_configuration_error(self):
        """Test configuration error"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Invalid config")

    def test_rate_limit_error(self):
        """Test rate limit error"""
        with pytest.raises(RateLimitError):
            raise RateLimitError("Rate limit exceeded")

    def test_timeout_error(self):
        """Test timeout error"""
        with pytest.raises(RAGTimeoutError):
            raise RAGTimeoutError("Operation timed out")

    def test_validation_error(self):
        """Test validation error"""
        error = ValidationError("Invalid field", field="test_field")
        assert error.message == "Invalid field"
        assert error.field == "test_field"

    def test_validation_error_without_field(self):
        """Test validation error without field"""
        error = ValidationError("Invalid field")
        assert error.message == "Invalid field"
        assert error.field is None

    def test_context_too_long_error(self):
        """Test context too long error"""
        error = ContextTooLongError(context_length=5000, max_length=4000)
        assert error.context_length == 5000
        assert error.max_length == 4000
        assert "exceeds maximum" in str(error)
