import logging
import sys
from typing import Optional
from datetime import datetime


class LoggerConfig:
    """Configuration for application logger"""
    
    @staticmethod
    def setup_logger(
        name: str,
        level: str = "INFO",
        log_file: Optional[str] = None,
    ) -> logging.Logger:
        """Setup logger with formatting
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for logging to file
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        
        return logger


class MetricsTracker:
    """Track application metrics"""
    
    def __init__(self):
        """Initialize metrics tracker"""
        self._metrics = {
            "queries_total": 0,
            "queries_successful": 0,
            "queries_failed": 0,
            "documents_processed": 0,
            "chunks_indexed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "embedding_requests": 0,
            "vector_searches": 0,
            "errors": {},
        }
    
    def increment(self, metric: str, amount: int = 1):
        """Increment a metric
        
        Args:
            metric: Metric name
            amount: Amount to increment
        """
        if metric in self._metrics:
            self._metrics[metric] += amount
        elif metric == "errors":
            pass  # Errors handled separately
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def track_error(self, error_type: str):
        """Track an error occurrence
        
        Args:
            error_type: Type of error
        """
        if error_type not in self._metrics["errors"]:
            self._metrics["errors"][error_type] = 0
        self._metrics["errors"][error_type] += 1
    
    def get_metrics(self) -> dict:
        """Get all metrics
        
        Returns:
            Dictionary of all metrics
        """
        metrics = self._metrics.copy()
        
        # Calculate derived metrics
        if metrics["queries_total"] > 0:
            metrics["success_rate"] = (
                metrics["queries_successful"] / metrics["queries_total"]
            )
        else:
            metrics["success_rate"] = 0.0
        
        if (metrics["cache_hits"] + metrics["cache_misses"]) > 0:
            metrics["cache_hit_rate"] = (
                metrics["cache_hits"] / 
                (metrics["cache_hits"] + metrics["cache_misses"])
            )
        else:
            metrics["cache_hit_rate"] = 0.0
        
        metrics["total_errors"] = sum(metrics["errors"].values())
        
        return metrics
    
    def reset(self):
        """Reset all metrics to zero"""
        self._metrics = {
            "queries_total": 0,
            "queries_successful": 0,
            "queries_failed": 0,
            "documents_processed": 0,
            "chunks_indexed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "embedding_requests": 0,
            "vector_searches": 0,
            "errors": {},
        }


# Global metrics tracker
metrics = MetricsTracker()


# Loggers
rag_logger = LoggerConfig.setup_logger("rag", level="INFO")
api_logger = LoggerConfig.setup_logger("api", level="INFO")
db_logger = LoggerConfig.setup_logger("database", level="WARNING")
