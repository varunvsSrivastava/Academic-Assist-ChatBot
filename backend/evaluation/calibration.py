# evaluation/calibration.py

def calibrate_confidence(score: float, query: str) -> float:
    """
    Adjust confidence score using simple heuristics.

    Why?
    Raw LLM scores are not always reliable.
    This improves decision-making for routing and evaluation.
    """

    if score is None:
        return 0.5

    # Query length factor
    query_length = len(query.split())

    # Short queries → usually easier → slightly boost
    if query_length < 5:
        score += 0.05

    # Long queries → more complex → reduce confidence slightly
    elif query_length > 15:
        score -= 0.05

    # Clamp between 0 and 1
    score = max(0.0, min(score, 1.0))

    return score