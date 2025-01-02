# lore_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from ai_helper import send_prompt


class LoreUI:
    def __init__(self, parent):
        self.parent = parent

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
        self.factions_button = ttk.Button(self.lore_frame, text="Improve Factions", command=self.improve_factions)
        self.factions_button.pack(pady=20)

        # Generate and Improve Characters Buttons
        self.characters_button = ttk.Button(self.lore_frame, text="Generate Characters", command=self.generate_characters)
        self.characters_button.pack(pady=20)

        self.improve_characters_button = ttk.Button(self.lore_frame, text="Improve Characters", command=self.improve_characters)
        self.improve_characters_button.pack(pady=20)

        # Generate Relationships Button
        self.relationships_button = ttk.Button(self.lore_frame, text="Generate Relationships", command=self.generate_relationships)
        self.relationships_button.pack(pady=20)


    # Helper function to open the main lore file
    def open_lore_file(self):
        print("opening lore file")

        with open("generated_lore.md", "r") as lore_file:
            setting_data = lore_file.read()

        return setting_data

    # Helper function to open the parameters file
    def open_parameters_file(self):
        print("opening parameters file")

        with open("parameters.txt", "r") as parameters_file:
            parameters = parameters_file.read()

        return parameters



    ### Generation Functions -- leveraging LLMs for content generation


    def generate_tech_lore(self):
        print("Generating Tech Lore")

        try:
            lore_data = self.open_lore_file()
            parameters = self.open_parameters_file()

            # Tech generator
            prompt = (
                f"I am writing a sci-fi novel using the following parameters:\n\n"
                f"{parameters}\n\n"
                f"Please help me generate a list of cool technology with descriptions.\n"
                f"Please see the following background information of this story:\n\n"
                f"{lore_data}"
            )

            print("Prompt... [tech lore]")
            print(prompt)

            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
            print(response)

            with open("technology.md", "w") as file:
                   file.write(response)

            print("Generated Technology")
            messagebox.showinfo("Success", "Technology background generated and saved successfully.")

        except Exception as e:
            print(f"Failed to generate tech lore: {e}")
            messagebox.showerror("Error", f"Failed to generate tech lore: {str(e)}")



    def generate_planet_list(self):
        print("Generating Planet List")

        try:
            lore_data = self.open_lore_file()
            parameters = self.open_parameters_file()

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

            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
            print(response)

            with open("planets.md", "w") as file:
                   file.write(response)

            print("Generated Planet List")
            messagebox.showinfo("Success", "Generated planet list and saved successfully.")

        except Exception as e:
            print(f"Failed to generate planet list: {e}")
            messagebox.showerror("Error", f"Failed to generate planet list: {str(e)}")



    def improve_factions(self):
        print("Improving Factions")

        try:
            lore_data = self.open_lore_file()
            parameters = self.open_parameters_file()

            # Faction improvement
            prompt = (
                f"I am writing a sci-fi novel using the following parameters:\n\n"
                f"{parameters}\n\n"
                f"Please generate a list of factions with important details in markdown format.\n"
                f"Please see the following background information of this story:\n\n"
                f"{lore_data}"
            )

            print("prompt... [Improving Factions]")
            print(prompt)

            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
            print(response)

            with open("factions.md", "w") as file:
                   file.write(response)

            print("Generated Technology")
            messagebox.showinfo("Success", "Improve faction details and saved successfully.")



        except Exception as e:
            print(f"Failed to generate faction details: {e}")
            messagebox.showerror("Error", f"Failed to generate faction details: {str(e)}")


    def generate_characters(self):
        print("Generate Characters")

        try:
            lore_data = self.open_lore_file()
            parameters = self.open_parameters_file()

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

            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
            print(response)

            with open("characters.md", "w") as file:
                   file.write(response)

            print("Generated Technology")
            messagebox.showinfo("Success", "Generated characters and saved successfully.")


        except Exception as e:
            print(f"Failed to generate character details: {e}")
            messagebox.showerror("Error", f"Failed to generate character details: {str(e)}")


    def improve_characters(self):
        print("Improve Characters")

        try:
            lore_data = self.open_lore_file()

            with open("characters.md", "r") as char_file:
                character_data = char_file.read()

            # Character Generation
            prompt = (
                f"I am writing a sci-fi novel with the following background information :\n\n"
                 f"{lore_data}\n\n"
                f"Please review the list of characters:\n"
                f"{character_data}\n\n"
                f"Please add a description for each character.\n"
                # f"Please add a little background details about the character's life so far."
            )

            print("prompt... [Improving characters]")
            print(prompt)

            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
            print(response)

            with open("characters_enhanced.md", "w") as file:
                   file.write(response)

            print("Generated Technology")
            messagebox.showinfo("Success", "Generated characters and saved successfully.")


        except Exception as e:
            print(f"Failed to generate character details: {e}")
            messagebox.showerror("Error", f"Failed to generate character details: {str(e)}")



    # Generate Relationships
    def generate_relationships(self):
        print("Generating Relationships")

        try:

            # Try to load characters from file
            with open("characters.md", "r") as char_file:
                       character_data = char_file.read()

            with open("characters_enhanced.md", "r") as echar_file:
                       en_character_data = echar_file.read()

            print("Prompt... [Generating Relationships]")

            prompt = (
                f"Here is a short list of characters in the story:\n\n{character_data}\n\n"
                f"plus some more information about them:\n\n{en_character_data}\n\n"
                f"Generate a list of relationships between these characters. \n"
                f"Include each character's name, the character they are related to, and the nature of the relationship (e.g., ally, rival, family). \n"
                # f"Please provide this in markdown format, but please don't insert backticks or the word 'markdown'."
            )

            print(prompt)

            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
            print(response)

            with open("relationships.md", "w") as file:
                   file.write(response)

            print("Relationships Generated")
            messagebox.showinfo("Success", "Relationships generated and saved successfully.")


        except Exception as e:
            print(f"Failed to generate relationships: {e}")
            messagebox.showerror("Error", f"Failed to generate relationships: {str(e)}")
