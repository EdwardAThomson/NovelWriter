# Roadmap — NovelWriter

_Status: active · updated 2026-07-14_

> Python/Tkinter desktop app that helps authors write multi-genre novels and short stories with LLMs, managing parameters, lore, story structure, scene plans, and chapter prose, layered with an agentic multi-agent orchestration and multi-level review framework.
>
> Collated from docs/refactor_plan.md (the source of the refactor checklists) plus the shipped agents/ package and docs/agentic_*.md for the agentic milestone. Design/spec docs that carry no actionable task lists are otherwise excluded.

## Codebase Refactor (core/ + agents/ structure)
> Completed August 4, 2025 per the "Refactor Completion Status" section of refactor_plan.md. The original document left its checklists unchecked, but its own sign-off confirms these were done (reflected here as complete). Double-check the two "Code Quality" items below.
- [x] Create `core/` directory structure (gui, generation, config, utils) with `__init__.py` files
- [x] Create `agents/` directory structure (base, quality, consistency, orchestration)
- [x] Move GUI components to `core/gui/` (main.py → core/gui/app.py, parameters, lore, story_structure, scene_plan, chapter_writing)
- [x] Move generation logic to `core/generation/` (ai_helper, helper_fns, rag_helper)
- [x] Move configuration to `core/config/` (logger_config, genre_configs)
- [x] Move utilities to `core/utils/` (combine.py)
- [x] Update all import statements across moved modules
- [x] Add new `main.py` entry point that imports `core.gui.app`

## Refactor Verification: Functional
- [x] Application starts successfully from new `main.py`
- [x] All GUI tabs load and function correctly
- [x] Parameter collection works
- [x] Lore generation works
- [x] Story structure generation works
- [x] Scene planning works
- [x] Chapter writing works
- [x] File save/load operations work
- [x] Logging functions correctly

## Refactor Verification: Code Quality & Agent Readiness
- [x] No circular imports
- [x] Clean import statements
- [x] Proper package structure
- [x] All `__init__.py` files in place
- [x] No hardcoded paths that break
- [x] Clear separation between core and future agents
- [x] Easy import path for agents to use core functionality
- [x] Modular structure ready for extension

## Agentic Framework (multi-agent orchestration + review)
> The agentic layer the refactor prepared for, now shipped. Present in the agents/ package and described in docs/agentic_implementation.md, agentic_integration_guide.md, and agent_workflow_explanation.md.
- [x] Base agent and tool abstractions (BaseAgent, BaseTool, ToolRegistry, typed AgentMessage/AgentResult)
- [x] Specialized agents: adaptive planning, consistency, quality control, review-and-retry, chapter writing
- [x] Consistency tooling (character-consistency, world-building, and plot-thread tracking tools)
- [x] Multi-agent orchestration layer (MultiAgentOrchestrator, plus StoryGeneration and IntegratedStory orchestrators)
- [x] Checkpoint/resume for long generation workflows (CheckpointStateManager, WorkflowState)
- [x] Multi-level review system (scene / chapter / batch reviews with quality thresholds and trend tracking)
- [x] Unified multi-backend LLM interface routing to hosted APIs or local CLI tools (core/generation/llm_interface)
- [x] Documentation refreshed: README synced to current code, plus developer, integration, and workflow guides under docs/

## Backlog
- [ ] CI/CD: build scripts, test paths, deployment scripts
      Low priority for a desktop app; revisit only if distribution/packaging calls for it.

## Notes
- refactor_plan.md documents the one-time core/ + agents/ reorganization. The agentic layer it prepared for has since shipped (see the Agentic Framework milestone); its design lives in docs/agentic_implementation.md, agentic_integration_guide.md, and agent_workflow_explanation.md.
