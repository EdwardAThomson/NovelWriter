# relationship_generator.py
import json
from ai_helper import send_prompt
import re

def generate_relationships_from_api():

   # Try to load characters from the JSON file
   with open("characters.md", "r") as char_file:
            character_data = char_file.read()

   print("character_data...")
   # print(character_data)

   prompt = (
     f"Here is a list of characters in a story:\n\n{character_data}\n\n"
     f"Generate a list of relationships between these characters. \n"
     f"Include each character's name, the character they are related to, and the nature of the relationship (e.g., ally, rival, family). \n"
     f"Please provide this in markdown format, but please don't insert backticks or the word 'markdown'."
   )

   print("prompt....")
   print(prompt)

   response = send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, role_description="You are an expert storyteller focused on character relationships.")
   print(response)

   with open("relationships.md", "w") as file:
       file.write(response)


# Call the function if running this script directly
if __name__ == "__main__":
    generate_relationships_from_api()
