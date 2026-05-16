# context-aware-academic-assistant/cache/embedding_cache.py

class EmbeddingCache:
    def __init__(self):
        self.cache = {}

    def get(self, text: str):
        return self.cache.get(text)

    def set(self, text: str, embedding):
        self.cache[text] = embedding


# Singleton
embedding_cache = EmbeddingCache()