from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from jinja2 import Environment, BaseLoader, StrictUndefined
from importlib.resources import files as pkg_files


# -------------------------
# Helpers
# -------------------------

_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(s: str) -> str:
    s = s.strip().lower()
    return _slug_re.sub("_", s).strip("_")


def pascal_case(s: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", s.strip())
    return "".join(p.capitalize() for p in parts if p)


def render_string(template: str, context: Dict[str, object]) -> str:
    env = Environment(loader=BaseLoader(), undefined=StrictUndefined, autoescape=False)
    return env.from_string(template).render(**context)


def write_text(path: Path, text: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(text, encoding="utf-8")


def tokenise_filename(name: str, context: Dict[str, object]) -> str:
    # simple token replacement for filenames
    out = name
    out = out.replace("__name_slug__", str(context.get("name_slug", "")))
    out = out.replace("__class_name__", str(context.get("class_name", "")))
    return out


# -------------------------
# Template discovery
# -------------------------

@dataclass
class BuiltinTemplate:
    kind: str   # "project" | "agent" | "tool"
    name: str   # e.g., "basic" or "python"
    path: Path  # package resource path


def _iter_pkg_dir(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            yield p


def list_builtin_templates() -> list[BuiltinTemplate]:
    out: list[BuiltinTemplate] = []
    root = pkg_files("agentik") / "templates"
    for kind in ("project", "agent", "tool"):
        base = root / kind
        if not base.exists():
            continue
        for child in base.iterdir():
            if child.is_dir():
                out.append(BuiltinTemplate(kind=kind, name=child.name, path=Path(str(child))))
    return out


def get_template_root(kind: str, name: str) -> Path:
    return Path(str((pkg_files("agentik") / "templates" / kind / name)))


# -------------------------
# Apply a directory template
# -------------------------

def apply_template_dir(kind: str, name: str, dest: Path, context: Dict[str, object], force: bool = False) -> None:
    src_root = get_template_root(kind, name)
    if not src_root.exists():
        raise FileNotFoundError(f"Template not found: {kind}/{name}")
    for src_file in _iter_pkg_dir(src_root):
        rel = src_file.relative_to(src_root)
        # tokenise filename segments
        rel_parts = [tokenise_filename(part, context) for part in rel.parts]
        out_rel = Path(*rel_parts)
        # strip .j2 extension if present
        if out_rel.suffix == ".j2":
            out_rel = out_rel.with_suffix("")
        dest_file = dest / out_rel

        # render file text
        raw = src_file.read_text(encoding="utf-8")
        text = render_string(raw, context)
        write_text(dest_file, text, overwrite=force)


# -------------------------
# High level commands
# -------------------------

def init_project(path: Path, template: str = "basic", force: bool = False, name: Optional[str] = None) -> None:
    ctx = {
        "project_name": name or path.name,
        "project_slug": slugify(name or path.name),
        "default_agent": "agent",
    }
    apply_template_dir("project", template, path, ctx, force=force)


def new_agent(path: Path, name: str, template: str = "basic",
              tools: list[str] | None = None,
              memory_type: str = "json", memory_path: str = "./memory/agent.json",
              force: bool = False, with_tests: bool = False) -> Path:
    name_slug = slugify(name)
    class_name = pascal_case(name)
    ctx = {
        "name": name,
        "name_slug": name_slug,
        "class_name": class_name,
        "tools": tools or [],
        "memory_type": memory_type,
        "memory_path": memory_path,
    }
    dest = path
    apply_template_dir("agent", template, dest, ctx, force=force)
    # Optional tests (kept simple: a CLI smoke test)
    if with_tests:
        test_path = dest / "tests" / f"test_agent_{name_slug}.py"
        test_code = f'''from pathlib import Path
def test_agent_config_exists():
    p = Path("agents") / "{name_slug}.yaml"
    assert p.exists(), "Expected agents/{name_slug}.yaml"
'''
        write_text(test_path, test_code, overwrite=force)
    return dest / "agents" / f"{name_slug}.yaml"


def new_tool(path: Path, name: str, template: str = "python",
             force: bool = False, with_tests: bool = False) -> Path:
    name_slug = slugify(name)
    class_name = pascal_case(name)
    ctx = {"name": name, "name_slug": name_slug, "class_name": class_name}
    dest = path
    apply_template_dir("tool", template, dest, ctx, force=force)
    if with_tests:
        test_path = dest / "tests" / f"test_tool_{name_slug}.py"
        test_code = f'''from tools.{name_slug} import {class_name}
def test_tool_has_run():
    t = {class_name}()
    assert hasattr(t, "run")
'''
        write_text(test_path, test_code, overwrite=force)
    return dest / "tools" / f"{name_slug}.py"


def pull_template(url_or_git: str, to: Path, force: bool = False) -> None:
    """
    Pull a template repo/zip into directory `to/templates/third_party/<slug>`.
    - If endswith ".zip": downloads and unzips (requires internet).
    - If endswith ".git" or startswith "git+": shell out to `git clone`.
    """
    to = to / "templates" / "third_party"
    to.mkdir(parents=True, exist_ok=True)
    slug = slugify(url_or_git.split("/")[-1].replace(".git", "").replace(".zip", ""))
    target = to / slug
    if target.exists() and not force:
        raise FileExistsError(f"Already exists: {target}")
    if url_or_git.endswith(".git") or url_or_git.startswith("git+"):
        # git clone
        url = url_or_git.replace("git+", "")
        try:
            subprocess.run(["git", "clone", "--depth", "1", url, str(target)], check=True)
        except FileNotFoundError:
            raise RuntimeError("git is not installed or not on PATH.")
    elif url_or_git.endswith(".zip"):
        # http download and unzip
        import httpx, zipfile, io  # lazy import
        r = httpx.get(url_or_git, timeout=60.0)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(target)
    else:
        raise ValueError("Unsupported template source. Use a .git repo or .zip URL.")
