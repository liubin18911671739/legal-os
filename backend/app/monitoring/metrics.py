"""
Metrics Collection Module

This module provides metrics collection for monitoring system performance.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import time
import threading

from app.monitoring.logging import MonitoringLogger

logger = MonitoringLogger()


@dataclass
class MetricValue:
    """A single metric value"""
    value: float
    timestamp: float
    tags: Dict[str, str]
    metric_type: str  # counter, gauge, histogram


@dataclass
class MetricConfig:
    """Configuration for a metric"""
    name: str
    metric_type: str  # counter, gauge, histogram
    description: str
    unit: str = ""
    labels: list = field(default_factory=list)


class MetricsCollector:
    """Collect and track application metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._lock = threading.Lock()
    
    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric

        Args:
            name: Metric name
            value: Increment amount (default 1)
            tags: Additional tags
        """
        timestamp = time.time()
        
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = {}
            current = self._metrics[name].get("counter", 0.0)
            self._metrics[name]["counter"] = current + value
            self._metrics[name]["tags"] = tags or {}
            self._metrics[name]["type"] = "counter"
            self._metrics[name]["unit"] = ""
            self._metrics[name]["timestamp"] = timestamp
        
        # Log to monitoring logger
        logger.system_metric(name, self._metrics[name]["counter"], self._metrics[name].get("unit", ""))
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric

        Args:
            name: Metric name
            value: Current value
            tags: Additional tags
        """
        timestamp = time.time()
        
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = {}
            self._metrics[name]["gauge"] = value
            self._metrics[name]["tags"] = tags or {}
            self._metrics[name]["type"] = "gauge"
            self._metrics[name]["unit"] = ""
            self._metrics[name]["timestamp"] = timestamp
        
        # Log to monitoring logger
        logger.system_metric(name, value, self._metrics[name].get("unit", ""))
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a histogram value

        Args:
            name: Metric name
            value: Value to record
            tags: Additional tags
        """
        timestamp = time.time()
        
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = {}
            current = self._metrics[name].get("histogram", 0.0)
            self._metrics[name]["histogram"] = current + value
            self._metrics[name]["count"] = self._metrics[name].get("count", 0) + 1
            self._metrics[name]["tags"] = tags or {}
            self._metrics[name]["type"] = "histogram"
            self._metrics[name]["unit"] = ""
            self._metrics[name]["timestamp"] = timestamp
        
        # Log to monitoring logger
        logger.system_metric(name, self._metrics[name]["histogram"], self._metrics[name].get("unit", ""))
    
    def timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a timing value as histogram

        Args:
            name: Metric name
            duration: Duration in seconds
            tags: Additional tags
        """
        self.histogram(name, duration, tags)
    
    def get_metric(self, name: str) -> Optional[MetricValue]:
        """
        Get current metric value

        Args:
            name: Metric name

        Returns:
            MetricValue or None
        """
        with self._lock:
            if name not in self._metrics:
                return None
            
            metric_type = self._metrics[name].get("type", "counter")
            value = self._metrics[name].get("counter") or self._metrics[name].get("gauge") or 0.0
            timestamp = self._metrics[name].get("timestamp", 0.0)
            tags = self._metrics[name].get("tags", {})
            unit = self._metrics[name].get("unit", "")
            
            return MetricValue(
                value=value,
                timestamp=last_timestamp,
                tags=tags,
                metric_type=metric_type
            )
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all collected metrics

        Returns:
            Dictionary of all metrics
        """
        with self._lock:
            return dict(self._metrics)
    
    def reset_metric(self, name: str):
        """
        Reset a metric to zero

        Args:
            name: Metric name
        """
        with self._lock:
            if name in self._metrics:
                self._metrics[name] = {
                    "counter": 0.0,
                    "gauge": 0.0,
                    "histogram": [],
                    "count": 0,
                    "tags": {},
                    "type": "counter",
                    "unit": "",
                    "timestamp": time.time()
                }
        
        logger.system_metric(name, 0, "reset")


# Global metrics collector
metrics_collector = MetricsCollector()


class PredefinedMetrics:
    """Predefined metric names and descriptions"""
    
    # RAG Metrics
    RAG_EMBEDDING_REQUESTS = "rag_embedding_requests_total"
    RAG_EMBEDDING_DURATION = "rag_embedding_duration_seconds"
    RAG_RETRIEVAL_REQUESTS = "rag_retrieval_requests_total"
    RAG_RETRIEVAL_RESULTS = "rag_retrieval_results_count"
    RAG_RETRIEVAL_DURATION = "rag_retrieval_duration_seconds"
    RAG_LLM_REQUESTS = "rag_llm_requests_total"
    RAG_LLM_DURATION = "rag_llm_duration_seconds"
    RAG_LLM_TOKENS = "rag_llm_tokens_total"
    RAG_ERROR_COUNT = "rag_errors_total"
    
    # Agent Metrics
    AGENT_COORDINATOR_REQUESTS = "agent_coordinator_requests_total"
    AGENT_COORDINATOR_DURATION = "agent_coordinator_duration_seconds"
    AGENT_RETRIEVAL_REQUESTS = "agent_retrieval_requests_total"
    AGENT_RETRIEVAL_DURATION = "agent_retrieval_duration_seconds"
    AGENT_ANALYSIS_REQUESTS = "agent_analysis_requests_total"
    AGENT_ANALYSIS_DURATION = "agent_analysis_duration_seconds"
    AGENT_REVIEW_REQUESTS = "agent_review_requests_total"
    AGENT_REVIEW_DURATION = "agent_review_duration_seconds"
    AGENT_VALIDATION_REQUESTS = "agent_validation_requests_total"
    AGENT_VALIDATION_DURATION = "agent_validation_duration_seconds"
    AGENT_REPORT_REQUESTS = "agent_report_requests_total"
    AGENT_REPORT_DURATION = "agent_report_duration_seconds"
    AGENT_TOTAL_DURATION = "agent_total_duration_seconds"
    
    # API Metrics
    API_REQUESTS_TOTAL = "api_requests_total"
    API_REQUESTS_SUCCESS = "api_requests_success_total"
    API_REQUESTS_ERROR = "api_requests_error_total"
    API_DURATION = "api_duration_seconds"
    API_ACTIVE_CONNECTIONS = "api_active_connections"
    
    # Database Metrics
    DB_QUERIES_TOTAL = "db_queries_total"
    DB_QUERIES_SUCCESS = "db_queries_success_total"
    DB_QUERIES_ERROR = "db_queries_error_total"
    DB_DURATION = "db_query_duration_seconds"
    DB_CONNECTIONS_ACTIVE = "db_connections_active"
    
    # System Metrics
    SYSTEM_CPU_USAGE = "system_cpu_usage_percent"
    SYSTEM_MEMORY_USAGE = "system_memory_usage_percent"
    SYSTEM_DISK_USAGE = "system_disk_usage_percent"
    SYSTEM_UPTIME_SECONDS = "system_uptime_seconds"


class PerformanceTracker:
    """Track performance of operations"""
    
    def __init__(self):
        self._timings: Dict[str, list] = defaultdict(list)
    
    def start_timing(self, operation_id: str) -> str:
        """
        Start timing an operation

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            Timer ID
        """
        timer_id = f"{operation_id}-{time.time()}"
        self._timings[operation_id].append({
            "timer_id": timer_id,
            "start_time": time.time(),
            "end_time": None,
            "duration": None
        })
        return timer_id
    
    def end_timing(self, operation_id: str, timer_id: str) -> Optional[float]:
        """
        End timing an operation

        args:
            operation_id: Operation ID
            timer_id: Timer ID returned by start_timing

        Returns:
            Duration in seconds, or None if timer not found
        """
        if operation_id not in self._timings:
            return None
        
        # Find timer
        for i, timer in enumerate(self._timings[operation_id]):
            if timer["timer_id"] == timer_id and timer["end_time"] is None:
                self._timings[operation_id][i]["end_time"] = time.time()
                self._timings[operation_id][i]["duration"] = time.time() - timer["start_time"]
                return self._timings[operation_id][i]["duration"]
        
        return None
    
    def get_timings(self, operation_id: str) -> list:
        """Get all timings for an operation"""
        return self._timings.get(operation_id, [])
    
    def get_average_duration(self, operation_id: str) -> Optional[float]:
        """Get average duration for an operation"""
        timings = self.get_timings(operation_id)
        if not timings:
            return None
        
        completed = [t for t in timings if t["duration"] is not None]
        if not completed:
            return None
        
        return sum(t["duration"] for t in completed) / len(completed)


# Global performance tracker
performance_tracker = PerformanceTracker()


class MetricsService:
    """Service for managing metrics and performance tracking"""
    
    def __init__(self):
        self.collector = metrics_collector
        self.tracker = performance_tracker
    
    def rag_embedding_request(self, duration: float):
        """Log RAG embedding request"""
        self.collector.increment(PredefinedMetrics.RAG_EMBEDDING_REQUESTS)
        self.collector.timing(PredefinedMetrics.RAG_EMBEDDING_DURATION, duration)
    
    def rag_retrieval_request(self, duration: float, results_count: int):
        """Log RAG retrieval request"""
        self.collector.increment(PredefinedMetrics.RAG_RETRIEVAL_REQUESTS)
        self.collector.increment(PredefinedMetrics.RAG_RETRIEVAL_RESULTS, value=float(results_count))
        self.collector.timing(Predefined.RAG_RETRIEVAL_DURATION, duration)
    
    def rag_llm_request(self, duration: float, token_count: int):
        """Log RAG LLM request"""
        self.collector.increment(PredefinedMetrics.RAG_LLM_REQUESTS)
        self.collector.timing(PredefinedMetrics.RAG_LLM_DURATION, duration)
        self.collector.increment(PredefinedMetrics.RAG_LLM_TOKENS, value=float(token_count))
    
    def agent_request(self, agent_name: str, duration: float):
        """Log agent request"""
        self.collector.increment(f"agent_{agent_name}_requests_total")
        self.collector.timing(f"agent_{agent_name}_duration_seconds", duration)
    
    def api_request(self, method: str, path: str, duration: float, status_code: int):
        """Log API request"""
        self.collector.increment(PredefinedMetrics.API_REQUESTS_TOTAL)
        if status_code < 400:
            self.collector.increment(PredefinedMetrics.API_REQUESTS_SUCCESS)
        else:
            self.collector.increment(PredefinedMetrics.API_REQUESTS_ERROR)
        self.collector.timing(PredefinedMetrics.API_DURATION, duration)
    
    def db_query(self, operation: str, duration: float, success: bool):
        """Log database query"""
        self.collector.increment(PredefinedMetrics.DB_QUERIES_TOTAL)
        if success:
            self.collector.increment(PredefinedMetrics.DB_QUERIES_SUCCESS)
        else:
            self.collector.increment(Predefined.DB_QUERIES_ERROR)
        self.collector.timing(PredefinedMetrics.DB_DURATION, duration)
    
    def error(self, component: str, error_type: str):
        """Log an error"""
        if component == "rag":
            self.collector.increment(PredefinedMetrics.RAG_ERROR_COUNT)
        elif component == "database":
            self.collector.increment(PredefinedMetrics.DB_QUERIES_ERROR)
        elif component == "api":
            self.collector.increment(PredefinedMetrics.API_REQUESTS_ERROR)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self.collector.get_all_metrics()
    
    def reset_metrics(self):
        """Reset all metrics"""
        all_metrics = self.collector.get_all_metrics()
        for name in all_metrics:
            self.collector.reset_metric(name)


# Global metrics service
metrics_service = MetricsService()


__all__ = [
    "MetricValue",
    "MetricConfig",
    "MetricsCollector",
    "PredefinedMetrics",
    "PerformanceTracker",
    "MetricsService",
    "metrics_collector",
    "performance_tracker",
    "metrics_service",
]
