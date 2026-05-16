# agents/critic.py

from backend.services.llm_service import llm_evaluate


def critic_agent(state):
    answer = state["answer"]

    # Avoid additional API calls when generation already failed.
    if isinstance(answer, str) and answer.lower().startswith("openai request failed"):
        return {
            **state,
            "score": 0.0,
            "feedback": "Generation failed due to API rate/quota issue; skipped critic evaluation to reduce extra calls.",
        }

    context = "\n".join(state["context"])

    score, feedback = llm_evaluate(answer, context)

    return {
        **state,
        "score": score,
        "feedback": feedback
    }