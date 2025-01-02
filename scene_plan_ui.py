from tkinter import ttk, messagebox
from ai_helper import send_prompt, send_prompt_o1

class ScenePlanningUI:
    def __init__(self, parent):
        self.parent = parent

        # Frame setup for chapter writing UI
        self.chapter_writing_frame = ttk.Frame(parent)
        self.chapter_writing_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.chapter_writing_frame, text="Scene Planner", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Entry to select chapter number
        self.chapter_label = ttk.Label(self.chapter_writing_frame, text="Enter Chapter Number:")
        self.chapter_label.pack()
        self.chapter_number_entry = ttk.Entry(self.chapter_writing_frame)
        self.chapter_number_entry.pack(pady=5)

        # Button to write chapter
        self.write_chapter_button = ttk.Button(self.chapter_writing_frame, text="Scene Planner", command=self.scene_plan)
        self.write_chapter_button.pack(pady=20)

        # Button to re-write chapter
        # self.write_chapter_button = ttk.Button(self.chapter_writing_frame, text="Re-Write Scenes", command=self.scene_review)
        # self.write_chapter_button.pack(pady=20)



    def scene_plan(self):
        try:
            chapter_number = int(self.chapter_number_entry.get())

            with open("generated_lore.md", "r") as lore_file:
                lore_content = lore_file.read()

            with open("characters_enhanced.md", "r") as characters_enhanced_file:
                enchar_content = characters_enhanced_file.read()

            with open("chapter_outlines.md", "r") as chapter_outlines_file:
                chapter_outlines_content = chapter_outlines_file.read()


            prompt = (
                f"Please help me to sketch out the scenes of chapter {chapter_number} of my sci-fi novel.\n\n"
                f"Here is an outline of the chapters: \n\n{chapter_outlines_content}\n\n"
                f"Please see the characters notes here: \n\n{enchar_content}\n\n"
                f"It may also be helpful to keep the overall lore in mind: \n\n{lore_content}\n\n"
            )

            print("prompt....")
            print(prompt)
            # Send prompt to OpenAI API
            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative author focusing on structuring a story into detailed scenes.")

            with open(f"scenes_chapter_{chapter_number}.md", "w") as scene_file:
                scene_file.write(response)

            messagebox.showinfo("Success", f"Scenes for chapter {chapter_number} saved successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid chapter number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write scenes for this chapter: {str(e)}")

    ## Currently unused!
    def scene_review(self):
        try:
            chapter_number = int(self.chapter_number_entry.get())

            with open(f"scenes_chapter_{chapter_number}.md", "r") as scene_file:
                scene_content = scene_file.read()

            prompt = (
                f"Please read the following sets of scenes for chapter {chapter_number} of my sci-fi novel.\n\n"
                f"Please re-write the scenes and include any details that you think add value. Please don't provide a review.\n"
                f"Some things to consider:\n"
                f"Are there hints of character goals?\n"
                f"Is there conflict in each scene? It can be conflict between characters, or between the character and their environment.\n\n"
                f"Here are the scenes:\n\n{scene_content}\n\n"
                # f"Should there be an indication of the character's emotions?"
                # f"Please don't provide any commentary or feedback here."
            )

            print("prompt....")
            print(prompt)
            # Send prompt to OpenAI API
            response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative author reviewing the structuring of these detailed scenes.")

            with open(f"re_scenes_chapter_{chapter_number}.md", "w") as scene_file:
                scene_file.write(response)

            messagebox.showinfo("Success", f"Chapter {chapter_number} RE-saved successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid chapter number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to RE-write scene: {str(e)}")