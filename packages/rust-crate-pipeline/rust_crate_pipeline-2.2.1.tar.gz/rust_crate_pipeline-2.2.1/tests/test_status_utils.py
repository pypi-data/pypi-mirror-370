import pytest
from unittest.mock import Mock, patch
from rust_crate_pipeline.utils.status_utils import (
    StatusIndicator,
    ProgressTracker,
    with_retry,
    timed_operation,
    status_report,
    safe_execute,
    platform_info,
)


class TestStatusUtils:
    """Test status_utils module."""

    def test_status_indicator(self):
        """Test StatusIndicator class."""
        indicator = StatusIndicator()
        assert "[OK]" in indicator.success
        assert "[ERROR]" in indicator.error

    def test_progress_tracker(self):
        """Test ProgressTracker class."""
        tracker = ProgressTracker(10)
        tracker.step()
        assert tracker.current_step == 1

    def test_with_retry(self):
        """Test with_retry decorator."""

        @with_retry(max_attempts=2, delay=0.01)
        def flaky_function(should_fail):
            if should_fail:
                raise ValueError("Simulated failure")
            return "Success!"

        assert flaky_function(False) == "Success!"
        with pytest.raises(ValueError):
            flaky_function(True)

    def test_timed_operation(self):
        """Test timed_operation decorator."""

        @timed_operation()
        def timed_func():
            return "Success!"

        assert timed_func() == "Success!"

    def test_status_report(self):
        """Test status_report function."""
        with patch("builtins.print") as mock_print:
            status_report("test_task", True)
            mock_print.assert_called_once()

    def test_safe_execute(self):
        """Test safe_execute function."""

        def success_func():
            return "Success!"

        def fail_func():
            raise ValueError("Simulated failure")

        success, result = safe_execute(success_func)
        assert success
        assert result == "Success!"

        success, result = safe_execute(fail_func)
        assert not success
        assert result is None

    def test_platform_info(self):
        """Test platform_info function."""
        info = platform_info()
        assert "platform" in info
