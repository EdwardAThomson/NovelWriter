"""Unified LLM interface for NovelWriter: thin wrapper over llm-backends.

The backend implementations (API providers and the three CLI agents) live in
the shared `llm-backends` package. This module keeps only the NovelWriter
specifics the package deliberately does not own:

- the "api" default backend (the package's module-level default is "codex"),
- the NovelWriter-facing backend name state (get_current_backend) and the
  AVAILABLE_BACKENDS description dict consumed by the GUI dropdown,
- the 16384 max_tokens default used by the writing workflows,
- the custom-binary kwargs (codex_bin / gemini_bin / claude_bin) of the old
  initialize_llm signature.

This is a plain re-export wrapper rather than a sys.modules alias because of
those NovelWriter-owned defaults; nothing in this repo monkeypatches the
module's privates (there was no test suite for this layer before adoption).

Backends:
- "api"         → Multi-provider API backend (registry in llm_backends)
- "codex"       → Codex CLI
- "gemini-cli"  → Gemini CLI backend using the local `gemini` binary
- "claude-cli"  → Claude Code CLI backend using the local `claude` binary
"""
from typing import Optional

from llm_backends import DEFAULT_API_MODEL
from llm_backends.llm_interface import LLMClient  # re-export, public surface
from llm_backends.llm_interface import check_cli_availability  # noqa: F401 re-export
from llm_backends import (
    ClaudeCliInterface,
    CodexInterface,
    GeminiCliInterface,
    MultiProviderInterface,
)


# Global LLM client instance used by helper functions
_llm_client: Optional[LLMClient] = None
_current_backend: Optional[str] = None


# Available backends (GUI dropdown source)
AVAILABLE_BACKENDS = {
    "api": "Multi-provider API (OpenAI, Gemini, Claude, OpenRouter, ...)",
    "codex": "Codex CLI",
    "gemini-cli": "Gemini CLI",
    "claude-cli": "Claude Code CLI",
}


def get_available_backends() -> dict:
    """Return dictionary of available backends with descriptions."""
    return AVAILABLE_BACKENDS.copy()


def get_current_backend() -> Optional[str]:
    """Return the currently active backend name (None if not initialized)."""
    return _current_backend


def initialize_llm(
    backend: str = "api",
    codex_bin: str = "codex",
    gemini_bin: str = "gemini",
    claude_bin: str = "claude",
    model: Optional[str] = None,
) -> LLMClient:
    """Initialize the LLM client for the given backend.

    Args:
        backend: LLM backend identifier ("api", "codex", "gemini-cli", or "claude-cli").
        codex_bin: Path to Codex CLI binary (for backend="codex").
        gemini_bin: Path to Gemini CLI binary (for backend="gemini-cli").
        claude_bin: Path to Claude CLI binary (for backend="claude-cli").
        model: Model identifier. For backend="api" this is a registry key
            (llm_backends.get_supported_models() lists them; legacy aliases
            like "claude-4-5-sonnet" also resolve). For the CLI backends it is
            forwarded when it fits the CLI (gemini-* names to the Gemini CLI,
            Claude names to the Claude CLI); otherwise the CLI's own default
            model is used.

    Returns:
        An initialized LLM client instance.

    Raises:
        RuntimeError: If the requested backend cannot be initialized.
    """
    global _llm_client, _current_backend

    backend_normalized = backend.lower().strip()

    if backend_normalized in {"api", "openai"}:
        # "openai" kept for backward compatibility
        _llm_client = MultiProviderInterface(model=model or DEFAULT_API_MODEL)
        _current_backend = "api"
    elif backend_normalized == "codex":
        _llm_client = CodexInterface(codex_bin)
        _current_backend = "codex"
    elif backend_normalized in {"gemini-cli", "gemini"}:
        # Only forward Gemini model names; otherwise the interface default wins.
        if model and model.startswith("gemini"):
            _llm_client = GeminiCliInterface(model=model, gemini_bin=gemini_bin)
        else:
            _llm_client = GeminiCliInterface(gemini_bin=gemini_bin)
        _current_backend = "gemini-cli"
    elif backend_normalized in {"claude-cli", "claude"}:
        # ClaudeCliInterface itself ignores non-Claude model names.
        _llm_client = ClaudeCliInterface(claude_bin, model=model)
        _current_backend = "claude-cli"
    else:
        raise RuntimeError(
            f"Unsupported LLM backend: {backend}. "
            f"Supported backends are: {', '.join(AVAILABLE_BACKENDS.keys())}"
        )

    return _llm_client


def send_prompt(prompt: str, max_tokens: int = 16384) -> str:
    """Send a prompt using the initialized LLM client.

    Args:
        prompt: The prompt to send.
        max_tokens: Maximum tokens to generate (API backend; the CLI backends
            use their own defaults).

    Returns:
        Generated text from the configured LLM backend.

    Raises:
        RuntimeError: If no backend is initialized or generation fails.
    """
    if _llm_client is None:
        # Default to API backend if nothing has been explicitly initialized
        initialize_llm(backend="api")

    return _llm_client.generate(prompt, max_tokens=max_tokens)  # type: ignore[union-attr]


def send_prompt_with_retry(
    prompt: str,
    max_tokens: int = 16384,
    max_retries: int = 3,
) -> str:
    """Send prompt with automatic retry on failure.

    Args:
        prompt: The prompt to send.
        max_tokens: Maximum tokens to generate.
        max_retries: Maximum retry attempts.

    Returns:
        Generated text from the configured LLM backend.

    Raises:
        RuntimeError: If all retry attempts fail or no backend is initialized.
    """
    if _llm_client is None:
        # Default to API backend if nothing has been explicitly initialized
        initialize_llm(backend="api")

    return _llm_client.generate_with_retry(  # type: ignore[union-attr]
        prompt,
        max_tokens=max_tokens,
        max_retries=max_retries,
    )


def is_initialized() -> bool:
    """Check if an LLM backend has been initialized."""
    return _llm_client is not None
