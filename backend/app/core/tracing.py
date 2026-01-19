"""
Tracing module for LegalOS multi-agent system

Supports both LangSmith (LangChain tracing) and LangFuse for
observability of agent workflows and LLM calls.
"""

import os
from typing import Optional, Dict, Any
from functools import wraps
from contextlib import contextmanager

from .config import settings
from .monitoring import rag_logger


class TracingManager:
    """Manages tracing initialization and configuration"""
    
    def __init__(self):
        """Initialize tracing manager"""
        self._langsmith_initialized = False
        self._langfuse_initialized = False
        self._langfuse_client = None
        
    def initialize_langsmith(self):
        """Initialize LangSmith tracing
        
        Sets environment variables for LangChain to enable tracing.
        """
        if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
            
            if settings.LANGCHAIN_ENDPOINT:
                os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
                
            self._langsmith_initialized = True
            rag_logger.info("LangSmith tracing initialized")
        else:
            rag_logger.info("LangSmith tracing disabled or not configured")
    
    def initialize_langfuse(self):
        """Initialize LangFuse client"""
        try:
            if settings.LANGFUSE_ENABLED and settings.LANGFUSE_PUBLIC_KEY:
                from langfuse import Langfuse
                
                self._langfuse_client = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                    release="1.0.0",
                )
                self._langfuse_initialized = True
                rag_logger.info("LangFuse tracing initialized")
            else:
                rag_logger.info("LangFuse tracing disabled or not configured")
        except ImportError:
            rag_logger.warning("LangFuse package not installed, skipping")
        except Exception as e:
            rag_logger.error(f"Failed to initialize LangFuse: {e}")
    
    def initialize_all(self):
        """Initialize all configured tracing providers"""
        if settings.TRACE_ENABLED:
            self.initialize_langsmith()
            self.initialize_langfuse()
        else:
            rag_logger.info("Tracing disabled globally")
    
    def get_langfuse_client(self):
        """Get LangFuse client instance
        
        Returns:
            LangFuse client or None if not initialized
        """
        return self._langfuse_client
    
    def is_enabled(self) -> bool:
        """Check if any tracing is enabled
        
        Returns:
            True if any tracing is enabled
        """
        return settings.TRACE_ENABLED and (
            self._langsmith_initialized or self._langfuse_initialized
        )


class SpanManager:
    """Manages trace spans for agent execution"""
    
    def __init__(self, tracing_manager: TracingManager):
        """Initialize span manager
        
        Args:
            tracing_manager: TracingManager instance
        """
        self.tracing_manager = tracing_manager
    
    @contextmanager
    def trace_agent_execution(
        self,
        agent_name: str,
        session_id: Optional[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager for tracing agent execution
        
        Args:
            agent_name: Name of the agent being traced
            session_id: Unique session identifier
            metadata: Optional metadata to attach to span
            
        Yields:
            span object or None if tracing disabled
        """
        span = None
        
        if not self.tracing_manager.is_enabled():
            yield None
            return
        
        try:
            langfuse = self.tracing_manager.get_langfuse_client()
            
            if langfuse:
                span = langfuse.trace(
                    name=agent_name,
                    session_id=session_id,
                    metadata=metadata or {},
                )
                rag_logger.debug(f"Started trace span for agent: {agent_name}")
            
            yield span
            
        except Exception as e:
            rag_logger.error(f"Failed to create trace span: {e}")
            yield None
    
    @contextmanager
    def trace_llm_call(
        self,
        model_name: str,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager for tracing LLM calls
        
        Args:
            model_name: Name of the LLM model
            prompt: The prompt being sent
            metadata: Optional metadata to attach
            
        Yields:
            observation object or None if tracing disabled
        """
        observation = None
        
        if not self.tracing_manager.is_enabled():
            yield None, lambda r: None
            return
        
        try:
            langfuse = self.tracing_manager.get_langfuse_client()
            
            if langfuse:
                observation = langfuse.generation(
                    name=f"{model_name}_call",
                    model=model_name,
                    input=prompt,
                    metadata=metadata or {},
                )
                rag_logger.debug(f"Started LLM trace for model: {model_name}")
            
            def finish_generation(response: str, metadata: Optional[Dict[str, Any]] = None):
                """Finish the generation observation
                
                Args:
                    response: The model's response
                    metadata: Additional metadata about the response
                """
                if observation:
                    try:
                        observation.end(
                            output=response,
                            metadata=metadata or {},
                        )
                        rag_logger.debug(f"Finished LLM trace for model: {model_name}")
                    except Exception as e:
                        rag_logger.error(f"Failed to end LLM trace: {e}")
            
            yield observation, finish_generation
            
        except Exception as e:
            rag_logger.error(f"Failed to trace LLM call: {e}")
            yield None, lambda r: None


def trace_function(name: Optional[str] = None):
    """Decorator for tracing function execution
    
    Args:
        name: Custom trace name, defaults to function name
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = name or func.__name__
            rag_logger.debug(f"Tracing function: {func_name}")
            
            try:
                result = await func(*args, **kwargs)
                rag_logger.debug(f"Completed function: {func_name}")
                return result
            except Exception as e:
                rag_logger.error(f"Error in function {func_name}: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = name or func.__name__
            rag_logger.debug(f"Tracing function: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                rag_logger.debug(f"Completed function: {func_name}")
                return result
            except Exception as e:
                rag_logger.error(f"Error in function {func_name}: {e}")
                raise
        
        if hasattr(func, '__await__'):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global tracing manager instance
tracing_manager = TracingManager()
span_manager = SpanManager(tracing_manager)


def initialize_tracing():
    """Initialize tracing on application startup"""
    tracing_manager.initialize_all()


def get_tracing_manager() -> TracingManager:
    """Get global tracing manager instance
    
    Returns:
        TracingManager instance
    """
    return tracing_manager


def get_span_manager() -> SpanManager:
    """Get global span manager instance
    
    Returns:
        SpanManager instance
    """
    return span_manager
