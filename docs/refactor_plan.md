# NovelWriter Refactoring Plan

## Overview
This document outlines the refactoring plan to reorganize the NovelWriter codebase in preparation for the agentic layer implementation. The goal is to create a clean, modular structure that separates concerns and provides a solid foundation for future development.

## Current Structure Analysis

### Root Directory Files (to be moved)
```
NovelWriter/
├── main.py                 # GUI entry point
├── parameters.py           # Parameter collection UI
├── lore.py                # Lore generation UI
├── story_structure.py     # Story structure UI
├── scene_plan.py          # Scene planning UI
├── chapter_writing.py     # Chapter writing UI
├── ai_helper.py           # LLM interface
├── helper_fns.py          # Utility functions
├── logger_config.py       # Logging configuration
├── combine.py             # File combination utility
├── rag_helper.py          # RAG functionality
├── genre_configs/         # Genre configuration files
├── Generators/            # Legacy generators (keep in place)
├── current_work/          # User output directory (keep in place)
├── docs/                  # Documentation (keep in place)
└── [other files]          # Keep in place
```

## Target Structure

```
NovelWriter/
├── core/                           # Existing app code (reorganized)
│   ├── __init__.py
│   ├── gui/                        # GUI components
│   │   ├── __init__.py
│   │   ├── app.py                  # main.py renamed
│   │   ├── parameters.py
│   │   ├── lore.py
│   │   ├── story_structure.py
│   │   ├── scene_plan.py
│   │   └── chapter_writing.py
│   ├── generation/                 # AI and generation logic
│   │   ├── __init__.py
│   │   ├── ai_helper.py
│   │   ├── helper_fns.py
│   │   └── rag_helper.py
│   ├── config/                     # Configuration files
│   │   ├── __init__.py
│   │   ├── logger_config.py
│   │   └── genre_configs/          # Moved from root
│   └── utils/                      # Utilities
│       ├── __init__.py
│       └── combine.py
├── agents/                         # New agentic layer (to be created)
│   ├── __init__.py
│   ├── base/
│   ├── quality/
│   ├── consistency/
│   └── orchestration/
├── main.py                         # New entry point
├── Generators/                     # Keep in place
├── current_work/                   # Keep in place
├── docs/                          # Keep in place
├── requirements.txt               # Keep in place
├── .env                           # Keep in place
└── [other config files]           # Keep in place
```

## Refactoring Steps

### Phase 1: Create Directory Structure
1. Create `core/` directory with subdirectories
2. Create `agents/` directory with subdirectories
3. Add `__init__.py` files to all new directories

### Phase 2: Move Files
1. **GUI Components** → `core/gui/`
   - `main.py` → `core/gui/app.py`
   - `parameters.py` → `core/gui/parameters.py`
   - `lore.py` → `core/gui/lore.py`
   - `story_structure.py` → `core/gui/story_structure.py`
   - `scene_plan.py` → `core/gui/scene_plan.py`
   - `chapter_writing.py` → `core/gui/chapter_writing.py`

2. **Generation Logic** → `core/generation/`
   - `ai_helper.py` → `core/generation/ai_helper.py`
   - `helper_fns.py` → `core/generation/helper_fns.py`
   - `rag_helper.py` → `core/generation/rag_helper.py`

3. **Configuration** → `core/config/`
   - `logger_config.py` → `core/config/logger_config.py`
   - `genre_configs/` → `core/config/genre_configs/`

4. **Utilities** → `core/utils/`
   - `combine.py` → `core/utils/combine.py`

### Phase 3: Update Import Statements

#### Files to Update and Their Import Changes:

**New `main.py` (entry point):**
```python
# New file content
from core.gui.app import NovelWriterApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()
```

**`core/gui/app.py` (renamed from main.py):**
```python
# OLD imports:
from parameters import Parameters
from genre_configs import get_genre_config
from lore import Lore
from story_structure import StoryStructure
from scene_plan import ScenePlanning
from chapter_writing import ChapterWriting
from ai_helper import get_supported_models
from logger_config import setup_app_logger

# NEW imports:
from core.gui.parameters import Parameters
from core.config.genre_configs import get_genre_config
from core.gui.lore import Lore
from core.gui.story_structure import StoryStructure
from core.gui.scene_plan import ScenePlanning
from core.gui.chapter_writing import ChapterWriting
from core.generation.ai_helper import get_supported_models
from core.config.logger_config import setup_app_logger
```

**`core/gui/parameters.py`:**
```python
# OLD imports:
from genre_configs import get_genre_config, get_available_genres
from helper_fns import save_to_file, load_from_file

# NEW imports:
from core.config.genre_configs import get_genre_config, get_available_genres
from core.generation.helper_fns import save_to_file, load_from_file
```

**`core/gui/lore.py`:**
```python
# OLD imports:
from ai_helper import get_llm_response
from helper_fns import save_to_file, load_from_file
from rag_helper import create_embeddings, search_similar

# NEW imports:
from core.generation.ai_helper import get_llm_response
from core.generation.helper_fns import save_to_file, load_from_file
from core.generation.rag_helper import create_embeddings, search_similar
```

**Similar pattern for other GUI files...**

### Phase 4: Update Configuration Files

**`core/config/__init__.py`:**
```python
"""Configuration module for NovelWriter core functionality."""
```

**`core/generation/__init__.py`:**
```python
"""Generation and AI helper modules for NovelWriter."""
```

**`core/gui/__init__.py`:**
```python
"""GUI components for NovelWriter application."""
```

**`core/utils/__init__.py`:**
```python
"""Utility functions for NovelWriter."""
```

### Phase 5: Update File Paths in Code

#### Files that reference file paths:
1. **Logger configuration** - Update output directory handling
2. **Genre configs** - Update config file loading paths
3. **Helper functions** - Update any hardcoded paths
4. **Save/load functions** - Ensure relative paths still work

#### Specific Path Updates:
```python
# In logger_config.py - if it references genre_configs
# OLD: "genre_configs/science_fiction.json"
# NEW: "core/config/genre_configs/science_fiction.json"

# In any file loading genre configs
# OLD: os.path.join("genre_configs", f"{genre}.json")
# NEW: os.path.join("core", "config", "genre_configs", f"{genre}.json")
```

## Testing Strategy

### Phase 1 Testing: Structure Creation
- Verify all directories are created correctly
- Confirm `__init__.py` files are in place
- Check that original files are still accessible

### Phase 2 Testing: File Movement
- Verify all files moved to correct locations
- Confirm no files were lost or duplicated
- Check that original functionality paths are preserved

### Phase 3 Testing: Import Updates
- Test each module can be imported correctly
- Verify no circular import issues
- Confirm all dependencies resolve

### Phase 4 Testing: Full Application
- Run the application from new `main.py`
- Test each GUI tab functionality
- Verify file I/O operations work correctly
- Confirm logging and configuration loading

## Rollback Plan

### If Issues Arise:
1. **Git Reset**: Use git to revert to pre-refactor state
2. **Manual Rollback**: 
   - Move files back to original locations
   - Restore original import statements
   - Remove new directory structure

### Backup Strategy:
- Commit current state before starting refactor
- Create backup branch: `git checkout -b pre-refactor-backup`
- Perform refactor on main branch
- Keep backup branch until refactor is confirmed stable

## Success Criteria

### Functional Requirements:
- [ ] Application starts successfully from new `main.py`
- [ ] All GUI tabs load and function correctly
- [ ] Parameter collection works
- [ ] Lore generation works
- [ ] Story structure generation works
- [ ] Scene planning works
- [ ] Chapter writing works
- [ ] File save/load operations work
- [ ] Logging functions correctly

### Code Quality Requirements:
- [ ] No circular imports
- [ ] Clean import statements
- [ ] Proper package structure
- [ ] All `__init__.py` files in place
- [ ] No hardcoded paths that break

### Preparation for Agents:
- [ ] Clear separation between core and future agents
- [ ] Easy import path for agents to use core functionality
- [ ] Modular structure ready for extension

## Post-Refactor Tasks

1. **Update Documentation**: 
   - Update README.md with new structure
   - Update any developer documentation
   - Update import examples in docs

2. **Update CI/CD**: 
   - Update any build scripts
   - Update test paths if applicable
   - Update deployment scripts

3. **Prepare for Agents**:
   - Create initial agent directory structure
   - Plan agent-to-core integration points
   - Design clean API boundaries

## Notes

- This refactor maintains backward compatibility for user data
- All user-facing functionality remains identical
- File output locations (`current_work/`) remain unchanged
- Configuration and genre files maintain same format
- No changes to external dependencies or requirements

## Refactor Completion Status

### ✅ COMPLETED - August 4, 2025

**Summary**: The refactoring has been successfully completed! All files have been moved to their new locations and import statements have been updated.

**Verification**: 
- All imports work correctly
- Application structure is clean and modular
- Ready for agentic layer implementation

**Files Successfully Moved**:
- ✅ `main.py` → `core/gui/app.py` (with new entry point `main.py`)
- ✅ GUI components → `core/gui/`
- ✅ Generation logic → `core/generation/`
- ✅ Configuration → `core/config/`
- ✅ Utilities → `core/utils/`

**Import Updates Completed**:
- ✅ All GUI files updated
- ✅ All cross-references fixed
- ✅ Package structure established

**Testing Results**:
- ✅ All imports successful
- ✅ No circular dependencies
- ✅ Clean package structure

**Next Steps**: Ready to begin Phase 1 of agentic implementation (Quality Control Agent)

---

*Refactoring completed successfully. Document preserved for reference.*
