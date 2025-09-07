import random
from datetime import datetime, timedelta
from typing import List, Dict


def schedule_posts(items: List[Dict], days: int = 7) -> List[Dict]:
    now = datetime.utcnow()
    scheduled = []
    for item in items:
        delta = timedelta(days=random.randint(0, days), hours=random.randint(0, 23))
        item["publish_at"] = now + delta
        scheduled.append(item)
    return scheduled


if __name__ == "__main__":
    sample = [{"content": "Test"} for _ in range(3)]
    print(schedule_posts(sample))
