"""LLM Interface Module for NovelWriter.

Provides a unified, backend-agnostic interface for LLM access.

Backends:
- "api"         → Multi-provider API backend (OpenAI, Gemini, Claude)
- "codex"       → Codex CLI (GPT-5 via codex exec)
- "gemini-cli"  → Gemini CLI backend using the local `gemini` binary
- "claude-cli"  → Claude Code CLI backend using the local `claude` binary

Usage:
    from core.generation.llm_interface import initialize_llm, send_prompt
    
    # Initialize with desired backend
    initialize_llm(backend="api", model="gpt-4o")
    
    # Send prompts
    response = send_prompt("Write a story about...")
"""

from .llm_interface import (
    initialize_llm,
    send_prompt,
    send_prompt_with_retry,
    is_initialized,
    get_current_backend,
    get_available_backends,
    check_cli_availability,
    LLMClient,
)

from .multi_provider_llm import (
    MultiProviderInterface,
    get_supported_models,
    send_prompt_openai,
    send_prompt_gemini,
    send_prompt_claude,
)

from .codex_interface import CodexInterface
from .gemini_cli_interface import GeminiCliInterface
from .claude_cli_interface import ClaudeCliInterface

__all__ = [
    # Main interface
    "initialize_llm",
    "send_prompt",
    "send_prompt_with_retry",
    "is_initialized",
    "get_current_backend",
    "get_available_backends",
    "check_cli_availability",
    "LLMClient",
    # Multi-provider
    "MultiProviderInterface",
    "get_supported_models",
    "send_prompt_openai",
    "send_prompt_gemini",
    "send_prompt_claude",
    # CLI interfaces
    "CodexInterface",
    "GeminiCliInterface",
    "ClaudeCliInterface",
]
