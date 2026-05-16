from typing import TypedDict, List

class GraphState(TypedDict):
    query: str
    context: List[str]
    answer: str
    score: float
    feedback: str
    sources: List[str]
    iterations: int
    validation_passed: bool
    validation_score: float
    validation_reason: str