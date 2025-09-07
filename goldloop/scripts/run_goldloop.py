import os
import sys
import sqlite3
import subprocess
import random
import requests
from pathlib import Path
from dotenv import load_dotenv
import openai
import argparse
from datetime import datetime, timezone
from PIL import Image
import io
import shutil
import yaml
from fpdf import FPDF
from bs4 import BeautifulSoup
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pathlib import Path
import sys



# Repo root (for touringmag-site paths)
REPO_ROOT = GOLDLOOP_ROOT.parent

# Always resolve to the goldloop/ folder (where modules/ lives)
GOLDLOOP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOLDLOOP_ROOT))

from modules.affiliate_injector import load_affiliate_links, inject_links

# Load env vars
load_dotenv()

#  Paths
# Project root = repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Goldloop root = where scripts/modules live
GOLDLOOP_ROOT = REPO_ROOT / "goldloop"

# Make goldloop root importable
sys.path.insert(0, str(GOLDLOOP_ROOT))

# Paths
DB_FILE      = GOLDLOOP_ROOT / "data" / "goldloop.db"
EXPORT_BASE  = REPO_ROOT / "touringmag-site" / "src" / "content"
ASSETS_DIR   = REPO_ROOT / "touringmag-site" / "public" / "assets"
LOG_FILE     = GOLDLOOP_ROOT / "logs" / "affiliate_log.txt"


# API keys
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

def build_prompt(mode: str) -> str:
    """Return a section-specific content prompt."""
    if mode == "gear":
        return """
        You are a product reviewer for TouringMag (motorcycle touring gear).
        IMPORTANT: Do not include colons (:) in titles except after "title:" itself. Keep YAML keys and values plain.
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
        return """
        You are writing an upgrade guide for TouringMag (motorcycle touring upgrades).
        IMPORTANT: Do not include colons (:) in titles except after "title:" itself. Keep YAML keys and values plain.
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
        return """
        You are writing a detailed how-to guide for TouringMag (motorcycle touring).
        IMPORTANT: Do not include colons (:) in titles except after "title:" itself. Keep YAML keys and values plain.
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
        return """
        You are a lifestyle writer for TouringMag (motorcycle touring).
        IMPORTANT: Do not include colons (:) in titles except after "title:" itself. Keep YAML keys and values plain.
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


def generate_article(mode="blog"):
    """Generate a full article with metadata, images, and DB insert."""
    init_db()
    prompt = build_prompt(mode)

    # Force guide structure when mode=guides
    if mode == "guides":
        prompt += """
        IMPORTANT: This is a detailed how-to guide. 
        You must include:
        - <h2>Tools & Materials</h2> with <ul>
        - <h2>Step-by-Step Instructions</h2> with <ol>
        - <h2>Safety Notes</h2> with <p>
        - <h2>Difficulty</h2> with Beginner / Intermediate / Advanced
        """

    print(f"[INFO] Requesting {mode} article from OpenAI...")
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response["choices"][0]["message"]["content"]

    # Strip code fences if present
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

    # 🛡 Guide fallback: inject steps if missing
    if mode == "guides" and "<ol>" not in body:
        print("[WARN] Guide missing step list — injecting fallback outline.")
        fallback_steps = """
        <h2>Step-by-Step Instructions</h2>
        <ol>
          <li>Prepare your motorcycle and gather tools.</li>
          <li>Follow the procedure carefully step by step.</li>
          <li>Test and verify before riding.</li>
        </ol>
        <h2>Difficulty</h2>
        <p>Beginner</p>
        """
        body += fallback_steps

    hero, thumb = generate_images(title, slug)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR IGNORE INTO posts (title, slug, summary, content, heroImage)
    VALUES (?, ?, ?, ?, ?)
    """, (title, slug, summary, body, hero))
    conn.commit()
    conn.close()

    print(f"[OK] Article stored: {title} ({slug})")
    return slug, title, summary, body, hero, thumb


def run_for_mode(mode):
    slug, title, summary, body, hero, thumb = generate_article(mode)
    extra_fields = {}

    if mode == "gear":
        extra_fields["rating"] = random.randint(3, 5)
    elif mode == "guides":
        extra_fields["difficulty"] = random.choice(["Beginner", "Intermediate", "Advanced"])
    elif mode == "upgrades":
        tags_pool = ["comfort", "performance", "storage", "safety", "electronics"]
        extra_fields["tags"] = random.sample(tags_pool, k=random.randint(1, 3))

    export_markdown(slug, title, summary, body, hero, thumb, collection=mode, extra_fields=extra_fields)


def log_affiliate_injection(slug, injected_details):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now(timezone.utc).isoformat()}] {slug}\n")
        if injected_details:
            for keyword, url, count in injected_details:
                f.write(f"  - {keyword} → {url} (injected {count} times)\n")
        else:
            f.write("  - No affiliate links injected.\n")


def export_markdown(slug, title, summary, body, hero, thumb, collection="blog", extra_fields=None):
    pub_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    link_map = load_affiliate_links()
    injected_details = []
    for keyword, url in link_map:
        updated_body, count = inject_links(body, [(keyword, url)])
        if count > 0:
            body = updated_body
            injected_details.append((keyword, url, count))

    log_affiliate_injection(slug, injected_details)

    frontmatter = f"""---
title: "{title}"
summary: "{summary}"
pubDate: "{pub_date}"
heroImage: "{hero}"
thumbnail: "{thumb}"
"""
    if extra_fields:
        for key, val in extra_fields.items():
            if isinstance(val, list):
                frontmatter += f"{key}:\n"
                for item in val:
                    frontmatter += f"  - {item}\n"
            else:
                frontmatter += f"{key}: {val}\n"

    if "affiliateLink" not in (extra_fields or {}) and injected_details:
        frontmatter += f"affiliateLink: {injected_details[0][1]}\n"

    frontmatter += "---\n\n" + body

    out_file = EXPORT_BASE / collection / f"{slug}.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(frontmatter, encoding="utf-8")
    
     # -------------------
    # Extra: generate checklist PDF for guides
    # -------------------
    if collection == "guides":
        try:
            soup = BeautifulSoup(body, "html.parser")
            steps = [li.get_text(strip=True) for li in soup.find_all("li")]
            if steps:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "TouringMag Checklist", ln=True, align="C")
                pdf.ln(10)

                pdf.set_font("Arial", size=12)
                for i, step in enumerate(steps, start=1):
                    pdf.cell(0, 10, f"[ ] {i}. {step}", ln=True)

                checklist_path = out_file.parent / f"{slug}-checklist.pdf"
                pdf.output(str(checklist_path))
                print(f"[OK] Checklist PDF generated: {checklist_path}")
            else:
                print("[WARN] No <li> steps found — checklist not generated.")
        except Exception as e:
            print(f"[ERROR] Failed to generate checklist PDF: {e}")

    print(f"[OK] Exported to {out_file}")


def git_push():
    repo_path = ROOT_DIR / "touringmag-site"
    if not (repo_path / ".git").exists():
        print(f"[INFO] Skipping git push: {repo_path} is not a git repo.")
        return
    try:
        subprocess.run(["git", "add", "src/content"], cwd=repo_path, check=True)
        subprocess.run(["git", "add", "public/assets"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "New AI article"], cwd=repo_path, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, check=True)
        print("[OK] Blog content pushed directly to main.")
    except subprocess.CalledProcessError as e:
        print("[INFO] Git push skipped (maybe no new content):", e)


# -------------------
# Entry point
# -------------------
def run_for_mode(mode):
    slug, title, summary, body, hero, thumb = generate_article(mode)
    extra_fields = {}

    # Gear: product rating
    if mode == "gear":
        extra_fields["rating"] = random.randint(3, 5)

    # Guides: difficulty + step fallback
    elif mode == "guides":
        extra_fields["difficulty"] = random.choice(["Beginner", "Intermediate", "Advanced"])

        # Ensure step-by-step instructions exist
        if "<ol>" not in body:
            print("[WARN] Guide missing step list — injecting fallback outline.")
            fallback_steps = """
            <h2>Step-by-Step Instructions</h2>
            <ol>
              <li>Prepare your motorcycle and gather tools.</li>
              <li>Follow the procedure carefully (adjust based on skill).</li>
              <li>Test and verify everything before riding.</li>
            </ol>
            """
            body += fallback_steps

    # Upgrades: tags
    elif mode == "upgrades":
        tags_pool = ["comfort", "performance", "storage", "safety", "electronics"]
        extra_fields["tags"] = random.sample(tags_pool, k=random.randint(1, 3))

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

    # git_push()  <-- REMOVE THIS LINE