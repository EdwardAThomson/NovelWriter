import tkinter as tk
from tkinter import ttk, messagebox
import json
from ai_helper import send_prompt

class ChapterOutliningUI:
    def __init__(self, parent):
        self.parent = parent

        # Frame setup for chapter outlining UI
        self.chapter_outlining_frame = ttk.Frame(parent)
        self.chapter_outlining_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.chapter_outlining_frame, text="Chapter Outlining", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Generate Chapter Outline Button
        self.generate_button = ttk.Button(self.chapter_outlining_frame, text="Generate Chapter Outlines", command=self.generate_chapter_outline)
        self.generate_button.pack(pady=20)


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
                f"Please provide the structure in markdown format."
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
