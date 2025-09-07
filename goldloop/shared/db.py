import os
import sqlite3
from pathlib import Path

# Absolute path to the SQLite DB
base_dir = Path(__file__).resolve().parent.parent  # points to /goldloop
db_path = os.getenv("SQLITE_DB_PATH", str(base_dir / "data" / "goldloop.db"))
print("Using SQLite DB at:", db_path)

_conn = sqlite3.connect(db_path, check_same_thread=False)
_conn.row_factory = sqlite3.Row

def query(sql, *args):
    cur = _conn.cursor()
    cur.execute(sql, args)
    return cur

def commit():
    _conn.commit()
