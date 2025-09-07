# scripts/reset_affiliate_flag.py

import os
import sys

# Make root path importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.db import query, commit

# Reset AffiliateReady flag on the first article (or adjust ID)
query("UPDATE Articles SET AffiliateReady = 0 WHERE ArticleID = 1")
commit()

print("✅ Reset AffiliateReady on ArticleID 1")
