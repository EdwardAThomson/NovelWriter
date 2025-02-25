import tkinter as tk
from tkinter import ttk
from parameters import ParametersUI
from lore import LoreUI
from story_structure import StoryStructureUI
from scene_plan import ScenePlanningUI
from chapter_writing import ChapterWritingUI

class NovelWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Writer")

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Parameters UI
        self.param_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.param_frame, text="Novel Parameters")
        self.param_ui = ParametersUI(self.param_frame)

        # Lore Generation UI
        self.lore_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lore_frame, text="Generate Lore")
        self.lore_ui = LoreUI(self.lore_frame)

        # High-Level Story Structure UI
        self.structure_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.structure_frame, text="Story Structure")
        self.structure_ui = StoryStructureUI(self.structure_frame)

        # Scene Planning UI
        self.outlining_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.outlining_frame, text="Scene Planning")
        self.outlining_ui = ScenePlanningUI(self.outlining_frame)

        # Chapter Writing UI
        self.chapter_writing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chapter_writing_frame, text="Write Chapters")
        self.chapter_writing_ui = ChapterWritingUI(self.chapter_writing_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()