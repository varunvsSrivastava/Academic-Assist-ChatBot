from langchain_community.vectorstores import FAISS
from backend.rag.embeddings import get_embeddings
from pathlib import Path

def load_vector_store():
    index_file = Path("data/index/index.faiss")
    if not index_file.exists():
        return None

    embeddings = get_embeddings()
    return FAISS.load_local("data/index", embeddings, allow_dangerous_deserialization=True)