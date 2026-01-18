from typing import List, Optional, Dict, Any
from app.rag.chunkers.base_chunker import BaseChunker, Chunk, ChunkingStrategy


class RecursiveCharacterChunker(BaseChunker):
    """Recursive character-based text chunker."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
    ):
        super().__init__(chunk_size, chunk_overlap)
        self.strategy = ChunkingStrategy.RECURSIVE_CHARACTER
    
    def chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Split text into chunks using recursive character splitting.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata for chunks
        
        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        text_length = len(text)
        chunk_size = self.chunk_size
        overlap = self.chunk_overlap
        start_idx = 0
        
        while start_idx < text_length:
            end_idx = min(start_idx + chunk_size, text_length)
            
            chunk_text = text[start_idx:end_idx]
            
            # Create chunk object
            chunk = Chunk(
                text=chunk_text,
                chunk_index=len(chunks),
                metadata={
                    **(metadata or {}),
                    "length": len(chunk_text),
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                }
            )
            
            chunks.append(chunk)
            
            # Move start index with overlap
            start_idx += (chunk_size - overlap)
        
        return chunks
