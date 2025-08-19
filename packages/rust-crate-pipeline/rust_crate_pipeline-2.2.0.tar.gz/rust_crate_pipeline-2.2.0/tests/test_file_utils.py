import pytest
from unittest.mock import mock_open, patch
from rust_crate_pipeline.utils.file_utils import (
    create_output_dir,
    save_checkpoint,
    safe_file_cleanup,
    disk_space_check,
    load_rule_zero_typing_quick_lookup,
)
import os


class TestFileUtils:
    """Test file_utils module."""

    def test_create_output_dir(self, tmpdir):
        """Test create_output_dir function."""
        output_dir = create_output_dir(base_name=str(tmpdir.join("test")))
        assert os.path.exists(output_dir)

    def test_save_checkpoint(self, tmpdir):
        """Test save_checkpoint function."""
        output_dir = str(tmpdir.mkdir("output"))
        checkpoint_file = save_checkpoint([{"key": "value"}], "test", output_dir)
        assert os.path.exists(checkpoint_file)

    def test_safe_file_cleanup(self, tmpdir):
        """Test safe_file_cleanup function."""
        p = tmpdir.join("test_file.txt")
        p.write("test content")
        safe_file_cleanup(str(p))
        assert not os.path.exists(str(p))

    def test_disk_space_check(self):
        """Test disk_space_check function."""
        assert disk_space_check()

    def test_load_rule_zero_typing_quick_lookup(self):
        """Test load_rule_zero_typing_quick_lookup function."""
        with patch("builtins.open", mock_open(read_data='{"key": "value"}')) as mock_file:
            data = load_rule_zero_typing_quick_lookup("dummy_path")
            assert data == {"key": "value"}
