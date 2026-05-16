# context-aware-academic-assistant/cache/semantic_cache.py

from backend.services.embedding_service import embedding_service
import numpy as np

class SemanticCache:
    def __init__(self, threshold=0.85):
        self.cache = []  # list of (embedding, query, answer)
        self.threshold = threshold

    def cosine_similarity(self, a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def get(self, query: str):
        query_vec = embedding_service.embed_query(query)

        for emb, cached_query, answer in self.cache:
            sim = self.cosine_similarity(query_vec, emb)

            if sim >= self.threshold:
                return answer

        return None

    def add(self, query: str, answer: str):
        emb = embedding_service.embed_query(query)
        self.cache.append((emb, query, answer))


# Singleton
semantic_cache = SemanticCache()