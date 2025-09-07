import openai
from typing import Dict

OPENAI_MODEL = "gpt-4o"


def build_ad(persona: str, product: str) -> Dict:
    prompt = (
        f"Create ad copy for the following product aimed at this persona:\n{persona}\n"
        f"Product: {product}\n"
        "Return a headline, description, CTA and an image prompt for DALL-E."
    )
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response["choices"][0]["message"]["content"].strip()
    return {
        "text": text,
        "platform": "Meta",
    }


if __name__ == "__main__":
    persona = "Veteran Harley rider interested in rugged accessories"
    ad = build_ad(persona, "weatherproof saddlebags")
    print(ad)
