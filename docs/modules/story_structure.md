# Story Structure Module (`story_structure.py`)

This module, managed by the `StoryStructure` class, is responsible for the "Story Structure" tab. It guides the process of developing the narrative backbone, starting from individual character and faction arcs, reconciling them, and then expanding them into detailed plot outlines tailored to the selected story length and structure (e.g., 6-Act Structure, Freytag's Pyramid).

## `StoryStructure` Class

The `StoryStructure` class handles the UI for this tab and orchestrates the multi-step process of plot generation through LLM interactions.

### Key UI Elements

The UI primarily consists of several buttons that trigger sequential generation steps:

*   **"Generate Character Arcs" Button**: Calls `generate_arcs()`.
*   **"Generate Faction Arcs" Button**: Calls `generate_faction_arcs()`. This method internally performs two steps: first generating faction-specific arcs and then reconciling them with the previously generated character arcs.
*   **"Add Planets to Arcs" Button**: Calls `add_planets_to_arcs()` to integrate location details into the reconciled arcs.
*   **Main Plot Generation Button** (`detailed_plot_button`):
    *   The text of this button is dynamic, changing based on the "Story Length" selected in the Parameters tab (e.g., "Outline Short Story Plot", "Create Detailed Act/Section Plots"). This is managed by `_update_detailed_plot_button_text()`.
    *   Its command is `_dispatch_detailed_plot_creation()`, which routes to the appropriate detailed plotting method.

### Core Methods

1.  **`__init__(self, parent, app)`**:
    *   Sets up the UI elements (labels and buttons) for the "Story Structure" tab.
    *   Registers `_update_detailed_plot_button_text` as a callback with `Parameters` to dynamically update the main plot button's text when story parameters change.

2.  **`_update_detailed_plot_button_text(self)`**:
    *   Called when parameters change (especially "Story Length").
    *   Updates the text of the `detailed_plot_button` to be contextually appropriate (e.g., "Outline Short Story Plot" for short stories, "Create Detailed Act/Section Plots" for novels).

3.  **`_dispatch_detailed_plot_creation(self)`**:
    *   Triggered by the `detailed_plot_button`.
    *   Reads the current "Story Length" from `Parameters`.
    *   Calls `_outline_short_story_plot()` if the length is "Short Story".
    *   Calls `improve_structure()` if the length is "Novella", "Novel (Standard)", or "Novel (Epic)".

4.  **`generate_arcs(self)`**:
    *   **Purpose**: Generates narrative arcs for the main characters.
    *   **Inputs**:
        *   `characters.json`: To identify main characters (protagonist, deuteragonist, antagonist) by role and to build a general character roster for context.
        *   Individual backstory files for main characters (e.g., `background_protagonist_mia_stone.md`, `background_antagonist_general_vex.md`).
        *   `generated_lore.md`: For overall universe context.
    *   **Process**:
        1.  Constructs a prompt asking the LLM to generate compelling character arcs for the identified main roles, based on their detailed backstories, the overall lore, and the character roster.
        2.  Saves this prompt to `prompts/character_arc_prompt.md`.
        3.  Sends the prompt to the selected LLM.
    *   **Output**: Saves the LLM's response to `character_arcs.md`.

5.  **`generate_faction_arcs(self)`**:
    *   **Purpose**: Generates story arcs for major factions and then reconciles them with character arcs.
    *   **Inputs**:
        *   `parameters.txt`: For the selected `Story Structure` framework.
        *   `character_arcs.md`: Previously generated character arcs.
        *   `factions.json`: To identify major factions and their profiles (typically top 5 by military strength).
        *   `generated_lore.md`: For universe context.
    *   **Process (Two LLM Calls)**:
        1.  **Generate Faction Arcs**: 
            *   Constructs a prompt asking the LLM to generate story arcs for the major factions using the selected `Story Structure` (e.g., 6-Act Structure), based on faction profiles, lore, and the existing character arcs.
            *   Saves this prompt to `prompts/faction_arc_generation_prompt.md`.
            *   The LLM response (raw faction arcs) is saved to `faction_arcs.md`.
        2.  **Reconcile Character and Faction Arcs**: 
            *   Constructs a new prompt containing both the original `character_arcs.md` content and the newly generated `faction_arcs.md` content.
            *   Asks the LLM to weave these into a single, unified story arc, again using the selected `Story Structure` framework, showing how character and faction actions influence each other.
            *   Saves this prompt to `prompts/arc_reconciliation_prompt.md`.
    *   **Output**: Saves the LLM's response (the unified arc) to `reconciled_arcs.md`.

6.  **`add_planets_to_arcs(self)`**:
    *   **Purpose**: Integrates specific planetary locations into the reconciled story arc.
    *   **Inputs**:
        *   `reconciled_arcs.md`: The unified character and faction arcs.
        *   `factions.json`: To extract a list of key planets and their controlling factions.
    *   **Process**:
        1.  Constructs a prompt asking the LLM to rewrite the `reconciled_arcs.md`, weaving in appropriate planet locations from the extracted list, ensuring logical alignment with faction control.
        2.  Saves this prompt to `prompts/add_planets_to_arcs_prompt.md`.
    *   **Output**: Saves the LLM's response (arc with locations) to `reconciled_planets_arcs.md`.

7.  **`improve_structure(self)`** (for Novella, Novel, Epic):
    *   **Purpose**: To take the high-level `reconciled_planets_arcs.md` and generate more detailed plot summaries for each major act or section of the chosen story structure.
    *   **Inputs**:
        *   `parameters.txt`: For the selected `Story Structure` (e.g., "6-Act Structure") and `Story Length`.
        *   `reconciled_planets_arcs.md`: The overall story arc with locations.
        *   `STRUCTURE_SECTIONS_MAP` (from `parameters.py`): To get the list of sections/acts for the chosen structure (e.g., "Beginning", "Rising Action", ... for 6-Act Structure).
    *   **Process**:
        1.  Iterates through each section/act defined in `STRUCTURE_SECTIONS_MAP` for the selected structure.
        2.  In each iteration:
            *   Constructs a prompt asking the LLM to provide a detailed summary for the *current section/act*.
            *   The prompt includes the full `reconciled_planets_arcs.md` as overall context.
            *   Crucially, it also includes the detailed summary generated for the *immediately preceding section/act* (from the previous iteration) to ensure logical flow and continuity.
            *   A specific instruction is added if the `Story Length` is "Novella" to aim for conciseness appropriate for that length.
            *   Saves this prompt to `prompts/improve_structure_[structure_name]_[section_name]_prompt.md`.
            *   Sends the prompt to the LLM.
    *   **Output**: For each section/act, saves the LLM's detailed summary to a separate Markdown file named according to the structure and section (e.g., `6-act_structure_beginning.md`, `6-act_structure_rising_action.md`). These files serve as input for the Scene Planning stage.

8.  **`_outline_short_story_plot(self)`**:
    *   **Purpose**: To generate a single, comprehensive, detailed plot outline for an entire short story.
    *   **Inputs**:
        *   `parameters.txt`: For the selected `Story Structure`, `novel_title`.
        *   `STRUCTURE_SECTIONS_MAP` (from `parameters.py`): To get the stages of the selected structure.
        *   Contextual files (loaded if available):
            *   `generated_lore.md`
            *   `reconciled_planets_arcs.md` (though its relevance for a short story might be less direct than for novels, it can provide thematic context).
            *   `characters.json` (for a brief summary of key characters).
            *   `factions.json` (for a brief summary of key factions).
    *   **Process**:
        1.  Constructs a prompt asking the LLM to outline the detailed plot for the short story, covering all stages of the selected `Story Structure` from beginning to end.
        2.  The prompt specifies that for each stage, details about key events, character actions/development, faction involvement (if any), locations, tone, and pacing should be described.
        3.  Includes the loaded contextual information (lore, arcs, character/faction summaries).
        4.  Saves this prompt to `prompts/outline_short_story_plot_[structure_name]_prompt.md`.
    *   **Output**: Saves the LLM's response (the detailed plot) to `plot_short_story_[structure_name].md`.

### File Interactions

The `story_structure.py` module is central to plot development and interacts with numerous files:

**Input Files (Read):**

*   `parameters.txt`: For selected `Story Structure`, `Story Length`, `novel_title`.
*   `generated_lore.md`: General world context.
*   `characters.json`: For character details and roles.
*   `factions.json`: For faction details and planet associations.
*   `background_[role]_[name].md` files: Individual backstories for main characters.
*   `character_arcs.md`: Generated character progression.
*   `faction_arcs.md`: Generated faction progression (intermediate file).
*   `reconciled_arcs.md`: Unified character and faction arcs (intermediate file).
*   `reconciled_planets_arcs.md`: Unified arcs with location data; serves as the main input for `improve_structure`.

**Output Files (Write):**

*   `character_arcs.md`
*   `faction_arcs.md`
*   `reconciled_arcs.md`
*   `reconciled_planets_arcs.md`
*   **For Long-Form Works**: Individual detailed plot files for each act/section (e.g., `6-act_structure_beginning.md`, `novel_standard_6-act_structure_rising_action.md`). The exact naming convention might vary but follows `[structure]_[section].md`.
*   **For Short Stories**: `plot_short_story_[structure_name].md`.
*   **Prompt Log Files**: Numerous prompt files are saved to the `prompts/` subdirectory, corresponding to each major LLM call (e.g., `character_arc_prompt.md`, `faction_arc_generation_prompt.md`, `improve_structure_*.md`, `outline_short_story_plot_*.md`).

**Key Data Structure Used:**

*   Relies heavily on `STRUCTURE_SECTIONS_MAP` from `parameters.py` to understand the components of different story structures. 