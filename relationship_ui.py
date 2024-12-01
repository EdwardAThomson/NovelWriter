import tkinter as tk
from tkinter import ttk, messagebox
from relationship_generator import generate_relationships_from_api

class RelationshipUI:
    def __init__(self, parent):
        self.parent = parent

        # Frame setup for relationships UI
        self.relationship_frame = ttk.Frame(parent)
        self.relationship_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.relationship_frame, text="Character Relationships", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Generate Relationships Button
        self.generate_button = ttk.Button(self.relationship_frame, text="Generate Relationships", command=self.generate_relationships)
        self.generate_button.pack(pady=20)

    def generate_relationships(self):
        try:
            # this function reads character file, calls OAI API, dumps a file of relationships.
            # generated_relationships = generate_relationships_from_api()
            generate_relationships_from_api()

            print("Relationships Generated")
            messagebox.showinfo("Success", "Relationships generated and *may* have saved successfully.")
        except Exception as e:
            print(f"Failed to generate relationships: {e}")
            messagebox.showerror("Error", f"Failed to generate relationships: {str(e)}")
