from typing import List, Dict, Any, AsyncIterator, Optional
from dataclasses import dataclass

from .base import BaseLLM
from .context_builder import ContextBuilder
from ..retrieval import RetrievalPipeline, RetrievedChunk, RetrievalConfig


@dataclass
class RAGResponse:
    """Response from RAG pipeline"""
    answer: str
    sources: List[Dict[str, Any]]
    chunks_used: int
    query: str


class RAGPipeline:
    """Retrieval Augmented Generation pipeline"""

    def __init__(
        self,
        llm: BaseLLM,
        retrieval_pipeline: RetrievalPipeline,
        context_builder: Optional[ContextBuilder] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize RAG pipeline

        Args:
            llm: Language model for generation
            retrieval_pipeline: Pipeline for retrieving relevant chunks
            context_builder: Builder for formatting context
            system_prompt: Custom system prompt
        """
        self.llm = llm
        self.retrieval_pipeline = retrieval_pipeline
        self.context_builder = context_builder or ContextBuilder()
        self.system_prompt = system_prompt

    async def query(
        self,
        query: str,
        retrieval_config: Optional[RetrievalConfig] = None,
    ) -> RAGResponse:
        """Process a query through the RAG pipeline

        Args:
            query: User question
            retrieval_config: Optional retrieval configuration

        Returns:
            RAGResponse with answer and sources
        """
        # Retrieve relevant chunks
        chunks = await self.retrieval_pipeline.retrieve(
            query,
            config=retrieval_config,
        )

        if not chunks:
            return RAGResponse(
                answer="I couldn't find relevant information to answer your question.",
                sources=[],
                chunks_used=0,
                query=query,
            )

        # Build messages with context
        messages = self.context_builder.build_messages(
            query=query,
            chunks=chunks,
            system_prompt=self.system_prompt,
        )

        # Generate response
        answer = await self.llm.generate_with_messages(messages)

        # Extract sources
        sources = [
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "score": chunk.score,
            }
            for chunk in chunks
        ]

        return RAGResponse(
            answer=answer,
            sources=sources,
            chunks_used=len(chunks),
            query=query,
        )

    async def query_stream(
        self,
        query: str,
        retrieval_config: Optional[RetrievalConfig] = None,
    ) -> AsyncIterator[str]:
        """Process a query with streaming response

        Args:
            query: User question
            retrieval_config: Optional retrieval configuration

        Yields:
            Chunks of the generated answer
        """
        # Retrieve relevant chunks
        chunks = await self.retrieval_pipeline.retrieve(
            query,
            config=retrieval_config,
        )

        if not chunks:
            yield "I couldn't find relevant information to answer your question."
            return

        # Build prompt
        prompt_dict = self.context_builder.build_prompt(
            query=query,
            chunks=chunks,
            system_prompt=self.system_prompt,
        )

        # Stream response
        full_response = ""
        async for chunk in self.llm.stream_generate(prompt_dict["user"]):
            full_response += chunk
            yield chunk

    async def query_with_history(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        retrieval_config: Optional[RetrievalConfig] = None,
    ) -> RAGResponse:
        """Process a query with conversation history

        Args:
            query: Current user question
            conversation_history: Previous conversation turns
            retrieval_config: Optional retrieval configuration

        Returns:
            RAGResponse with answer and sources
        """
        # Retrieve relevant chunks
        chunks = await self.retrieval_pipeline.retrieve(
            query,
            config=retrieval_config,
        )

        if not chunks:
            return RAGResponse(
                answer="I couldn't find relevant information to answer your question.",
                sources=[],
                chunks_used=0,
                query=query,
            )

        # Build messages with context and history
        messages = self.context_builder.build_messages(
            query=query,
            chunks=chunks,
            system_prompt=self.system_prompt,
            conversation_history=conversation_history,
        )

        # Generate response
        answer = await self.llm.generate_with_messages(messages)

        # Extract sources
        sources = [
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "score": chunk.score,
            }
            for chunk in chunks
        ]

        return RAGResponse(
            answer=answer,
            sources=sources,
            chunks_used=len(chunks),
            query=query,
        )

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics from retrieval pipeline

        Returns:
            Dictionary with cache stats if available
        """
        return self.retrieval_pipeline.get_cache_stats()

    async def health_check(self) -> bool:
        """Check if RAG pipeline is healthy

        Returns:
            True if all components are healthy
        """
        try:
            retrieval_healthy = await self.retrieval_pipeline.health_check()
            return retrieval_healthy
        except Exception:
            return False
