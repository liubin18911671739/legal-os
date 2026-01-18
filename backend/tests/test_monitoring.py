import pytest
from app.core.monitoring import (
    LoggerConfig,
    MetricsTracker,
    metrics,
    rag_logger,
    api_logger,
    db_logger,
)


class TestLoggerConfig:
    """Test cases for LoggerConfig"""

    def test_setup_logger(self):
        """Test logger setup"""
        logger = LoggerConfig.setup_logger("test_logger", level="INFO")
        
        assert logger.name == "test_logger"
        assert logger.level == 20  # INFO level

    def test_setup_logger_with_file(self, tmp_path):
        """Test logger setup with file output"""
        log_file = tmp_path / "test.log"
        logger = LoggerConfig.setup_logger(
            "test_file_logger",
            level="DEBUG",
            log_file=str(log_file),
        )
        
        assert logger.name == "test_file_logger"
        
        logger.info("Test message")
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content

    def test_setup_logger_different_levels(self):
        """Test logger setup with different levels"""
        debug_logger = LoggerConfig.setup_logger("debug_logger", level="DEBUG")
        info_logger = LoggerConfig.setup_logger("info_logger", level="INFO")
        error_logger = LoggerConfig.setup_logger("error_logger", level="ERROR")
        
        assert debug_logger.level == 10  # DEBUG
        assert info_logger.level == 20  # INFO
        assert error_logger.level == 40  # ERROR

    def test_global_loggers_exist(self):
        """Test that global loggers are configured"""
        assert rag_logger is not None
        assert api_logger is not None
        assert db_logger is not None
        assert rag_logger.name == "rag"
        assert api_logger.name == "api"
        assert db_logger.name == "database"


class TestMetricsTracker:
    """Test cases for MetricsTracker"""

    @pytest.fixture
    def tracker(self):
        """Create fresh tracker for each test"""
        tracker = MetricsTracker()
        return tracker

    def test_initialization(self, tracker):
        """Test tracker initialization"""
        metrics = tracker.get_metrics()
        
        assert metrics["queries_total"] == 0
        assert metrics["queries_successful"] == 0
        assert metrics["queries_failed"] == 0
        assert metrics["documents_processed"] == 0
        assert metrics["chunks_indexed"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 0
        assert metrics["embedding_requests"] == 0
        assert metrics["vector_searches"] == 0

    def test_increment_metric(self, tracker):
        """Test incrementing a metric"""
        tracker.increment("queries_total")
        tracker.increment("queries_total", 2)
        
        metrics = tracker.get_metrics()
        assert metrics["queries_total"] == 3

    def test_increment_multiple_metrics(self, tracker):
        """Test incrementing multiple metrics"""
        tracker.increment("queries_total", 5)
        tracker.increment("queries_successful", 4)
        tracker.increment("queries_failed", 1)
        tracker.increment("chunks_indexed", 20)
        
        metrics = tracker.get_metrics()
        assert metrics["queries_total"] == 5
        assert metrics["queries_successful"] == 4
        assert metrics["queries_failed"] == 1
        assert metrics["chunks_indexed"] == 20

    def test_increment_invalid_metric(self, tracker):
        """Test incrementing invalid metric"""
        with pytest.raises(ValueError, match="Unknown metric"):
            tracker.increment("invalid_metric")

    def test_track_error(self, tracker):
        """Test tracking errors"""
        tracker.track_error("RetrievalException")
        tracker.track_error("RetrievalException")
        tracker.track_error("EmbeddingException")
        
        metrics = tracker.get_metrics()
        assert metrics["errors"]["RetrievalException"] == 2
        assert metrics["errors"]["EmbeddingException"] == 1
        assert metrics["total_errors"] == 3

    def test_success_rate_calculation(self, tracker):
        """Test success rate calculation"""
        tracker.increment("queries_total", 10)
        tracker.increment("queries_successful", 8)
        tracker.increment("queries_failed", 2)
        
        metrics = tracker.get_metrics()
        assert metrics["success_rate"] == 0.8

    def test_success_rate_no_queries(self, tracker):
        """Test success rate with no queries"""
        metrics = tracker.get_metrics()
        assert metrics["success_rate"] == 0.0

    def test_cache_hit_rate_calculation(self, tracker):
        """Test cache hit rate calculation"""
        tracker.increment("cache_hits", 80)
        tracker.increment("cache_misses", 20)
        
        metrics = tracker.get_metrics()
        assert metrics["cache_hit_rate"] == 0.8

    def test_cache_hit_rate_no_cache_activity(self, tracker):
        """Test cache hit rate with no activity"""
        metrics = tracker.get_metrics()
        assert metrics["cache_hit_rate"] == 0.0

    def test_reset(self, tracker):
        """Test resetting metrics"""
        tracker.increment("queries_total", 10)
        tracker.increment("cache_hits", 5)
        tracker.track_error("TestError")
        
        tracker.reset()
        
        metrics = tracker.get_metrics()
        assert metrics["queries_total"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["total_errors"] == 0

    def test_get_metrics_returns_dict(self, tracker):
        """Test that get_metrics returns dictionary"""
        metrics = tracker.get_metrics()
        assert isinstance(metrics, dict)
        assert "queries_total" in metrics
        assert "success_rate" in metrics
        assert "cache_hit_rate" in metrics
        assert "total_errors" in metrics


class TestGlobalMetrics:
    """Test cases for global metrics instance"""

    def test_global_metrics_instance(self):
        """Test that global metrics instance exists"""
        assert metrics is not None
        assert isinstance(metrics, MetricsTracker)

    def test_global_metrics_operations(self):
        """Test operations on global metrics"""
        initial = metrics.get_metrics()
        initial_queries = initial["queries_total"]
        
        metrics.increment("queries_total")
        
        updated = metrics.get_metrics()
        assert updated["queries_total"] == initial_queries + 1
        
        # Reset for other tests
        metrics.reset()
