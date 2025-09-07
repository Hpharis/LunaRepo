# scripts/init_db.py
import sqlite3
from pathlib import Path

DB_FILE = Path("data/goldloop.db")
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS Articles (
    ArticleID INTEGER PRIMARY KEY AUTOINCREMENT,
    Lang TEXT DEFAULT 'en',
    Title TEXT NOT NULL,
    Slug TEXT UNIQUE,
    MetaDescription TEXT,
    Keywords TEXT,
    ContentHtml TEXT NOT NULL,
    ImageUrl TEXT,
    PublishedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastUpdated DATETIME,
    AffiliateReady INTEGER DEFAULT 0,
    Programmatic INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS GenerationLog (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    Pipeline TEXT,
    Topic TEXT,
    ArticleID INTEGER,
    Success INTEGER,
    Error TEXT,
    RunAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
print(f"✅ Initialized SQLite DB at {DB_FILE}")
