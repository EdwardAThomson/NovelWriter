from tkinter import ttk, messagebox
from ai_helper import send_prompt
import re
from helper_fns import open_file, write_file

class StoryStructureUI:
    def __init__(self, parent):
        self.parent = parent

        # self.model="gpt-4o"
        # self.model="gemini-1.5-pro"
        self.model="gemini-2.0-pro-exp-02-05"

        # Frame setup for story structure UI
        self.story_structure_frame = ttk.Frame(parent)
        self.story_structure_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.story_structure_frame, text="High-Level Story Structure", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Arcs
        self.c_arc_button = ttk.Button(self.story_structure_frame, text="Character Arcs", command=self.generate_arcs)
        self.c_arc_button.pack(pady=20)

        self.f_arc_button = ttk.Button(self.story_structure_frame, text="Faction Arcs", command=self.generate_faction_arcs)
        self.f_arc_button.pack(pady=20)

        self.cfp_arc_button = ttk.Button(self.story_structure_frame, text="Add Planets to Arcs", command=self.add_planets_to_arcs)
        self.cfp_arc_button.pack(pady=20)

        # Generate Structure Buttons
        self.generate_button = ttk.Button(self.story_structure_frame, text="Generate Story Structure", command=self.generate_structure)
        self.generate_button.pack(pady=20)

        self.add_planets_to_structure_button = ttk.Button(self.story_structure_frame, text="Add Locations to Story Structure", command=self.generate_structure_w_locations)
        self.add_planets_to_structure_button.pack(pady=20)

        self.improve_structure_button = ttk.Button(self.story_structure_frame, text="Create 6 Act Story Structure", command=self.improve_structure)
        self.improve_structure_button.pack(pady=20)


    # Generate character story arcs
    def generate_arcs(self):
        lore_content = open_file("generated_lore.md")
        characters_content = open_file("characters.md")

        try:
            prompt = (
                    f"I am writing a science fiction novel and need help with the planning."
                    f"I would like help to generate the character arcs of the story.\n"
                    f"Please focus on the main 2 protagonist characters and the main antagonist.\n"
                    f"Please use the following background information:\n\n{lore_content}\n\n"
                    f"Please also see the character information:\n\n{characters_content}\n\n"
            )
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            write_file("character_arcs.md", response)


        except Exception as e:
            print(f"Failed to generate character arcs: {e}")
            messagebox.showerror("Error", f"Failed to generate character arcs: {str(e)}")


    # Generate faction story arcs, THEN reconcile faction and character arcs
    # This eventually outputs: reconciled_arcs.md
    def generate_faction_arcs(self):
        try:
            char_arcs = open_file("character_arcs.md")
            factions = open_file("factions.md")
            lore_content = open_file("generated_lore.md")

            prompt = (
                f"I am writing a science fiction novel and need help with the planning."
                f"I would like help to sketch out the story arcs of the various factions.\n"
                f"Please use the following background information:\n\n{lore_content}\n\n"
                f"Please see the following faction overview:\n\n{factions}\n\n"
                f"Please follow the 6 act structure: Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution.\n"
                f"It may also help to consider the character arcs and how they overlap with faction goals:\n\n{char_arcs}\n\n"
                f"Some factions play a more important role than others. Please focus on generating faction arcs."
            )
            response = send_prompt(prompt, model=self.model)
            write_file("faction_arcs.md", response)

            prompt2 = (
                 f"I am writing a science fiction novel and need help with the planning. "
                 "I would like help to reconcile the story arcs of the characters and the factions. "
                 f"The two arcs should weave together in a way that's consistent and logical.\n\n"
                 f"Here are the character arcs:\n\n{char_arcs}\n\n"
                 f"Here are the faction arcs:\n\n{response}\n\n"
                 f"Please write out a combined story arc using these sub-arcs. No further text beyond that is required.\n"
                 f"Please follow the 6 act structure: Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution."
            )
            response2 = send_prompt(prompt2, model=self.model)
            write_file("reconciled_arcs.md", response2)
            print("Reconciled story arcs")

        except Exception as e:
            print(f"Failed to generate faction arcs: {e}")
            messagebox.showerror("Error", f"Failed to generate faction: {str(e)}")

    # Add in the locations (planets) to the reconciled story arc
    def add_planets_to_arcs(self):
        try:
            reconciled_arcs = open_file("reconciled_arcs.md")
            planets = open_file("planets.md")
            planets_factions = open_file("faction_planet_match.md")

            prompt = (
                f"I am writing a science fiction novel and need help with the planning. "
                f"I would like help to add the planet locations the story arc, but they must match correctly.\n"
                f"Please see the following list of planets:\n\n{planets}\n\n"
                f"Please also look at the following information that matches planets and factions:\n\n{planets_factions}\n\n"
                f"Please also review the latest story arc information:\n\n{reconciled_arcs}\n\n"
                f"Please add the correct planet location to each point of the story arc. Please write out the story arc again as the output.\n"
                f"Please don't remove any information from the story arc."
            )
            response = send_prompt(prompt, model=self.model)
            write_file("reconciled_planets_arcs.md", response)

        except Exception as e:
            print(f"Failed to reconcile planets and story arcs: {e}")
            messagebox.showerror("Error", f"Failed to reconcile planets and story arcs: {str(e)}")


    # Generate high-level structure as a 6 Act story
    def generate_structure(self):
        lore_content = open_file("generated_lore.md")
        char_arcs = open_file("character_arcs.md")
        faction_arcs = open_file("faction_arcs.md")
        reconciled_arcs = open_file("reconciled_planets_arcs.md")
        reconciled_arcs_w_planets = open_file("reconciled_planets_arcs.md") # this might not well work with weak LLMs?

        # Generate high-level structure
        try:

            prompt = (
                f"Please generate a high-level structure for a story based on the following information.\n"
                f"Please review the following background parameters, factions, and characters:\n\n{lore_content}\n\n"
                f"Please see the story arc details:\n\n{reconciled_arcs}\n\n"
                # f"Please see the story arc details:\n\n{reconciled_arcs_w_planets}\n\n" # not working great here.
                f"Provide a structured outline with major plot points, faction interactions, character arcs, and key events.\n"
                f"Please include lists of plot points, faction interactions, character arcs, locations.\n"
                f"Here is an example sequence of events that make up the story:\n"
                f"* Beginning: Introduce characters, setting, and basic conflict.\n"
                f"* Rising Action: Develops the main conflict through a series of events.\n"
                f"* First Climax: a turning point and important moment of the story. Some hints of resolution, but also further conflict.\n"
                f"* Solution Finding: a plan starts to come together, but not all parts of the solution are revealed.\n"
                f"* Second Climax: a turning point and the most intense moment of the story. The solution to conflict is finally revealed.\n"
                f"* Resolution (Denouement):  Events that follow the climax and begin to resolve the conflict. Concludes the story, tying up loose ends.\n\n"
                f"Please be detailed and write as much as possible.\n"
                f"Please provide the structure in markdown format."
            )

            print(prompt)
            response = send_prompt(prompt, model=self.model)
            write_file("story_structure.md", response)
            print("Story structure saved successfully to story_structure.md")

        except Exception as e:
            print(f"Failed to generate story structure: {e}")
            messagebox.showerror("Error", f"Failed to generate story structure: {str(e)}")


    # Add locations to the structure
    # Less smart LLMs keep killing off the location data, so need to keep adding it back.
    def generate_structure_w_locations(self):
            story_structure = open_file("story_structure.md")
            reconciled_arcs = open_file("reconciled_planets_arcs.md")

            try:
                prompt2 = (
                    f"I am writing a science fiction novel and need help with the planning. "
                    f"I need your help to add location information to my story structure document.\n"
                    f"Here is the contents of my story structure document:\n\n{story_structure}\n\n"
                    f"Please find the location information in the previously written story arc document:\n\n{reconciled_arcs}\n\n"
                    "Please preserve the information in the story structure document and provide it in the output."
                    "Please ensure the correct location information is added. Thanks"
                )

                response2 = send_prompt(prompt2, model=self.model)
                write_file("story_structure_locations.md", response2)
                print("Story structure and location saved successfully to story_structure_locations.md")

            except Exception as e:
                print(f"Failed to generate story structure: {e}")
                messagebox.showerror("Error", f"Failed to generate story structure: {str(e)}")


    # Flesh out the acts of structure
    # Loop over each act (section) of the story arc
    def improve_structure(self):

        try:
            story_structure = open_file("story_structure.md")
            sections = ("Beginning", "Rising Action", "First Climax", "Solution Finding", "Second Climax", "Resolution")

            for section in sections:
                prompt = (
                    f"I am writing a science fiction novel and need help with the planning.\n"
                    f"There is a 6 Act structure: Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution.\n"
                    f"Please write out a lot more detail for the section: **{section}**. We are NOT writing scenes yet.\n\n" #These could be chapters.\n\n"
                    f"Please refer to this story structure:\n\n{story_structure}\n\n"
                    f"Please state the **location** of the main action. This is important. "
                    f"If the focus of the action changes, please make a note of that. "
                    f"Please list which characters are present in this **act**. "
                    f"Please be as detailed as possible. "
                    f"Please provide the structure in markdown format."
                )

                print(f"Generating section: {section}")
                response = send_prompt(prompt, model=self.model)
                filename = f"story_structure_{section.lower().replace(' ', '_')}.md"
                write_file(filename, response)

            print("Story structure generation complete!")

        except Exception as e:
            print(f"Failed to generate story structure: {e}")
