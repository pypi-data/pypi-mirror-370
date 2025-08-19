import argparse
import asyncio
from unittest.mock import MagicMock, patch

import pytest

from rust_crate_pipeline.main import (
    build_pipeline_config,
    main_async,
    parse_arguments,
    run_sigil_pipeline,
    run_standard_pipeline,
    setup_environment,
)


@pytest.mark.asyncio
@patch("rust_crate_pipeline.main.enforce_rule_zero_reinforcement")
@patch("rust_crate_pipeline.main.setup_environment")
@patch("rust_crate_pipeline.main.build_pipeline_config")
@patch("rust_crate_pipeline.main.run_standard_pipeline")
@patch("rust_crate_pipeline.main.run_sigil_pipeline")
async def test_main_standard_pipeline(
    mock_run_sigil_pipeline: MagicMock,
    mock_run_standard_pipeline: MagicMock,
    mock_build_pipeline_config: MagicMock,
    mock_setup_environment: MagicMock,
    mock_enforce_rule_zero: MagicMock,
):
    """Test the main function with the standard pipeline."""
    args = argparse.Namespace(
        enable_sigil_protocol=False,
        output_dir=None,
        limit=None,
        crates=None,
        skip_ai=False,
        skip_source_analysis=False,
    )
    mock_setup_environment.return_value = (args, {})
    mock_run_standard_pipeline.return_value = asyncio.sleep(0)

    await main_async()

    mock_enforce_rule_zero.assert_called_once()
    mock_setup_environment.assert_called_once()
    mock_build_pipeline_config.assert_called_once()
    mock_run_standard_pipeline.assert_called_once()
    mock_run_sigil_pipeline.assert_not_called()


@pytest.mark.asyncio
@patch("rust_crate_pipeline.main.enforce_rule_zero_reinforcement")
@patch("rust_crate_pipeline.main.setup_environment")
@patch("rust_crate_pipeline.main.build_pipeline_config")
@patch("rust_crate_pipeline.main.run_standard_pipeline")
@patch("rust_crate_pipeline.main.run_sigil_pipeline")
async def test_main_sigil_pipeline(
    mock_run_sigil_pipeline: MagicMock,
    mock_run_standard_pipeline: MagicMock,
    mock_build_pipeline_config: MagicMock,
    mock_setup_environment: MagicMock,
    mock_enforce_rule_zero: MagicMock,
):
    """Test the main function with the Sigil Protocol pipeline."""
    args = argparse.Namespace(
        enable_sigil_protocol=True,
        output_dir=None,
        limit=None,
        crates=None,
        skip_ai=False,
        skip_source_analysis=False,
    )
    mock_setup_environment.return_value = (args, {})
    mock_run_sigil_pipeline.return_value = asyncio.sleep(0)

    await main_async()

    mock_enforce_rule_zero.assert_called_once()
    mock_setup_environment.assert_called_once()
    mock_build_pipeline_config.assert_called_once()
    mock_run_standard_pipeline.assert_not_called()
    mock_run_sigil_pipeline.assert_called_once()


def test_parse_arguments():
    """Test that argument parsing works as expected."""
    with patch("sys.argv", ["test_main.py", "--limit", "10"]):
        args = parse_arguments()
        assert args.limit == 10
