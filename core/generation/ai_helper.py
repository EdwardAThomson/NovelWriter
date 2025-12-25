# ai_helper.py
# https://platform.openai.com/docs/models
#
# This module provides backward-compatible LLM access for NovelWriter.
# It now uses the unified llm_interface module under the hood, which supports:
# - API backends (OpenAI, Gemini, Claude)
# - CLI backends (Codex, Gemini CLI, Claude CLI)

import os
from typing import Optional
from dotenv import load_dotenv

# Import from the new unified interface
from .llm_interface import (
    initialize_llm,
    send_prompt as llm_send_prompt,
    send_prompt_with_retry as llm_send_prompt_with_retry,
    get_available_backends,
    get_current_backend,
    is_initialized,
    check_cli_availability,
)
from .llm_interface.multi_provider_llm import (
    get_supported_models as get_api_models,
    send_prompt_openai,
    send_prompt_gemini,
    send_prompt_claude,
)


load_dotenv()  # This will load environment variables from the .env file


# --- Backend State ---
# Note: The actual backend state is managed by llm_interface module.
# We keep _current_model here for API backend model selection.
_current_model: str = "gpt-4o"  # Default model for API backend


def set_backend(backend: str, model: str = "gpt-4o") -> None:
    """Set the LLM backend to use.
    
    Args:
        backend: Backend identifier ("api", "codex", "gemini-cli", "claude-cli")
        model: Model to use (only applies to "api" backend)
    """
    global _current_model
    _current_model = model
    initialize_llm(backend=backend, model=model)


def get_backend() -> str:
    """Get the current backend name."""
    # Use the llm_interface module's state (single source of truth)
    return get_current_backend() or "api"


def get_model() -> str:
    """Get the current model name (for API backend)."""
    return _current_model


# --- Model Configuration (Backward Compatibility) ---
# These are the models available via the API backend
_model_config = {
    "gpt-4o": lambda prompt: send_prompt_openai(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=16384,
        temperature=0.7,
        role_description="You are an expert storyteller focused on character relationships."
    ),
    "o3": lambda prompt: send_prompt_openai_reasoning(prompt, model="o3"),
    "o4-mini": lambda prompt: send_prompt_openai_reasoning(prompt, model="o4-mini"),
    "gpt-5-2025-08-07": lambda prompt: send_prompt_openai_reasoning(prompt, model="gpt-5-2025-08-07"),
    "gemini-2.5-pro-exp-03-25": lambda prompt: send_prompt_gemini(
         prompt=prompt,
         model_name="gemini-2.5-pro-exp-03-25",
         max_output_tokens=8192,
         temperature=0.7,
    ),
    "gemini-3-pro-preview": lambda prompt: send_prompt_gemini(
         prompt=prompt,
         model_name="gemini-3-pro-preview",
         max_output_tokens=8192,
         temperature=0.7,
    ),
    "claude-4-5-sonnet": lambda prompt: send_prompt_claude(
         prompt=prompt,
         model="claude-sonnet-4-5-20250929",
         max_tokens=8192,
         temperature=0.7
    ),
    "claude-4-5-opus": lambda prompt: send_prompt_claude(
         prompt=prompt,
         model="claude-opus-4-5",
         max_tokens=8192,
         temperature=0.7
    ),
}


def get_supported_models():
    """Returns a list of supported model names for the API backend."""
    return list(_model_config.keys())


def send_prompt(prompt, model="gpt-4o"):
    """Sends a prompt to the specified AI model.
    
    This function routes to the appropriate backend based on current settings.
    For API backend, it uses the model parameter.
    For CLI backends, it uses the configured CLI tool.
    
    Args:
        prompt: The text prompt to send.
        model: Model name (used for API backend, ignored for CLI backends).
        
    Returns:
        Generated text from the LLM.
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
    
    # For API backend, use the model registry
    if model not in _model_config:
        # Try adding '-latest' if applicable
        if f"{model}-latest" in _model_config:
             model = f"{model}-latest"
        else:
             supported_models = get_supported_models()
             raise ValueError(f"Unsupported model: {model}. Supported models are: {supported_models}")

    print(f"Attempting to use model: {model}")
    _current_model = model
    
    try:
        return _model_config[model](prompt)
    except Exception as e:
        print(f"Error calling model '{model}': {e}")
        raise


def send_prompt_with_retry(prompt, model="gpt-4o", max_retries=3):
    """Send a prompt with automatic retry on failure.
    
    Args:
        prompt: The text prompt to send.
        model: Model name (used for API backend).
        max_retries: Maximum number of retry attempts.
        
    Returns:
        Generated text from the LLM.
    """
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


# --- Provider-specific functions (for backward compatibility) ---

# Lazy-loaded clients
_openai_client = None
_anthropic_client = None
_gemini_configured = False


def _get_openai_client():
    """Get or create OpenAI client."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _openai_client


def _get_anthropic_client():
    """Get or create Anthropic client."""
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
    return _anthropic_client


def _ensure_gemini_configured():
    """Configure Gemini if not already done."""
    global _gemini_configured
    if not _gemini_configured:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        _gemini_configured = True


def send_prompt_oai(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7,
                role_description="You are a helpful fiction writing assistant. You will create original text only."):
    """Send prompts with GPT-4o and similar models."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": role_description},
            {"role": "user", "content": prompt},
        ],
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    print("model used: ", model)
    return response.choices[0].message.content


def send_prompt_openai_reasoning(prompt, model="o3"):
    """Send prompts with OpenAI reasoning models (o1, o3, o4-mini, etc.)."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    print("Used model: ", model)
    return response.choices[0].message.content


# Alias for backward compatibility
send_prompt_o1 = send_prompt_openai_reasoning


def send_prompt_gemini_direct(prompt, model_name="gemini-2.5-pro-exp-03-25", max_output_tokens=8192, 
                              temperature=0.7, top_p=1, top_k=1):
    """Send a prompt to the Gemini API directly."""
    _ensure_gemini_configured()
    import google.generativeai as genai
    
    model = genai.GenerativeModel(model_name)
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=False
        )
        print("Used model: ", model_name)
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def send_prompt_claude_direct(prompt, model="claude-sonnet-4-5-20250929", max_tokens=8192, temperature=0.7,
                              role_description="You are a skilled creative writer focused on producing original fiction."):
    """Send a prompt to Anthropic's Claude API directly."""
    try:
        client = _get_anthropic_client()
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=role_description,
            messages=[{"role": "user", "content": prompt}]
        )
        print("Used model: ", model)
        return response.content[0].text
    except Exception as e:
        print(f"Error generating content with Claude: {e}")
        return None

