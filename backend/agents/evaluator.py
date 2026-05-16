# agents/evaluator.py

import re

from backend.app.config import config
from backend.services.llm_service import llm_quick_score


_COMPLEXITY_HINTS = {
    "compare", "derive", "prove", "analyze", "analysis", "evaluate",
    "critical", "framework", "methodology", "algorithm", "implement",
    "literature", "citation", "hypothesis", "experiment", "dataset",
    "equation", "theorem", "tradeoff", "limitations", "pipeline",
}


def _heuristic_query_score(query: str) -> float:
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    token_count = len(tokens)

    if token_count == 0:
        return 0.5

    score = 0.45

    if token_count <= 5:
        score += 0.25
    elif token_count >= 18:
        score -= 0.15

    hint_hits = sum(1 for token in tokens if token in _COMPLEXITY_HINTS)
    score -= min(hint_hits * 0.08, 0.24)

    if "?" in query:
        score += 0.05

    return max(0.0, min(score, 1.0))


def evaluate_query(query):
    # Default: local heuristic to avoid an extra LLM call per request.
    if not config.USE_LLM_QUERY_SCORER:
        return _heuristic_query_score(query)

    return llm_quick_score(query)