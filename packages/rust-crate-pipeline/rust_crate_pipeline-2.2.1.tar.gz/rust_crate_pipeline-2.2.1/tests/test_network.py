import pytest
from unittest.mock import Mock, patch
from rust_crate_pipeline.network import GitHubBatchClient, CrateAPIClient
from rust_crate_pipeline.config import PipelineConfig
import requests


@pytest.fixture
def mock_pipeline_config():
    """Provides a mock PipelineConfig object for testing."""
    config = Mock(spec=PipelineConfig)
    config.github_token = "test_token"
    config.max_retries = 1
    return config


class TestGitHubBatchClient:
    """Test GitHubBatchClient class."""

    def test_initialization(self, mock_pipeline_config):
        """Test GitHubBatchClient initialization."""
        client = GitHubBatchClient(mock_pipeline_config)
        assert client.config == mock_pipeline_config

    @patch("requests.Session.get")
    def test_check_rate_limit(self, mock_get, mock_pipeline_config):
        """Test check_rate_limit method."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"resources": {"core": {"remaining": 4999, "reset": 0}}}
        mock_get.return_value = mock_response

        client = GitHubBatchClient(mock_pipeline_config)
        client.check_rate_limit()
        assert client.remaining_calls == 4999

    @patch("requests.Session.get")
    def test_get_repo_stats(self, mock_get, mock_pipeline_config):
        """Test get_repo_stats method."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"stargazers_count": 100}
        mock_get.return_value = mock_response

        client = GitHubBatchClient(mock_pipeline_config)
        stats = client.get_repo_stats("owner", "repo")
        assert stats["stargazers_count"] == 100


class TestCrateAPIClient:
    """Test CrateAPIClient class."""

    def test_initialization(self, mock_pipeline_config):
        """Test CrateAPIClient initialization."""
        client = CrateAPIClient(mock_pipeline_config)
        assert client.config == mock_pipeline_config

    @patch("requests.Session.get")
    def test_fetch_crate_metadata(self, mock_get, mock_pipeline_config):
        """Test fetch_crate_metadata method."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "crate": {"newest_version": "1.0.0", "repository": ""},
            "dependencies": [],
        }
        mock_get.return_value = mock_response

        client = CrateAPIClient(mock_pipeline_config)
        metadata = client.fetch_crate_metadata("test-crate")
        assert metadata is not None
        assert metadata["name"] == "test-crate"
