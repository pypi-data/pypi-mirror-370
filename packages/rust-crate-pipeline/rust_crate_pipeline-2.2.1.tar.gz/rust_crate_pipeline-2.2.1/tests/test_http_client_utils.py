import pytest
from unittest.mock import Mock, patch
from rust_crate_pipeline.utils.http_client_utils import HTTPClientUtils, MetadataExtractor
import requests
from requests_cache import CachedSession


class TestHTTPClientUtils:
    """Test HTTPClientUtils class."""

    def test_create_cached_session(self):
        """Test create_cached_session method."""
        session = HTTPClientUtils.create_cached_session("test_cache", 3600)
        assert isinstance(session, CachedSession)

    @patch("requests.Session.get")
    def test_fetch_with_retry_success(self, mock_get):
        """Test fetch_with_retry method with a successful request."""
        mock_response = Mock()
        mock_response.ok = True
        mock_get.return_value = mock_response

        session = requests.Session()
        response = HTTPClientUtils.fetch_with_retry(session, "http://test.com")

        assert response is not None
        assert response.ok

    @patch("requests.Session.get")
    def test_fetch_with_retry_failure(self, mock_get):
        """Test fetch_with_retry method with a failed request."""
        mock_response = Mock()
        mock_response.ok = False
        mock_get.return_value = mock_response

        session = requests.Session()
        response = HTTPClientUtils.fetch_with_retry(session, "http://test.com")

        assert response is None

    def test_extract_github_repo_info(self):
        """Test extract_github_repo_info method."""
        owner, repo = HTTPClientUtils.extract_github_repo_info("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_get_github_headers(self):
        """Test get_github_headers method."""
        headers = HTTPClientUtils.get_github_headers("test_token")
        assert "Authorization" in headers
        assert headers["Authorization"] == "token test_token"


class TestMetadataExtractor:
    """Test MetadataExtractor class."""

    def test_extract_code_snippets(self):
        """Test extract_code_snippets method."""
        readme = "```rust\nfn main() {}\n```"
        snippets = MetadataExtractor.extract_code_snippets(readme)
        assert len(snippets) == 1
        assert snippets[0] == "fn main() {}"

    def test_extract_readme_sections(self):
        """Test extract_readme_sections method."""
        readme = "# Intro\nintro text\n# Usage\nusage text"
        sections = MetadataExtractor.extract_readme_sections(readme)
        assert "intro" in sections
        assert "usage" in sections
        assert sections["intro"] == "intro text"
        assert sections["usage"] == "usage text"

    def test_create_empty_metadata(self):
        """Test create_empty_metadata method."""
        metadata = MetadataExtractor.create_empty_metadata()
        assert "name" in metadata
        assert metadata["name"] == ""
