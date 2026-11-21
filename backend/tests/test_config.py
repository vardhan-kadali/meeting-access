import json
import pytest
from pydantic import ValidationError
from app.config import Settings


def test_fallback_models_json_array_config(monkeypatch):
    """Test GEMINI_FALLBACK_MODELS configured as a standard JSON array string."""
    models = ["gemini-3.1-flash-lite", "gemini-2.5-flash"]
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", json.dumps(models))
    s = Settings()
    assert s.GEMINI_FALLBACK_MODELS == models
    assert s.model_chain == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash"]


def test_fallback_models_comma_separated_config(monkeypatch):
    """Test GEMINI_FALLBACK_MODELS configured as a comma-separated string."""
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", "gemini-3.1-flash-lite, gemini-2.5-flash")
    s = Settings()
    assert s.GEMINI_FALLBACK_MODELS == ["gemini-3.1-flash-lite", "gemini-2.5-flash"]
    assert s.model_chain == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash"]


def test_fallback_models_empty_and_null_config(monkeypatch):
    """Test GEMINI_FALLBACK_MODELS with empty strings, null, none, and empty brackets."""
    for empty_val in ["", "   ", "none", "null", "[]", "false"]:
        monkeypatch.setenv("GEMINI_FALLBACK_MODELS", empty_val)
        s = Settings()
        assert s.GEMINI_FALLBACK_MODELS == [], f"Failed on empty value: '{empty_val}'"
        assert s.model_chain == ["gemini-3.5-flash-lite"]


def test_fallback_models_deduplication(monkeypatch):
    """Duplicate models within the fallback list must be removed, preserving first occurrence."""
    monkeypatch.setenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.1-flash-lite, gemini-2.5-flash, gemini-3.1-flash-lite, gemini-2.5-flash"
    )
    s = Settings()
    assert s.GEMINI_FALLBACK_MODELS == ["gemini-3.1-flash-lite", "gemini-2.5-flash"]


def test_fallback_models_ignore_empty_entries(monkeypatch):
    """Whitespace-only and empty comma segments must be discarded."""
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", "gemini-3.1-flash-lite, , , gemini-2.5-flash, ")
    s = Settings()
    assert s.GEMINI_FALLBACK_MODELS == ["gemini-3.1-flash-lite", "gemini-2.5-flash"]


def test_primary_and_fallback_deduplication_in_model_chain(monkeypatch):
    """If primary model is accidentally included in fallback models, it must not be duplicated in model_chain."""
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", "gemini-3.5-flash-lite, gemini-3.1-flash-lite")
    s = Settings()
    assert s.model_chain == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]


def test_invalid_json_fallback_configuration_fails_clearly(monkeypatch):
    """Malformed JSON starting with [ or { must fail with a clear ValidationError."""
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", '["gemini-3.5-flash-lite",')
    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "Invalid JSON in GEMINI_FALLBACK_MODELS" in str(excinfo.value)


def test_json_non_list_fallback_configuration_fails(monkeypatch):
    """JSON that parses to a dictionary or number instead of a list must fail."""
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", '{"model": "gemini-3.5-flash-lite"}')
    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "must be a list of model names" in str(excinfo.value)


def test_cors_origins_comma_separated_and_json(monkeypatch):
    """Verify CORS_ORIGINS accepts both comma-separated and JSON string formats."""
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, https://myapp.pages.dev")
    s1 = Settings()
    assert s1.CORS_ORIGINS == ["http://localhost:3000", "https://myapp.pages.dev"]

    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000", "https://myapp.pages.dev"]')
    s2 = Settings()
    assert s2.CORS_ORIGINS == ["http://localhost:3000", "https://myapp.pages.dev"]
