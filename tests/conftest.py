"""Test configuration: make the repo root importable.

NovelWriter is run from the repo root (python main.py), so absolute imports
like `core.generation.ai_helper` expect the root on sys.path.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
