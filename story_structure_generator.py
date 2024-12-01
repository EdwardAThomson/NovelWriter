# story_structure_generator.py
from ai_helper import send_prompt, send_prompt_o1

def generate_structure_from_api():
        try:
            # Load the lore and relationships
            with open("generated_lore.md", "r") as lore_file:
                lore_content = lore_file.read()

            with open("relationships.md", "r") as rel_file:
                relationships_content = rel_file.read()

            # Generate the prompt for high-level structure
            ### the relationships information is too much for GPT4o
            prompt = (
                f"Please generate a high-level structure for a story based on the following information.\n"
                f"Please use the following background parameters, factions, and characters:\n\n{lore_content}\n\n"
                f"For reference please see the relationships between characters:\n\n{relationships_content}\n\n"
                f"Provide a structured outline with major plot points, faction interactions, character arcs, and key events.\n"
                f"Here is an example sequence of events that make up the story:\n"
                f"* Beginning: Introduce characters, setting, and basic conflict.\n"
                f"* Rising Action: Develops the main conflict through a series of events.\n"
                f"* First Climax: a turning point and important moment of the story. Some hints of resolution, but also further conflict.\n"
                f"* Solution Finding: a plan starts to come together, but not all parts of the solution are revealed.\n"
                f"* Second Climax: a turning point and the most intense moment of the story. The solution to conflict is finally revealed.\n"
                f"* Resolution (Denouement):  Events that follow the climax and begin to resolve the conflict. Concludes the story, tying up loose ends.\n\n"
                f"Please Development outline the main character arcs: The transformation or growth a character undergoes.\n"
                f"* Consider the depth and complexity: Creating multi-dimensional characters with strengths, flaws, and motivations.\n\n"
                f"Please provide the structure in markdown format."
            )

            print(prompt)

            # Send prompt to OpenAI API --- uses GTP4o
            # response = send_prompt(prompt, model="gpt-4o", max_tokens=16384 , temperature=0.7, role_description="You are an expert storyteller focusing on developing a compelling story structure.")

            # o1 -- this uses o1 instead of GPT4o
            response = send_prompt_o1(prompt, model="o1-mini")

            # Save the structure to a file
            print("Trying to save file as markdown....")
            with open("story_structure.md", "w") as struct_file:
                struct_file.write(response)
            print("Story structure saved successfully to story_structure.md")


        except Exception as e:
            print(f"Failed to generate story structure: {e}")
            # messagebox.showerror("Error", f"Failed to generate story structure: {str(e)}")

# Call the function if running this script directly
if __name__ == "__main__":
    generate_structure_from_api()