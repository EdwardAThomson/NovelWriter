import os
import re

def get_novel_title_from_parameters(base_dir="current_work"):
    """Attempts to read the novel title from parameters.txt."""
    params_filepath = os.path.join(base_dir, "parameters.txt")
    if os.path.exists(params_filepath):
        try:
            with open(params_filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Novel Title:"):
                        title = line.split(":", 1)[1].strip()
                        if title:
                            return title
        except Exception as e:
            print(f"Warning: Could not read or parse {params_filepath}: {e}")
    return None

def sanitize_filename(title):
    """Sanitizes a string to be a safe filename."""
    if not title:
        return "Untitled_Novel"
    # Remove invalid characters
    filename = re.sub(r'[\\/\:*?"<>|]', '', title)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Limit length (optional, but good practice)
    filename = filename[:100] # Max 100 chars for filename part
    if not filename: # If all chars were invalid
        return "Untitled_Novel"
    return filename

def combine_markdown_files(input_directory, output_file):
    # Check if the input directory exists
    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' not found.")
        print("Please ensure the application has generated chapters first.")
        return

    # Get a list of all markdown files in the input directory, sorted by file name
    # Exclude the potential output file itself from being read as an input chapter
    output_basename = os.path.basename(output_file)
    try:
        markdown_files = sorted([f for f in os.listdir(input_directory) if f.endswith('.md') and f != output_basename])
    except FileNotFoundError:
        print(f"Error: Could not list files in '{input_directory}'. It might have been deleted after the initial check.")
        return

    if not markdown_files:
        print(f"No markdown files found in '{input_directory}' to combine (excluding '{output_basename}').")
        return

    # Ensure output directory exists (it should be the same as input_directory for chapters/combined_novel.md)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx, md_file in enumerate(markdown_files):
            # Write a chapter separator (e.g., Chapter title)
            chapter_title_text = f"# Chapter {idx + 1}\n\n"
            outfile.write(chapter_title_text)

            # Write the content of the markdown file
            try:
                with open(os.path.join(input_directory, md_file), 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n\n')  # Add some space between chapters
            except FileNotFoundError:
                print(f"Warning: File '{md_file}' not found during combination. It might have been deleted.")
                continue # Skip to the next file
            except Exception as e:
                print(f"Warning: Could not read file '{md_file}': {e}")
                continue

    print(f"Combined markdown files saved to {output_file}")

if __name__ == "__main__":
    # Default directory containing the markdown files
    base_output_dir = "current_work"
    chapters_subdir = "chapters"
    input_directory = os.path.join(base_output_dir, chapters_subdir)

    novel_title = get_novel_title_from_parameters(base_output_dir)
    
    if novel_title:
        output_filename = sanitize_filename(novel_title) + ".md"
        print(f"Using novel title from parameters.txt for output file: '{output_filename}'")
    else:
        output_filename = "combined_novel.md"
        print(f"Novel title not found in parameters.txt. Using default output file: '{output_filename}'")

    output_file = os.path.join(input_directory, output_filename)

    combine_markdown_files(input_directory, output_file)

    print("Done!")
