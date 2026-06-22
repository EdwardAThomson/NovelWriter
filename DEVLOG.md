# Development Log

## 2026-06-20

Reconciled the README against the current codebase after a refactor had moved several modules around. The documentation still pointed at old locations, so paths were corrected to reflect the new layout — `combine.py` now lives at `core/utils/combine.py` (previously described as being in the root directory) and `ai_helper.py` at `core/generation/ai_helper.py`. The configured-models list was also brought up to date: Gemini 3 Pro and Claude 4.5 Opus were added, and o3 / o4-mini were removed from the Deprecated list since they are in fact still active per `ai_helper.py`.

**Decisions & notes:** This was a full-audit pass of the README rather than a one-off fix, aimed at keeping the docs trustworthy as the code is refactored.
