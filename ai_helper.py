# ai_helper.py
# https://platform.openai.com/docs/models

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # This will load environment variables from the .env file

# Create an OpenAI client instance
# Ensure you've set your OpenAI API key
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

# Send prompts with GPT4o and 4o-mini
def send_prompt(prompt, model="gpt-4o-mini", max_tokens=1500, temperature=0.7,
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
