# Development Log

## 2026-07-14

A project-housekeeping day focused on making NovelWriter's status and direction legible from the repo itself. The morning brought GitHub Sponsors support: a `.github/FUNDING.yml` config plus a sponsor badge in the README. The bigger work was creating `ROADMAP.md`, which collates the completed core/ + agents/ refactor (signed off August 2025 in `docs/refactor_plan.md`) and the since-shipped agentic framework milestone (base agent/tool abstractions, specialized agents, orchestration, checkpointing, multi-level review, and the multi-backend LLM interface) into one checklist-style document. A follow-up pass then added a "Cross-pollination from StoryDaemon" section, planning to port tension/arc-pressure control, grounded name generation, contradiction detection, wiring up the dormant ChromaDB RAG memory, and making the QA review loop actually enforce retries, with the full rationale living in StoryDaemon's `docs/CROSS_POLLINATION.md`.

**Decisions & notes:** The roadmap deliberately marks the refactor checklists complete based on the plan's own sign-off even though the original document left them unchecked. New backlog items acknowledge known debt: no test suite for core/ and agents/, dead code to remove (IntegratedStoryOrchestrator, AdaptivePlanningAgent, the mismatched top-level `generate_story()`), and a possible shared LLM-backend package spanning NovelWriter, StoryDaemon, and LLM-Remote-Runner (home/name/distribution still undecided).

## 2026-06-20

Reconciled the README against the current codebase after a refactor had moved several modules around. The documentation still pointed at old locations, so paths were corrected to reflect the new layout — `combine.py` now lives at `core/utils/combine.py` (previously described as being in the root directory) and `ai_helper.py` at `core/generation/ai_helper.py`. The configured-models list was also brought up to date: Gemini 3 Pro and Claude 4.5 Opus were added, and o3 / o4-mini were removed from the Deprecated list since they are in fact still active per `ai_helper.py`.

**Decisions & notes:** This was a full-audit pass of the README rather than a one-off fix, aimed at keeping the docs trustworthy as the code is refactored.
