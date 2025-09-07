from flask import Flask, render_template, jsonify
import json
from pathlib import Path

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logs")
def logs():
    events_file = Path("logs/events.json")
    if events_file.exists():
        data = json.loads(events_file.read_text())
    else:
        data = []
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
