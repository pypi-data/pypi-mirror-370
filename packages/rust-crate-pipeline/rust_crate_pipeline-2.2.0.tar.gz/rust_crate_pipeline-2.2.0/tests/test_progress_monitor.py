import pytest
from unittest.mock import Mock, patch
from rust_crate_pipeline.progress_monitor import ProgressMonitor, PipelineMetrics
import os


@pytest.fixture
def mock_psutil():
    """Provides a mock psutil object for testing."""
    with patch("rust_crate_pipeline.progress_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = Mock(percent=50.0, available=1024)
        mock_psutil.disk_usage.return_value = Mock(percent=50.0, free=1024)
        yield mock_psutil


@pytest.fixture
def progress_monitor(tmpdir):
    """Provides a ProgressMonitor instance for the tests."""
    return ProgressMonitor(total_crates=100, output_dir=str(tmpdir))


class TestProgressMonitor:
    """Test ProgressMonitor class."""

    def test_initialization(self, progress_monitor):
        """Test ProgressMonitor initialization."""
        assert progress_monitor.metrics.total_crates == 100
        assert progress_monitor.metrics.processed_crates == 0

    def test_start_and_complete_crate(self, progress_monitor):
        """Test start_crate and complete_crate methods."""
        progress_monitor.start_crate("test-crate")
        assert progress_monitor.current_crate == "test-crate"
        progress_monitor.complete_crate("test-crate", success=True, processing_time=1.0)
        assert progress_monitor.metrics.processed_crates == 1
        assert progress_monitor.metrics.successful_crates == 1
        assert len(progress_monitor.crate_times) == 1

    def test_skip_crate(self, progress_monitor):
        """Test skip_crate method."""
        progress_monitor.skip_crate("test-crate", reason="testing")
        assert progress_monitor.metrics.skipped_crates == 1
        assert len(progress_monitor.metrics.warnings) == 1

    def test_start_and_complete_batch(self, progress_monitor):
        """Test start_batch and complete_batch methods."""
        progress_monitor.start_batch(1, 10)
        assert progress_monitor.metrics.current_batch == 1
        progress_monitor.complete_batch(1, processing_time=10.0)
        assert len(progress_monitor.batch_times) == 1

    def test_add_error_and_warning(self, progress_monitor):
        """Test add_error and add_warning methods."""
        progress_monitor.add_error("test-crate", "test error")
        assert len(progress_monitor.metrics.errors) == 1
        progress_monitor.add_warning("test-crate", "test warning")
        assert len(progress_monitor.metrics.warnings) == 1

    def test_update_performance_stats(self, progress_monitor, mock_psutil):
        """Test _update_performance_stats method."""
        progress_monitor.complete_crate("test-crate", success=True, processing_time=1.0)
        progress_monitor._update_performance_stats()
        assert "avg_crate_time" in progress_monitor.metrics.performance_stats
        assert "system_cpu_percent" in progress_monitor.metrics.performance_stats

    def test_save_status(self, progress_monitor):
        """Test _save_status method."""
        progress_monitor._save_status()
        assert os.path.exists(progress_monitor.status_file)
