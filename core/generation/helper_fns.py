import os, json
import jsonschema
from jsonschema import validate
from datetime import datetime

schema_directory = "schema/"

def open_file(full_path):
    """Open and read a file. Throws an error if the file is missing."""
    print(f"Opening file: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Error: File {full_path} not found.")
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        raise IOError(f"Error reading {full_path}: {e}")

def write_file(full_path, data):
    """Write data to a file, ensuring the directory exists. Raises IOError on failure."""
    try:
        # Ensure the directory exists, moved here to be part of the try block for this specific operation
        dir_name = os.path.dirname(full_path)
        if dir_name: # Only create if there is a directory part
             os.makedirs(dir_name, exist_ok=True)
        print(f"Writing file: {full_path}")
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(data)
        return True # Explicitly return True on success
    except Exception as e:
        # Let the caller handle logging of this specific error context.
        raise IOError(f"Error writing {full_path}: {e}")

# JSON functions
## Read
def read_json(full_path):
    """Read and parse a JSON file. Throws an error if the file is missing or invalid."""
    print(f"Reading JSON file: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Error: File {full_path} not found.")
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            return json.load(file)  # Deserialize JSON into a Python dictionary
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON from {full_path}: {e}")
    except Exception as e:
        raise IOError(f"Error reading {full_path}: {e}")

## Write
def write_json(full_path, data):
    """Write a Python dictionary to a JSON file, ensuring the directory exists."""
    # os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure the directory exists

    print(f"Writing JSON file: {full_path}")
    try:
        dir_name = os.path.dirname(full_path)
        if dir_name: # Only create if there is a directory part
            os.makedirs(dir_name, exist_ok=True)
        # print(f"Writing JSON file: {full_path}") # Removed print
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)  # Pretty-print JSON with indentation
        return True # Explicitly return True on success
    except Exception as e:
        raise IOError(f"Error writing {full_path}: {e}")


# Load the schema from the separate JSON file
def load_schema(schema_filename):
    """Loads a JSON schema from a file."""
    full_path = os.path.join(schema_directory, schema_filename)
    print(f"Opening schema file: {full_path}")
    # Ensure the schema directory itself is not accidentally created by this helper if it's missing.
    # This helper assumes schema_directory exists or path is absolute.
    # os.makedirs(os.path.dirname(full_path), exist_ok=True) # This line is debatable for a load function
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Schema file not found: {full_path}")
    with open(full_path, "r", encoding="utf-8") as file:
        return json.load(file)

def validate_json_schema(data, schema):
    """
    Validates a JSON string against a predefined JSON schema.

    :param response_text: The JSON text received from LLM.
    :param schema: A JSON Schema dictionary defining structure and constraints.
    :return: True if JSON is valid, raises ValueError otherwise.
    """
    try:
        validate(instance=data, schema=schema)  # Validate against schema
        print("✅ JSON is valid!")
        return True  # JSON is valid
    except json.JSONDecodeError as e: # This exception type is not directly raised by jsonschema.validate
        # This was likely intended for validating raw text before parsing. `validate` expects parsed data.
        raise ValueError(f"Invalid JSON input for schema validation (should be parsed data): {e}")
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ JSON validation failed: {e.message}")
        raise ValueError(f"JSON validation error: {e.message}")


# Not using this now
def validate_json(response_text, schema):
        """
        Generic JSON validation function.

        :param response_text: The JSON text received from LLM.
        :param schema: A dictionary defining required fields and their expected types.
        :return: Parsed JSON object if valid, raises ValueError otherwise.
        """
        try:
            data = json.loads(response_text)  # Convert text to JSON

            for key, value_type in schema.items():
                if key not in data:
                    raise ValueError(f"Invalid JSON format: Missing required key '{key}'.")
                if not isinstance(data[key], value_type):
                    raise ValueError(f"Invalid JSON format: '{key}' should be of type {value_type}.")

            return data  # Return the valid JSON object

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON: Could not parse response.")

def save_prompt_to_file(output_dir, base_name, content, subfolder="prompts", ext=".md"):
    """
    Saves the given content (prompt) to a timestamped file in a specified subfolder 
    of the output directory.

    Args:
        output_dir (str): The base output directory.
        base_name (str): A base name for the prompt file (e.g., 'character_arc_prompt').
        content (str): The string content of the prompt.
        subfolder (str, optional): The name of the subfolder to create within output_dir. 
                                 Defaults to "prompts".
        ext (str, optional): The file extension for the prompt file. Defaults to ".md".

    Returns:
        str: The full path to the saved file if successful, None otherwise.
    """
    try:
        target_dir = os.path.join(output_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize base_name for use in filename (replace spaces, convert to lower)
        safe_base_name = base_name.replace(' ', '_').lower()
        filename = f"{safe_base_name}_{timestamp}{ext}"
        filepath = os.path.join(target_dir, filename)
        
        # write_file will raise IOError on failure
        write_file(filepath, content) 
        return filepath # If write_file succeeds (doesn't raise), return the path
    except Exception as e: # Catch any exception during path ops, dir creation, or from write_file
        # The caller will log this failure contextually.
        # logger.error(f"Internal error in save_prompt_to_file for prompt '{base_name}': {e}", exc_info=True) # Removed module log
        return None
