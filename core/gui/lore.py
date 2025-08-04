# lore.py
import tkinter as tk
from tkinter import ttk, messagebox
from core.gui.notifications import show_success, show_error, show_warning
from core.generation.ai_helper import send_prompt
# from core.generation.rag_helper import upsert_text
import json
import os
import logging
from core.generation.helper_fns import open_file, write_file, validate_json_schema, read_json, write_json, validate_json, save_prompt_to_file
from Generators.GenreHandlers import get_genre_handler
# Character generation now handled through genre handlers
import random
from datetime import datetime

class Lore:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Add genre/subgenre display at top
        self.genre_label = ttk.Label(
            self.main_frame, 
            text="Current Genre: Not Selected",
            font=("Arial", 12, "bold")
        )
        self.genre_label.pack(pady=10)
        
        # Update the label initially
        self.update_genre_display()

        # Frame setup for relationships UI
        self.lore_frame = ttk.Frame(parent)
        self.lore_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.lore_frame, text="Lore Builder", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Add parameter input frame
        self.param_frame = ttk.LabelFrame(self.lore_frame, text="Story Parameters")
        self.param_frame.pack(pady=10, padx=10, fill="x")

        # Number of Factions input
        self.faction_frame = ttk.Frame(self.param_frame)
        self.faction_frame.pack(fill="x", padx=5, pady=5)
        self.faction_label = ttk.Label(self.faction_frame, text="Number of Factions (Max 10):")
        self.faction_label.pack(side="left", padx=5)
        self.num_factions_var = tk.StringVar(value="3")
        self.num_factions_entry = ttk.Entry(self.faction_frame, textvariable=self.num_factions_var, width=5)
        self.num_factions_entry.pack(side="left")

        # Number of Characters input
        self.char_frame = ttk.Frame(self.param_frame)
        self.char_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(self.char_frame, text="Number of Characters (Max 10):").pack(side="left", padx=5)
        self.num_chars_var = tk.StringVar(value="5")
        self.num_chars_entry = ttk.Entry(self.char_frame, textvariable=self.num_chars_var, width=5)
        self.num_chars_entry.pack(side="left")

        # Additional parameter frame
        self.extra_param_frame = ttk.Frame(self.param_frame)
        self.extra_param_label = ttk.Label(self.extra_param_frame, text="")
        self.extra_param_label.pack(side="left", padx=5)
        self.extra_param_var = tk.StringVar()
        self.extra_param_entry = ttk.Entry(self.extra_param_frame, textvariable=self.extra_param_var, width=15)
        self.extra_param_entry.pack(side="left")

        # Buttons
        # Generate Factions Button
        self.factions_button = ttk.Button(self.lore_frame, text="Generate Factions", command=self.generate_factions)
        self.factions_button.pack(pady=20)

        # Generate Characters Button
        self.characters_button = ttk.Button(self.lore_frame, text="Generate Characters", command=self.generate_characters)
        self.characters_button.pack(pady=20)

        # Generate Lore Button
        self.generate_lore_button = ttk.Button(self.lore_frame, text="Generate Lore", command=self.generate_lore)
        self.generate_lore_button.pack(pady=20)

        # Enhance Main Characters Button
        self.main_char_enh_button = ttk.Button(self.lore_frame, text="Enhance main characters", command=self.main_character_enhancement)
        self.main_char_enh_button.pack(pady=20)

        # Suggest Titles Button
        self.suggest_titles_button = ttk.Button(self.lore_frame, text="Suggest Story Titles", command=self.suggest_titles)
        self.suggest_titles_button.pack(pady=20)

        # Call update_extra_parameter after all UI elements are created
        self.update_extra_parameter()

    def update_genre_display(self):
        """Update the genre/subgenre display label"""
        try:
            params_ui = self.app.param_ui
            genre = params_ui.genre_var.get()
            subgenre = params_ui.subgenre_var.get()
            self.genre_label.config(
                text=f"Current Genre: {genre} - {subgenre}"
            )
        except AttributeError:
            self.genre_label.config(text="Current Genre: Not Connected")

    def update_extra_parameter(self):
        """Update UI based on selected subgenre"""
        self.update_genre_display()
        try:
            # Update faction label based on genre
            genre = self.app.param_ui.genre_var.get()
            try:
                genre_handler = get_genre_handler(genre)
                if genre_handler.uses_factions():
                    organization_type = genre_handler.get_organization_type()
                    if organization_type == "factions":
                        self.faction_label.config(text="Number of Factions (Max 10):")
                        self.factions_button.config(text="Generate Factions")
                    elif organization_type == "agencies":
                        self.faction_label.config(text="Number of Agencies (Max 10):")
                        self.factions_button.config(text="Generate Agencies")
                    elif organization_type == "social circles":
                        self.faction_label.config(text="Number of Social Groups (Max 10):")
                        self.factions_button.config(text="Generate Social Groups")
                    elif organization_type == "cults":
                        self.faction_label.config(text="Number of Cults/Groups (Max 10):")
                        self.factions_button.config(text="Generate Cults/Groups")
                    else:
                        self.faction_label.config(text=f"Number of {organization_type.title()} (Max 10):")
                        self.factions_button.config(text=f"Generate {organization_type.title()}")
                else:
                    # Hide faction generation for genres that don't use them
                    self.faction_frame.pack_forget()
                    self.factions_button.pack_forget()
                    return
            except ValueError:
                # Default to factions if genre handler not found
                self.faction_label.config(text="Number of Factions (Max 10):")
                self.factions_button.config(text="Generate Factions")
            
            # Ensure faction frame and button are visible for genres that use them
            if not self.faction_frame.winfo_manager():
                self.faction_frame.pack(fill="x", padx=5, pady=5, after=self.genre_label)
            if not self.factions_button.winfo_manager():
                self.factions_button.pack(pady=20, before=self.characters_button)
            
            subgenre = self.app.param_ui.subgenre_var.get()
            
            # Handle other extra parameters
            extra_params = {
                # Sci-Fi subgenres
                "Cyberpunk": "Technological Focus:",
                "Military Sci-Fi": "Conflict Scale:",
                "Post-Apocalyptic": "Disaster Type:",
                "Hard Science Fiction": "Scientific Focus:",
                "Time Travel": "Time Period Range:",
                "Alternate History": "Divergence Point:",
                "Dystopian": "Social Issue Focus:",
                # Fantasy subgenres
                "High Fantasy": "Magic System Focus:",
                "Dark Fantasy": "Horror Elements:",
                "Urban Fantasy": "Modern Setting:",
                "Sword and Sorcery": "Adventure Focus:",
                "Mythic Fantasy": "Mythological Focus:",
                "Fairy Tale": "Moral Theme:",
            }

            if subgenre in extra_params:
                self.extra_param_label.config(text=extra_params[subgenre])
                self.extra_param_frame.pack(fill="x", padx=5, pady=5)
            else:
                self.extra_param_frame.pack_forget()

        except Exception as e:
            self.app.logger.error(f"Failed to update extra parameter: {e}", exc_info=True)

# Generation functions

    # Generate list of factions and some of their details
    def generate_factions(self):
        try:
            # Get the number of factions from the UI
            num_factions = int(self.num_factions_var.get())
            
            # Get the selected gender bias percentages from ParametersUI
            params = self.app.param_ui.get_current_parameters()
            female_percentage = params.get("female_percentage", 50) # Default to 50 if not found
            male_percentage = params.get("male_percentage", 50)   # Default to 50 if not found
            genre = params.get("genre", "Sci-Fi")  # Get current genre
            subgenre = params.get("subgenre", "")  # Get current subgenre
            
            self.app.logger.info(f"Generating {genre} factions (using gender bias: Female {female_percentage}%, Male {male_percentage}%)")
            
            # Get the appropriate genre handler
            try:
                genre_handler = get_genre_handler(genre)
            except ValueError as e:
                self.app.logger.error(f"Unsupported genre: {genre}. Error: {e}")
                show_error("Error", f"Unsupported genre: {genre}")
                return
            
            # Generate factions using the genre handler
            factions = genre_handler.generate_factions(
                num_factions=num_factions,
                female_percentage=female_percentage,
                male_percentage=male_percentage,
                subgenre=subgenre
            )
            
            # Print factions to console for debugging
            if factions:
                self.app.logger.info(f"Generated {len(factions)} factions. First faction example: {factions[0].get('faction_name', 'N/A')}")
                for i, faction_data in enumerate(factions):
                    self.app.logger.debug(f"Faction {i+1} Summary:")
                    self.app.logger.debug(f"  Name: {faction_data.get('faction_name', 'N/A')}")
                    self.app.logger.debug(f"  Profile: {faction_data.get('faction_profile', 'N/A')}")
                    self.app.logger.debug(f"  Systems: {len(faction_data.get('systems', []))}")
            else:
                self.app.logger.warning("Faction generation returned no factions.")

            # Determine the output directory from the app settings
            output_dir = self.app.get_output_dir()
            os.makedirs(output_dir, exist_ok=True) # Ensure the directory exists
            
            # Construct the full filepath for factions.json
            factions_filepath = os.path.join(output_dir, "factions.json")
            
            # Save factions to file using the genre handler
            genre_handler.save_factions(factions, factions_filepath)

            self.app.logger.info(f"Generated {genre} factions and saved to {factions_filepath}")
            show_success("Success", f"Generated {genre} factions and saved successfully.")

        except AttributeError as ae:
            # This might happen if parameters_ui or gender_bias_var is not found
            self.app.logger.error(f"AttributeError in generate_factions: {ae}. UI element access issue?", exc_info=True)
            show_error("Error", f"UI Element Access Error: {str(ae)}")
        except Exception as e:
            self.app.logger.error(f"Failed to generate faction details: {e}", exc_info=True)
            show_error("Error", f"Failed to generate faction details: {str(e)}")

    # Generate a list of characters
    # Then match characters to the list of factions
    # Also generates relationships between characters?
    def generate_characters(self):
        try:
            num_chars = int(self.num_chars_var.get())
            self.app.logger.info(f"Attempting to generate {num_chars} characters.")
            
            # Get the selected gender bias percentages and genre from Parameters.py
            params = self.app.param_ui.get_current_parameters()
            female_percentage = params.get("female_percentage", 50)
            male_percentage = params.get("male_percentage", 50)
            genre = params.get("genre", "Sci-Fi")
            
            self.app.logger.info(f"Using gender bias for character generation: Female {female_percentage}%, Male {male_percentage}%")
            self.app.logger.info(f"Generating characters for genre: {genre}")
            
            # Generate characters using the genre handler system
            try:
                genre_handler = get_genre_handler(genre)
                characters = genre_handler.generate_characters(
                    num_characters=num_chars,
                    female_percentage=female_percentage,
                    male_percentage=male_percentage,
                    include_races=True  # This will be ignored by sci-fi handler, used by fantasy handler
                )
            except ValueError as e:
                self.app.logger.error(f"Unsupported genre for character generation: {genre}. Error: {e}")
                show_error("Error", f"Unsupported genre for character generation: {genre}")
                return
            
            if not characters:
                self.app.logger.error("Failed to generate characters. generate_main_characters returned empty.")
                show_error("Error", "Failed to generate characters.")
                return
            
            # Note: Characters are now generated with genre-appropriate attributes from the start
            # No post-processing needed as each generator handles its own genre-specific attributes
            
            # Print to console for debugging
            # for char in characters:
            #     print_character(char) # Replaced by logger below
            self.app.logger.info(f"Successfully generated {len(characters)} characters.")
            for i, char_data in enumerate(characters):
                # char_data is a Character object, not a dict. Access attributes directly or use getattr.
                char_name = getattr(char_data, 'name', 'N/A')
                char_role = getattr(char_data, 'role', 'N/A')
                self.app.logger.debug(f"Character {i+1}: {char_name} ({char_role})")
            
            # --- Add Gender Count for Main Characters ---
            female_main_char_count = 0
            male_main_char_count = 0
            for char_obj in characters:
                if hasattr(char_obj, 'gender'):
                    if char_obj.gender == "Female":
                        female_main_char_count += 1
                    elif char_obj.gender == "Male":
                        male_main_char_count += 1
            
            total_main_chars = len(characters)
            if total_main_chars > 0:
                female_actual_percentage = (female_main_char_count / total_main_chars) * 100
                male_actual_percentage = (male_main_char_count / total_main_chars) * 100
                self.app.logger.info(f"MAIN CHARACTER GENDER SUMMARY: Total={total_main_chars}, Females={female_main_char_count} ({female_actual_percentage:.2f}%), Males={male_main_char_count} ({male_actual_percentage:.2f}%)")
                self.app.logger.info(f"  (Expected based on input: Female {female_percentage}%, Male {male_percentage}%)")
            else:
                self.app.logger.info("MAIN CHARACTER GENDER SUMMARY: No main characters generated to summarize.")
            # --- End Gender Count ---
            
            # Save to file
            output_dir = self.app.get_output_dir()
            os.makedirs(output_dir, exist_ok=True)
            characters_filepath = os.path.join(output_dir, "characters.json")
            
            # Save using the genre handler's save function
            genre_handler.save_characters(characters, filename=characters_filepath)
            
            self.app.logger.info(f"Generated main characters and saved to {characters_filepath}")
            show_success("Success", "Generated characters and saved successfully.")

        except Exception as e:
            self.app.logger.error(f"Failed to generate character details: {e}", exc_info=True)
            show_error("Error", f"Failed to generate character details: {str(e)}")

    def _add_genre_specific_attributes(self, characters, genre_handler):
        """Add genre-specific attributes to characters based on the genre handler."""
        try:
            genre_name = genre_handler.get_genre_name()
            
            # Check if this genre uses factions/organizations
            if not genre_handler.uses_factions():
                self.app.logger.info(f"{genre_name} doesn't use traditional factions - skipping faction assignment")
                return
            
            # Load faction data to assign characters to factions/organizations
            output_dir = self.app.get_output_dir()
            factions_filepath = os.path.join(output_dir, "factions.json")
            
            factions_data = None
            try:
                factions_data = read_json(factions_filepath)
                organization_type = genre_handler.get_organization_type()
                self.app.logger.info(f"Loaded {len(factions_data)} {organization_type} for character assignment")
            except FileNotFoundError:
                self.app.logger.warning(f"No {genre_handler.get_organization_type()} file found - characters will be generated without organizational affiliations")
                return
            except Exception as e:
                self.app.logger.warning(f"Error loading {genre_handler.get_organization_type()} for character assignment: {e}")
                return
            
            if not factions_data:
                return
            
            if genre_name == "Sci-Fi":
                self._assign_scifi_attributes(characters, factions_data)
            elif genre_name == "Fantasy":
                self._assign_fantasy_attributes(characters, factions_data)
            else:
                # For other genres that use factions, assign basic faction affiliation
                self._assign_basic_faction_attributes(characters, factions_data, genre_handler)
                
        except Exception as e:
            self.app.logger.error(f"Error adding genre-specific attributes: {e}", exc_info=True)
    
    def _assign_scifi_attributes(self, characters, factions_data):
        """Assign sci-fi specific attributes like homeworld and home_system."""
        # Get list of all habitable planets
        habitable_planets = []
        for faction in factions_data:
            for system in faction.get("systems", []):
                for planet in system.get("habitable_planets", []):
                    habitable_planets.append({
                        "name": planet.get("name", "Unknown"),
                        "system": system.get("name", "Unknown"),
                        "faction": faction.get("faction_name", "Unknown")
                    })
        
        if not habitable_planets:
            self.app.logger.warning("No habitable planets found in factions data")
            return
            
        # Assign homeworld and faction to each character
        for char in characters:
            homeworld = random.choice(habitable_planets)
            char.homeworld = homeworld["name"]
            char.home_system = homeworld["system"]
            char.faction = homeworld["faction"]
            
    def _assign_fantasy_attributes(self, characters, factions_data):
        """Assign fantasy specific attributes like homeland, home_region, and race."""
        # Get list of all cities and their regions
        cities_and_regions = []
        for faction in factions_data:
            faction_race = faction.get("race", "Human")  # Get faction's race
            for region in faction.get("regions", []):
                for city in region.get("cities", []):
                    cities_and_regions.append({
                        "name": city.get("name", "Unknown"),
                        "region": region.get("name", "Unknown"),
                        "faction": faction.get("faction_name", "Unknown"),
                        "race": faction_race
                    })
        
        if not cities_and_regions:
            self.app.logger.warning("No cities found in factions data")
            return
            
        # Assign homeland, region, race, and faction to each character
        for char in characters:
            homeland_info = random.choice(cities_and_regions)
            char.homeland = homeland_info["name"]
            char.home_region = homeland_info["region"]
            char.race = homeland_info["race"]
            char.faction = homeland_info["faction"]
            
            # Add fantasy-specific attributes if they don't exist
            if not hasattr(char, 'homeland'):
                char.homeland = None
            if not hasattr(char, 'home_region'):
                char.home_region = None
            if not hasattr(char, 'race'):
                char.race = None
    
    def _assign_basic_faction_attributes(self, characters, factions_data, genre_handler):
        """Assign basic faction/organization affiliation for genres that use them."""
        organization_type = genre_handler.get_organization_type()
        
        # Extract organization names from the factions data
        organizations = []
        for faction in factions_data:
            organizations.append({
                "name": faction.get("name", "Unknown Organization"),
                "type": faction.get("type", "Unknown Type")
            })
        
        if not organizations:
            self.app.logger.warning(f"No {organization_type} found in data")
            return
            
        # Assign organization affiliation to each character
        for char in characters:
            org_info = random.choice(organizations)
            char.faction = org_info["name"]
            
            # Add organization type as an attribute for some genres
            if hasattr(char, 'organization_type') or organization_type in ['agencies', 'cults']:
                char.organization_type = org_info["type"]


   ### Generation Functions -- leveraging LLMs for content generation


    def generate_lore(self):
        """Generate lore using an internally constructed prompt and LLM"""
        self.app.logger.info("Lore generation process started.")
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        self.app.logger.info(f"Using model: {selected_model} for lore generation.")
        self.app.logger.info(f"Output directory for lore files: {output_dir}")

        try:
            # Define and create the prompts subdirectory
            prompts_subdir = os.path.join(output_dir, "prompts")
            os.makedirs(prompts_subdir, exist_ok=True)
            self.app.logger.info(f"Ensured prompts subdirectory exists at: {prompts_subdir}")

            # --- Load necessary data ---
            parameters_txt_path = os.path.join(output_dir, "parameters.txt")
            characters_json_path = os.path.join(output_dir, "characters.json")
            factions_json_path = os.path.join(output_dir, "factions.json")

            story_params = {}
            try:
                if os.path.exists(parameters_txt_path):
                    params_content = open_file(parameters_txt_path)
                    for line in params_content.splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            story_params[key.strip()] = value.strip()
                    self.app.logger.info(f"Loaded parameters from {parameters_txt_path}")
                else:
                    self.app.logger.warning(f"Parameters file not found: {parameters_txt_path}. Proceeding without detailed parameters.")
            except Exception as e:
                self.app.logger.error(f"Error loading parameters from {parameters_txt_path}: {e}", exc_info=True)


            characters = []
            try:
                all_character_data = read_json(characters_json_path)
                characters = all_character_data.get("characters", [])
                if not characters:
                    self.app.logger.warning(f"No characters found in {characters_json_path}")
                else:
                    self.app.logger.info(f"Loaded {len(characters)} characters from {characters_json_path}")
            except FileNotFoundError:
                self.app.logger.warning(f"Character file not found: {characters_json_path}")
            except (json.JSONDecodeError, ValueError) as e:
                self.app.logger.error(f"Error loading character data from {characters_json_path}: {e}", exc_info=True)

            factions = []
            try:
                factions_data = read_json(factions_json_path)
                if factions_data:
                    # Handle both direct list format and wrapped format
                    if isinstance(factions_data, list):
                        # Direct list format (used by some genres)
                        factions = factions_data
                    elif isinstance(factions_data, dict) and "factions" in factions_data:
                        # Wrapped format (used by Horror and potentially other genres)
                        factions = factions_data["factions"]
                    else:
                        # Fallback: try to use the data as-is if it's a dict with faction-like structure
                        factions = factions_data if isinstance(factions_data, list) else []
                    
                    self.app.logger.info(f"Loaded {len(factions)} factions from {factions_json_path}")
                else:
                    self.app.logger.warning(f"No factions found or empty data in {factions_json_path}")
            except FileNotFoundError:
                self.app.logger.warning(f"Faction file not found: {factions_json_path}")
            except (json.JSONDecodeError, ValueError) as e:
                self.app.logger.error(f"Error loading faction data from {factions_json_path}: {e}", exc_info=True)

            # --- Step 1: Construct the base prompt ---
            self.app.logger.info("Constructing base lore prompt...")
            prompt_lines = [
                "You are an AI assistant helping to generate the foundational lore for a new story.",
                "Based on the provided parameters, character summaries, and faction summaries, please generate a rich and detailed background for the story's universe.", # This should include:
                # "- Key historical events.",
                # "- Cultural details.",
                # "- Technological level and unique aspects.",
                # "- Potential conflicts and mysteries.",
                # "- Initial plot points or hooks.",
                "Please ensure the lore is consistent with all provided information."
            ]

            prompt_lines.append("\n## Story Parameters:")
            if story_params:
                for key, value in story_params.items():
                    prompt_lines.append(f"- {key}: {value}")
            else:
                prompt_lines.append("- (No parameters loaded)")

            prompt_lines.append("\n## Character Summaries:")
            if characters:
                for char_dict in characters:
                    name = char_dict.get('name', 'Unknown Character')
                    role = char_dict.get('role', 'Unknown Role')
                    prompt_lines.append(f"- {name} ({role})")
            else:
                prompt_lines.append("- (No characters loaded for summary)")

            prompt_lines.append("\n## Faction Summaries:")
            prompt_lines.append("\nPlease focus on the top 2 factions. The other factions will be handled later.\n")
            if factions:
                for faction_dict in factions:
                    faction_name = faction_dict.get('faction_name', 'Unknown Faction')
                    prompt_lines.append(f"- {faction_name}")
            else:
                prompt_lines.append("- (No factions loaded for summary)")
            
            # Initial prompt content is now built
            prompt = "\n".join(prompt_lines)
            
            # --- Step 2: Enhance the prompt with detailed character and faction information ---
            self.app.logger.info("Enhancing prompt with faction capitals and detailed character info...")
            if factions:
                # Get current genre and appropriate handler
                params = self.app.param_ui.get_current_parameters()
                current_genre = params.get("genre", "Sci-Fi")
                
                try:
                    genre_handler = get_genre_handler(current_genre)
                    faction_section = genre_handler.get_faction_capitals_info(factions)
                    prompt += faction_section
                except ValueError as e:
                    self.app.logger.warning(f"Could not get genre handler for {current_genre}: {e}. Skipping faction capitals.")
                    # Fallback: add basic faction names only
                    faction_section = "\n## Faction Names:\n"
                    for faction in factions:
                        faction_name = faction.get("faction_name", "Unknown Faction")
                        faction_section += f"- {faction_name}\n"
                    prompt += faction_section

            if characters:
                # Add a detailed character section to the prompt
                character_section = "\n## Detailed Character Information:\n"
                
                # Sort characters by role priority
                role_priority = {"protagonist": 0, "deuteragonist": 1, "antagonist": 2}
                # Ensure characters is a list of dicts here when loaded from JSON
                sorted_chars = sorted(characters, key=lambda x: role_priority.get(x.get("role", "").lower(), 99))
                
                for char_dict in sorted_chars: # char_dict is a dictionary from characters.json
                    char_name = char_dict.get('name', 'Unknown') # Use .get() for dict
                    char_role = char_dict.get('role', 'Unknown Role') # Use .get() for dict
                    char_section_detail = f"\n### {char_name} ({char_role}):\n"
                    
                    # Add basic information
                    basic_info = []
                    # Get character attributes from genre handler
                    try:
                        genre_handler = get_genre_handler(current_genre)
                        basic_keys = genre_handler.get_character_attributes()
                    except ValueError:
                        # Fallback to basic attributes if genre handler not found
                        basic_keys = ['gender', 'age', 'title', 'occupation', 'faction', 'faction_role', 
                                    'goals', 'motivations', 'flaws', 'strengths', 'arc']
                    
                    for key in basic_keys:
                        value = char_dict.get(key)
                        if value:
                            if isinstance(value, list):
                                basic_info.append(f"- {key.replace('_', ' ').capitalize()}: {', '.join(value)}")
                            else:
                                basic_info.append(f"- {key.replace('_', ' ').capitalize()}: {value}")
                    
                    # Add character traits (this section is now redundant since basic_keys already includes these)
                    traits = []
                    
                    family_data = char_dict.get('family', {})
                    if family_data:
                        family_info_list = ["- Family:"]
                        parents = family_data.get('parents', [])
                        if parents:
                            parents_str = ", ".join([f"{p.get('name', 'N/A')} ({p.get('relation', 'N/A')}, {p.get('gender', 'N/A')}, {p.get('status', 'N/A')})" 
                                                   for p in parents])
                            family_info_list.append(f"  - Parents: {parents_str}")
                        siblings = family_data.get('siblings', [])
                        if siblings:
                            siblings_str = ", ".join([f"{s.get('name', 'N/A')} ({s.get('relation', 'N/A')}, {s.get('gender', 'N/A')})" 
                                                    for s in siblings])
                            family_info_list.append(f"  - Siblings: {siblings_str}")
                        spouse = family_data.get('spouse')
                        if spouse and isinstance(spouse, dict):
                            family_info_list.append(f"  - Spouse: {spouse.get('name', 'N/A')} ({spouse.get('gender', 'N/A')})")
                        children_val = family_data.get('children', [])
                        if children_val:
                            children_str = ", ".join([f"{c.get('name', 'N/A')} ({c.get('relation', 'N/A')}, {c.get('gender', 'N/A')})" 
                                                    for c in children_val])
                            family_info_list.append(f"  - Children: {children_str}")
                        # Only extend traits if family_info_list has more than just the "- Family:" header
                        if len(family_info_list) > 1:
                             traits.extend(family_info_list)
                    
                    # Combine all information
                    char_section_detail += "\n".join(basic_info + traits)
                    character_section += char_section_detail

                # Add the character section to the prompt
                prompt += character_section
                
            prompt += "\n\n## Final Instructions:\nPlease ensure that the generated lore is consistent with all the character details and faction information provided above, particularly regarding gender, relationships, and personal backgrounds. The lore should reflect and respect these attributes while building the broader universe context."
            prompt += "\n\nImportant: Please generate only the lore, background, and initial plot points as requested. Do NOT include a title for the story in this response. A title will be generated and managed separately."
            prompt += "\n\nNow, generate the lore:"

            # --- Step 3: Save the final assembled prompt to a single, non-timestamped file ---
            main_lore_prompt_filepath = os.path.join(prompts_subdir, "main_lore_prompt.md")
            try:
                write_file(main_lore_prompt_filepath, prompt)
                self.app.logger.info(f"Definitive Main Lore Generation Prompt (length {len(prompt)}) saved to: {main_lore_prompt_filepath}")
            except IOError as e_write:
                self.app.logger.error(f"Failed to write Main Lore Generation Prompt to {main_lore_prompt_filepath}: {e_write}", exc_info=True)
                show_error("Error", f"Failed to save lore prompt to {main_lore_prompt_filepath}")
                return False # Stop if we can't save the prompt

            # --- Step 4: Send the enhanced prompt to the LLM ---
            self.app.logger.info(f"Sending main lore prompt from {main_lore_prompt_filepath} to LLM ({selected_model})...")
            lore_text = send_prompt(prompt, model=selected_model)
            
            if not lore_text:
                self.app.logger.error(f"Failed to generate lore from LLM ({selected_model}). Received no response.")
                show_error("Error", "Lore generation failed (LLM).")
                return False
            
            self.app.logger.info(f"Lore successfully generated by LLM. Response length: {len(lore_text)} chars.")
            # --- Step 5: Save the generated lore ---
            self.app.logger.info("Saving generated lore...")
            generated_lore_filepath = os.path.join(output_dir, "generated_lore.md")
            write_file(generated_lore_filepath, lore_text)
            
            self.app.logger.info(f"Lore successfully generated and saved to {generated_lore_filepath}")
            show_success("Success", f"Lore generated and saved to {generated_lore_filepath}.\n\nPrompt used is in {main_lore_prompt_filepath}")
            return True

        except Exception as e:
            self.app.logger.error(f"Error during lore generation process: {e}", exc_info=True)
            show_error("Error", f"Error in lore generation: {e}")
            return False


    # New function to suggest titles
    def suggest_titles(self):
        self.app.logger.info("Title suggestion process started.")
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir() # This is typically "current_work"
        # The save_prompt_to_file function will handle creating the 'prompts' subdirectory within output_dir.
        # os.makedirs(os.path.join(output_dir, "prompts"), exist_ok=True) # Ensured by save_prompt_to_file

        lore_file_path = os.path.join(output_dir, "generated_lore.md")
        params_file_path = os.path.join(output_dir, "parameters.txt")

        try:
            # 1. Load Lore Content
            if not os.path.exists(lore_file_path):
                self.app.logger.error(f"Lore file not found at {lore_file_path}. Cannot suggest titles.")
                show_error("Error", f"Lore file ({lore_file_path}) not found. Please generate lore first.")
                return
            lore_content = open_file(lore_file_path)
            self.app.logger.info(f"Loaded lore content from {lore_file_path} for title suggestion.")

            # 2. Load Parameters (for genre, subgenre, themes - optional but good context)
            story_genre = "fiction"  # Default
            story_subgenre = ""    # Default
            story_themes = ""      # Default to empty, will be updated if themes are found

            try:
                if os.path.exists(params_file_path):
                    params_content = open_file(params_file_path)
                    current_params = {}
                    for line in params_content.splitlines():
                        if ":" in line:
                            key, value = line.split(":", 1)
                            current_params[key.strip().lower().replace(' ','_')] = value.strip()
                    story_genre = current_params.get('genre', story_genre)
                    story_subgenre = current_params.get('subgenre', story_subgenre)
                    # Get theme, if it's "Not specified" or empty, story_themes will reflect that or be empty.
                    story_themes = current_params.get('theme', '').strip()
                    self.app.logger.info(f"Loaded parameters for title context: Genre='{story_genre}', Subgenre='{story_subgenre}', Theme='{story_themes}'.")
                else:
                    self.app.logger.warning(f"Parameters file not found at {params_file_path}. Proceeding without theme/genre context for titles.")
            except Exception as e_params:
                self.app.logger.warning(f"Could not parse parameters from {params_file_path} for title context: {e_params}")

            # 3. Construct the prompt for title suggestions
            # Use full lore content, no truncation
            lore_for_prompt = lore_content

            prompt_lines = [
                f"I have the following {story_subgenre} {story_genre} lore. Based on this lore and the listed themes (if any), please suggest 5-10 potential titles for this story.",
                "Please provide the titles as a simple numbered list, with each title on a new line.\n\n For example:\n",
                "1. Title One\n",
                "2. Another Great Title\n",
                "3. The Final Suggestion\n",
                "",
                "## Story Lore:", # Header changed from "Story Lore Excerpt"
                lore_for_prompt, # Using full lore
                ""
            ]
            # Conditionally add the "Key Themes" section
            if story_themes and story_themes.lower() != "not specified":
                prompt_lines.append(f"## Key Themes: {story_themes}")
                prompt_lines.append("")

            prompt_lines.append("Please provide ONLY the numbered list of titles as your response:")
            title_prompt_content = "\n".join(prompt_lines)

            # 4. Save the title suggestion prompt
            title_prompt_base_name = "title_suggestion_prompt"
            # Pass output_dir directly; save_prompt_to_file will place it in the 'prompts' subfolder by default.
            title_prompt_filepath = save_prompt_to_file(output_dir, title_prompt_base_name, title_prompt_content)

            if title_prompt_filepath:
                self.app.logger.info(f"Title suggestion prompt (length {len(title_prompt_content)}) saved to: {title_prompt_filepath}")
            else:
                self.app.logger.error(f"Failed to save title suggestion prompt. Length: {len(title_prompt_content)}.")
                # Fallback logging if needed (similar to other prompt saves)
                if self.app.logger.isEnabledFor(logging.DEBUG):
                    self.app.logger.debug(f"Fallback: Full title suggestion prompt:\n{title_prompt_content}")
                else:
                    self.app.logger.warning("Title suggestion prompt content not logged. Enable DEBUG for full prompt.")

            # 5. Send to LLM
            log_msg_prompt_source = f"(from {title_prompt_filepath})" if title_prompt_filepath else "(from memory, save failed)"
            self.app.logger.info(f"Sending title suggestion prompt {log_msg_prompt_source} to LLM ({selected_model})...")
            suggested_titles_text = send_prompt(title_prompt_content, model=selected_model)

            if not suggested_titles_text:
                self.app.logger.error("Failed to get title suggestions from LLM.")
                show_error("Error", "Could not retrieve title suggestions from the LLM.")
                return

            self.app.logger.info(f"Received title suggestions from LLM. Length: {len(suggested_titles_text)}.")

            # 6. Save suggested titles to a file
            suggested_titles_filepath = os.path.join(output_dir, "suggested_titles.md")
            try:
                write_file(suggested_titles_filepath, suggested_titles_text)
                self.app.logger.info(f"Suggested titles saved to: {suggested_titles_filepath}")
                show_success("Success", f"Title suggestions have been saved to:\n{suggested_titles_filepath}\n\nPlease review this file and then update the Novel Title in the Parameters tab.")
            except IOError as e_write:
                self.app.logger.error(f"Failed to write suggested titles to {suggested_titles_filepath}: {e_write}", exc_info=True)
                show_error("Error", f"Failed to save suggested titles to file: {e_write}")

        except FileNotFoundError as fnf_e:
            self.app.logger.error(f"File not found during title suggestion: {fnf_e}", exc_info=True)
            # Messagebox likely shown by specific file check earlier.
        except Exception as e:
            self.app.logger.error(f"An error occurred during title suggestion: {e}", exc_info=True)
            show_error("Error", f"An unexpected error occurred while suggesting titles: {str(e)}")


    # Generate background story for the main characters
    def main_character_enhancement(self):
        self.app.logger.info("Main character enhancement process started.")
        selected_model = self.app.get_selected_model() 
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)

        self.app.logger.info(f"Using model: {selected_model} for main character enhancement")
        self.app.logger.info(f"Output directory for character files: {output_dir}")

        # Construct full paths for input files
        characters_json_path = os.path.join(output_dir, "characters.json")
        generated_lore_path = os.path.join(output_dir, "generated_lore.md")

        try:
            # Load generated lore
            try:
                lore_content = open_file(generated_lore_path)
                self.app.logger.info(f"Loaded lore content from {generated_lore_path}. Length: {len(lore_content)} chars.")
            except FileNotFoundError:
                self.app.logger.warning(f"Lore file {generated_lore_path} not found. Proceeding without lore context for backstories.")
                lore_content = "No overall lore context available."
            
            # Load character data
            try:
                all_character_data = read_json(characters_json_path)
                characters = all_character_data.get("characters", [])
                if not characters:
                    self.app.logger.warning(f"No characters found in {characters_json_path}")
                    characters = []
                else:
                    self.app.logger.info(f"Loaded {len(characters)} characters for enhancement from {characters_json_path}")
                    # self.app.logger.debug(f"Raw characters loaded from JSON: {characters}") # ADDED: Log all loaded characters
            except FileNotFoundError:
                self.app.logger.error(f"Character file {characters_json_path} not found. Cannot enhance.", exc_info=True)
                show_error("Error", f"Character file {characters_json_path} not found.")
                return
            except (json.JSONDecodeError, ValueError) as e:
                self.app.logger.error(f"Error decoding JSON from {characters_json_path}: {e}. Cannot enhance.", exc_info=True)
                show_error("Error", f"Error decoding JSON from {characters_json_path}: {e}.")
                return

            # Identify and sort main characters (Protagonist, Deuteragonist, Antagonist)
            main_roles = ["protagonist", "deuteragonist", "antagonist"]
            main_chars_data = [c for c in characters if c.get("role", "").lower() in main_roles]
            role_priority = {"protagonist": 0, "deuteragonist": 1, "antagonist": 2}
            main_chars_data.sort(key=lambda x: role_priority.get(x.get("role", "").lower(), 99))

            if not main_chars_data:
                self.app.logger.warning("No Protagonist, Deuteragonist, or Antagonist found in characters.json for enhancement.")
                show_warning("Warning", "No Protagonist, Deuteragonist, or Antagonist found in characters.json.")
                return

            self.app.logger.info(f"Found main characters for enhancement (Count: {len(main_chars_data)}): {[c.get('name', 'NAME N/A') for c in main_chars_data]}")
            # self.app.logger.debug(f"Full main_chars_data content before loop: {main_chars_data}") # ADDED: Log full list before loop

            # --- Loop through main characters to generate backstories ---
            generated_backstories = {} # Store generated backstories

            for i, char_data_item in enumerate(main_chars_data): # Changed char_data to char_data_item and used enumerate
                self.app.logger.info(f"--- Iteration {i} for main character enhancement ---") # ADDED: Iteration log
                self.app.logger.debug(f"Processing char_data_item (type: {type(char_data_item)}): {char_data_item}") # ADDED: Log current item and its type
                
                char_name = char_data_item.get('name', 'Unknown Character') 
                char_role = char_data_item.get('role', 'Unknown Role')
                self.app.logger.info(f"Extracted - Name: '{char_name}', Role: '{char_role}'") # ADDED: Log extracted name/role

                self.app.logger.info(f"--- Generating backstory for: {char_name} ({char_role}) ---") # Original log line

                # Get current genre for appropriate prompt
                params = self.app.param_ui.get_current_parameters()
                current_genre = params.get("genre", "Sci-Fi")
                current_subgenre = params.get("subgenre", "")
                
                # Build the prompt
                genre_text = f"{current_subgenre} {current_genre}" if current_subgenre else current_genre
                prompt_lines = [
                    f"I am writing a {genre_text.lower()} novel and require help developing the background story for a key character: {char_name}, the {char_role}.",
                    "Please generate a detailed backstory covering their family, upbringing, significant life events, and how they came to be who they are in the story.",
                    "Incorporate elements consistent with the overall universe lore and the character's provided details, including their age, gender, and family members."
                ]

                # Add overall lore
                prompt_lines.append("\n## Overall Universe Lore:")
                prompt_lines.append(lore_content)

                # Add current character details
                prompt_lines.append(f"\n## Details for {char_name} ({char_role}):")
                
                # Add basic character information using dict.get()
                # Get character attributes from genre handler
                try:
                    genre_handler = get_genre_handler(current_genre)
                    character_keys = genre_handler.get_character_attributes()
                except ValueError:
                    # Fallback to basic attributes if genre handler not found
                    character_keys = ['age', 'gender', 'title', 'occupation', 'faction', 'faction_role', 
                                    'goals', 'motivations', 'flaws', 'strengths', 'arc']
                
                for key in character_keys:
                    value = char_data_item.get(key)
                    if value:
                        if isinstance(value, list):
                            prompt_lines.append(f"- {key.replace('_', ' ').capitalize()}: {', '.join(value)}")
                        else:
                            prompt_lines.append(f"- {key.replace('_', ' ').capitalize()}: {value}")

                # Add formatted family details using dict.get()
                family_data = char_data_item.get('family', {})
                if family_data: # Check if family_data itself is not empty
                    prompt_lines.append("- Family:")
                    parents = family_data.get('parents', [])
                    if parents:
                        parents_str = ", ".join([f"{p.get('name', 'N/A')} ({p.get('relation', 'N/A')}, {p.get('gender', 'N/A')}, {p.get('status', 'N/A')})" 
                                               for p in parents])
                        prompt_lines.append(f"  - Parents: {parents_str}")
                    
                    siblings = family_data.get('siblings', [])
                    if siblings:
                        siblings_str = ", ".join([f"{s.get('name', 'N/A')} ({s.get('relation', 'N/A')}, {s.get('gender', 'N/A')})" 
                                                for s in siblings])
                        prompt_lines.append(f"  - Siblings: {siblings_str}")

                    spouse = family_data.get('spouse') # Can be a dict or None
                    if spouse and isinstance(spouse, dict):
                        prompt_lines.append(f"  - Spouse: {spouse.get('name', 'N/A')} ({spouse.get('gender', 'N/A')})")

                    children = family_data.get('children', [])
                    if children:
                        children_str = ", ".join([f"{c.get('name', 'N/A')} ({c.get('relation', 'N/A')}, {c.get('gender', 'N/A')})" 
                                                for c in children])
                        prompt_lines.append(f"  - Children: {children_str}")

                # Add previously generated backstories for context
                if generated_backstories:
                    prompt_lines.append("\n## Context from Other Main Character Backstories:")
                    for name, story in generated_backstories.items():
                        prompt_lines.append(f"### Backstory for {name}:")
                        prompt_lines.append(story)
                        prompt_lines.append("\n---\n")
                    prompt_lines.append(f"\nPlease ensure the backstory you generate for {char_name} is consistent with or complementary to these existing backstories, creating potential connections or contrasts.")

                # Final instruction
                prompt_lines.append("\nGenerate the backstory now:")
                prompt = "\n".join(prompt_lines)
                # self.app.logger.debug(f"Backstory prompt for {char_name} (length: {len(prompt)} chars):\n{prompt}") # Old direct logging

                # Save the prompt for this character's backstory to a file
                prompt_base_name = f"background_{char_role.lower().replace(' ', '_').replace('/', '_').replace(':', '_')}_{char_name.lower().replace(' ', '_').replace('/', '_').replace(':', '_')}_prompt"
                prompt_filepath = save_prompt_to_file(output_dir, prompt_base_name, prompt)

                if prompt_filepath:
                    self.app.logger.info(f"Backstory prompt for {char_name} (length {len(prompt)}) saved to: {prompt_filepath}")
                else:
                    self.app.logger.error(f"Failed to save backstory prompt for {char_name} to a file. Prompt length: {len(prompt)}.")
                    if self.app.logger.isEnabledFor(logging.DEBUG):
                        self.app.logger.debug(f"Fallback: Full backstory prompt for {char_name} due to save failure:\n{prompt}")
                    else:
                        self.app.logger.warning(f"Backstory prompt content for {char_name} not logged directly due to length and save failure. Enable DEBUG for full prompt.")

                # Send prompt to LLM
                log_msg_prompt_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"
                self.app.logger.info(f"Sending backstory prompt for {char_name} {log_msg_prompt_source} to LLM ({selected_model})...")
                response = send_prompt(prompt, model=selected_model)

                if not response:
                    self.app.logger.warning(f"Failed to get backstory from LLM for {char_name}. Skipping.")
                    continue
                
                self.app.logger.info(f"Received backstory for {char_name}. Length: {len(response)} chars.")
                # Save the generated backstory
                # Sanitize char_role and char_name for the filename to avoid issues with spaces or special characters
                safe_char_role = char_role.lower().replace(' ', '_').replace('/', '_').replace(':', '_')
                safe_char_name = char_name.lower().replace(' ', '_').replace('/', '_').replace(':', '_')
                base_filename = f"background_{safe_char_role}_{safe_char_name}.md"
                background_filepath = os.path.join(output_dir, base_filename)
                write_file(background_filepath, response)
                self.app.logger.info(f"Saved background for {char_name} to {background_filepath}")
                
                # Store for next iteration's context
                generated_backstories[char_name] = response

            self.app.logger.info("--- Main character enhancement process complete! ---")
            show_success("Success", "Successfully generated backstories for main characters.")

        except Exception as e:
            self.app.logger.error(f"An error occurred during main character enhancement: {e}", exc_info=True)
            # import traceback # No longer needed
            # traceback.print_exc()
            show_error("Error", f"Failed to enhance main characters: {str(e)}")