from sqlalchemy import Column, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.models.base import BaseModel


class KnowledgeChunk(BaseModel):
    """Model for storing text chunks with vector embeddings."""
    
    __tablename__ = "knowledge_chunks"
    
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(
        Vector(1024),
        nullable=True,
    )
    meta = Column(JSON, nullable=True, default={})
    
    def __repr__(self):
        return f"<KnowledgeChunk(id={self.id}, chunk_index={self.chunk_index})>"
