# scripts/run_timer_once.py
import sys
import os

# Add project root (C:\goldloop\goldloop) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_app.article_timer import main

class FakeTimer:
    past_due = False

try:
    main(FakeTimer())
except Exception as e:
    import traceback
    traceback.print_exc()

