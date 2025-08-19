import pytest
from unittest.mock import Mock, patch, mock_open
from rust_crate_pipeline.config_loader import ConfigLoader
import os


@pytest.fixture
def mock_config_file():
    """Provides a mock config file for testing."""
    config_content = '{"llm_config": {"model_path": "test_path"}}'
    with patch("builtins.open", mock_open(read_data=config_content)):
        yield


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_initialization(self, mock_config_file):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()
        assert loader._config is not None

    def test_get_config(self, mock_config_file):
        """Test get method."""
        loader = ConfigLoader()
        model_path = loader.get("llm_config.model_path")
        assert model_path == "test_path"

    def test_get_llm_config(self, mock_config_file):
        """Test get_llm_config method."""
        loader = ConfigLoader()
        llm_config = loader.get_llm_config()
        assert "model_path" in llm_config
        assert llm_config["model_path"] == "test_path"

    def test_update_and_save_config(self, tmpdir):
        """Test update and save methods."""
        config_path = str(tmpdir.join("test_config.json"))
        loader = ConfigLoader(config_path=config_path)
        loader.update("llm_config.model_path", "new_path")
        loader.save()
        assert os.path.exists(config_path)
        with open(config_path, "r") as f:
            assert "new_path" in f.read()
