import pytest
from unittest.mock import Mock, patch, AsyncMock
from rust_crate_pipeline.unified_pipeline import (
    UnifiedSigilPipeline,
    PipelineConfig,
    LLMConfig,
)
from rust_crate_pipeline.config import CrateMetadata
from rust_crate_pipeline.core.sacred_chain import SacredChainTrace, TrustVerdict


@pytest.fixture
def sample_crate_metadata():
    """Provides a sample CrateMetadata object for testing."""
    return CrateMetadata(
        name="test-crate",
        version="1.0.0",
        description="A test crate for testing.",
        repository="https://github.com/test/test-crate",
        keywords=["test", "testing"],
        categories=["testing"],
        readme="This is a test README.",
        downloads=100,
        github_stars=10,
        dependencies=[],
        features={},
        code_snippets=[],
        readme_sections={},
        librs_downloads=None,
        source="crates.io",
    )


@pytest.fixture
def mock_pipeline_config():
    """Provides a mock PipelineConfig object for testing."""
    return Mock(spec=PipelineConfig)


@pytest.fixture
def mock_llm_config():
    """Provides a mock LLMConfig object for testing."""
    return Mock(spec=LLMConfig)


@pytest.mark.asyncio
@patch("rust_crate_pipeline.unified_pipeline.IRLEngine")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedScraper")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedLLMProcessor")
async def test_unified_sigil_pipeline_initialization(
    mock_llm_processor, mock_scraper, mock_irl_engine, mock_pipeline_config, mock_llm_config
):
    """Tests that the UnifiedSigilPipeline class initializes correctly."""
    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)
    assert pipeline.config == mock_pipeline_config
    assert pipeline.llm_config == mock_llm_config
    assert pipeline.irl_engine is not None
    assert pipeline.scraper is not None
    assert pipeline.unified_llm_processor is not None


@pytest.mark.asyncio
@patch("rust_crate_pipeline.unified_pipeline.IRLEngine")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedScraper")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedLLMProcessor")
async def test_analyze_crate(
    mock_llm_processor,
    mock_scraper,
    mock_irl_engine,
    mock_pipeline_config,
    mock_llm_config,
):
    """Tests the analyze_crate method."""
    mock_scraper_instance = mock_scraper.return_value
    mock_scraper_instance.scrape_crate_documentation = AsyncMock(return_value={})
    mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
    mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)

    mock_irl_engine_instance = mock_irl_engine.return_value
    mock_irl_engine_instance.analyze_with_sacred_chain = AsyncMock(
        return_value=SacredChainTrace(
            input_data="test-crate",
            context_sources=[],
            reasoning_steps=[],
            suggestion="",
            verdict=TrustVerdict.DEFER,
            audit_info={},
            irl_score=0.0,
            execution_id="",
            timestamp="",
            canon_version="",
        )
    )
    mock_irl_engine_instance.__aenter__ = AsyncMock(return_value=mock_irl_engine_instance)
    mock_irl_engine_instance.__aexit__ = AsyncMock(return_value=None)

    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)
    async with pipeline:
        pipeline._get_latest_crate_version = AsyncMock(return_value="1.0.0")
        pipeline._add_crate_analysis_results = AsyncMock()
        trace = await pipeline.analyze_crate("test-crate")

    assert isinstance(trace, SacredChainTrace)
    assert trace.input_data == "test-crate"
