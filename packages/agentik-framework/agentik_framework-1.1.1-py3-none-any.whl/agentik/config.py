from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError
import yaml


# ---------------------
# Base schema (unchanged)
# ---------------------

class LoopConfig(BaseModel):
    max_steps: int = 8
    reflect: bool = True


class AgentConfig(BaseModel):
    name: str = "AgentikBot"
    goal: str = ""
    loop: LoopConfig = LoopConfig()


class LLMConfig(BaseModel):
    model: str = "openai/gpt-4o-mini"
    temperature: float = 0.2
    json_mode: bool = False


class MemoryConfig(BaseModel):
    type: str = "json"
    path: str = "./memory/default.json"


class PoliciesConfig(BaseModel):
    allow_network: bool = True
    allow_filesystem: bool = True


class AgentikConfig(BaseModel):
    version: int = 1
    agent: AgentConfig = AgentConfig()
    llm: LLMConfig = LLMConfig()
    memory: MemoryConfig = MemoryConfig()
    tools: list[str] = Field(default_factory=list)
    policies: PoliciesConfig = PoliciesConfig()


# ---------------------
# Config loading & precedence
# CLI > local .agentikrc > env vars > YAML file defaults
# ---------------------

RC_FILENAMES = [".agentikrc", ".agentikrc.yaml", ".agentikrc.yml"]


def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def find_rc_path_for_read() -> Tuple[Optional[Path], str]:
    """
    Prefer local .agentikrc in CWD; else home. Return (path or None, "local"/"global"/"none").
    """
    cwd = Path.cwd()
    for name in RC_FILENAMES:
        p = cwd / name
        if p.exists():
            return p, "local"
    home = Path.home()
    for name in RC_FILENAMES:
        p = home / name
        if p.exists():
            return p, "global"
    return None, "none"


def rc_path_for_write(scope: str) -> Path:
    if scope == "global":
        return Path.home() / ".agentikrc"
    return Path.cwd() / ".agentikrc"


def read_rc() -> Tuple[Dict[str, Any], Optional[Path], str]:
    path, scope = find_rc_path_for_read()
    return (_safe_load_yaml(path) if path else {}), path, scope


def write_rc(rc: Dict[str, Any], scope: str = "local") -> Path:
    path = rc_path_for_write(scope)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(rc, allow_unicode=True, sort_keys=True)
    path.write_text(text, encoding="utf-8")
    return path


def get_nested(d: Dict[str, Any], keypath: str) -> Any:
    cur: Any = d
    for k in keypath.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def set_nested(d: Dict[str, Any], keypath: str, value: Any) -> Dict[str, Any]:
    cur = d
    parts = keypath.split(".")
    for k in parts[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[parts[-1]] = value
    return d


def load_config(path: str | Path) -> AgentikConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    try:
        return AgentikConfig(**data)
    except ValidationError as e:
        raise SystemExit("Invalid config:\n" + str(e))


def merge_precedence(
    cfg: AgentikConfig,
    cli_overrides: Dict[str, Any],
) -> AgentikConfig:
    """
    Apply precedence: CLI > local RC > env vars > YAML defaults (already in cfg).
    Only a few high-impact fields are overridden in Step 2.
    """
    rc, _path, _scope = read_rc()
    env_model = os.getenv("AGENTIK_MODEL")
    env_temp = os.getenv("AGENTIK_TEMPERATURE")
    env_steps = os.getenv("AGENTIK_MAX_STEPS")

    # RC overrides
    rc_model = get_nested(rc, "llm.model")
    rc_temp = get_nested(rc, "llm.temperature")
    rc_steps = get_nested(rc, "agent.loop.max_steps")

    # Build effective values
    model_eff = cli_overrides.get("llm.model") or rc_model or env_model or cfg.llm.model
    temp_eff = cli_overrides.get("llm.temperature") or rc_temp or env_temp or cfg.llm.temperature
    steps_eff = cli_overrides.get("agent.loop.max_steps") or rc_steps or env_steps or cfg.agent.loop.max_steps

    # Coerce numeric env if present
    try:
        temp_eff = float(temp_eff)
    except (TypeError, ValueError):
        temp_eff = cfg.llm.temperature
    try:
        steps_eff = int(steps_eff)
    except (TypeError, ValueError):
        steps_eff = cfg.agent.loop.max_steps

    cfg.llm.model = model_eff
    cfg.llm.temperature = temp_eff
    cfg.agent.loop.max_steps = steps_eff
    return cfg


# ---------------------
# Key helpers & cache paths
# ---------------------

def get_openrouter_key() -> Optional[str]:
    """
    Env first; else RC llm.openrouter_api_key; else None.
    """
    env = os.getenv("OPENROUTER_API_KEY")
    if env:
        return env
    rc, _p, _s = read_rc()
    return get_nested(rc, "llm.openrouter_api_key")


def rc_cache_path(filename: str) -> Path:
    root = Path.home() / ".agentik" / "cache"
    root.mkdir(parents=True, exist_ok=True)
    return root / filename
