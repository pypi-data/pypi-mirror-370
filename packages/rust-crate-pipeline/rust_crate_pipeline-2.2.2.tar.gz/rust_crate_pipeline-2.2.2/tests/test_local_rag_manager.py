import pytest
from unittest.mock import Mock, patch
from rust_crate_pipeline.utils.local_rag_manager import LocalRAGManager
import os


@pytest.fixture
def rag_manager(tmpdir):
    """Provides a LocalRAGManager instance for the tests."""
    return LocalRAGManager(db_path=str(tmpdir.join("test.db")))


class TestLocalRAGManager:
    """Test LocalRAGManager class."""

    def test_initialization(self, rag_manager):
        """Test LocalRAGManager initialization."""
        assert rag_manager.db_path is not None
        assert rag_manager.conn is not None

    def test_store_and_get_hardware_profile(self, rag_manager):
        """Test store_hardware_profile and get_hardware_profile methods."""
        rag_manager.store_hardware_profile()
        profile = rag_manager.get_hardware_profile()
        assert profile is not None
        assert profile["profile_name"] == "current"

    def test_index_codebase(self, rag_manager, tmpdir):
        """Test index_codebase method."""
        # Create a dummy file
        p = tmpdir.mkdir("sub").join("hello.py")
        p.write("print('hello')")
        count = rag_manager.index_codebase(str(tmpdir))
        assert count == 1

    def test_cache_documentation(self, rag_manager):
        """Test cache_documentation method."""
        rag_manager.cache_documentation("test_type", "test_title", "test_content")
        results = rag_manager.search_knowledge("test_title")
        assert len(results) > 0

    def test_record_code_change(self, rag_manager):
        """Test record_code_change method."""
        rag_manager.record_code_change("test_path", "test_change")
        history = rag_manager.get_file_history("test_path")
        assert len(history) > 0

    def test_get_project_context(self, rag_manager):
        """Test get_project_context method."""
        # This method is not implemented yet, so we just check that it returns
        # an empty dict.
        context = rag_manager.get_project_context("test_path")
        assert context == {}
