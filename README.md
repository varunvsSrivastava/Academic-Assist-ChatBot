# Context-Aware Academic Assistant

Multi-agent academic assistant with RAG, retrieval validation, upload-based indexing, and feedback-driven learning.

## Layout

- `backend/` - Python backend runner and API entrypoint helpers
- `frontend/` - React dashboard and chat UI
- `docs/` - Project documentation copies and reference material

## What it does

- Accepts academic questions through a React frontend (recommended) or FastAPI
- Lets users upload PDF documents and rebuild the FAISS knowledge index
- Retrieves supporting context before generation
- Uses a validation gate to decide whether the retrieved context is strong enough to answer
- Runs a multi-agent loop: retriever -> validator -> generator -> critic -> improver -> learning

## Main entry points

- Frontend (React): see `frontend/README.md` for setup. The legacy Streamlit UI is preserved at `backend/app/streamlit_app.py` but is no longer the primary UI.
- Backend runner: `python backend/run.py`

## Document workflow

1. Upload PDFs through `POST /documents/upload`.
2. The files are stored in `data/raw/`.
3. The FAISS index is rebuilt in `data/index/`.
4. Queries now use the indexed documents as retrieval context.

## Notes

- The app requires `OPENAI_API_KEY` for live generation and embeddings.
- If the index is empty, the assistant falls back to direct LLM answering for simple questions.
