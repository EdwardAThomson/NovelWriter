# Agentic Features in NovelWriter

NovelWriter is a comprehensive Python application designed to assist authors in writing novels and short stories across multiple genres by leveraging Large Language Models (LLMs). It provides a GUI-based interface for managing novel parameters, generating universe lore, outlining story structure, planning scenes, and writing chapter prose.

The application features an advanced agentic framework with multi-agent orchestration and a multi-level review system for quality control, plus a unified multi-backend LLM interface that can route requests to either hosted APIs or local CLI tools.

## The Agentic Question

While NovelWriter doesn't use an LLM to make autonomous decisions (the modern definition of "agentic"), it demonstrates several sophisticated automation patterns that align with agent-oriented architecture principles. Rather than unpredictable LLM decision-making, it uses **programmatic orchestration** with deterministic workflows—a pragmatic approach for creative writing where you want reliable automation with human oversight.

## Overview of Agentic Features

### 1. Multi-Agent Architecture

The app implements a specialized agent system with distinct roles:

* StoryGenerationOrchestrator - Coordinates the entire workflow across multiple phases
* QualityControlAgent - Evaluates content quality (coherence, pacing, prose)
* ConsistencyAgent - Maintains character and world-building consistency
* ReviewAndRetryAgent - Analyzes content and applies retry logic
* ChapterWritingAgent - Automates chapter writing with multi-level reviews

Each agent has:

* Specific jobs with clear success criteria
* Purpose-built tools (not generic APIs)
* Tool selection capabilities (agents decide which tools to use)
* Communication protocols (AgentMessage, AgentResult)


#### System Architecture Overview

The diagram below shows how NovelWriter's agent system coordinates the novel writing process.

```
┌─────────────────────────────────────────┐
│      GUI (Tkinter Interface)            │
│   Parameters | Lore | Structure | etc.  │
└──────────────────┬──────────────────────┘
                   │
     ┌─────────────▼───────────────┐
     │ StoryGenerationOrchestrator │
     └──┬────────┬────────┬─────┬──┘
        │        │        │     │
   ┌────▼───┐ ┌──▼────┐ ┌─▼──┐ ┌▼──────────┐
   │Quality │ │Consis-│ │Rev-│ │Chapter    │
   │Agent   │ │tency  │ │iew │ │Writing    │
   │        │ │Agent  │ │Ag. │ │Agent      │
   └────┬───┘ └───┬───┘ └─┬──┘ └─────┬─────┘
        │         │       │          │
        └─────────┴───────┴──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Tool Registry      │
        │  • AnalyzeCoherence  │
        │  • AnalyzePacing     │
        │  • ValidateConsis... │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Checkpoint State Mgr │
        │ (Persistent Storage) │
        └──────────────────────┘
```

### 2. Workflow Orchestration
The orchestrator manages a complete automated pipeline:

```
Lore Generation → Story Structure → Scene Planning → Chapter Writing
```

Key orchestration features:

* Dependency management - Ensures steps execute in proper order
* Checkpoint system - Saves progress and allows resuming
* State persistence - Tracks workflow status across sessions
* Step validation - Verifies each phase before proceeding


### 3. Checkpoint & State Management
A sophisticated workflow state system (CheckpointStateManager):

* Persistent checkpoints - Save workflow state to JSON
* Progress tracking - Monitor completion of each phase
* File scanning - Automatically detect generated outputs
* Resume capability - Pick up where you left off
* Retry logic - Reset and retry failed steps

Status tracking includes: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `SKIPPED`


### 4. Quality Control System
Multi-level review with automated quality analysis:

* Scene-level reviews - Quality, word count, issues, strengths
* Chapter-level reviews - Coherence, pacing, character development
* Batch-level reviews - Consistency, progression, style
* Quality metrics - Numerical scoring (coherence, consistency, pacing, prose)
* Trend tracking - Monitor quality over time
* Automated retry - Regenerate content below quality thresholds


### 5. Tool Registry System
A discoverable tool system where agents can:

* Register specialized tools (e.g. AnalyzeCoherenceTool, AnalyzePacingTool)
* Select appropriate tools based on context
* Execute tools with validated parameters
* Synthesize results from multiple tools


### 6. Decision-Making Capabilities
While not using an LLM for decisions, the system makes **programmatic autonomous choices**:

* **Tool selection** - Conditional logic determines which analysis tools to apply based on content type and context
* **Quality assessment** - Automatically determines if content meets standards using numerical thresholds
* **Workflow routing** - Decides next steps based on current state (skip completed steps, retry failed ones)
* **Error recovery** - Handles failures with fallback strategies and configurable retry limits


### 7. Feedback Loops
Iterative improvement through:

* Quality evaluation → Recommendations → Content improvement
* Consistency checking → Validation → Correction
* Multi-pass refinement with configurable thresholds


### 8. User Approval Checkpoints
Human-in-the-loop capabilities:

* Pause workflow for user review
* Display checkpoint messages with progress
* Wait for approval before continuing
* Support manual retry of steps


### 9. Automation Features
The "Automation" tab provides:

* One-click complete story generation
* Automated execution of all workflow steps
* Progress monitoring and status updates
* Quality dashboards with detailed metrics


### 10. Modular & Extensible Design
Following agentic principles:

* Separation of concerns - GUI vs. agentic layer
* Clean interfaces - Well-defined APIs between components
* Testable outcomes - Clear metrics for performance
* Backward compatibility - Agentic features are opt-in


## How It Relates to Modern Agentic Systems

While NovelWriter doesn't use an LLM to make autonomous decisions about what to do, it shares these agentic characteristics:

* ✅ **Specialized agents** with specific jobs
* ✅ **Tool-based architecture** (agents use purpose-built tools)
* ✅ **Workflow orchestration** (coordinating multiple agents)
* ✅ **State management** (tracking progress and context)
* ✅ **Quality control** (automated evaluation and improvement)
* ✅ **Feedback loops** (iterative refinement)
* ✅ **Decision points** (automated routing based on conditions)

### The Key Difference

The main difference is that the **decision-making logic is programmatic** rather than LLM-driven. It's more like a sophisticated automation framework with agent-like patterns, rather than a fully autonomous agentic system.

This is actually a **pragmatic approach** for creative writing, where you want deterministic, reliable automation with human oversight, rather than unpredictable LLM decision-making that might take the story in unwanted directions!

## Try It Yourself

Interested in exploring NovelWriter's agentic capabilities?

* **GitHub Repository**: [EdwardAThomson/NovelWriter](https://github.com/EdwardAThomson/NovelWriter)
* **Example Outputs**: See complete novels generated with the system at [NovelWriter-Examples](https://github.com/EdwardAThomson/NovelWriter-Examples)
* **Documentation**: Check out the [User Guide](user_guide.md) and [Agentic Implementation Plan](agentic_implementation.md)

The "Automation" tab in the GUI provides one-click access to the complete agentic workflow—try it with your own story ideas!
