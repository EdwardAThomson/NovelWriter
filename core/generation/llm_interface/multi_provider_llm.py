"""Compatibility shim over the llm-backends package; will eventually be dropped.

The multi-provider API layer now lives in the shared `llm-backends` package
(sibling checkout / pinned git dependency; see StoryDaemon
docs/LLM_BACKENDS_INVENTORY.md section 7.4, step 4). This module aliases
itself to ``llm_backends.multi_provider_llm`` in ``sys.modules``, so every
name under the old import path (send_prompt, the provider send functions,
get_supported_models, MultiProviderInterface, MODEL_ALIASES, resolve_model)
resolves to the package module itself. New code should import from
``llm_backends`` directly.

Note the model-list bump that comes with this: the old NovelWriter registry
(gpt-4o, o3, o4-mini, gpt-5-2025-08-07, gemini-2.5-pro-exp-03-25,
claude-4-5-sonnet) is replaced by the package's unified registry.
"claude-4-5-sonnet" still resolves via MODEL_ALIASES; "claude-4-5-opus" has
no package primary and now raises ValueError by design (it must not be
silently aliased to a newer Opus).
"""
import sys

from llm_backends import multi_provider_llm as _impl

sys.modules[__name__] = _impl
