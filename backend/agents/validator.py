from backend.evaluation.grounding import assess_retrieval_coverage, build_insufficient_context_answer


def context_validator_agent(state):
    query = state["query"]
    retrieved_docs = state.get("context", [])

    validation = assess_retrieval_coverage(query, retrieved_docs)

    if validation["passed"]:
        return {
            **state,
            "validation_passed": True,
            "validation_score": validation["score"],
            "validation_reason": validation["reason"],
        }

    return {
        **state,
        "validation_passed": False,
        "validation_score": validation["score"],
        "validation_reason": validation["reason"],
        "score": validation["score"],
        "answer": build_insufficient_context_answer(query),
    }