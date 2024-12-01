# chapter_generator.py

import json
from ai_helper import send_prompt, send_prompt_o1


def generate_chapter(chapter_number):

    # Parameters
    # Lore
    ## characters
    ## Factions
    # Chapter Outlines

    try:
        # Parameters
        with open("parameters.txt", "r") as param_file:
            parameters = param_file.read()

        # Lore
        with open("generated_lore.md", "r") as lore_file:
            lore = lore_file.read()

        # Chapter outlines
        with open("chapter_outlines.md", "r") as chapter_file:
            chapter_file_in = chapter_file.read()


        # Prompt
        print("Trying to generate chapter....")
        prompt = (
                f"Please generate the complete text for Chapter {chapter_number} of my novel based upon the information I provide here."
                f"Ensure the narrative is engaging, includes vivid descriptions, and develops the characters and plot as described."
                f"You may wish to take a little time to think before writing.\n"
                f"Here are the story parameters:\n\n"
                f"{parameters}\n\n"
                f"Here is the background lore of the novel, plus a list of the major factions, the main characters, and some minor characters.\n\n"
                f"{lore}\n\n"
                f"Now I will provide the high-level structure of all chapters:\n\n"
                f"{chapter_file_in}\n\n"
                f"When generating text for this chapter consider how to structure a chapter, e.g.: \n"
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
                f"and anything else as needed to bring the scene to life.\n"
                f"You have thousands of tokens available for the output, so there are no problems with generating a lot of text."
        )

        print(prompt)

        # Send the prompt to generate the content for the section
        ### model="gpt-4o"
        ### GPT4 works with roles, but o1 models don't seem to.

        # GPT4
        # response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative storyteller like George RR Martin.")
        # o1-mini    //     o1-preview
        response = send_prompt_o1(prompt, model="o1-preview")

        # Save the generated chapter content to a file
        print("Trying to save Chapter_(number).md")
        chapter_filename = f"chapter_{chapter_number}.md"
        with open(chapter_filename, "w") as chapter_file:
            chapter_file.write(response)

        print(f"Chapter {chapter_number} saved successfully to {chapter_filename}")

    except Exception as e:
        print(f"Failed to generate Chapter {chapter_number}: {e}")


def regenerate_chapter(chapter_number):
        try:
            # Parameters
            with open("parameters.txt", "r") as param_file:
                parameters = param_file.read()

            # High-level structure
            with open("story_structure.md", "r") as act_file:
                structure = act_file.read()

            # Chapter to re-write
            chapter_filename = f"chapter_{chapter_number}.md"
            with open(chapter_filename, "r") as chapter_file:
                chapter_file_in = chapter_file.read()


            # Prompt
            print("Trying to re-generate chapter....")
            prompt = (
                f"Please read and then re-write the chapter of my novel. This is Chapter {chapter_number}.\n"
                f"Please check that the narrative is engaging, includes vivid descriptions, and develops the characters and plot as described.\n"
                f"As a reminder, here are the story parameters:\n\n"
                f"{parameters}\n\n"
                f"For clarity of the overall story structure, here is the high-level outline.\n"
                f"{structure}\n\n"
                f"We should check that the chapter text fits the structure.\n\n"
                f"When reading the text please check if there is there anything missing from the text? Such as:\n"
                f"* location descriptions (as appropriate for the genre)\n"
                f"* character dialogue\n"
                f"* character descriptions\n"
                f"* character thoughts and emotions\n"
                f"* character introspections (what are the main characters thinking about?)\n"
                f"* character actions that progress the story\n"
                f"* character interactions beyond dialogue\n\n"
                f"Here is the text for Chapter {chapter_number}\n\n"
                f"{chapter_file_in}"
            )

            # GPT4
            # response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are a creative storyteller like George RR Martin.")
            # o1
            response = send_prompt_o1(prompt, model="o1-mini")


            # Save the generated chapter content to a file
            print("Trying to RE-save Chapter_(number).md")
            chapter_filename = f"chapter_{chapter_number}.md"

            with open(chapter_filename, "w") as chapter_file:
                chapter_file.write(response)

            print(f"Chapter {chapter_number} saved successfully to {chapter_filename}")

        except Exception as e:
            print(f"Failed to re-generate Chapter {chapter_number}: {e}")

