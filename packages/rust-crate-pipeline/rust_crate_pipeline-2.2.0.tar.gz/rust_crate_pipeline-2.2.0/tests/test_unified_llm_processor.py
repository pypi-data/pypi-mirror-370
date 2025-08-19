import pytest
from unittest.mock import patch
from rust_crate_pipeline.llm_client import LLMConfig, LLMClient
from rust_crate_pipeline.llm_factory import (
    create_ollama_client,
    create_llama_cpp_client,
    create_azure_client,
    create_openai_client,
    create_litellm_client,
)
from rust_crate_pipeline.ai_processing import LLMEnricher
from rust_crate_pipeline.config import CrateMetadata, EnrichedCrate, PipelineConfig


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
def mock_llm_config():
    """Provides a mock LLMConfig object for testing."""
    return LLMConfig(
        provider="ollama",
        model="test-model",
        api_base="http://localhost:11434",
        api_key="ollama",
        request_timeout=30.0,
        max_retries=3,
    )


@pytest.fixture
def mock_pipeline_config():
    """Provides a mock PipelineConfig object for testing."""
    return PipelineConfig(
        use_azure_openai=False,
        batch_size=4,
        llm_max_retries=3,
    )


class TestLLMClient:
    """Test the new unified LLM client system."""

    @pytest.mark.asyncio
    async def test_llm_client_initialization(self, mock_llm_config):
        """Test that LLMClient initializes correctly."""
        client = LLMClient(mock_llm_config)
        assert client.cfg == mock_llm_config
        assert client.cfg.provider == "ollama"
        assert client.cfg.model == "test-model"

    @pytest.mark.asyncio
    async def test_llm_client_chat(self, mock_llm_config):
        """Test the chat method of LLMClient."""
        with patch("rust_crate_pipeline.llm_client.HTTPLLMClient.chat") as mock_chat:
            mock_chat.return_value = {"choices": [{"message": {"content": "Test response"}}]}

            client = LLMClient(mock_llm_config)
            async with client:
                response = await client.chat(messages=[{"role": "user", "content": "Hello"}])

            assert response["choices"][0]["message"]["content"] == "Test response"

    @pytest.mark.asyncio
    async def test_llm_client_chat_json(self, mock_llm_config):
        """Test the chat_json method of LLMClient."""
        with patch("rust_crate_pipeline.llm_client.HTTPLLMClient.chat_json") as mock_chat_json:
            mock_chat_json.return_value = {"result": "test"}

            client = LLMClient(mock_llm_config)
            async with client:
                response = await client.chat_json(
                    messages=[{"role": "user", "content": "Hello"}],
                    schema={"type": "object", "properties": {"result": {"type": "string"}}},
                )

            assert response["result"] == "test"


class TestLLMFactory:
    """Test the LLM factory functions."""

    def test_create_ollama_client(self):
        """Test creating an Ollama client."""
        client = create_ollama_client(
            model="test-model",
            host="http://localhost:11434",
            request_timeout=30.0,
            max_retries=3,
        )
        assert client.cfg.provider == "ollama"
        assert client.cfg.model == "test-model"
        assert client.cfg.api_base == "http://localhost:11434"

    def test_create_llama_cpp_client(self):
        """Test creating a llama-cpp client."""
        client = create_llama_cpp_client(
            model_path="/path/to/model.gguf",
            n_gpu_layers=-1,
            n_ctx=8192,
            request_timeout=30.0,
            max_retries=3,
        )
        assert client.cfg.provider == "llama-cpp"
        assert client.cfg.model_path == "/path/to/model.gguf"
        assert client.cfg.n_gpu_layers == -1

    def test_create_azure_client(self):
        """Test creating an Azure client."""
        client = create_azure_client(
            model="test-deployment",
            api_base="https://test.openai.azure.com",
            api_key="test-key",
            request_timeout=30.0,
            max_retries=3,
        )
        assert client.cfg.provider == "azure"
        assert client.cfg.model == "test-deployment"
        assert client.cfg.api_base == "https://test.openai.azure.com"

    def test_create_openai_client(self):
        """Test creating an OpenAI client."""
        client = create_openai_client(
            model="gpt-4",
            api_key="test-key",
            request_timeout=30.0,
            max_retries=3,
        )
        assert client.cfg.provider == "openai"
        assert client.cfg.model == "gpt-4"
        assert client.cfg.api_key == "test-key"

    def test_create_litellm_client(self):
        """Test creating a LiteLLM client."""
        client = create_litellm_client(
            model="anthropic/claude-3-sonnet",
            api_key="test-key",
            request_timeout=30.0,
            max_retries=3,
        )
        assert client.cfg.provider == "litellm"
        assert client.cfg.model == "anthropic/claude-3-sonnet"
        assert client.cfg.api_key == "test-key"


class TestLLMEnricher:
    """Test the new LLMEnricher with unified client."""

    @pytest.mark.asyncio
    async def test_enricher_initialization(self, mock_pipeline_config):
        """Test that LLMEnricher initializes correctly."""
        enricher = LLMEnricher(mock_pipeline_config)
        assert enricher.config == mock_pipeline_config
        assert hasattr(enricher, "llm_client")

    @pytest.mark.asyncio
    async def test_enrich_crate(self, mock_pipeline_config, sample_crate_metadata):
        """Test the enrich_crate method."""
        with patch("rust_crate_pipeline.ai_processing.LLMEnricher._perform_ai_enrichment") as mock_enrich:
            mock_enrich.return_value = {
                "ai_summary": "Test summary",
                "ai_analysis": "Test analysis",
                "ai_risk_score": 0.5,
            }

            enricher = LLMEnricher(mock_pipeline_config)
            enriched_crate = await enricher.enrich_crate(sample_crate_metadata)

            assert isinstance(enriched_crate, EnrichedCrate)
            assert enriched_crate.name == "test-crate"
            assert enriched_crate.readme_summary == "Test summary"
            assert enriched_crate.use_case == "Test analysis"
            assert enriched_crate.score == 0.5

    @pytest.mark.asyncio
    async def test_enrich_crate_error_handling(self, mock_pipeline_config, sample_crate_metadata):
        """Test error handling in enrich_crate method."""
        with patch("rust_crate_pipeline.ai_processing.LLMEnricher._perform_ai_enrichment") as mock_enrich:
            mock_enrich.side_effect = Exception("LLM error")

            enricher = LLMEnricher(mock_pipeline_config)
            enriched_crate = await enricher.enrich_crate(sample_crate_metadata)

            # Should return a fallback enriched crate
            assert isinstance(enriched_crate, EnrichedCrate)
            assert enriched_crate.name == "test-crate"
            assert "error" in enriched_crate.readme_summary.lower()


class TestProviderRouting:
    """Test that the LLMClient correctly routes to different providers."""

    def test_ollama_routing(self):
        """Test routing to Ollama provider."""
        config = LLMConfig(provider="ollama", model="test-model")
        client = LLMClient(config)
        assert client._backend.__class__.__name__ == "HTTPLLMClient"

    def test_llama_cpp_routing(self):
        """Test routing to llama-cpp provider."""
        config = LLMConfig(provider="llama-cpp", model="/path/to/model.gguf")
        client = LLMClient(config)
        assert client._backend.__class__.__name__ == "LlamaCppClient"

    def test_litellm_routing(self):
        """Test routing to LiteLLM provider."""
        config = LLMConfig(provider="litellm", model="test-model")
        client = LLMClient(config)
        assert client._backend.__class__.__name__ == "LiteLLMClient"

    def test_invalid_provider_routing(self):
        """Test that invalid providers raise an error."""
        config = LLMConfig(provider="invalid", model="test-model")
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMClient(config)
