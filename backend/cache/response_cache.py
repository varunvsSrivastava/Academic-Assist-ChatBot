# context-aware-academic-assistant/cache/response_cache.py

class ResponseCache:
    def __init__(self):
        self.cache = {}

    def get(self, query: str):
        return self.cache.get(query)

    def set(self, query: str, response: dict):
        self.cache[query] = response

    def clear(self):
        self.cache = {}


# Singleton
response_cache = ResponseCache()