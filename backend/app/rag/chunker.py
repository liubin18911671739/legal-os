from typing import Dict, List, Optional
from app.rag.chunkers.base_chunker import BaseChunker, Chunk, ChunkingStrategy


class Chunker:
    """Main chunker class that uses different strategies."""
    
    def __init__(
        self,
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE_CHARACTER,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
    ):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, any] = None,
    ) -> List[Chunk]:
        """
        Chunk document using selected strategy.
        
        Args:
            document_id: Document ID
            content: Text to chunk
            metadata: Optional metadata
        
        Returns:
            List of Chunk objects
        """
        from app.rag.chunkers.recursive_character_chunker import RecursiveCharacterChunker
        from app.rag.chunkers.semantic_chunker import SemanticChunker
        
        # Select chunker based on strategy
        if self.strategy == ChunkingStrategy.RECURSIVE_CHARACTER:
            from app.rag.chunkers.recursive_character_chunker import RecursiveCharacterChunker
            chunker = RecursiveCharacterChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            from app.rag.chunkers.semantic_chunker import SemanticChunker
            chunker = SemanticChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        # Chunk document
        chunks = chunker.chunk(content, metadata or {})
        
        # Add document_id to each chunk
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
        
        return chunks
    
    def batch_chunk(
        self,
        documents: List[Dict[str, any]],
    ) -> Dict[str, List[Chunk]]:
        """
        Chunk multiple documents in batch.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Dictionary mapping document_id to chunks
        """
        results = {}
        
        for doc in documents:
            document_id = doc.get("id") or doc.get("document_id")
            content = doc.get("content") or ""
            metadata = doc.get("metadata", {})
            
            chunks = self.chunk(document_id, content, metadata)
            results[document_id] = chunks
        
        return results
