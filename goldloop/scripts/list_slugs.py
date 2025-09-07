import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.db import query

rows = query("SELECT ArticleID, Title, Slug, AffiliateReady FROM Articles ORDER BY PublishedAt DESC").fetchall()

for row in rows:
    print(f"📝 ID {row['ArticleID']} – /articles/{row['Slug']} – AffiliateReady: {row['AffiliateReady']}")
