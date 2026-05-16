# rag/ingest.py

import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

from backend.rag.chunking import chunking_service
from backend.services.embedding_service import embedding_service


DATA_PATH = Path("data/raw")
INDEX_PATH = Path("data/index")


def _ensure_directories(data_path: Path = DATA_PATH, index_path: Path = INDEX_PATH):
    data_path.mkdir(parents=True, exist_ok=True)
    index_path.mkdir(parents=True, exist_ok=True)


def load_pdfs(data_path=DATA_PATH):
    """
    Load all PDFs from data/raw folder
    """
    documents = []

    _ensure_directories(data_path, INDEX_PATH)

    for file in os.listdir(data_path):
        if file.endswith(".pdf"):
            file_path = os.path.join(data_path, file)

            loader = PyPDFLoader(file_path)
            docs = loader.load()

            # Add metadata (source tracking)
            for doc in docs:
                doc.metadata["source"] = file

            documents.extend(docs)

    return documents


def process_documents(documents):
    """
    Chunk documents
    """
    return chunking_service.split_documents(documents)


def create_vector_store(chunks):
    """
    Create FAISS index
    """
    embeddings = embedding_service.model

    vector_store = FAISS.from_documents(chunks, embeddings)

    return vector_store


def save_vector_store(vector_store, index_path=INDEX_PATH):
    """
    Save FAISS index locally
    """
    vector_store.save_local(str(index_path))


def save_uploaded_pdf(filename: str, content: bytes, data_path: Path = DATA_PATH) -> Path:
    """
    Persist an uploaded PDF into the raw documents folder.
    """
    _ensure_directories(data_path, INDEX_PATH)

    filename = Path(filename).name
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    destination = data_path / filename
    with open(destination, "wb") as target:
        target.write(content)

    return destination


def run_ingestion(data_path: Path = DATA_PATH, index_path: Path = INDEX_PATH):
    """
    Full pipeline:
    PDF → Chunk → Embed → FAISS → Save
    """
    _ensure_directories(data_path, index_path)

    print(" Loading PDFs...")
    documents = load_pdfs(data_path)

    print(f" Loaded {len(documents)} documents")

    print(" Chunking...")
    chunks = process_documents(documents)

    print(f" Created {len(chunks)} chunks")

    print(" Creating embeddings + FAISS index...")
    vector_store = create_vector_store(chunks)

    print(" Saving index...")
    save_vector_store(vector_store, index_path)

    print(" Ingestion complete!")


def ingest_uploaded_file(filename: str, content: bytes, data_path: Path = DATA_PATH, index_path: Path = INDEX_PATH):
    """
    Save one uploaded PDF and rebuild the vector index from all raw PDFs.
    """
    saved_path = save_uploaded_pdf(filename, content, data_path)
    run_ingestion(data_path=data_path, index_path=index_path)
    return saved_path


if __name__ == "__main__":
    run_ingestion()