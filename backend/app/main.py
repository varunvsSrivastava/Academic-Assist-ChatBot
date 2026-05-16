"""
Replacement `app/main.py` — Streamlit UI has been preserved in
`app/streamlit_app.py` (legacy). The preferred frontend is now the
React app in `frontend/` which talks to the FastAPI backend at `/query`.

To run the backend:

    uvicorn app.api:app --reload --port 8000

To run the frontend (from `frontend/`):

    npm install
    npm start

"""