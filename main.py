import tkinter as tk
from tkinter import ttk
import logging
from logger_config import setup_app_logger
from parameters import Parameters
from genre_configs import get_genre_config
from lore import Lore
from story_structure import StoryStructure
from scene_plan import ScenePlanning
from chapter_writing import ChapterWriting
from ai_helper import get_supported_models

# NovelWriter: An AI-assisted novel writing tool
# Features:
# - GUI-based interface for novel development
# - Supports parameter collection, lore generation, and chapter writing
# - Saves work across multiple files
#
# Currently optimized for Science Fiction, with planned expansion to other genres

class NovelWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Writer")

        # --- Add Model Selection ---
        self.model_frame = ttk.Frame(root)
        self.model_frame.pack(pady=5, padx=10, fill='x')

        ttk.Label(self.model_frame, text="Select LLM Model:").pack(side="left", padx=5)

        # Get available models dynamically
        self.available_models = get_supported_models()
        if not self.available_models: # Fallback if list is empty
            self.available_models = ["gpt-4o"] # Provide a default fallback
            # Potential place for a log warning if logger was already set up
            # print("Warning: Could not retrieve models from ai_helper. Using default.")

        self.selected_model_var = tk.StringVar(value=self.available_models[0] if self.available_models else "") # Default to the first model or empty

        self.model_combobox = ttk.Combobox(
            self.model_frame,
            textvariable=self.selected_model_var,
            values=self.available_models, # Use the dynamic list
            state="readonly"
        )
        self.model_combobox.pack(side="left", fill='x', expand=True)
        # --- End Model Selection ---

        # Create notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Parameters UI
        self.param_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.param_frame, text="Novel Parameters")
        self.param_ui = Parameters(self.param_frame, app=self)
        
        # --- Initialize Logger HERE, after param_ui is available for get_output_dir() ---
        # self.get_output_dir() has a fallback, so it's safe to call even if params haven't been loaded by user yet.
        self.logger = setup_app_logger(output_dir=self.get_output_dir(), level=logging.DEBUG)
        self.logger.info("NovelWriterApp initialized and logger started.")
        if not self.available_models:
             self.logger.warning("Could not retrieve models from ai_helper. Using default: gpt-4o")
        # --- End Logger Initialization ---
        
        # Lore Generation UI
        self.lore_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lore_frame, text="Generate Lore")
        # self.lore_frame.parameters_ui = self.param_ui # Lore gets app, which has param_ui
        self.lore_ui = Lore(self.lore_frame, app=self) # Pass the app instance
        
        # Register Lore's update method as a callback in Parameters
        self.param_ui.add_callback(self.lore_ui.update_extra_parameter)

        # High-Level Story Structure UI
        self.structure_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.structure_frame, text="Story Structure")
        self.structure_ui = StoryStructure(self.structure_frame, app=self)

        # Scene Planning UI
        self.outlining_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.outlining_frame, text="Scene Planning")
        self.outlining_ui = ScenePlanning(self.outlining_frame, app=self)

        # Chapter Writing UI
        self.chapter_writing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chapter_writing_frame, text="Write Chapters")
        self.chapter_writing_ui = ChapterWriting(self.chapter_writing_frame, app=self)

        # Now you can access relevant parameters while the implied settings
        # are handled automatically by your universe generator

        # Access parameters directly when needed

    def get_output_dir(self):
        """Returns the configured output directory path."""
        # Default to 'current_work' if param_ui isn't ready or var is empty
        
        try:
            path = self.param_ui.output_dir_var.get()
            # Log which path is being used if logger is available
            if hasattr(self, 'logger') and self.logger:
                returning_value = path if path else "current_work"
                self.logger.debug(f"get_output_dir called. Path from param_ui: '{path}'. Returning: '{returning_value}'")
            return path if path else "current_work"
        except AttributeError:
            # Logger might not be initialized yet if this is called before param_ui setup.
            # This case is less likely if logger setup is after param_ui init.
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning("get_output_dir called before param_ui fully initialized or output_dir_var missing. Falling back to 'current_work'.")
            return "current_work"

    def get_selected_model(self):
        """Returns the currently selected LLM model name."""
        model = self.selected_model_var.get()
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"get_selected_model called. Returning: {model}")
        return model

    def generate_story(self):
        """
        Coordinates story generation across all UI components using current parameters
        and genre configurations.
        """
        # Ensure this function also uses the selected model if it makes LLM calls
        selected_model = self.get_selected_model()
        # print(f"Using model: {selected_model} for story generation coordination")
        self.logger.info(f"generate_story called. Using model: {selected_model} for story generation coordination")

        # 1. Get base parameters
        current_params = self.param_ui.get_current_parameters()
        genre = current_params["genre"]
        subgenre = current_params["subgenre"]
        genre_config = get_genre_config(genre, subgenre)

        # 2. Generate world lore
        #lore_elements = self.lore_ui.generate_lore(
        #    parameters=current_params,
        #    genre_config=genre_config
        #)
        lore_elements = self.lore_ui.generate_lore()

        # 3. Create high-level story structure
        story_outline = self.structure_ui.generate_structure(
            parameters=current_params,
            genre_config=genre_config,
            lore=lore_elements
        )

        # 4. Plan scenes based on story structure
        scene_plan = self.outlining_ui.plan_scenes(
            parameters=current_params,
            genre_config=genre_config,
            story_structure=story_outline,
            lore=lore_elements
        )

        # 5. Initialize chapter writing interface
        self.chapter_writing_ui.initialize_chapters(
            parameters=current_params,
            genre_config=genre_config,
            scene_plan=scene_plan,
            lore=lore_elements
        )

        # 6. Switch to the chapter writing tab
        self.notebook.select(self.chapter_writing_frame)

        return {
            "parameters": current_params,
            "lore": lore_elements,
            "story_structure": story_outline,
            "scene_plan": scene_plan
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()