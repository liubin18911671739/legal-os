from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    content: str = Field(..., description="Document text content")
    filename: str = Field(..., description="Original filename")
    title: Optional[str] = Field(None, description="Document title")
    document_type: Optional[str] = Field(None, description="Document type/category")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class QueryRequest(BaseModel):
    """Request model for querying the RAG system"""
    query: str = Field(..., min_length=1, description="User query")
    top_k: Optional[int] = Field(
        5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve"
    )
    score_threshold: Optional[float] = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score"
    )
    stream: bool = Field(False, description="Whether to stream the response")
    filter_conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Filter conditions for retrieval"
    )


class SourceCitation(BaseModel):
    """Source citation in response"""
    document_id: str
    chunk_id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for query"""
    answer: str
    sources: List[SourceCitation]
    chunks_used: int
    query: str


class DocumentMetadata(BaseModel):
    """Document metadata in list response"""
    document_id: str
    title: Optional[str]
    filename: str
    document_type: Optional[str]
    created_at: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Response model for document list"""
    documents: List[DocumentMetadata]
    total: int


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    retrieval_healthy: bool
    collection_exists: bool
    cache_stats: Optional[Dict[str, Any]] = None
