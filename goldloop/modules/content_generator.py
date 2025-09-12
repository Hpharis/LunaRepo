import os
import json
from pathlib import Path
from typing import Dict
import openai

OPENAI_MODEL = "gpt-4o"

# Load persona definitions from JSON
with open("src/data/personas.json", "r", encoding="utf-8") as f:
    PERSONAS = json.load(f)


def apply_persona_prompt(category: str, topic: str) -> str:
    """
    Build a content prompt based on persona voice + topic.
    """
    persona = PERSONAS.get(category, PERSONAS["blog"])
    return (
        f"You are writing as {persona['name']}, the {persona['role']} at TouringMag. "
        f"Write in this style: {persona.get('voice','')} "
        f"\n\nTopic: {topic}\n\n"
        "Include SEO-friendly headings, metadata, and natural sub-sections."
    )


def generate_content(category: str, topic: str) -> str:
    """
    Generate raw article content from OpenAI based on persona + topic.
    """
    prompt = apply_persona_prompt(category, topic)
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"].strip()


from datetime import datetime

def wrap_with_frontmatter(category: str, title: str, summary: str, content: str) -> str:
    """
    Add YAML frontmatter to article, using persona metadata.
    Matches Astro schema: summary, pubDate, heroImage, thumbnail, author, role.
    """
    persona = PERSONAS.get(category, PERSONAS["blog"])
    pub_date = datetime.utcnow().isoformat() + "+00:00"
    slug = title.replace(" ", "-").lower()

    frontmatter = f"""---
title: "{title}"
summary: "{summary}"
pubDate: "{pub_date}"
heroImage: "/assets/{slug}-hero.jpg"
thumbnail: "/assets/{slug}-thumb.jpg"
author: "{persona['name']}"
role: "{persona['role']}"
---
"""
    return frontmatter + "\n" + content



def save_article(category: str, title: str, description: str, content: str):
    """
    Save article into src/content/{category}/ with proper filename.
    """
    filename = f"src/content/{category}/{title.replace(' ', '-').lower()}.md"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text(content, encoding="utf-8")
    print(f"✅ Article saved to {filename}")


if __name__ == "__main__":
    # Example run
    category = "guides"
    topic = "Packing for a 7-Day Ride"
    description = "How to efficiently prepare and pack for a week-long motorcycle tour."

    raw_content = generate_content(category, topic)
    article = wrap_with_frontmatter(category, topic, description, raw_content)
    save_article(category, topic, description, article)

