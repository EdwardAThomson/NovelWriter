# Lore Generation Module (`lore.py`)

This module, managed by the `Lore` class, is responsible for the "Generate Lore" tab in the application. It plays a crucial role in building the foundational elements of the story's universe, including its factions, characters, background history, and thematic elements. It relies on both local generators and LLM interactions.

## `Lore` Class

The `Lore` class handles the user interface for lore generation, orchestrates the calls to various generation functions, and manages the resulting data.

### Key UI Elements

*   **Genre/Subgenre Display**: A label at the top (`genre_label`) that dynamically shows the currently selected Genre and Subgenre from the Parameters tab.
*   **Input Fields** (within the "Story Parameters" `LabelFrame`):
    *   `num_factions_var`: `tk.StringVar` for the "Number of Factions" entry.
    *   `num_chars_var`: `tk.StringVar` for the "Number of Characters" entry.
    *   `num_locations_var`: `tk.StringVar` for the "Number of Locations" entry (e.g., Planets for Sci-Fi, Cities for Fantasy). This field's visibility and label may change based on the selected genre.
    *   `extra_param_var`: `tk.StringVar` for an additional parameter whose label (`extra_param_label`) changes based on the subgenre (e.g., "Technological Focus:" for Cyberpunk).
*   **Action Buttons**:
    *   `factions_button`: Triggers `generate_factions()`.
    *   `characters_button`: Triggers `generate_characters()`.
    *   `generate_lore_button`: Triggers `generate_lore()`, the main LLM-driven world-building function.
    *   `main_char_enh_button`: Triggers `main_character_enhancement()` to generate detailed backstories.
    *   `suggest_titles_button`: Triggers `suggest_titles()`.

### Core Methods

1.  **`__init__(self, parent, app)`**:
    *   Sets up the main frame and UI elements for the "Generate Lore" tab.
    *   Initializes `tk.StringVar`s for user inputs.
    *   Calls `update_genre_display()` and `update_extra_parameter()` for initial UI state based on parameters.

2.  **`update_genre_display(self)`**:
    *   Retrieves the current genre and subgenre from `self.app.param_ui`.
    *   Updates the `genre_label` text to reflect these selections.

3.  **`update_extra_parameter(self)`**:
    *   This method is registered as a callback with `Parameters` and is called when parameters change.
    *   It first calls `update_genre_display()`.
    *   Dynamically adjusts the UI based on the selected genre and subgenre:
        *   Updates the label and visibility of the "Number of Locations" input based on the current genre handler's requirements (e.g., some genres may not require a user-defined number of locations).
        *   Updates the label for `extra_param_label` and makes the `extra_param_frame` visible if the subgenre has a specific extra parameter (e.g., "Technological Focus:" for Cyberpunk); otherwise, hides it.

4.  **`generate_factions(self)`**:
    *   Retrieves `num_factions` from `num_factions_var`, `num_locations` from `num_locations_var` (if applicable for the genre), and `gender_bias_str` from `self.app.param_ui`.
    *   Calls the `generate_factions()` method on the current genre's handler (e.g., `self.app.genre_handler.generate_factions(num_factions, num_locations)`).
    *   The handler is responsible for generating faction data (and initial location data if applicable) and saving it (typically to `factions.json`).

5.  **`generate_characters(self)`**:
    *   Retrieves `num_chars` from `num_chars_var` and `gender_bias_str` from `self.app.param_ui`.
    *   Calls `Generators.CharacterGenerator.generate_main_characters()` which returns a list of `Character` objects.
    *   Calls `Generators.CharacterGenerator.save_characters_to_file()` to serialize these objects and save them as `characters.json` in the output directory.

6.  **`generate_lore(self)`**:
    *   This is a major LLM-driven function for comprehensive world-building.
    *   **Process**:
        1.  Loads basic story parameters from `parameters.txt`.
        2.  Loads character data from `characters.json` (extracting names and roles for summaries, and later full details).
        3.  Loads faction data from `factions.json`.
        4.  Constructs a multi-part prompt for the LLM:
            *   Initial instructions for generating foundational lore.
            *   Story parameters loaded.
            *   Summaries of characters and factions.
            *   Detailed information about key faction locations, retrieved via `self.app.genre_handler.get_location_info_from_factions(factions_data)`. The specifics of this information (e.g., capital planets for Sci-Fi, main cities for Fantasy) depend on the genre.
            *   Detailed information for each character (sorted by role: protagonist, deuteragonist, antagonist first), including gender, age, title, occupation, faction, homeworld, traits, and family details.
            *   Final instructions emphasizing consistency and not generating a story title.
        5.  Saves this comprehensive prompt to `prompts/main_lore_prompt.md` in the output directory.
        6.  Sends the prompt to the selected LLM (via `ai_helper.send_prompt`).
        7.  Saves the LLM's response (the generated world lore) to `generated_lore.md` in the output directory.

7.  **`suggest_titles(self)`**:
    *   Aims to generate potential story titles using the LLM.
    *   **Process**:
        1.  Loads the full content of `generated_lore.md`.
        2.  Loads `parameters.txt` to get context like genre, subgenre, and themes.
        3.  Constructs a prompt asking the LLM to suggest 5-10 titles based on the provided lore and themes, requesting a simple numbered list format.
        4.  Saves this prompt to `prompts/title_suggestion_prompt.md`.
        5.  Sends the prompt to the LLM.
        6.  Saves the LLM's response (the list of suggested titles) to `suggested_titles.md`.

8.  **`main_character_enhancement(self)`**:
    *   Focuses on generating detailed backstories for main characters (Protagonist, Deuteragonist, Antagonist) using the LLM.
    *   **Process**:
        1.  Loads `generated_lore.md` for overall universe context.
        2.  Loads character data from `characters.json`.
        3.  Identifies and sorts main characters based on their roles.
        4.  Iterates through each main character:
            *   Constructs a specific prompt for that character's backstory. This prompt includes:
                *   Instructions to generate a detailed backstory (family, upbringing, life events).
                *   The overall universe lore (`generated_lore.md`).
                *   The specific details of the current character (age, gender, family, goals, etc.).
                *   Any backstories already generated for *other* main characters in previous iterations of this loop (to provide context and encourage consistency or complementary narratives).
            *   Saves this character-specific prompt to `prompts/background_[role]_[name]_prompt.md`.
            *   Sends the prompt to the LLM.
            *   Saves the LLM's response (the backstory) to a dedicated file: `background_[role]_[name].md` in the output directory.
            *   Stores the generated backstory to be included as context for subsequent characters in the loop.

### File Interactions

The `lore.py` module reads from and writes to several files, all within the user-defined output directory:

**Input Files (Read):**

*   `parameters.txt`: Accessed via `self.app.param_ui.get_current_parameters()` for gender bias and subgenre (for UI updates), and read directly by `generate_lore()` and `suggest_titles()` for detailed parameters.
*   `characters.json`: Read by `generate_lore()` and `main_character_enhancement()` to get character details.
*   `factions.json`: Read by `generate_lore()` to get faction details.
*   `generated_lore.md`: Read by `suggest_titles()` and `main_character_enhancement()` as context.

**Output Files (Write):**

*   `factions.json`: Created by `generate_factions()`.
*   `characters.json`: Created by `generate_characters()`.
*   `generated_lore.md`: Created by `generate_lore()`.
*   `suggested_titles.md`: Created by `suggest_titles()`.
*   `background_[role]_[name].md`: Multiple files, one for each main character's backstory, created by `main_character_enhancement()`.
*   **Prompt Log Files**: Various prompt files are saved into a `prompts/` subdirectory within the main output directory, for example:
    *   `prompts/main_lore_prompt.md`
    *   `prompts/title_suggestion_prompt.md`
    *   `prompts/background_[role]_[name]_prompt.md` (for each main character)

**External Module Usage:**

*   Uses helper functions from `helper_fns.py` (e.g., `open_file`, `write_file`, `read_json`, `write_json`, `save_prompt_to_file`).
*   Uses `ai_helper.send_prompt` for all LLM communications.
*   Utilizes the current genre's handler (obtained via `self.app.genre_handler`, an instance of a class from `Generators/GenreHandlers/`) for genre-specific faction and initial location generation.
*   Utilizes `Generators.CharacterGenerator` (specifically `generate_main_characters`, `save_characters_to_file`) for non-LLM initial character generation. 