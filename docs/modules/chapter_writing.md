# Chapter Writing Module (`chapter_writing.py`)

This module is responsible for the final stage of story generation: converting detailed scene plans into narrative prose. It manages the "Write Chapters" tab in the user interface and handles the generation of both individual chapters for long-form stories and complete prose for short stories.

## `ChapterWritingUI` Class

The `ChapterWritingUI` class orchestrates the user interactions and logic for this tab.

### Key UI Elements

-   **Chapter Number Entry**: A text field where users input the specific chapter number they wish to generate (visible only for Novella, Novel, and Epic story lengths).
-   **Write Button**: This button's text and function adapt based on the selected "Story Length":
    -   For "Short Story": Reads "Write Short Story".
    -   For longer forms: Reads "Write Chapter".
-   **Re-Write Button**: Intended for rewriting an existing chapter. (Currently, its visibility and full functionality might be under development or refinement).

### Core Methods

1.  **`__init__(self, parent, app)`**
    *   Initializes the UI elements for the "Write Chapters" tab, including labels, entry fields, and buttons.
    *   Registers `_update_ui_based_on_parameters` as a callback with the `Parameters` to dynamically adjust the UI when story parameters change.

2.  **`_update_ui_based_on_parameters(self)`**
    *   This method is called automatically when story parameters (like "Story Length") are modified in the "Novel Parameters" tab.
    *   It adjusts the visibility and text of UI elements:
        *   If "Story Length" is "Short Story", it hides the chapter number entry and label, and sets the main button text to "Write Short Story". The "Re-Write" button is also hidden.
        *   For longer forms ("Novella", "Novel (Standard)", "Novel (Epic)"), it ensures the chapter number entry and label are visible, sets the button text to "Write Chapter", and currently hides the "Re-Write" button.

3.  **`_dispatch_prose_generation(self)`**
    *   This method is triggered when the user clicks the main "Write" button.
    *   It reads the current "Story Length" from the parameters.
    *   Based on the story length, it calls either:
        *   `_write_short_story_prose()` if it's a "Short Story".
        *   `write_chapter()` if it's a longer form.

4.  **`_write_short_story_prose(self)`**
    *   **Purpose**: Generates the complete narrative prose for a short story, scene by scene.
    *   **Inputs**:
        *   Reads `parameters.txt` for `novel_title` and `story_structure`.
        *   The primary input is the short story's scene plan file (e.g., `scenes_short_story_[structure_name].md`) located in the main output directory.
        *   Loads `generated_lore.md` for universe context.
        *   Loads `characters.json` to create a detailed character roster summary.
        *   Loads `factions.json` to create a faction summary.
    *   **Process**:
        1.  Parses the scene plan file to identify individual scene descriptions. It looks for headings like `## Scene X: Title` or `### Scene X: Title`.
        2.  For each parsed scene:
            *   Constructs a detailed prompt for the LLM. This prompt includes:
                *   The specific scene description.
                *   The novel title (if set).
                *   The selected story structure.
                *   The full content of `generated_lore.md`.
                *   The generated character roster summary (name, role, key traits, backstory snippet).
                *   The generated faction summary (name, profile, traits for top factions).
                *   Specific instructions to write engaging prose for *only that scene*, adhere to lore, and maintain character consistency.
            *   Saves the prompt to a log file (e.g., `short_story_scene_X_prompt.md`).
            *   Sends the prompt to the selected LLM (via `ai_helper.send_prompt`).
            *   Collects the LLM's response (the prose for that scene).
        3.  Concatenates the prose from all scenes, separated by `\n\n---\n\n`.
    *   **Output**:
        *   Saves the complete short story prose to a single Markdown file in the main output directory (e.g., `prose_short_story_[safe_title].md`).
        *   Shows a success or error message to the user.

5.  **`write_chapter(self)`**
    *   **Purpose**: Generates the narrative prose for a single, specified chapter in a long-form work.
    *   **Inputs**:
        *   The `target_chapter_number_global` entered by the user.
        *   Reads `parameters.txt` for `Story Structure` and `Story Length`.
        *   Uses `STRUCTURE_SECTIONS_MAP` (from `parameters.py`) and chapter outline files (e.g., `chapter_outlines_[structure]_[section].md`) to determine which major section the target chapter belongs to.
        *   The primary input is the detailed scene plan for the specific target chapter, located in the `detailed_scene_plans/` subdirectory (e.g., `detailed_scene_plans/scenes_[structure]_[section]_ch[GlobalChapterNumber].md`).
        *   Loads `generated_lore.md`.
        *   Loads `characters.json` for a character roster summary.
        *   Loads `factions.json` for a faction summary.
    *   **Process**:
        1.  Determines the story section corresponding to the `target_chapter_number_global` by examining chapter counts in the various `chapter_outlines_...md` files.
        2.  Constructs the path to and loads the specific scene plan file for the target chapter from the `detailed_scene_plans` subdirectory.
        3.  Parses this chapter-specific scene plan file to identify individual scene descriptions (looking for `## Scene X: ...` headings).
        4.  For each parsed scene within the chapter:
            *   Constructs a detailed prompt for the LLM, very similar in structure and content to the one used in `_write_short_story_prose` (including the scene plan, full lore, character roster, faction summary, and writing instructions for that single scene).
            *   Saves the prompt to a log file (e.g., `write_chapter_[num]_scene_[idx]_prompt.md`).
            *   Sends the prompt to the selected LLM.
            *   Collects the LLM's response.
        5.  Concatenates the prose from all scenes of the chapter.
    *   **Output**:
        *   Saves the generated chapter prose to a Markdown file in the `chapters/` subdirectory (e.g., `chapters/chapter_[target_chapter_number_global].md`).
        *   Shows a success or error message.

6.  **`rewrite_chapter(self)`**
    *   **Purpose**: Allows the user to take an existing, previously written chapter and have the LLM rewrite it, typically to expand or improve it.
    *   **Inputs**:
        *   The chapter number entered by the user.
        *   The existing chapter file from the `chapters/` subdirectory (e.g., `chapters/chapter_[num].md`).
        *   Currently reads `parameters.txt` for general story parameters.
    *   **Process**:
        1.  Reads the content of the specified chapter file.
        2.  Constructs a prompt that includes:
            *   The existing chapter text.
            *   Instructions to the LLM to rewrite and expand the chapter, focusing on missing elements like descriptions, dialogue, character thoughts, etc.
            *   The general story parameters from `parameters.txt`.
            *   *(Note: This prompt currently does not include the detailed lore, character roster, or faction summaries that the primary writing functions use, which might be an area for future enhancement for consistency.)*
        3.  Sends the prompt to the selected LLM.
    *   **Output**:
        *   Saves the rewritten chapter prose to a new file in the `chapters/` subdirectory, typically prefixed (e.g., `chapters/re_chapter_[num].md`).

## File Interactions

The `chapter_writing.py` module interacts with several files:

**Input Files (Read):**

*   `parameters.txt`: To get `novel_title`, `story_structure`, `story_length`.
*   `generated_lore.md`: For full universe context.
*   `characters.json`: To build a summarized character roster for prompts.
*   `factions.json`: To build a summarized faction overview for prompts.
*   **For Short Stories**: `scenes_short_story_[structure_name].md` (from the main output directory).
*   **For Long-Form Chapters**:
    *   `chapter_outlines_[structure]_[section].md` files: To determine chapter distribution across sections and locate the target chapter.
    *   `detailed_scene_plans/scenes_[structure]_[section]_ch[GlobalChapterNumber].md`: The specific scene plan for the target chapter.
*   **For Rewriting**: `chapters/chapter_[num].md`: The existing chapter to be rewritten.

**Output Files (Write):**

*   **For Short Stories**: `prose_short_story_[safe_title].md` (to the main output directory).
*   **For Long-Form Chapters**: `chapters/chapter_[num].md` (to the `chapters/` subdirectory).
*   **For Rewritten Chapters**: `chapters/re_chapter_[num].md` (to the `chapters/` subdirectory).
*   Prompt log files (e.g., `short_story_scene_X_prompt.md`, `write_chapter_Y_scene_Z_prompt.md`) are saved to the main output directory for debugging and review. 