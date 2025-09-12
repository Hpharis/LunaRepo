import os
import sys
import sqlite3
import subprocess
import random
import requests
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
from dotenv import load_dotenv
import openai
import argparse
from datetime import datetime, timezone, timedelta
from PIL import Image
import io
import shutil
import yaml
from fpdf import FPDF
from bs4 import BeautifulSoup
from modules.affiliate_injector import load_affiliate_links, inject_links
from modules.persona_engine import get_persona, apply_persona_prompt

# -------------------------------------------------------------------
# Path setup
# -------------------------------------------------------------------

# Always resolve to the goldloop/ folder (where modules/ lives)
GOLDLOOP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOLDLOOP_ROOT))

# Repo root = parent of goldloop (where touringmag-site lives)
REPO_ROOT = GOLDLOOP_ROOT.parent

# Paths
DB_FILE      = GOLDLOOP_ROOT / "data" / "goldloop.db"
EXPORT_BASE  = REPO_ROOT / "touringmag-site" / "src" / "content"
ASSETS_DIR   = REPO_ROOT / "touringmag-site" / "public" / "assets"
LOG_FILE     = GOLDLOOP_ROOT / "logs" / "affiliate_log.txt"

EXPORT_BASE.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Load env vars
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")



# -------------------
# Helpers
# -------------------

def search_stock_image(query: str):
    """Search Unsplash for a motorcycle touring image based on the article title."""
    try:
        if not UNSPLASH_ACCESS_KEY:
            return None
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": f"motorcycle touring {query}",
            "orientation": "landscape",
            "per_page": 1,
        }
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
        return None
    except Exception as e:
        print(f"[ERROR] Unsplash API error: {e}")
        return None


def enhance_with_ai(base_path, hero_path):
    """Stub: just copy stock → hero path unchanged."""
    shutil.copy(base_path, hero_path)


def init_db():
    """Ensure the posts table exists before inserting."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        heroImage TEXT,
        content TEXT NOT NULL,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def slugify(title: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")


def generate_images(title: str, slug: str):
    """Generate hero + thumbnail using stock first, fallback to DALL·E."""
    try:
        stock_img = search_stock_image(title)
        if stock_img:
            base_path = ASSETS_DIR / f"{slug}-base.jpg"
            with open(base_path, "wb") as f:
                f.write(requests.get(stock_img).content)

            hero_path = ASSETS_DIR / f"{slug}-hero.jpg"
            enhance_with_ai(base_path, hero_path)

            thumb_path = ASSETS_DIR / f"{slug}-thumb.jpg"
            image = Image.open(hero_path)
            image.thumbnail((512, 512))
            image.save(thumb_path, "JPEG", quality=85, optimize=True)

            return f"/assets/{slug}-hero.jpg", f"/assets/{slug}-thumb.jpg"
    except Exception as e:
        print(f"[ERROR] Stock image processing failed: {e}")

    # --- DALL·E fallback ---
    try:
        prompt = f"Motorcycle touring photo, {title}, professional magazine style"
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
        )
        hero_url = response["data"][0]["url"]
        hero_bytes = requests.get(hero_url).content

        hero_path = ASSETS_DIR / f"{slug}-hero.jpg"
        with open(hero_path, "wb") as f:
            f.write(hero_bytes)

        thumb_path = ASSETS_DIR / f"{slug}-thumb.jpg"
        image = Image.open(io.BytesIO(hero_bytes))
        image.thumbnail((512, 512))
        image.save(thumb_path, "JPEG", quality=85, optimize=True)

        return f"/assets/{slug}-hero.jpg", f"/assets/{slug}-thumb.jpg"
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return "/assets/blog-placeholder-1.jpg", "/assets/blog-placeholder-1.jpg"

# -------------------
# Prompt builder
# -------------------

def build_prompt(mode: str) -> str:
    """Return a section-specific content prompt with persona voice applied."""

    if mode == "gear":
        base_prompt = """
        You are a product reviewer for TouringMag (motorcycle touring gear).
        IMPORTANT: Always wrap string values in double quotes (") in YAML.
        Respond ONLY in valid YAML (without markdown code fences) with:

        title: A clear product review title (max 12 words)
        summary: One-sentence SEO overview
        body: |
          <h2>Overview</h2>
          <p>What the product is, who it’s for.</p>
          <h2>Specs</h2>
          <ul>
            <li>Feature</li>
          </ul>
          <h2>Pros & Cons</h2>
          <p>Pros: ...</p>
          <p>Cons: ...</p>
          <h2>Verdict</h2>
          <p>Overall rating and buyer’s tip.</p>
        """
    elif mode == "upgrades":
        base_prompt = """
        You are writing an upgrade guide for TouringMag (motorcycle touring upgrades).
        IMPORTANT: Always wrap string values in double quotes (") in YAML.
        Respond ONLY in valid YAML (without markdown code fences) with:

        title: Upgrade title (max 12 words, include keyword)
        summary: One-sentence SEO overview
        body: |
          <h2>Why Upgrade</h2>
          <p>Why this matters for touring.</p>
          <h2>Benefits</h2>
          <ul>
            <li>Benefit</li>
          </ul>
          <h2>Recommended Products</h2>
          <ul>
            <li>Product suggestion</li>
          </ul>
          <h2>Install Difficulty</h2>
          <p>Easy / Intermediate / Advanced</p>
        """
    elif mode == "guides":
        base_prompt = """
        You are writing a detailed how-to guide for TouringMag (motorcycle touring).
        IMPORTANT: Always wrap string values in double quotes (") in YAML.
        Respond ONLY in valid YAML (without markdown code fences) with:

        title: Guide title (max 12 words, include keyword)
        summary: One-sentence SEO overview
        body: |
          <h2>Introduction</h2>
          <p>Why this guide is useful for touring riders.</p>
          <h2>Tools & Materials</h2>
          <ul>
            <li>Tool or item</li>
          </ul>
          <h2>Step-by-Step Instructions</h2>
          <ol>
            <li>Step 1 instruction</li>
            <li>Step 2 instruction</li>
          </ol>
          <h2>Pro Tips</h2>
          <ul>
            <li>Tip</li>
          </ul>
          <h2>Safety Notes</h2>
          <p>Warnings or common mistakes to avoid.</p>
          <h2>Difficulty</h2>
          <p>Beginner / Intermediate / Advanced</p>
        """
    else:  # blog
        base_prompt = """
        You are a lifestyle writer for TouringMag (motorcycle touring).
        IMPORTANT: Always wrap string values in double quotes (") in YAML.
        Respond ONLY in valid YAML (without markdown code fences) with:

        title: Blog title (max 12 words, include keyword)
        summary: One-sentence SEO overview
        body: |
          <h2>Introduction</h2>
          <p>Story or hook.</p>
          <h2>Main Story</h2>
          <p>3–4 paragraphs of narrative or opinion.</p>
          <h2>Takeaway</h2>
          <p>Lesson, reflection, or call to action.</p>
        """

    return apply_persona_prompt(mode, base_prompt)

# -------------------
# Article generator
# -------------------

def generate_article(mode="blog"):
    """Generate a full article with metadata, images, and DB insert."""
    init_db()
    prompt = build_prompt(mode)

    print(f"[INFO] Requesting {mode} article from OpenAI...")
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response["choices"][0]["message"]["content"]

    # Strip markdown fences if present
    if content.startswith("```"):
        content = content.strip().strip("`")
        if content.lower().startswith("yaml"):
            content = content[4:].strip()

    try:
        parsed = yaml.safe_load(content)
    except Exception as e:
        print("[WARN] YAML parse failed, falling back to raw content", e)
        parsed = {}

    title = parsed.get("title") or f"TouringMag {mode.capitalize()} {datetime.now().strftime('%Y%m%d%H%M%S')}"
    summary = parsed.get("summary", f"TouringMag {mode} article.")
    body = parsed.get("body", content)
    slug = slugify(title) or f"touringmag-{mode}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Persona metadata
    persona = get_persona(mode)

    # 🛡 Guide fallback: inject steps if missing
    if mode == "guides" and "<ol>" not in body:
        print("[WARN] Guide missing step list — injecting fallback outline.")
        body += """
        <h2>Step-by-Step Instructions</h2>
        <ol>
          <li>Prepare your motorcycle and gather tools.</li>
          <li>Follow the procedure carefully step by step.</li>
          <li>Test and verify before riding.</li>
        </ol>
        <h2>Difficulty</h2>
        <p>Beginner</p>
        """

    hero, thumb = generate_images(title, slug)

    # Save to DB
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR IGNORE INTO posts (title, slug, summary, content, heroImage)
    VALUES (?, ?, ?, ?, ?)
    """, (title, slug, summary, body, hero))
    conn.commit()
    conn.close()

    print(f"[OK] Article stored: {title} ({slug})")
    return slug, title, summary, body, hero, thumb, persona
 
def sanitize_comment(text: str) -> str:
    """
    YAML-safe editorComment:
    - collapse newlines
    - strip double/single quotes
    - plain string, no Markdown formatting
    """
    if not text:
        return "''"
    safe = text.replace("\n", " ").strip()
    safe = safe.replace('"', "").replace("'", "").replace("''", "")
    return f"'{safe}'"

 
def generate_editor_comment(mode, title, summary, persona):
    """
    Generate a short editor's note in the persona's voice.
    Always returns a non-empty string.
    """
    prompt = (
        f"You are {persona['name']}, the {persona['role']} at TouringMag. "
        f"Write a short 1–2 sentence editor’s note in your voice, "
        f"reacting to this article:\n\n"
        f"Title: {title}\nSummary: {summary}\n\n"
        "Keep it concise and authentic."
        "Never use asterixis or quotaion marks."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        text = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[WARN] Failed to generate editor comment: {e}")
        text = ""

    # ✅ Guarantee a fallback if GPT returns empty
    if not text:
        text = f"This piece was selected by {persona['name']} for its unique perspective on touring."

    return text



# -------------------
# Export
# -------------------

def export_markdown(
    slug, title, summary, body, hero, thumb, collection="blog", extra_fields=None, export_base=None
):
    """Export an article to Markdown (with persona metadata)."""
    if export_base is None:
        export_base = EXPORT_BASE

    # Always use current publish date
    pub_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    # Persona metadata
    persona = get_persona(collection)

    # --- Compose frontmatter ---
    frontmatter = f"""---
title: "{title}"
summary: "{summary}"
pubDate: "{pub_date}"
heroImage: "{hero}"
thumbnail: "{thumb}"
author: "{persona['name']}"
role: "{persona['role']}"
"""
    if extra_fields:
        for key, val in extra_fields.items():
            if isinstance(val, list):
                frontmatter += f"{key}:\n"
                for item in val:
                    frontmatter += f"  - {item}\n"
            else:
                frontmatter += f"{key}: {val}\n"

    frontmatter += "---\n\n" + body

    # --- Write markdown file ---
    out_file = export_base / collection / f"{slug}.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(frontmatter, encoding="utf-8")

    print(f"[OK] Exported to {out_file}")

# -------------------
# Runner
# -------------------

def sanitize_comment(text: str) -> str:
    """
    Make editorComment YAML-safe:
    - collapse newlines
    - replace internal single quotes with doubled '' (YAML safe)
    - wrap whole string in single quotes, italics only
    """
    if not text:
        return "''"
    safe = text.replace("\n", " ").strip()
    safe = safe.replace("'", "''")  # escape single quotes
    return f"'*{safe}*'"

def run_for_mode(mode):
    slug, title, summary, body, hero, thumb, persona = generate_article(mode)

    extra_fields = {}

    if mode == "gear":
        extra_fields["rating"] = random.randint(3, 5)
    elif mode == "guides":
        extra_fields["difficulty"] = random.choice(["Beginner", "Intermediate", "Advanced"])
    elif mode == "upgrades":
        tags_pool = ["comfort", "performance", "storage", "safety", "electronics"]
        extra_fields["tags"] = random.sample(tags_pool, k=random.randint(1, 3))

    # ✅ Generate editor comment (sanitized)
    raw_comment = generate_editor_comment(mode, title, summary, persona)
    extra_fields["editorComment"] = sanitize_comment(raw_comment)

    export_markdown(slug, title, summary, body, hero, thumb,
                    collection=mode, extra_fields=extra_fields)


    export_markdown(slug, title, summary, body, hero, thumb, collection=mode, extra_fields=extra_fields)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["blog", "gear", "upgrades", "guides", "all"], default="all", nargs="?")
    args = parser.parse_args()

    if args.mode == "all":
        for section in ["blog", "gear", "upgrades", "guides"]:
            run_for_mode(section)
    else:
        run_for_mode(args.mode)
