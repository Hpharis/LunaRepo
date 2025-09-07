import os
from typing import Dict

import openai

OPENAI_MODEL = "gpt-4o"


def generate_content(persona: str, topic: str) -> str:
    prompt = (
        f"Write a blog post about {topic} for the following persona:\n{persona}\n"
        "Include SEO friendly headings and metadata."
    )
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    persona = "Harley rider who loves custom bikes"
    print(generate_content(persona, "best maintenance tips"))
