"""Unified LLM interface for NovelWriter.

Provides a backend-agnostic interface for LLM access.

Backends:
- "api"         → Multi-provider API backend (OpenAI, Gemini, Claude) using
                  a model registry.
- "codex"       → Codex CLI (GPT-5 via codex exec)
- "gemini-cli"  → Gemini CLI backend using the local `gemini` binary.
- "claude-cli"  → Claude Code CLI backend using the local `claude` binary.

The API backend uses model names (e.g. "gpt-4o", "claude-4-5-sonnet",
"gemini-2.5-pro-exp-03-25") to route to the correct provider.
"""
from typing import Optional, Union

from .codex_interface import CodexInterface
from .multi_provider_llm import MultiProviderInterface
from .gemini_cli_interface import GeminiCliInterface
from .claude_cli_interface import ClaudeCliInterface


LLMClient = Union[CodexInterface, MultiProviderInterface, GeminiCliInterface, ClaudeCliInterface]


# Global LLM client instance used by helper functions
_llm_client: Optional[LLMClient] = None
_current_backend: Optional[str] = None


# Available backends
AVAILABLE_BACKENDS = {
    "api": "Multi-provider API (OpenAI, Gemini, Claude)",
    "codex": "Codex CLI (GPT-5)",
    "gemini-cli": "Gemini CLI",
    "claude-cli": "Claude Code CLI",
}


def get_available_backends() -> dict:
    """Return dictionary of available backends with descriptions.
    
    Returns:
        Dict mapping backend ID to description string.
    """
    return AVAILABLE_BACKENDS.copy()


def get_current_backend() -> Optional[str]:
    """Return the currently active backend name.
    
    Returns:
        Backend name string or None if not initialized.
    """
    return _current_backend


def initialize_llm(
    backend: str = "api",
    codex_bin: str = "codex",
    gemini_bin: str = "gemini",
    claude_bin: str = "claude",
    model: str = "gpt-4o",
) -> LLMClient:
    """Initialize the LLM client for the given backend.

    Args:
        backend: LLM backend identifier ("api", "codex", "gemini-cli", or "claude-cli").
        codex_bin: Path to Codex CLI binary (for backend="codex").
        gemini_bin: Path to Gemini CLI binary (for backend="gemini-cli").
        claude_bin: Path to Claude CLI binary (for backend="claude-cli").
        model: Model identifier for API backend (for backend="api").

    Returns:
        An initialized LLM client instance.

    Raises:
        RuntimeError: If the requested backend cannot be initialized.
    """
    global _llm_client, _current_backend

    backend_normalized = backend.lower().strip()

    if backend_normalized in {"api", "openai"}:
        # "openai" kept for backward compatibility
        _llm_client = MultiProviderInterface(model=model)
        _current_backend = "api"
    elif backend_normalized == "codex":
        _llm_client = CodexInterface(codex_bin)
        _current_backend = "codex"
    elif backend_normalized in {"gemini-cli", "gemini"}:
        # Use Gemini-appropriate model, not the API default
        gemini_model = model if model.startswith("gemini") else "gemini-2.5-pro"
        _llm_client = GeminiCliInterface(model=gemini_model, gemini_bin=gemini_bin)
        _current_backend = "gemini-cli"
    elif backend_normalized in {"claude-cli", "claude"}:
        _llm_client = ClaudeCliInterface(claude_bin)
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
        max_tokens: Maximum tokens to generate.

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
    """Check if an LLM backend has been initialized.

    Returns:
        True if initialized, False otherwise.
    """
    return _llm_client is not None


def check_cli_availability() -> dict:
    """Check which CLI backends are available on the system.
    
    Returns:
        Dict mapping CLI backend names to availability status.
    """
    return {
        "codex": CodexInterface.is_available(),
        "gemini-cli": GeminiCliInterface.is_available(),
        "claude-cli": ClaudeCliInterface.is_available(),
    }
