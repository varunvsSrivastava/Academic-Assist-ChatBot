import time

from backend.memory.session_memory import session_memory
from backend.graph.router import route_query
from backend.rag.ingest import ingest_uploaded_file
from backend.evaluation.metrics import metrics_tracker


def ingest_document(filename: str, content: bytes):
    return ingest_uploaded_file(filename, content)

def handle_query(query: str):
    start_time = time.time()
    result = route_query(query)
    end_time = time.time()

    latency = round(end_time - start_time, 3)

    # Save conversation
    session_memory.add_interaction(query, result.get("answer", ""))

    # Log metrics centrally (includes optional grounding accuracy)
    metrics_tracker.log(
        query,
        result.get("score", 0.0),
        latency,
        answer=result.get("answer"),
        sources=result.get("sources", []),
    )

    return result