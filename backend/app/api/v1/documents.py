from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.schemas import (
    DocumentResponse,
    DocumentCreate,
    DocumentUpdate,
    DocumentListResponse,
    PaginatedResponse,
)
from app.models import Document
from app.utils.database import (
    create_document,
    get_document_by_id,
    get_documents,
    count_documents,
    update_document_status,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document_endpoint(
    document_in: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new document."""
    try:
        document = await create_document(db, document_in)
        return document
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create document: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a document by ID."""
    document = await get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """List documents with pagination."""
    skip = (page - 1) * size
    documents = await get_documents(db, skip=skip, limit=size)
    total = await count_documents(db)
    pages = (total + size - 1) // size
    
    return DocumentListResponse(
        items=documents,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a document."""
    document = await get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    for field, value in document_in.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    
    await db.commit()
    await db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document."""
    document = await get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    await db.delete(document)
    await db.commit()
    return None
