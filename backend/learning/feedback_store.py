# learning/feedback_store.py

import json
import os
from datetime import datetime

FEEDBACK_FILE = "data/feedback.json"


def _ensure_file():
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([], f)


def load_feedback():
    _ensure_file()
    with open(FEEDBACK_FILE, "r") as f:
        return json.load(f)


def save_feedback(data):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)


def store_feedback(query, answer, feedback, score):
    """
    Store bad responses for future learning
    """
    data = load_feedback()

    entry = {
        "query": query,
        "answer": answer,
        "feedback": feedback,
        "score": score,
        "timestamp": str(datetime.now())
    }

    data.append(entry)
    save_feedback(data)