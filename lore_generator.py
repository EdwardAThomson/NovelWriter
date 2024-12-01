# lore_generator.py
from ai_helper import send_prompt

def generate_lore_from_api(data):
    prompt = (
        f"Please generate background lore for a novel length story using the following parameters:\n\n"
        f"{data}\n\n"
        f"Provide a compelling summary that establishes the setting and major elements of the story. Include the major factions involved.\n"
        f"Then, please create a new section for the major factions. List out their main planets.\n"
        f"Then, please create a new section for Key Characters. Please also include a list of minor characters too."
        f"Please provide a list of key characters in markdown, include each character's name, role, gender (male or female), faction alignment, character description.\n"
        f"No more text should come after the characters list.\n"
        f"Please use markdown format for the output"
    )

    return send_prompt(prompt, model="gpt-4o", max_tokens=16384, temperature=0.7,
                       role_description="You are a creative and descriptive storyteller. You will create original text only.")


    # prompt = (
    #     f"Generate a background lore for a {data['genre']} story.\n"
    #     f"Central Theme: {data['central_theme']}\n"
    #     f"Target Audience: {data['target_audience']}\n"
    #     f"Key Themes: {data['key_themes']}\n"
    #     f"Descriptive Style: {data['style_preferences']}\n"
    #     f"Provide a compelling summary that establishes the setting and major elements of the story.\n"
    #     f"Then, create a new section for Key Characters. But also include a list of minor characters too."
    #     f"Please provide a list of key characters in markdown, include each character's name, role, gender (male or female), character description.\n"
    #     f"No more text should come after the characters list."
    # )

    # prompt = (
    #     f"Generate a background lore for a {data['genre']} story.\n"
    #     f"Central Theme: {data['central_theme']}\n"
    #     f"Target Audience: {data['target_audience']}\n"
    #     f"Key Themes: {data['key_themes']}\n"
    #     f"Descriptive Style: {data['style_preferences']}\n"
    #     f"Provide a compelling summary that establishes the setting and major elements of the story."
    #     f"Then, create a new section for Key Characters."
    #     f"Please provide a list of key characters in valid JSON format only, include each character's name, role, gender (male or female), character description. No more text should come after the JSON objects"
    # )


