"""Subprocess environment hygiene for the CLI backends.

The billing gotcha (hotfix ported from the analyzer/StoryDaemon lineage,
step 0 of the shared llm-backends plan): ai_helper.py runs load_dotenv(),
so provider API keys from .env sit in os.environ. The agent CLIs (codex,
claude, gemini) treat an environment API key as OUTRANKING their own
configured subscription login, so a CLI backend that inherits the full
environment silently bills the metered API key instead of the
subscription the user thinks is paying. Stripping the key from the child
environment restores the CLI's own auth; the failure mode of stripping is
a visible auth error, the failure mode of not stripping is silent money.

This module is expected to be superseded by the shared llm-backends
package (docs/LLM_BACKENDS_INVENTORY.md in StoryDaemon).
"""

import os


def subprocess_env_without(*keys: str) -> dict:
    """A copy of os.environ with the named variables removed."""
    env = os.environ.copy()
    for key in keys:
        env.pop(key, None)
    return env
