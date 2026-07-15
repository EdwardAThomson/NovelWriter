"""Shim identity / import checks for the llm-backends adoption.

Every old NovelWriter import path used by consumers must keep working, and
the sys.modules-aliased modules must BE the package modules (not copies).

Consumers (grepped at adoption time) import only from
core.generation.ai_helper:
    send_prompt, send_prompt_with_retry, get_model, get_backend, set_backend,
    get_supported_models, get_available_backends, check_cli_availability
core.generation.llm_interface is imported only by ai_helper itself, but its
public __init__ surface is kept and checked here too.
"""

import importlib


def test_multi_provider_llm_shim_identity():
    import llm_backends.multi_provider_llm as pkg
    shim = importlib.import_module("core.generation.llm_interface.multi_provider_llm")
    assert shim is pkg


def test_cli_interface_shim_identity():
    import llm_backends.claude_cli_interface as claude_pkg
    import llm_backends.codex_interface as codex_pkg
    import llm_backends.gemini_cli_interface as gemini_pkg

    assert importlib.import_module(
        "core.generation.llm_interface.claude_cli_interface") is claude_pkg
    assert importlib.import_module(
        "core.generation.llm_interface.codex_interface") is codex_pkg
    assert importlib.import_module(
        "core.generation.llm_interface.gemini_cli_interface") is gemini_pkg


def test_llm_interface_package_surface():
    """The old `from core.generation.llm_interface import X` names all exist."""
    from core.generation.llm_interface import (  # noqa: F401
        LLMClient,
        ClaudeCliInterface,
        CodexInterface,
        GeminiCliInterface,
        MultiProviderInterface,
        check_cli_availability,
        get_available_backends,
        get_current_backend,
        get_supported_models,
        initialize_llm,
        is_initialized,
        send_prompt,
        send_prompt_claude,
        send_prompt_gemini,
        send_prompt_openai,
        send_prompt_with_retry,
    )
    # The CLI classes must be the package classes (key-stripping defaults ON).
    import llm_backends
    assert ClaudeCliInterface is llm_backends.ClaudeCliInterface
    assert CodexInterface is llm_backends.CodexInterface
    assert GeminiCliInterface is llm_backends.GeminiCliInterface
    assert MultiProviderInterface is llm_backends.MultiProviderInterface


def test_ai_helper_public_surface():
    """Every name the GUI/agents import from ai_helper still exists."""
    from core.generation.ai_helper import (  # noqa: F401
        DEFAULT_API_MODEL,
        check_cli_availability,
        get_available_backends,
        get_backend,
        get_model,
        get_supported_models,
        send_prompt,
        send_prompt_with_retry,
        set_backend,
    )


def test_env_hotfix_removed():
    """The interim _env.py hotfix is superseded by the package key-stripping."""
    import os
    import core.generation.llm_interface as nw_pkg
    assert not os.path.exists(os.path.join(os.path.dirname(nw_pkg.__file__), "_env.py"))
    # ...and the package's own stripping helper is what the CLI classes use.
    import llm_backends._env  # noqa: F401
