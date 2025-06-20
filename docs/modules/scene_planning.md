# Scene Planning Module (`scene_plan.py`)

This module, primarily managed by the `ScenePlanning` class, is responsible for the "Scene Planning" tab. It takes the detailed plot outlines generated by the Story Structure module and refines them further, first into chapter outlines (for long-form works) and then into specific, actionable scene descriptions that will be used for prose generation.

## `ScenePlanning` Class

The `ScenePlanning` class provides the user interface for these planning stages and orchestrates the LLM calls needed to break down plots into chapters and scenes.

### Key UI Elements

*   **"Generate Chapter Outlines" Button** (`chapter_outline_button`):
    *   Triggers the `generate_chapter_outline()` method.
    *   This button is only visible when a long-form story length (Novella, Novel, Epic) is selected in the Parameters tab.
*   **"Plan Scenes" Button** (`plan_scenes_button`):
    *   Triggers the `_dispatch_scene_planning()` method.
    *   The user-facing text of this button is generally static ("Plan Scenes"), but its underlying action changes based on the selected story length.

### Core Methods

1.  **`__init__(self, parent, app)`**:
    *   Sets up the UI elements for the "Scene Planning" tab.
    *   Registers `_update_ui_based_on_parameters` as a callback with `Parameters` to dynamically adjust UI visibility based on story length.

2.  **`_update_ui_based_on_parameters(self)`**:
    *   Called when parameters (especially "Story Length") change.
    *   If story length is "Short Story", it hides the "Generate Chapter Outlines" button.
    *   For longer forms, it ensures the "Generate Chapter Outlines" button is visible (packed before the "Plan Scenes" button).

3.  **`_dispatch_scene_planning(self)`**:
    *   Triggered by the "Plan Scenes" button.
    *   Reads the "Story Length" from `Parameters`.
    *   Calls `_plan_short_story_scenes()` if the length is "Short Story".
    *   Calls `_plan_long_form_scenes()` if the length is "Novella", "Novel (Standard)", or "Novel (Epic)".

4.  **`generate_chapter_outline(self)`** (For long-form works: Novella, Novel, Epic):
    *   **Purpose**: To generate a chapter-by-chapter outline for each major section/act of a long-form story.
    *   **Inputs**:
        *   `parameters.txt`: For the selected `Story Structure` (e.g., "6-Act Structure").
        *   Detailed plot files for each section/act of the chosen structure (e.g., `6-act_structure_beginning.md`, `6-act_structure_rising_action.md`), which are outputs from the Story Structure module.
        *   `STRUCTURE_SECTIONS_MAP` (from `parameters.py`): To identify the sequence of sections for the selected structure.
    *   **Process**:
        1.  Iterates through each `current_section_name` defined in `STRUCTURE_SECTIONS_MAP` for the selected structure.
        2.  For each section, it loads the corresponding detailed plot file (e.g., `output_dir/6-act_structure_beginning.md`).
        3.  Constructs a prompt for the LLM asking it to generate a chapter-by-chapter outline *specifically for that current section*. The prompt includes:
            *   The detailed plot content of the current section.
            *   The overall story structure framework name and its parts.
            *   Instructions to suggest scenes within each chapter, list characters, factions, locations, and to assign chapter numbers sequentially, starting from a running `chapter_number_offset` (which ensures unique chapter numbers across the entire story).
        4.  Sends the prompt to the selected LLM.
        5.  The LLM response, which is the chapter outline for that section, is saved to a corresponding file (e.g., `output_dir/chapter_outlines_6-act_structure_beginning.md`).
        6.  The `chapter_number_offset` is updated based on the number of chapters generated for the current section.
    *   **Output**: A set of Markdown files, one for each section of the story structure, containing chapter outlines (e.g., `chapter_outlines_[structure]_[section].md`).

5.  **`_plan_long_form_scenes(self)`** (For Novella, Novel, Epic):
    *   **Purpose**: To take the chapter outlines (generated by `generate_chapter_outline`) and create detailed scene-by-scene plans for every chapter in the story.
    *   **Inputs**:
        *   `parameters.txt`: For `Story Structure` and `Story Length`.
        *   `generated_lore.md`: For overall universe context.
        *   `chapter_outlines_[structure]_[section].md` files: One for each section of the story.
        *   `STRUCTURE_SECTIONS_MAP` (from `parameters.py`).
    *   **Process**:
        1.  Maintains an `overall_chapter_number` counter, starting at 1.
        2.  Iterates through each `current_section_name` of the selected story structure.
        3.  Loads the corresponding `chapter_outlines_[structure]_[section].md` file.
        4.  Parses this file to identify the chapters within that section's outline.
        5.  For each chapter identified in the section's outline (using the `overall_chapter_number` for identification in prompts and output filenames):
            *   Constructs a prompt for the LLM asking it to sketch out detailed scenes *for that specific chapter*.
            *   The prompt includes:
                *   The content of the entire `section_chapter_outline_content` (the outline for the current major section).
                *   The `overall_chapter_number` to focus on.
                *   The `current_section_name` for context.
                *   The `story_length` (with a specific instruction for "Novella" to aim for conciseness).
                *   The `generated_lore.md`.
                *   Instructions to describe setting, characters, key actions/events, dialogue snippets, and plot/character advancement for each scene.
            *   Saves this prompt to `prompts/plan_scenes_ch[overall_chapter_number]_[structure]_[section]_prompt.md`.
            *   Sends the prompt to the LLM.
        6.  The LLM response (detailed scenes for that chapter) is saved into the `detailed_scene_plans/` subdirectory, with a filename like `scenes_[structure]_[section]_ch[overall_chapter_number].md`.
        7.  Increments `overall_chapter_number` for each chapter processed.
    *   **Output**: A collection of Markdown files in the `detailed_scene_plans/` subdirectory, each containing the scene breakdown for a single chapter of the long-form work.

6.  **`_plan_short_story_scenes(self)`**:
    *   **Purpose**: To generate a detailed scene-by-scene plan for an entire short story.
    *   **Inputs**:
        *   `parameters.txt`: For `story_structure` and `novel_title`.
        *   The detailed plot outline for the entire short story (e.g., `plot_short_story_[structure_name].md`), generated by the Story Structure module.
        *   `generated_lore.md` (optional, for context).
    *   **Process**:
        1.  Loads the short story's overall detailed plot.
        2.  Constructs a prompt for the LLM asking it to break down this plot into a sequence of distinct scenes.
        3.  The prompt instructs the LLM to describe for each scene: scene number, setting, characters, key actions/events, dialogue, and how it advances the plot/themes, ensuring logical flow.
        4.  Includes `generated_lore.md` as additional context.
        5.  Saves the prompt to `prompts/plan_scenes_short_story_[structure_name]_prompt.md`.
        6.  Sends the prompt to the LLM.
    *   **Output**: Saves the LLM's response (the complete scene-by-scene plan for the short story) to `scenes_short_story_[structure_name].md` in the main output directory.

### File Interactions

**Input Files (Read):**

*   `parameters.txt`: For `Story Structure`, `Story Length`, and `novel_title`.
*   Detailed plot files (outputs from `story_structure.py`):
    *   For long-form works (input to `generate_chapter_outline`): `[structure]_[section].md` files (e.g., `6-act_structure_beginning.md`).
    *   For short stories (input to `_plan_short_story_scenes`): `plot_short_story_[structure_name].md`.
*   `generated_lore.md`: Used as context for scene planning prompts.
*   Chapter outline files (outputs of `generate_chapter_outline`, inputs to `_plan_long_form_scenes`): `chapter_outlines_[structure]_[section].md`.

**Output Files (Write):**

*   **Chapter Outlines** (for long-form works): `chapter_outlines_[structure]_[section].md` (e.g., `chapter_outlines_6-act_structure_beginning.md`). One file per story section.
*   **Detailed Scene Plans**:
    *   For long-form works: `detailed_scene_plans/scenes_[structure]_[section]_ch[GlobalChapterNumber].md`. One file per chapter.
    *   For short stories: `scenes_short_story_[structure_name].md`. One file for the entire story.
*   **Prompt Log Files**: Various prompt files are saved into the `prompts/` subdirectory (e.g., `plan_scenes_ch*_prompt.md`, `plan_scenes_short_story_*_prompt.md`).

**Key Data Structure Used:**

*   Relies on `STRUCTURE_SECTIONS_MAP` from `parameters.py` to iterate through the defined sections of a story structure, particularly for long-form works. 