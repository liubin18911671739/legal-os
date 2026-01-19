"""
Monitoring Module

This module provides structured logging, metrics collection, and monitoring utilities.
"""

import logging
import logging.config
import sys
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime
import json

try:
    from structlog import get_logger, configure, processors
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("Warning: structlog not installed. Falling back to standard logging.")

from app.core.config import settings


class LogLevel:
    """Standardized log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


if STRUCTLOG_AVAILABLE:
    # Configure structlog
    configure(
        processors=[
            processors.add_log_level,
            processors.JSONRenderer()
        ],
        logger_factory=processors.CallsiteParameterLogger(),
        cache_logger_on_first_use=True,
    )

    # Create loggers
    rag_logger = get_logger("legalos.rag")
    api_logger = get_logger("legalos.api")
    db_logger = get_logger("legalos.database")
    agent_logger = get_logger("legalos.agents")
    monitoring_logger = get_logger("legalos.monitoring")
    security_logger = get_logger("legalos.security")

    def setup_logging(level: str = "INFO"):
        """Setup logging level"""
        import logging
        logging_level = getattr(logging, level.upper(), logging.INFO)
        
        for logger in [rag_logger, api_logger, db_logger, agent_logger, monitoring_logger, security_logger]:
            # structlog sets level separately
            logging.getLogger("legalos.rag").setLevel(logging_level)
            logging.getLogger("legalos.api").setLevel(logging_level)
            logging.getLogger("legalos.database").setLevel(logging_level)
            logging.getLogger("legalos.agents").setLevel(logging_level)
            logging.getLogger("legalos.monitoring").setLevel(logging_level)
            logging.getLogger("legalos.security").setLevel(logging_level)
        
        print(f"Logging level set to: {level}")
    
else:
    # Fallback to standard logging
    rag_logger = logging.getLogger("legalos.rag")
    api_logger = logging.getLogger("legalos.api")
    db_logger = logging.getLogger("legalos.database")
    agent_logger = logging.getLogger("legalos.agents")
    monitoring_logger = logging.getLogger("legalos.monitoring")
    security_logger = logging.getLogger("legalos.security")

    def setup_logging(level: str = "INFO"):
        """Setup logging level for standard logging"""
        logging_level = getattr(logging, level.upper(), logging.INFO)
        
        for logger in [rag_logger, api_logger, db_logger, agent_logger, monitoring_logger, security_logger]:
            logger.setLevel(logging_level)
            # Add stream handler
            if not logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
                logger.addHandler(handler)
        
        print(f"Logging level set to: {level} (using standard logging)")


class LogContext:
    """Helper class for structured logging context"""
    
    @staticmethod
    def get_log_context(**kwargs) -> Dict[str, Any]:
        """Get common log context"""
        return {
            "app": "legalos",
            "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "development",
            **kwargs
        }


class RAGLogger:
    """Logger for RAG operations"""
    
    def __init__(self):
        self.logger = rag_logger
    
    def embedding_request(self, text: str, model: str):
        """Log embedding request"""
        self.logger.info(
            "embedding_request",
            extra={
                "text_length": len(text),
                "model": model,
                "context": LogContext.get_log_context(component="rag", operation="embedding")
            }
        )
    
    def embedding_response(self, text: str, model: str, duration: float, token_count: int = 0):
        """Log embedding response"""
        self.logger.info(
            "embedding_response",
            extra={
                "text_length": len(text),
                "model": model,
                "duration": duration,
                "token_count": token_count,
                "context": LogContext.get_log_context(component="rag", operation="embedding")
            }
        )
    
    def retrieval_request(self, query: str, retrieval_type: str):
        """Log retrieval request"""
        self.logger.info(
            "retrieval_request",
            extra={
                "query": query,
                "type": retrieval_type,
                "context": LogContext.get_log_context(component="rag", operation="retrieval")
            }
        )
    
    def retrieval_response(self, query: str, results_count: int, duration: float, retrieval_type: str):
        """Log retrieval response"""
        self.logger.info(
            "retrieval_response",
            extra={
                "query": query,
                "results_count": results_count,
                "duration": duration,
                "type": retrieval_type,
                "context": LogContext.get_log_context(component="rag", operation="retrieval")
            }
        )
    
    def llm_request(self, prompt: str, model: str, agent: str = None):
        """Log LLM request"""
        self.logger.info(
            "llm_request",
            extra={
                "prompt_length": len(prompt),
                "model": model,
                "agent": agent or "unknown",
                "context": LogContext.get_log_context(component="llm", operation="request")
            }
        )
    
    def llm_response(self, prompt: str, model: str, agent: str = None, duration: float, token_usage: int = 0, error: str = None):
        """Log LLM response"""
        if error:
            self.logger.error(
                "llm_error",
                extra={
                    "error": error,
                    "agent": agent or "unknown",
                    "context": LogContext.get_log_context(component="llm", operation="response")
                }
            )
        else:
            self.logger.info(
                "llm_response",
                extra={
                    "prompt_length": len(prompt),
                    "model": model,
                    "agent": agent or "unknown",
                    "duration": duration,
                    "token_usage": token_usage,
                    "context": LogContext.get_log_context(component="llm", operation="response")
                }
            )


class APILogger:
    """Logger for API operations"""
    
    def __init__(self):
        self.logger = api_logger
    
    def request_received(self, method: str, path: str, client_ip: str = None):
        """Log API request received"""
        self.logger.info(
            "api_request",
            extra={
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "context": LogContext.get_log_context(component="api", operation="request")
            }
        )
    
    def request_completed(self, method: str, path: str, status_code: int, duration: float):
        """Log API request completed"""
        level = "info" if status_code < 400 else "error"
        self.logger.info(
            "api_response",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration,
                "level": level,
                "context": LogContext.get_log_context(component="api", operation="response")
            }
        )
    
    def request_error(self, method: str, path: str, error: str, duration: float):
        """Log API request error"""
        self.logger.error(
            "api_error",
            extra={
                "method": method,
                "path": path,
                "error": error,
                "duration": duration,
                "context": LogContext.get_log_context(component="api", operation="error")
            }
        )


class AgentLogger:
    """Logger for agent operations"""
    
    def __init__(self):
        self.logger = agent_logger
    
    def agent_start(self, agent_name: str, task_id: str):
        """Log agent start"""
        self.logger.info(
            "agent_start",
            extra={
                "agent": agent_name,
                "task_id": task_id,
                "context": LogContext.get_log_context(component="agent", operation="start")
            }
        )
    
    def agent_complete(self, agent_name: str, task_id: str, duration: float, output_length: int = 0):
        """Log agent completion"""
        self.logger.info(
            "agent_complete",
            extra={
                "agent": agent_name,
                "task_id": task_id,
                "duration": duration,
                "output_length": output_length,
                "context": LogContext.get_log_context(component="agent", operation="complete")
            }
        )
    
    def agent_error(self, agent_name: str, task_id: str, error: str):
        """Log agent error"""
        self.logger.error(
            "agent_error",
            extra={
                "agent": agent_name,
                "task_id": task_id,
                "error": error,
                "context": LogContext.get_log_context(component="agent", operation="error")
            }
        )


class DatabaseLogger:
    """Logger for database operations"""
    
    def __init__(self):
        self.logger = db_logger
    
    def query_start(self, operation: str, table: str):
        """Log database query start"""
        self.logger.debug(
            "db_query_start",
            extra={
                "operation": operation,
                "table": table,
                "context": LogContext.get_log_context(component="database", operation="query")
            }
        )
    
    def query_complete(self, operation: str, table: str, duration: float, row_count: int = 0):
        """Log database query completion"""
        self.logger.debug(
            "db_query_complete",
            extra={
                "operation": operation,
                "table": table,
                "duration": duration,
                "row_count": row_count,
                "context": LogContext.get_log_context(component="database", operation="complete")
            }
        )
    
    def query_error(self, operation: str, table: str, error: str, duration: float):
        """Log database query error"""
        self.logger.error(
            "db_query_error",
            extra={
                "operation": operation,
                "table": table,
                "error": error,
                "duration": duration,
                "context": LogContext.get_log_context(component="database", operation="error")
            }
        )


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self):
        self.logger = security_logger
    
    def authentication_event(self, user_id: str = None, success: bool = True, ip: str = None):
        """Log authentication event"""
        self.logger.info(
            "authentication_event",
            extra={
                "user_id": user_id,
                "success": success,
                "ip": ip,
                "context": LogContext.get_log_context(component="security", operation="authentication")
            }
        )
    
    def authorization_event(self, user_id: str, resource: str, action: str, allowed: bool = True):
        """Log authorization event"""
        self.logger.info(
            "authorization_event",
            extra={
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "allowed": allowed,
                "context": LogContext.get_log_context(component="security", operation="authorization")
            }
        )
    
    def suspicious_activity(self, user_id: str, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        self.logger.warning(
            "suspicious_activity",
            extra={
                "user_id": user_id,
                "activity_type": activity_type,
                "details": details,
                "context": LogContext.get_log_context(component="security", operation="suspicious")
            }
        )


class MonitoringLogger:
    """Logger for monitoring events"""
    
    def __init__(self):
        self.logger = monitoring_logger
    
    def system_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log system metric"""
        self.logger.info(
            "system_metric",
            extra={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": LogContext.get_log_context(component="monitoring", operation="metric")
            }
        )
    
    def health_check(self, service: str, status: str, duration: float = 0):
        """Log health check result"""
        self.logger.info(
            "health_check",
            extra={
                "service": service,
                "status": status,
                "duration": duration,
                "context": LogContext.get_log_context(component="monitoring", operation="health_check")
            }
        )


# Export loggers
__all__ = [
    "LogLevel",
    "LogContext",
    "RAGLogger",
    "APILogger",
    "AgentLogger",
    "DatabaseLogger",
    "SecurityLogger",
    "MonitoringLogger",
    "setup_logging",
    "rag_logger",
    "api_logger",
    "db_logger",
    "agent_logger",
    "monitoring_logger",
    "security_logger",
]
