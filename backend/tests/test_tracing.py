"""
Tests for tracing functionality

Tests cover TracingManager, SpanManager, and integration
with LangGraph workflow and agent nodes.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from app.core.tracing import (
    TracingManager,
    SpanManager,
    trace_function,
    get_tracing_manager,
    get_span_manager,
    initialize_tracing,
)


class TestTracingManager:
    """Test TracingManager initialization and configuration"""
    
    @pytest.fixture
    def tracing_manager(self):
        """Create a fresh TracingManager instance for each test"""
        return TracingManager()
    
    def test_initialize_langsmith_enabled(self, tracing_manager):
        """Test LangSmith initialization when enabled"""
        with patch("app.core.tracing.settings") as mock_settings:
            mock_settings.LANGCHAIN_TRACING_V2 = True
            mock_settings.LANGCHAIN_API_KEY = "test_key"
            mock_settings.LANGCHAIN_PROJECT = "test_project"
            mock_settings.LANGCHAIN_ENDPOINT = ""
            
            tracing_manager.initialize_langsmith()
            
            assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
            assert os.environ.get("LANGCHAIN_API_KEY") == "test_key"
            assert os.environ.get("LANGCHAIN_PROJECT") == "test_project"
            assert tracing_manager._langsmith_initialized is True
    
    def test_initialize_langsmith_disabled(self, tracing_manager):
        """Test LangSmith initialization when disabled"""
        with patch.dict(os.environ, {
            "LANGCHAIN_API_KEY": "",
        }, clear=True):
            tracing_manager.initialize_langsmith()
            
            assert tracing_manager._langsmith_initialized is False
    
    def test_initialize_langfuse_enabled(self, tracing_manager):
        """Test LangFuse initialization when enabled"""
        with patch("app.core.tracing.settings") as mock_settings, \
             patch("langfuse.Langfuse") as mock_langfuse:
            
            mock_client = Mock()
            mock_langfuse.return_value = mock_client
            
            mock_settings.LANGFUSE_ENABLED = True
            mock_settings.LANGFUSE_PUBLIC_KEY = "test_public_key"
            mock_settings.LANGFUSE_SECRET_KEY = "test_secret_key"
            mock_settings.LANGFUSE_HOST = "https://cloud.langfuse.com"
            
            tracing_manager.initialize_langfuse()
            
            mock_langfuse.assert_called_once_with(
                public_key="test_public_key",
                secret_key="test_secret_key",
                host="https://cloud.langfuse.com",
                release="1.0.0",
            )
            assert tracing_manager._langfuse_initialized is True
            assert tracing_manager._langfuse_client == mock_client
    
    def test_initialize_langfuse_disabled(self, tracing_manager):
        """Test LangFuse initialization when disabled"""
        with patch("app.core.tracing.settings") as mock_settings, \
             patch("langfuse.Langfuse") as mock_langfuse:
            
            mock_settings.LANGFUSE_ENABLED = False
            mock_settings.LANGFUSE_PUBLIC_KEY = ""
            
            tracing_manager.initialize_langfuse()
            
            mock_langfuse.assert_not_called()
            assert tracing_manager._langfuse_initialized is False
    
    def test_initialize_langfuse_import_error(self, tracing_manager):
        """Test LangFuse initialization handles import error gracefully"""
        with patch("langfuse.Langfuse") as mock_langfuse, \
             patch("app.core.tracing.settings") as mock_settings:
            
            mock_langfuse.side_effect = ImportError("Langfuse not installed")
            mock_settings.LANGFUSE_ENABLED = True
            mock_settings.LANGFUSE_PUBLIC_KEY = "test_key"
            
            tracing_manager.initialize_langfuse()
            
            assert tracing_manager._langfuse_initialized is False
    
    def test_initialize_all(self, tracing_manager):
        """Test initialization of all tracing providers"""
        with patch.object(tracing_manager, "initialize_langsmith") as mock_langsmith, \
             patch.object(tracing_manager, "initialize_langfuse") as mock_langfuse, \
             patch("app.core.tracing.settings") as mock_settings:
            
            mock_settings.TRACE_ENABLED = True
            
            tracing_manager.initialize_all()
            
            mock_langsmith.assert_called_once()
            mock_langfuse.assert_called_once()
    
    def test_get_langfuse_client(self, tracing_manager):
        """Test getting LangFuse client"""
        mock_client = Mock()
        tracing_manager._langfuse_client = mock_client
        tracing_manager._langfuse_initialized = True
        
        client = tracing_manager.get_langfuse_client()
        
        assert client == mock_client
    
    def test_is_enabled(self, tracing_manager):
        """Test checking if tracing is enabled"""
        tracing_manager._langsmith_initialized = False
        tracing_manager._langfuse_initialized = False
        
        assert tracing_manager.is_enabled() is False
        
        tracing_manager._langsmith_initialized = True
        
        assert tracing_manager.is_enabled() is True


class TestSpanManager:
    """Test SpanManager for agent execution and LLM call tracing"""
    
    @pytest.fixture
    def span_manager(self, mock_tracing_manager):
        """Create SpanManager with mocked TracingManager"""
        return SpanManager(mock_tracing_manager)
    
    @pytest.fixture
    def mock_tracing_manager(self):
        """Create mock TracingManager"""
        manager = Mock(spec=TracingManager)
        manager.is_enabled.return_value = False
        return manager
    
    def test_trace_agent_execution_disabled(self, span_manager):
        """Test agent execution tracing when disabled"""
        with span_manager.trace_agent_execution(
            agent_name="test_agent",
            session_id="test_session",
            metadata={"key": "value"}
        ) as span:
            assert span is None
    
    def test_trace_agent_execution_enabled(self, span_manager):
        """Test agent execution tracing when enabled"""
        with patch("langfuse.Langfuse") as mock_langfuse:
            mock_client = Mock()
            mock_span = Mock()
            mock_client.trace.return_value = mock_span
            
            span_manager.tracing_manager.is_enabled.return_value = True
            span_manager.tracing_manager._langfuse_client = mock_client
            
            with span_manager.trace_agent_execution(
                agent_name="test_agent",
                session_id="test_session",
                metadata={"key": "value"}
            ) as span:
                assert span == mock_span
                mock_client.trace.assert_called_once_with(
                    name="test_agent",
                    session_id="test_session",
                    metadata={"key": "value"},
                )
    
    def test_trace_llm_call_disabled(self, span_manager):
        """Test LLM call tracing when disabled"""
        with span_manager.trace_llm_call(
            model_name="test_model",
            prompt="test prompt",
            metadata={"key": "value"}
        ) as (obs, finish):
            assert obs is None
            assert callable(finish)
    
    def test_trace_llm_call_enabled(self, span_manager):
        """Test LLM call tracing when enabled"""
        with patch("langfuse.Langfuse") as mock_langfuse:
            mock_client = Mock()
            mock_observation = Mock()
            mock_client.generation.return_value = mock_observation
            
            span_manager.tracing_manager.is_enabled.return_value = True
            span_manager.tracing_manager._langfuse_client = mock_client
            
            with span_manager.trace_llm_call(
                model_name="test_model",
                prompt="test prompt",
                metadata={"key": "value"}
            ) as (obs, finish):
                assert obs == mock_observation
                mock_client.generation.assert_called_once_with(
                    name="test_model_call",
                    model="test_model",
                    input="test prompt",
                    metadata={"key": "value"},
                )
                
                # Test finish function
                finish("test response", {"response_key": "value"})
                mock_observation.end.assert_called_once_with(
                    output="test response",
                    metadata={"response_key": "value"},
                )


class TestTraceFunctionDecorator:
    """Test trace_function decorator"""
    
    @pytest.mark.asyncio
    async def test_async_function_decorator(self):
        """Test decorator on async function"""
        @trace_function(name="test_async")
        async def async_func(x, y):
            return x + y
        
        result = await async_func(2, 3)
        assert result == 5
    
    def test_sync_function_decorator(self):
        """Test decorator on sync function"""
        @trace_function(name="test_sync")
        def sync_func(x, y):
            return x * y
        
        result = sync_func(3, 4)
        assert result == 12
    
    @pytest.mark.asyncio
    async def test_async_function_exception_handling(self):
        """Test decorator handles exceptions in async functions"""
        @trace_function(name="test_exception")
        async def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            await failing_func()


class TestGlobalFunctions:
    """Test global tracing utility functions"""
    
    @patch("app.core.tracing.tracing_manager")
    def test_get_tracing_manager(self, mock_manager):
        """Test getting global tracing manager"""
        result = get_tracing_manager()
        assert result == mock_manager
    
    @patch("app.core.tracing.span_manager")
    def test_get_span_manager(self, mock_manager):
        """Test getting global span manager"""
        result = get_span_manager()
        assert result == mock_manager
    
    @patch("app.core.tracing.tracing_manager")
    def test_initialize_tracing(self, mock_manager):
        """Test initialize_tracing function"""
        initialize_tracing()
        mock_manager.initialize_all.assert_called_once()


@pytest.mark.asyncio
class TestTracingIntegration:
    """Test tracing integration with agent workflow"""
    
    @patch("app.agents.coordinator.get_span_manager")
    async def test_coordinator_node_tracing(self, mock_get_span_manager):
        """Test that coordinator node includes tracing"""
        from app.agents.coordinator import coordinator_node
        from app.agents.state import create_initial_state, ContractType
        
        mock_span_manager = Mock()
        mock_span = Mock()
        mock_span_manager.trace_agent_execution.return_value.__enter__ = Mock(return_value=mock_span)
        mock_span_manager.trace_agent_execution.return_value.__exit__ = Mock(return_value=None)
        mock_get_span_manager.return_value = mock_span_manager
        
        state = create_initial_state(
            contract_id="test_contract_123",
            contract_text="test contract",
            contract_type=ContractType.EMPLOYMENT,
            session_id="test_session",
        )
        
        result = await coordinator_node(state)
        
        assert result is not None
        mock_span_manager.trace_agent_execution.assert_called()
    
    @patch("app.agents.analysis.get_span_manager")
    async def test_analysis_node_tracing(self, mock_get_span_manager):
        """Test that analysis node includes tracing"""
        from app.agents.analysis import analysis_node
        from app.agents.state import create_initial_state, ContractType
        
        mock_span_manager = Mock()
        mock_span = Mock()
        mock_span_manager.trace_agent_execution.return_value.__enter__ = Mock(return_value=mock_span)
        mock_span_manager.trace_agent_execution.return_value.__exit__ = Mock(return_value=None)
        mock_get_span_manager.return_value = mock_span_manager
        
        state = create_initial_state(
            contract_id="test_contract_123",
            contract_text="test contract",
            contract_type=ContractType.EMPLOYMENT,
            session_id="test_session",
        )
        
        result = await analysis_node(state)
        
        assert result is not None
        mock_span_manager.trace_agent_execution.assert_called()
    
    @patch("app.agents.analysis.get_span_manager")
    async def test_analysis_node_tracing(self, mock_get_span_manager):
        """Test that analysis node includes tracing"""
        from app.agents.analysis import analysis_node
        from app.agents.state import create_initial_state
        
        mock_span_manager = Mock()
        mock_span = Mock()
        mock_span_manager.trace_agent_execution.return_value.__enter__ = Mock(return_value=mock_span)
        mock_span_manager.trace_agent_execution.return_value.__exit__ = Mock(return_value=None)
        mock_get_span_manager.return_value = mock_span_manager
        
        state = create_initial_state(
            contract_id="test_contract_123",
            contract_text="test contract",
            contract_type="employment",
            session_id="test_session",
        )
        
        result = await analysis_node(state)
        
        assert result is not None
        mock_span_manager.trace_agent_execution.assert_called()
