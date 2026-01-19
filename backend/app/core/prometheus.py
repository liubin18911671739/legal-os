import time
from typing import Optional, Dict, Any
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from contextlib import contextmanager
import asyncio


# Custom registry
registry = CollectorRegistry()


# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=registry
)

# RAG Metrics
rag_queries_total = Counter(
    'rag_queries_total',
    'Total RAG queries',
    ['query_type', 'retrieval_method'],
    registry=registry
)

rag_query_duration_seconds = Histogram(
    'rag_query_duration_seconds',
    'RAG query latency',
    ['agent', 'stage'],
    registry=registry
)

rag_cache_hits = Counter(
    'rag_cache_hits',
    'Total RAG cache hits',
    ['cache_type'],
    registry=registry
)

rag_cache_misses = Counter(
    'rag_cache_misses',
    'Total RAG cache misses',
    ['cache_type'],
    registry=registry
)

# LLM Metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'agent'],
    registry=registry
)

llm_requests_failed = Counter(
    'llm_requests_failed',
    'Total failed LLM requests',
    ['model', 'agent', 'error_type'],
    registry=registry
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'token_type', 'agent'],
    registry=registry
)

llm_cost_total = Counter(
    'llm_cost_total',
    'Total LLM cost',
    ['model', 'agent'],
    registry=registry
)

llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'LLM request latency',
    ['model', 'agent'],
    registry=registry
)

# Database Metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'table'],
    registry=registry
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['operation', 'table'],
    registry=registry
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    registry=registry
)

# Agent Metrics
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status'],
    registry=registry
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution latency',
    ['agent_name'],
    registry=registry
)

# Document Metrics
documents_processed_total = Counter(
    'documents_processed_total',
    'Total documents processed',
    ['document_type', 'status'],
    registry=registry
)

chunks_indexed_total = Counter(
    'chunks_indexed_total',
    'Total chunks indexed',
    ['index_type'],
    registry=registry
)

# System Metrics
system_errors_total = Counter(
    'system_errors_total',
    'Total system errors',
    ['error_type', 'component'],
    registry=registry
)

# Application Info
app_info = Info(
    'app_info',
    'Application information',
    registry=registry
)


def track_http_request(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def track_rag_query(query_type: str, retrieval_method: str, duration: float):
    """Track RAG query metrics
    
    Args:
        query_type: Type of query (e.g., 'contract', 'knowledge')
        retrieval_method: Retrieval method (e.g., 'vector', 'hybrid')
        duration: Query duration in seconds
    """
    rag_queries_total.labels(
        query_type=query_type,
        retrieval_method=retrieval_method
    ).inc()
    rag_query_duration_seconds.labels(
        agent='rag',
        stage='retrieval'
    ).observe(duration)


def track_cache_hit(cache_type: str):
    """Track cache hit
    
    Args:
        cache_type: Type of cache (e.g., 'embedding', 'retrieval')
    """
    rag_cache_hits.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """Track cache miss
    
    Args:
        cache_type: Type of cache (e.g., 'embedding', 'retrieval')
    """
    rag_cache_misses.labels(cache_type=cache_type).inc()


def track_llm_request(
    model: str,
    agent: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    duration: float,
    success: bool = True,
    error_type: Optional[str] = None
):
    """Track LLM request metrics
    
    Args:
        model: LLM model name
        agent: Agent name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cost: Request cost
        duration: Request duration in seconds
        success: Whether request succeeded
        error_type: Type of error if failed
    """
    llm_requests_total.labels(model=model, agent=agent).inc()
    
    if success:
        llm_tokens_total.labels(model=model, token_type='input', agent=agent).inc(input_tokens)
        llm_tokens_total.labels(model=model, token_type='output', agent=agent).inc(output_tokens)
        llm_cost_total.labels(model=model, agent=agent).inc(cost)
    else:
        llm_requests_failed.labels(
            model=model,
            agent=agent,
            error_type=error_type or 'unknown'
        ).inc()
    
    llm_request_duration_seconds.labels(model=model, agent=agent).observe(duration)


def track_db_query(operation: str, table: str, duration: float):
    """Track database query metrics
    
    Args:
        operation: Type of operation (e.g., 'select', 'insert')
        table: Database table
        duration: Query duration in seconds
    """
    db_queries_total.labels(operation=operation, table=table).inc()
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)


def set_db_connections(count: int):
    """Set active database connections
    
    Args:
        count: Number of active connections
    """
    db_connections_active.set(count)


def track_agent_execution(agent_name: str, duration: float, status: str = 'success'):
    """Track agent execution metrics
    
    Args:
        agent_name: Name of the agent
        duration: Execution duration in seconds
        status: Execution status (success, failed, timeout)
    """
    agent_executions_total.labels(
        agent_name=agent_name,
        status=status
    ).inc()
    agent_execution_duration_seconds.labels(
        agent_name=agent_name
    ).observe(duration)


def track_document_processing(document_type: str, status: str):
    """Track document processing metrics
    
    Args:
        document_type: Type of document (pdf, docx, txt)
        status: Processing status (success, failed)
    """
    documents_processed_total.labels(
        document_type=document_type,
        status=status
    ).inc()


def track_chunk_indexed(index_type: str):
    """Track chunk indexing metrics
    
    Args:
        index_type: Type of index (vector, bm25)
    """
    chunks_indexed_total.labels(index_type=index_type).inc()


def track_error(error_type: str, component: str):
    """Track system errors
    
    Args:
        error_type: Type of error
        component: Component where error occurred
    """
    system_errors_total.labels(
        error_type=error_type,
        component=component
    ).inc()


def set_app_info(version: str, environment: str):
    """Set application information
    
    Args:
        version: Application version
        environment: Environment (dev, staging, prod)
    """
    app_info.info({
        'version': version,
        'environment': environment
    })


def get_metrics() -> bytes:
    """Get Prometheus metrics
    
    Returns:
        Metrics in Prometheus format
    """
    return generate_latest(registry)


def get_metrics_text() -> str:
    """Get Prometheus metrics as text
    
    Returns:
        Metrics as text string
    """
    return get_metrics().decode('utf-8')


@contextmanager
def track_http_request_context(method: str, endpoint: str):
    """Context manager to track HTTP requests
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        
    Yields:
        None
    """
    start_time = time.time()
    status = 200
    try:
        yield
    except Exception:
        status = 500
        raise
    finally:
        duration = time.time() - start_time
        track_http_request(method, endpoint, status, duration)


async def track_async_function(duration_metric: Histogram, labels: Dict[str, str]):
    """Async context manager to track function duration
    
    Args:
        duration_metric: Histogram metric to use
        labels: Labels for the metric
        
    Yields:
        None
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        duration_metric.labels(**labels).observe(duration)


def time_it(metric: Histogram, **labels):
    """Decorator to track function execution time
    
    Args:
        metric: Histogram metric to use
        **labels: Labels for the metric
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                metric.labels(**labels).observe(time.time() - start_time)
                return result
            except Exception as e:
                track_error(type(e).__name__, func.__module__)
                metric.labels(**labels).observe(time.time() - start_time)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                metric.labels(**labels).observe(time.time() - start_time)
                return result
            except Exception as e:
                track_error(type(e).__name__, func.__module__)
                metric.labels(**labels).observe(time.time() - start_time)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
