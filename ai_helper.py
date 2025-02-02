# ai_helper.py
# https://platform.openai.com/docs/models

from openai import OpenAI
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()  # This will load environment variables from the .env file

# Create an OpenAI client instance
# Ensure you've set your OpenAI API key
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Adding the possibility of using the Gemini API
g_api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=g_api_key)

def send_prompt(prompt, model="gpt-4o"):
    # Define configurations for each model
    model_config = {
        "gpt-4o": lambda prompt: send_prompt_oai(
            prompt=prompt,
            model="gpt-4o",
            max_tokens=16384,
            temperature=0.7,
            role_description="You are an expert storyteller focused on character relationships."
        ),
        "o1": lambda prompt: send_prompt_o1(prompt, model="o1"),
        "o1-mini": lambda prompt: send_prompt_o1(prompt, model="o1-mini"),
        "gemini-1.5-pro": lambda prompt: send_prompt_gemini(
            prompt=prompt,
            model_name="gemini-1.5-pro",
            max_output_tokens=8192,
            temperature=0.9,
            top_p=1,
            top_k=40
        ),
    }

    # Check if the model is supported
    if model not in model_config:
        raise ValueError(f"Unsupported model: {model}")

    print(f"trying:{model}")
    # Call the corresponding function by looking up the dictionary
    return model_config[model](prompt)


# def send_prompt(prompt, model="gpt-4o"):
#     # Default parameter mapping
#     if model == "gpt-4o":
#         print(f"trying:{model}")
#         return send_prompt_oai(
#             prompt=prompt,
#             model=model,
#             max_tokens=16384,  # Default for OpenAI
#             temperature=0.7,
#             role_description="You are an expert storyteller focused on character relationships."
#         )
#     elif model == "o1":
#         print(f"trying:{model}")
#         return send_prompt_o1(prompt, model=model)
#     elif model == "gemini-1.5-pro":
#         print(f"trying:{model}")
#         return send_prompt_gemini(
#             prompt=prompt,
#             model_name=model,  # Mapped internally to "model_name"
#             max_output_tokens=8192,  # Default for Gemini
#             temperature=0.9,
#             top_p=1,
#             top_k=40
#         )
#     else:
#         raise ValueError(f"Unsupported model: {model}")




# Send prompts with GPT4o and 4o-mini
def send_prompt_oai(prompt, model="gpt-4o", max_tokens=1500, temperature=0.7,
                role_description="You are a helpful fiction writing assistant. You will create original text only."):
    # Make the chat completion request using the OpenAI client
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": role_description},
            {"role": "user", "content": prompt},
        ],
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    print("model used: ", model)
    # Extract the generated text from the response
    content = response.choices[0].message.content

    return content

# Send prompts with o1 models
# model="o1-preview"
# model="o1-mini",
def send_prompt_o1(prompt, model="o1-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
            "role": "user",
            "content": prompt
            }
        ]
    )

    print("Used model: ", model)
    content = response.choices[0].message.content

    return content


def send_prompt_gemini(prompt, model_name="gemini-1.5-pro", max_output_tokens=1024, temperature=0.9, top_p=1, top_k=1):
    """
    Sends a prompt to the Gemini API and returns the response.

    Args:
        prompt: The text prompt to send.
        model_name: The name of the Gemini model to use (e.g., "gemini-pro").
        max_output_tokens: The maximum number of tokens to generate.
        temperature: Controls the randomness of the output.
        top_p: Controls the diversity of the output.
        top_k: Controls the diversity of the output (similar to top_p).
    Returns:
        The generated text, or None if there was an error.
    """

    model = genai.GenerativeModel(model_name)

    generation_config = genai.types.GenerationConfig(
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k
    )


    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=False
        )

        print("Used model: ", model)

        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

