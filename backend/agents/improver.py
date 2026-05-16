# agents/improver.py

from backend.services.llm_service import llm_improve

def improver_agent(state):
    answer = state["answer"]
    feedback = state["feedback"]
    iterations = state.get("iterations", 0)

    improved = llm_improve(answer, feedback)

    return {**state, "answer": improved, "iterations": iterations + 1}