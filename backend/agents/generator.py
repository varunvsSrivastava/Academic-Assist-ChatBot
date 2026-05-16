from backend.memory.context_builder import build_context
from backend.services.llm_service import llm_generate

def generator_agent(state):
    query = state["query"]
    retrieved_docs = state["context"]

    full_context = build_context(query, retrieved_docs)

    answer = llm_generate(query, full_context)

    return {**state, "answer": answer}