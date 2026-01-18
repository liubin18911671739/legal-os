from sqlalchemy import Column, String, Text, Boolean, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class DocumentFileType(str, enum.Enum):
    """Document file types."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(BaseModel):
    """Document model for storing uploaded files."""
    
    __tablename__ = "documents"
    
    title = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(
        Enum(DocumentFileType),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(String(50), nullable=True)
    status = Column(
        Enum(DocumentStatus),
        default=DocumentStatus.UPLOADING,
        index=True,
    )
    meta = Column(JSON, nullable=True, default={})
    vectorized = Column(Boolean, default=False, index=True)
    
    # Relationship
    contracts = relationship("Contract", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', status='{self.status}')>"
