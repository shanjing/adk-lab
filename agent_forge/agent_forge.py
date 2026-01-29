#!/usr/bin/env python3
"""
agent_forge.py: A multi-pattern scaffolding engine for ADK agentic projects.

Generates adk agentic pattern skeleton directory structure from a YAML or JSON spec.

Creates:
  - Project root (output_dir / project_name)
  - Pattern-specific agent packages (root_agent, sub_agents)
  - __init__.py and agent.py per component, .env from spec
  - main.py, check_env.py, tools/ (from src/)

Usage:
  python agent_forge.py -f project.yaml
  python agent_forge.py -f spec.json --output-dir ./builds
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import click

AGENT_FORGE_DIR = Path(__file__).resolve().parent
SRC_DIR = AGENT_FORGE_DIR / "src"

def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        raise SystemExit("YAML input requires PyYAML. Install with: pip install pyyaml") from None
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid YAML: expected a mapping, got {type(data).__name__}")
    return data

def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid JSON: expected an object, got {type(data).__name__}")
    return data


REQUIRED_KEYS = ("project_name", "root_agent", "sub_agents")
DEFAULTS = {
    "user_id": "Sam",
    "agent_env": "development",
    "output_dir": ".",
}


def load_spec(path: Path) -> dict:
    suf = path.suffix.lower()
    if suf in (".yaml", ".yml"):
        data = _load_yaml(path)
    elif suf == ".json":
        data = _load_json(path)
    else:
        raise SystemExit(f"Unsupported spec format: {suf!r}. Use .yaml, .yml, or .json.")
    for k in REQUIRED_KEYS:
        if k not in data:
            raise SystemExit(f"Missing required key in spec: {k!r}")
    sub = data["sub_agents"]
    if not isinstance(sub, (list, tuple)) or not sub:
        raise SystemExit("Spec 'sub_agents' must be a non-empty list.")
    return {**DEFAULTS, **data}


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _tree_lines(project_name: str, root_agent: str, sub_agents: list[str]) -> list[str]:
    """Build tree structure lines for the scaffolded project."""
    lines = [f"{project_name}/"]
    lines.append("├── .env")
    lines.append("├── main.py")
    lines.append("├── check_env.py")
    lines.append("├── tools/")
    lines.append("│   ├── __init__.py")
    lines.append("│   ├── config.py")
    lines.append("│   ├── logging_utils.py")
    lines.append("│   ├── runner_utils.py")
    lines.append("│   └── schemas.py")
    lines.append(f"└── {root_agent}/")
    lines.append("    ├── __init__.py")
    lines.append("    ├── agent.py")
    lines.append("    └── sub_agents/")
    lines.append("        ├── __init__.py")
    for i, name in enumerate(sub_agents):
        last = i == len(sub_agents) - 1
        branch = "└──" if last else "├──"
        lines.append(f"        {branch} {name}/")
        if last:
            lines.append("            ├── __init__.py")
            lines.append("            └── agent.py")
        else:
            lines.append("        │   ├── __init__.py")
            lines.append("        │   └── agent.py")
    return lines


def _file_summary(project_name: str, root_agent: str, sub_agents: list[str]) -> list[tuple[str, str]]:
    """List (path, function) for each scaffolded file."""
    base = f"{project_name}"
    entries: list[tuple[str, str]] = [
        (f"{base}/.env", "Env vars: AGENT_APP_NAME, USER_ID, ROOT_AGENT, SUB_AGENTS, etc."),
        (f"{base}/main.py", "CLI entrypoint; run agent with --input, --debug, --thoughts."),
        (f"{base}/check_env.py", "Sanity check: root/sub-agent names, imports, config."),
        (f"{base}/tools/__init__.py", "Package marker for tools."),
        (f"{base}/tools/config.py", "AI_MODEL, ROOT_AGENT, SUB_AGENTS from .env; model selection."),
        (f"{base}/tools/logging_utils.py", "setup_logging, log_event, log_session_state, THEME."),
        (f"{base}/tools/runner_utils.py", "execute_agent_stream, build_user_message, APP_NAME, session."),
        (f"{base}/tools/schemas.py", "Shared Pydantic schemas (placeholder)."),
        (f"{base}/{root_agent}/__init__.py", "Exports root_agent."),
        (f"{base}/{root_agent}/agent.py", "Root LlmAgent + AgentTools for sub-agents."),
        (f"{base}/{root_agent}/sub_agents/__init__.py", "Exports sub-agents."),
    ]
    for name in sub_agents:
        entries.append((f"{base}/{root_agent}/sub_agents/{name}/__init__.py", f"Exports {name}."))
        entries.append((f"{base}/{root_agent}/sub_agents/{name}/agent.py", f"Sub-agent {name} (LlmAgent placeholder)."))
    return entries


def _print_success_report(root: Path, spec: dict) -> None:
    """Print tree, file summary, and cd + check_env hint."""
    project_name = spec["project_name"]
    root_agent = spec["root_agent"]
    sub_agents = spec["sub_agents"]

    click.echo("\n--- Project tree ---")
    for line in _tree_lines(project_name, root_agent, sub_agents):
        click.echo(line)

    click.echo("\n--- File summary ---")
    for path, fn in _file_summary(project_name, root_agent, sub_agents):
        click.echo(f"  {path} [{fn}]")

    click.echo("\n--- Next steps ---")
    project_root = root.resolve()
    click.echo(f"  cd {project_root}")
    click.echo("  python check_env.py")


def copy_core_assets(project_root: Path) -> None:
    """Copy src/main.py, src/check_env.py, and src/tools/ into project root."""
    if not SRC_DIR.is_dir():
        raise SystemExit(f"Source directory not found: {SRC_DIR}")
    for name in ("main.py", "check_env.py"):
        src = SRC_DIR / name
        if not src.is_file():
            raise SystemExit(f"Source file not found: {src}")
        shutil.copy2(src, project_root / name)
    tools_src = SRC_DIR / "tools"
    tools_dst = project_root / "tools"
    if not tools_src.is_dir():
        raise SystemExit(f"Source directory not found: {tools_src}")
    if tools_dst.exists():
        shutil.rmtree(tools_dst)
    shutil.copytree(tools_src, tools_dst)


def write(p: Path, content: str) -> None:
    ensure_dir(p.parent)
    p.write_text(content, encoding="utf-8")


def root_init(root_agent: str) -> str:
    return f'''from .agent import root_agent

__all__ = ["root_agent"]
'''


def root_agent_py(spec: dict) -> str:
    root = spec["root_agent"]
    subs = spec["sub_agents"]
    sub_imports = "\n".join(f"from .sub_agents.{s} import {s}" for s in subs)
    tool_list = ",\n        ".join(f"AgentTool(agent={s})" for s in subs)
    tools_desc = "\n    ".join(f"- {s}: ..." for s in subs)
    return f'''"""
{root} – supervisor/root agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

from tools.config import AI_MODEL, INCLUDE_THOUGHTS
{sub_imports}

# For consistency, python variable and agent name are identical
root_agent = LlmAgent(
    name="{root}",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=1000,
    ),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=INCLUDE_THOUGHTS)
    ),
    instruction="""
    You are a coordinator agent. Delegate user requests to the appropriate specialist.
    You are given the following tools:
    {tools_desc}
    Use them as needed and synthesize responses for the user.
    """,
    tools=[
        {tool_list}
    ],
)
'''


def sub_agents_init(sub_agents: list[str]) -> str:
    imports = "\n".join(f"from .{s} import {s}" for s in sub_agents)
    all_ = ", ".join(f'"{s}"' for s in sub_agents)
    return f'''{imports}

__all__ = [{all_}]
'''


def sub_agent_init(name: str) -> str:
    return f'''from .agent import {name}

__all__ = ["{name}"]
'''


def sub_agent_py(name: str) -> str:
    return f'''"""
{name} – sub-agent (placeholder).
"""

from google.adk.agents import LlmAgent

from tools.config import AI_MODEL

# For consistency, python variable and agent name are identical
{name} = LlmAgent(
    name="{name}",
    model=AI_MODEL,
    description="A specialist agent.",
    instruction="""
    You are a placeholder for the {name} agent.
    Currently under construction.
    Acknowledge the user's request and state that you cannot process it yet.
    """,
)
'''


def env_content(spec: dict) -> str:
    proj = spec["project_name"]
    root = spec["root_agent"]
    subs = ",".join(spec["sub_agents"])
    uid = spec.get("user_id", DEFAULTS["user_id"])
    env = spec.get("agent_env", DEFAULTS["agent_env"])
    return f'''AGENT_APP_NAME="{proj}"
USER_ID="{uid}"
AGENT_ENV="{env}"
ROOT_AGENT="{root}"
SUB_AGENTS="{subs}"
'''


def run(spec_path: Path, output_dir_override: Path | None) -> Path:
    spec = load_spec(spec_path)
    out = Path(spec["output_dir"]).resolve()
    if output_dir_override is not None:
        out = output_dir_override.resolve()
    project_name = spec["project_name"]
    root_agent = spec["root_agent"]
    sub_agents = spec["sub_agents"]

    root = out / project_name
    if root.exists():
        raise SystemExit(
            f"Project root already exists: {root}. "
            "Use a different --output-dir or project_name in the spec."
        )

    # .env
    write(root / ".env", env_content(spec))

    # root_agent/
    ra = root / root_agent
    write(ra / "__init__.py", root_init(root_agent))
    write(ra / "agent.py", root_agent_py(spec))

    # root_agent/sub_agents/
    sa = ra / "sub_agents"
    write(sa / "__init__.py", sub_agents_init(sub_agents))
    for name in sub_agents:
        subdir = sa / name
        write(subdir / "__init__.py", sub_agent_init(name))
        write(subdir / "agent.py", sub_agent_py(name))

    copy_core_assets(root)
    return root, spec


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Scaffold an ADK agent from a YAML or JSON spec.",
)
@click.option(
    "-f",
    "--file",
    "spec_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to YAML or JSON spec (project_name, root_agent, sub_agents, etc.).",
)
@click.option(
    "--output-dir",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Override output_dir from spec. Project is created at <output-dir>/<project_name>.",
)
def main(spec_path: Path, output_dir: Path | None) -> None:
    if not spec_path.is_file():
        click.echo(f"Not a file: {spec_path}", err=True)
        sys.exit(1)
    root, spec = run(spec_path, output_dir)
    click.echo(f"Created project at: {root}")
    _print_success_report(root, spec)


if __name__ == "__main__":
    main()
