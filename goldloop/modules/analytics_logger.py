import json
from datetime import datetime
from typing import Dict
from pathlib import Path

LOG_FILE = Path("logs/events.json")


def log_event(event: Dict) -> None:
    event["timestamp"] = datetime.utcnow().isoformat()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        data = json.loads(LOG_FILE.read_text())
    else:
        data = []
    data.append(event)
    LOG_FILE.write_text(json.dumps(data, indent=2))


def weekly_summary() -> Dict:
    if not LOG_FILE.exists():
        return {}
    data = json.loads(LOG_FILE.read_text())
    last_week = [e for e in data if (datetime.utcnow() - datetime.fromisoformat(e["timestamp"])) .days < 7]
    return {
        "events": len(last_week),
    }


if __name__ == "__main__":
    log_event({"type": "click", "label": "test"})
    print(weekly_summary())
