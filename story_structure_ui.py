from tkinter import ttk, messagebox
from ai_helper import send_prompt, send_prompt_o1

class StoryStructureUI:
    def __init__(self, parent):
        self.parent = parent

        # Frame setup for story structure UI
        self.story_structure_frame = ttk.Frame(parent)
        self.story_structure_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.story_structure_frame, text="High-Level Story Structure", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Generate Structure Button
        self.generate_button = ttk.Button(self.story_structure_frame, text="Generate Story Structure", command=self.generate_structure)
        self.generate_button.pack(pady=20)

        # Generate Chapter Outline Button
        self.chapter_outline_button = ttk.Button(self.story_structure_frame, text="Generate Chapter Outlines", command=self.generate_chapter_outline)
        self.chapter_outline_button.pack(pady=20)

    # Helper function to open the main lore file
    def open_file(self, filename):
        print("opening file: " + filename)
        with open(filename, "r") as file:
            data = file.read()
        return data


    def generate_structure(self):
        try:
            params = self.open_file("parameters.txt")
            lore_content = self.open_file("generated_lore.md")
            characters_content = self.open_file("characters.md")
            en_characters_content = self.open_file("characters.md")
            relationships_content = self.open_file("relationships.md")
            factions_content = self.open_file("factions.md")


            # Load the lore and relationships
            # Generate the prompt for high-level structure
            # Send prompt to OpenAI API
            # Save the structure to a file
            ## generate_structure_from_api()


            # Generate the prompt for high-level structure
            ### the relationships information is too much for GPT4o
            prompt = (
                f"Please generate a high-level structure for a story based on the following information.\n"
                f"Please use the following background parameters, factions, and characters:\n\n{lore_content}\n\n"
                f"For reference please see the relationships between characters:\n\n{relationships_content}\n\n"
                f"Provide a structured outline with major plot points, faction interactions, character arcs, and key events.\n"
                f"Here is an example sequence of events that make up the story:\n"
                f"* Beginning: Introduce characters, setting, and basic conflict.\n"
                f"* Rising Action: Develops the main conflict through a series of events.\n"
                f"* First Climax: a turning point and important moment of the story. Some hints of resolution, but also further conflict.\n"
                f"* Solution Finding: a plan starts to come together, but not all parts of the solution are revealed.\n"
                f"* Second Climax: a turning point and the most intense moment of the story. The solution to conflict is finally revealed.\n"
                f"* Resolution (Denouement):  Events that follow the climax and begin to resolve the conflict. Concludes the story, tying up loose ends.\n\n"
                f"Please Development outline the main character arcs: The transformation or growth a character undergoes.\n"
                f"* Consider the depth and complexity: Creating multi-dimensional characters with strengths, flaws, and motivations.\n\n"
                f"Please provide the structure in markdown format."
            )

            print(prompt)

            # Send prompt to OpenAI API --- uses GTP4o
            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384 , temperature=0.7, role_description="You are an expert storyteller focusing on developing a compelling story structure.")

            # o1 -- this uses o1 instead of GPT4o
            #response = send_prompt_o1(prompt, model="o1-mini")

            # Save the structure to a file
            print("Trying to save file as markdown....")
            with open("story_structure.md", "w") as struct_file:
                struct_file.write(response)
            print("Story structure saved successfully to story_structure.md")



        except Exception as e:
            print(f"Failed to generate story structure: {e}")
            messagebox.showerror("Error", f"Failed to generate story structure: {str(e)}")


    def generate_chapter_outline(self):
        try:

            with open("generated_lore.md", "r") as lore_file:
                lore_content = lore_file.read()

            with open("story_structure.md", "r") as struct_file:
                structure_content = struct_file.read()

            # Prompt for outlining multiple chapters
            #  includes:
            ## Lore? Includes characters.
            ## High-level structure
            prompt = (
                f"I wish to generate a list of chapters for my novel."
                f"Please use the following background information:\n\n"
                f"{lore_content}\n\n"
                f"Please generate the chapter list and details based on the following high-level section of the story,"
                f"I have also included high-level details of character arcs and faction interactions:\n\n"
                f"{structure_content}\n\n"
                f"Please dive further into the details of key plot points, events, and character interactions.\n"
                f"Please provide the structure in markdown format. Please don't use backticks or the word 'markdown' in the output."
            )

            print("prompt....")
            print(prompt)
            # Send prompt to OpenAI API
            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative author focusing on structuring a story into detailed chapters.")

            # Increment the chapter number based on the response (assuming response includes multiple chapters)
            chapter_count = response.count("### Chapter")
            print("chapter_count", chapter_count)

            # Save the chapter outline to a markdown file
            outline_filename = f"chapter_outlines.md"
            with open(outline_filename, "w") as outline_file:
                outline_file.write(response)
            print(f"Chapter outline saved successfully to {outline_filename}")

            # Show a success message
            messagebox.showinfo("Success", f"Chapter outline saved to {outline_filename}")

        except Exception as e:
            print(f"Failed to generate chapter outline: {e}")
            messagebox.showerror("Error", f"Failed to generate chapter outline: {str(e)}")
