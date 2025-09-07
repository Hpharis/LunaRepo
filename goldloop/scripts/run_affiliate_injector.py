# scripts/run_affiliate_injector.py

import os
import sys
import csv
from dotenv import load_dotenv

# Add project root to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.affiliate_injector import run_affiliate_injection

# Load .env
load_dotenv()

def main():
    print("🚀 Running affiliate injector...")
    try:
        run_affiliate_injection()
        print("✅ Done running injector.")
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    main()
