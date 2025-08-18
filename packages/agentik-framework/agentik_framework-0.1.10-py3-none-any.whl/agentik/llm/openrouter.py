# llm/openrouter.py
from __future__ import annotations

import os
import json
import time
from typing import Any, Dict, Generator, List, Optional

import httpx

from ..config import get_openrouter_key, rc_cache_path
from ..utils.errors import AuthError, RateLimitError, NetworkError

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def redact(s: str, keep: int = 6) -> str:
    if not s:
        return ""
    return s[:keep] + "..." if len(s) > keep else "***"


def _raise_http_error(e: httpx.HTTPStatusError) -> None:
    code = e.response.status_code
    text = e.response.text[:500]
    if code in (401, 403):
        raise AuthError("OpenRouter auth failed (401/403). Check OPENROUTER_API_KEY.") from e
    if code == 429:
        raise RateLimitError("OpenRouter rate limit (429). Slow down or upgrade plan.") from e
    raise NetworkError(f"OpenRouter HTTP {code}: {text}") from e


class OpenRouterClient:
    """
    Minimal OpenRouter client with graceful fallback:
      - If model does not support tool use and a request includes tools,
        retry once without tool params.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = OPENROUTER_BASE_URL,
        timeout: float = 60.0,
        referer: Optional[str] = None,
        title: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or get_openrouter_key()
        self.base_url = base_url
        self.timeout = timeout
        self.referer = referer or os.getenv("OPENROUTER_REFERER")
        self.title = title or os.getenv("OPENROUTER_TITLE") or "Agentik"
        self._client = httpx.Client(timeout=self.timeout)

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise AuthError(
                "OPENROUTER_API_KEY is not set. Use `agentik keys set openrouter sk-or-...` or set env."
            )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.title:
            headers["X-Title"] = self.title
        return headers

    # ---- internal helpers (NON-STREAM + STREAM split) --------------------

    def _has_tool_params(self, p: Dict[str, Any]) -> bool:
        if "tools" in p and p["tools"]:
            return True
        tc = p.get("tool_choice")
        return tc is not None and tc != "none"

    def _strip_tools(self, p: Dict[str, Any]) -> Dict[str, Any]:
        q = {k: v for k, v in p.items() if k not in ("tools", "parallel_tool_calls")}
        q["tool_choice"] = "none"
        return q

    def _post_with_tool_fallback(self, payload: Dict[str, Any]) -> httpx.Response:
        """
        Non-streaming POST to /chat/completions.
        Returns httpx.Response.
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._headers()

        try:
            r = self._client.post(url, headers=headers, json=payload)
            try:
                r.raise_for_status()
                return r
            except httpx.HTTPStatusError as e:
                text = (e.response.text or "").lower()
                if (
                    e.response.status_code == 404
                    and "support tool use" in text
                    and self._has_tool_params(payload)
                ):
                    payload2 = self._strip_tools(payload)
                    r2 = self._client.post(url, headers=headers, json=payload2)
                    r2.raise_for_status()
                    return r2
                _raise_http_error(e)
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.TransportError) as e:
            raise NetworkError("Network error talking to OpenRouter.") from e

    def _stream_with_tool_fallback(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Streaming POST to /chat/completions.
        Yields SSE text lines (str).
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._headers()
        # Hint to servers we expect SSE
        headers.setdefault("Accept", "text/event-stream")

        try:
            with self._client.stream("POST", url, headers=headers, json=payload) as r:
                try:
                    r.raise_for_status()
                    for line in r.iter_lines():
                        if not line:
                            continue
                        # httpx.iter_lines() yields str lines
                        yield line
                    return
                except httpx.HTTPStatusError as e:
                    text = (e.response.text or "").lower()
                    if (
                        e.response.status_code == 404
                        and "support tool use" in text
                        and self._has_tool_params(payload)
                    ):
                        payload2 = self._strip_tools(payload)
                        with self._client.stream("POST", url, headers=headers, json=payload2) as r2:
                            r2.raise_for_status()
                            for line in r2.iter_lines():
                                if not line:
                                    continue
                                yield line
                            return
                    _raise_http_error(e)
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.TransportError) as e:
            raise NetworkError("Network error talking to OpenRouter.") from e

    # ---- public API ------------------------------------------------------

    def chat(self, messages: List[Dict[str, str]], model: str, **params: Any) -> Dict[str, Any]:
        """Return dict with keys: raw (full response), content (assistant text or "")."""
        payload = {"model": model, "messages": messages} | params
        r = self._post_with_tool_fallback(payload)
        data = r.json()
        choice = data.get("choices", [{}])[0]
        content = ""
        if "message" in choice and isinstance(choice["message"], dict):
            content = choice["message"].get("content") or ""
        return {"raw": data, "content": content}

    def stream_chat(
        self, messages: List[Dict[str, str]], model: str, **params: Any
    ) -> Generator[str, None, None]:
        """Yield content deltas as they arrive."""
        payload = {"model": model, "stream": True, "messages": messages} | params
        for line in self._stream_with_tool_fallback(payload):
            # httpx.iter_lines gives str; normalize
            if isinstance(line, bytes):
                try:
                    line = line.decode("utf-8", errors="ignore")
                except Exception:
                    continue
            if not isinstance(line, str):
                continue
            if not line.startswith("data: "):
                continue
            chunk = line[len("data: ") :].strip()
            if chunk == "[DONE]":
                break
            try:
                obj = json.loads(chunk)
                delta = obj.get("choices", [{}])[0].get("delta", {}).get("content")
                if delta:
                    yield delta
            except Exception:
                continue


def ensure_openrouter_key(required: bool = True) -> Optional[str]:
    key = get_openrouter_key()
    if not key and required:
        raise AuthError(
            "OPENROUTER_API_KEY is not set. Use:\n"
            "  PowerShell: setx OPENROUTER_API_KEY \"sk-or-...\"\n"
            "  or: agentik keys set openrouter sk-or-... --global"
        )
    return key


def list_models_cached(ttl: int = 24 * 3600) -> List[Dict[str, Any]]:
    """Cached model list (24h default) at ~/.agentik/cache/models.json"""
    cache_file = rc_cache_path("models.json")
    if cache_file.exists():
        try:
            meta = json.loads(cache_file.read_text(encoding="utf-8"))
            if time.time() - meta.get("_ts", 0) < ttl and "data" in meta:
                return meta["data"]
        except Exception:
            pass

    api_key = get_openrouter_key()
    if not api_key:
        return []

    try:
        with httpx.Client(timeout=30.0) as c:
            r = c.get(
                f"{OPENROUTER_BASE_URL}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            r.raise_for_status()
            data = r.json().get("data", [])
    except httpx.HTTPStatusError as e:
        _raise_http_error(e)
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.TransportError) as e:
        raise NetworkError("Network error listing models.") from e

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps({"_ts": time.time(), "data": data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return data
