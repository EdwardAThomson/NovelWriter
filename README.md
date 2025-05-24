# NovelWriter

## Description

NovelWriter is a Python application designed to assist authors in writing novels and short stories, currently in the Science Fiction genre, by leveraging Large Language Models (LLMs). It provides a GUI-based interface built with Tkinter for managing novel parameters, generating universe lore, outlining story structure, planning scenes, and writing chapter prose.

The application features a dynamic LLM model selector, allowing users to choose from various supported models for different generation tasks. Currently configured models include:

*   OpenAI GPT-4o, o1, o1-mini o3, o4-mini
*   Gemini 1.5, 2.0, 2.5 pro
*   Claude 3.5, 3.7 Sonnet
*   *(You can add/remove models by configuring `ai_helper.py`)*

Running this code requires API keys for the specific LLMs you intend to use (e.g., an **OpenAI API key** for GPT models, a **Google AI API key** for Gemini models, **Anthropic API Key** for Claude models). These keys should be stored in a `.env` file in the project's root directory.

While many steps are automated, the output often serves as a strong starting point that can be further refined by the author.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url> # Replace <your-repository-url> with the actual URL
    cd NovelWriter
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Make sure you have a `requirements.txt` file listing the necessary packages (like `openai`, `google-generativeai`, `python-dotenv`, `anthropic`, etc.). If not, you'll need to create one.
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` doesn't exist, you'll need to `pip install openai python-dotenv google-generativeai anthropic`)*

4.  **Configure API Keys:**
    *   Create a file named `.env` in the root directory of the project.
    *   Add your API keys to this file in the following format:
        ```dotenv
        OPENAI_API_KEY='your_openai_api_key_here'
        GEMINI_API_KEY='your_gemini_api_key_here'
        ANTHROPIC_API_KEY='your_anthropic_api_key_here'
        ```
    *   Replace the placeholder text with your actual keys.

5.  **Run the Application:**
    ```bash
    python main.py
    ```

## Utility Scripts

### `combine.py` -- build the novel file

Located in the root directory, this script is used to combine all generated chapter markdown files (typically found in `current_work/chapters/`) into a single markdown file. The output file is named after the novel's title (if found in `parameters.txt`) or defaults to `combined_novel.md`, and is saved within the `current_work/chapters/` directory. This is useful for creating a complete manuscript from individual chapter files.

## Detailed Documentation

**For a comprehensive understanding of the application's workflow, modules, file formats, and user guidance, please refer to our [Detailed Documentation here](./docs/README.md).**

The new documentation in the `docs` directory provides the most up-to-date and in-depth information about the project.

## The Generation Process

The novel generation process follows these main stages through the UI tabs:

1.  **Novel Parameters (`parameters.py`):** Collect core parameters like genre, subgenre, tone, themes, etc. These parameters influence subsequent generation steps.
2.  **Generate Lore (`lore.py` & Supporting Modules):**
    *   Generate factions and planetary systems (`SciFiGenerator`).
    *   Generate characters, including relationships (`CharacterGenerator`).
    *   Enhance main characters (Protagonist, Deuteragonist, Antagonist) by assigning age, gender, and generating some family details locally. Save augmented character details (`lore.py`).
    *   Generate narrative backstories for main characters using an LLM, providing previously generated context (`lore.py`).
    *   Compile a detailed prompt including novel parameters, character details, faction info, and technology (`LorePromptGenerator.py`).
    *   Generate the main universe lore narrative using an LLM (`lore.py`).
3.  **Story Structure (`story_structure.py`):**
    *   Generate Character Arcs based on their backstories.
    *   Generate Faction Arcs based on lore and faction details.
    *   Reconcile Character and Faction Arcs.
    *   Generate a high-level story structure, often prompted using a **6-Act Structure** (Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution).
    *   Refine each act of the structure with more detail.
4.  **Scene Planning (`scene_plan.py`):**
    *   Generate chapter outlines based on the 6-Act structure.
    *   Generate detailed scene plans for each chapter.
5.  **Write Chapters (`chapter_writing.py`):**
    *   Generate prose for each scene within a selected chapter, using the scene plans, lore, and character details as context.
    *   Provides functionality to re-write chapters for improvement.

More details, project history, and ongoing developer insights can be found in our [Developer Diary & Design Notes](./docs/discussion.md).

### Original Version

The original version was created as part of NaNoGenMo 2024 ([**completed**](https://github.com/NaNoGenMo/2024/issues/31)). The first version of the code was pushed to a different repo as I lost access to my GitHub account (fixed!), please find the original repo here: [NovelWriter](https://github.com/edthomson/NovelWriter). That code was not fully automated, but it did generate a 52,000-word novel (Echoes of Terra Nova).
