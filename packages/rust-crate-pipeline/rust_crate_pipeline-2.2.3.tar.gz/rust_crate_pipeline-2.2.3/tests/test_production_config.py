import pytest
from unittest.mock import patch
from rust_crate_pipeline.production_config import (
    get_production_config,
    is_production,
    setup_production_environment,
)


class TestProductionConfig:
    """Test production_config module."""

    def test_get_production_config(self):
        """Test get_production_config function."""
        config = get_production_config()
        assert "max_retries" in config

    def test_is_production(self):
        """Test is_production function."""
        with patch.dict("os.environ", {"PRODUCTION": "true"}):
            assert is_production()
        with patch.dict("os.environ", {"PRODUCTION": "false"}):
            assert not is_production()

    def test_setup_production_environment(self):
        """Test setup_production_environment function."""
        with patch.dict("os.environ", {"PRODUCTION": "true"}):
            config = setup_production_environment()
            assert "max_retries" in config
