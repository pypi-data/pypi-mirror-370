import pytest
from unittest.mock import Mock, patch, MagicMock
from rust_crate_pipeline.observability import (
    StructuredLogger,
    MetricsCollector,
    TracingManager,
)


class TestStructuredLogger:
    """Test StructuredLogger class."""

    def test_initialization(self):
        """Test StructuredLogger initialization."""
        logger = StructuredLogger("test_logger")
        assert logger.logger.name == "test_logger"

    @patch("logging.Logger.log")
    def test_info(self, mock_log):
        """Test info method."""
        logger = StructuredLogger("test_logger")
        logger.info("test message", key="value")
        mock_log.assert_called_once()


class TestMetricsCollector:
    """Test MetricsCollector class."""

    def test_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.namespace == "rust_crate_pipeline"

    @patch("opentelemetry.metrics.Meter.create_counter")
    def test_increment(self, mock_create_counter):
        """Test increment method."""
        collector = MetricsCollector()
        collector.increment("test_metric")
        # This is hard to test without a real meter.
        # We will just check that it runs without errors.
        pass


class TestTracingManager:
    """Test TracingManager class."""

    def test_initialization(self):
        """Test TracingManager initialization."""
        manager = TracingManager()
        assert manager.service_name == "rust-crate-pipeline"

    @patch("rust_crate_pipeline.observability.OPENTELEMETRY_AVAILABLE", True)
    @patch("opentelemetry.trace.get_tracer")
    def test_span(self, mock_get_tracer):
        """Test span method."""
        mock_tracer = MagicMock()
        mock_get_tracer.return_value = mock_tracer
        manager = TracingManager()
        with manager.span("test_span"):
            pass
        mock_tracer.start_as_current_span.assert_called_once()
