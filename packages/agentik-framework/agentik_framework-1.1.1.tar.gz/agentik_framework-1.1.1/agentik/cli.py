from __future__ import annotations

import os
import sys
import re
import csv
import json
import platform
import time
from pathlib import Path
from typing import Optional, List, Dict, Set

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import (
    load_config,
    AgentikConfig,
    merge_precedence,
    read_rc,
    write_rc,
    set_nested,
    get_nested,
    rc_path_for_write,
)
from .llm.openrouter import (
    OpenRouterClient,
    ensure_openrouter_key,
    list_models_cached,
    redact,
)
from .scaffold import (
    list_builtin_templates,
    init_project,
    new_agent,
    new_tool,
    pull_template,
)
from .tools.registry import discover_tools, instantiate
from .utils.errors import AuthError, RateLimitError, NetworkError
from .memory import make_memory
from .utils.watch import watch_for_changes  # NEW (Step 10)

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

# Sub-apps
keys_app = typer.Typer(help="Manage API keys")
models_app = typer.Typer(help="List OpenRouter models")
config_app = typer.Typer(help="Config helpers (paths, show)")
template_app = typer.Typer(help="Template utilities")
new_app = typer.Typer(help="Create new things (agent, tool)")
tools_app = typer.Typer(help="Tool management and local runs")
batch_app = typer.Typer(help="Batch processing")
validate_app = typer.Typer(help="Validate configs")
memory_app = typer.Typer(help="Memory management")
eval_app = typer.Typer(help="Tiny evaluation harness")
dev_app = typer.Typer(help="Developer utilities (watch & auto-rerun)")  # NEW (Step 10)


def _builtin_profile_overrides(name: str) -> Dict[str, object]:
    name = (name or "").strip().lower()
    if name in ("", "none"):
        return {}
    table: Dict[str, Dict[str, object]] = {
        "fast": {"agent.loop.max_steps": 2, "agent.loop.reflect": False, "llm.temperature": 0.2},
        "thorough": {"agent.loop.max_steps": 6, "agent.loop.reflect": True, "llm.temperature": 0.3},
        "deterministic": {"llm.temperature": 0.0, "agent.loop.reflect": False},
        "creative": {"llm.temperature": 0.9, "agent.loop.reflect": False},
        "cheap": {"llm.temperature": 0.2},  # keep model as-is
        "dev": {"agent.loop.max_steps": 3, "agent.loop.reflect": False, "llm.temperature": 0.3},  # NEW
    }
    return table.get(name, {})


def _clear_console() -> None:
    try:
        if platform.system().lower().startswith("win"):
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        pass


@app.command()
def version() -> None:
    console.print(f"agentik-framework {__version__}")


@app.command()
def self_test() -> None:
    table = Table(title="Agentik Self-Test")
    table.add_column("Check")
    table.add_column("Result")
    table.add_row("Python", sys.version.split()[0])
    table.add_row("OS", f"{platform.system()} {platform.release()} ({platform.machine()})")
    try:
        key = ensure_openrouter_key(required=False)
        table.add_row("OPENROUTER_API_KEY", "set" if key else "missing")
    except Exception:
        table.add_row("OPENROUTER_API_KEY", "missing")
    _rc, rc_path, rc_scope = read_rc()
    table.add_row(".agentikrc", f"{rc_scope}{' @ ' + str(rc_path) if rc_path else ''}")
    console.print(table)


@app.command()
def init(
    path: str = typer.Argument(".", help="Directory to initialize"),
    template: str = typer.Option("basic", "--template", help="Project template name"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    name: Optional[str] = typer.Option(None, "--name", help="Project name (default=folder name)"),
) -> None:
    target = os.path.abspath(path)
    init_project(Path(target), template=template, force=force, name=name)
    console.print(f"✔ Initialized project at [bold]{target}[/bold]")


@app.command()
def run(
    config: str = typer.Argument(..., help="Path to agent YAML config"),
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="User prompt"),
    model: Optional[str] = typer.Option(None, "--model", help="Override model slug"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Override temperature"),
    stream: bool = typer.Option(False, "--stream", help="Stream the final answer"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate only; no LLM calls"),
    save_transcript: Optional[str] = typer.Option(None, "--save-transcript", help="Write a JSONL transcript"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Builtin profile: fast|thorough|deterministic|creative|cheap|dev|none"),
    tag: List[str] = typer.Option([], "--tag", help="Tag this run (repeatable)"),
    note: Optional[str] = typer.Option(None, "--note", help="Freeform note saved in transcript meta"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Provide your own run id"),
    obs_max_chars: int = typer.Option(1200, "--obs-max-chars", help="Max chars in observation previews"),
) -> None:
    """Plan→Act→Reflect loop with memory. Profiles + run metadata. Saves cost/tokens into transcript."""
    cfg: AgentikConfig = load_config(config)
    overrides: Dict[str, object] = {}

    if model is not None:
        overrides["llm.model"] = model
    if temperature is not None:
        overrides["llm.temperature"] = temperature

    # profile overrides
    if profile:
        prof = _builtin_profile_overrides(profile)
        if not prof and profile.lower() not in ("", "none"):
            console.print(f"[yellow]Unknown profile:[/yellow] {profile}. Using config defaults.")
        overrides.update(prof)

    cfg = merge_precedence(cfg, overrides)

    if not prompt:
        console.print("[red]No prompt given.[/red] Use -p/--prompt to send a message.")
        raise typer.Exit(2)

    console.print(
        f"[bold]Agent:[/bold] {cfg.agent.name} • "
        f"Model: [cyan]{cfg.llm.model}[/cyan] • Temp: {cfg.llm.temperature}"
    )
    console.print(
        f"[bold]Max steps:[/bold] {cfg.agent.loop.max_steps} • "
        f"[bold]Reflect:[/bold] {cfg.agent.loop.reflect}"
    )
    console.print(f"[bold]Memory:[/bold] {cfg.memory.type} ({cfg.memory.path})")
    if profile:
        console.print(f"[bold]Profile:[/bold] {profile}")
    if cfg.tools:
        console.print(f"[bold]Enabled tools:[/bold] {', '.join(cfg.tools)}")
    else:
        console.print("[yellow]No tools enabled. Planner may still finalize.[/yellow]")

    if dry_run:
        console.print("[green]Dry run completed (config validated).[/green]")
        return

    try:
        ensure_openrouter_key(required=True)
        client = OpenRouterClient()
        from .agent import AgentRunner
        runner = AgentRunner(cfg, client)
        transcript_path = Path(save_transcript) if save_transcript else None

        result = runner.run(
            user_prompt=prompt,
            stream_final=stream,
            save_transcript=transcript_path,
            run_meta={"profile": profile, "tags": tag, "note": note, "run_id": run_id},
            obs_max_chars=obs_max_chars,
        )
        if stream:
            console.print("\n[dim](stream complete)[/dim]")
        else:
            console.print("\n[bold]Final:[/bold] " + (result.final_text or "(empty)"))

        # Summary
        stats = result.stats or {}
        tokens = stats.get("tokens", {})
        duration = stats.get("duration_ms", {})
        cost = stats.get("cost_estimated_usd", None)
        rid = stats.get("run_id")

        table = Table(title="Run Summary")
        table.add_column("Metric"); table.add_column("Value", justify="right")
        table.add_row("Run ID", str(rid))
        table.add_row("Steps", str(result.steps))
        table.add_row("Planner calls", str(stats.get("planner_calls", 0)))
        table.add_row("Tool calls", str(stats.get("tool_calls", 0)))
        table.add_row("Reflect calls", str(stats.get("reflect_calls", 0)))
        table.add_row("Tokens (prompt)", str(tokens.get("prompt", 0)))
        table.add_row("Tokens (completion)", str(tokens.get("completion", 0)))
        table.add_row("Tokens (total)", str(tokens.get("total", 0)))
        table.add_row("Time (planner ms)", f"{duration.get('planner', 0.0):.1f}")
        table.add_row("Time (tools ms)", f"{duration.get('tools', 0.0):.1f}")
        table.add_row("Time (reflect ms)", f"{duration.get('reflect', 0.0):.1f}")
        if cost is not None:
            table.add_row("Estimated cost (USD)", f"${cost:.4f}")
        console.print(table)

        if cost is None:
            console.print(
                "[dim]Tip: set env vars AGENTIK_PRICE_PROMPT_PER_1K and "
                "AGENTIK_PRICE_COMPLETION_PER_1K to show estimated cost, "
                "or ensure OpenRouter pricing is available for the model.[/dim]"
            )

        if transcript_path:
            console.print(f"📝 Saved transcript → [bold]{transcript_path}[/bold]")

    except AuthError as e:
        console.print(f"[red]Auth error:[/red] {e}\nHint: `agentik keys show` or setx OPENROUTER_API_KEY ...")
        raise typer.Exit(1)
    except RateLimitError as e:
        console.print(f"[red]Rate limited:[/red] {e}\nHint: add delay/batch or upgrade plan.")
        raise typer.Exit(1)
    except NetworkError as e:
        console.print(f"[red]Network error:[/red] {e}\nHint: check connectivity or retry.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Run failed:[/red] {e}")
        raise typer.Exit(1)


# -------- keys --------
@keys_app.command("set")
def keys_set_openrouter(
    api_key: str = typer.Argument(..., help="Your OpenRouter API key (sk-or-...)"),
    global_scope: bool = typer.Option(False, "--global", help="Write to HOME .agentikrc"),
    local_scope: bool = typer.Option(False, "--local", help="Write to local project .agentikrc"),
) -> None:
    scope = "global" if global_scope else "local"
    if global_scope and local_scope:
        console.print("[red]Choose only one of --global or --local.[/red]")
        raise typer.Exit(2)
    rc, _p, _s = read_rc()
    set_nested(rc, "llm.openrouter_api_key", api_key)
    path = write_rc(rc, scope=scope)
    console.print(f"✔ Saved to [bold]{path}[/bold]")

@keys_app.command("show")
def keys_show_openrouter() -> None:
    env = os.getenv("OPENROUTER_API_KEY")
    if env:
        console.print(f"Env: OPENROUTER_API_KEY = {redact(env)}")
    rc, rc_path, rc_scope = read_rc()
    k = get_nested(rc, "llm.openrouter_api_key")
    if k:
        console.print(f"{rc_scope.title()} RC ({rc_path}): {redact(k)}")
    if not env and not k:
        console.print("[yellow]No key found in env or RC.[/yellow]")

app.add_typer(keys_app, name="keys")


# -------- models --------
@models_app.command("list")
def models_list(
    filter: Optional[str] = typer.Option(None, "--filter", help="Substring filter on model id"),
    refresh: bool = typer.Option(False, "--refresh", help="Ignore cache"),
) -> None:
    data = list_models_cached(ttl=0 if refresh else 24 * 3600)
    if not data:
        console.print("[yellow]No models found. Missing key or network?[/yellow]")
        raise typer.Exit(1)

    table = Table(title="OpenRouter Models")
    table.add_column("ID", overflow="fold")
    table.add_column("Context")
    table.add_column("Pricing (prompt/comp)", overflow="fold")

    for m in data:
        mid = m.get("id") or m.get("name") or "unknown"
        if filter and filter.lower() not in str(mid).lower():
            continue
        ctx = str(m.get("context_length") or m.get("context") or "")
        pricing = m.get("pricing") or {}
        prompt_p = pricing.get("prompt") or ""
        comp_p = pricing.get("completion") or ""
        table.add_row(str(mid), ctx, f"{prompt_p} / {comp_p}")

    console.print(table)

app.add_typer(models_app, name="models")


# -------- new --------
@new_app.command("agent")
def new_agent_cmd(
    name: str = typer.Argument(..., help="Agent name"),
    template: str = typer.Option("basic", "--template", help="Agent template"),
    tools: str = typer.Option("", "--tools", help="Comma-separated tools"),
    memory: str = typer.Option("json", "--memory", help="dict|json"),
    memory_path: str = typer.Option("./memory/agent.json", "--memory-path"),
    to: str = typer.Option(".", "--to", help="Destination directory"),
    with_tests: bool = typer.Option(False, "--with-tests"),
    force: bool = typer.Option(False, "--force"),
) -> None:
    dest = Path(to).resolve()
    tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    path = new_agent(dest, name, template=template, tools=tool_list,
                     memory_type=memory, memory_path=memory_path,
                     force=force, with_tests=with_tests)
    console.print(f"✔ Created agent config → [bold]{path}[/bold]")

@new_app.command("tool")
def new_tool_cmd(
    name: str = typer.Argument(..., help="Tool name"),
    template: str = typer.Option("python", "--template"),
    to: str = typer.Option(".", "--to"),
    with_tests: bool = typer.Option(False, "--with-tests"),
    force: bool = typer.Option(False, "--force"),
) -> None:
    dest = Path(to).resolve()
    path = new_tool(dest, name, template=template, force=force, with_tests=with_tests)
    console.print(f"✔ Created tool → [bold]{path}[/bold]")

app.add_typer(new_app, name="new")


# -------- template --------
@template_app.command("list")
def template_list() -> None:
    rows = list_builtin_templates()
    table = Table(title="Built-in Templates")
    table.add_column("Kind")
    table.add_column("Name")
    for t in rows:
        table.add_row(t.kind, t.name)
    console.print(table)

@template_app.command("apply")
def template_apply(
    template: str = typer.Argument(..., help="kind/name"),
    to: str = typer.Option(".", "--to"),
    force: bool = typer.Option(False, "--force"),
    name: Optional[str] = typer.Option(None, "--name"),
) -> None:
    try:
        kind, name_t = template.split("/", 1)
    except ValueError:
        console.print("[red]Use 'kind/name' (e.g., agent/basic)[/red]")
        raise typer.Exit(2)
    dest = Path(to).resolve()
    nm = name or "artifact"
    from .scaffold import apply_template_dir, slugify, pascal_case
    ctx = {
        "name": nm, "name_slug": slugify(nm), "class_name": pascal_case(nm),
        "project_name": nm, "project_slug": slugify(nm), "default_agent": "agent",
        "tools": [], "memory_type": "json", "memory_path": "./memory/agent.json",
    }
    apply_template_dir(kind, name_t, dest, ctx, force=force)
    console.print(f"✔ Applied template {template} to [bold]{dest}[/bold]")

@template_app.command("pull")
def template_pull(
    source: str = typer.Argument(..., help=".git repo or .zip URL"),
    to: str = typer.Option(".", "--to"),
    force: bool = typer.Option(False, "--force"),
) -> None:
    dest = Path(to).resolve()
    pull_template(source, dest, force=force)
    console.print(f"✔ Pulled template into [bold]{dest}/templates/third_party[/bold]")

app.add_typer(template_app, name="template")


# -------- tools --------
@tools_app.command("list")
def tools_list() -> None:
    tools = discover_tools()
    table = Table(title="Available Tools")
    table.add_column("Name")
    table.add_column("Class")
    for name, cls in tools.items():
        table.add_row(name, f"{cls.__module__}.{cls.__name__}")
    console.print(table)

@tools_app.command("info")
def tools_info(name: str = typer.Argument(...)) -> None:
    tools = discover_tools()
    if name not in tools:
        console.print(f"[red]Unknown tool:[/red] {name}")
        raise typer.Exit(2)
    cls = tools[name]
    desc = getattr(cls, "description", "")
    console.print(f"[bold]{name}[/bold] → {cls.__module__}.{cls.__name__}\n{desc}")

@tools_app.command("run")
def tools_run(
    name: str = typer.Argument(..., help="Tool name"),
    arg: List[str] = typer.Option([], "--arg", help="key=value (repeatable)"),
    json_out: bool = typer.Option(False, "--json", help="Emit raw JSON"),
) -> None:
    kwargs: Dict[str, object] = {}
    for pair in arg:
        if "=" not in pair:
            console.print(f"[yellow]Skipping malformed arg:[/yellow] {pair}")
            continue
        k, v = pair.split("=", 1)
        v = v.strip()
        if v.lower() in ("true", "false"):
            v = (v.lower() == "true")
        else:
            try:
                v = float(v) if "." in v else int(v)
            except ValueError:
                pass
        kwargs[k.strip()] = v
    try:
        tool = instantiate(name)
        result = tool.run(**kwargs)
    except Exception as e:
        console.print(f"[red]Tool error:[/red] {e}")
        raise typer.Exit(1)
    if json_out:
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        table = Table(title=f"{name} result")
        table.add_column("Key"); table.add_column("Value", overflow="fold")
        for k, v in result.items():
            table.add_row(str(k), json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v))
        console.print(table)

app.add_typer(tools_app, name="tools")


# -------- validate --------
@validate_app.command("file")
def validate_file(
    config: str = typer.Argument(..., help="Path to YAML"),
    show_effective: bool = typer.Option(False, "--show-effective", help="Show values after RC/env/CLI merges"),
    model: Optional[str] = typer.Option(None, "--model"),
    temperature: Optional[float] = typer.Option(None, "--temperature"),
    max_steps: Optional[int] = typer.Option(None, "--max-steps"),
) -> None:
    try:
        cfg: AgentikConfig = load_config(config)
    except SystemExit as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    overrides = {}
    if model is not None:
        overrides["llm.model"] = model
    if temperature is not None:
        overrides["llm.temperature"] = temperature
    if max_steps is not None:
        overrides["agent.loop.max_steps"] = max_steps
    eff = merge_precedence(cfg, overrides)
    console.print("[green]Config is valid.[/green]")
    if show_effective:
        console.print(json.dumps(eff.model_dump(), ensure_ascii=False, indent=2))

app.add_typer(validate_app, name="validate")


# -------- batch --------
@batch_app.command("run")
def batch_run(
    file: str = typer.Argument(..., help="CSV or JSONL file"),
    column: str = typer.Option("prompt", "--column", help="Prompt column (CSV) or JSON key (JSONL)"),
    out: str = typer.Option("results.jsonl", "--out", help="Write JSONL results here"),
    model: Optional[str] = typer.Option(None, "--model"),
    temperature: Optional[float] = typer.Option(None, "--temperature"),
) -> None:
    ensure_openrouter_key(required=True)
    client = OpenRouterClient()

    path = Path(file)
    if not path.exists():
        console.print(f"[red]Not found:[/red] {path}")
        raise typer.Exit(2)

    is_jsonl = path.suffix.lower() == ".jsonl"
    prompts: List[str] = []

    if is_jsonl:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if column not in obj:
                continue
            prompts.append(str(obj[column]))
    else:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if column not in reader.fieldnames:
                console.print(f"[red]CSV missing column:[/red] {column}")
                raise typer.Exit(2)
            for row in reader:
                prompts.append(str(row[column]))

    if not prompts:
        console.print("[yellow]No prompts found.[/yellow]")
        raise typer.Exit(1)

    outp = Path(out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    written = 0

    with outp.open("w", encoding="utf-8") as fout:
        for i, ptxt in enumerate(prompts, 1):
            try:
                resp = client.chat(
                    [{"role": "user", "content": ptxt}],
                    model=model or "openai/gpt-4o-mini",
                    temperature=temperature if temperature is not None else 0.2,
                )
                content = resp.get("content") or ""
                fout.write(json.dumps({"i": i, "input": ptxt, "output": content}, ensure_ascii=False) + "\n")
                written += 1
                if i % 10 == 0:
                    console.print(f"Processed: {i}/{len(prompts)}")
            except Exception as e:
                fout.write(json.dumps({"i": i, "input": ptxt, "error": str(e)}, ensure_ascii=False) + "\n")

    console.print(f"✔ Wrote [bold]{written}[/bold] results → {outp}")

app.add_typer(batch_app, name="batch")


# -------- memory --------
@memory_app.command("init")
def memory_init(
    type: str = typer.Option("json", "--type", help="dict|json"),
    path: Optional[str] = typer.Option("./memory/agentik.json", "--path"),
) -> None:
    mem = make_memory(type, path)
    if hasattr(mem, "remember"):
        mem.remember({"role": "system", "content": "memory initialized"})
    console.print(f"✔ Memory initialized: {type} ({path})")

@memory_app.command("recall")
def memory_recall(
    n: int = typer.Option(10, "--n"),
    config: Optional[str] = typer.Option(None, "--config", help="Read memory params from this config"),
) -> None:
    if config:
        cfg: AgentikConfig = load_config(config)
        mem = make_memory(cfg.memory.type, cfg.memory.path)
    else:
        mem = make_memory("json", "./memory/agentik.json")
    rows = mem.recall(n)
    console.print(json.dumps(rows, ensure_ascii=False, indent=2))

@memory_app.command("summarize")
def memory_summarize(
    n: int = typer.Option(20, "--n"),
    max_chars: int = typer.Option(1200, "--max-chars"),
    config: Optional[str] = typer.Option(None, "--config"),
) -> None:
    if config:
        cfg: AgentikConfig = load_config(config)
        mem = make_memory(cfg.memory.type, cfg.memory.path)
    else:
        mem = make_memory("json", "./memory/agentik.json")
    console.print(mem.summarize(n=n, max_chars=max_chars))

@memory_app.command("clear")
def memory_clear(
    config: Optional[str] = typer.Option(None, "--config"),
) -> None:
    if config:
        cfg: AgentikConfig = load_config(config)
        mem = make_memory(cfg.memory.type, cfg.memory.path)
    else:
        mem = make_memory("json", "./memory/agentik.json")
    mem.clear()
    console.print("✔ Memory cleared.")

@memory_app.command("path")
def memory_path(
    config: Optional[str] = typer.Option(None, "--config"),
) -> None:
    if config:
        cfg: AgentikConfig = load_config(config)
        console.print(f"{cfg.memory.type} → {cfg.memory.path}")
    else:
        console.print("./memory/agentik.json")

app.add_typer(memory_app, name="memory")


# -------- eval --------
@eval_app.command("run")
def eval_run(
    file: str = typer.Argument(..., help="JSONL with fields: prompt, expect_contains[] or expect_regex"),
    config: str = typer.Option(..., "--config", help="Agent config to use"),
    out: str = typer.Option("eval_results.jsonl", "--out"),
) -> None:
    cfg: AgentikConfig = load_config(config)
    ensure_openrouter_key(required=True)
    client = OpenRouterClient()
    from .agent import AgentRunner
    runner = AgentRunner(cfg, client)

    path = Path(file)
    if not path.exists():
        console.print(f"[red]Not found:[/red] {path}")
        raise typer.Exit(2)

    tests = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        tests.append(json.loads(line))

    outp = Path(out); outp.parent.mkdir(parents=True, exist_ok=True)
    passed = 0
    with outp.open("w", encoding="utf-8") as fout:
        for i, t in enumerate(tests, 1):
            prompt = t.get("prompt", "")
            contains = t.get("expect_contains") or []
            regex = t.get("expect_regex")
            result = runner.run(user_prompt=prompt, stream_final=False, save_transcript=None)
            text = result.final_text or ""
            ok = True
            reasons: List[str] = []
            for c in contains:
                if c not in text:
                    ok = False; reasons.append(f"missing substring: {c}")
            if regex:
                if not re.search(regex, text, re.I | re.S):
                    ok = False; reasons.append(f"regex no match: {regex}")
            fout.write(json.dumps({"i": i, "prompt": prompt, "ok": ok, "reasons": reasons, "output": text[:1200]}, ensure_ascii=False) + "\n")
            passed += 1 if ok else 0

    console.print(f"✔ Eval complete: {passed}/{len(tests)} passed → {outp}")

app.add_typer(eval_app, name="eval")


# -------- dev (watch) --------
@dev_app.command("watch")
def dev_watch(
    config: str = typer.Argument(..., help="Path to agent YAML config"),
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="Inline prompt; ignored if --prompt-file is used"),
    prompt_file: Optional[str] = typer.Option(None, "--prompt-file", help="Read prompt text from this file every run"),
    paths: List[str] = typer.Option(["."], "--path", help="Paths to watch (repeatable)"),
    include: List[str] = typer.Option(["**/*.py", "**/*.yml", "**/*.yaml", "**/*.json", "**/*.md", "templates/**", "tools/**"], "--include"),
    exclude: List[str] = typer.Option([], "--exclude"),
    interval: float = typer.Option(0.6, "--interval", help="Polling interval seconds"),
    debounce: float = typer.Option(0.5, "--debounce", help="Debounce seconds"),
    clear: bool = typer.Option(True, "--clear/--no-clear", help="Clear console before each run"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream final answer"),
    profile: Optional[str] = typer.Option("dev", "--profile", help="Profile to apply; default 'dev'"),
    save_transcripts: Optional[str] = typer.Option(None, "--save-transcripts", help="Directory to append JSONL transcripts with timestamp"),
    obs_max_chars: int = typer.Option(800, "--obs-max-chars", help="Max chars in observation previews"),
    no_initial_run: bool = typer.Option(False, "--no-initial-run", help="Wait for first change before running"),
    tag: List[str] = typer.Option(["dev"], "--tag", help="Tags to add to transcript meta"),
    note: Optional[str] = typer.Option(None, "--note", help="Note to add to transcript meta"),
) -> None:
    """
    Watch files and auto-rerun the agent on changes. Great for inner-loop development.
    """
    ensure_openrouter_key(required=True)
    overrides: Dict[str, object] = _builtin_profile_overrides(profile or "dev")
    cfg = merge_precedence(load_config(config), overrides)

    def _read_prompt() -> str:
        if prompt_file:
            p = Path(prompt_file)
            if not p.exists():
                console.print(f"[red]Prompt file not found:[/red] {p}")
                raise typer.Exit(2)
            return p.read_text(encoding="utf-8")
        if prompt:
            return prompt
        console.print("[red]No prompt provided.[/red] Use --prompt or --prompt-file.")
        raise typer.Exit(2)

    def _ts() -> str:
        return time.strftime("%Y%m%d-%H%M%S")

    from .agent import AgentRunner
    client = OpenRouterClient()
    runner = AgentRunner(cfg, client)

    def _run_once(reason: str) -> None:
        pr = _read_prompt()
        if clear:
            _clear_console()
        console.rule(f"[bold green]agentik dev watch[/bold green]  •  {reason}")
        console.print(
            f"[bold]Agent:[/bold] {cfg.agent.name} • "
            f"Model: [cyan]{cfg.llm.model}[/cyan] • Temp: {cfg.llm.temperature} • "
            f"Profile: [magenta]{profile or 'dev'}[/magenta]"
        )
        transcript_path: Optional[Path] = None
        if save_transcripts:
            d = Path(save_transcripts).resolve()
            d.mkdir(parents=True, exist_ok=True)
            transcript_path = d / f"run-{_ts()}.jsonl"
        try:
            result = runner.run(
                user_prompt=pr,
                stream_final=stream,
                save_transcript=transcript_path,
                run_meta={"profile": profile or "dev", "tags": tag, "note": note},
                obs_max_chars=obs_max_chars,
            )
            if stream:
                console.print("\n[dim](stream complete)[/dim]")
            else:
                console.print("\n[bold]Final:[/bold] " + (result.final_text or "(empty)"))

            st = result.stats or {}
            tokens = st.get("tokens", {})
            cost = st.get("cost_estimated_usd")
            console.print(
                f"[dim]Steps={result.steps} • tokens={tokens.get('total', 0)}"
                + (f" • ~${cost:.4f}" if cost is not None else "")
                + "[/dim]"
            )
            if transcript_path:
                console.print(f"📝 Saved transcript → [bold]{transcript_path}[/bold]")
        except Exception as e:
            console.print(f"[red]Run failed:[/red] {e}")

    # Initial run
    if not no_initial_run:
        _run_once("initial run")

    console.print(
        f"[dim]Watching: {', '.join(paths)}  |  include={include}  |  exclude={exclude}  "
        f"|  interval={interval}s  debounce={debounce}s[/dim]"
    )

    try:
        for changed in watch_for_changes(paths=paths, include=include, exclude=exclude, interval=interval, debounce=debounce):
            changed_list = sorted(str(p) for p in changed)
            console.print(f"[blue]Change detected in {len(changed_list)} file(s):[/blue]")
            for p in changed_list[:10]:
                console.print(f"  • {p}")
            if len(changed_list) > 10:
                console.print(f"  … and {len(changed_list) - 10} more")
            _run_once("file changes")
    except KeyboardInterrupt:
        console.print("[yellow]Stopped watching.[/yellow]")

app.add_typer(dev_app, name="dev")


# -------- config helpers --------
@config_app.command("path")
def config_path(
    global_scope: bool = typer.Option(False, "--global"),
    local_scope: bool = typer.Option(False, "--local"),
) -> None:
    if global_scope and local_scope:
        console.print("[red]Choose only one of --global or --local.[/red]")
        raise typer.Exit(2)
    scope = "global" if global_scope else "local"
    console.print(str(rc_path_for_write(scope)))

app.add_typer(config_app, name="config")


if __name__ == "__main__":
    app()
