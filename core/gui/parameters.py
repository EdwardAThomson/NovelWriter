# parameters.py
# Collect parameters from the user and save them to a file
# These parameters will be used to generate the background lore
# The background lore will be used to generate the story (via AI)
# The story will be saved to a series of files

import re, json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.gui.notifications import show_success, show_error
import jsonschema
from jsonschema import validate
import os
import logging

from core.generation.ai_helper import send_prompt
from core.generation.helper_fns import write_file, write_json, load_schema, validate_json_schema
# from core.generation.rag_helper import upsert_text
from core.config.genre_configs import get_genre_config
from Generators.GenreHandlers import get_supported_genres

# --- Define Length and Structure Options ---
# Simplified for initial implementation
LENGTH_OPTIONS = ["Short Story", "Novella", "Novel (Standard)", "Novel (Epic)"]

STRUCTURE_MAP = {
    "Short Story": ["3-Act Structure", "Fichtean Curve", "Freytag's Pyramid"],
    "Novella": ["3-Act Structure", "Seven-Point Structure", "Hero's Journey (Simplified)"],
    "Novel (Standard)": ["3-Act Structure", "6-Act Structure", "Save the Cat!", "Hero's Journey"],
    "Novel (Epic)": ["6-Act Structure", "Hero's Journey", "Save the Cat!", "Episodic Structure"]
}

# Define default structures for each length
DEFAULT_STRUCTURE = {
    "Short Story": "3-Act Structure",
    "Novella": "3-Act Structure",
    "Novel (Standard)": "6-Act Structure", # Default to existing one
    "Novel (Epic)": "6-Act Structure",
}

# --- Define Sections/Parts for each Story Structure ---
# This map is used by story_structure.py (improve_structure) and scene_plan.py (generate_chapter_outline)
STRUCTURE_SECTIONS_MAP = {
    "3-Act Structure": ("Act 1: Setup", "Act 2: Confrontation", "Act 3: Resolution"),
    "6-Act Structure": ("Beginning", "Rising Action", "First Climax", "Solution Finding", "Second Climax", "Resolution"),
    "Fichtean Curve": ("Inciting Incident", "Rising Action", "Climax", "Falling Action", "Denouement"),
    "Seven-Point Structure": ("Hook", "Plot Point 1", "Pinch Point 1", "Midpoint", "Pinch Point 2", "Plot Point 2", "Resolution"),
    "Hero's Journey": (
        "The Ordinary World", "The Call to Adventure", "Refusal of the Call", "Meeting the Mentor", 
        "Crossing the Threshold", "Tests, Allies, and Enemies", "Approach to the Inmost Cave", 
        "The Ordeal", "Reward (Seizing the Sword)", "The Road Back", "The Resurrection", "Return with the Elixir"
    ),
    "Hero's Journey (Simplified)": ("Departure", "Initiation", "Return"),
    "Save the Cat!": (
        "Opening Image", "Theme Stated", "Set-up", "Catalyst", "Debate", "Break into Two", "B Story", 
        "Fun and Games", "Midpoint", "Bad Guys Close In", "All Is Lost", "Dark Night of the Soul", 
        "Break into Three", "Finale", "Final Image"
    ),
    "Episodic Structure": (
        "Episode 1: Introduction", "Episode 2: Rising Action", "Episode 3: Midpoint/Turning Point", 
        "Episode 4: Climax Actions", "Episode 5: Resolution/Lead to Next"
    ) # Example for a 5-episode arc; this might need to be more dynamic if num_episodes is user-defined
}
# ---------------------------------------------------------

# Add GENDER_BIAS_MAP at the class level or near the top
GENDER_BIAS_MAP = {
    "Balanced (50F/50M)": (50, 50),     # (female_%, male_%) - Note: Storing as (female, male) to match original Combobox order of F/M
    "Slightly Female (60F/40M)": (60, 40),
    "Mostly Female (75F/25M)": (75, 25),
    "Primarily Female (90F/10M)": (90, 10),
    "Slightly Male (40F/60M)": (40, 60),
    "Mostly Male (25F/75M)": (25, 75),
    "Primarily Male (10F/90M)": (10, 90),
    "Exclusively Female (100F/0M)": (100, 0), # Optional: Add if needed
    "Exclusively Male (0F/100M)": (0, 100)   # Optional: Add if needed
}

class Parameters:
    def __init__(self, parent, app=None): # Added app parameter
        self.parent = parent
        self.app = app # Store the app instance
        # Get logger from app if available, otherwise create a default one for this module
        self.logger = app.logger if app and hasattr(app, 'logger') else logging.getLogger(__name__)
        if not (app and hasattr(app, 'logger')):
            # If not using app's logger, configure a basic one for standalone use/testing
            # This won't log to the main app file but will show messages.
            logging.basicConfig(level=logging.INFO)
            self.logger.info("Parameters.py initialized without main app logger. Using default logger for this module.")
        
        self.current_parameters = {}
        self.callbacks = []
        
        # Initialize variables with defaults first
        self.genre_var = tk.StringVar(value="Sci-Fi")
        self.subgenre_var = tk.StringVar(value="Space Opera")
        self.length_var = tk.StringVar()
        self.structure_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.theme_var = tk.StringVar()
        self.tone_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="current_work") # Default output dir
        self.gender_bias_options = self.get_gender_bias_options() # Get options first
        self.gender_bias_var = tk.StringVar(value=self.gender_bias_options[0]) # Default to first option ("Balanced")
        # self.gender_bias_var = tk.StringVar(value="Balanced (50F/50M)") # Added for gender bias, with default

        # Dictionary to hold dynamically created tk variables for settings/chars/etc.
        self.dynamic_vars = {}

        # --- Create Main Layout Frames --- 
        # This frame holds everything and uses pack
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(expand=True, fill='both', padx=5, pady=5)

        # Frame for always-visible top selectors (Genre/Subgenre)
        top_selector_frame = ttk.Frame(self.main_frame)
        top_selector_frame.pack(side="top", fill="x", pady=(0, 5))
        self.create_genre_selector(top_selector_frame) # Create selectors inside this frame

        # Frame for always-visible core parameters (Length, Structure, Title etc.)
        core_params_frame = ttk.LabelFrame(self.main_frame, text="Core Details")
        core_params_frame.pack(side="top", fill="x", pady=5, padx=5)
        self.create_core_parameters_ui(core_params_frame) # Create core param widgets inside

        # Frame to contain the notebook for dynamic tabs
        self.notebook_container = ttk.Frame(self.main_frame)
        self.notebook_container.pack(side="top", expand=True, fill="both", pady=5)
        self.notebook = None # Notebook will be created/destroyed here

        # Frame for bottom buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(side="bottom", pady=10)

        # Add Save/Load buttons (using pack within button_frame)
        self.save_button = ttk.Button(button_frame, text="Save Parameters", command=self.save_parameters)
        self.save_button.pack(side="left", padx=5)
        self.load_button = ttk.Button(button_frame, text="Load Parameters", command=self.load_parameters)
        self.load_button.pack(side="left", padx=5)

        # --- Initial Setup --- 
        self.populate_subgenres() # Populate subgenres based on default genre
        # Create initial dynamic tabs based on default subgenre
        self.update_dynamic_tabs()
        self.load_parameters() # Load saved params, potentially overriding defaults and triggering updates

    def create_genre_selector(self, parent_frame):
        # Uses grid layout INSIDE parent_frame
        parent_frame.columnconfigure(1, weight=1)
        parent_frame.columnconfigure(3, weight=1)
        
        ttk.Label(parent_frame, text="Genre").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Get supported genres dynamically from genre handlers
        supported_genres = get_supported_genres()
        genre_dropdown = ttk.Combobox(parent_frame, textvariable=self.genre_var, values=supported_genres, state="readonly")
        genre_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(parent_frame, text="Subgenre").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.subgenre_dropdown = ttk.Combobox(parent_frame, textvariable=self.subgenre_var, state="readonly")
        self.subgenre_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        genre_dropdown.bind('<<ComboboxSelected>>', self.on_genre_select)
        self.subgenre_dropdown.bind('<<ComboboxSelected>>', self.on_subgenre_select)

    def create_core_parameters_ui(self, parent_frame):
        # Uses grid layout INSIDE parent_frame
        parent_frame.columnconfigure(1, weight=1)
        current_row = 0

        # Output Directory
        ttk.Label(parent_frame, text="Output Directory:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        dir_frame = ttk.Frame(parent_frame) # Frame to hold entry and button
        dir_frame.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        dir_frame.columnconfigure(0, weight=1) # Make entry expand

        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.grid(row=0, column=0, sticky="ew")
        self.browse_button = ttk.Button(dir_frame, text="Browse...", command=self.browse_directory)
        self.browse_button.grid(row=0, column=1, padx=(3,0))
        current_row += 1

        # Story Length
        ttk.Label(parent_frame, text="Story Length:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.length_combobox = ttk.Combobox(parent_frame, textvariable=self.length_var, values=LENGTH_OPTIONS, state="readonly")
        self.length_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        self.length_combobox.bind("<<ComboboxSelected>>", self.on_length_select)
        current_row += 1

        # Story Structure
        ttk.Label(parent_frame, text="Story Structure:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.structure_combobox = ttk.Combobox(parent_frame, textvariable=self.structure_var, state="disabled")
        self.structure_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        self.structure_combobox.bind("<<ComboboxSelected>>", self.on_structure_select)
        current_row += 1
        
        # Title, Author, Theme, Tone
        ttk.Label(parent_frame, text="Novel Title:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.title_entry = ttk.Entry(parent_frame, textvariable=self.title_var)
        self.title_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        current_row += 1
        
        ttk.Label(parent_frame, text="Author Name:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.author_entry = ttk.Entry(parent_frame, textvariable=self.author_var)
        self.author_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        current_row += 1
        
        ttk.Label(parent_frame, text="Theme:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.theme_entry = ttk.Entry(parent_frame, textvariable=self.theme_var)
        self.theme_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        current_row += 1
        
        ttk.Label(parent_frame, text="Tone:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.tone_entry = ttk.Entry(parent_frame, textvariable=self.tone_var)
        self.tone_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        current_row += 1

        # Gender Generation Bias
        ttk.Label(parent_frame, text="Gender Generation Bias:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
        self.gender_bias_combobox = ttk.Combobox(parent_frame, textvariable=self.gender_bias_var, values=self.gender_bias_options, state="readonly")
        self.gender_bias_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=2)
        # Add tooltip for Gender Bias - this part was missing from the previous structure of this function
        # For simplicity, adding it directly. Ideally, tooltips would be managed more centrally if there were many.
        # gender_tooltip_label = ttk.Label(parent_frame, text="Set a bias for character gender generation (Female/Male ratio).", wraplength=200, font=("TkDefaultFont", 8))
        # gender_tooltip_label.grid(row=current_row, column=2, padx=5, pady=2, sticky='w') # Place tooltip in a new column or row if needed
        current_row += 1

    def browse_directory(self):
        """Opens a dialog to select the output directory."""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir_var.get(), # Start in current dir
            title="Select Output Directory"
        )
        if directory: # If user selected a directory (didn't cancel)
            self.output_dir_var.set(directory)
            self.logger.info(f"Output directory set by user to: {directory}")

    def on_genre_select(self, event=None):
        self.populate_subgenres()
        self.update_dynamic_tabs() # Update tabs when genre changes
        self.trigger_callbacks()

    def on_subgenre_select(self, event=None):
        self.update_dynamic_tabs() # Update tabs when subgenre changes
        self.trigger_callbacks()
        
    def populate_subgenres(self):
        genre = self.genre_var.get()
        if genre == "Sci-Fi":
            subgenres = (
                "Space Opera", "Hard Sci-Fi", "Cyberpunk",
                "Time Travel", "Post-Apocalyptic", "Biopunk"
            )
        elif genre == "Fantasy":
            subgenres = (
                "High Fantasy", "Dark Fantasy", "Urban Fantasy",
                "Sword and Sorcery", "Mythic Fantasy", "Fairy Tale"
            )
        elif genre == "Horror":
            subgenres = (
                "Gothic Horror", "Psychological Horror", "Supernatural Horror",
                "Body Horror", "Cosmic Horror", "Slasher"
            )
        elif genre == "Mystery":
            subgenres = (
                "Cozy Mystery", "Hard-boiled Detective", "Police Procedural",
                "Amateur Sleuth", "Legal Thriller", "Forensic Mystery"
            )
        elif genre == "Romance":
            subgenres = (
                "Contemporary Romance", "Historical Romance", "Paranormal Romance",
                "Romantic Suspense", "Regency Romance", "Western Romance"
            )
        elif genre == "Thriller":
            subgenres = (
                "Espionage Thriller", "Psychological Thriller", "Action Thriller",
                "Techno-Thriller", "Medical Thriller", "Legal Thriller"
            )
        elif genre == "Western":
            subgenres = (
                "Traditional Western", "Weird Western", "Space Western",
                "Modern Western", "Outlaw Western", "Cattle Drive Western"
            )
        elif genre == "Historical Fiction":
            subgenres = (
                "Ancient History", "Medieval", "Renaissance",
                "Colonial America", "Civil War Era", "World War Era"
            )
        else:
             subgenres = ()
        
        current_subgenre = self.subgenre_var.get()
        self.subgenre_dropdown['values'] = subgenres
        
        if subgenres:
            if current_subgenre not in subgenres:
                 self.subgenre_var.set(subgenres[0])
        else:
            self.subgenre_var.set("")
            
    def update_dynamic_tabs(self):
        """Destroy and recreate dynamic tabs based on current genre/subgenre."""
        if self.notebook:
            self.notebook.destroy()
        self.dynamic_vars.clear() # Clear old dynamic variables
            
        self.notebook = ttk.Notebook(self.notebook_container) # Create notebook in its container
        self.notebook.pack(expand=True, fill='both')
        
        genre = self.genre_var.get()
        subgenre = self.subgenre_var.get()
        config = get_genre_config(genre, subgenre)
        
        if not config:
             self.logger.warning(f"No genre config found for {genre} - {subgenre} during dynamic tab update.")
             # Maybe add a default placeholder tab?
             placeholder_frame = ttk.Frame(self.notebook)
             self.notebook.add(placeholder_frame, text="Settings")
             ttk.Label(placeholder_frame, text="No specific settings for this subgenre.").pack(padx=10, pady=10)
             return
        
        # Create tabs based on config keys
        if "implied_settings" in config:
            self.create_settings_tab(config["implied_settings"])
        if "protagonist_types" in config:
            self.create_character_tab(config["protagonist_types"])
        if "conflict_scales" in config:
            self.create_conflict_tab(config["conflict_scales"])
        # Add more checks here if you have other dynamic sections in genre_configs

    def _create_dynamic_widget(self, parent, setting_name, value, row_num):
        """Helper to create widget and store its variable."""
        label = ttk.Label(parent, text=setting_name.replace('_', ' ').title())
        label.grid(row=row_num, column=0, padx=5, pady=2, sticky='w')
        
        var_key = setting_name.lower().replace(' ', '_') # Consistent key for dict
        
        if isinstance(value, bool):
            var = tk.BooleanVar(value=value)
            widget = ttk.Checkbutton(parent, variable=var)
        elif isinstance(value, (list, tuple)):
            var = tk.StringVar(value=value[0])
            widget = ttk.Combobox(parent, textvariable=var, values=value, state="readonly")
        else:
            var = tk.StringVar(value=str(value))
            widget = ttk.Entry(parent, textvariable=var)
            
        widget.grid(row=row_num, column=1, padx=5, pady=2, sticky='ew')
        self.dynamic_vars[var_key] = var # Store var in the dictionary

    def create_settings_tab(self, settings):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Specific Settings")
        settings_frame.columnconfigure(1, weight=1)
        
        i = 0
        for setting, value in settings.items():
            self._create_dynamic_widget(settings_frame, setting, value, i)
            i += 1

    def create_character_tab(self, protagonist_types):
        char_frame = ttk.Frame(self.notebook)
        self.notebook.add(char_frame, text="Protagonist")
        char_frame.columnconfigure(1, weight=1)

        self._create_dynamic_widget(char_frame, "Protagonist Type", protagonist_types, 0)

    def create_conflict_tab(self, conflict_scales):
        conflict_frame = ttk.Frame(self.notebook)
        self.notebook.add(conflict_frame, text="Conflict")
        conflict_frame.columnconfigure(1, weight=1)

        self._create_dynamic_widget(conflict_frame, "Conflict Scale", conflict_scales, 0)

    def get_current_parameters(self):
        params = {
            "output_directory": self.output_dir_var.get(),
            "genre": self.genre_var.get(),
            "subgenre": self.subgenre_var.get(),
            "story_length": self.length_var.get(),
            "story_structure": self.structure_var.get(),
            "novel_title": self.title_var.get(),
            "author_name": self.author_var.get(),
            "theme": self.theme_var.get(),
            "tone": self.tone_var.get(),
            # "gender_generation_bias": self.gender_bias_var.get() # Old way
        }
        
        # Resolve gender bias string to percentages
        selected_bias_string = self.gender_bias_var.get()
        # The map stores (female_%, male_%)
        # The SciFiCharacterGenerator and FantasyCharacterGenerator will expect (male_percentage, female_percentage)
        # So we will flip them when retrieving if necessary, or store them as (male, female) in the map.
        # Let's assume the generators will expect (male_percentage, female_percentage)
        # And the map will provide (female_p, male_p) matching the F/M display order.
        # So, when SciFiCharacterGenerator or FantasyCharacterGenerator gets male_p and female_p, it will use them directly.
        
        # Let's redefine GENDER_BIAS_MAP to store (male_percentage, female_percentage)
        # This makes downstream usage more direct.
        # GENDER_BIAS_MAP_INTERNAL = {
        #     "Balanced (50F/50M)": (50, 50), # (male_%, female_%)
        #     "Slightly Female (60F/40M)": (40, 60),
        #     "Mostly Female (75F/25M)": (25, 75),
        #     "Primarily Female (90F/10M)": (10, 90),
        #     "Slightly Male (40F/60M)": (60, 40),
        #     "Mostly Male (25F/75M)": (75, 25),
        #     "Primarily Male (10F/90M)": (90, 10)
        # }
        # The GENDER_BIAS_MAP is defined outside the class, let's use that one.
        # The map stores (female_%, male_%) currently to match the F/M in the string.
        # We will pass these two values and let the generator use them.
        # The generator was expecting male_weight, female_weight.
        # If we pass (female_p, male_p) from the map as female_percentage and male_percentage to the generator,
        # then the generator will correctly assign female_weight = female_percentage / 100.0 etc.
        
        female_p, male_p = GENDER_BIAS_MAP.get(selected_bias_string, (50, 50)) # Default to 50/50 if not found
        
        params["female_percentage"] = female_p
        params["male_percentage"] = male_p
        params["gender_generation_bias_string"] = selected_bias_string # Keep original string for saving/logging if needed

        # print("params: ", params)
        # Add dynamic parameters
        for key, var in self.dynamic_vars.items():
             # Ensure boolean values are read correctly
             if isinstance(var, tk.BooleanVar):
                 params[key] = var.get()
             else:
                 params[key] = var.get()
                 
        # Return the raw parameters dictionary without filtering empty strings here
        return params

    def save_parameters(self):
        params = self.get_current_parameters()
        # --- DEBUG PRINT --- 
        # print("\n--- DEBUG: Parameters collected for saving ---")
        # print(params)
        # print("---------------------------------------------")
        # --- END DEBUG ---
        self.logger.debug(f"Parameters collected for saving: {params}")
        
        # Define the order for saving - include core params first
        param_order = ["Output Directory", "Genre", "Subgenre", "Story Length", "Story Structure", 
                       "Novel Title", "Author Name", "Theme", "Tone", "Gender Generation Bias String"] # Use the string for saving
        
        output_lines = []
        # Add ordered core params
        for key_display in param_order:
            dict_key = key_display.lower().replace(" ", "_")
            value = params.get(dict_key, "")
            if value or isinstance(value, bool): # Include booleans even if False
                 output_lines.append(f"{key_display}: {value}")
                 
        # Add dynamic params (order might vary)
        for key_internal, value in params.items():
            # Skip already added core params
            if key_internal in [k.lower().replace(" ", "_") for k in param_order]:
                continue
            key_display = key_internal.replace('_', ' ').title() # Recreate display name
            if value or isinstance(value, bool):
                 output_lines.append(f"{key_display}: {value}")

        # Use the configured output directory with new structured layout
        output_dir = params.get("output_directory", "current_work") # Get configured dir
        system_dir = os.path.join(output_dir, "system") # Create system subdirectory
        os.makedirs(system_dir, exist_ok=True) # Ensure system directory exists
        filepath = os.path.join(system_dir, "parameters.txt") # Save params in system dir

        try:
            write_file(filepath, "\n".join(output_lines))
            self.logger.info(f"Parameters saved to {filepath}")
            # show_success("Success", f"Parameters saved to {filepath}")
        except Exception as e:
            show_error("Error", f"Failed to save parameters: {e}")
            self.logger.error(f"Error saving parameters to {filepath}: {e}", exc_info=True)

    def load_parameters(self):
        # Check for parameters file in new structured directory first, then fall back to old location
        default_dir = "current_work"
        
        # Option 1: New structured path
        structured_filepath = os.path.join(default_dir, "system", "parameters.txt")
        # Option 2: Old flat path (fallback)
        flat_filepath = os.path.join(default_dir, "parameters.txt")
        
        # Determine which file to use
        if os.path.exists(structured_filepath):
            filepath = structured_filepath
            self.logger.info(f"Loading parameters from structured path: {filepath}")
        elif os.path.exists(flat_filepath):
            filepath = flat_filepath
            self.logger.info(f"Loading parameters from legacy path: {filepath}")
        else:
            # No parameters file found, use defaults
            filepath = structured_filepath  # Will be created here when saved
            self.logger.info(f"No parameters file found, will use defaults and save to: {filepath}")

        loaded_params = {}
        if os.path.exists(filepath):
             try:
                 with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            loaded_params[key.strip()] = value.strip()
             except Exception as e:
                 show_error("Error", f"Failed to read parameters file {filepath}: {e}")
                 self.logger.error(f"Error reading parameters file {filepath}: {e}", exc_info=True)
                 # Continue with defaults below

        # --- Load Core Parameters ---
        # Load output directory FIRST if available
        self.output_dir_var.set(loaded_params.get("Output Directory", default_dir))

        self.genre_var.set(loaded_params.get("Genre", "Sci-Fi"))
        self.populate_subgenres() # IMPORTANT: Update subgenres before setting subgenre var
        self.subgenre_var.set(loaded_params.get("Subgenre", "")) # Load saved subgenre
        
        self.length_var.set(loaded_params.get("Story Length", LENGTH_OPTIONS[0]))
        self.on_length_select() # Update structure options based on loaded length
        self.structure_var.set(loaded_params.get("Story Structure", self.structure_var.get())) # Load structure
        
        self.title_var.set(loaded_params.get("Novel Title", ""))
        self.author_var.set(loaded_params.get("Author Name", ""))
        self.theme_var.set(loaded_params.get("Theme", ""))
        self.tone_var.set(loaded_params.get("Tone", ""))
        self.gender_bias_var.set(loaded_params.get("Gender Generation Bias String", self.gender_bias_options[0]))

        # --- Load Dynamic Parameters ---
        # This needs to happen AFTER dynamic tabs are potentially recreated by subgenre change
        self.update_dynamic_tabs() # Ensure correct tabs are present first
        
        for key_display, value in loaded_params.items():
             # Skip core parameters already handled
            if key_display in ["Output Directory", "Genre", "Subgenre", "Story Length", "Story Structure", 
                              "Novel Title", "Author Name", "Theme", "Tone", "Gender Generation Bias String"]:
                continue
            
            # Find the corresponding dynamic variable
            var_key = key_display.lower().replace(" ", "_")
            if var_key in self.dynamic_vars:
                var = self.dynamic_vars[var_key]
                # Handle different types (esp. Boolean)
                if isinstance(var, tk.BooleanVar):
                    # Ensure string 'True'/'true' becomes Python True, and 'False'/'false' becomes False
                    var.set(value.lower() == 'true') 
                else:
                    var.set(value)
            elif var_key == "gender_generation_bias_string": # Check for the string version
                # This key is derived, not directly in dynamic_vars, it's set by self.gender_bias_var
                 self.gender_bias_var.set(value) # Set the combobox selection string
            else:
                self.logger.warning(f"No dynamic variable found for loaded parameter '{key_display}' (internal key: '{var_key}') from {filepath}")

        self.logger.info(f"Parameters loaded from {filepath}")
        self.trigger_callbacks() # Trigger callbacks after everything is loaded

    def add_callback(self, callback):
        if callable(callback):
            self.callbacks.append(callback)

    def trigger_callbacks(self):
        current_params = self.get_current_parameters()
        for callback in self.callbacks:
            try:
                # Callbacks might need the parameters, or fetch them themselves
                # For now, call without arguments, assuming they fetch if needed
                callback() # It's important callbacks can access app.param_ui.get_current_parameters()
            except Exception as e:
                self.logger.error(f"Error executing callback {callback.__name__}: {e}", exc_info=True)

    def on_length_select(self, event=None):
        selected_length = self.length_var.get()
        if selected_length in STRUCTURE_MAP:
            available_structures = STRUCTURE_MAP[selected_length]
            self.structure_combobox['values'] = available_structures
            self.structure_combobox['state'] = 'readonly'
            default = DEFAULT_STRUCTURE.get(selected_length, available_structures[0])
            # Only set default if structure var is empty or not in new list
            if not self.structure_var.get() or self.structure_var.get() not in available_structures:
                self.structure_var.set(default)
        else:
            self.structure_combobox['values'] = []
            self.structure_combobox['state'] = 'disabled'
            self.structure_var.set("")
        self.trigger_callbacks() # Ensure callbacks are triggered

    def on_structure_select(self, event=None):
        """Called when the story structure is manually selected."""
        self.trigger_callbacks() # Ensure callbacks are triggered

    def get_gender_bias_options(self):
        # These strings must exactly match the keys in GENDER_BIAS_MAP
        return [
            "Balanced (50F/50M)",
            "Slightly Female (60F/40M)",
            "Mostly Female (75F/25M)",
            "Primarily Female (90F/10M)",
            "Slightly Male (40F/60M)",
            "Mostly Male (25F/75M)",
            "Primarily Male (10F/90M)"
        ]

# (Example __main__ block can be removed or kept for testing)

