import os
import sys
import datetime
import re
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.db import query

EXPORT_DIR = Path("touringmag-site/src/content/posts")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def slugify(title):
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug

rows = query("SELECT ArticleID, Title, Slug, MetaDescription, Keywords, ContentHtml, PublishedAt FROM Articles ORDER BY PublishedAt DESC").fetchall()

print(f"🧠 Exporting {len(rows)} articles...")

for row in rows:
    slug = row["Slug"]
    title = row["Title"]
    content_html = row["ContentHtml"]
    date_str = row["PublishedAt"]

    date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d")


    md_content = f"""---
title: "{title}"
summary: "{row['MetaDescription'] or ''}"
date: "{date}"
---

{content_html}
"""

    out_file = EXPORT_DIR / f"{slug}.md"
    out_file.write_text(md_content, encoding="utf-8")
    print(f"✅ Exported: {out_file.name}")
