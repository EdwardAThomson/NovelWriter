"""Multi-provider LLM interface for NovelWriter.

This module provides a model→function registry and a single send_prompt
entry point that can route prompts to different providers (OpenAI, Gemini,
Claude) based on the model name.

Environment variables expected (if using those providers):
- OPENAI_API_KEY   – for OpenAI Chat API
- GEMINI_API_KEY   – for Google Gemini
- CLAUDE_API_KEY   – for Anthropic Claude
"""

from typing import Callable, Dict, List, Optional
import os


try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore


_openai_client: Optional["OpenAI"] = None
_anthropic_client: Optional["anthropic.Anthropic"] = None
_gemini_configured: bool = False


def _get_openai_client() -> "OpenAI":
    """Return a shared OpenAI client, initialized from OPENAI_API_KEY."""
    global _openai_client

    if OpenAI is None:
        raise RuntimeError(
            "openai package is not installed. Install it with 'pip install openai'."
        )

    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Environment variable 'OPENAI_API_KEY' is not set. "
                "Set your OpenAI API key or use a different backend."
            )
        _openai_client = OpenAI(api_key=api_key)

    return _openai_client


def _get_anthropic_client() -> "anthropic.Anthropic":
    """Return a shared Anthropic client, initialized from CLAUDE_API_KEY."""
    global _anthropic_client

    if anthropic is None:
        raise RuntimeError(
            "anthropic package is not installed. Install it with 'pip install anthropic'."
        )

    if _anthropic_client is None:
        api_key = os.environ.get("CLAUDE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Environment variable 'CLAUDE_API_KEY' is not set. "
                "Set your Anthropic API key or use a different model."
            )
        _anthropic_client = anthropic.Anthropic(api_key=api_key)

    return _anthropic_client


def _ensure_gemini_configured():
    """Configure Gemini client using GEMINI_API_KEY if available."""
    global _gemini_configured

    if _gemini_configured:
        return

    if genai is None:
        raise RuntimeError(
            "google-generativeai package is not installed. Install it with "
            "'pip install google-generativeai'."
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Environment variable 'GEMINI_API_KEY' is not set. "
            "Set your Gemini API key or use a different model."
        )

    genai.configure(api_key=api_key)
    _gemini_configured = True


# --- Provider-specific prompt helpers ---


def send_prompt_openai(
    prompt: str,
    model: str = "gpt-4o",
    max_tokens: int = 16384,
    temperature: float = 0.7,
    role_description: str = (
        "You are a helpful fiction writing assistant. You will create original text only."
    ),
) -> str:
    """Send a prompt to the OpenAI Chat API."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": role_description},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def send_prompt_openai_reasoning(
    prompt: str,
    model: str = "o3",
) -> str:
    """Send a prompt to OpenAI reasoning models (o1, o3, o4-mini, etc.)."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def send_prompt_gemini(
    prompt: str,
    model_name: str = "gemini-2.5-pro-exp-03-25",
    max_output_tokens: int = 8192,
    temperature: float = 0.7,
) -> str:
    """Send a prompt to the Gemini API and return the generated text."""
    _ensure_gemini_configured()
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        ),
        stream=False,
    )
    return getattr(response, "text", "")


def send_prompt_claude(
    prompt: str,
    model: str = "claude-sonnet-4-5-20250929",
    max_tokens: int = 8192,
    temperature: float = 0.7,
    role_description: str = (
        "You are a skilled creative writer focused on producing original fiction."
    ),
) -> str:
    """Send a prompt to Anthropic Claude and return the generated text."""
    client = _get_anthropic_client()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=role_description,
        messages=[{"role": "user", "content": prompt}],
    )
    # Anthropic returns a list of content blocks; we take the first text block
    if response.content and hasattr(response.content[0], "text"):
        return response.content[0].text
    return ""


# --- Model registry ---


ModelFn = Callable[[str, int], str]


_model_config: Dict[str, ModelFn] = {
    # OpenAI GPT-4o family
    "gpt-4o": lambda prompt, max_tokens: send_prompt_openai(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=max_tokens,
    ),
    # OpenAI reasoning models
    "o3": lambda prompt, max_tokens: send_prompt_openai_reasoning(
        prompt=prompt,
        model="o3",
    ),
    "o4-mini": lambda prompt, max_tokens: send_prompt_openai_reasoning(
        prompt=prompt,
        model="o4-mini",
    ),
    "gpt-5-2025-08-07": lambda prompt, max_tokens: send_prompt_openai_reasoning(
        prompt=prompt,
        model="gpt-5-2025-08-07",
    ),
    # Gemini
    "gemini-2.5-pro-exp-03-25": lambda prompt, max_tokens: send_prompt_gemini(
        prompt=prompt,
        model_name="gemini-2.5-pro-exp-03-25",
        max_output_tokens=max_tokens,
    ),
    # Claude
    "claude-4-5-sonnet": lambda prompt, max_tokens: send_prompt_claude(
        prompt=prompt,
        model="claude-sonnet-4-5-20250929",
        max_tokens=max_tokens,
    ),
}


def get_supported_models() -> List[str]:
    """Return the list of supported model identifiers."""
    return list(_model_config.keys())


def send_prompt(prompt: str, model: str = "gpt-4o", max_tokens: int = 16384) -> str:
    """Send a prompt using the configured model registry.

    If the model key is not found, tries a "-latest" suffix before failing.
    """
    # Resolve model key
    if model not in _model_config:
        alt = f"{model}-latest"
        if alt in _model_config:
            model = alt
        else:
            supported = ", ".join(sorted(get_supported_models()))
            raise ValueError(
                f"Unsupported model: {model}. Supported models are: {supported}"
            )

    try:
        return _model_config[model](prompt, max_tokens)
    except Exception as e:
        raise RuntimeError(f"Error calling model '{model}': {e}") from e


def send_prompt_with_retry(
    prompt: str,
    model: str = "gpt-4o",
    max_tokens: int = 16384,
    max_retries: int = 3,
) -> str:
    """Send a prompt with simple retry logic on failure."""
    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            return send_prompt(prompt, model=model, max_tokens=max_tokens)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                continue

    raise RuntimeError(
        f"Model '{model}' failed after {max_retries} attempts. Last error: {last_error}"
    ) from last_error


class MultiProviderInterface:
    """Thin adapter exposing generate / generate_with_retry.

    This class allows NovelWriter to treat the model registry functions
    as a simple LLM client with generate(...) and generate_with_retry(...),
    similar to the CLI interfaces.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 16384, timeout: int = 120) -> str:
        # timeout is accepted for interface compatibility but not used directly
        return send_prompt(prompt, model=self.model, max_tokens=max_tokens)

    def generate_with_retry(
        self,
        prompt: str,
        max_tokens: int = 16384,
        timeout: int = 120,
        max_retries: int = 3,
    ) -> str:
        return send_prompt_with_retry(
            prompt,
            model=self.model,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )
