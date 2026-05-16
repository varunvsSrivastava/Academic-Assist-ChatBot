# context-aware-academic-assistant/services/embedding_service.py

import hashlib

from langchain_openai import OpenAIEmbeddings
from backend.app.config import config

from backend.cache.embedding_cache import embedding_cache


class EmbeddingService:
    def __init__(self):
        """
        Initialize embedding model
        """
        self.model = None
        if config.OPENAI_API_KEY:
            self.model = OpenAIEmbeddings(
                openai_api_key=config.OPENAI_API_KEY
            )

    def _fallback_vector(self, text: str, dim: int = 32):
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = list(digest)
        vector = []
        for i in range(dim):
            vector.append(values[i % len(values)] / 255.0)
        return vector

    def embed_query(self, text: str):
        """
        Convert query into embedding vector (with caching)
        """
        # -------------------------------
        # Check cache first
        # -------------------------------
        cached = embedding_cache.get(text)
        if cached:
            return cached

        # -------------------------------
        # Generate embedding
        # -------------------------------
        if self.model is None:
            vector = self._fallback_vector(text)
        else:
            try:
                vector = self.model.embed_query(text)
            except Exception:
                vector = self._fallback_vector(text)

        # -------------------------------
        # Store in cache
        # -------------------------------
        embedding_cache.set(text, vector)

        return vector

    def embed_documents(self, texts: list[str]):
        """
        Convert multiple documents into embeddings (with caching)
        """
        embeddings = []

        for text in texts:
            cached = embedding_cache.get(text)

            if cached:
                embeddings.append(cached)
            else:
                if self.model is None:
                    vector = self._fallback_vector(text)
                else:
                    try:
                        vector = self.model.embed_query(text)
                    except Exception:
                        vector = self._fallback_vector(text)
                embedding_cache.set(text, vector)
                embeddings.append(vector)

        return embeddings


# Singleton instance (recommended)
embedding_service = EmbeddingService()