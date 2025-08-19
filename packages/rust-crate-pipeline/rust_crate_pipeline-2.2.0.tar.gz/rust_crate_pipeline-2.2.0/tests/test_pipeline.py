import pytest
from unittest.mock import Mock, patch, AsyncMock
from rust_crate_pipeline.pipeline import CrateDataPipeline, PipelineConfig
from rust_crate_pipeline.config import CrateMetadata, EnrichedCrate


@pytest.fixture
def mock_pipeline_config():
    """Provides a mock PipelineConfig object for testing."""
    config = Mock(spec=PipelineConfig)
    config.output_path = "test_output"
    config.enable_crawl4ai = False
    return config


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


class TestCrateDataPipeline:
    """Test CrateDataPipeline class."""

    @patch("rust_crate_pipeline.pipeline.CrateAPIClient")
    @patch("rust_crate_pipeline.pipeline.GitHubBatchClient")
    @patch("rust_crate_pipeline.pipeline.LLMEnricher")
    @patch("rust_crate_pipeline.pipeline.CrateAnalyzer")
    def test_initialization(
        self,
        mock_crate_analyzer,
        mock_llm_enricher,
        mock_github_batch_client,
        mock_crate_api_client,
        mock_pipeline_config,
    ):
        """Test CrateDataPipeline initialization."""
        pipeline = CrateDataPipeline(mock_pipeline_config)
        assert pipeline.config == mock_pipeline_config

    @pytest.mark.asyncio
    @patch("rust_crate_pipeline.pipeline.CrateAPIClient")
    @patch("rust_crate_pipeline.pipeline.GitHubBatchClient")
    @patch("rust_crate_pipeline.pipeline.LLMEnricher")
    @patch("rust_crate_pipeline.pipeline.CrateAnalyzer")
    async def test_fetch_metadata_batch(
        self,
        mock_crate_analyzer,
        mock_llm_enricher,
        mock_github_batch_client,
        mock_crate_api_client,
        mock_pipeline_config,
        sample_crate_metadata,
    ):
        """Test fetch_metadata_batch method."""
        mock_api_client_instance = mock_crate_api_client.return_value
        mock_api_client_instance.fetch_crate_metadata = Mock(return_value=sample_crate_metadata.__dict__)
        pipeline = CrateDataPipeline(mock_pipeline_config)
        results = await pipeline.fetch_metadata_batch(["test-crate"])
        assert len(results) == 1
        assert results[0].name == "test-crate"

    @pytest.mark.asyncio
    @patch("rust_crate_pipeline.pipeline.CrateAPIClient")
    @patch("rust_crate_pipeline.pipeline.GitHubBatchClient")
    @patch("rust_crate_pipeline.pipeline.LLMEnricher")
    @patch("rust_crate_pipeline.pipeline.CrateAnalyzer")
    async def test_enrich_batch(
        self,
        mock_crate_analyzer,
        mock_llm_enricher,
        mock_github_batch_client,
        mock_crate_api_client,
        mock_pipeline_config,
        sample_crate_metadata,
    ):
        """Test enrich_batch method."""
        mock_llm_enricher_instance = mock_llm_enricher.return_value
        mock_llm_enricher_instance.enrich_crate.return_value = EnrichedCrate(**sample_crate_metadata.__dict__)
        pipeline = CrateDataPipeline(mock_pipeline_config)
        results = await pipeline.enrich_batch([sample_crate_metadata])
        assert len(results) == 1
        assert results[0].name == "test-crate"
