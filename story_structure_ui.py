import tkinter as tk
from tkinter import ttk, messagebox
from story_structure_generator import generate_structure_from_api

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

    def generate_structure(self):
        try:
            # Load the lore and relationships
            # Generate the prompt for high-level structure
            # Send prompt to OpenAI API
            # Save the structure to a file
            generate_structure_from_api()

        except Exception as e:
            print(f"Failed to generate story structure: {e}")
            messagebox.showerror("Error", f"Failed to generate story structure: {str(e)}")
