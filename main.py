#!/usr/bin/env python3
"""
NovelWriter: An AI-assisted novel writing tool
Entry point for the application.
"""

import sys

# Checked before the imports below, because the modules they pull in use syntax
# added in Python 3.12. On an older interpreter those imports fail with a
# SyntaxError pointing at a log line, which says nothing about the real problem.
REQUIRED_PYTHON = (3, 12)
if sys.version_info < REQUIRED_PYTHON:
    sys.exit(
        f"NovelWriter needs Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} or newer. "
        f"This is Python {sys.version.split()[0]} ({sys.executable}).\n"
        f"Run it with a newer interpreter, for example: "
        f"python{REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} main.py"
    )

import tkinter as tk  # noqa: E402  (imported after the version check above)
from core.gui.app import NovelWriterApp  # noqa: E402

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x900")  # Width x Height in pixels
    app = NovelWriterApp(root)
    root.mainloop()
