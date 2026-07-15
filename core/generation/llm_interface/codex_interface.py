"""Compatibility shim over the llm-backends package; will eventually be dropped.

The Codex CLI backend now lives in the shared `llm-backends` package, which
key-strips OPENAI_API_KEY from the subprocess env by default (superseding the
interim _env.py hotfix), runs from a neutral cwd, uses a read-only sandbox,
and carries the bubblewrap/user-namespace workaround for hardened Linux.
New code should import from ``llm_backends`` directly.
"""
import sys

from llm_backends import codex_interface as _impl

sys.modules[__name__] = _impl
