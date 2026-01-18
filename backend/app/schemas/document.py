from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.document import DocumentFileType, DocumentStatus
import uuid


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str = Field(..., min_length=1, max_length=500)
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: DocumentFileType
    metadata: Optional[Dict[str, Any]] = {}


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_path: Optional[str] = None
    file_size: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[DocumentStatus] = None
    vectorized: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: uuid.UUID
    file_path: Optional[str] = None
    file_size: Optional[str] = None
    content: Optional[str] = None
    status: DocumentStatus
    vectorized: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated document list."""
    items: list[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int
