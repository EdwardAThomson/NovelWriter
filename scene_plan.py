from tkinter import ttk, messagebox
from ai_helper import send_prompt
import re
from helper_fns import open_file, write_file


class ScenePlanningUI:
    def __init__(self, parent):
        self.parent = parent

        # self.model="gpt-4o"
        self.model="gemini-2.0-pro-exp-02-05"
        # self.model="gemini-1.5-pro"

        # Frame setup for chapter writing UI
        self.scene_chapter_planning_frame = ttk.Frame(parent)
        self.scene_chapter_planning_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.scene_chapter_planning_frame, text="Scene and Chapter Planning", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Generate Chapter Outline Button
        self.chapter_outline_button = ttk.Button(self.scene_chapter_planning_frame, text="Generate Chapter Outlines", command=self.generate_chapter_outline)
        self.chapter_outline_button.pack(pady=20)

        # Generate scene plan
        self.write_chapter_button = ttk.Button(self.scene_chapter_planning_frame, text="Scene Planner", command=self.scene_plan)
        self.write_chapter_button.pack(pady=20)


     # Generate an outline of the chapters given the 6-act story structure
    def generate_chapter_outline(self):
        try:

            sections = ("Beginning", "Rising Action", "First Climax", "Solution Finding", "Second Climax", "Resolution")
            chapter_number = 1

            for section in sections:

                filename = f"story_structure_{section.lower().replace(' ', '_')}.md"
                structure_content = open_file(filename)

                prompt = (
                    f"Please help me to generate an outline of the chapters for my novel. "
                    f"The story structure has 6 Acts: Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution.\n"
                    f"Please re-write the acts as a structured outline of chapters. "
                    f"Each act now has now has a detailed plan that I will share with you.\n"
                    f"Please preserve the details provided while writing out the chapter structure. These details are important. "
                    f"Please list the characters, factions, and locations (including planets) within each chapter of the structure. "
                    f"Please suggest the scenes within each chapter too.\n"
                    f"Let's have a look at this act: {section}. Here is the contents of my story structure document:\n\n{structure_content}\n\n"
                    f"Please be detailed and write as much as possible. This act starts with Chapter {chapter_number}.\n"
                    f"Please provide the structure in markdown format. Please don't use backticks or the word 'markdown' in the output."
                )

                print("prompt....")
                print(prompt)
                response = send_prompt(prompt, model=self.model)

                # Match all chapter headings
                # chapter_count = len(re.findall(r"(?:\*\*|##|###)\s*Chapter\b", response))
                chapter_count = len(re.findall(r"(?:\*{2}|#{1,4})\s*Chapter\b", response))
                print("chapter_count", chapter_count)
                chapter_number = chapter_number + chapter_count
                print("Last chapter:", chapter_number)

                # Save the chapter outline to a markdown file
                outline_filename = f"chapter_outlines_{section.lower().replace(' ', '_')}.md"
                write_file(outline_filename, response)

                print(f"Chapter outline saved successfully to {outline_filename}")

            messagebox.showinfo("Success", f"Chapter outlines saved.")

        except Exception as e:
            print(f"Failed to generate chapter outline: {e}")
            messagebox.showerror("Error", f"Failed to generate chapter outline: {str(e)}")


    # Generate an outline of the scenes within each chapter
    def scene_plan(self):
        try:
            # Load the lore content
            lore_content = open_file("generated_lore.md").strip()
            sections = ("Beginning", "Rising Action", "First Climax", "Solution Finding", "Second Climax", "Resolution")

            chapter_number = 1  # Start with the real first chapter

            for section in sections:
                filename = f"chapter_outlines_{section.lower().replace(' ', '_')}.md"
                structure_content = open_file(filename).strip()

                # Skip empty files
                # If anything is missing it means the prior process is broken somewhere, so it shouldn't happen
                if not structure_content:
                    print(f"Warning: {filename} is empty. Skipping...")
                    continue

                # Count chapters in the act
                chapter_count = len(re.findall(r"(?:\*{2}|#{1,4})\s*Chapter\b", structure_content))
                print(f"Detected {chapter_count} chapters in {section}.")

                for _ in range(chapter_count):  # Iterate `chapter_count` times
                    prompt = (
                        f"Sketch out the scenes for Chapter {chapter_number} of my sci-fi novel.\n\n"
                        f"This story follows a structured six-act format: Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution.\n"
                        f"We are currently working on this act: **{section}**.\n\n"
                        f"Here is the outline of the chapters in this act:\n{structure_content}\n\n"
                        f"Expand the scenes for Chapter {chapter_number}. Please ensure consistency with, and maintain the lists for:\n"
                        f"- Character arcs, factions, and locations (including planets).\n"
                        f"Please note the overarching lore of the story:\n{lore_content}\n\n"
                        f"Your response should be in well-structured markdown with headings for each scene."
                    )

                    response = send_prompt(prompt, model=self.model)
                    filename_out = f"scenes_chptr_{chapter_number}.md"
                    write_file(filename_out, response)

                    chapter_number += 1  # Move to the next real chapter number

        except Exception as e:
            print(f"Failed to generate scene outlines: {e}")
            messagebox.showerror("Error", f"Failed to generate scene outlines: {str(e)}")
