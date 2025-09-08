import csv
import re
from pathlib import Path
from dotenv import load_dotenv
from goldloop.shared.db import query, commit

load_dotenv()

MAX_LINKS_PER_KEYWORD = 2
AFFILIATE_FILE = Path(__file__).resolve().parents[1] / "data" / "affiliate_links.csv"

def load_affiliate_links(csv_path=AFFILIATE_FILE):
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
    """Process DB articles not affiliate-ready yet."""
    link_map = load_affiliate_links()
    rows = query("SELECT ArticleID, ContentHtml FROM Articles WHERE AffiliateReady = 0").fetchall()
    print(f"🔎 Found {len(rows)} articles needing injection.")

    for row in rows:
        article_id, html = row["ArticleID"], row["ContentHtml"]
        updated_html, injected_count = inject_links(html, link_map)
        if injected_count > 0:
            query("UPDATE Articles SET ContentHtml = ?, AffiliateReady = 1 WHERE ArticleID = ?",
                  updated_html, article_id)
            print(f"✅ ArticleID {article_id}: injected {injected_count} links")
        else:
            print(f"⚠️ ArticleID {article_id}: no matches")
    commit()
    print("🎉 Affiliate injection completed.")