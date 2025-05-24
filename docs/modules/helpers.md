# Helper Modules

This document provides an overview of various helper modules and utility files that support the main functionality of the Novel Writer application. These modules handle tasks like AI model interaction, file operations, logging, and genre-specific configurations.

## `ai_helper.py`

*   **Purpose**: This module centralizes all interactions with different Large Language Model (LLM) APIs, providing a unified interface for sending prompts and receiving responses.
*   **Key Functions/Variables**:
    *   `get_supported_models()`: Returns a list of string identifiers for the LLM models currently configured and supported by the application (e.g., `["gpt-4o", "gemini-1.5-pro"]`). This list is used to populate the model selection dropdown in the main UI.
    *   `send_prompt(prompt: str, model: str, temperature: float = 0.7, max_tokens: int = None) -> str`:
        *   This is the primary function used by other modules to send a text prompt to a specified LLM and get a text response.
        *   It takes the `prompt` string and the `model` identifier (from `get_supported_models()`) as main inputs.
        *   Internally, it dispatches the request to a model-specific private function (e.g., `_call_openai`, `_call_gemini`, `_call_claude`) based on the `model` identifier.
        *   API keys, required by the underlying LLM libraries (OpenAI, Google, Anthropic), are expected to be available in environment variables (typically loaded from a `.env` file at the project root by the `python-dotenv` library when the respective LLM libraries initialize).
        *   `temperature`: Controls the randomness/creativity of the output. Higher values mean more randomness.
        *   `max_tokens`: Can be used to limit the length of the generated response (though not all models/APIs might use this parameter identically).
        *   Includes basic error handling for API calls and will log issues. It returns the LLM's text response or an empty string/error message if the call fails.
    *   Internal functions like `_call_openai(prompt, model_name, temperature, max_tokens)`, `_call_gemini(...)`, `_call_claude(...)` handle the specific API client initialization and request formatting for each LLM provider.
*   **Configuration**: The list of supported models and their specific API parameters (if any beyond the standard ones) are defined directly within `ai_helper.py`. To add a new model or modify existing ones, this file needs to be edited.

## `helper_fns.py`

*   **Purpose**: Provides a collection of common utility functions, primarily for file input/output, JSON manipulation, and schema validation.
*   **Key Functions**:
    *   `open_file(filepath: str) -> str`: Reads the entire content of a specified text file (UTF-8 encoded) and returns it as a string.
    *   `write_file(filepath: str, content: str)`: Writes the given string `content` to the specified text file (UTF-8 encoded), overwriting it if it exists or creating it if it doesn't.
    *   `read_json(filepath: str) -> dict | list` : Reads a JSON file from the given `filepath`, parses it, and returns the resulting Python dictionary or list.
    *   `write_json(filepath: str, data: dict | list)`: Writes the given Python `data` (dictionary or list) to the specified `filepath` as a JSON formatted string, with an indent of 4 for readability.
    *   `load_schema(schema_filename: str) -> dict`: Loads a JSON schema from a file (typically located in a `schemas/` directory). Used for validating JSON data structures.
    *   `validate_json_schema(data: dict | list, schema_filename: str) -> bool`: Validates the given Python `data` against the JSON schema specified by `schema_filename`. Returns `True` if valid, `False` otherwise, and logs validation errors.
    *   `validate_json(data_to_validate, schema_file)`: This appears to be a duplicate or an older version of `validate_json_schema`. Refer to `validate_json_schema` for primary use.
    *   `save_prompt_to_file(output_dir: str, base_filename: str, prompt_content: str, add_timestamp: bool = True) -> str | None`:
        *   A utility for saving LLM prompt strings to files for logging and debugging purposes.
        *   Ensures a `prompts` subdirectory exists within the `output_dir` (creating it if necessary).
        *   Constructs a filename using the `base_filename`. If `add_timestamp` is `True` (default), a timestamp is prepended to `base_filename` to ensure unique filenames.
        *   Writes the `prompt_content` to this file.
        *   Returns the full path to the saved prompt file, or `None` if saving fails.

## `logger_config.py`

*   **Purpose**: Configures the application-wide logging system using Python's `logging` module.
*   **Key Functions**:
    *   `setup_app_logger(output_dir: str, level=logging.INFO) -> logging.Logger`:
        *   Initializes and configures the root logger for the application.
        *   Sets up two handlers: one to write log messages to a file (`app.log` located in the specified `output_dir`) and another to stream log messages to the console (stdout).
        *   Both handlers use a consistent log format that includes timestamp, log level, module name, and the message.
        *   The `level` parameter determines the minimum severity of messages that will be handled (e.g., `logging.INFO`, `logging.DEBUG`).
        *   This function is typically called once at the beginning of the application's execution (in `main.py`) to make the configured logger available throughout the application via `app.logger`.

## `genre_configs.py`

*   **Purpose**: This module acts as a data store or provider for configurations specific to different literary genres and subgenres. These configurations influence UI elements and can guide certain generation steps.
*   **Key Functions/Data**:
    *   `get_genre_config(genre: str, subgenre: str) -> dict`:
        *   The primary function of this module.
        *   Takes `genre` and `subgenre` strings as input.
        *   Returns a dictionary containing configuration settings relevant to that specific genre/subgenre combination. This dictionary is used by `ParametersUI` in `parameters.py` to dynamically populate tabs and input fields for settings like "Implied Settings", "Protagonist Types", "Conflict Scales", etc.
        *   The actual configuration data (the dictionaries returned) is defined within `genre_configs.py` itself.

## `Generators/` (e.g., `SciFiGenerator.py`, `CharacterGenerator.py`)

*   **Purpose**: Modules within the `Generators/` directory provide functions for initial, structured data generation, often *before* significant LLM interaction or for creating foundational elements that LLMs will later refine or use as context. These are typically non-LLM based local generation routines.
*   **Examples & Functionality**:
    *   **`SciFiGenerator.py`**: Contains functions like `generate_universe` which can create initial data for factions, their systems, and planets based on parameters like the number of factions and gender bias. `save_factions_to_file` is used to persist this data.
    *   **`CharacterGenerator.py`**: Contains functions like `generate_main_characters` to create initial profiles for characters (name, role, basic traits, gender, age, family structure) based on parameters like number of characters and gender bias. `save_characters_to_file` is used to persist this data.
    *   These generators often use random choices from predefined lists or simple algorithms to create varied initial data. The output (e.g., `factions.json`, `characters.json`) then serves as a more detailed starting point for LLM-driven lore generation and backstory creation in the `lore.py` module.

## `rag_helper.py`

*   **Purpose**: This module appears to be intended for Retrieval Augmented Generation (RAG) functionalities, likely involving the creation and querying of a vector database for semantic search over lore or other generated content.
*   **Key Functions (Example)**:
    *   `upsert_text(...)`: Likely used to add or update text data (e.g., chunks of lore) into a vector store, along with its embeddings.
    *   Functions for querying the vector store to find relevant context would also be part of this module if fully implemented.
*   **Status**: The extent of its current use might vary. If RAG is actively used, this module would be critical for providing relevant, condensed context to LLMs instead of or in addition to full lore documents.

## `combine.py` (Root Directory Utility)

*   **Purpose**: This standalone Python script is designed to combine multiple individual chapter markdown files into a single, continuous markdown document. It serves as a utility to assemble a full draft or manuscript from the chapter files generated by the application.
*   **Input**: The script reads `.md` files from a specified input directory, which defaults to `current_work/chapters/` (the typical output location for generated chapter files).
*   **Output**:
    *   A single combined markdown file is created.
    *   This output file is saved within the same directory as the input chapters (i.e., `current_work/chapters/`).
    *   The filename for the combined output is dynamically determined:
        *   It attempts to read the "Novel Title" from `current_work/parameters.txt`.
        *   If the title is found, it's sanitized (spaces replaced with underscores, special characters removed) and used as the filename (e.g., `My_Novel_Title.md`).
        *   If the title is not found or `parameters.txt` doesn't exist, the output file defaults to `combined_novel.md`.
        *   Each combined chapter is preceded by a markdown heading (e.g., `# Chapter 1`).
*   **Usage**: It is intended to be run manually from the command line after the chapter generation process is complete:
    ```bash
    python combine.py
    ```
*   **Error Handling**: Includes checks for the existence of the input directory and handles cases where no markdown files are found. It also attempts to gracefully handle file reading errors during the combination process. 