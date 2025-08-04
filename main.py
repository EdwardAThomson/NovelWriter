#!/usr/bin/env python3
"""
NovelWriter: An AI-assisted novel writing tool
Entry point for the application.
"""

import tkinter as tk
from core.gui.app import NovelWriterApp

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()
