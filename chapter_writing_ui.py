from tkinter import ttk, messagebox
from ai_helper import send_prompt
import re

class ChapterWritingUI:
    def __init__(self, parent):
        self.parent = parent

        # self.model="gpt-4o"
        self.model="gemini-1.5-pro"

        # Frame setup for chapter writing UI
        self.chapter_writing_frame = ttk.Frame(parent)
        self.chapter_writing_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.chapter_writing_frame, text="Write Chapters", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Entry to select chapter number
        self.chapter_label = ttk.Label(self.chapter_writing_frame, text="Enter Chapter Number:")
        self.chapter_label.pack()
        self.chapter_number_entry = ttk.Entry(self.chapter_writing_frame)
        self.chapter_number_entry.pack(pady=5)

        # Button to write chapter
        self.write_chapter_button = ttk.Button(self.chapter_writing_frame, text="Write Chapter", command=self.write_chapter)
        self.write_chapter_button.pack(pady=20)

        # Button to re-write chapter
        self.write_chapter_button = ttk.Button(self.chapter_writing_frame, text="Re-Write Chapter", command=self.rewrite_chapter)
        self.write_chapter_button.pack(pady=20)

    # Helper function to open the main lore file
    def open_file(self, filename):
        print("opening file: " + filename)
        with open(filename, "r") as file:
            data = file.read()
        return data

    def normalize_markdown(self, scenes):
        # Match scene headings specifically (e.g., **Scene 1: ...**)
        normalized_scenes = re.sub(r"\*\*Scene (\d+): (.+?)\*\*", r"### Scene \1: \2", scenes)
        return normalized_scenes


    def write_chapter(self):
        try:
            chapter_number = int(self.chapter_number_entry.get())

            params = self.open_file("parameters.txt")
            lore_content = self.open_file("generated_lore.md")
            characters_content = self.open_file("characters.md")
            en_characters_content = self.open_file("characters.md")
            relationships_content = self.open_file("relationships.md")
            factions_content = self.open_file("factions.md")


            with open(f"scenes_chapter_{chapter_number}.md", "r") as scenes_file:
                scenes = scenes_file.read()

            print("Using scenes for this chapter")
            # Increment the chapter number based on the response (assuming response includes multiple chapters)
            scene_count = scenes.count("### ")
            print("scene_count", scene_count)

            # Normalize markdown formatting
            scenes = self.normalize_markdown(scenes)

            # Detect the number of scenes using regex
            scene_titles = re.findall(r"### (.+)", scenes)  # Extracts titles after "### "
            scene_count = len(scene_titles)

            print(f"Detected {scene_count} scenes in Chapter {chapter_number}.")
            print("Trying to generate chapter....")

            scenes = []

            # TODO: IF we are on the final chapter, include that detail in the prompt. The LLMs dont know to end.
            # Potentially we need to state where we are in the story arc??

            # Iterate over the scenes and make API requests
            for idx, title in enumerate(scene_titles, start=1):
                print(f"Processing Scene {idx}: {title}")

                # Generate prompt for the API request
                prompt = (
                    f"Please generate text for Chapter {chapter_number} of my novel based upon the information I provide here."
                    # f"Please generate the complete text for Chapter {chapter_number} of my novel based upon the information I provide here."
                    # f"Ensure the narrative is engaging, includes vivid descriptions, and develops the characters and plot as described."
                    f"You may wish to take a little time to think before writing.\n"
                    # f"Here are the story parameters:\n\n"
                    # f"{parameters}\n\n"
                    f"Here is the background lore of the novel, plus a list of the major factions, the main characters, and some minor characters.\n\n"
                    f"{lore_content}\n\n"
                    # f"Now I will provide the high-level structure of all chapters:\n\n"
                    f"Now I will provide the scenes of Chapter {chapter_number}, which will guide you on how the chapter should look like."
                    f"Using the information please generate text for Scene {idx}.\n\n"
                    f"{scenes}\n\n"
                    f"When generating text for this scene consider important factors on how to structure a chapter, e.g.: \n"
                    f"* Setting the scene for the chapter.\n"
                    f"* introduce a conflict that escalates the tension.\n"
                    f"* consider the potential resolution of this chapter's conflict (if necessary) and set up the events in the later chapters.\n\n"
                    f"Include the following considerations while writing:\n"
                    f"* location descriptions (as appropriate for the genre)\n"
                    f"* character descriptions\n"
                    f"* character thoughts and emotions\n"
                    f"* character introspections (what are the main characters thinking about?)\n"
                    f"* character dialogue\n"
                    f"* character actions that progress the story\n"
                    f"* character interactions beyond dialogue\n"
                    f"and anything else as needed to bring the scene to life. Please only generate prose with no additional comments.\n"
                    f"You have thousands of tokens available for the output, so there are no problems with generating a lot of text."
                )

                print(prompt)

                # Perform API request (example call)
                # response = send_prompt(prompt, model="gpt-4-turbo", max_tokens=800, temperature=0.7)
                # response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative storyteller like George RR Martin.")
                response = send_prompt(prompt, model=self.model)
                scenes.append(response)

                # Save the generated scene to a file
                with open(f"scene_{chapter_number}_{idx}.md", "w") as scene_file:
                    scene_file.write(response)
                print(f"Scene {idx} saved as scene_{chapter_number}_{idx}.md.")


            # Combine all scenes into one string
            chapter_content = "\n\n".join(scenes)

            # Save the combined chapter to a file
            chapter_filename = f"chapter_{chapter_number}.md"
            with open(chapter_filename, "w") as chapter_file:
                    chapter_file.write(chapter_content)

            print(f"Chapter {chapter_number} saved as {chapter_filename}")

        #    print(f"Chapter {chapter_number} saved successfully to {chapter_filename}")
            messagebox.showinfo("Success", f"Chapter {chapter_number} saved successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid chapter number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write chapter: {str(e)}")



    def rewrite_chapter(self):
        try:
            chapter_number = int(self.chapter_number_entry.get())

            parameters = self.open_file("parameters.txt")
            lore_content = self.open_file("generated_lore.md")
            characters_content = self.open_file("characters.md")
            en_characters_content = self.open_file("characters.md")
            relationships_content = self.open_file("relationships.md")
            factions_content = self.open_file("factions.md")

            structure = self.open_file("story_structure.md")  # High-level structure

            # High-level structure
            # with open("story_structure.md", "r") as act_file:
            #     structure = act_file.read()

            # Chapter to re-write
            # TODO: remove?
            chapter_filename = f"chapter_{chapter_number}.md"
            with open(chapter_filename, "r") as chapter_file:
                chapter_file_in = chapter_file.read()

        #   # with open("chapter_.md", "r") as scene_file:
        #   #     scene = scene_file.read()


            # Prompt
            print("Trying to re-generate chapter....")
            prompt = (
                f"Please read and then re-write this scene of Chapter {chapter_number} in my novel.\n"
                f"The scene is far too short and only a rough draft of what I need. Please make it much longer."
                f"Please also check that the narrative is engaging, includes vivid descriptions, and develops the characters and plot as described.\n"
                f"As an English Professor in storytelling, Ask yourself 'what is missing?'" # Don't tell me what's missing, but make the changes."
                f"As a reminder, here are the story parameters:\n\n"
                f"{parameters}\n\n"
                # f"For clarity of the overall story structure, here is the high-level outline.\n"
                # f"{structure}\n\n"
                # f"We should check that the scene text fits the structure.\n\n"
                f"When reading the text please check if there is there anything missing from the text? Such as:\n"
                f"* location descriptions (as appropriate for the genre)\n"
                f"* character dialogue\n"
                f"* character descriptions\n"
                f"* character thoughts and emotions\n"
                f"* character introspections (what are the main characters thinking about?)\n"
                f"* character actions that progress the story\n"
                f"* character interactions beyond dialogue\n\n"
                f"Here is the text for this chapter:\n\n"
                f"{chapter_file_in}"
            )

            # GPT4o
            # response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative storyteller like George RR Martin.")
            response = send_prompt(prompt, model=self.model)
            # o1
            # response = send_prompt_o1(prompt, model="o1-mini")


            # Save the generated chapter content to a file
            print("Trying to RE-save Chapter_(number).md")
            chapter_filename = f"re_chapter_{chapter_number}.md"

            with open(chapter_filename, "w") as chapter_file:
                chapter_file.write(response)

            print(f"Chapter {chapter_number} saved successfully to {chapter_filename}")
            messagebox.showinfo("Success", f"Chapter {chapter_number} RE-saved successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid chapter number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to RE-write chapter: {str(e)}")
