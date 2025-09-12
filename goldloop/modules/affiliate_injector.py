import csv
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MAX_LINKS_PER_KEYWORD = 2
AFFILIATE_FILE = Path(__file__).resolve().parents[1] / "data" / "affiliate_links.csv"

def load_affiliate_links(csv_path=AFFILIATE_FILE):
    """Load affiliate keyword→URL mappings from CSV."""
    link_map = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required_headers = {"Keyword", "URL"}
        if not required_headers.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV must contain 'Keyword' and 'URL' headers.")
        for row in reader:
            keyword, url = row["Keyword"].strip(), row["URL"].strip()
            if keyword and url:
                link_map.append((keyword, url))
    return link_map

def inject_links(html: str, link_map):
    """Inject affiliate links into given HTML/Markdown string."""
    total_injected = 0
    for keyword, url in link_map:
        # Skip inside existing <a> tags
        pattern = re.compile(
            rf'(?<!["\'>])\b({re.escape(keyword)})\b(?![^<]*</a>)',
            re.IGNORECASE
        )
        html, count = pattern.subn(
            rf'<a href="{url}" target="_blank" rel="noopener noreferrer">\1</a>',
            html,
            count=MAX_LINKS_PER_KEYWORD
        )
        total_injected += count
    return html, total_injected

def run_affiliate_injection():
    """Placeholder: originally injected into DB.
    For now, just print a message and return.
    """
    print("[INFO] run_affiliate_injection() is not wired to a DB in this version.")
    print("       Use inject_links(html, link_map) directly in your pipeline.")
