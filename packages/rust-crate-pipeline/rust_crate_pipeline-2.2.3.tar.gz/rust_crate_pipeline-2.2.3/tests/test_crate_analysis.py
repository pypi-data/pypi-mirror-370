import pytest
from unittest.mock import Mock, patch
from rust_crate_pipeline.crate_analysis import CrateAnalyzer
import os


@pytest.fixture
def crate_analyzer(tmpdir):
    """Provides a CrateAnalyzer instance for the tests."""
    return CrateAnalyzer(str(tmpdir))


class TestCrateAnalyzer:
    """Test CrateAnalyzer class."""

    def test_initialization(self, crate_analyzer):
        """Test CrateAnalyzer initialization."""
        assert crate_analyzer.crate_source_path is not None

    @patch("subprocess.run")
    def test_run_cargo_cmd(self, mock_run, crate_analyzer):
        """Test run_cargo_cmd method."""
        mock_run.return_value = Mock(stdout='{"reason": "compiler-message"}', stderr="", returncode=0)
        result = crate_analyzer.run_cargo_cmd(["test", "command"])
        assert "cmd" in result
        assert "returncode" in result
        assert "stdout" in result
        assert "stderr" in result

    @patch("rust_crate_pipeline.crate_analysis.CrateAnalyzer.run_cargo_cmd")
    def test_analyze(self, mock_run_cargo_cmd, crate_analyzer):
        """Test analyze method."""
        mock_run_cargo_cmd.return_value = {}
        results = crate_analyzer.analyze()
        assert "build" in results
        assert "test" in results
        assert "clippy" in results
        assert "fmt" in results
        assert "audit" in results
        assert "tree" in results
        assert "doc" in results
