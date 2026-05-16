# evaluation/metrics.py

import math
from typing import Iterable

from backend.services.embedding_service import embedding_service


def _cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    a_values = list(a)
    b_values = list(b)

    if not a_values or not b_values:
        return 0.0

    dot_product = sum(x * y for x, y in zip(a_values, b_values))
    a_norm = sum(x * x for x in a_values) ** 0.5
    b_norm = sum(y * y for y in b_values) ** 0.5

    if a_norm == 0 or b_norm == 0:
        return 0.0

    return dot_product / (a_norm * b_norm)


class MetricsTracker:
    def __init__(self):
        self.records = []

    def compute_answer_grounding(self, answer: str, retrieved_docs: list[str]) -> float:
        """
        Compute a simple grounding/accuracy score for an answer relative to retrieved documents.

        Approach:
        - Use embedding similarity between the answer and each retrieved document and take the max.
        - Fallback to 0.0 when no retrieved docs are provided.

        Returns a float in [0.0, 1.0].
        """
        if not answer or not retrieved_docs:
            return 0.0

        try:
            answer_vec = embedding_service.embed_query(answer)
            doc_vecs = embedding_service.embed_documents(retrieved_docs)
        except Exception:
            return 0.0

        best_sim = 0.0
        for dv in doc_vecs:
            sim = _cosine_similarity(answer_vec, dv)
            if sim > best_sim:
                best_sim = sim

        # Clamp to [0,1]
        return max(0.0, min(1.0, best_sim))

    def log(self, query: str, score: float, latency: float, answer: str = None, sources: list[str] = None):
        """
        Store each query's performance along with optional grounding accuracy.
        """
        accuracy = None
        if answer is not None and sources:
            # sources may be identifiers or actual document text. If they look like paths/ids,
            # we can't embed them meaningfully here; this best-effort assumes sources contain
            # the retrieved document text. If they are IDs, accuracy will be 0.0.
            accuracy = self.compute_answer_grounding(answer, sources)

        self.records.append({
            "query": query,
            "score": score,
            "latency": latency,
            "accuracy": accuracy,
        })

    def get_average_score(self) -> float:
        if not self.records:
            return 0.0
        return sum(r["score"] for r in self.records) / len(self.records)

    def get_average_latency(self) -> float:
        if not self.records:
            return 0.0
        return sum(r["latency"] for r in self.records) / len(self.records)

    def get_average_accuracy(self) -> float:
        vals = [r["accuracy"] for r in self.records if r.get("accuracy") is not None]
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    def get_total_queries(self) -> int:
        return len(self.records)

    def reset(self):
        self.records = []


# Singleton instance
metrics_tracker = MetricsTracker()