from __future__ import annotations

import re
import html as ihtml
from typing import Any, Dict


class HtmlToTextTool:
    """
    Minimal HTML -> plain text converter without extra deps.
    Removes <script>/<style>, collapses whitespace, preserves simple line breaks.
    """

    name = "html_to_text"
    description = "Convert raw HTML into readable plain text (no external dependencies)."
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "html": {"type": "string", "description": "Raw HTML to convert"},
            "keep_newlines": {"type": "boolean", "default": True, "description": "Preserve logical line breaks"},
            "drop_links": {"type": "boolean", "default": False, "description": "Remove link URLs, keep anchor text"},
            "max_chars": {"type": "integer", "minimum": 0, "default": 200000, "description": "Limit characters in output (0 = unlimited)"},
        },
        "required": ["html"]
    }

    # crude but effective sanitizer/stripping patterns
    _re_script = re.compile(r"<script[\s\S]*?</script>", re.I)
    _re_style  = re.compile(r"<style[\s\S]*?</style>", re.I)
    _re_tags   = re.compile(r"<[^>]+>")
    _re_block_breaks = re.compile(
        r"</?(?:p|div|section|article|header|footer|li|ul|ol|br|hr|h[1-6]|table|tr|td|th)>",
        re.I
    )

    def run(
        self,
        html: str,
        keep_newlines: bool = True,
        drop_links: bool = False,
        max_chars: int = 200000,
        **_: Any,
    ) -> Dict[str, Any]:
        try:
            s = html or ""
            s = self._re_script.sub(" ", s)
            s = self._re_style.sub(" ", s)

            # Optional: drop URLs from anchors but keep visible text
            if drop_links:
                s = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', s, flags=re.I | re.S)

            # Introduce newlines for common block-level tags
            if keep_newlines:
                s = self._re_block_breaks.sub("\n", s)

            # Remove remaining tags
            s = self._re_tags.sub(" ", s)

            # Unescape entities
            s = ihtml.unescape(s)

            # Normalize whitespace
            s = re.sub(r"[ \t\r\f\v]+", " ", s)
            if keep_newlines:
                # Collapse multiple newlines
                s = re.sub(r"\n{3,}", "\n\n", s)
                # Clean spaces around newlines
                s = re.sub(r" *\n *", "\n", s)
            else:
                s = re.sub(r"\n+", " ", s)

            s = s.strip()
            if max_chars and max_chars > 0:
                s = s[:max_chars]

            return {
                "ok": True,
                "data": {"text": s},
                "error": None,
                "meta": {"tool": self.name},
            }
        except Exception as e:
            return {
                "ok": False,
                "data": None,
                "error": f"html_to_text failed: {e}",
                "meta": {"tool": self.name},
            }
