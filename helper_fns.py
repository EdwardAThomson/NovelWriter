import os

directory = "current_work/"


def open_file(filename):
    """Open and read a file. Throws an error if the file is missing."""
    full_path = os.path.join(directory, filename)
    print(f"Opening file: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Error: File {full_path} not found.")

    try:
        with open(full_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        raise IOError(f"Error reading {full_path}: {e}")

def write_file(filename, data):
    """Write data to a file, ensuring the directory exists."""
    full_path = os.path.join(directory, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure the directory exists

    print(f"Writing file: {full_path}")
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(data)
    except Exception as e:
        raise IOError(f"Error writing {full_path}: {e}")
