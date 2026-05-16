# learning/learning_engine.py

from backend.learning.feedback_store import store_feedback
from backend.learning.knowledge_refiner import update_knowledge
from backend.learning.prompt_optimizer import update_prompt

LOW_THRESHOLD = 0.6
HIGH_THRESHOLD = 0.85


def learning_step(state):
    """
    Core learning logic
    """
    query = state["query"]
    answer = state["answer"]
    score = state["score"]
    feedback = state["feedback"]

    # 🔴 Case 1: Bad answer → learn from mistakes
    if score < LOW_THRESHOLD:
        store_feedback(query, answer, feedback, score)

        # Improve prompt
        update_prompt(feedback)

    # 🟢 Case 2: Good answer → store knowledge
    elif score > HIGH_THRESHOLD:
        update_knowledge(query, answer)

    # 🟡 Medium → ignore (optional tuning zone)

    return state