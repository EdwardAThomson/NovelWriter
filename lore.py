# lore.py
import tkinter as tk
from tkinter import ttk, messagebox
from ai_helper import send_prompt
from rag_helper import upsert_lore_text, retrieve_relevant_lore
import json
from helper_fns import open_file, write_file

class LoreUI:
    def __init__(self, parent):
        self.parent = parent

        # self.model="gpt-4o"
        self.model="gemini-2.0-pro-exp-02-05"
        # gemini-1.5-pro
        # gemini-2.0-pro-exp-02-05

        # Frame setup for relationships UI
        self.lore_frame = ttk.Frame(parent)
        self.lore_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.lore_frame, text="Lore Builder", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        #Buttons
        # Generate Tech Button
        self.tech_button = ttk.Button(self.lore_frame, text="Generate Tech Lore", command=self.generate_tech_lore)
        self.tech_button.pack(pady=20)

        # Generate Planet List Button
        self.planet_button = ttk.Button(self.lore_frame, text="Generate Planet List", command=self.generate_planet_list)
        self.planet_button.pack(pady=20)

        # Improve Factions Button
        self.factions_button = ttk.Button(self.lore_frame, text="Generate Factions", command=self.generate_factions)
        self.factions_button.pack(pady=20)

        # Generate and Improve Characters Buttons
        self.characters_button = ttk.Button(self.lore_frame, text="Generate Characters", command=self.generate_characters)
        self.characters_button.pack(pady=20)

        self.improve_characters_button = ttk.Button(self.lore_frame, text="Improve Characters and Relationships", command=self.improve_characters)
        self.improve_characters_button.pack(pady=20)

        self.main_char_enh_button = ttk.Button(self.lore_frame, text="Enhance main characters", command=self.main_character_enhancement)
        self.main_char_enh_button.pack(pady=20)

    def validate_json(self, response_text, schema):
        """
        Generic JSON validation function.

        :param response_text: The JSON text received from LLM.
        :param schema: A dictionary defining required fields and their expected types.
        :return: Parsed JSON object if valid, raises ValueError otherwise.
        """
        try:
            data = json.loads(response_text)  # Convert text to JSON

            for key, value_type in schema.items():
                if key not in data:
                    raise ValueError(f"Invalid JSON format: Missing required key '{key}'.")
                if not isinstance(data[key], value_type):
                    raise ValueError(f"Invalid JSON format: '{key}' should be of type {value_type}.")

            return data  # Return the valid JSON object

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON: Could not parse response.")

    ### Generation Functions -- leveraging LLMs for content generation

    # Generate technology lore
    def generate_tech_lore(self):
        print("Generating Tech Lore")

        try:
            lore_data = open_file("generated_lore.md")
            parameters = open_file("parameters.txt")

            # Tech generator
            prompt = (
               f"I am writing a sci-fi novel using the following parameters:\n\n"
               f"{parameters}\n\n"
               f"Please help me generate a list of cool technology with descriptions.\n"
               f"Please see the following background information of this story:\n\n"
               f"{lore_data}"
            )

            # prompt = """
            # I am writing a sci-fi novel, and I need a structured list of futuristic technologies.
            #
            # Please output the response in JSON format with the following structure:
            #
            # {
            #     "technologies": [
            #         {
            #             "name": "Technology Name",
            #             "description": "Brief description of what it does.",
            #             "category": "Category (e.g., Energy, Cybernetics, Weapons, etc.)",
            #             "applications": ["List of applications"],
            #             "inventor": "Who invented it (or UNKNOWN if not relevant)",
            #             "era": "Time period in the story when it was developed"
            #         }
            #     ]
            # }
            #
            # Generate 5 unique technologies based on these criteria.
            # """


            print("Prompt... [tech lore]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("technology.md", response)
            print("Generated Technology")

            # TODO: fix this later -- adding RAG
            # VectorDB upsert: Store the new lore for later retrieval
            # upsert_lore_text("technology.md", response, metadata={"type": "technology"})

            messagebox.showinfo("Success", "Technology background generated and saved successfully.")

        except Exception as e:
            print(f"Failed to generate tech lore: {e}")
            messagebox.showerror("Error", f"Failed to generate tech lore: {str(e)}")


    # def generate_tech_lore(self):
    #     print("Generating Tech Lore")
    #
    #     try:
    #         lore_data = self.open_file("generated_lore.md")
    #         parameters = self.open_file("parameters.txt")
    #
    #         # LLM prompt
    #         prompt = """
    #         I am writing a sci-fi novel, and I need a structured list of futuristic technologies.
    #
    #         Please output the response in JSON format with the following structure:
    #
    #         {
    #             "technologies": [
    #                 {
    #                     "name": "Technology Name",
    #                     "description": "Brief description of what it does.",
    #                     "category": "Category (e.g., Energy, Cybernetics, Weapons, etc.)",
    #                     "applications": ["List of applications"],
    #                     "inventor": "Who invented it (or UNKNOWN if not relevant)",
    #                     "era": "Time period in the story when it was developed"
    #                 }
    #             ]
    #         }
    #
    #         Generate 5 unique technologies based on these criteria.
    #         """
    #
    #         print("Prompt... [tech lore]")
    #         response = send_prompt(prompt, model=self.model)
    #         print(response)
    #
    #         # Define schema for validation
    #         tech_schema = {
    #             "technologies": list
    #         }
    #
    #         # Validate JSON response
    #         valid_data = self.validate_json(response, tech_schema)
    #
    #         # Save validated JSON to file
    #         with open("technology.json", "w") as file:
    #             json.dump(valid_data, file, indent=4)
    #
    #         print("Generated Technology")
    #
    #         # VectorDB upsert: Store the new lore for later retrieval
    #         # upsert_lore_text("technology.json", json.dumps(valid_data), metadata={"type": "technology"})
    #
    #         messagebox.showinfo("Success", "Technology background generated and saved successfully.")
    #
    #     except ValueError as e:
    #         print(f"JSON Validation Error: {e}")
    #         messagebox.showerror("Error", f"Invalid JSON format: {str(e)}")
    #
    #     except Exception as e:
    #         print(f"Failed to generate tech lore: {e}")
    #         messagebox.showerror("Error", f"Failed to generate tech lore: {str(e)}")



    # Generate list of planets
    def generate_planet_list(self):
        print("Generating Planet List")

        try:
            lore_data = open_file("generated_lore.md")
            parameters = open_file("parameters.txt")

            # Planet list generation
            prompt = (
                f"I am writing a sci-fi novel using the following parameters:\n\n"
                f"{parameters}\n\n"
                f"Please generate a list of planets in markdown format.\n"
                f"If relevant please see the following background information of this story:\n\n"
                f"{lore_data}"
            )

            print("Prompt... [list of planets]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("planets.md", response)
            print("Generated Planet List")
            messagebox.showinfo("Success", "Generated planet list and saved successfully.")

        except Exception as e:
            print(f"Failed to generate planet list: {e}")
            messagebox.showerror("Error", f"Failed to generate planet list: {str(e)}")


    # Generate list of factions
    # Then match the factions to the planets
    def generate_factions(self):
        print("Generate Factions (now). Then match factions and planets (after)")

        try:
            lore_data = open_file("generated_lore.md")
            parameters = open_file("parameters.txt")

            # Faction generation
            prompt = (
                f"I am writing a sci-fi novel using the following parameters:\n\n"
                f"{parameters}\n\n"
                f"Please generate a list of factions with important details in markdown format.\n"
                f"Please see the following background information of this story:\n\n"
                f"{lore_data}"
            )

            print("prompt... [Generating Factions]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("factions.md", response)
            print("Generated Factions")

        except Exception as e:
            print(f"Failed to generate faction details: {e}")
            messagebox.showerror("Error", f"Failed to generate faction details: {str(e)}")


        # Match factions to planets
        print("Now: Matching Factions and Planets")

        try:
            lore = open_file("generated_lore.md") # need to replace this in other places too
            factions = open_file("factions.md")
            planets = open_file("planets.md")

            # Faction and planet matching
            prompt = (
                f"I am writing a sci-fi novel using the following background lore:\n\n"
                f"{lore}\n"
                f"Please help me to match the list of planets to the list of factions.\n"
                f"Here is the list of planets:\n\n"
                f"{planets}\n\n"
                f"And here is the list of factions:\n\n"
                f"{factions}.\n\n"
                f"Please respond in markdown format."
            )

            print("prompt... [Matching Factions and Planets]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("faction_planet_match.md", response)
            print("Matched Factions with Planets")
            # upsert
            messagebox.showinfo("Success", "Match factions with planets. File saved successfully.")

        except Exception as e:
            print(f"Failed to generate faction details: {e}")
            messagebox.showerror("Error", f"Failed to match faction and planets. Details: {str(e)}")


    # Generate a list of characters
    # Then match characters to the list of factions
    def generate_characters(self):
        print("Now: Generate Characters. After: Match characters and factions.")

        try:
            lore_data = open_file("generated_lore.md")
            parameters = open_file("parameters.txt")

            # Character Generation
            prompt = (
                f"I am writing a sci-fi novel using the following parameters:\n\n"
                f"{parameters}\n\n"
                f"Please generate a list of characters in markdown format.\n"
                f"Please include their goals, motivations, flaws, how they will grow throughout the story.\n"
                f"Please see the following background information of this story:\n\n"
                f"{lore_data}"
            )

            print("prompt... [Generating characters]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("characters.md", response)
            print("Generated Characters")

        except Exception as e:
            print(f"Failed to generate character details: {e}")
            messagebox.showerror("Error", f"Failed to generate character details: {str(e)}")


        # Match People to factions
        #
        print("Now: Match Characters and Factions")

        try:
            character_data = open_file("characters.md")
            factions = open_file("factions.md")

            # Character Generation
            prompt = (
                f"I am writing a sci-fi novel.\n"
                f"Please help me to match the list of characters with a list of factions.\n"
                f"Here is the list of characters:\n\n"
                f"{character_data}\n\n"
                f"Here is the list of factions:\n\n"
                f"{factions}\n\n"
                f"Please respond in markdown format."
            )

            print("prompt... [matching characters with factions]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("characters_and_factions.md", response)
            print("Matching Characters and Factions")
            #upsert
            messagebox.showinfo("Success", "Matching characters and factions. File saved successfully.")

        except Exception as e:
            print(f"Failed to generate character details: {e}")
            messagebox.showerror("Error", f"Failed to generate character details: {str(e)}")

    # Add a description for each character
    def improve_characters(self):
        print("Now: Improve Characters. After: Figure out relationships.")

        try:
            lore_data = open_file("generated_lore.md")
            character_data = open_file("characters.md")
            match_data = open_file("characters_and_factions.md")

            # Character Generation
            prompt = (
                f"I am writing a sci-fi novel with the following background information :\n\n"
                f"{lore_data}\n\n"
                f"Please review the list of characters:\n"
                f"{character_data}\n\n"
                f"Please also review the following information that matches characters with factions:\n\n"
                f"{match_data}"
                f"Please add a description for each character.\n"
            )

            print("prompt... [Improving characters]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("characters_enhanced.md", response)
            # upsert
            print("Improved Characters")
            messagebox.showinfo("Success", "Improved characters and saved successfully.")

        except Exception as e:
            print(f"Failed to generate character details: {e}")


        # Generate Relationships
        print("Now: Generating Relationships")

        try:
            character_data = open_file("characters.md")
            en_character_data = open_file("characters_enhanced.md")

            prompt = (
                f"I am writing a sci-fi novel and require some help.\n"
                f"Here is a short list of characters in the story:\n\n{character_data}\n\n"
                f"plus some more information about them:\n\n{en_character_data}\n\n"
                f"Generate a list of relationships between these characters. \n"
                f"Include each character's name, the character they are related to, and the nature of the relationship (e.g., ally, rival, family)."
            )

            print("Prompt... [Generating Relationships]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("relationships.md", response)
            print("Relationships Generated")
            messagebox.showinfo("Success", "Relationships generated and saved successfully.")

        except Exception as e:
            print(f"Failed to generate relationships: {e}")
            messagebox.showerror("Error", f"Failed to generate relationships: {str(e)}")

    # Generate background story for the main characters
    def main_character_enhancement(self):
        print("Now: Enhance Characters.")
        lore_data = open_file("generated_lore.md")
        character_data = open_file("characters.md")
        en_character_data = open_file("characters_enhanced.md")

        # Main character
        try:

            prompt = (
                f"I am writing a sci-fi novel and require some help to improve the main character.\n"
                f"I need to have a deeper background story of the main character. Perhaps about their family.\n"
                f"Something about their upbringing and their life.\n"
                f"Please use the background information provided to weave a good backstory for the main character.\n"
                f"Please see the following background information of this story:\n\n{lore_data}\n\n"
                f"Here is a short list of characters in the story:\n\n{character_data}\n\n"
                f"And here is a little extra background information\n\n{en_character_data}."
            )
            print("prompt... [Enhance Main Characters]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("main_character_enhanced.md", response)
            print("Enhanced Main Characters")

        except Exception as e:
            print(f"Failed to enhance the main character. Details: {e}")

        # Supporting main character (main character 2)
        try:
            prompt = (
                f"I am writing a sci-fi novel and require some help to improve the 2nd main protagonist.\n"
                f"I need to have a deeper background story of this supporting character. Perhaps about their family.\n"
                f"Something about their upbringing and their life.\n"
                f"Please use the background information provided to weave a good backstory for this character.\n"
                f"Please see the following background information of this story:\n\n{lore_data}\n\n"
                f"Here is a short list of characters in the story:\n\n{character_data}\n\n"
                f"And here is a little extra background information\n\n{en_character_data}."
            )
            print("prompt... [Enhance 2nd Main Characters]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("main_character_2_enhanced.md", response)
            print("Enhanced 2nd Main Characters")

        except Exception as e:
            print(f"Failed to enhance the 2nd main character. Details: {e}")

        # Main antagonist
        try:
            prompt = (
                f"I am writing a sci-fi novel and require some help to improve the main antagonist character.\n"
                f"The character needs a deeper background story. Perhaps about their family. Is there something sinister?\n"
                f"We need something about their upbringing and their life.\n"
                f"Please use the background information provided to weave a good backstory for this character.\n"
                f"Please see the following background information of this story:\n\n{lore_data}\n\n"
                f"Here is a short list of characters in the story:\n\n{character_data}\n\n"
                f"And here is a little extra background information\n\n{en_character_data}."
            )
            print("prompt... [Enhance Main Antagonist]")
            print(prompt)
            response = send_prompt(prompt, model=self.model)
            print(response)
            write_file("main_antagonist_enhanced.md", response)
            print("Enhanced antagonist")

        except Exception as e:
            print(f"Failed to enhance the antagonist. Details: {e}")