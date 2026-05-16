import re
from typing import Iterable

from backend.app.config import config
from backend.services.embedding_service import embedding_service


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "was", "what", "when", "where", "which", "who", "why", "with",
}


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if token not in _STOPWORDS and len(token) > 2}


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


def assess_retrieval_coverage(query: str, retrieved_docs: list[str]) -> dict:
    if not retrieved_docs:
        return {
            "passed": False,
            "score": 0.0,
            "reason": "No supporting documents were retrieved.",
        }

    query_tokens = _tokenize(query)
    best_semantic_score = 0.0
    best_keyword_hits = 0

    query_vector = embedding_service.embed_query(query)

    for doc in retrieved_docs:
        doc_tokens = _tokenize(doc)
        if query_tokens:
            best_keyword_hits = max(best_keyword_hits, len(query_tokens & doc_tokens))

        doc_vector = embedding_service.embed_query(doc)
        semantic_score = _cosine_similarity(query_vector, doc_vector)
        best_semantic_score = max(best_semantic_score, semantic_score)

    keyword_score = 0.0
    if query_tokens:
        keyword_score = min(best_keyword_hits / max(len(query_tokens), 1), 1.0)

    combined_score = round((0.7 * best_semantic_score) + (0.3 * keyword_score), 3)
    passed = combined_score >= config.RETRIEVAL_SCORE_THRESHOLD or best_keyword_hits >= 2

    if passed:
        reason = "Retrieved documents are relevant enough to ground the answer."
    else:
        reason = "Retrieved documents do not provide enough grounding for a confident answer."

    return {
        "passed": passed,
        "score": combined_score,
        "reason": reason,
    }


def build_insufficient_context_answer(query: str) -> str:
    return (
        "Insufficient information in the uploaded or indexed documents to answer confidently. "
        "Please upload more relevant PDFs or ask a narrower question.\n\n"
        f"Question: {query}"
    )