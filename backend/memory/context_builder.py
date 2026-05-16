# context-aware-academic-assistant/memory/context_builder.py

from backend.memory.session_memory import session_memory


def build_context(query: str, retrieved_docs: list[str]) -> str:
    """
    Build final context for LLM using:
    - Conversation history
    - Retrieved documents
    """

    # -------------------------------
    # 1. Get chat history
    # -------------------------------
    history = session_memory.get_formatted_history()

    # -------------------------------
    # 2. Combine retrieved docs
    # -------------------------------
    docs_text = "\n\n".join(retrieved_docs)

    # -------------------------------
    # 3. Build final context
    # -------------------------------
    context = ""

    if history:
        context += "Conversation History:\n"
        context += history
        context += "\n\n"

    context += "Relevant Documents:\n"
    context += docs_text

    return context