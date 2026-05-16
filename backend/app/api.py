from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import sys

# Allow running this file directly (e.g., `python backend/app/api.py`).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.routes import handle_query, ingest_document
from backend.evaluation.metrics import metrics_tracker

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_endpoint(request: QueryRequest):
    result = handle_query(request.query)
    return result


@app.get("/_metrics")
def metrics_endpoint():
    return {
        "average_score": round(metrics_tracker.get_average_score(), 3),
        "average_latency": round(metrics_tracker.get_average_latency(), 3),
        "average_accuracy": round(metrics_tracker.get_average_accuracy(), 3),
        "total": metrics_tracker.get_total_queries(),
    }

@app.get("/")
def root():
    return {"message": "Academic Assistant API is running"}


@app.post("/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    saved_files = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        content = await file.read()
        saved_path = ingest_document(file.filename, content)
        saved_files.append(str(saved_path))

    return {
        "message": "Documents uploaded and indexed successfully.",
        "files": saved_files,
    }