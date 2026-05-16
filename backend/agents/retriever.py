# agents/retriever.py

from backend.rag.vector_store import load_vector_store
from backend.rag.retriever_utils import retrieve_documents

def retriever_agent(state):
    query = state["query"]

    vector_store = load_vector_store()
    if vector_store is None:
        return {
            **state,
            "context": [],
            "sources": []
        }

    context, sources = retrieve_documents(query, vector_store)

    return {
        **state,
        "context": context,
        "sources": sources
    }