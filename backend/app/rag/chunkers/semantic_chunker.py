from typing import List, Dict, Any
import re
from app.rag.chunkers.base_chunker import BaseChunker, Chunk, ChunkingStrategy


class SemanticChunker(BaseChunker):
    """Semantic text chunker using sentence boundaries."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
    ):
        super().__init__(chunk_size, chunk_overlap)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Split text into semantic chunks based on sentence boundaries.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata for chunks
        
        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []
        
        # Simple sentence-based chunking
        # In production, use NLTK or spaCy for better results
        import re
        
        # Split by common delimiters
        delimiters = r'[。！？；；，。\\n\\r\\t]'
        
        # Split into sentences
        sentences = re.split(delimiters, text)
        
        chunks = []
        chunk_text = ""
        sent_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sent_count += 1
            
            # Add to current chunk if within size limit
            if len(chunk_text + sentence) > self.chunk_size:
                # Save current chunk
                chunk = self._create_chunk(
                    text=chunk_text.strip(),
                    chunk_index=len(chunks),
                    metadata={
                        "document_type": metadata.get("document_type", "generic"),
                        "sentences_count": sent_count,
                    "strategy": "semantic",
                    **(metadata or {}),
                    "length": len(chunk_text),
                    "sentences_count": sent_count,
                    }
                )
                chunks.append(chunk)
                chunk_text = sentence + "。"  # Add delimiter for readability
            
            else:
                chunk_text += sentence
        
        # Add remaining text as last chunk
        if chunk_text.strip():
            chunk = self._create_chunk(
                text=chunk_text.strip(),
                chunk_index=len(chunks),
                metadata={
                    **(metadata or {}),
                    "sentences_count": sent_count,
                    "strategy": "semantic",
                    "length": len(chunk_text),
                    "sentences_count": sent_count,
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        text: str,
        chunk_index: int,
        metadata: Dict[str, Any],
    ) -> Chunk:
        """Create a chunk object."""
        # Estimate tokens (roughly 1 token ≈2 Chinese characters)
        tokens = self._estimate_tokens(text)
        
        return Chunk(
            text=text,
            chunk_index=chunk_index,
            metadata={
                **(metadata or {}),
                "strategy": "semantic",
                "length": len(text),
                "tokens": tokens,
            }
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (roughly 1 token ≈ 2 Chinese characters).
        """
        return len(text) // 2  # Rough estimate for Chinese
