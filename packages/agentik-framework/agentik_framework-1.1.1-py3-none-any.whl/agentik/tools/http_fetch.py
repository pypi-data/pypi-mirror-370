from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from ..config import rc_cache_path


class HttpFetchTool:
    """
    Simple HTTP GET fetcher with caching.
    Honors policy: allow_network (bool).
    """

    name = "http_fetch"
    description = "Fetch a URL over HTTP(S) with TTL-based disk caching and size/time limits."
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Absolute HTTP(S) URL to GET"},
            "ttl": {"type": "integer", "minimum": 0, "default": 86400, "description": "Cache TTL seconds (0=disable cache)"},
            "timeout": {"type": "number", "minimum": 1, "default": 20.0, "description": "Request timeout seconds"},
            "max_bytes": {"type": "integer", "minimum": 1024, "default": 1000000, "description": "Max response bytes to keep"},
            "headers": {"type": "object", "additionalProperties": {"type": "string"}, "description": "Optional request headers"},
            "allow_network": {"type": "boolean", "default": False},
        },
        "required": ["url"]
    }

    def __init__(self) -> None:
        self.cache_dir = rc_cache_path("http")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -------- utils --------

    def _cache_file(self, url: str, headers: Optional[Dict[str, str]]) -> Path:
        h = hashlib.sha1()
        h.update(url.encode("utf-8"))
        if headers:
            h.update(json.dumps(headers, sort_keys=True).encode("utf-8"))
        return self.cache_dir / (h.hexdigest() + ".json")

    def _from_cache(self, p: Path, ttl: int) -> Optional[Dict[str, Any]]:
        if ttl <= 0:
            return None
        if not p.exists():
            return None
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            if time.time() - float(obj.get("_ts", 0)) <= ttl:
                return obj
        except Exception:
            return None
        return None

    def _to_cache(self, p: Path, payload: Dict[str, Any]) -> None:
        try:
            payload = dict(payload)
            payload["_ts"] = time.time()
            p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            # best-effort cache
            pass

    # -------- run --------

    def run(
        self,
        url: str,
        ttl: int = 86400,
        timeout: float = 20.0,
        max_bytes: int = 1_000_000,
        headers: Optional[Dict[str, str]] = None,
        allow_network: bool = False,
        **_: Any,
    ) -> Dict[str, Any]:
        if not allow_network:
            return {
                "ok": False,
                "data": None,
                "error": "Network is disabled by policy (allow_network=False).",
                "meta": {"tool": self.name},
            }

        cache_p = self._cache_file(url, headers)
        cached = self._from_cache(cache_p, ttl)
        if cached:
            payload = {
                "ok": True,
                "data": {
                    "url": url,
                    "status": cached.get("status"),
                    "headers": cached.get("headers"),
                    "text": cached.get("text"),
                    "cached": True,
                    "cache_age": time.time() - float(cached.get("_ts", 0)),
                },
                "error": None,
                "meta": {"tool": self.name},
            }
            return payload

        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as c:
                r = c.get(url, headers=headers)
            status = r.status_code
            # Truncate safely to max_bytes
            b = r.content[: max(0, int(max_bytes))]
            # Decode using server-declared encoding or fallback
            enc = r.encoding or "utf-8"
            text = b.decode(enc, errors="ignore")

            to_store = {"status": status, "headers": dict(r.headers), "text": text}
            if ttl > 0:
                self._to_cache(cache_p, to_store)

            return {
                "ok": True,
                "data": {
                    "url": url,
                    "status": status,
                    "headers": dict(r.headers),
                    "text": text,
                    "cached": False,
                },
                "error": None,
                "meta": {"tool": self.name},
            }
        except Exception as e:
            return {
                "ok": False,
                "data": None,
                "error": f"HTTP error: {e}",
                "meta": {"tool": self.name},
            }
