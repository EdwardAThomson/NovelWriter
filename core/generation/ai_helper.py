# ai_helper.py
#
# Backward-compatible LLM facade for NovelWriter, now backed by the shared
# `llm-backends` package (StoryDaemon docs/LLM_BACKENDS_INVENTORY.md section
# 7.4, step 4). The GUI and the agents import everything LLM-shaped from here:
# send_prompt / send_prompt_with_retry, the backend state (set_backend /
# get_backend / get_model), and the dropdown sources (get_supported_models /
# get_available_backends / check_cli_availability).
#
# What changed at adoption:
# - ONE model registry (the package's) instead of the two disagreeing local
#   ones this module and llm_interface/multi_provider_llm.py used to carry.
#   get_supported_models() now returns the package's primary keys; the old
#   NovelWriter names are gone from the list. "claude-4-5-sonnet" still works
#   via the package alias table; "claude-4-5-opus" has no package primary and
#   deliberately raises ValueError (it must not be silently re-pointed at a
#   newer Opus).
# - The default API model is the package's DEFAULT_API_MODEL instead of the
#   hardcoded "gpt-4o".
# - The Anthropic key is read by the package: ANTHROPIC_API_KEY is canonical,
#   with the historical CLAUDE_API_KEY spelling still honored as a deprecated
#   fallback, so existing .env files keep working.
# - The CLI backends strip provider API keys from their subprocess env by
#   default (the billing gotcha; this supersedes the interim _env.py hotfix).

import os  # noqa: F401  (kept for callers that reach through this module)
from typing import Optional

from dotenv import load_dotenv

from llm_backends import DEFAULT_API_MODEL
from llm_backends import multi_provider_llm as _mp
from llm_backends.multi_provider_llm import (  # noqa: F401  back-compat re-exports
    get_supported_models,
    resolve_model,
    send_prompt_claude,
    send_prompt_gemini,
    send_prompt_openai,
)

from .llm_interface import (
    check_cli_availability,  # noqa: F401  re-export (GUI dropdown source)
    get_available_backends,  # noqa: F401  re-export (GUI dropdown source)
    get_current_backend,
    initialize_llm,
    is_initialized,
    send_prompt as llm_send_prompt,
)


load_dotenv()  # Load API keys from .env into the environment (app-owned; the package only reads os.environ)


# --- Backend State ---
# Backend selection state lives in llm_interface; we keep the current API
# model here for the API backend.
_current_model: str = DEFAULT_API_MODEL

# NovelWriter's system prompt for API generations (A5: system prompts are
# app-owned; the package default would otherwise apply).
ROLE_DESCRIPTION = (
    "You are a helpful fiction writing assistant. You will create original text only."
)

# max_tokens for API generations (the CLI backends use their own defaults).
DEFAULT_MAX_TOKENS = 16384


def set_backend(backend: str, model: Optional[str] = None) -> None:
    """Set the LLM backend to use.

    Args:
        backend: Backend identifier ("api", "codex", "gemini-cli", "claude-cli")
        model: Model to use. For "api" this is a package registry key
               (defaults to the current model, initially DEFAULT_API_MODEL).
    """
    global _current_model
    if model:
        _current_model = model

    initialize_llm(backend=backend, model=_current_model)


def get_backend() -> str:
    """Get the current backend name."""
    # Use the llm_interface module's state (single source of truth)
    return get_current_backend() or "api"


def get_model() -> str:
    """Get the current model name (for API backend)."""
    return _current_model


def send_prompt(prompt, model=None):
    """Sends a prompt to the specified AI model.

    Routes to the appropriate backend based on current settings: CLI backends
    go through llm_interface; the API backend goes through the llm-backends
    model registry (which also accepts legacy aliases such as
    "claude-4-5-sonnet" and the "openrouter:<upstream-id>" passthrough form).

    Args:
        prompt: The text prompt to send.
        model: Model name (used for API backend, ignored for CLI backends).
               If None, uses the currently selected model.

    Returns:
        Generated text from the LLM.

    Raises:
        ValueError: If the model is not in the package registry (nor an alias).
    """
    global _current_model

    # Get current backend from the unified interface (single source of truth)
    current_backend = get_backend()

    # If using a CLI backend, use the unified interface directly
    if current_backend != "api":
        if not is_initialized():
            initialize_llm(backend=current_backend)
        print(f"Using CLI backend: {current_backend}")
        return llm_send_prompt(prompt)

    # Use current model if none provided
    if model is None:
        model = _current_model

    # Validate/resolve against the package registry (raises ValueError with
    # the supported list for unknown names, e.g. the retired claude-4-5-opus).
    resolve_model(model)

    print(f"Attempting to use model: {model}")
    _current_model = model

    try:
        return _mp.send_prompt(prompt, model=model, max_tokens=DEFAULT_MAX_TOKENS)
    except Exception as e:
        print(f"Error calling model '{model}': {e}")
        raise


def send_prompt_with_retry(prompt, model=None, max_retries=3):
    """Send a prompt with automatic retry on failure.

    Args:
        prompt: The text prompt to send.
        model: Model name (used for API backend). If None, uses current model.
        max_retries: Maximum number of retry attempts.

    Returns:
        Generated text from the LLM.
    """
    if model is None:
        model = get_model()

    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            return send_prompt(prompt, model=model)
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                continue

    raise RuntimeError(
        f"Model '{model}' failed after {max_retries} attempts. Last error: {last_error}"
    )


# --- Provider-specific functions (backward compatibility) ---
# Thin delegates to the package provider functions. The old local client
# singletons are gone; the package manages clients (and the ANTHROPIC_API_KEY
# canon with the CLAUDE_API_KEY fallback) itself.


def send_prompt_oai(prompt, model=None, max_tokens=DEFAULT_MAX_TOKENS, temperature=0.7,
                    role_description=ROLE_DESCRIPTION):
    """Send prompts to OpenAI chat models (legacy helper)."""
    if model is None:
        model = get_model()
    return send_prompt_openai(
        prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        role_description=role_description,
    )


def send_prompt_gemini_direct(prompt, model_name="gemini-2.5-pro", max_output_tokens=8192,
                              temperature=0.7):
    """Send a prompt to the Gemini API directly (legacy helper)."""
    return send_prompt_gemini(
        prompt,
        model_name=model_name,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
    )


def send_prompt_claude_direct(prompt, model="claude-sonnet-4-5-20250929", max_tokens=8192,
                              temperature=0.7,
                              role_description=(
                                  "You are a skilled creative writer focused on producing original fiction."
                              )):
    """Send a prompt to Anthropic's Claude API directly (legacy helper)."""
    return send_prompt_claude(
        prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        role_description=role_description,
    )
