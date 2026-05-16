# context-aware-academic-assistant/graph/router.py

from backend.agents.evaluator import evaluate_query
from backend.graph.workflow import graph

from backend.learning.knowledge_refiner import get_cached_answer
from backend.services.llm_service import llm_generate
from backend.rag.vector_store import load_vector_store

from backend.evaluation.calibration import calibrate_confidence
from backend.evaluation.threshold import should_use_agents

from backend.cache.response_cache import response_cache
from backend.cache.semantic_cache import semantic_cache


def route_query(query: str):
    """
    Main routing logic:
    1. Knowledge base check
    2. Exact cache
    3. Semantic cache
    4. Fast evaluation + calibration
    5. Decide: direct answer OR multi-agent pipeline
    6. Store results in cache
    """

    # -------------------------------
    # STEP 0: Knowledge Base (FASTEST)
    # -------------------------------
    kb_answer = get_cached_answer(query)
    if kb_answer:
        return {
            "answer": kb_answer,
            "score": 1.0,
            "sources": ["knowledge_base"]
            ,"route_source": "knowledge_base"
            ,"retrieval_mode": "knowledge_base"
            ,"validation_passed": True
            ,"validation_score": 1.0
            ,"validation_reason": "Matched a stored knowledge base answer."
        }

    # -------------------------------
    # STEP 1: Exact Cache
    # -------------------------------
    cached_response = response_cache.get(query)
    if cached_response:
        cached_response.setdefault("route_source", "exact_cache")
        cached_response.setdefault("retrieval_mode", "cache")
        cached_response.setdefault("validation_passed", True)
        cached_response.setdefault("validation_score", cached_response.get("score", 0.0))
        cached_response.setdefault("validation_reason", "Returned from exact cache.")
        return cached_response

    # -------------------------------
    # STEP 2: Semantic Cache
    # -------------------------------
    semantic_answer = semantic_cache.get(query)
    if semantic_answer:
        return {
            "answer": semantic_answer,
            "score": 0.9,
            "sources": ["semantic_cache"]
            ,"route_source": "semantic_cache"
            ,"retrieval_mode": "cache"
            ,"validation_passed": True
            ,"validation_score": 0.9
            ,"validation_reason": "Returned from semantic cache."
        }

    vector_store = load_vector_store()

    # -------------------------------
    # STEP 3: Fast Evaluation
    # -------------------------------
    score = evaluate_query(query)

    # Apply confidence calibration
    score = calibrate_confidence(score, query)

    # -------------------------------
    # STEP 4: Routing Decision
    # -------------------------------
    if not should_use_agents(score):
        # Simple query → direct LLM
        answer = llm_generate(query, "")

        result = {
            "answer": answer,
            "score": score,
            "sources": ["direct_llm"],
            "route_source": "direct_llm",
            "retrieval_mode": "none" if vector_store is None else "direct",
            "validation_passed": vector_store is None,
            "validation_score": score,
            "validation_reason": "Answered directly because the query was classified as simple.",
        }

        # Store in cache
        response_cache.set(query, result)
        semantic_cache.add(query, answer)

        return result

    # -------------------------------
    # STEP 5: Multi-Agent Pipeline
    # -------------------------------
    result = graph.invoke({
        "query": query,
        "context": [],
        "answer": "",
        "score": 0.0,
        "feedback": "",
        "sources": [],
        "iterations": 0,
        "validation_passed": False,
        "validation_score": 0.0,
        "validation_reason": "",
        "route_source": "rag_graph",
    })

    # -------------------------------
    # STEP 6: Cache Results
    # -------------------------------
    if result.get("answer"):
        response_cache.set(query, result)
        semantic_cache.add(query, result["answer"])

    result.setdefault("route_source", "rag_graph")
    result.setdefault("retrieval_mode", "rag")
    result.setdefault("validation_passed", False)
    result.setdefault("validation_score", 0.0)
    result.setdefault("validation_reason", "RAG pipeline completed.")

    return result