from __future__ import annotations
from typing import List, Dict, Any

class DictMemory:
    def __init__(self) -> None:
        self._store: List[Dict[str, Any]] = []

    def remember(self, event: Dict[str, Any]) -> None:
        self._store.append(event)

    def recall(self, n: int = 10) -> List[Dict[str, Any]]:
        return self._store[-n:]

    def clear(self) -> None:
        self._store.clear()

    def summarize(self, n: int = 20, max_chars: int = 1200) -> str:
        items = self.recall(n)
        out = []
        for i, e in enumerate(items, 1):
            role = e.get("role", e.get("name", "event"))
            content = e.get("content") or e.get("text") or str(e)
            out.append(f"{i}. {role}: {content}")
        s = "\n".join(out)
        return s[:max_chars]
