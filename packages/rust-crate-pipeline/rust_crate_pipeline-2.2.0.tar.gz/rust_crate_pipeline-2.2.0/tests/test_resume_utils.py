import pytest
from unittest.mock import mock_open, patch
from rust_crate_pipeline.utils.resume_utils import (
    get_processed_crates,
    load_crate_list,
    get_remaining_crates,
    _is_problematic_crate,
    validate_resume_state,
    create_resume_report,
)
import os


class TestResumeUtils:
    """Test resume_utils module."""

    def test_get_processed_crates(self, tmpdir):
        """Test get_processed_crates function."""
        output_dir = str(tmpdir.mkdir("output"))
        p = tmpdir.join("output").join("test-crate_enriched.json")
        p.write("content")
        processed = get_processed_crates(output_dir=output_dir)
        assert "test-crate" in processed

    def test_load_crate_list(self):
        """Test load_crate_list function."""
        with patch("builtins.open", mock_open(read_data="test-crate\n#comment")):
            crates = load_crate_list()
            assert "test-crate" in crates
            assert "#comment" not in crates

    def test_get_remaining_crates(self, tmpdir):
        """Test get_remaining_crates function."""
        output_dir = str(tmpdir.mkdir("output"))
        p = tmpdir.join("output").join("test-crate_enriched.json")
        p.write("content")
        with patch("builtins.open", mock_open(read_data="test-crate\nanother-crate")) as mock_file:
            remaining, total, processed = get_remaining_crates(output_dir=output_dir)
            assert "another-crate" in remaining
            assert "test-crate" not in remaining

    def test_is_problematic_crate(self):
        """Test _is_problematic_crate function."""
        assert _is_problematic_crate("syn")
        assert not _is_problematic_crate("test-crate")

    def test_validate_resume_state(self, tmpdir):
        """Test validate_resume_state function."""
        output_dir = str(tmpdir.mkdir("output"))
        assert validate_resume_state([], 0, 0, output_dir=output_dir)

    def test_create_resume_report(self):
        """Test create_resume_report function."""
        report = create_resume_report([], 10, 5)
        assert "50.0%" in report
