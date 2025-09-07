import os
import zipfile
from pathlib import Path

# Project root (adjust if script isn’t run from root)
ROOT_DIR = Path(__file__).resolve().parents[0]

# Paths to include in the bundle
INCLUDE_PATHS = [
    "touringmag-site/src",
    "touringmag-site/.github",
    "scripts/run_goldloop.py",
    "modules/",
    "data/affiliate_links.csv",
    "logs/affiliate_log.txt",
]

OUTPUT_ZIP = ROOT_DIR / "review_bundle.zip"

def zip_files():
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in INCLUDE_PATHS:
            full_path = ROOT_DIR / path
            if full_path.is_file():
                zipf.write(full_path, arcname=path)
            elif full_path.is_dir():
                for root, _, files in os.walk(full_path):
                    for f in files:
                        file_path = Path(root) / f
                        rel_path = file_path.relative_to(ROOT_DIR)
                        zipf.write(file_path, arcname=rel_path)
    print(f"✅ Review bundle created: {OUTPUT_ZIP}")

if __name__ == "__main__":
    zip_files()
