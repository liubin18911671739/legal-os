from typing import List, Dict, Any, Optional
from ..retrieval import RetrievedChunk


class ContextBuilder:
    """Builds context from retrieved chunks for LLM prompts"""

    def __init__(
        self,
        max_context_length: int = 4000,
        include_metadata: bool = False,
        include_sources: bool = True,
        merge_adjacent: bool = True,
        merge_distance: int = 2,
    ):
        """Initialize context builder

        Args:
            max_context_length: Maximum total length of context in characters
            include_metadata: Whether to include chunk metadata
            include_sources: Whether to include source citations
            merge_adjacent: Whether to merge adjacent chunks from same document
            merge_distance: Maximum chunk index distance to consider for merging
        """
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata
        self.include_sources = include_sources
        self.merge_adjacent = merge_adjacent
        self.merge_distance = merge_distance

    def build_context(
        self,
        chunks: List[RetrievedChunk],
        query: str = "",
    ) -> str:
        """Build context string from retrieved chunks

        Args:
            chunks: Retrieved chunks to include in context
            query: Original query (optional, can be used for relevance)

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant information found."

        # Sort chunks by score (descending)
        sorted_chunks = sorted(chunks, key=lambda x: x.score, reverse=True)

        # Merge adjacent chunks if enabled
        if self.merge_adjacent:
            sorted_chunks = self._merge_adjacent_chunks(sorted_chunks)

        # Build context with length limit
        context_parts = []
        total_length = 0

        for i, chunk in enumerate(sorted_chunks):
            chunk_text = self._format_chunk(chunk, i + 1)
            
            if total_length + len(chunk_text) > self.max_context_length:
                # Add partial chunk if beneficial
                remaining = self.max_context_length - total_length
                if remaining > 100:  # Only if >100 chars remaining
                    chunk_text = chunk_text[:remaining]
                    context_parts.append(chunk_text)
                break
            
            context_parts.append(chunk_text)
            total_length += len(chunk_text)

        return "\n\n".join(context_parts)

    def _merge_adjacent_chunks(
        self,
        chunks: List[RetrievedChunk],
    ) -> List[RetrievedChunk]:
        """Merge adjacent chunks from same document

        Args:
            chunks: Sorted list of chunks

        Returns:
            List of merged chunks
        """
        if not chunks:
            return []

        merged = [chunks[0]]

        for chunk in chunks[1:]:
            last_chunk = merged[-1]

            # Check if from same document and close in index
            if (
                chunk.document_id == last_chunk.document_id
                and abs(chunk.chunk_index - last_chunk.chunk_index) <= self.merge_distance
            ):
                # Merge chunks
                merged_content = f"{last_chunk.content}\n{chunk.content}"
                
                # Update last chunk
                last_chunk.content = merged_content
                last_chunk.score = max(last_chunk.score, chunk.score)
                
                # Merge metadata
                last_chunk.metadata.update(chunk.metadata)
            else:
                # Add as new chunk
                merged.append(chunk)

        return merged

    def _format_chunk(self, chunk: RetrievedChunk, index: int) -> str:
        """Format a single chunk

        Args:
            chunk: Chunk to format
            index: Chunk index number

        Returns:
            Formatted chunk string
        """
        parts = []
        
        if self.include_sources:
            parts.append(f"[Source {index}: Document {chunk.document_id}]")
        
        parts.append(chunk.content)
        
        if self.include_metadata:
            metadata_str = ", ".join(
                f"{k}: {v}" for k, v in chunk.metadata.items()
                if k not in ["content", "chunk_id", "document_id"]
            )
            if metadata_str:
                parts.append(f"(Metadata: {metadata_str})")

        return " ".join(parts)

    def build_prompt(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, str]:
        """Build complete prompt with system message and context

        Args:
            query: User query
            chunks: Retrieved chunks
            system_prompt: Optional system prompt

        Returns:
            Dictionary with 'system' and 'user' messages
        """
        default_system_prompt = (
            "You are a helpful AI assistant. "
            "Use the provided context to answer the user's question. "
            "If the context doesn't contain enough information, say so. "
            "Cite your sources when appropriate."
        )
        
        if system_prompt:
            system_message = system_prompt
        else:
            system_message = default_system_prompt

        context = self.build_context(chunks, query)
        
        user_message = f"""Context:
{context}

Question: {query}

Answer:"""

        return {
            "system": system_message,
            "user": user_message,
        }

    def build_messages(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """Build message list for LLM

        Args:
            query: User query
            chunks: Retrieved chunks
            system_prompt: Optional system prompt
            conversation_history: Optional conversation history

        Returns:
            List of message dictionaries
        """
        prompt = self.build_prompt(query, chunks, system_prompt)
        
        messages = [
            {"role": "system", "content": prompt["system"]},
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": prompt["user"]})
        
        return messages
