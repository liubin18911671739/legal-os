import structlog
import logging
import sys
from typing import Optional
from contextvars import ContextVar
from uuid import uuid4


request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_output: bool = True,
) -> None:
    """Setup structured logging for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file
        json_output: Whether to output logs in JSON format
    """
    # Configure structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if json_output:
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        shared_processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        )
    
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID for logging context
    
    Args:
        request_id: Request ID to set. If None, generates a new one.
        
    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid4())
    request_id_var.set(request_id)
    return request_id


def set_user_id(user_id: Optional[str]) -> None:
    """Set user ID for logging context
    
    Args:
        user_id: User ID to set
    """
    user_id_var.set(user_id)


def add_context(**kwargs) -> None:
    """Add context to the current logging context
    
    Args:
        **kwargs: Key-value pairs to add to context
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all logging context"""
    structlog.contextvars.clear_contextvars()


class LoggingMiddleware:
    """Middleware to add logging context to requests"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID
        request_id = set_request_id()
        
        # Add request context
        method = scope["method"]
        path = scope["path"]
        client_host = scope.get("client", [""])[0]
        
        add_context(
            request_id=request_id,
            method=method,
            path=path,
            client_host=client_host,
        )
        
        logger = get_logger("api")
        logger.info("request_started")
        
        # Send response
        await self.app(scope, receive, send)
        
        logger.info("request_completed")
        
        # Clear context
        clear_context()


def log_function_call(func):
    """Decorator to log function calls
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(
            "function_called",
            function=func.__name__,
            args=str(args),
            kwargs=str(kwargs),
        )
        result = func(*args, **kwargs)
        logger.info(
            "function_completed",
            function=func.__name__,
            result=type(result).__name__,
        )
        return result
    return wrapper


def log_agent_execution(agent_name: str):
    """Decorator to log agent execution
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = get_logger("agents")
            
            # Add agent context
            add_context(agent=agent_name)
            
            logger.info("agent_started")
            
            try:
                result = await func(*args, **kwargs)
                logger.info("agent_completed")
                return result
            except Exception as e:
                logger.error("agent_failed", error=str(e), error_type=type(e).__name__)
                raise
            finally:
                clear_context()
        
        return wrapper
    return decorator


def log_llm_request(model: str, temperature: float = None):
    """Decorator to log LLM requests
    
    Args:
        model: Model name
        temperature: Model temperature
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = get_logger("llm")
            
            logger.info(
                "llm_request_started",
                model=model,
                temperature=temperature,
            )
            
            try:
                result = await func(*args, **kwargs)
                logger.info(
                    "llm_request_completed",
                    model=model,
                    tokens_used=getattr(result, "tokens_used", None),
                    cost=getattr(result, "cost", None),
                )
                return result
            except Exception as e:
                logger.error(
                    "llm_request_failed",
                    model=model,
                    error=str(e),
                )
                raise
        
        return wrapper
    return decorator
