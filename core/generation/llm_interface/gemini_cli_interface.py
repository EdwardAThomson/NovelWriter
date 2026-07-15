"""Compatibility shim over the llm-backends package; will eventually be dropped.

The Gemini CLI backend now lives in the shared `llm-backends` package, which
key-strips GEMINI_API_KEY and GOOGLE_API_KEY from the subprocess env by
default (superseding the interim _env.py hotfix) and runs from a neutral cwd
with --skip-trust. New code should import from ``llm_backends`` directly.
"""
import sys

from llm_backends import gemini_cli_interface as _impl

sys.modules[__name__] = _impl
