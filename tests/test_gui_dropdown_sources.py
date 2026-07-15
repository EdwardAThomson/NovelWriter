"""The GUI dropdowns read their contents through ai_helper from llm-backends.

core/gui/app.py builds:
- the model combobox from get_supported_models(),
- the backend combobox from get_available_backends(),
- the CLI status label from check_cli_availability().
"""

from core.generation.ai_helper import (
    DEFAULT_API_MODEL,
    check_cli_availability,
    get_available_backends,
    get_supported_models,
)


def test_get_supported_models_is_package_registry():
    import llm_backends
    models = get_supported_models()
    assert models, "model dropdown source must be non-empty"
    assert models == llm_backends.get_supported_models()
    # The GUI default selection must be a real registry key.
    assert DEFAULT_API_MODEL in models
    # Spot-check current-generation keys and absence of the 2025 list.
    assert "claude-sonnet-4-6" in models
    assert "gpt-4o" not in models
    assert "claude-4-5-opus" not in models


def test_check_cli_availability_returns_three_backends():
    status = check_cli_availability()
    assert set(status.keys()) == {"codex", "gemini-cli", "claude-cli"}
    assert all(isinstance(v, bool) for v in status.values())


def test_get_available_backends_keys():
    backends = get_available_backends()
    assert set(backends.keys()) == {"api", "codex", "gemini-cli", "claude-cli"}
