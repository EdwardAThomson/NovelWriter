# Parameters UI Module (`parameters.py`)

This module is foundational to the Novel Writer application. It defines and manages the "Novel Parameters" tab, which is the starting point for any new story project. The parameters collected here dictate the overall direction and scope for all subsequent content generation stages.

## `Parameters` Class

The `Parameters` class is responsible for creating the user interface elements within the "Novel Parameters" tab, handling user input for these parameters, saving them to a file, and loading them back.

### Key UI Elements and `tk.StringVar`s

The UI is divided into static controls (always visible) and dynamic tabs that change based on genre/subgenre selection.

**Static Controls:**

*   **Output Directory**: An `ttk.Entry` (`output_dir_var`) paired with a "Browse..." `ttk.Button` (`browse_directory()` method) allowing users to select where all project files will be saved. Defaults to `current_work`.
*   **Genre**: A `ttk.Combobox` (`genre_var`) for selecting the primary genre (e.g., "Sci-Fi", "Fantasy").
*   **Subgenre**: A `ttk.Combobox` (`subgenre_var`) whose options are dynamically populated based on the selected Genre (via `populate_subgenres()` and `on_genre_select()`).
*   **Story Length**: A `ttk.Combobox` (`length_var`) for choosing the intended length of the work (e.g., "Short Story", "Novella").
*   **Story Structure**: A `ttk.Combobox` (`structure_var`) whose options are dynamically populated based on the selected Story Length (via `on_length_select()`).
*   **Novel Title**: A `ttk.Entry` (`title_var`) for the story's title.
*   **Author Name**: A `ttk.Entry` (`author_var`) for the author's name.
*   **Theme**: A `ttk.Entry` (`theme_var`) to define the central theme(s) of the story.
*   **Tone**: A `ttk.Entry` (`tone_var`) to set the desired tone.
*   **Gender Generation Bias**: A `ttk.Combobox` (`gender_bias_var`) allowing users to specify a bias for character gender generation (e.g., "Balanced (50F/50M)", "Mostly Male (25F/75M)").

**Dynamic Tabs:**

*   A `ttk.Notebook` widget is used to display additional settings that are specific to the chosen Genre and Subgenre.
*   These tabs and their content are created by the `update_dynamic_tabs()` method, which consults `genre_configs.py` (via `get_genre_config()`).
*   Input fields within these dynamic tabs have their values stored in `tk.StringVar`s (or `tk.BooleanVar`s) which are managed in the `self.dynamic_vars` dictionary.

### Core Data Structures/Constants

Several Python data structures defined at the module level in `parameters.py` are crucial for the UI's behavior:

*   **`LENGTH_OPTIONS`**: A list defining the selectable options for story length (e.g., `["Short Story", "Novella", ...]`).
*   **`STRUCTURE_MAP`**: A dictionary that maps each story length to a list of appropriate story structure frameworks (e.g., `{"Short Story": ["3-Act Structure", ...], ...}`).
*   **`DEFAULT_STRUCTURE`**: A dictionary specifying the default story structure to be selected for each story length.
*   **`STRUCTURE_SECTIONS_MAP`**: A vital dictionary that maps each recognized story structure name to a tuple of its constituent parts or acts (e.g., `"6-Act Structure": ("Beginning", "Rising Action", "First Climax", ...)`). This map is heavily used by other modules like `story_structure.py` (for generating detailed act plots) and `scene_plan.py` (for generating chapter outlines and determining chapter distribution).

### Key Methods

1.  **`__init__(self, parent, app)`**:
    *   Sets up the main frame and layout for the tab.
    *   Initializes all `tk.StringVar`s with default values.
    *   Calls helper methods (`create_genre_selector`, `create_core_parameters_ui`) to build the static UI components.
    *   Initializes the dynamic notebook area.
    *   Calls `populate_subgenres()` and `update_dynamic_tabs()` to set up initial dynamic content.
    *   Automatically calls `load_parameters()` to attempt loading any previously saved settings.

2.  **`create_genre_selector(self, parent_frame)` & `create_core_parameters_ui(self, parent_frame)`**:
    *   These methods are responsible for creating and arranging the labels, entry fields, and comboboxes for the static parameters within their respective parent frames.

3.  **`browse_directory(self)`**:
    *   Opens a standard OS file dialog allowing the user to select a folder for the project's output. The chosen path is set to `output_dir_var`.

4.  **Event Handlers (`on_genre_select`, `on_subgenre_select`, `on_length_select`, `on_structure_select`)**:
    *   `on_genre_select()`: Triggered when the Genre combobox changes. It calls `populate_subgenres()` and `update_dynamic_tabs()`.
    *   `on_subgenre_select()`: Triggered when the Subgenre combobox changes. It calls `update_dynamic_tabs()`.
    *   `on_length_select()`: Triggered when Story Length changes. It updates the available options in the Story Structure combobox based on `STRUCTURE_MAP` and sets a default structure using `DEFAULT_STRUCTURE`.
    *   All these handlers also call `trigger_callbacks()` to notify other application components of changes.

5.  **`populate_subgenres(self)`**:
    *   Clears and repopulates the Subgenre combobox based on the currently selected Genre. Subgenre lists are hardcoded within this method for now.

6.  **`update_dynamic_tabs(self)`**:
    *   This is a key method for UI dynamism.
    *   It first destroys any existing notebook (if present) and clears `self.dynamic_vars`.
    *   It then creates a new `ttk.Notebook`.
    *   It fetches the configuration for the current Genre and Subgenre using `get_genre_config()` (from `genre_configs.py`).
    *   Based on this configuration, it calls helper methods like `create_settings_tab`, `create_character_tab`, etc., to populate the notebook with relevant tabs and input fields.

7.  **`_create_dynamic_widget(self, parent, setting_name, value, row_num)`**:
    *   A helper used by the `create_<type>_tab` methods.
    *   Creates a label and an appropriate input widget (`ttk.Checkbutton` for booleans, `ttk.Combobox` for lists/tuples, `ttk.Entry` otherwise) for a given setting.
    *   Stores the associated `tk.Variable` in the `self.dynamic_vars` dictionary, keyed by a normalized version of `setting_name`.

8.  **`get_current_parameters(self)`**:
    *   Collects values from all `tk.StringVar`s (both static like `self.title_var` and dynamic ones from `self.dynamic_vars`).
    *   Returns a single dictionary containing all current parameter settings.

9.  **`save_parameters(self)`**:
    *   Calls `get_current_parameters()` to get all settings.
    *   Formats these parameters into a string, with each key-value pair on a new line.
    *   Writes this string to a file named `parameters.txt` located inside the directory specified by `output_dir_var`.

10. **`load_parameters(self)`**:
    *   Attempts to read `parameters.txt` (first from the `current_work` directory, then potentially from a directory specified within a loaded `parameters.txt` itself if `Output Directory` is one of the first lines).
    *   Parses the key-value pairs from the file.
    *   Sets the values of the corresponding `tk.StringVar`s in the UI.
    *   Critically, it calls `populate_subgenres()` and `update_dynamic_tabs()` *after* setting genre/subgenre to ensure the UI reflects the loaded dynamic settings correctly.
    *   Finally, calls `trigger_callbacks()`.

11. **`add_callback(self, callback)` & `trigger_callbacks(self)`**:
    *   These methods implement a simple callback system.
    *   Other UI modules (like `LoreUI`, `ChapterWritingUI`) can register callback functions using `add_callback()`.
    *   `trigger_callbacks()` is called whenever significant parameters change (e.g., after loading, or when genre/length/structure selections are modified), allowing other modules to react to these changes (e.g., by updating their own UI or internal state).

12. **`get_gender_bias_options(self)`**:
    *   Returns a predefined list of strings representing different gender bias options for character generation.

### File Interactions

*   **Primary Output**: Writes all collected parameters to `parameters.txt` in the user-specified output directory.
*   **Primary Input**: Reads `parameters.txt` from the output directory to restore settings.
*   **Configuration Source**: Relies on `genre_configs.py` (via the `get_genre_config` function) to define the structure and content of the dynamic tabs based on genre and subgenre selections.

### Interaction with Other Modules

*   **Central Data Source**: The `Parameters` class instance (via `app.param_ui`) serves as the primary source of configuration for most other modules in the application. They access settings using `app.param_ui.get_current_parameters()`.
*   **Notifications**: Through its callback mechanism, it informs other registered modules when parameters have been updated, allowing them to adapt accordingly. 