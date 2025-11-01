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

# --- Define Model Configurations ---
# Define configurations for each model
_model_config = { # Renamed to avoid potential naming conflicts if imported directly
    "gpt-4o": lambda prompt: send_prompt_oai(
        prompt=prompt,
        model="gpt-4o",
        max_tokens=16384,
        temperature=0.7,
        role_description="You are an expert storyteller focused on character relationships."
    ),
    #"o1": lambda prompt: send_prompt_o1(prompt, model="o1"), # Assuming these are placeholders or deprecated
    #"o1-mini": lambda prompt: send_prompt_o1(prompt, model="o1-mini"),
    "o3": lambda prompt: send_prompt_o1(prompt, model="o3"),
    "o4-mini": lambda prompt: send_prompt_o1(prompt, model="o4-mini"),
    "gpt-5-2025-08-07": lambda prompt: send_prompt_o1(prompt, model="gpt-5-2025-08-07"),
    #"gpt-4-turbo": lambda prompt: send_prompt_oai( # Added gpt-4-turbo if supported by send_prompt_oai
    #    prompt=prompt,
    #    model="gpt-4-turbo",
    #    max_tokens=8192, # Example token limit
    #    temperature=0.7,
    #    role_description="You are a helpful fiction writing assistant."
    #),
    #"gemini-1.5-pro-latest": lambda prompt: send_prompt_gemini( # Renamed key to match main.py example
    #    prompt=prompt,
    #    model_name="gemini-1.5-pro-latest", # Use the correct API model name here
    #    max_output_tokens=8192,
    #    temperature=0.7,
    #    top_p=1,
    #    top_k=40
    #),
    #"gemini-2.0-pro-exp-02-05": lambda prompt: send_prompt_gemini( # Keep if needed
    #     prompt=prompt,
    #     model_name="gemini-2.0-pro-exp-02-05",
    #     max_output_tokens=8192,
    #     temperature=0.7,
    #     top_p=1,
    #     top_k=40
    #),
    "gemini-2.5-pro-exp-03-25": lambda prompt: send_prompt_gemini( # Keep if needed
         prompt=prompt,
         model_name="gemini-2.5-pro-exp-03-25",
         max_output_tokens=8192,
         temperature=0.7,
    ),
    #"claude-3-5-sonnet": lambda prompt: send_prompt_claude( # Keep if needed
    #     prompt=prompt,
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=4096,
    #     temperature=1.0
    #),
    #"claude-3-7-sonnet": lambda prompt: send_prompt_claude( # Keep if needed
    #     prompt=prompt,
    #     model="claude-3-7-sonnet-20250219",
    #     max_tokens=4096,
    #     temperature=0.7
    #),
    "claude-4-5-sonnet": lambda prompt: send_prompt_claude( # Keep if needed
         prompt=prompt,
         model="claude-sonnet-4-5-20250929",
         max_tokens=4096,
         temperature=0.7
    ),
}
# --- End Model Configurations ---

def get_supported_models():
    """Returns a list of supported model names."""
    return list(_model_config.keys())

def send_prompt(prompt, model="gpt-4o"):
    """Sends a prompt to the specified AI model."""
    # Check if the model is supported
    if model not in _model_config:
        # Try adding '-latest' if applicable (e.g., for gemini-1.5-pro)
        if f"{model}-latest" in _model_config:
             model = f"{model}-latest"
        else:
             supported_models = get_supported_models()
             raise ValueError(f"Unsupported model: {model}. Supported models are: {supported_models}")


    print(f"Attempting to use model: {model}")
    # Call the corresponding function by looking up the dictionary
    try:
        return _model_config[model](prompt)
    except Exception as e:
        print(f"Error calling model '{model}': {e}")
        # Optionally, implement fallback logic here or re-raise
        raise # Re-raise the exception for now


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


def send_prompt_claude(prompt, model="claude-3-sonnet-20240229", max_tokens=4096, temperature=0.7,
                     role_description="You are a skilled creative writer focused on producing original fiction."):
    """
    Sends a prompt to Anthropic's Claude API and returns the generated text.
    
    Args:
        prompt: The text prompt to send.
        model: The Claude model to use (e.g., "claude-3-opus-20240229").
        max_tokens: Maximum number of tokens to generate.
        temperature: Controls randomness of generations.
        role_description: System prompt that sets the context for the model.
        
    Returns:
        The generated text, or None if there was an error.
    """
    try:
        # Create a message with system and user content
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=role_description,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        print("Used model: ", model)
        
        # Extract the content from the response
        return response.content[0].text
        
    except Exception as e:
        print(f"Error generating content with Claude: {e}")
        return None

