import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from rust_crate_pipeline.ai_processing import LLMEnricher
from rust_crate_pipeline.config import PipelineConfig, CrateMetadata, EnrichedCrate


class FakeEncoding:
    def __init__(self, name):
        self.name = name

    def encode(self, text, **kwargs):
        return text.split()

    def decode(self, tokens, **kwargs):
        return " ".join(str(i) for i in tokens)


class TestLLMEnricher(unittest.TestCase):
    def setUp(self):
        self.config = PipelineConfig()
        self.config.model_path = "path/to/model"
        self.config.use_azure_openai = False

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    def test_llm_enricher_initialization(self, mock_get_encoding, mock_create_client):
        """Test that LLMEnricher initializes correctly with new unified client."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        self.assertEqual(enricher.config, self.config)
        self.assertIsNotNone(enricher.llm_client)
        mock_create_client.assert_called_once_with(self.config)

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    def test_llm_enricher_azure_config(self, mock_get_encoding, mock_create_client):
        """Test LLMEnricher with Azure configuration."""
        self.config.use_azure_openai = True
        self.config.azure_openai_endpoint = "https://test.openai.azure.com/"
        self.config.azure_openai_api_key = "test_key"
        self.config.azure_openai_deployment_name = "test_deployment"

        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        self.assertTrue(enricher.config.use_azure_openai)
        mock_create_client.assert_called_once_with(self.config)

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    def test_llm_enricher_client_creation_failure(self, mock_get_encoding, mock_create_client):
        """Test LLMEnricher handles client creation failure gracefully."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_create_client.side_effect = Exception("Client creation failed")

        with self.assertRaises(Exception):
            LLMEnricher(self.config)

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    async def test_enrich_crate_success(self, mock_get_encoding, mock_create_client):
        """Test successful crate enrichment with new unified client."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = AsyncMock()
        mock_client.chat.return_value = {"choices": [{"message": {"content": "Test summary"}}]}
        mock_client.chat_json.return_value = {"analysis": "Test analysis", "risk_score": 0.5}
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        # Create sample crate metadata
        crate_metadata = CrateMetadata(
            name="test-crate",
            version="1.0.0",
            description="A test crate",
            repository="https://github.com/test/test-crate",
            keywords=["test"],
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

        enriched_crate = await enricher.enrich_crate(crate_metadata)

        self.assertIsInstance(enriched_crate, EnrichedCrate)
        self.assertEqual(enriched_crate.name, "test-crate")
        self.assertEqual(enriched_crate.readme_summary, "Test summary")
        self.assertEqual(enriched_crate.use_case, "Test analysis")
        self.assertEqual(enriched_crate.score, 0.5)

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    async def test_enrich_crate_llm_error(self, mock_get_encoding, mock_create_client):
        """Test crate enrichment handles LLM errors gracefully."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = AsyncMock()
        mock_client.chat.side_effect = Exception("LLM error")
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        crate_metadata = CrateMetadata(
            name="test-crate",
            version="1.0.0",
            description="A test crate",
            repository="https://github.com/test/test-crate",
            keywords=["test"],
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

        enriched_crate = await enricher.enrich_crate(crate_metadata)

        # Should return a fallback enriched crate
        self.assertIsInstance(enriched_crate, EnrichedCrate)
        self.assertEqual(enriched_crate.name, "test-crate")
        self.assertIn("error", enriched_crate.readme_summary.lower())

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    async def test_perform_ai_enrichment(self, mock_get_encoding, mock_create_client):
        """Test the _perform_ai_enrichment method."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = AsyncMock()
        mock_client.chat.return_value = {"choices": [{"message": {"content": "Test summary"}}]}
        mock_client.chat_json.return_value = {"analysis": "Test analysis", "risk_score": 0.5}
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        crate_metadata = CrateMetadata(
            name="test-crate",
            version="1.0.0",
            description="A test crate",
            repository="https://github.com/test/test-crate",
            keywords=["test"],
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

        result = await enricher._perform_ai_enrichment(crate_metadata)

        self.assertIn("ai_summary", result)
        self.assertIn("ai_analysis", result)
        self.assertIn("ai_risk_score", result)
        self.assertEqual(result["ai_summary"], "Test summary")
        self.assertEqual(result["ai_analysis"], "Test analysis")
        self.assertEqual(result["ai_risk_score"], 0.5)

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    async def test_generate_summary(self, mock_get_encoding, mock_create_client):
        """Test the _generate_summary method."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = AsyncMock()
        mock_client.chat.return_value = {"choices": [{"message": {"content": "Test summary"}}]}
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        crate_metadata = CrateMetadata(
            name="test-crate",
            version="1.0.0",
            description="A test crate",
            repository="https://github.com/test/test-crate",
            keywords=["test"],
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

        summary = await enricher._generate_summary(crate_metadata)

        self.assertEqual(summary, "Test summary")
        mock_client.chat.assert_called_once()

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    async def test_generate_feature_summary(self, mock_get_encoding, mock_create_client):
        """Test the _generate_feature_summary method."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = AsyncMock()
        mock_client.chat.return_value = {"choices": [{"message": {"content": "Test feature summary"}}]}
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        crate_metadata = CrateMetadata(
            name="test-crate",
            version="1.0.0",
            description="A test crate",
            repository="https://github.com/test/test-crate",
            keywords=["test"],
            categories=["testing"],
            readme="This is a test README.",
            downloads=100,
            github_stars=10,
            dependencies=[],
            features={"feature1": ["dep1"], "feature2": ["dep2"]},
            code_snippets=[],
            readme_sections={},
            librs_downloads=None,
            source="crates.io",
        )

        feature_summary = await enricher._generate_feature_summary(crate_metadata)

        self.assertEqual(feature_summary, "Test feature summary")
        mock_client.chat.assert_called_once()

    @patch("rust_crate_pipeline.ai_processing.create_llm_client_from_config")
    @patch("tiktoken.get_encoding")
    async def test_perform_analysis(self, mock_get_encoding, mock_create_client):
        """Test the _perform_analysis method."""
        mock_get_encoding.return_value = FakeEncoding("cl100k_base")
        mock_client = AsyncMock()
        mock_client.chat_json.return_value = {"analysis": "Test analysis", "risk_score": 0.5}
        mock_create_client.return_value = mock_client

        enricher = LLMEnricher(self.config)

        crate_metadata = CrateMetadata(
            name="test-crate",
            version="1.0.0",
            description="A test crate",
            repository="https://github.com/test/test-crate",
            keywords=["test"],
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

        analysis = await enricher._perform_analysis(crate_metadata)

        self.assertEqual(analysis["analysis"], "Test analysis")
        self.assertEqual(analysis["risk_score"], 0.5)
        mock_client.chat_json.assert_called_once()

    def test_truncate_content(self):
        """Test content truncation functionality."""
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_get_encoding.return_value = FakeEncoding("cl100k_base")

            enricher = LLMEnricher(self.config)
            content = "This is a test sentence."
            truncated_content = enricher.truncate_content(content, max_tokens=3)

            # With our fake encoding, this should truncate
            self.assertEqual(truncated_content, "")

    def test_clean_output(self):
        """Test output cleaning functionality."""
        enricher = LLMEnricher(self.config)

        # Test various output cleaning scenarios
        test_cases = [
            ('```json\n{"key": "value"}\n```', '{"key": "value"}'),
            ('```\n{"key": "value"}\n```', '{"key": "value"}'),
            ('{"key": "value"}', '{"key": "value"}'),
            ("Test output", "Test output"),
        ]

        for input_text, expected in test_cases:
            cleaned = enricher.clean_output(input_text)
            self.assertEqual(cleaned, expected)


if __name__ == "__main__":
    unittest.main()
