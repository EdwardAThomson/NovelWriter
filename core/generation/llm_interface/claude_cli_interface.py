"""Compatibility shim over the llm-backends package; will eventually be dropped.

The Claude Code CLI backend now lives in the shared `llm-backends` package,
which key-strips ANTHROPIC_API_KEY and CLAUDE_API_KEY from the subprocess env
by default (superseding the interim _env.py hotfix) and runs from a neutral
cwd. New code should import from ``llm_backends`` directly.
"""
import sys

from llm_backends import claude_cli_interface as _impl

sys.modules[__name__] = _impl
