from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ChunkingStrategy(str, Enum):
    """Chunking strategies."""
    RECURSIVE_CHARACTER = "recursive_character"
    SEMANTIC = "semantic"
    FIXED_SIZE = "fixed_size"


class Chunk(BaseModel):
    """Chunk model for document chunks."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_index: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    tokens: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class BaseChunker:
    """Base class for chunking strategies."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata for chunks
            
        Returns:
            List of Chunk objects
        """
        raise NotImplementedError("Subclasses must implement chunk() method")
    
    def _create_chunk(
        self,
        text: str,
        chunk_index: int,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Chunk:
        """Create a chunk object."""
        return Chunk(
            text=text,
            metadata=metadata or {},
            chunk_index=chunk_index,
            **kwargs
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (approximate: 1 token ≈ 2 Chinese characters).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 2  # Rough estimate for Chinese
