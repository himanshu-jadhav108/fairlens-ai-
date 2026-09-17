"""
Unit tests for LLM Providers and Explanation Generation.
Verifies MockLLMProvider modes, GeminiProvider with mocked API calls,
missing API key error handling, and complete provenance tracking.
"""
import pytest
from unittest.mock import MagicMock, patch
from research.llm.schemas import LLMGenerationConfig, LLMResponse
from research.llm.providers.mock import MockLLMProvider
from research.llm.providers.gemini import GeminiProvider
from research.llm.providers import get_llm_provider
from research.llm.generator import ExplanationGenerator
from research.evidence.schemas import (
    AuditEvidence, AuditStateEvidence, DatasetEvidence, ModelEvidence, ObservedMetric, MetricType
)


def test_mock_llm_provider_modes():
    p_faithful = MockLLMProvider(mode="faithful")
    resp_f = p_faithful.generate("Prompt test")
    assert resp_f.provider_name == "mock"
    assert "demographic parity difference" in resp_f.raw_text.lower()

    p_num_err = MockLLMProvider(mode="numerical_error")
    resp_num = p_num_err.generate("Prompt test")
    assert "0.9999" in resp_num.raw_text

    p_custom = MockLLMProvider(mode="custom", custom_response="Custom test explanation")
    resp_c = p_custom.generate("Prompt")
    assert resp_c.raw_text == "Custom test explanation"


def test_gemini_missing_api_key():
    # When GEMINI_API_KEY is not provided or in env, must raise ValueError
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
            GeminiProvider(api_key=None)


def test_gemini_mocked_api_response():
    # Mock genai to simulate Gemini API response without network call
    fake_response = MagicMock()
    fake_response.text = "This is a faithful mock Gemini fairness audit explanation."
    fake_candidate = MagicMock()
    fake_candidate.finish_reason = "STOP"
    fake_response.candidates = [fake_candidate]
    fake_response.usage_metadata.prompt_token_count = 120
    fake_response.usage_metadata.candidates_token_count = 60

    with patch("research.llm.providers.gemini.genai") as mock_genai:
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = fake_response
        mock_genai.GenerativeModel.return_value = mock_model_instance

        provider = GeminiProvider(api_key="fake-test-key-12345")
        config = LLMGenerationConfig(model_name="gemini-2.5-flash", temperature=0.2)
        response = provider.generate("Test prompt content", config=config)

        assert response.provider_name == "gemini"
        assert response.model_name == "gemini-2.5-flash"
        assert response.raw_text == "This is a faithful mock Gemini fairness audit explanation."
        assert response.prompt_tokens == 120
        assert response.completion_tokens == 60
        assert response.finish_reason == "STOP"


def test_gemini_api_failure():
    with patch("research.llm.providers.gemini.genai") as mock_genai:
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = RuntimeError("Quota exceeded")
        mock_genai.GenerativeModel.return_value = mock_model_instance

        provider = GeminiProvider(api_key="fake-test-key-12345")
        with pytest.raises(RuntimeError, match="Gemini API generation failed"):
            provider.generate("Test prompt")


def test_explanation_generator_provenance(tmp_path):
    dataset = DatasetEvidence("adult", "sex", 1, 0, "income", 100, 20, 30)
    model = ModelEvidence("logistic_regression", {}, 42)
    base_state = AuditStateEvidence("baseline", {}, {})
    evidence = AuditEvidence("exp_prov_001", dataset, model, base_state)

    provider = MockLLMProvider(mode="faithful")
    generator = ExplanationGenerator(provider=provider)

    record = generator.generate_explanation(
        evidence=evidence,
        prompt_id="combined_audit_v1",
        output_dir=str(tmp_path)
    )

    assert record.experiment_id == "exp_prov_001"
    assert record.llm_provider == "mock"
    assert record.prompt_id == "combined_audit_v1"
    assert len(record.input_evidence_hash) == 64
    assert record.git_commit_hash is not None
    assert record.timestamp_utc is not None
