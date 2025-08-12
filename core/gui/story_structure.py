from tkinter import ttk, messagebox
from core.gui.notifications import show_success, show_error, show_warning
from core.generation.ai_helper import send_prompt
import re
from core.generation.helper_fns import open_file, write_file, read_json, save_prompt_to_file
import os
import traceback
import json
from core.gui.parameters import STRUCTURE_SECTIONS_MAP # Import the centralized map
import logging

class StoryStructure:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app  # Store the app instance
        
        # Initialize directory manager for structured file paths
        from core.config.directory_config import get_directory_manager
        self.dir_manager = get_directory_manager(
            output_dir=app.get_output_dir() if hasattr(app, 'get_output_dir') else 'current_work',
            use_new_structure=True
        )

        # Frame setup for story structure UI
        self.story_structure_frame = ttk.Frame(parent)
        self.story_structure_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.story_structure_frame, text="High-Level Story Structure", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Arcs
        self.c_arc_button = ttk.Button(self.story_structure_frame, text="Generate Character Arcs", command=self.generate_arcs)
        self.c_arc_button.pack(pady=20)

        self.f_arc_button = ttk.Button(self.story_structure_frame, text="Generate Faction Arcs", command=self.generate_faction_arcs)
        self.f_arc_button.pack(pady=20)

        self.cfp_arc_button = ttk.Button(self.story_structure_frame, text="Add Locations to Arcs", command=self.add_planets_to_arcs)
        self.cfp_arc_button.pack(pady=20)

        # Generate Structure Buttons
        # self.generate_button = ttk.Button(self.story_structure_frame, text="Generate Story Structure", command=self.generate_structure)
        # self.generate_button.pack(pady=20)

        # self.add_planets_to_structure_button = ttk.Button(self.story_structure_frame, text="Add Locations to Story Structure", command=self.generate_structure_with_locations)
        # self.add_planets_to_structure_button.pack(pady=20)

        self.detailed_plot_button = ttk.Button(
            self.story_structure_frame,
            text="Create Detailed Plot", # Set a basic default text immediately
            command=self._dispatch_detailed_plot_creation 
        )
        self.detailed_plot_button.pack(pady=20)

        # Log right after button creation and packing
        if self.app and hasattr(self.app, 'logger'):
            if hasattr(self, 'detailed_plot_button'):
                self.app.logger.info("StoryStructure.__init__: self.detailed_plot_button has been created and packed.")
            else:
                self.app.logger.error("StoryStructure.__init__: self.detailed_plot_button IS MISSING after creation attempt.")

        # Register callback to update button text when parameters change
        if self.app and hasattr(self.app, 'param_ui') and hasattr(self.app.param_ui, 'add_callback'):
            self.app.param_ui.add_callback(self._update_detailed_plot_button_text)
        self._update_detailed_plot_button_text() # Set initial text

    def _update_detailed_plot_button_text(self):
        """Updates the text of the detailed plot button based on story length."""
        if not hasattr(self, 'detailed_plot_button'):
            if self.app and hasattr(self.app, 'logger'):
                 self.app.logger.error("detailed_plot_button does not exist when _update_detailed_plot_button_text is called.")
            return

        # Check for app, param_ui, and the method's existence more rigorously
        if not (self.app and 
                hasattr(self.app, 'param_ui') and 
                self.app.param_ui is not None and  # Ensure param_ui is instantiated
                hasattr(self.app.param_ui, 'get_current_parameters') and
                callable(self.app.param_ui.get_current_parameters)):
            
            if self.app and hasattr(self.app, 'logger'):
                # Log this only once or less frequently if it becomes too noisy during startup
                self.app.logger.info("ParametersUI or get_current_parameters not fully available yet. Button text remains default or last set.")
            # Do not proceed further if dependencies are not met; button keeps its current text.
            # The callback will eventually trigger this method again when things are ready.
            return

        try:
            params = self.app.param_ui.get_current_parameters()
            story_length = params.get("story_length") # Allow None if not set yet
        except Exception as e:
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.error(f"Error getting parameters in _update_detailed_plot_button_text: {e}. Button text will not be updated this cycle.", exc_info=True)
            return # Keep current button text on error

        # Determine the text based on story_length
        # Start with the current button text as a fallback if no conditions match
        # or if story_length is None/unexpected.
        current_button_text = self.detailed_plot_button.cget("text") 
        button_text_to_set = current_button_text # Initialize with current

        if story_length == "Short Story":
            button_text_to_set = "Outline Short Story Plot"
        elif story_length == "Novella":
            button_text_to_set = "Outline Novella Plot Sections"
        elif story_length in ["Novel (Standard)", "Novel (Epic)"]:
            button_text_to_set = "Create Detailed Act/Section Plots"
        elif story_length is None: 
             # If story_length is None (e.g. params not fully loaded), 
             # keep a generic default if current text is also generic, or revert to a base default.
             # This handles the very initial call before params are loaded via callback.
             if current_button_text == "Create Detailed Plot" or not current_button_text.startswith(("Outline", "Create Detailed Act")):
                 button_text_to_set = "Create Detailed Plot"
             # else, it means params were loaded, then story_length became None, so keep specific text.
        else: # Unknown story_length, keep current or a generic default
            button_text_to_set = "Create Detailed Plot"
        
        if self.detailed_plot_button.cget("text") != button_text_to_set: # Only configure if text changes
            self.detailed_plot_button.config(text=button_text_to_set)
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.debug(f"Detailed plot button text changed to: '{button_text_to_set}' for story length: '{story_length}'")

    def _dispatch_detailed_plot_creation(self):
        """Dispatches to the correct plot creation method based on story length."""
        if not (self.app and hasattr(self.app, 'param_ui')):
            self.app.logger.error("ParametersUI not available to dispatch plot creation.")
            show_error("Error", "Cannot determine story parameters.")
            return

        params = self.app.param_ui.get_current_parameters()
        story_length = params.get("story_length")
        self.app.logger.info(f"Dispatching detailed plot creation for story length: {story_length}")

        if story_length == "Short Story":
            self._outline_short_story_plot()
        elif story_length in ["Novella", "Novel (Standard)", "Novel (Epic)"]:
            # Novella, Novel, and Epic will use the existing improve_structure logic.
            # improve_structure itself will make minor prompt adjustments for Novella.
            self.improve_structure()
        else:
            self.app.logger.error(f"Unknown story length '{story_length}' for detailed plot creation.")
            show_error("Error", f"Unsupported story length '{story_length}' for this operation.")

    # Generate character story arcs using individual backstories
    def generate_arcs(self):
        selected_model = self.app.get_selected_model() # Get selected model
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        self.app.logger.info(f"Generating Character Arcs using model: {selected_model}, output_dir: {output_dir}")
        
        lore_file_path = os.path.join(output_dir, "story", "lore", "generated_lore.md")
        characters_json_path = os.path.join(output_dir, "story", "lore", "characters.json") # Path to characters.json
        output_file_path = os.path.join(output_dir, "story", "structure", "character_arcs.md")
        
        # --- Dynamically determine backstory file paths --- 
        main_character_names_by_role = {
            "protagonist": None,
            "deuteragonist": None,
            "antagonist": None
        }
        character_roster_summaries = []
        all_characters_data = [] # To store all loaded character dicts

        try:
            # Load Full Character Roster from characters.json FIRST to get names for backstories
            full_character_data_json = read_json(characters_json_path)
            all_characters_data = full_character_data_json.get("characters", [])
            if not all_characters_data:
                self.app.logger.error(f"No characters found in {characters_json_path}. Cannot determine main character names or build roster.")
                show_error("Error", f"No characters loaded from {characters_json_path}. Required for identifying main character backstories.")
                return
            
            self.app.logger.info(f"Loaded {len(all_characters_data)} characters from {characters_json_path}.")

            for char_info in all_characters_data:
                name = char_info.get("name", "Unknown")
                role_raw = char_info.get("role", "").lower()
                gender = char_info.get("gender", "N/A")
                faction = char_info.get("faction", "Unaffiliated")
                age = char_info.get("age", "N/A") 
                title = char_info.get("title", "") 
                
                # Store names of main characters for backstory file lookup
                if role_raw in main_character_names_by_role:
                    safe_name_for_file = name.lower().replace(' ', '_').replace('/', '_').replace(':', '_')
                    main_character_names_by_role[role_raw] = safe_name_for_file # Store sanitized name
                    self.app.logger.info(f"Identified {role_raw}: {name} (sanitized for filename: {safe_name_for_file})")

                # Build summary for character roster (including flaws and strengths)
                summary_parts = [f"  - {name} ({char_info.get('role', 'N/A')})"] # Use original role string for display
                if title:
                    summary_parts.append(f"Title: {title}")
                summary_parts.append(f"Age: {age}")
                summary_parts.append(f"Gender: {gender}")
                summary_parts.append(f"Faction: {faction}")
                
                goals = char_info.get("goals", [])
                if goals and isinstance(goals, list) and len(goals) > 0:
                    summary_parts.append(f"Primary Goal: {goals[0]}")
                
                strengths = char_info.get("strengths", [])
                if strengths and isinstance(strengths, list) and len(strengths) > 0:
                    summary_parts.append(f"Strength: {strengths[0]}")

                flaws = char_info.get("flaws", [])
                if flaws and isinstance(flaws, list) and len(flaws) > 0:
                    summary_parts.append(f"Flaw: {flaws[0]}")

                summary = ", ".join(summary_parts)
                character_roster_summaries.append(summary)

        except FileNotFoundError:
            self.app.logger.error(f"Characters.json not found at {characters_json_path}. Cannot proceed.", exc_info=True)
            show_error("Error", f"Characters file not found: {characters_json_path}")
            return
        except (json.JSONDecodeError, ValueError) as e:
            self.app.logger.error(f"Error loading or parsing {characters_json_path}: {e}", exc_info=True)
            show_error("Error", f"Error parsing characters file: {characters_json_path}")
            return
        
        # Construct dynamic background file paths (use structured directory layout)
        background_files_paths = {}
        for role, char_file_name_part in main_character_names_by_role.items():
            if char_file_name_part:
                # Filename format from lore.py: background_{role}_{name_part}.md
                filename = f"background_{role}_{char_file_name_part}.md"
                # Use structured directory: story/lore/ instead of flat structure
                background_files_paths[role] = os.path.join(output_dir, "story", "lore", filename)
            else:
                self.app.logger.warning(f"Could not find character name for role: {role} in characters.json. Cannot load their backstory.")
        
        # --- End dynamic backstory file path determination ---

        try:
            # Load Overall Lore
            try:
                lore_content = open_file(lore_file_path)
                self.app.logger.info(f"Loaded lore from {lore_file_path}")
            except FileNotFoundError:
                self.app.logger.warning(f"Lore file not found: {lore_file_path}. Arcs might lack context.")
                show_warning("Missing File", f"Lore file not found: {lore_file_path}. Arcs might lack context.")
                lore_content = "Lore context is missing."

            # Load Individual Character Backstories
            backstory_content = {}
            main_chars_with_backstories = [] # Stores the role ('protagonist', etc.)
            roles_to_load = ["protagonist", "deuteragonist", "antagonist"]

            for role in roles_to_load:
                filepath = background_files_paths.get(role)
                if filepath and os.path.exists(filepath):
                    try:
                        backstory_content[role] = open_file(filepath)
                        main_chars_with_backstories.append(role) # Add the role string, not capitalized yet
                        self.app.logger.info(f"Loaded backstory for {role} from {filepath}.")
                    except Exception as e_open:
                        self.app.logger.warning(f"Could not open backstory file for {role} at {filepath}: {e_open}. Skipping {role} backstory.")
                        backstory_content[role] = f"Backstory for {role} is missing or unreadable."
                elif filepath: # Filepath was determined but doesn't exist
                    self.app.logger.warning(f"Background file for {role} not found at {filepath}. Skipping {role} backstory.")
                    backstory_content[role] = f"Backstory for {role} is missing (File not found: {os.path.basename(filepath)})."
                else: # Filepath could not be determined (name for role not found)
                    # Already logged earlier, but good to have a placeholder for prompt
                    backstory_content[role] = f"Backstory for {role} is missing (Character for role not identified)."

            if not main_chars_with_backstories:
                self.app.logger.error("No main character background files could be loaded (protagonist, deuteragonist, antagonist). Cannot generate arcs.")
                show_error("Error", "No main character background files could be loaded. Check logs for details. Cannot generate arcs.")
                return

            # Construct the Prompt
            prompt_lines = [
                "I am writing a science fiction novel and need help planning the character arcs for the main characters.",
                f"Please generate compelling character arcs for the following roles: {', '.join([r.capitalize() for r in main_chars_with_backstories])}.",
                "Base these arcs on the overall universe lore, their detailed backstories, and the full character roster provided below.",
                "The arcs should show significant development or change for each of these main characters.",
                "When developing these arcs, you may reference or involve characters from the 'Full Character Roster'. Avoid introducing new significant named characters unless essential.",
                "\n## Overall Universe Lore:",
                lore_content
            ]

            if character_roster_summaries:
                prompt_lines.append("\n ## Character Roster for Reference:")
                prompt_lines.extend(character_roster_summaries)
            else:
                prompt_lines.append("\n ## Character Roster for Reference: (No additional characters loaded from characters.json)")

            prompt_lines.append("\n## Main Character Backstories:")
            for role, story in backstory_content.items():
                prompt_lines.append(f"\n### Backstory for the {role.capitalize()}:\n{story}")

            prompt_lines.append(f"\n Please generate the character arcs for {', '.join([r.capitalize() for r in main_chars_with_backstories])} now, focusing on meaningful progression and connection to the provided backstories, lore, and character roster.")
            prompt = "\n".join(prompt_lines)
            
            # Save prompt to a file and log its path
            prompt_filepath = save_prompt_to_file(output_dir, "character_arc_prompt", prompt)
            
            if prompt_filepath:
                self.app.logger.info(f"Character Arc Generation Prompt (length {len(prompt)}) saved to: {prompt_filepath}")
            else:
                self.app.logger.error(f"Failed to save Character Arc Generation Prompt to a file. Prompt length: {len(prompt)}.")
                # As a fallback, if saving failed, log the prompt directly if DEBUG is on, or a snippet.
                # This ensures critical info isn't lost if file saving fails.
                if self.app.logger.isEnabledFor(logging.DEBUG): # Check if DEBUG is enabled for the app logger
                    self.app.logger.debug(f"Fallback: Full Character Arc Prompt due to save failure:\n{prompt}")
                else:
                    self.app.logger.warning("Prompt content not logged directly due to length and save failure. Enable DEBUG for full prompt.")

            # Send to LLM
            log_msg_prompt_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"
            self.app.logger.info(f"Sending prompt {log_msg_prompt_source} to LLM ({selected_model}) for character arc generation...")
            response = send_prompt(prompt, model=selected_model)
            
            if not response:
                 self.app.logger.error("Failed to generate character arcs from LLM. No response received.")
                 show_error("Error", "Failed to generate character arcs from LLM.")
                 return
            
            self.app.logger.info(f"Received character arcs from LLM. Length: {len(response)} chars.")
            # Save the response
            write_file(output_file_path, response)
            self.app.logger.info(f"Character arcs saved successfully to {output_file_path}")
            # show_success("Success", f"Character arcs generated and saved to {output_file_path}")

        except Exception as e:
            self.app.logger.error(f"Failed to generate character arcs: {e}", exc_info=True)
            # traceback.print_exc() # Handled by logger
            show_error("Error", f"An unexpected error occurred during character arc generation: {str(e)}")


    # Generate faction story arcs, THEN reconcile faction and character arcs
    def generate_faction_arcs(self):
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        self.app.logger.info(f"Faction Arc Generation & Reconciliation started. Model: {selected_model}, Output Dir: {output_dir}")

        # Define file paths consistently using output_dir
        parameters_file_path = os.path.join(output_dir, "system", "parameters.txt")
        character_arcs_file_path = os.path.join(output_dir, "story", "structure", "character_arcs.md")
        factions_json_file_path = os.path.join(output_dir, "story", "lore", "factions.json")
        lore_file_path = os.path.join(output_dir, "story", "lore", "generated_lore.md")
        faction_arcs_output_file_path = os.path.join(output_dir, "story", "structure", "faction_arcs.md")
        reconciled_output_file_path = os.path.join(output_dir, "story", "structure", "reconciled_arcs.md")
        
        try:
            # --- Read Parameters to get selected structure --- 
            selected_structure = "6-Act Structure" # Default if file/key is missing
            try:
                params = {}
                # Use open_file helper for reading parameters.txt if it's simple text,
                # or parse manually if open_file isn't suitable for this format.
                # For now, keeping manual open as it was.
                if not os.path.exists(parameters_file_path):
                    raise FileNotFoundError
                with open(parameters_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            params[key.strip()] = value.strip()
                selected_structure = params.get("Story Structure", selected_structure)
                self.app.logger.info(f"Using selected story structure: {selected_structure}")
            except FileNotFoundError:
                self.app.logger.warning(f"Parameters file not found: {parameters_file_path}. Using default structure: {selected_structure}")
            except Exception as e:
                 self.app.logger.warning(f"Error reading parameters file: {e}. Using default structure: {selected_structure}")

            # --- Step 1: Generate Faction Arcs --- 
            self.app.logger.info("--- Step 1: Generating Faction Arcs ---")

            # Load required inputs (character arcs, lore, factions)
            try:
                char_arcs_content = open_file(character_arcs_file_path)
            except FileNotFoundError:
                self.app.logger.error(f"Character arcs file not found: {character_arcs_file_path}. Cannot proceed.")
                show_error("Error", f"Character arcs file not found: {character_arcs_file_path}. Cannot proceed.")
                return
            
            try:
                lore_content = open_file(lore_file_path)
            except FileNotFoundError:
                show_warning("Missing File", f"Lore file not found: {lore_file_path}. Faction arcs might lack context.")
                self.app.logger.warning(f"Lore file not found: {lore_file_path}. Faction arcs might lack context.")
                lore_content = "Lore context is missing."
                
            # Load and parse factions.json
            try:
                # Assuming factions.json is read using helper_fns.read_json if available and suitable
                # or direct open as it was. For now, direct open.
                if not os.path.exists(factions_json_file_path):
                    raise FileNotFoundError
                with open(factions_json_file_path, 'r', encoding='utf-8') as f:
                    factions_data = json.load(f)
                
                # Extract top 5 factions based on military strength (similar to LorePromptGenerator)
                for faction in factions_data:
                    military_strength = 0
                    if "military_assets" in faction and isinstance(faction["military_assets"], dict):
                        military_strength = faction["military_assets"].get("total_military_personnel", 0)
                    # Ensure conversion handles potential None or non-digit strings gracefully
                    mil_val = str(military_strength).replace(',', '') if military_strength is not None else '0'
                    faction["_military_strength_value"] = int(mil_val) if mil_val.isdigit() else 0
                
                factions_data.sort(key=lambda x: x.get("_military_strength_value", 0), reverse=True)
                major_factions = factions_data[:5]
                
                if not major_factions:
                    self.app.logger.error(f"No faction data found or extracted from {factions_json_file_path}. Cannot generate faction arcs.")
                    show_error("Error", f"No faction data found or extracted from {factions_json_file_path}.")
                    return
                    
                # Create a summary for the prompt
                faction_summaries = []
                for f in major_factions:
                    name = f.get("faction_name", "Unknown")
                    profile = f.get("faction_profile", "No profile")
                    traits = ", ".join(f.get("primary_traits", []))
                    summary = f"- {name}: {profile} (Traits: {traits})"
                    faction_summaries.append(summary)
                faction_overview = "\n".join(faction_summaries)
                
            except FileNotFoundError:
                self.app.logger.error(f"Factions JSON file not found: {factions_json_file_path}. Cannot proceed.")
                show_error("Error", f"Factions JSON file not found: {factions_json_file_path}. Cannot proceed.")
                return
            except json.JSONDecodeError:
                 self.app.logger.error(f"Error decoding JSON from {factions_json_file_path}.")
                 show_error("Error", f"Error decoding JSON from {factions_json_file_path}.")
                 return

            # Build the first prompt for generating faction arcs (USING SELECTED STRUCTURE)
            prompt1_lines = [
                "I am writing a science fiction novel and need help planning the story arcs for the major factions.",
                f"Please generate compelling story arcs using the '{selected_structure}' framework for the following major factions, considering their profiles and traits:", # Use selected structure
                "\n## Major Factions Overview:",
                faction_overview,
                "\nBase these faction arcs on the overall universe lore and the established character arcs provided below. Ensure the faction arcs interact logically with the character arcs.",
                "\n## Overall Universe Lore:",
                lore_content,
                "\n## Character Arcs:",
                char_arcs_content,
                f"\nPlease generate ONLY the '{selected_structure}' story arcs for these major factions:" # Use selected structure
            ]
            prompt1 = "\n".join(prompt1_lines)

            # Save Prompt 1 (Faction Arc Generation)
            prompt1_filepath = save_prompt_to_file(output_dir, "faction_arc_generation_prompt", prompt1)
            if prompt1_filepath:
                self.app.logger.info(f"Faction Arc Generation Prompt (length {len(prompt1)}) saved to: {prompt1_filepath}")
            else:
                self.app.logger.error(f"Failed to save Faction Arc Generation Prompt. Length: {len(prompt1)}.")
                if self.app.logger.isEnabledFor(logging.DEBUG):
                    self.app.logger.debug(f"Fallback: Full Faction Arc Generation Prompt:\n{prompt1}")
                else:
                    self.app.logger.warning("Faction Arc Generation Prompt not logged directly. Enable DEBUG for full prompt.")
            
            # Send prompt 1 to LLM
            log_msg_prompt1_source = f"(from {prompt1_filepath})" if prompt1_filepath else "(from memory, save failed)"
            self.app.logger.info(f"Sending Faction Arc Generation Prompt {log_msg_prompt1_source} to LLM ({selected_model})...")
            faction_arcs_response = send_prompt(prompt1, model=selected_model)
            
            if not faction_arcs_response:
                self.app.logger.error(f"Failed to generate faction arcs from LLM ({selected_model}). No response.")
                show_error("Error", "Failed to generate faction arcs from LLM.")
                return
            
            self.app.logger.info(f"Received faction arcs from LLM. Length: {len(faction_arcs_response)}.")
            # Save the faction arcs response
            write_file(faction_arcs_output_file_path, faction_arcs_response)
            self.app.logger.info(f"Faction arcs content saved to {faction_arcs_output_file_path}")

            # --- Step 2: Reconcile Character and Faction Arcs --- 
            self.app.logger.info("--- Step 2: Reconciling Character and Faction Arcs ---")

            # Build the second prompt for reconciling arcs (USING SELECTED STRUCTURE)
            prompt2_lines = [
                 "I am writing a science fiction novel and need help reconciling the previously generated story arcs for the main characters and the major factions.",
                 "The two sets of arcs should weave together consistently and logically to form a unified narrative progression.",
                 "\nHere are the character arcs:",
                 char_arcs_content,
                 "\nHere are the faction arcs:",
                 faction_arcs_response, # Use the response from the first prompt
                 f"\nPlease write out a single, combined story arc using the '{selected_structure}' framework, integrating the key developments from both the character and faction arcs.", # Use selected structure
                 "Focus on showing how character actions influence faction events and vice-versa throughout the structure.",
                 f"Provide the unified '{selected_structure}' now:" # Use selected structure
            ]
            prompt2 = "\n".join(prompt2_lines)
            
            # Save Prompt 2 (Arc Reconciliation)
            prompt2_filepath = save_prompt_to_file(output_dir, "arc_reconciliation_prompt", prompt2)
            if prompt2_filepath:
                self.app.logger.info(f"Arc Reconciliation Prompt (length {len(prompt2)}) saved to: {prompt2_filepath}")
            else:
                self.app.logger.error(f"Failed to save Arc Reconciliation Prompt. Length: {len(prompt2)}.")
                if self.app.logger.isEnabledFor(logging.DEBUG):
                    self.app.logger.debug(f"Fallback: Full Arc Reconciliation Prompt:\n{prompt2}")
                else:
                    self.app.logger.warning("Arc Reconciliation Prompt not logged directly. Enable DEBUG for full prompt.")
            
            # Send prompt 2 to LLM
            log_msg_prompt2_source = f"(from {prompt2_filepath})" if prompt2_filepath else "(from memory, save failed)"
            self.app.logger.info(f"Sending Arc Reconciliation Prompt {log_msg_prompt2_source} to LLM ({selected_model})...")
            reconciled_response = send_prompt(prompt2, model=selected_model)
            
            if not reconciled_response:
                self.app.logger.error(f"Failed to reconcile arcs using LLM ({selected_model}). No response.")
                show_error("Error", "Failed to reconcile arcs using LLM.")
                return
            
            self.app.logger.info(f"Received reconciled arcs from LLM. Length: {len(reconciled_response)}.")
            # Save the reconciled arcs
            write_file(reconciled_output_file_path, reconciled_response)
            self.app.logger.info(f"Reconciled story arcs content saved to {reconciled_output_file_path}")
            # show_success("Success", f"Faction arcs generated and reconciled arcs saved to {reconciled_output_file_path}")

        except FileNotFoundError as fnf_e:
            self.app.logger.error(f"File not found during faction arc generation/reconciliation: {fnf_e}", exc_info=True)
            show_error("Error", f"File not found: {str(fnf_e)}")
        except json.JSONDecodeError as json_e:
            self.app.logger.error(f"JSON decode error during faction arc generation/reconciliation: {json_e}", exc_info=True)
            show_error("Error", f"Error decoding JSON data: {str(json_e)}")
        except Exception as e:
            self.app.logger.error(f"Failed during faction arc generation/reconciliation: {e}", exc_info=True)
            # traceback.print_exc() # Handled by logger
            show_error("Error", f"An unexpected error occurred: {str(e)}")

    # Add in the locations to the reconciled story arc (generic for all genres)
    def add_planets_to_arcs(self):
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        
        # Get current genre to determine location type
        try:
            from Generators.GenreHandlers import get_genre_handler
            params = self.app.param_ui.get_current_parameters()
            current_genre = params.get("genre", "Sci-Fi")
            genre_handler = get_genre_handler(current_genre)
            location_type_name = genre_handler.get_location_type_name()
        except Exception as e:
            self.app.logger.warning(f"Could not determine genre for location type: {e}. Using default.")
            location_type_name = "Locations"
            genre_handler = None
        
        self.app.logger.info(f"Adding {location_type_name} to Arcs. Model: {selected_model}, Output Dir: {output_dir}")
        
        # Define file paths
        reconciled_arcs_file_path = os.path.join(output_dir, "story", "structure", "reconciled_arcs.md")
        factions_json_file_path = os.path.join(output_dir, "story", "lore", "factions.json")
        output_file_path = os.path.join(output_dir, "story", "planning", "reconciled_locations_arcs.md")
        
        try:
            # Load the reconciled arcs
            try:
                reconciled_arcs_content = open_file(reconciled_arcs_file_path)
            except FileNotFoundError:
                show_error("Error", f"Reconciled arcs file not found: {reconciled_arcs_file_path}. Cannot proceed.")
                return

            # Load factions and extract relevant location data using genre handler
            location_faction_info = []
            try:
                if not os.path.exists(factions_json_file_path):
                    raise FileNotFoundError
                with open(factions_json_file_path, 'r', encoding='utf-8') as f:
                    factions_data = json.load(f)
                
                if genre_handler:
                    # Use genre-specific location extraction
                    locations = genre_handler.get_location_info_from_factions(factions_data)
                    for location in locations:
                        location_faction_info.append(f"- {location['description']}")
                else:
                    # Fallback for unknown genres - try to extract basic info
                    for faction in factions_data:
                        faction_name = faction.get("faction_name", faction.get("name", "Unknown Faction"))
                        # Try different possible location fields
                        location_name = None
                        if "systems" in faction:  # Sci-fi style
                            for system in faction.get("systems", []):
                                planets = system.get("habitable_planets", [])
                                if planets:
                                    location_name = f"{planets[0].get('name', 'Unknown')} in {system.get('name', 'Unknown System')}"
                                    break
                        elif "regions" in faction:  # Fantasy style
                            for region in faction.get("regions", []):
                                cities = region.get("cities", [])
                                if cities:
                                    location_name = f"{cities[0].get('name', 'Unknown')} in {region.get('name', 'Unknown Region')}"
                                    break
                        elif "territory" in faction:  # Western/other styles
                            location_name = faction.get("territory", "Unknown Territory")
                        
                        if location_name:
                            location_faction_info.append(f"- {location_name} (Controlled by {faction_name})")
                            
            except FileNotFoundError:
                 show_error("Error", f"Factions file not found: {factions_json_file_path}. Cannot extract location info.")
                 return
            except json.JSONDecodeError:
                 show_error("Error", f"Error decoding JSON from {factions_json_file_path}.")
                 return
                 
            if not location_faction_info:
                show_warning("Warning", f"Could not extract relevant {location_type_name.lower()}/faction information from factions.json.")
                location_list_str = f"No specific {location_type_name.lower()} data available."
            else:
                location_list_str = "\n".join(location_faction_info)

            # Build the prompt (genre-agnostic)
            prompt_lines = [
                f"I am writing a {current_genre.lower()} novel and need help adding specific {location_type_name.lower()} to the story arc.",
                f"Below is the reconciled story arc for characters and factions, followed by a list of key {location_type_name.lower()} and the factions that control them.",
                f"Please rewrite the story arc, weaving in appropriate {location_type_name.lower()} from the provided list where actions occur.",
                f"Ensure the chosen {location_type_name.lower()} align logically with the factions involved in each part of the arc.",
                f"Do not add {location_type_name.lower()} not on the list. Preserve the original arc structure and details as much as possible, only adding the location context.",
                "\n## Reconciled Story Arc:",
                reconciled_arcs_content,
                f"\n## Key {location_type_name} and Controlling Factions:",
                location_list_str,
                f"\nPlease provide the revised story arc with integrated {location_type_name.lower()}:"
            ]
            prompt = "\n".join(prompt_lines)

            # Save the prompt
            prompt_filepath = save_prompt_to_file(output_dir, "add_locations_to_arcs_prompt", prompt)
            if prompt_filepath:
                self.app.logger.info(f"Add {location_type_name} to Arcs Prompt (length {len(prompt)}) saved to: {prompt_filepath}")
            else:
                self.app.logger.error(f"Failed to save Add {location_type_name} to Arcs Prompt. Length: {len(prompt)}.")
                if self.app.logger.isEnabledFor(logging.DEBUG):
                    self.app.logger.debug(f"Fallback: Full Add {location_type_name} to Arcs Prompt:\n{prompt}")
                else:
                    self.app.logger.warning(f"Add {location_type_name} to Arcs Prompt not logged directly. Enable DEBUG for full prompt.")

            # Send prompt to LLM
            log_msg_prompt_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"
            self.app.logger.info(f"Sending Add {location_type_name} to Arcs Prompt {log_msg_prompt_source} to LLM ({selected_model})...")
            response = send_prompt(prompt, model=selected_model)
            
            if not response:
                self.app.logger.error(f"Failed to get response from LLM ({selected_model}) when adding {location_type_name.lower()}.")
                show_error("Error", f"Failed to get response from LLM when adding {location_type_name.lower()}.")
                return

            self.app.logger.info(f"Received response from LLM for adding {location_type_name.lower()}. Length: {len(response)}.")
            # Save the response
            write_file(output_file_path, response)
            self.app.logger.info(f"Story arc with {location_type_name.lower()} saved to {output_file_path}")
            # show_success("Success", f"Added {location_type_name.lower()}. Result saved to {output_file_path}")

        except FileNotFoundError as fnf_e:
            self.app.logger.error(f"File not found during add_locations_to_arcs: {fnf_e}", exc_info=True)
            show_error("Error", f"File not found: {str(fnf_e)}")
        except json.JSONDecodeError as json_e:
            self.app.logger.error(f"JSON decode error during add_locations_to_arcs: {json_e}", exc_info=True)
            show_error("Error", f"Error decoding JSON data: {str(json_e)}")
        except Exception as e:
            self.app.logger.error(f"Failed to add {location_type_name.lower()} to arcs: {e}", exc_info=True)
            # traceback.print_exc() # Handled by logger
            show_error("Error", f"An unexpected error occurred: {str(e)}")


    # Generate high-level structure (we use the user-selected structure)
    # TODO: review if this is needed. Perhaps we can skip.
    #   Although the output seems useful, it's not clear that it's needed.
    # def generate_structure(self):
    #     selected_model = self.app.get_selected_model()
    #     output_dir = self.app.get_output_dir()
    #     os.makedirs(output_dir, exist_ok=True)
    #     print(f"Generating structure with model: {selected_model}, output dir: {output_dir}")

    #     # --- Read Parameters to get selected structure --- 
    #     parameters_file_path = os.path.join(output_dir, "parameters.txt")
    #     selected_structure = "6-Act Structure" # Default if file/key is missing
    #     try:
    #         params = {}
    #         if not os.path.exists(parameters_file_path):
    #             print(f"Warning: Parameters file not found at {parameters_file_path}. Using default structure: {selected_structure}")
    #         else:
    #             with open(parameters_file_path, "r", encoding="utf-8") as f:
    #                 for line in f:
    #                     if ":" in line:
    #                         key, value = line.split(":", 1)
    #                         params[key.strip()] = value.strip()
    #             loaded_structure = params.get("Story Structure")
    #             if loaded_structure and loaded_structure.strip(): # Ensure it's not empty
    #                 selected_structure = loaded_structure
    #             else:
    #                 print(f"Warning: 'Story Structure' not found or empty in {parameters_file_path}. Using default: {selected_structure}")
    #         print(f"Using selected story structure: {selected_structure}")
    #     except Exception as e:
    #         print(f"Error reading parameters file ({parameters_file_path}): {e}. Using default structure: {selected_structure}")
    #     # --- End Reading Parameters ---

    #     # Construct full paths for input files
    #     lore_content_path = os.path.join(output_dir, "generated_lore.md")
    #     reconciled_arcs_path = os.path.join(output_dir, "reconciled_planets_arcs.md") 
    #     story_structure_output_path = os.path.join(output_dir, "story_structure.md")

    #     try:
    #         lore_content = open_file(lore_content_path)
    #         reconciled_arcs = open_file(reconciled_arcs_path)

    #         # Generate high-level structure using the selected_structure
    #         prompt = (
    #             f"Please generate a high-level story structure using the '{selected_structure}' framework, based on the following information.\n"
    #             f"Please review the following background parameters, factions, and characters:\n\n{lore_content}\n\n"
    #             f"Please see the story arc details:\n\n{reconciled_arcs}\n\n"
    #             f"Provide a structured outline with major plot points, faction interactions, character arcs, and key events, adhering to the '{selected_structure}'.\n"
    #             f"Ensure the outline clearly reflects the components and flow typical of a '{selected_structure}'.\n"
    #             f"Please be detailed and write as much as possible.\n"
    #             f"Please provide the structure in markdown format."
    #         )

    #         print("--- Generate Structure Prompt ---")
    #         print(prompt)
    #         print("---------------------------------")
    #         response = send_prompt(prompt, model=selected_model)
    #         write_file(story_structure_output_path, response)
    #         print(f"Story structure saved successfully to {story_structure_output_path}")
    #         show_success("Success", f"Story structure ({selected_structure}) saved to {story_structure_output_path}")

    #     except FileNotFoundError as fnf_e:
    #         show_error("Error", f"File not found during structure generation: {fnf_e}")
    #         print(f"File not found: {fnf_e}")
    #     except Exception as e:
    #         print(f"Failed to generate story structure: {e}")
    #         traceback.print_exc()
    #         show_error("Error", f"Failed to generate story structure: {str(e)}")


    # Add locations to the structure
    # Less smart LLMs keep killing off the location data, so need to keep adding it back.
    # TODO: review if this is needed. Perhaps we can skip.
    # def generate_structure_with_locations(self):
    #     selected_model = self.app.get_selected_model() 
    #     output_dir = self.app.get_output_dir()
    #     os.makedirs(output_dir, exist_ok=True)
    #     print(f"Generating structure w/locations with model: {selected_model}, output dir: {output_dir}")

    #     story_structure_path = os.path.join(output_dir, "story_structure.md")
    #     reconciled_arcs_path = os.path.join(output_dir, "reconciled_planets_arcs.md")
    #     story_structure_locations_output_path = os.path.join(output_dir, "story_structure_locations.md")

    #     try:
    #         story_structure_content = open_file(story_structure_path)
    #         reconciled_arcs_content = open_file(reconciled_arcs_path)

    #         prompt_text = (
    #             f"I am writing a science fiction novel and need help with the planning. "
    #             f"I need your help to add location information to my story structure document.\n"
    #             f"Here is the contents of my story structure document:\n\n{story_structure_content}\n\n"
    #             f"Please find the location information in the previously written story arc document:\n\n{reconciled_arcs_content}\n\n"
    #             "Please preserve the information in the story structure document and provide it in the output."
    #             "Please ensure the correct location information is added. Thanks"
    #         )

    #         llm_response = send_prompt(prompt_text, model=selected_model)
    #         write_file(story_structure_locations_output_path, llm_response)
    #         print(f"Story structure and location saved successfully to {story_structure_locations_output_path}")
    #         show_success("Success", f"Locations added to structure. Saved to {os.path.basename(story_structure_locations_output_path)}")

    #     except FileNotFoundError as fnf_e:
    #         show_error("Error", f"File not found: {fnf_e}")
    #         print(f"File not found: {fnf_e}")
    #     except Exception as e:
    #         print(f"Failed to generate story structure with locations: {e}")
    #         traceback.print_exc()
    #         show_error("Error", f"Failed to generate story structure with locations: {str(e)}")


    # Flesh out the acts of structure
    # Loop over each act (section) of the story arc
    def improve_structure(self):
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        # print(f"Improving structure with model: {selected_model}, output dir: {output_dir}") # Replaced
        self.app.logger.info(f"Improving structure. Model: {selected_model}, Output Dir: {output_dir}")

        # --- Read Parameters to get selected structure --- 
        parameters_file_path = os.path.join(output_dir, "parameters.txt")
        selected_structure_name = "6-Act Structure" # Default
        story_length = "Novel (Standard)" # Default story length for prompt modification
        try:
            params = {}
            if not os.path.exists(parameters_file_path):
                # print(f"Warning: Parameters file not found at {parameters_file_path}. Using default structure: {selected_structure_name}") # Replaced
                self.app.logger.warning(f"Parameters file not found at {parameters_file_path}. Using default structure: {selected_structure_name}")
            else:
                with open(parameters_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            params[key.strip()] = value.strip()
                loaded_structure = params.get("Story Structure")
                story_length = params.get("Story Length", story_length) # Get story length
                if loaded_structure and loaded_structure.strip():
                    selected_structure_name = loaded_structure
                else:
                    # print(f"Warning: 'Story Structure' not found or empty in {parameters_file_path}. Using default: {selected_structure_name}") # Replaced
                    self.app.logger.warning(f"'Story Structure' not found or empty in {parameters_file_path}. Using default: {selected_structure_name}")
            # print(f"Using selected story structure for improvement: {selected_structure_name}") # Replaced
            self.app.logger.info(f"Using selected story structure for improvement: {selected_structure_name} (Story Length: {story_length})")
        except Exception as e:
            # print(f"Error reading parameters file ({parameters_file_path}): {e}. Using default structure: {selected_structure_name}") # Replaced
            self.app.logger.error(f"Error reading parameters file ({parameters_file_path}): {e}. Using default: {selected_structure_name}", exc_info=True)
        # --- End Reading Parameters ---

        # --- STRUCTURE_SECTIONS_MAP is now imported from parameters.py ---
        sections_to_iterate = STRUCTURE_SECTIONS_MAP.get(selected_structure_name)

        if not sections_to_iterate:
            show_error("Error", f"No defined sections for structure '{selected_structure_name}'. Cannot improve structure.")
            # print(f"Error: Section definitions not found for structure '{selected_structure_name}'.") # Replaced
            self.app.logger.error(f"Section definitions not found for structure '{selected_structure_name}'. Cannot improve structure.")
            return

        try:
            # Try the new generic filename first, fall back to old filename for backward compatibility
            story_structure_path = os.path.join(output_dir, "story", "planning", "reconciled_locations_arcs.md")
            if not os.path.exists(story_structure_path):
                # Try legacy flat structure locations for backward compatibility
                story_structure_path = os.path.join(output_dir, "reconciled_locations_arcs.md")
                if not os.path.exists(story_structure_path):
                    story_structure_path = os.path.join(output_dir, "reconciled_planets_arcs.md")
            story_structure_content = open_file(story_structure_path)
            
            
            # print(f"Iterating over sections for '{selected_structure_name}': {sections_to_iterate}") # Replaced
            self.app.logger.info(f"Iterating over sections for '{selected_structure_name}': {sections_to_iterate}")

            previous_section_content = "" # Initialize to store the output of the previous section
            previous_section_name_for_prompt = "" # Store the user-friendly name of the previous section

            for i, section_name in enumerate(sections_to_iterate):
                current_section_name_for_prompt = section_name # User-friendly name like "Act I: Setup"
                prompt_lines = [
                    f"I am writing a science fiction novel using the '{selected_structure_name}' framework and need help fleshing out its parts.",
                    f"The overall framework consists of these parts: {', '.join(sections_to_iterate)}.",
                    f"Please write out a lot more detail specifically for the part: **{current_section_name_for_prompt}**. We are NOT writing individual scenes yet, but rather a more detailed summary for this part of the story.",
                    f"\n## Overall Story Structure Context (from {os.path.basename(story_structure_path)}):\n{story_structure_content}"
                ]

                # Add context from the immediately preceding detailed section (if not the first section)
                if previous_section_content: # i > 0 would also work
                    prompt_lines.append(f"\n\n## Context from the Immediately Preceding Detailed Section ('{previous_section_name_for_prompt}'):\n{previous_section_content}")
                    prompt_lines.append(f"\nPlease ensure your detailing of the current section ('{current_section_name_for_prompt}') flows logically from THIS PRECEDING DETAILED CONTEXT as well as the overall story structure provided earlier.")

                # Add novella-specific instruction if applicable
                if story_length == "Novella":
                    prompt_lines.append(f"\nGiven this section is part of a novella, please ensure the detailing is focused and appropriately scaled for a shorter overall work, while still being comprehensive for this specific section.")

                prompt_lines.extend([
                    f"\n\nFor the **{current_section_name_for_prompt}** part, please describe:\n",
                    f"- Key events and plot developments.\n",
                    f"- How characters (especially main ones) act, react, and develop.\n",
                    f"- How faction goals and conflicts manifest or progress.\n",
                    f"- The primary **location(s)** of the main action within this part. Note if the focus shifts.\n",
                    f"- The overall tone and pacing for this part.\n",
                    f"IMPORTANT: Do NOT include a title for the story or this section in your response. The title will be handled separately.\n",
                    f"Please be as detailed as possible. Provide the output in markdown format. Please do NOT use backticks in the output."
                ])
                prompt = "\n".join(prompt_lines)

                safe_structure_name_for_file = selected_structure_name.lower().replace(' ', '_').replace(':', '').replace('/', '_')
                safe_section_name_for_file = current_section_name_for_prompt.lower().replace(' ', '_').replace(':','').replace('/','_')
                prompt_base_name = f"improve_structure_{safe_structure_name_for_file}_{safe_section_name_for_file}_prompt"

                # Save the prompt for this section
                prompt_filepath = save_prompt_to_file(output_dir, prompt_base_name, prompt)
                
                if prompt_filepath:
                    self.app.logger.info(f"Prompt for section '{current_section_name_for_prompt}' (length {len(prompt)}) saved to: {prompt_filepath}")
                else:
                    self.app.logger.error(f"Failed to save prompt for section '{current_section_name_for_prompt}'. Prompt length: {len(prompt)}.")
                    if self.app.logger.isEnabledFor(logging.DEBUG):
                        self.app.logger.debug(f"Fallback: Full prompt for section '{current_section_name_for_prompt}' due to save failure:\n{prompt}")
                    else:
                        self.app.logger.warning(f"Prompt for section '{current_section_name_for_prompt}' not logged directly. Enable DEBUG for full prompt.")

                log_msg_prompt_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"
                self.app.logger.info(f"Sending prompt for section '{current_section_name_for_prompt}' {log_msg_prompt_source} to LLM ({selected_model})...")
                response = send_prompt(prompt, model=selected_model)
                
                safe_section_name_for_output = current_section_name_for_prompt.lower().replace(' ', '_').replace(':','').replace('/','_')
                output_filename_base = f"{selected_structure_name.lower().replace(' ', '_')}_{safe_section_name_for_output}.md"
                output_filename_full_path = os.path.join(output_dir, "story", "structure", output_filename_base)
                write_file(output_filename_full_path, response)
                self.app.logger.info(f"Saved details for section '{current_section_name_for_prompt}' to {output_filename_full_path}")

                # Update for the next iteration
                previous_section_content = response 
                previous_section_name_for_prompt = current_section_name_for_prompt

            self.app.logger.info("Story structure improvement process complete!")
            # show_success("Success", f"Detailed sections for '{selected_structure_name}' generated.")

        except FileNotFoundError as fnf_e:
            show_error("Error", f"File not found during structure improvement: {fnf_e}")
            # print(f"File not found: {fnf_e}") # Replaced
            self.app.logger.error(f"File not found during structure improvement: {fnf_e}", exc_info=True)
        except Exception as e:
            # print(f"Failed to improve story structure: {e}") # Replaced
            # traceback.print_exc() # Handled by logger
            self.app.logger.error(f"Failed to improve story structure: {e}", exc_info=True)
            show_error("Error", f"Failed to improve story structure: {str(e)}")

    def _outline_short_story_plot(self):
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        self.app.logger.info(f"Outlining Short Story Plot. Model: {selected_model}, Output Dir: {output_dir}")

        # --- Read Parameters ---
        if not (self.app and hasattr(self.app, 'param_ui')):
            self.app.logger.error("ParametersUI not available for short story plot outlining.")
            show_error("Error", "Cannot load story parameters.")
            return
        
        parameters = self.app.param_ui.get_current_parameters()
        selected_structure_name = parameters.get("story_structure")
        novel_title = parameters.get("novel_title", "Untitled Short Story")

        if not selected_structure_name:
            self.app.logger.error("No story structure selected in parameters. Cannot outline short story.")
            show_error("Error", "No story structure selected. Please select one in Novel Parameters.")
            return

        # --- Get Structure Sections/Stages ---
        structure_stages = STRUCTURE_SECTIONS_MAP.get(selected_structure_name)
        if not structure_stages:
            self.app.logger.error(f"Definition for structure '{selected_structure_name}' not found in STRUCTURE_SECTIONS_MAP.")
            show_error("Error", f"Cannot find definition for structure '{selected_structure_name}'.")
            return
        stages_list_str = ", ".join(structure_stages)

        # --- Load Context Files (Optional, but good for consistency) ---
        lore_content = "No lore content available."
        reconciled_arcs_content = "No character/faction arc context available."
        characters_summary = "No character roster available."
        factions_summary = "No faction overview available."

        try:
            lore_path = os.path.join(output_dir, "story", "lore", "generated_lore.md")
            if os.path.exists(lore_path):
                lore_content = open_file(lore_path)
                self.app.logger.info(f"Loaded lore from {lore_path}")
        except Exception as e:
            self.app.logger.warning(f"Could not load lore: {e}")

        try:
            # Try the new generic filename first, fall back to old filename for backward compatibility
            arcs_path = os.path.join(output_dir, "story", "planning", "reconciled_locations_arcs.md")
            if not os.path.exists(arcs_path):
                # Try legacy flat structure locations for backward compatibility
                arcs_path = os.path.join(output_dir, "reconciled_locations_arcs.md")
                if not os.path.exists(arcs_path):
                    arcs_path = os.path.join(output_dir, "reconciled_planets_arcs.md")
            if os.path.exists(arcs_path):
                reconciled_arcs_content = open_file(arcs_path)
                self.app.logger.info(f"Loaded reconciled arcs from {arcs_path}")
        except Exception as e:
            self.app.logger.warning(f"Could not load reconciled arcs file: {e}")
        
        # Basic character and faction summaries (can be expanded)
        try:
            char_json_path = os.path.join(output_dir, "story", "lore", "characters.json")
            if os.path.exists(char_json_path):
                char_data = read_json(char_json_path)
                if char_data and "characters" in char_data:
                    chars = [c.get('name', 'N/A') for c in char_data["characters"]]
                    characters_summary = f"Key Characters: {', '.join(chars[:5])}{'...' if len(chars) > 5 else ''} (see characters.json for full list)."
                self.app.logger.info(f"Loaded character data for summary from {char_json_path}")
        except Exception as e:
            self.app.logger.warning(f"Could not load characters.json for summary: {e}")

        try:
            faction_json_path = os.path.join(output_dir, "story", "lore", "factions.json")
            if os.path.exists(faction_json_path):
                faction_data = read_json(faction_json_path) # Assuming read_json returns list of dicts
                if faction_data: # Check if faction_data is not None or empty
                    factions_list = [f.get('faction_name', 'N/A') for f in faction_data]
                    factions_summary = f"Key Factions: {', '.join(factions_list[:3])}{'...' if len(factions_list) > 3 else ''} (see factions.json for full list)."
                self.app.logger.info(f"Loaded faction data for summary from {faction_json_path}")
        except Exception as e:
            self.app.logger.warning(f"Could not load factions.json for summary: {e}")


        # --- Construct the Prompt ---
        prompt_lines = [
            f"You are an AI assistant helping to outline the detailed plot for a short story titled '{novel_title}'.",
            f"The story will follow the '{selected_structure_name}' framework. The stages of this structure are: {stages_list_str}.",
            "Please generate a single, continuous, detailed plot that covers all these stages from beginning to end.\n",
            "For each stage of the structure, describe in detail:\n",
            "  - Key events and plot developments.\n",
            "  - How characters (especially main ones) act, react, and develop.\n",
            "  - How any relevant faction goals or conflicts manifest or progress.\n",
            "  - The primary location(s) of the main action within this stage.\n",
            "  - The overall tone and pacing for this stage.\n\n",
            "Ensure the plot flows logically and cohesively from one stage to the next, building towards the story's climax and resolution.",
            "\n## Overall Universe Lore Context:",
            lore_content,
            f"\n## Character Arcs & Faction Context (from {os.path.basename(arcs_path) if 'arcs_path' in locals() else 'reconciled arcs file'}, if available):",
            reconciled_arcs_content,
            "\n## Key Characters Summary:",
            characters_summary,
            "\n## Key Factions Summary:",
            factions_summary,
            f"IMPORTANT: Do NOT include a title for the story in your response. The title will be handled separately.\\n",
            f"\\nPlease provide the complete, detailed plot for the short story '{novel_title}' using the '{selected_structure_name}' ({stages_list_str}) now. The output should be a single markdown document."
        ]
        prompt = "\n".join(prompt_lines)

        safe_structure_name_for_file = selected_structure_name.lower().replace(' ', '_').replace(':', '').replace('/', '_')
        prompt_base_name = f"outline_short_story_plot_{safe_structure_name_for_file}_prompt"
        
        prompt_filepath = save_prompt_to_file(output_dir, prompt_base_name, prompt)
        if prompt_filepath:
            self.app.logger.info(f"Short Story Plot Outline Prompt (length {len(prompt)}) saved to: {prompt_filepath}")
        else:
            self.app.logger.error(f"Failed to save Short Story Plot Outline Prompt. Length: {len(prompt)}.")
            if self.app.logger.isEnabledFor(logging.DEBUG):
                self.app.logger.debug(f"Fallback: Full Short Story Plot Outline Prompt due to save failure:\n{prompt}")
            else:
                self.app.logger.warning("Short Story Plot Outline Prompt not logged directly. Enable DEBUG for full prompt.")

        log_msg_prompt_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"
        self.app.logger.info(f"Sending Short Story Plot Outline Prompt {log_msg_prompt_source} to LLM ({selected_model})...")
        
        response = send_prompt(prompt, model=selected_model)

        if not response:
            self.app.logger.error(f"Failed to generate short story plot from LLM ({selected_model}). No response.")
            show_error("Error", "Failed to generate short story plot from LLM.")
            return
        
        self.app.logger.info(f"Received short story plot from LLM. Length: {len(response)} chars.")
        
        output_filename_base = f"plot_short_story_{safe_structure_name_for_file}.md"
        output_filename_full_path = os.path.join(output_dir, "story", "structure", output_filename_base)
        
        try:
            write_file(output_filename_full_path, response)
            self.app.logger.info(f"Short story plot saved successfully to {output_filename_full_path}")
            # show_success("Success", f"Short story plot generated and saved to {output_filename_full_path}")
        except Exception as e:
            self.app.logger.error(f"Error saving short story plot to {output_filename_full_path}: {e}", exc_info=True)
            show_error("Error", f"Failed to save short story plot: {e}")
