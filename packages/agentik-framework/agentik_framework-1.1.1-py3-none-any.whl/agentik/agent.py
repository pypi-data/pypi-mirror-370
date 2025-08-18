from __future__ import annotations

import json
import re
import time
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError
from jsonschema import validate as js_validate, ValidationError as JSONSchemaError

from .config import AgentikConfig
from .llm.openrouter import OpenRouterClient
from .llm.openrouter import list_models_cached
from .tools.registry import discover_tools, instantiate
from .tools.io import shape_tool_result, summarize_for_observation
from .memory import make_memory


# ---------- Planning action schema ----------

class ToolCall(BaseModel):
    type: str = Field("call_tool", pattern="^call_tool$")
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)

class FinalAnswer(BaseModel):
    type: str = Field("final_answer", pattern="^final_answer$")
    final: str

PlanAction = ToolCall | FinalAnswer


# ---------- Utilities ----------

def _safe_json(s: str) -> Optional[dict]:
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"\{.*\}", s, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _render_tools_catalog() -> Tuple[str, Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    tools = discover_tools()
    catalog_lines: List[str] = []
    schemas: Dict[str, Dict[str, Any]] = {}
    meta: Dict[str, Dict[str, Any]] = {}

    for name, cls in tools.items():
        descr = getattr(cls, "description", "").strip()
        schema = getattr(cls, "schema", None) or {"type": "object"}
        schemas[name] = schema
        meta[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": descr or f"Tool {name}",
                "parameters": schema,
            },
        }
        pretty_schema = json.dumps(schema, ensure_ascii=False, indent=2) if schema else "{}"
        catalog_lines.append(f"- {name}: {descr}\n  schema: {pretty_schema}")

    return "\n".join(catalog_lines), schemas, meta


def _validate_args(args: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    if not schema:
        return True, ""
    try:
        js_validate(instance=args, schema=schema)
        return True, ""
    except JSONSchemaError as e:
        msg = str(getattr(e, "message", "")) or str(e).splitlines()[0]
        return False, msg


def _price_per_1k_from_env() -> Tuple[Optional[float], Optional[float]]:
    def _parse(name: str) -> Optional[float]:
        v = os.getenv(name)
        if not v:
            return None
        try:
            return float(v.strip().replace("$", ""))
        except Exception:
            return None
    return _parse("AGENTIK_PRICE_PROMPT_PER_1K"), _parse("AGENTIK_PRICE_COMPLETION_PER_1K")


def _estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> Optional[float]:
    pp_env, cp_env = _price_per_1k_from_env()
    if pp_env is not None or cp_env is not None:
        pp = pp_env or 0.0
        cp = cp_env or 0.0
        return (prompt_tokens / 1000.0) * pp + (completion_tokens / 1000.0) * cp

    try:
        models = list_models_cached(ttl=24 * 3600)
        rec = None
        for m in models:
            m_id = m.get("id") or m.get("name")
            if m_id and str(m_id).lower() == str(model).lower():
                rec = m
                break
        if not rec:
            return None
        pricing = rec.get("pricing") or {}
        def _coerce(x: Any) -> Optional[float]:
            if x is None:
                return None
            if isinstance(x, (int, float)):
                return float(x)
            s = str(x)
            s = s.replace("$", "").replace(",", "").strip().lower()
            try:
                num = float(re.split(r"[^0-9.]+", s)[0])
            except Exception:
                return None
            if "/1m" in s or "/1000000" in s:
                return num / 1000.0
            return num
        pp = _coerce(pricing.get("prompt"))
        cp = _coerce(pricing.get("completion"))
        if pp is None or cp is None:
            return None
        return (prompt_tokens / 1000.0) * pp + (completion_tokens / 1000.0) * cp
    except Exception:
        return None


# ---------- Prompts ----------

PLANNER_SYSTEM = """You are Agentik's planner. Your job each step is to either:
1) choose ONE tool to call with proper JSON args, or
2) produce the final answer when the goal is satisfied.

Return STRICT JSON matching ONE of these schemas:

- Call a tool:
  {"type":"call_tool","tool":"<tool_name>","args":{...}}

- Final answer:
  {"type":"final_answer","final":"<your final answer>"}

Rules:
- Only choose tools from the 'Available tools' section.
- Validate your args against the tool schema (when provided).
- If no tool is needed, return a final answer.
- NEVER wrap JSON in code fences. Output JSON ONLY.
"""

REFLECT_SYSTEM = """You are Agentik's reflector. Given the last step (thought, action, observation) and the overall goal,
write one short sentence about what to try next. Keep it terse."""

def _build_planner_messages(goal: str, tools_catalog: str, context: List[Dict[str, str]]) -> List[Dict[str, str]]:
    msgs: List[Dict[str, str]] = [{"role": "system", "content": PLANNER_SYSTEM}]
    msgs.append({"role": "system", "content": f"Goal: {goal}"})
    msgs.append({"role": "system", "content": "Available tools:\n" + tools_catalog})
    msgs.extend(context)
    msgs.append({"role": "user", "content": "Decide the next action and return JSON ONLY."})
    return msgs

def _build_reflect_messages(goal: str, last_step_summary: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": REFLECT_SYSTEM},
        {"role": "system", "content": f"Goal: {goal}"},
        {"role": "user", "content": last_step_summary},
    ]


# ---------- Agent Runner ----------

@dataclass
class AgentResult:
    final_text: str
    steps: int
    transcript: List[Dict[str, Any]]
    stats: Dict[str, Any]


class AgentRunner:
    def __init__(self, cfg: AgentikConfig, client: OpenRouterClient) -> None:
        self.cfg = cfg
        self.client = client
        self.memory = make_memory(cfg.memory.type, cfg.memory.path)

    def run(
        self,
        user_prompt: str,
        stream_final: bool = False,
        save_transcript: Optional[Path] = None,
        run_meta: Optional[Dict[str, Any]] = None,
        obs_max_chars: int = 1200,
    ) -> AgentResult:
        """
        Execute the loop and persist a JSONL transcript with meta_start/meta_end lines.
        """
        t_run0 = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()
        run_meta = run_meta or {}
        run_id = run_meta.get("run_id") or f"run_{int(time.time()*1000)}"

        goal = self.cfg.agent.goal or f"Respond to: {user_prompt}"
        max_steps = max(1, int(self.cfg.agent.loop.max_steps))
        reflect_on = bool(self.cfg.agent.loop.reflect)

        catalog, schemas, tool_meta = _render_tools_catalog()
        allowed = set(self.cfg.tools or [])

        if allowed:
            tool_meta = {k: v for k, v in tool_meta.items() if k in allowed}

        prior_summary = self.memory.summarize(n=20, max_chars=1000)
        context: List[Dict[str, str]] = []
        if prior_summary:
            context.append({"role": "system", "content": f"Memory summary:\n{prior_summary}"})

        transcript: List[Dict[str, Any]] = [{"role": "user", "content": user_prompt}]
        self.memory.remember({"role": "user", "content": user_prompt})

        # stats
        total_prompt_tokens = 0
        total_completion_tokens = 0
        stats = {
            "planner_calls": 0,
            "reflect_calls": 0,
            "tool_calls": 0,
            "duration_ms": {"planner": 0.0, "reflect": 0.0, "tools": 0.0},
        }

        # file lines
        file_lines: List[Dict[str, Any]] = []

        # meta_start
        file_lines.append({
            "type": "meta_start",
            "run_id": run_id,
            "started_at": started_at,
            "agent": self.cfg.agent.name,
            "model": self.cfg.llm.model,
            "temperature": self.cfg.llm.temperature,
            "tools_enabled": sorted(list(allowed)) if allowed else None,
            "memory": {"type": self.cfg.memory.type, "path": self.cfg.memory.path},
            "policies": {
                "allow_network": bool(self.cfg.policies.allow_network),
                "allow_filesystem": bool(self.cfg.policies.allow_filesystem),
            },
            "profile": run_meta.get("profile"),
            "tags": run_meta.get("tags") or [],
            "note": run_meta.get("note"),
        })

        final_text = ""
        last_observation = ""
        step = 0

        for step in range(1, max_steps + 1):
            # planner
            planner_msgs = _build_planner_messages(
                goal, catalog,
                context + [
                    {"role": "system", "content": f"User prompt: {user_prompt}"},
                    {"role": "system", "content": f"Previous observation: {last_observation[:obs_max_chars]}"},
                ],
            )
            t0 = time.perf_counter()
            resp = self.client.chat(
                planner_msgs,
                model=self.cfg.llm.model,
                temperature=self.cfg.llm.temperature,
                response_format={"type": "json_object"},
                tools=list(tool_meta.values()),
                tool_choice="auto",
            )
            stats["duration_ms"]["planner"] += (time.perf_counter() - t0) * 1000.0
            stats["planner_calls"] += 1

            raw = resp.get("raw") or {}
            usage = raw.get("usage") or {}
            total_prompt_tokens += int(usage.get("prompt_tokens") or 0)
            total_completion_tokens += int(usage.get("completion_tokens") or 0)

            content = resp.get("content") or ""
            data = _safe_json(content)
            if not data:
                # second try
                t1 = time.perf_counter()
                resp2 = self.client.chat(
                    [{"role": "system", "content": PLANNER_SYSTEM},
                     {"role": "user", "content": "Return the JSON now. If you cannot decide, return a final answer."}],
                    model=self.cfg.llm.model,
                    temperature=0,
                    response_format={"type": "json_object"},
                    tools=list(tool_meta.values()),
                    tool_choice="auto",
                )
                stats["duration_ms"]["planner"] += (time.perf_counter() - t1) * 1000.0
                stats["planner_calls"] += 1
                raw2 = resp2.get("raw") or {}
                usage2 = raw2.get("usage") or {}
                total_prompt_tokens += int(usage2.get("prompt_tokens") or 0)
                total_completion_tokens += int(usage2.get("completion_tokens") or 0)
                data = _safe_json((resp2.get("content") or ""))

            if not data:
                final_text = "I'm sorry, I couldn't decide the next action."
                break

            # action
            action: Optional[PlanAction] = None
            try:
                if data.get("type") == "call_tool":
                    action = ToolCall(**data)
                elif data.get("type") == "final_answer":
                    action = FinalAnswer(**data)
            except ValidationError:
                action = None

            if action is None:
                final_text = "Planner returned an invalid action."
                break

            if isinstance(action, FinalAnswer):
                final_text = action.final
                self.memory.remember({"role": "assistant", "content": final_text})
                if stream_final:
                    final_msgs = context + [
                        {"role": "system", "content": f"Goal: {goal}"},
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": "Write the final answer clearly."},
                    ]
                    t2 = time.perf_counter()
                    acc: List[str] = []
                    for chunk in self.client.stream_chat(final_msgs, model=self.cfg.llm.model, temperature=0.2):
                        acc.append(chunk)
                        print(chunk, end="")
                    print()
                    stats["duration_ms"]["planner"] += (time.perf_counter() - t2) * 1000.0
                    final_text = "".join(acc) or final_text
                break

            # tool call
            tool_name = action.tool
            args = dict(action.args or {})

            if allowed and tool_name not in allowed:
                last_observation = f"Tool '{tool_name}' is not enabled by configuration."
                preview = summarize_for_observation({"error": "disabled"}, obs_max_chars)
                context.append({"role": "system", "content": f"Observation: {preview}"})
                row = {"role": "tool", "name": tool_name, "error": "disabled"}
                transcript.append(row)
                file_lines.append(row)
                self.memory.remember({"role": "tool", "name": tool_name, "error": "disabled"})
                continue

            args.setdefault("allow_network", bool(self.cfg.policies.allow_network))
            args.setdefault("allow_filesystem", bool(self.cfg.policies.allow_filesystem))

            schema = schemas.get(tool_name) or {"type": "object"}
            ok, msg = _validate_args(args, schema)
            if not ok:
                last_observation = f"Invalid args for {tool_name}: {msg}"
                preview = summarize_for_observation({"error": msg}, obs_max_chars)
                context.append({"role": "system", "content": f"Observation: {preview}"})
                row = {"role": "tool", "name": tool_name, "error": msg}
                transcript.append(row)
                file_lines.append(row)
                self.memory.remember({"role": "tool", "name": tool_name, "error": msg})
                continue

            t3 = time.perf_counter()
            try:
                tool = instantiate(tool_name)
                raw_result = tool.run(**args)
                shaped = shape_tool_result(tool_name, raw_result)
                latency_ms = (time.perf_counter() - t3) * 1000.0
                stats["tool_calls"] += 1
                stats["duration_ms"]["tools"] += latency_ms

                preview = summarize_for_observation(shaped, obs_max_chars)
                last_observation = f"{tool_name} → {preview}"
                context.append({"role": "system", "content": f"Observation: {last_observation}"})

                row = {"role": "tool", "name": tool_name, "args": args, "result": shaped, "latency_ms": round(latency_ms, 1)}
                transcript.append(row)
                file_lines.append(row)
                self.memory.remember({"role": "tool", "name": tool_name, "args": args, "result": shaped})
            except Exception as e:
                latency_ms = (time.perf_counter() - t3) * 1000.0
                stats["duration_ms"]["tools"] += latency_ms
                last_observation = f"Tool '{tool_name}' failed: {e}"
                context.append({"role": "system", "content": f"Observation: {last_observation}"})
                row = {"role": "tool", "name": tool_name, "args": args, "error": str(e), "latency_ms": round(latency_ms, 1)}
                transcript.append(row)
                file_lines.append(row)
                self.memory.remember({"role": "tool", "name": tool_name, "args": args, "error": str(e)})

            # reflect
            if reflect_on and step < max_steps:
                t4 = time.perf_counter()
                refl = self.client.chat(
                    _build_reflect_messages(goal, last_observation[:400]),
                    model=self.cfg.llm.model,
                    temperature=0.2,
                )
                dt = (time.perf_counter() - t4) * 1000.0
                stats["duration_ms"]["reflect"] += dt
                stats["reflect_calls"] += 1
                rawr = refl.get("raw") or {}
                usar = rawr.get("usage") or {}
                total_prompt_tokens += int(usar.get("prompt_tokens") or 0)
                total_completion_tokens += int(usar.get("completion_tokens") or 0)

                reflection = (refl.get("content") or "").strip()
                if reflection:
                    context.append({"role": "system", "content": f"Reflection: {reflection}"})
                    row = {"role": "assistant", "content": f"[reflection] {reflection}"}
                    transcript.append(row)
                    file_lines.append(row)
                    self.memory.remember(row)

        # FINAL write
        total_tokens = total_prompt_tokens + total_completion_tokens
        cost = _estimate_cost_usd(self.cfg.llm.model, total_prompt_tokens, total_completion_tokens)
        elapsed_ms = (time.perf_counter() - t_run0) * 1000.0
        ended_at = datetime.now(timezone.utc).isoformat()

        # Ensure final answer shows up in file lines
        file_lines.extend(transcript)  # guaranteed safe even if already added rows above
        file_lines.append({"role": "assistant", "content": final_text})

        meta_end = {
            "type": "meta_end",
            "run_id": run_id,
            "ended_at": ended_at,
            "elapsed_ms": round(elapsed_ms, 1),
            "steps": min(step, max_steps),
            "stats": {
                "tokens": {
                    "prompt": total_prompt_tokens,
                    "completion": total_completion_tokens,
                    "total": total_tokens,
                },
                "duration_ms": stats["duration_ms"],
                "planner_calls": stats["planner_calls"],
                "reflect_calls": stats["reflect_calls"],
                "tool_calls": stats["tool_calls"],
                "cost_estimated_usd": cost,
            },
        }

        # Save transcript
        if save_transcript:
            save_transcript.parent.mkdir(parents=True, exist_ok=True)
            with save_transcript.open("a", encoding="utf-8") as f:
                f.write(json.dumps(file_lines[0], ensure_ascii=False) + "\n")  # meta_start
                # avoid duplicating meta_start; file_lines[1:] contain rows & final
                for line in file_lines[1:]:
                    f.write(json.dumps(line, ensure_ascii=False) + "\n")
                f.write(json.dumps(meta_end, ensure_ascii=False) + "\n")

        return AgentResult(
            final_text=final_text,
            steps=min(step, max_steps),
            transcript=transcript,
            stats={
                "tokens": {
                    "prompt": total_prompt_tokens,
                    "completion": total_completion_tokens,
                    "total": total_tokens,
                },
                "cost_estimated_usd": cost,
                "duration_ms": stats["duration_ms"],
                "planner_calls": stats["planner_calls"],
                "reflect_calls": stats["reflect_calls"],
                "tool_calls": stats["tool_calls"],
                "run_id": run_id,
                "started_at": started_at,
            },
        )
