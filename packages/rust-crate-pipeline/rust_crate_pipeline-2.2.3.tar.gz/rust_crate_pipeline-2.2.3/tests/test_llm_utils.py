import pytest
from rust_crate_pipeline.llm_utils import (
    estimate_tokens_simple,
    truncate_content_simple,
    smart_truncate_content,
    clean_llm_output,
    validate_classification_result,
    validate_factual_pairs,
    simplify_prompt,
    validate_and_retry_llm_call,
)


class TestLLMUtils:
    """Test llm_utils module."""

    def test_estimate_tokens_simple(self):
        """Test estimate_tokens_simple function."""
        assert estimate_tokens_simple("hello world") == 2

    def test_truncate_content_simple(self):
        """Test truncate_content_simple function."""
        content = "a" * 4000
        truncated = truncate_content_simple(content, max_tokens=500)
        assert len(truncated) < len(content)

    def test_smart_truncate_content(self):
        """Test smart_truncate_content function."""
        content = "# Intro\n" + "a" * 4000
        truncated = smart_truncate_content(content, max_tokens=500)
        assert len(truncated) < len(content)

    def test_clean_llm_output(self):
        """Test clean_llm_output function."""
        assert clean_llm_output("  hello world  ") == "hello world"

    def test_validate_classification_result(self):
        """Test validate_classification_result function."""
        assert validate_classification_result("AI")
        assert not validate_classification_result("invalid")

    def test_validate_factual_pairs(self):
        """Test validate_factual_pairs function."""
        assert validate_factual_pairs("✅ Factual: a\n❌ Counterfactual: b")
        assert not validate_factual_pairs("invalid")

    def test_simplify_prompt(self):
        """Test simplify_prompt function."""
        prompt = "  Please be extremely detailed  "
        simplified = simplify_prompt(prompt)
        assert "Please be extremely detailed" not in simplified

    def test_validate_and_retry_llm_call(self):
        """Test validate_and_retry_llm_call function."""

        def mock_llm_call_success(prompt):
            return "AI"

        def mock_llm_call_fail(prompt):
            return "invalid"

        def validation_func(result):
            return result == "AI"

        result = validate_and_retry_llm_call(mock_llm_call_success, validation_func, 1, "prompt")
        assert result == "AI"

        result = validate_and_retry_llm_call(mock_llm_call_fail, validation_func, 1, "prompt")
        assert result is None
