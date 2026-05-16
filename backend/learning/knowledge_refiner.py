# learning/knowledge_refiner.py

import json
import os

KB_FILE = "data/knowledge_base.json"


def _ensure_file():
    if not os.path.exists(KB_FILE):
        with open(KB_FILE, "w") as f:
            json.dump({}, f)


def load_kb():
    _ensure_file()
    with open(KB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_kb(kb):
    with open(KB_FILE, "w") as f:
        json.dump(kb, f, indent=2)


def update_knowledge(query, answer):
    """
    Save high-quality answers
    """
    kb = load_kb()
    kb[query] = {
        "answer": answer
    }
    save_kb(kb)


def get_cached_answer(query):
    """
    Retrieve stored answer if exists
    """
    kb = load_kb()
    entry = kb.get(query)

    if entry:
        return entry["answer"]

    return None