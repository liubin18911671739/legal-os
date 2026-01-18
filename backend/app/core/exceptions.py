from typing import Optional, Any


class RAGException(Exception):
    """Base exception for RAG system"""
    pass


class RetrievalException(RAGException):
    """Exception raised during retrieval operations"""
    pass


class EmbeddingException(RAGException):
    """Exception raised during embedding generation"""
    pass


class VectorStoreException(RAGException):
    """Exception raised during vector store operations"""
    pass


class DocumentProcessingException(RAGException):
    """Exception raised during document processing"""
    pass


class PipelineNotInitializedError(RAGException):
    """Exception raised when pipeline is not initialized"""
    pass


class ConfigurationError(RAGException):
    """Exception raised for configuration issues"""
    pass


class RateLimitError(RAGException):
    """Exception raised when rate limit is exceeded"""
    pass


class TimeoutError(RAGException):
    """Exception raised when operation times out"""
    pass


class ValidationError(RAGException):
    """Exception raised for validation failures"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class ContextTooLongError(RAGException):
    """Exception raised when context exceeds limits"""
    def __init__(self, context_length: int, max_length: int):
        self.context_length = context_length
        self.max_length = max_length
        message = f"Context length ({context_length}) exceeds maximum ({max_length})"
        super().__init__(message)
