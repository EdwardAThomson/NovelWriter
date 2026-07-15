"""Fake-LLM generation through ai_helper's public send_prompt path.

Monkeypatches the llm-backends registry entry (no network, no SDKs needed)
and drives the exact route the GUI/agents use:
ai_helper.send_prompt -> llm_backends.multi_provider_llm.send_prompt.
"""

import pytest

import llm_backends.multi_provider_llm as mp
from core.generation import ai_helper


@pytest.fixture()
def fake_model(monkeypatch):
    calls = {}

    def fake_fn(prompt, max_tokens, timeout=None):
        calls["prompt"] = prompt
        calls["max_tokens"] = max_tokens
        return "FAKE RESPONSE"

    monkeypatch.setitem(mp._model_config, "gpt-5.5", fake_fn)
    return calls


def test_send_prompt_default_model_routes_through_package(fake_model):
    ai_helper.set_backend("api")  # ensure API backend, default model
    out = ai_helper.send_prompt("hello world")
    assert out == "FAKE RESPONSE"
    assert fake_model["prompt"] == "hello world"
    # NovelWriter's writing workflows keep the 16384 budget of the old layer.
    assert fake_model["max_tokens"] == ai_helper.DEFAULT_MAX_TOKENS == 16384


def test_send_prompt_explicit_model(fake_model):
    ai_helper.set_backend("api")
    assert ai_helper.send_prompt("hi", model="gpt-5.5") == "FAKE RESPONSE"
    assert ai_helper.get_model() == "gpt-5.5"


def test_send_prompt_with_retry_recovers(monkeypatch):
    attempts = {"n": 0}

    def flaky_fn(prompt, max_tokens, timeout=None):
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise RuntimeError("transient")
        return "OK"

    monkeypatch.setitem(mp._model_config, "gpt-5.5", flaky_fn)
    ai_helper.set_backend("api")
    assert ai_helper.send_prompt_with_retry("hi", model="gpt-5.5") == "OK"
    assert attempts["n"] == 2


def test_legacy_sonnet_alias_still_resolves(monkeypatch):
    """NW's old registry key claude-4-5-sonnet resolves via MODEL_ALIASES."""
    seen = {}

    def fake_fn(prompt, max_tokens, timeout=None):
        seen["hit"] = True
        return "ALIASED"

    monkeypatch.setitem(mp._model_config, "claude-sonnet-4-5", fake_fn)
    ai_helper.set_backend("api")
    assert ai_helper.send_prompt("hi", model="claude-4-5-sonnet") == "ALIASED"
    assert seen["hit"]


def test_retired_claude_4_5_opus_errors_loudly():
    """claude-4-5-opus has no package primary and must NOT be silently
    aliased to a newer Opus: selecting it raises ValueError."""
    ai_helper.set_backend("api")
    with pytest.raises(ValueError, match="Unsupported model"):
        ai_helper.send_prompt("hi", model="claude-4-5-opus")


def test_old_dead_models_error_loudly():
    """The 2025-era NW registry names are gone from the package registry."""
    ai_helper.set_backend("api")
    for dead in ("gpt-4o", "o3", "o4-mini", "gpt-5-2025-08-07",
                 "gemini-2.5-pro-exp-03-25"):
        with pytest.raises(ValueError, match="Unsupported model"):
            ai_helper.send_prompt("hi", model=dead)
