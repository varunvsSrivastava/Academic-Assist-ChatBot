# evaluation/threshold.py

LOW_CONFIDENCE = 0.4
HIGH_CONFIDENCE = 0.7


def classify_query(score: float) -> str:
    """
    Classify query complexity based on score
    """
    if score >= HIGH_CONFIDENCE:
        return "simple"

    if score <= LOW_CONFIDENCE:
        return "complex"

    return "moderate"


def should_use_agents(score: float) -> bool:
    """
    Decide whether to trigger multi-agent pipeline
    """
    return score < HIGH_CONFIDENCE