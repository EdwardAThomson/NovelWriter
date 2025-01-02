 
import os

def combine_markdown_files(input_directory, output_file):
    # Get a list of all markdown files in the input directory, sorted by file name
    markdown_files = sorted([f for f in os.listdir(input_directory) if f.endswith('.md')])

    with open(output_file, 'w') as outfile:
        for idx, md_file in enumerate(markdown_files):
            # Write a chapter separator (e.g., Chapter title)
            # chapter_title = f"# Chapter {idx + 1}\n\n"
            # outfile.write(chapter_title)

            # Write the content of the markdown file
            with open(os.path.join(input_directory, md_file), 'r') as infile:
                outfile.write(infile.read())
                outfile.write('\n\n')  # Add some space between chapters

    print(f"Combined markdown files saved to {output_file}")

if __name__ == "__main__":
    # Directory containing the markdown files
    # input_directory = "path/to/your/markdown/files"
    input_directory = "/home/edward/PycharmProjects/NovelWriter/Starbound_Legacy"

    # Output file name for the combined novel
    output_file = "combined_novel.md"

    combine_markdown_files(input_directory, output_file)
