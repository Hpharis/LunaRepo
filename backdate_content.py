import os
import random
from datetime import datetime, timedelta

# Root content folder
CONTENT_ROOT = "touringmag-site/src/content"

def random_pub_date():
    """Return an ISO date within the last 90 days"""
    days_back = random.randint(0, 90)
    return (datetime.now() - timedelta(days=days_back)).replace(microsecond=0).isoformat()

def adjust_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    updated = False
    for line in lines:
        if line.startswith("pubDate:"):
            new_date = random_pub_date()
            new_lines.append(f'pubDate: "{new_date}"\n')
            updated = True
        else:
            new_lines.append(line)

    if updated:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Updated {path}")
    else:
        print(f"⚠️ No pubDate found in {path}")

def walk_and_update():
    for root, _, files in os.walk(CONTENT_ROOT):
        for file in files:
            if file.endswith(".md"):
                adjust_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_update()
