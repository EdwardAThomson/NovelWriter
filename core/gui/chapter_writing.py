from tkinter import ttk, messagebox
from core.gui.notifications import show_success, show_error
from core.generation.ai_helper import send_prompt
import re
from core.generation.helper_fns import open_file, write_file, save_prompt_to_file, read_json
import os
from core.gui.parameters import STRUCTURE_SECTIONS_MAP # Import for section mapping

class ChapterWriting:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app  # Store the app instanc
        
        # Frame setup for chapter writing UI
        self.chapter_writing_frame = ttk.Frame(parent)
        self.chapter_writing_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.chapter_writing_frame, text="Write Chapters", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Entry to select chapter number
        self.chapter_label = ttk.Label(self.chapter_writing_frame, text="Enter Chapter Number:")
        self.chapter_label.pack()
        self.chapter_number_entry = ttk.Entry(self.chapter_writing_frame)
        self.chapter_number_entry.pack(pady=5)

        # Button to write chapter/story - command will be set to dispatcher
        self.write_prose_button = ttk.Button(self.chapter_writing_frame, text="Write", command=self._dispatch_prose_generation)
        self.write_prose_button.pack(pady=20)

        # Button to re-write chapter - initially hidden
        self.rewrite_button = ttk.Button(self.chapter_writing_frame, text="Re-Write", command=self.rewrite_chapter)
        # self.rewrite_button.pack(pady=20) # Keep hidden for now
        self.rewrite_button.pack_forget() # Explicitly hide

        # Separator for automation section
        separator = ttk.Separator(self.chapter_writing_frame, orient='horizontal')
        separator.pack(fill='x', pady=20)

        # Automation section label
        automation_label = ttk.Label(self.chapter_writing_frame, text="Automated Chapter Writing", font=("Helvetica", 14, "bold"))
        automation_label.pack(pady=(10, 5))

        # Progress display frame
        self.progress_frame = ttk.Frame(self.chapter_writing_frame)
        self.progress_frame.pack(pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Progress: Analyzing...")
        self.progress_label.pack()

        # Automation buttons frame
        automation_buttons_frame = ttk.Frame(self.chapter_writing_frame)
        automation_buttons_frame.pack(pady=10)

        # Button to analyze chapters
        self.analyze_button = ttk.Button(automation_buttons_frame, text="📊 Analyze Chapters", command=self.analyze_chapters)
        self.analyze_button.pack(side="left", padx=5)

        # Button to write next chapter
        self.write_next_button = ttk.Button(automation_buttons_frame, text="✍️ Write Next Chapter", command=self.write_next_chapter)
        self.write_next_button.pack(side="left", padx=5)

        # Button to write all remaining chapters
        self.write_all_button = ttk.Button(automation_buttons_frame, text="🚀 Write All Chapters", command=self.write_all_chapters)
        self.write_all_button.pack(side="left", padx=5)

        # Initialize progress display
        self.update_progress_display()

        # Register callback and call for initial setup
        if self.app and hasattr(self.app, 'param_ui') and hasattr(self.app.param_ui, 'add_callback'):
            self.app.param_ui.add_callback(self._update_ui_based_on_parameters)
        self._update_ui_based_on_parameters() # Set initial UI state

    def _update_ui_based_on_parameters(self):
        """Updates UI elements based on current story parameters."""
        if not (self.app and hasattr(self.app, 'param_ui') and 
                hasattr(self.app.param_ui, 'get_current_parameters') and 
                callable(self.app.param_ui.get_current_parameters)):
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.info("ChapterWriting: Parameters.py not fully available for UI update.")
            return

        try:
            params = self.app.param_ui.get_current_parameters()
            story_length = params.get("story_length")
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.info(f"ChapterWriting._update_ui: story_length = '{story_length}'")
        except Exception as e:
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.error(f"ChapterWriting: Error getting parameters: {e}", exc_info=True)
            return

        if story_length == "Short Story":
            self.chapter_label.pack_forget()
            self.chapter_number_entry.pack_forget()
            self.write_prose_button.config(text="Write Short Story")
            self.rewrite_button.pack_forget() # Ensure rewrite is hidden for short story
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.debug("ChapterWriting: Configured for Short Story.")
        elif story_length in ["Novella", "Novel (Standard)", "Novel (Epic)"]:
            self.chapter_label.pack(pady=(10,0)) # Re-pack if previously hidden
            self.chapter_number_entry.pack(pady=5) # Re-pack
            self.write_prose_button.config(text="Write Chapter")
            # self.rewrite_button.pack(pady=20) # Decide later if rewrite is shown for longer forms
            self.rewrite_button.pack_forget() # Keep hidden for now for long form too
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.debug(f"ChapterWriting: Configured for {story_length}.")
        else: # Default or unknown
            self.chapter_label.pack(pady=(10,0)) 
            self.chapter_number_entry.pack(pady=5)
            self.write_prose_button.config(text="Write")
            self.rewrite_button.pack_forget()
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.debug(f"ChapterWriting: Configured for default/unknown story length '{story_length}'.")
                
    def _dispatch_prose_generation(self):
        """Dispatches to the correct prose generation method based on story length."""
        if not (self.app and hasattr(self.app, 'param_ui')):
            self.app.logger.error("ChapterWriting: Parameters.py not available for dispatching prose generation.")
            show_error("Error", "Cannot determine story parameters for prose generation.")
            return

        params = self.app.param_ui.get_current_parameters()
        story_length = params.get("story_length")
        self.app.logger.info(f"ChapterWriting: Dispatching prose generation for story length: {story_length}")

        if story_length == "Short Story":
            self._write_short_story_prose()
        elif story_length in ["Novella", "Novel (Standard)", "Novel (Epic)"]:
            self.write_chapter() # Existing function, to be refactored
        else:
            self.app.logger.error(f"ChapterWriting: Unknown story length '{story_length}' for prose generation.")
            show_error("Error", f"ChapterWriting: Unsupported story length '{story_length}'.")
            
    def _write_short_story_prose(self):
        """Generates the full prose for a short story, scene by scene."""
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        self.app.logger.info(f"Initiating short story prose generation. Model: {selected_model}, Output Dir: {output_dir}")

        try:
            parameters = self.app.param_ui.get_current_parameters()
            novel_title = parameters.get("novel_title", "Untitled Short Story")
            selected_structure_name = parameters.get("story_structure")

            if not selected_structure_name:
                self.app.logger.error("No story structure selected. Cannot determine input file for short story prose.")
                show_error("Error", "No story structure selected in parameters.")
                return

            # 1. Determine and Read Input File (scene plan for the short story)
            safe_structure_name = selected_structure_name.lower().replace(' ', '_').replace(':', '').replace('/', '_')
            scene_plan_filename = f"scenes_short_story_{safe_structure_name}.md"
            scene_plan_filepath = os.path.join(output_dir, "story", "planning", scene_plan_filename)

            self.app.logger.info(f"Attempting to load scene plan from: {scene_plan_filepath}")
            try:
                scene_plan_content = open_file(scene_plan_filepath)
                if not scene_plan_content.strip():
                    self.app.logger.error(f"Scene plan file '{scene_plan_filename}' is empty.")
                    show_error("Error", f"The scene plan file '{scene_plan_filename}' is empty. Cannot generate prose.")
                    return
            except FileNotFoundError:
                self.app.logger.error(f"Scene plan file not found: {scene_plan_filepath}")
                show_error("Error", f"Scene plan file '{scene_plan_filename}' not found. Please generate scenes first via the 'Scene Planning' tab.")
                return
            except Exception as e:
                self.app.logger.error(f"Error reading scene plan file '{scene_plan_filepath}': {e}", exc_info=True)
                show_error("Error", f"Could not read the scene plan file: {e}")
                return

            # 2. Parse Individual Scenes from the scene_plan_content
            # Assuming scenes are separated by "### Scene X:" or similar.
            # We'll split by the scene heading, keeping the heading with its content.
            # Regex to find scene headings like "### Scene 1: Title" or "### Scene 1"
            # The split will result in: [content_before_first_scene_heading, heading1, content_after_heading1, heading2, content_after_heading2, ...]
            # We need to combine heading with its content.
            
            # --- New parsing logic using re.finditer --- 
            parsed_scenes = []
            # Pattern to match both colon and dash formats with optional space:
            heading_pattern = r'^## Scene \d+\s*[:\-].*$' 
            self.app.logger.debug(f"Using ULTRA-SPECIFIC heading_pattern: {heading_pattern}")

            # Log the beginning of the content that finditer will process
            self.app.logger.debug(f"Scene Plan Content (first 500 chars) for finditer:\n---\n{scene_plan_content[:500]}\n---\n")

            matches = []
            for match in re.finditer(heading_pattern, scene_plan_content, flags=re.MULTILINE):
                matches.append((match.start(), match.end(), match.group(0).strip())) # Store start, end, and stripped heading text
            
            self.app.logger.debug(f"Found {len(matches)} scene headings using finditer.")

            if not matches:
                self.app.logger.warning(f"Could not find any scene headings in '{scene_plan_filename}'. Treating entire content as one scene.")
                if scene_plan_content.strip():
                    parsed_scenes.append(scene_plan_content.strip())
            else:
                # Check for content before the first heading
                first_heading_start_index = matches[0][0]
                if first_heading_start_index > 0:
                    pre_content = scene_plan_content[0:first_heading_start_index].strip()
                    if pre_content:
                        self.app.logger.debug(f"Found pre-heading content: {pre_content[:100].replace('\\n',' ')}...")
                        parsed_scenes.append(pre_content) # Add content before the first heading

                # Iterate through matches to construct scenes
                for i in range(len(matches)):
                    heading_start, heading_end, heading_text = matches[i]
                    
                    # Content for this scene starts AT the heading_start (to include the heading itself)
                    # and ends just before the next heading, or at the end of the file.
                    content_block_start_index = heading_start # Include the heading in the scene block
                    content_block_end_index = len(scene_plan_content) # Default to end of file
                    
                    if i + 1 < len(matches): # If there's a next heading
                        content_block_end_index = matches[i+1][0] # End before the next heading starts
                    
                    scene_text_with_heading = scene_plan_content[content_block_start_index:content_block_end_index].strip()
                    
                    if scene_text_with_heading: # Ensure we're not adding empty strings
                        parsed_scenes.append(scene_text_with_heading)
                        self.app.logger.debug(f"Parsed scene {len(parsed_scenes)} (heading: '{heading_text[:100].replace('\\n',' ')}...'). Length: {len(scene_text_with_heading)}.")
                    else:
                        self.app.logger.debug(f"Skipping empty scene block for heading: '{heading_text[:100].replace('\\n',' ')}...'")
            # --- End of new parsing logic ---
            
            if not parsed_scenes:
                self.app.logger.error(f"Could not parse any scenes from '{scene_plan_filename}'. Check scene heading format (e.g., '### Scene 1: Title').")
                show_error("Error", "Could not parse scenes from the plan. Ensure scenes start with '### Scene X: ...' or '**Scene X: ...**'.")
                return

            self.app.logger.info(f"Successfully parsed {len(parsed_scenes)} scenes from '{scene_plan_filename}'.")
            for idx, scene_text in enumerate(parsed_scenes):
                self.app.logger.debug(f"Parsed Scene {idx+1} Content (first 100 chars): {scene_text[:100].replace('\n', ' ')}...")
            
            # --- Load Contextual Information (Lore, Characters, Factions) ---
            lore_content = "Lore context is missing or not loaded."
            try:
                lore_path = os.path.join(output_dir, "story", "lore", "generated_lore.md")
                if os.path.exists(lore_path):
                    lore_content = open_file(lore_path)
                    self.app.logger.info(f"Loaded lore context from {lore_path}")
            except Exception as e:
                self.app.logger.warning(f"Could not load lore for short story prose: {e}")

            character_roster_summary = "Character roster not available."
            try:
                characters_json_path = os.path.join(output_dir, "characters.json")
                if os.path.exists(characters_json_path):
                    characters_data = read_json(characters_json_path) # Assuming read_json is in helper_fns
                    if characters_data and "characters" in characters_data:
                        summaries = []
                        for char_info in characters_data["characters"]:
                            details = [f"\n\n Name: {char_info.get('name', 'N/A')}\n"]
                            details.append(f" - Role: {char_info.get('role', 'N/A')}\n")
                            details.append(f" - Gender: {char_info.get('gender', 'N/A')}\n")
                            details.append(f" - Age: {char_info.get('age', 'N/A')}\n")
                            details.append(f" - Appearance: {char_info.get('appearance_summary', 'N/A')}\n")
                            goals = char_info.get('goals', [])
                            if goals: details.append(f" -    Primary Goal: {goals[0] if goals else 'N/A'}\n")
                            strengths = char_info.get('strengths', [])
                            if strengths: details.append(f" -    Key Strength: {strengths[0] if strengths else 'N/A'}\n")
                            flaws = char_info.get('flaws', [])
                            if flaws: details.append(f" -    Key Flaw: {flaws[0] if flaws else 'N/A'}\n")
                            backstory = char_info.get('backstory_summary', '')
                            if backstory: details.append(f" -    Backstory Summary: {backstory}")
                            summaries.append("\n".join(details))
                        if summaries:
                            character_roster_summary = "Key Characters:\n" + "\n".join(summaries)
                            self.app.logger.info(f"Loaded and summarized character roster from {characters_json_path}")
            except Exception as e:
                self.app.logger.warning(f"Could not load or process character roster from {characters_json_path}: {e}", exc_info=True)
            # --- Load Faction Summary ---
            faction_summary_info = "Faction information not available."
            try:
                factions_json_path = os.path.join(output_dir, "story", "lore", "factions.json")
                if os.path.exists(factions_json_path):
                    factions_data = read_json(factions_json_path) # Assuming read_json is from helper_fns
                    if factions_data: # Assuming factions_data is a list of faction dicts
                        summaries = []
                        for faction_info in factions_data[:5]: # Limit to top 5 for prompt brevity
                            details = [f"\n\n Faction Name: {faction_info.get('faction_name', 'N/A')}\n"]
                            details.append(f" - Profile: {faction_info.get('faction_profile', 'N/A')}\n")
                            traits = faction_info.get('primary_traits', [])
                            if traits: details.append(f" - Primary Traits: {', '.join(traits)}\n")
                            summaries.append("\n".join(details))
                        if summaries:
                            faction_summary_info = "Key Factions Overview:\n" + "\n".join(summaries)
                            self.app.logger.info(f"Loaded and summarized faction info from {factions_json_path}")
            except Exception as e:
                self.app.logger.warning(f"Could not load or process faction info from {factions_json_path}: {e}", exc_info=True)

            # --- Loop Through Scenes and Generate Prose ---
            all_generated_prose = []
            for scene_index, single_scene_description in enumerate(parsed_scenes):
                self.app.logger.info(f"Processing Scene {scene_index + 1}/{len(parsed_scenes)} for prose generation.")
                
                title_line = f"You are an AI assistant helping to write a science fiction short story titled '{novel_title}'."
                if not novel_title or novel_title == "Untitled Short Story":
                    title_line = "You are an AI assistant helping to write a science fiction short story."

                prompt_lines = [
                    title_line,
                    f"The story follows the '{selected_structure_name}' framework.",
                    "I will provide you with the description for a single scene. Please write the full prose for this scene.",
                    "Focus ONLY on the current scene description provided below. Do not try to write other scenes or summarize the story.",
                    "\n## Current Scene Description:",
                    single_scene_description,
                    "\n## Overall Story Context (for your reference):"
                ]
                if novel_title and novel_title != "Untitled Short Story":
                    prompt_lines.append(f"Title: {novel_title}")
                prompt_lines.append(f"Structure: {selected_structure_name}")
                prompt_lines.append(f"Full Universe Lore: {lore_content}") # Full lore
                prompt_lines.append(f"\n{character_roster_summary}") # Detailed character roster
                prompt_lines.append(f"\n{faction_summary_info}")   # Faction summary

                prompt_lines.extend([
                    "\n## Instructions for Writing This Scene:",
                    " - Write engaging and descriptive prose for this scene.",
                    " - Include character actions, dialogue (if appropriate for the scene description), thoughts, and emotions, consistent with their profiles in the roster.",
                    " - Ensure the setting is clear.",
                    " - The scene should flow logically and advance the plot or character development as indicated in its description.",
                    " - Adhere strictly to the provided 'Full Universe Lore Context' for all world-building details (e.g., planetary features, technology, species). Do not introduce new significant details not found in the lore or this scene's description.",
                    " - If specific details (e.g., number of suns/moons for a planet) are not present in the lore, use generic descriptions (e.g., 'the sun set') or omit such details rather than inventing new canonical facts.",
                    " - Provide ONLY the prose for this scene. Do NOT add any extra commentary, scene numbers, or titles yourself. I will handle the final assembly.",
                    " - Do NOT use backticks."
                ])
                prompt = "\n".join(prompt_lines)

                prompt_filename_base = f"short_story_scene_{scene_index + 1}_prompt"
                prompt_filepath = save_prompt_to_file(output_dir, prompt_filename_base, prompt)
                log_msg_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"
                
                self.app.logger.info(f"Sending prompt for Scene {scene_index + 1} {log_msg_source} to LLM ({selected_model}).")
                
                try:
                    scene_prose = send_prompt(prompt, model=selected_model)
                    if not scene_prose or not scene_prose.strip():
                        self.app.logger.warning(f"LLM returned empty or whitespace-only response for Scene {scene_index + 1}.")
                        scene_prose = f"[[[LLM CAME BACK BLANK FOR SCENE {scene_index + 1}]]]" # Placeholder - corrected extra brace
                    else:
                        self.app.logger.info(f"Received prose for Scene {scene_index + 1}. Length: {len(scene_prose)} chars.")
                    all_generated_prose.append(scene_prose)
                except Exception as e_llm:
                    self.app.logger.error(f"Error calling LLM for Scene {scene_index + 1}: {e_llm}", exc_info=True)
                    all_generated_prose.append(f"[[[ERROR GENERATING SCENE {scene_index + 1}: {e_llm}]]]")
                    # Optionally, decide if we should stop or continue with other scenes
                    # For now, it continues and marks the error.

            # --- Concatenate and Save Full Story ---
            if not all_generated_prose:
                self.app.logger.error("No prose was generated for any scene. Cannot save short story.")
                show_error("Error", "No prose could be generated for the short story.")
                return

            full_story_content = "\n\n---\n\n".join(all_generated_prose) # Join scenes with a separator

            safe_title = novel_title.lower().replace(' ', '_').replace(':', '').replace('/', '')
            output_story_filename = f"prose_short_story_{safe_title}.md"
            os.makedirs(os.path.join(output_dir, "story", "content"), exist_ok=True)
            output_story_filepath = os.path.join(output_dir, "story", "content", output_story_filename)

            try:
                write_file(output_story_filepath, full_story_content)
                self.app.logger.info(f"Short story prose successfully written to: {output_story_filepath}")
                # show_success("Success", f"Short story prose generated and saved to {output_story_filename}")
            except Exception as e_write:
                self.app.logger.error(f"Error writing full short story to file '{output_story_filepath}': {e_write}", exc_info=True)
                show_error("Error", f"Failed to save the complete short story: {e_write}")

        except Exception as e:
            self.app.logger.error(f"An unexpected error occurred in _write_short_story_prose: {e}", exc_info=True)
            show_error("Error", f"An unexpected error occurred: {str(e)}")

    def normalize_markdown(self, scenes):
        # Match scene headings specifically (e.g., **Scene 1: ...**)
        normalized_scenes = re.sub(r"\*\*Scene (\d+): (.+?)\*\*", r"### Scene \1: \2", scenes)
        return normalized_scenes

    def write_chapter(self):
        selected_model = self.app.get_selected_model()
        output_dir = self.app.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)
        self.app.logger.info(f"Initiating Write Chapter. Model: {selected_model}, Output Dir: {output_dir}")

        try:
            target_chapter_number_global = int(self.chapter_number_entry.get())
            if target_chapter_number_global <= 0:
                show_error("Error", "Chapter number must be a positive integer.")
                return
            self.app.logger.info(f"Target chapter (global): {target_chapter_number_global}")

            # 1. Access Core Parameters (Structure and Length)
            parameters_file_path = os.path.join(output_dir, "system", "parameters.txt")
            selected_structure_name = "6-Act Structure" # Default
            story_length = "Novel (Standard)" # Default
            params_from_file = {}
            try:
                if not os.path.exists(parameters_file_path):
                    self.app.logger.error(f"Parameters file not found: {parameters_file_path}. Cannot determine structure for chapter writing.")
                    show_error("Error", f"Parameters file 'parameters.txt' not found in {output_dir}.")
                    return
                with open(parameters_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            params_from_file[key.strip()] = value.strip()
                loaded_structure = params_from_file.get("Story Structure")
                story_length = params_from_file.get("Story Length", story_length)
                if loaded_structure and loaded_structure.strip():
                    selected_structure_name = loaded_structure
                else:
                    self.app.logger.warning(f"'Story Structure' not found/empty in {parameters_file_path}. Using default: {selected_structure_name}")
                self.app.logger.info(f"Using structure: '{selected_structure_name}', Length: '{story_length}' for chapter writing.")
            except Exception as e_params:
                self.app.logger.error(f"Error reading parameters file ({parameters_file_path}): {e_params}. Using defaults.", exc_info=True)
                # Continue with defaults if param file reading fails, but log it.
            
            # 2. Determine the Correct Section for the Given Chapter Number
            sections_to_process = STRUCTURE_SECTIONS_MAP.get(selected_structure_name)
            if not sections_to_process:
                self.app.logger.error(f"Section definitions for '{selected_structure_name}' not found in STRUCTURE_SECTIONS_MAP.")
                show_error("Error", f"Cannot find structure definition for '{selected_structure_name}'.")
                return

            current_section_name_for_chapter = None
            chapter_count_accumulator = 0
            # chapter_number_within_section = 0 # Not strictly needed for filename, global number is used

            for section_name_iter in sections_to_process:
                safe_struct_name = selected_structure_name.lower().replace(' ', '_')
                safe_sect_name_iter = section_name_iter.lower().replace(' ', '_').replace(':','').replace('/','_')
                
                # This is the file that tells us how many chapters are in THIS section
                chapter_outline_input_base = f"chapter_outlines_{safe_struct_name}_{safe_sect_name_iter}.md"
                chapter_outline_input_filepath = os.path.join(output_dir, "story", "planning", chapter_outline_input_base)
                self.app.logger.debug(f"Checking chapter outline: {chapter_outline_input_filepath}")

                try:
                    outline_content = open_file(chapter_outline_input_filepath)
                    # Count chapters in this section's outline
                    chapters_in_this_section_outline = re.findall(r"^(?:\*{2,}|#{2,})\s*Chapter\s*(\d+)(?:[:\s\S]*?)?$", outline_content, re.MULTILINE | re.IGNORECASE)
                    num_chapters_in_section = len(chapters_in_this_section_outline)
                    self.app.logger.debug(f"Section '{section_name_iter}' has {num_chapters_in_section} chapters in its outline.")

                    if target_chapter_number_global <= chapter_count_accumulator + num_chapters_in_section:
                        current_section_name_for_chapter = section_name_iter
                        # chapter_number_within_section = target_chapter_number_global - chapter_count_accumulator
                        self.app.logger.info(f"Target chapter {target_chapter_number_global} found in section: '{current_section_name_for_chapter}'.")
                        break # Found the section
                    chapter_count_accumulator += num_chapters_in_section
                except FileNotFoundError:
                    self.app.logger.warning(f"Chapter outline file {chapter_outline_input_filepath} not found. Cannot determine chapter distribution for section '{section_name_iter}'.")
                    # This is problematic; we might not find the target chapter if outlines are missing.
                    # Consider how to handle this - for now, it will likely fail to find current_section_name_for_chapter.
                    continue # Try next section, but it's a data integrity issue.
                except Exception as e_outline:
                    self.app.logger.error(f"Error processing chapter outline {chapter_outline_input_filepath}: {e_outline}", exc_info=True)
                    continue
            
            if not current_section_name_for_chapter:
                self.app.logger.error(f"Could not determine which section target chapter {target_chapter_number_global} belongs to. Total chapters counted: {chapter_count_accumulator}.")
                show_error("Error", f"Could not locate chapter {target_chapter_number_global} within the known structure sections. Ensure all chapter outlines are generated.")
                return

            # 3. Construct the Correct Filename and Path for the detailed scene plan of the target chapter
            scene_plans_subdir_name = "detailed_scene_plans"
            safe_selected_structure_name_for_file = selected_structure_name.lower().replace(' ', '_')
            safe_current_section_name_for_file = current_section_name_for_chapter.lower().replace(' ', '_').replace(':','').replace('/','_')
            
            # The filename uses the global chapter number
            scene_plan_filename_base = f"scenes_{safe_selected_structure_name_for_file}_{safe_current_section_name_for_file}_ch{target_chapter_number_global}.md"
            scene_plan_filepath = os.path.join(output_dir, "story", "planning", scene_plans_subdir_name, scene_plan_filename_base)
            self.app.logger.info(f"Attempting to load scene plan for Chapter {target_chapter_number_global} from: {scene_plan_filepath}")

            # 4. Read the Scene File
            try:
                scenes_content_for_chapter = open_file(scene_plan_filepath)
                if not scenes_content_for_chapter.strip():
                    self.app.logger.error(f"Scene plan file '{scene_plan_filepath}' is empty.")
                    show_error("Error", f"Scene plan file for Chapter {target_chapter_number_global} is empty.")
                    return
            except FileNotFoundError:
                self.app.logger.error(f"Scene plan file not found: {scene_plan_filepath}")
                show_error("Error", f"Scene plan file for Chapter {target_chapter_number_global} not found in '{scene_plans_subdir_name}'. Ensure scenes are planned.")
                return
            except Exception as e_read_scenes:
                self.app.logger.error(f"Error reading scene plan file '{scene_plan_filepath}': {e_read_scenes}", exc_info=True)
                show_error("Error", f"Could not read scene plan for Chapter {target_chapter_number_global}: {e_read_scenes}")
                return

            # --- Original logic from here, using scenes_content_for_chapter --- 
            # params = open_file("parameters.txt") # Already loaded as params_from_file
            # lore_content = open_file(os.path.join(output_dir, "story", "lore", "generated_lore.md"))
            # characters_content = open_file("characters.md") # Not used, character roster comes from JSON below
            # en_characters_content = open_file("characters.md") # Duplicate
            # relationships_content = open_file("relationships.md") # Not used
            # factions_content = open_file("factions.md") # Not used, faction summary comes from JSON below

            # The variable `scenes` was used for `scenes_content_for_chapter`
            # `scenes_content_for_chapter` holds the content of the specific chapter's scene plan file.
            
            # Detect scenes within this chapter's plan file
            # Normalize markdown formatting (if necessary, current scene plans should be ## Scene...)
            # scenes_content_for_chapter = self.normalize_markdown(scenes_content_for_chapter) # Current parser uses ## Scene, so normalize might not be needed if input is consistent

            # Detect the number of scenes using regex from the content of the specific chapter file
            # Use the same robust pattern as _write_short_story_prose
            scene_heading_pattern_for_chapter = r'^## Scene \d+:.*$'
            scene_details_list = [] # Will store (heading, body) tuples or just full scene content strings
            
            # Using re.finditer to parse scenes within this chapter's plan
            scene_matches_in_chapter = []
            for match in re.finditer(scene_heading_pattern_for_chapter, scenes_content_for_chapter, flags=re.MULTILINE):
                scene_matches_in_chapter.append((match.start(), match.end(), match.group(0).strip()))
            
            self.app.logger.debug(f"Found {len(scene_matches_in_chapter)} scene headings in Chapter {target_chapter_number_global}'s plan file ('{scene_plan_filename_base}').")

            if not scene_matches_in_chapter:
                self.app.logger.error(f"No scene headings found within {scene_plan_filepath}. Cannot process chapter.")
                show_error("Error", f"No individual scenes found in the plan for Chapter {target_chapter_number_global}.")
                return
            
            # Construct scene_details_list from finditer matches (heading + body for each scene)
            for i in range(len(scene_matches_in_chapter)):
                heading_start, heading_end, heading_text = scene_matches_in_chapter[i]
                content_block_start_index = heading_start
                content_block_end_index = len(scenes_content_for_chapter)
                if i + 1 < len(scene_matches_in_chapter):
                    content_block_end_index = scene_matches_in_chapter[i+1][0]
                scene_text_with_heading = scenes_content_for_chapter[content_block_start_index:content_block_end_index].strip()
                if scene_text_with_heading:
                    scene_details_list.append(scene_text_with_heading)
            
            self.app.logger.info(f"Successfully parsed {len(scene_details_list)} scenes for Chapter {target_chapter_number_global} from its plan file.")

            # --- Load Character Roster Summary ---
            character_roster_summary = "Character roster not available."
            try:
                characters_json_path = os.path.join(output_dir, "story", "lore", "characters.json")
                if os.path.exists(characters_json_path):
                    characters_data = read_json(characters_json_path)
                    if characters_data and "characters" in characters_data:
                        # (Identical summarization logic as in _write_short_story_prose)
                        summaries = []
                        for char_info in characters_data["characters"]:
                            details = [f"\n\n Name: {char_info.get('name', 'N/A')}\n"]
                            details.append(f" - Role: {char_info.get('role', 'N/A')}\n")
                            details.append(f" - Gender: {char_info.get('gender', 'N/A')}\n")
                            details.append(f" - Age: {char_info.get('age', 'N/A')}\n")
                            details.append(f" - Appearance: {char_info.get('appearance_summary', 'N/A')}\n")
                            goals = char_info.get('goals', [])
                            if goals: details.append(f" -    Primary Goal: {goals[0] if goals else 'N/A'}\n")
                            strengths = char_info.get('strengths', [])
                            if strengths: details.append(f" -    Key Strength: {strengths[0] if strengths else 'N/A'}\n")
                            flaws = char_info.get('flaws', [])
                            if flaws: details.append(f" -    Key Flaw: {flaws[0] if flaws else 'N/A'}\n")
                            backstory = char_info.get('backstory_summary', '')
                            if backstory: details.append(f" -    Backstory Summary: {backstory}")
                            summaries.append("\n".join(details))
                        if summaries:
                            character_roster_summary = "Key Characters:\n" + "\n".join(summaries)
                            self.app.logger.info(f"Loaded character roster for Chapter {target_chapter_number_global}.")
            except Exception as e_char_load:
                self.app.logger.warning(f"Could not load/process character roster for Chapter {target_chapter_number_global}: {e_char_load}", exc_info=True)

            faction_summary_info = "Faction information not available."
            try:
                factions_json_path = os.path.join(output_dir, "story", "lore", "factions.json")
                if os.path.exists(factions_json_path):
                    factions_data = read_json(factions_json_path)
                    if factions_data:
                        # (Identical summarization logic as in _write_short_story_prose)
                        summaries = []
                        for faction_info in factions_data[:5]: 
                            details = [f"\n\n Faction Name: {faction_info.get('faction_name', 'N/A')}\n"]
                            details.append(f" - Profile: {faction_info.get('faction_profile', 'N/A')}\n")
                            traits = faction_info.get('primary_traits', [])
                            if traits: details.append(f" - Primary Traits: {', '.join(traits)}\n")
                            summaries.append("\n".join(details))
                        if summaries:
                            faction_summary_info = "Key Factions Overview:\n" + "\n".join(summaries)
                            self.app.logger.info(f"Loaded faction summary for Chapter {target_chapter_number_global}.")
            except Exception as e_faction_load:
                self.app.logger.warning(f"Could not load/process faction info for Chapter {target_chapter_number_global}: {e_faction_load}", exc_info=True)

            # Load lore content
            lore_content = "Lore context is missing or not loaded."
            try:
                lore_path = os.path.join(output_dir, "story", "lore", "generated_lore.md")
                if os.path.exists(lore_path):
                    lore_content = open_file(lore_path)
                    self.app.logger.info(f"Loaded lore content for Chapter {target_chapter_number_global}.")
            except Exception as e_lore_load:
                self.app.logger.warning(f"Could not load lore content for Chapter {target_chapter_number_global}: {e_lore_load}", exc_info=True)
            # --- End Context Loading --- 

            generated_scenes_for_chapter = [] # Changed from `scenes` to avoid conflict with original `scenes_content_for_chapter`

            # Iterate over the scenes parsed from the current chapter's scene plan file
            for scene_idx_in_chapter, single_scene_detail_from_plan in enumerate(scene_details_list, start=1):
                self.app.logger.info(f"Processing Scene {scene_idx_in_chapter}/{len(scene_details_list)} for Chapter {target_chapter_number_global}.")

                # Generate prompt for the API request
                # This prompt needs to be updated to be similar to _write_short_story_prose's prompt
                prompt_lines = [
                    f"You are an AI assistant helping to write Chapter {target_chapter_number_global} of a science fiction {story_length.lower()}.",
                    f"This story follows the '{selected_structure_name}' framework. We are currently in the '{current_section_name_for_chapter}' part of this structure.",
                    f"I will provide you with the detailed plan for a single scene within Chapter {target_chapter_number_global}. Please write the full prose for THIS SCENE ONLY.",
                    "Do not try to write other scenes or summarize the chapter.",
                    f"\n## Current Scene Description (Scene {scene_idx_in_chapter} of Chapter {target_chapter_number_global}):",
                    single_scene_detail_from_plan, # This is the full content for one scene from the plan file
                    "\n## Overall Story Context (for your reference):",
                    f"Full Universe Lore: {lore_content}",
                    f"\n{character_roster_summary}",
                    f"\n{faction_summary_info}",
                    "\n## Instructions for Writing This Scene:",
                    " - Write engaging and descriptive prose for this scene.",
                    " - Include character actions, dialogue (if appropriate for the scene description), thoughts, and emotions, consistent with their profiles in the roster.",
                    " - Ensure the setting is clear.",
                    " - The scene should flow logically and advance the plot or character development as indicated in its description.",
                    " - Adhere strictly to the provided 'Full Universe Lore Context' for all world-building details (e.g., planetary features, technology, species). Do not introduce new significant details not found in the lore or this scene's description.",
                    " - If specific details (e.g., number of suns/moons for a planet) are not present in the lore, use generic descriptions (e.g., 'the sun set') or omit such details rather than inventing new canonical facts.",
                    " - Provide ONLY the prose for this scene. Do NOT add any extra commentary, scene numbers, or titles yourself. I will handle the final assembly of the chapter.",
                    " - Do NOT use backticks."
                ]
                prompt = "\n".join(prompt_lines)

                prompt_filename_base = f"write_chapter_{target_chapter_number_global}_scene_{scene_idx_in_chapter}_prompt"
                prompt_filepath = save_prompt_to_file(output_dir, prompt_filename_base, prompt)
                log_msg_source = f"(from {prompt_filepath})" if prompt_filepath else "(from memory, save failed)"

                self.app.logger.info(f"Sending prompt for Chapter {target_chapter_number_global}, Scene {scene_idx_in_chapter} {log_msg_source} to LLM ({selected_model}).")
                
                try:
                    scene_prose_text = send_prompt(prompt, model=selected_model)
                    if not scene_prose_text or not scene_prose_text.strip():
                        self.app.logger.warning(f"LLM returned empty response for Chapter {target_chapter_number_global}, Scene {scene_idx_in_chapter}.")
                        scene_prose_text = f"[[[LLM CAME BACK BLANK FOR CHAPTER {target_chapter_number_global}, SCENE {scene_idx_in_chapter}]]]"
                    else:
                        self.app.logger.info(f"Received prose for Chapter {target_chapter_number_global}, Scene {scene_idx_in_chapter}. Length: {len(scene_prose_text)} chars.")
                    generated_scenes_for_chapter.append(scene_prose_text)
                except Exception as e_llm_scene:
                    self.app.logger.error(f"Error calling LLM for Chapter {target_chapter_number_global}, Scene {scene_idx_in_chapter}: {e_llm_scene}", exc_info=True)
                    generated_scenes_for_chapter.append(f"[[[ERROR GENERATING CHAPTER {target_chapter_number_global}, SCENE {scene_idx_in_chapter}: {e_llm_scene}]]]")
                
            # Combine all scenes for this chapter into one string
            chapter_content_full = "\n\n---\n\n".join(generated_scenes_for_chapter)

            # --- Create subdirectory for chapter prose output ---
            chapters_subdir_name = "chapters"
            full_chapters_subdir_path = os.path.join(output_dir, "story", "content", chapters_subdir_name)
            os.makedirs(full_chapters_subdir_path, exist_ok=True)
            # --- End subdirectory creation ---

            # Save the combined chapter to a file within the subdirectory
            chapter_filename_output = f"chapter_{target_chapter_number_global}.md"
            chapter_filepath_output = os.path.join(full_chapters_subdir_path, chapter_filename_output)
            
            write_file(chapter_filepath_output, chapter_content_full)
            self.app.logger.info(f"Chapter {target_chapter_number_global} successfully written to: {chapter_filepath_output}")
            # show_success("Success", f"Chapter {target_chapter_number_global} generated and saved to {chapter_filename_output}")

        except ValueError:
            self.app.logger.error("Invalid chapter number entered.", exc_info=True) # Log before showing messagebox
            show_error("Error", "Please enter a valid chapter number.")
        except Exception as e_main:
            self.app.logger.error(f"Failed to write chapter {target_chapter_number_global if 'target_chapter_number_global' in locals() else 'UNKNOWN'}: {e_main}", exc_info=True)
            show_error("Error", f"Failed to write chapter: {str(e_main)}")

    def rewrite_chapter(self):
        # Ensure the `try` block is correctly paired with an `except` or `finally`
        try:
            chapter_number = int(self.chapter_number_entry.get())

            # Simplified parameter loading for rewrite - assumes files are in output_dir
            output_dir = self.app.get_output_dir() # Get output_dir
            parameters = open_file(os.path.join(output_dir, "system", "parameters.txt"))
            # lore_content = open_file(os.path.join(output_dir, "generated_lore.md")) # Consider if needed for rewrite
            # characters_content = open_file(os.path.join(output_dir, "characters.md")) # Likely not needed directly if chapter text is main input
            # factions_content = open_file(os.path.join(output_dir, "factions.md")) # Likely not needed
            # structure = open_file(os.path.join(output_dir, "story_structure.md"))  # Consider if high-level structure needed

            # --- Define chapters subdirectory --- 
            chapters_subdir_name = "chapters"
            full_chapters_subdir_path = os.path.join(output_dir, "story", "content", chapters_subdir_name)
            # Ensure it exists for both reading and writing, though reading assumes it was created by write_chapter
            os.makedirs(full_chapters_subdir_path, exist_ok=True) 
            # --- End subdirectory definition ---

            chapter_filename_input = f"chapter_{chapter_number}.md"
            # Read from the chapters subdirectory
            chapter_filepath_input = os.path.join(full_chapters_subdir_path, chapter_filename_input)
            
            try:
                with open(chapter_filepath_input, "r", encoding='utf-8') as chapter_file:
                    chapter_file_in = chapter_file.read()
            except FileNotFoundError:
                self.app.logger.error(f"Chapter file to rewrite not found: {chapter_filepath_input}")
                show_error("Error", f"Chapter file '{chapter_filename_input}' not found to rewrite.")
                return
            except Exception as e_read_rewrite:
                self.app.logger.error(f"Error reading chapter file {chapter_filepath_input} for rewrite: {e_read_rewrite}", exc_info=True)
                show_error("Error", f"Could not read chapter for rewrite: {e_read_rewrite}")
                return

            self.app.logger.info(f"Trying to re-write chapter {chapter_number}....") # Changed from print
            
            # TODO: The prompt for rewrite_chapter needs more context (lore, characters, factions)
            # similar to _write_short_story_prose and the refactored write_chapter to ensure consistency.
            # For now, it uses a simpler prompt structure.
            prompt = (
                f"Please read and then re-write this scene of Chapter {chapter_number} in my novel.\n"
                f"The scene is far too short and only a rough draft of what I need. Please make it much longer."
                f"Please also check that the narrative is engaging, includes vivid descriptions, and develops the characters and plot as described.\n"
                f"As an English Professor in storytelling, Ask yourself 'what is missing?'"
                f"As a reminder, here are the story parameters:\n\n"
                f"{parameters}\n\n"
                f"When reading the text please check if there is there anything missing from the text? Such as:\n"
                f"* location descriptions (as appropriate for the genre)\n"
                f"* character dialogue\n"
                f"* character descriptions\n"
                f"* character thoughts and emotions\n"
                f"* character introspections (what are the main characters thinking about?)\n"
                f"* character actions that progress the story\n"
                f"* character interactions beyond dialogue\n\n"
                f"Here is the text for this chapter:\n\n"
                f"{chapter_file_in}"
            )

            selected_model = self.app.get_selected_model() # Use selected model
            response = send_prompt(prompt, model=selected_model) # Pass selected_model

            output_rewrite_filename = f"re_chapter_{chapter_number}.md"
            # Write to the chapters subdirectory
            output_rewrite_filepath = os.path.join(full_chapters_subdir_path, output_rewrite_filename)
            
            write_file(output_rewrite_filepath, response)
            self.app.logger.info(f"Chapter {chapter_number} re-written and saved successfully to: {output_rewrite_filepath}") # Changed from print
            show_success("Success", f"Chapter {chapter_number} RE-saved successfully to {output_rewrite_filename}")

        except ValueError:
            self.app.logger.error("Invalid chapter number entered for rewrite.", exc_info=True)
            show_error("Error", "Please enter a valid chapter number for rewrite.")
        except Exception as e_rewrite_main:
            self.app.logger.error(f"Failed to RE-write chapter {chapter_number if 'chapter_number' in locals() else 'UNKNOWN'}: {e_rewrite_main}", exc_info=True)
            show_error("Error", f"Failed to RE-write chapter: {str(e_rewrite_main)}")

    # ===== AUTOMATED CHAPTER WRITING METHODS =====
    
    def update_progress_display(self):
        """Update the progress display with current chapter status."""
        try:
            # Import here to avoid circular imports
            from agents.writing.chapter_writing_agent import get_chapter_progress
            
            output_dir = self.app.get_output_dir() if self.app else "current_work"
            progress = get_chapter_progress(output_dir, self.app)
            
            completed = progress.get('completed_chapters', 0)
            total = progress.get('total_chapters', 0)
            percentage = progress.get('completion_percentage', 0)
            next_chapter = progress.get('next_chapter')
            
            if total > 0:
                status_text = f"Progress: {completed}/{total} chapters ({percentage:.1f}%)"
                if next_chapter:
                    status_text += f" - Next: Chapter {next_chapter}"
                else:
                    status_text += " - All Complete! ✅"
            else:
                status_text = "Progress: No chapters found (run story structure first)"
                
            self.progress_label.config(text=status_text)
            
            # Update button states
            has_chapters = total > 0
            has_remaining = next_chapter is not None
            
            self.write_next_button.config(state="normal" if has_remaining else "disabled")
            self.write_all_button.config(state="normal" if has_remaining else "disabled")
            
        except Exception as e:
            self.progress_label.config(text=f"Progress: Error - {str(e)}")
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.error(f"Error updating progress display: {e}")
    
    def analyze_chapters(self):
        """Analyze the chapter structure and update progress display."""
        try:
            self.analyze_button.config(state="disabled", text="📊 Analyzing...")
            self.update_progress_display()
            
            # Import here to avoid circular imports
            from agents.writing.chapter_writing_agent import analyze_story_chapters
            
            output_dir = self.app.get_output_dir() if self.app else "current_work"
            chapter_info_list, plan = analyze_story_chapters(output_dir, self.app)
            
            total = len(chapter_info_list)
            completed = len(plan.chapters_completed)
            remaining = len(plan.chapters_to_write)
            
            message = f"Analysis Complete!\n\nTotal Chapters: {total}\nCompleted: {completed}\nRemaining: {remaining}"
            
            if remaining > 0:
                next_chapters = plan.chapters_to_write[:5]  # Show first 5
                message += f"\n\nNext to write: {', '.join(map(str, next_chapters))}"
                if len(plan.chapters_to_write) > 5:
                    message += f" (and {len(plan.chapters_to_write) - 5} more)"
            
            show_success("Chapter Analysis", message)
            
        except Exception as e:
            error_msg = f"Error analyzing chapters: {str(e)}"
            show_error("Analysis Error", error_msg)
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.error(f"Chapter analysis error: {e}")
        finally:
            self.analyze_button.config(state="normal", text="📊 Analyze Chapters")
            self.update_progress_display()
    
    def write_next_chapter(self):
        """Write the next chapter automatically."""
        try:
            self.write_next_button.config(state="disabled", text="✍️ Writing...")
            
            # Import here to avoid circular imports
            from agents.writing.chapter_writing_agent import write_next_chapters
            
            output_dir = self.app.get_output_dir() if self.app else "current_work"
            result = write_next_chapters(output_dir, batch_size=1, app_instance=self.app)
            
            if result.success:
                chapters_written = result.data.get("chapters_written", [])
                if chapters_written:
                    chapter_num = chapters_written[0]
                    # show_success("Chapter Written", f"Successfully wrote Chapter {chapter_num}!")
                else:
                    show_success("Complete", "All chapters are already written!")
                    
            else:
                show_error("Writing Error", f"Failed to write chapter: {result.message}")
                
        except Exception as e:
            error_msg = f"Error writing next chapter: {str(e)}"
            show_error("Writing Error", error_msg)
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.error(f"Next chapter writing error: {e}")
        finally:
            self.write_next_button.config(state="normal", text="✍️ Write Next Chapter")
            self.update_progress_display()
    
    def write_all_chapters(self):
        """Write all remaining chapters automatically."""
        try:
            self.write_all_button.config(state="disabled", text="🚀 Writing All...")
            
            # Import here to avoid circular imports
            from agents.writing.chapter_writing_agent import write_next_chapters
            
            output_dir = self.app.get_output_dir() if self.app else "current_work"
            
            # Write in larger batches for efficiency
            result = write_next_chapters(output_dir, batch_size=5, app_instance=self.app)
            
            if result.success:
                chapters_written = result.data.get("chapters_written", [])
                errors = result.data.get("errors", [])
                total_completed = result.data.get("total_completed", 0)
                
                message = f"Batch Writing Complete!\n\n"
                message += f"Chapters written: {len(chapters_written)}\n"
                message += f"Total completed: {total_completed}\n"
                
                if chapters_written:
                    message += f"\nNew chapters: {', '.join(map(str, chapters_written))}"
                
                if errors:
                    message += f"\n\nErrors ({len(errors)}): {'; '.join(errors[:3])}"
                    if len(errors) > 3:
                        message += f" (and {len(errors) - 3} more)"
                
                # show_success("Batch Writing Complete", message)
            else:
                show_error("Writing Error", f"Failed to write chapters: {result.message}")
                
        except Exception as e:
            error_msg = f"Error writing all chapters: {str(e)}"
            show_error("Writing Error", error_msg)
            if self.app and hasattr(self.app, 'logger'):
                self.app.logger.error(f"All chapters writing error: {e}")
        finally:
            self.write_all_button.config(state="normal", text="🚀 Write All Chapters")
            self.update_progress_display()
