from __future__ import annotations
import re
import httpx
from typing import Any, Dict, List
from .base import ToolBase

_DDG = "https://duckduckgo.com/html/?q={q}&kl=wt-wt"
_LINK_RE = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.I)

def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)

class WebSearch(ToolBase):
    name = "websearch"
    description = "Search the web via DuckDuckGo HTML (no API key). Returns top links."
    schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "k": {"type": "integer"},
            "allow_network": {"type": "boolean"}
        },
        "required": ["query"],
        "additionalProperties": True
    }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        if not kwargs.get("allow_network", True):
            return {"ok": False, "error": "Network disabled by policy."}
        query = kwargs.get("query")
        if not query:
            raise ValueError("Missing 'query'")
        k = int(kwargs.get("k", 5))

        headers = {"User-Agent": "Mozilla/5.0 (Agentik)"}
        url = _DDG.format(q=httpx.QueryParams({"q": query})["q"])
        r = httpx.get(url, headers=headers, timeout=20.0)
        r.raise_for_status()
        html = r.text
        results: List[Dict[str, str]] = []
        for href, title_html in _LINK_RE.findall(html):
            results.append({"title": _strip_tags(title_html).strip(), "url": href})
            if len(results) >= k:
                break
        return {"ok": True, "query": query, "results": results}
