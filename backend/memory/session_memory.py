class SessionMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history = []

    def add_interaction(self, query: str, answer: str) -> None:
        self.history.append({"query": query, "answer": answer})
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns :]

    def get_formatted_history(self) -> str:
        lines = []
        for item in self.history:
            lines.append(f"User: {item['query']}")
            lines.append(f"Assistant: {item['answer']}")
        return "\n".join(lines)

    def clear(self) -> None:
        self.history = []


session_memory = SessionMemory()