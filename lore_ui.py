# lore_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from lore_generator import generate_lore_from_api

import re
import json

# class LoreUI:
#     def __init__(self, root):
#         self.root = root
#         # self.proceed_to_character = proceed_to_character
#
#         # Genre Dropdown
#         self.genre_label = ttk.Label(root, text="Genre")
#         self.genre_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
#         self.genre_var = tk.StringVar(value="Sci-Fi")
#         self.genre_dropdown = ttk.Combobox(root, textvariable=self.genre_var)
#         self.genre_dropdown['values'] = ("Fantasy", "Sci-Fi", "Romance", "Thriller", "Mystery", "Historical Fiction")
#         self.genre_dropdown.grid(row=0, column=1, padx=10, pady=5)
#
#         # Central Theme or Subject Text Field
#         self.central_theme_label = ttk.Label(root, text="Central Theme or Subject")
#         self.central_theme_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
#         self.central_theme_entry = ttk.Entry(root)
#         self.central_theme_entry.insert(0, "A hero's journey to discover their true power")  # Default value
#         self.central_theme_entry.grid(row=1, column=1, padx=10, pady=5)
#
#         # Target Audience Dropdown
#         self.target_audience_label = ttk.Label(root, text="Target Audience")
#         self.target_audience_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
#         self.target_audience_var = tk.StringVar(value="Adult")
#         self.target_audience_dropdown = ttk.Combobox(root, textvariable=self.target_audience_var)
#         self.target_audience_dropdown['values'] = ("Children", "Young Adult", "Adult")
#         self.target_audience_dropdown.grid(row=2, column=1, padx=10, pady=5)
#
#         # Key Themes Multi-Line Text Area
#         self.key_themes_label = ttk.Label(root, text="Key Themes")
#         self.key_themes_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
#         self.key_themes_text = tk.Text(root, height=5, width=40)
#         self.key_themes_text.insert("1.0", "Courage, Overcoming Adversity")  # Default value
#         self.key_themes_text.grid(row=3, column=1, padx=10, pady=5)
#
#         # Descriptive Style Preferences Dropdown
#         self.style_preferences_label = ttk.Label(root, text="Descriptive Style Preferences")
#         self.style_preferences_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
#         self.style_preferences_var = tk.StringVar(value="Descriptive")
#         self.style_preferences_dropdown = ttk.Combobox(root, textvariable=self.style_preferences_var)
#         self.style_preferences_dropdown['values'] = ("Lyrical", "Concise", "Descriptive", "Conversational")
#         self.style_preferences_dropdown.grid(row=4, column=1, padx=10, pady=5)
#
#         # Submit Button
#         self.submit_button = ttk.Button(root, text="Generate Lore", command=self.generate_lore)
#         self.submit_button.grid(row=5, column=0, columnspan=2, pady=10)

class LoreUI:
    def __init__(self, root):
        self.root = root
        # self.root.title("Sci-Fi Novel Parameter Generator")
        self.create_widgets()

    def create_widgets(self):
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create Frames for each tab
        self.genre_theme_frame = ttk.Frame(self.notebook)
        self.setting_frame = ttk.Frame(self.notebook)
        self.worldbuilding_frame = ttk.Frame(self.notebook)
        # self.characters_frame = ttk.Frame(self.notebook) # not sure I want this.
        self.plot_frame = ttk.Frame(self.notebook)
        self.narrative_style_frame = ttk.Frame(self.notebook)
        self.key_themes_frame = ttk.Frame(self.notebook)
        self.target_audience_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.genre_theme_frame, text="Genre & Theme")
        self.notebook.add(self.setting_frame, text="Setting")
        self.notebook.add(self.worldbuilding_frame, text="Worldbuilding")
        # self.notebook.add(self.characters_frame, text="Characters")
        self.notebook.add(self.plot_frame, text="Plot")
        self.notebook.add(self.narrative_style_frame, text="Narrative Style")
        self.notebook.add(self.key_themes_frame, text="Key Themes")
        self.notebook.add(self.target_audience_frame, text="Target Audience")

        # Populate each tab with relevant fields
        self.populate_genre_theme()
        self.populate_setting()
        self.populate_worldbuilding()
        # self.populate_characters()
        self.populate_plot()
        self.populate_narrative_style()
        self.populate_key_themes()
        self.populate_target_audience()

        # Submit Button
        self.submit_button = ttk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

    def populate_genre_theme(self):
        # Genre Dropdown
        genre_label = ttk.Label(self.genre_theme_frame, text="Genre")
        genre_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.genre_var = tk.StringVar(value="Sci-Fi")
        genre_dropdown = ttk.Combobox(self.genre_theme_frame, textvariable=self.genre_var)
        genre_dropdown['values'] = ("Fantasy", "Sci-Fi", "Romance", "Thriller", "Mystery", "Historical Fiction")
        genre_dropdown.grid(row=0, column=1, padx=10, pady=5)

        # Subgenre Dropdown
        subgenre_label = ttk.Label(self.genre_theme_frame, text="Subgenre")
        subgenre_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.subgenre_var = tk.StringVar(value="Space Opera")
        subgenre_dropdown = ttk.Combobox(self.genre_theme_frame, textvariable=self.subgenre_var)
        subgenre_dropdown['values'] = (
            "Hard Sci-Fi", "Space Opera", "Dystopian", "Cyberpunk", "Time Travel",
            "Alien Invasion", "Post-Apocalyptic", "Biopunk"
        )
        subgenre_dropdown.grid(row=1, column=1, padx=10, pady=5)

        # Central Theme or Subject Text Field
        central_theme_label = ttk.Label(self.genre_theme_frame, text="Central Theme or Subject")
        central_theme_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.central_theme_entry = ttk.Entry(self.genre_theme_frame, width=50)
        self.central_theme_entry.insert(0, "A hero's journey to discover their true power")  # Default value
        self.central_theme_entry.grid(row=2, column=1, padx=10, pady=5)

    def populate_setting(self):
        # Timeframe Dropdown
        timeframe_label = ttk.Label(self.setting_frame, text="Timeframe")
        timeframe_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.timeframe_var = tk.StringVar(value="Alternate Timeline")
        timeframe_dropdown = ttk.Combobox(self.setting_frame, textvariable=self.timeframe_var)
        timeframe_dropdown['values'] = ("Near Future", "Distant Future", "Alternate Timeline")
        timeframe_dropdown.grid(row=0, column=1, padx=10, pady=5)

        # Location Text Field
        location_label = ttk.Label(self.setting_frame, text="Location")
        location_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.location_entry = ttk.Entry(self.setting_frame, width=50)
        self.location_entry.insert(0, "Earth-like planet, Multiple planets, Planetary Colonies, Spaceships")  # Default value
        self.location_entry.grid(row=1, column=1, padx=10, pady=5)

        # Technological Level Dropdown
        tech_level_label = ttk.Label(self.setting_frame, text="Technological Level")
        tech_level_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.tech_level_var = tk.StringVar(value="Interstellar Travel Enabled")
        tech_level_dropdown = ttk.Combobox(self.setting_frame, textvariable=self.tech_level_var)
        tech_level_dropdown['values'] = (
            "Post-Scarcity", "Apocalyptic", "Advanced AI",
            "Robotics Dominated", "Interstellar Travel Enabled"
        )
        tech_level_dropdown.grid(row=2, column=1, padx=10, pady=5)

        # Sociopolitical Context Dropdown
        socpol_label = ttk.Label(self.setting_frame, text="Sociopolitical Context")
        socpol_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.socpol_var = tk.StringVar(value="Far-future Earth-like Democracy")
        socpol_dropdown = ttk.Combobox(self.setting_frame, textvariable=self.socpol_var)
        socpol_dropdown['values'] = (
            "Utopian", "Dystopian", "Anarchistic", "Corporatocracy", "Feudal", "Far-future Earth-like Democracy"
        )
        socpol_dropdown.grid(row=3, column=1, padx=10, pady=5)

        # Environment Text Field
        environment_label = ttk.Label(self.setting_frame, text="Environments")
        environment_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.environment_entry = ttk.Entry(self.setting_frame, width=50)
        self.environment_entry.insert(0, "Urban Metropolis, Rural Farmlands, Terraforming Zones")  # Default
        self.environment_entry.grid(row=4, column=1, padx=10, pady=5)

    def populate_worldbuilding(self):
        # Technology Text Field
        tech_label = ttk.Label(self.worldbuilding_frame, text="Key Technologies")
        tech_label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        self.tech_text = tk.Text(self.worldbuilding_frame, width=50, height=4)
        self.tech_text.insert("1.0", "Faster-than-light travel, Gene editing, Advanced AI")
        self.tech_text.grid(row=0, column=1, padx=10, pady=5)

        # Species Text Field
        species_label = ttk.Label(self.worldbuilding_frame, text="Species")
        species_label.grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.species_text = tk.Text(self.worldbuilding_frame, width=50, height=4)
        self.species_text.insert("1.0", "Humans, Aliens, Augmented Humans, Sentient Machines")
        self.species_text.grid(row=1, column=1, padx=10, pady=5)

        # Economy Text Field
        economy_label = ttk.Label(self.worldbuilding_frame, text="Economy")
        economy_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.economy_text = tk.Text(self.worldbuilding_frame, width=50, height=4)
        self.economy_text.insert("1.0", "Resource scarcity, Barter system, Replicator abundance")
        self.economy_text.grid(row=2, column=1, padx=10, pady=5)

        # Cultural Norms Text Field
        culture_label = ttk.Label(self.worldbuilding_frame, text="Cultural Norms")
        culture_label.grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        self.culture_text = tk.Text(self.worldbuilding_frame, width=50, height=4)
        self.culture_text.insert("1.0", "Religion, Art, Laws, Taboo practices")
        self.culture_text.grid(row=3, column=1, padx=10, pady=5)

        # Challenges Text Field
        challenges_label = ttk.Label(self.worldbuilding_frame, text="Challenges")
        challenges_label.grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.challenges_text = tk.Text(self.worldbuilding_frame, width=50, height=4)
        self.challenges_text.insert("1.0", "Alien threats, Interplanetary war, Rogue AI")
        self.challenges_text.grid(row=4, column=1, padx=10, pady=5)

    # def populate_characters(self):
    #     # Protagonist Text Field
    #     protagonist_label = ttk.Label(self.characters_frame, text="Protagonist")
    #     protagonist_label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
    #     self.protagonist_text = tk.Text(self.characters_frame, width=50, height=4)
    #     self.protagonist_text.insert("1.0", "Name, motivations, skills, flaws")
    #     self.protagonist_text.grid(row=0, column=1, padx=10, pady=5)
    #
    #     # Antagonist Text Field
    #     antagonist_label = ttk.Label(self.characters_frame, text="Antagonist")
    #     antagonist_label.grid(row=1, column=0, padx=10, pady=5, sticky="nw")
    #     self.antagonist_text = tk.Text(self.characters_frame, width=50, height=4)
    #     self.antagonist_text.insert("1.0", "Villains, natural forces, moral dilemmas")
    #     self.antagonist_text.grid(row=1, column=1, padx=10, pady=5)
    #
    #     # Supporting Cast Text Field
    #     supporting_label = ttk.Label(self.characters_frame, text="Supporting Cast")
    #     supporting_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
    #     self.supporting_text = tk.Text(self.characters_frame, width=50, height=4)
    #     self.supporting_text.insert("1.0", "Companions, rivals, mentors, AI sidekicks")
    #     self.supporting_text.grid(row=2, column=1, padx=10, pady=5)

    def populate_plot(self):
        # Core Conflict Text Field
        conflict_label = ttk.Label(self.plot_frame, text="Core Conflict")
        conflict_label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        self.conflict_text = tk.Text(self.plot_frame, width=50, height=4)
        self.conflict_text.insert("1.0", "Survival, exploration, rebellion, mystery")
        self.conflict_text.grid(row=0, column=1, padx=10, pady=5)

        # Inciting Incident Text Field
        inciting_label = ttk.Label(self.plot_frame, text="Inciting Incident")
        inciting_label.grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.inciting_text = tk.Text(self.plot_frame, width=50, height=4)
        self.inciting_text.insert("1.0", "Event that disrupts the status quo")
        self.inciting_text.grid(row=1, column=1, padx=10, pady=5)

        # Goals Text Field
        goals_label = ttk.Label(self.plot_frame, text="Goals")
        goals_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.goals_text = tk.Text(self.plot_frame, width=50, height=4)
        self.goals_text.insert("1.0", "Saving humanity, uncovering a conspiracy")
        self.goals_text.grid(row=2, column=1, padx=10, pady=5)

        # Obstacles Text Field
        obstacles_label = ttk.Label(self.plot_frame, text="Obstacles")
        obstacles_label.grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        self.obstacles_text = tk.Text(self.plot_frame, width=50, height=4)
        self.obstacles_text.insert("1.0", "Challenges, enemies, self-doubt")
        self.obstacles_text.grid(row=3, column=1, padx=10, pady=5)

        # Resolution Text Field
        resolution_label = ttk.Label(self.plot_frame, text="Resolution")
        resolution_label.grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.resolution_text = tk.Text(self.plot_frame, width=50, height=4)
        self.resolution_text.insert("1.0", "Triumphant") #also:  tragic, open-ended, etc.
        self.resolution_text.grid(row=4, column=1, padx=10, pady=5)

    def populate_narrative_style(self):
        # Point of View Dropdown
        pov_label = ttk.Label(self.narrative_style_frame, text="Point of View")
        pov_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.pov_var = tk.StringVar(value="Third-person Omniscient")
        pov_dropdown = ttk.Combobox(self.narrative_style_frame, textvariable=self.pov_var)
        pov_dropdown['values'] = ("First-person", "Third-person Limited", "Third-person Omniscient", "Epistolary")
        pov_dropdown.grid(row=0, column=1, padx=10, pady=5)

        # Tense Dropdown
        tense_label = ttk.Label(self.narrative_style_frame, text="Tense")
        tense_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.tense_var = tk.StringVar(value="Present")
        tense_dropdown = ttk.Combobox(self.narrative_style_frame, textvariable=self.tense_var)
        tense_dropdown['values'] = ("Past", "Present", "Future")
        tense_dropdown.grid(row=1, column=1, padx=10, pady=5)

        # Structure Dropdown
        structure_label = ttk.Label(self.narrative_style_frame, text="Structure")
        structure_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.structure_var = tk.StringVar(value="Linear")
        structure_dropdown = ttk.Combobox(self.narrative_style_frame, textvariable=self.structure_var)
        structure_dropdown['values'] = ("Linear", "Non-linear", "Multi-POV", "Episodic")
        structure_dropdown.grid(row=2, column=1, padx=10, pady=5)

    def populate_key_themes(self):
        # Key Themes Text Field
        themes_label = ttk.Label(self.key_themes_frame, text="Key Themes and Messages")
        themes_label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        self.themes_text = tk.Text(self.key_themes_frame, width=50, height=10)
        self.themes_text.insert("1.0", "AI, Transhumanism, Nature of consciousness")
        self.themes_text.grid(row=0, column=1, padx=10, pady=5)

    def populate_target_audience(self):
        # Target Audience Dropdown
        audience_label = ttk.Label(self.target_audience_frame, text="Target Audience")
        audience_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.audience_var = tk.StringVar(value="Adult")
        audience_dropdown = ttk.Combobox(self.target_audience_frame, textvariable=self.audience_var)
        audience_dropdown['values'] = ("Young Adult (YA)", "Adult", "Niche (e.g., Cyberpunk, Military Sci-Fi)")
        audience_dropdown.grid(row=0, column=1, padx=10, pady=5)

    def submit(self):
        # Gather all input data
        data = {
            "Genre": self.genre_var.get(),
            "Subgenre": self.subgenre_var.get(),
            "Central Theme": self.central_theme_entry.get(),
            "Timeframe": self.timeframe_var.get(),
            "Location": self.location_entry.get(),
            "Technological Level": self.tech_level_var.get(),
            "Sociopolitical Context": self.socpol_var.get(),
            "Environments": self.environment_entry.get(),
            "Key Technologies": self.tech_text.get("1.0", tk.END).strip(),
            "Species": self.species_text.get("1.0", tk.END).strip(),
            "Economy": self.economy_text.get("1.0", tk.END).strip(),
            "Cultural Norms": self.culture_text.get("1.0", tk.END).strip(),
            "Challenges": self.challenges_text.get("1.0", tk.END).strip(),
            # "Protagonist": self.protagonist_text.get("1.0", tk.END).strip(),
            # "Antagonist": self.antagonist_text.get("1.0", tk.END).strip(),
            # "Supporting Cast": self.supporting_text.get("1.0", tk.END).strip(),
            "Core Conflict": self.conflict_text.get("1.0", tk.END).strip(),
            "Inciting Incident": self.inciting_text.get("1.0", tk.END).strip(),
            "Goals": self.goals_text.get("1.0", tk.END).strip(),
            "Obstacles": self.obstacles_text.get("1.0", tk.END).strip(),
            "Resolution": self.resolution_text.get("1.0", tk.END).strip(),
            "Point of View": self.pov_var.get(),
            "Tense": self.tense_var.get(),
            "Structure": self.structure_var.get(),
            "Key Themes and Messages": self.themes_text.get("1.0", tk.END).strip(),
            "Target Audience": self.audience_var.get(),
        }

        # For demonstration, we'll just show the collected data in a messagebox
        # In a real application, you might want to save this data to a file or use it further
        summary = "\n".join([f"{key}: {value}" for key, value in data.items()])
        # messagebox.showinfo("Collected Parameters", summary)
        print(summary)

        print("Writing parameters to file....")
        with open("parameters.txt", "w") as file:
                 file.write(summary)

        # make API request
        try:
            # Generate lore from API
            print("trying to make an API request")
            generated_lore = generate_lore_from_api(data)

            # Save the generated lore to a file
            with open("generated_lore.md", "w") as file:
                 file.write(generated_lore)

            # # DEBUG: Print the entire generated response to ensure it is complete
            print("Generated Lore Response:")
            print(generated_lore)

## first attempt at parsing
            # Extract Major Factions and Key Characters sections
#            factions_match = re.search(r'## Major Factions\n(.*?)(?=\n##|$)', generated_lore, re.DOTALL)
            # factions_match = re.search(r'## Major Factions\n(.*)\n##', generated_lore, re.DOTALL)
            # factions_match = re.search(r'## Major Factions\n(.*?)\n##', generated_lore, re.DOTALL)
#            characters_match = re.search(r'## Key Characters\n(.*)', generated_lore, re.DOTALL)

#            factions = factions_match.group(1).strip() if factions_match else ""
#            characters = characters_match.group(1).strip() if characters_match else ""


## second attempt at parsing
            # Split the content based on double hashtags, which indicates the major sections
            sections = re.split(r'(?m)^## ', generated_lore)

            # Dictionary to store the content of each section
            parsed_sections = {}

            # Iterate through the split sections
            for section in sections:
                if section.strip():
                    # Extract the title and content
                    lines = section.splitlines()
                    title = lines[0].strip()
                    content = "\n".join(lines[1:]).strip()

                    # Store the content by title
                    parsed_sections[title] = content

            # Extract the content for "Major Factions" and "Key Characters"
            factions = parsed_sections.get("Major Factions", "")
            characters = parsed_sections.get("Key Characters", "")


            # Save factions and characters to file
            # Save Major Factions to a file
            with open("major_factions.md", "w") as factions_file:
                factions_file.write(f"## Major Factions\n{factions}")
            print("Major factions saved to major_factions.md")

            # Save Key Characters to a file
            with open("characters.md", "w") as characters_file:
                characters_file.write(f"## Key Characters\n{characters}")
            print("Key characters saved to key_characters.md")



        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

