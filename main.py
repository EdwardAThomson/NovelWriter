import tkinter as tk
from tkinter import ttk
from lore_ui import LoreUI
from relationship_ui import RelationshipUI
from story_structure_ui import StoryStructureUI
from chapter_outlining_ui import ChapterOutliningUI
from chapter_writing_ui import ChapterWritingUI

class NovelWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Writer")

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Lore Generation UI
        self.lore_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lore_frame, text="Generate Lore")
        self.lore_ui = LoreUI(self.lore_frame)

        # Relationships Generation UI
        self.relationship_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.relationship_frame, text="Character Relationships")
        self.relationship_ui = RelationshipUI(self.relationship_frame)

        # High-Level Story Structure UI
        self.structure_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.structure_frame, text="Story Structure")
        self.structure_ui = StoryStructureUI(self.structure_frame)

        # Chapter Outlining UI
        self.outlining_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.outlining_frame, text="Chapter Outlining")
        self.outlining_ui = ChapterOutliningUI(self.outlining_frame)

        # Chapter Writing UI
        self.chapter_writing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chapter_writing_frame, text="Write Chapters")
        self.chapter_writing_ui = ChapterWritingUI(self.chapter_writing_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()