from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
import uuid

from app.api.schemas import (
    DocumentUploadRequest,
    QueryRequest,
    QueryResponse,
    SourceCitation,
    DocumentListResponse,
    DocumentMetadata,
    HealthResponse,
)
from app.rag.llm import RAGPipeline
from app.rag.retrieval import RetrievalConfig


router = APIRouter(prefix="/api/v1", tags=["RAG"])


class RAGService:
    """Service for managing RAG pipeline"""
    
    _instance = None
    _pipeline: RAGPipeline = None
    
    @classmethod
    def get_instance(cls) -> 'RAGService':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_pipeline(self, pipeline: RAGPipeline):
        """Set RAG pipeline"""
        self._pipeline = pipeline
    
    def get_pipeline(self) -> RAGPipeline:
        """Get RAG pipeline"""
        if self._pipeline is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG pipeline not initialized"
            )
        return self._pipeline


rag_service = RAGService.get_instance()


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system
    
    Args:
        request: Query request with question and parameters
    
    Returns:
        QueryResponse with answer and sources
    """
    pipeline = rag_service.get_pipeline()
    
    config = RetrievalConfig(
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        filter_conditions=request.filter_conditions,
    )
    
    try:
        response = await pipeline.query(request.query, retrieval_config=config)
        
        sources = [
            SourceCitation(
                document_id=src["document_id"],
                chunk_id=src["chunk_id"],
                score=src["score"],
            )
            for src in response.sources
        ]
        
        return QueryResponse(
            answer=response.answer,
            sources=sources,
            chunks_used=response.chunks_used,
            query=response.query,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/query/stream")
async def query_rag_stream(request: QueryRequest):
    """Query the RAG system with streaming response
    
    Args:
        request: Query request with question and parameters
    
    Returns:
        Streaming response with answer chunks
    """
    pipeline = rag_service.get_pipeline()
    
    config = RetrievalConfig(
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        filter_conditions=request.filter_conditions,
    )
    
    async def generate_stream() -> AsyncIterator[str]:
        try:
            async for chunk in pipeline.query_stream(request.query, config):
                yield chunk
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
    )


@router.post("/documents/upload")
async def upload_document(request: DocumentUploadRequest):
    """Upload a document to the RAG system
    
    Args:
        request: Document upload request with content and metadata
    
    Returns:
        Document ID and processing status
    """
    pipeline = rag_service.get_pipeline()
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # In a real implementation, this would:
    # 1. Save document to database
    # 2. Process and chunk the document
    # 3. Generate embeddings for chunks
    # 4. Store embeddings in vector store
    
    return {
        "document_id": document_id,
        "status": "uploaded",
        "message": "Document uploaded successfully",
        "filename": request.filename,
    }


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    document_type: str = None,
):
    """List all documents in the RAG system
    
    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        document_type: Optional filter by document type
    
    Returns:
        List of documents
    """
    pipeline = rag_service.get_pipeline()
    
    # In a real implementation, this would query the database
    # For now, return empty list
    return DocumentListResponse(
        documents=[],
        total=0,
    )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the RAG system
    
    Args:
        document_id: ID of document to delete
    
    Returns:
        Deletion status
    """
    pipeline = rag_service.get_pipeline()
    
    # In a real implementation, this would:
    # 1. Delete chunks from vector store
    # 2. Delete document from database
    
    return {
        "document_id": document_id,
        "status": "deleted",
        "message": "Document deleted successfully",
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint
    
    Returns:
        Health status of RAG system
    """
    pipeline = rag_service.get_pipeline()
    
    is_healthy = await pipeline.health_check()
    cache_stats = pipeline.get_cache_stats()
    
    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        retrieval_healthy=is_healthy,
        collection_exists=is_healthy,
        cache_stats=cache_stats,
    )
