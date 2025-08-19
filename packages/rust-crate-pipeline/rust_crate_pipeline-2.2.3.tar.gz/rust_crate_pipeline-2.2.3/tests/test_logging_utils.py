import pytest
from unittest.mock import patch
from rust_crate_pipeline.utils.logging_utils import (
    configure_logging,
)


class TestLoggingUtils:
    """Test logging_utils module."""

    def test_configure_logging(self, tmpdir):
        """Test configure_logging function."""
        log_dir = str(tmpdir.mkdir("logs"))
        logger = configure_logging(log_dir=log_dir)
        assert logger.name == "root"
