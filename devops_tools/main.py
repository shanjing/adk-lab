from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

import click
from google.adk.apps.app import App
from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from devops_tools.common.utilities import dump_state, dump_event

logging.basicConfig(level=logging.INFO)


def _agents_root() -> Path:
    return Path(__file__).resolve().parent


def _agent_loader() -> AgentLoader:
    return AgentLoader(str(_agents_root()))


def _db_url() -> str:
    db_path = _agents_root() / "devops_tools_data.db"
    return f"sqlite+aiosqlite:///{db_path}"


def _session_service() -> DatabaseSessionService:
    return DatabaseSessionService(_db_url())


def _build_user_message(text: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=text)])


def _extract_final_text_from_event(event) -> str:
    if event.is_final_response() and event.content and event.content.parts:
        return "".join(part.text for part in event.content.parts if part.text)
    return ""


async def run_agent(agent_name: str, input_text: str, debug: bool) -> str:
    loader = _agent_loader()
    agent_or_app = loader.load_agent(agent_name)

    app = (
        agent_or_app
        if isinstance(agent_or_app, App)
        else App(name=agent_name, root_agent=agent_or_app)
    )
    session_service = _session_service()
    runner = Runner(app=app, session_service=session_service)

    session_id = str(uuid.uuid4())
    user_id = "local-user"
    user_message = _build_user_message(input_text)
    initial_state = {"user_name": "John Doe", "application": "devops_tools"}

    await session_service.create_session(
        app_name=app.name, 
        user_id=user_id, 
        session_id=session_id, 
        state=initial_state
    )
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        if debug:
            await dump_event(event)
        final_text = _extract_final_text_from_event(event) or final_text

    if not final_text:
        final_text = "(no final response text)"

    if debug:
        await dump_state(
            session_service,
            app.name,
            user_id,
            session_id,
        )

    return final_text


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Run ADK agents from the devops_tools directory."""


@cli.command("list")
def list_agents() -> None:
    """List available agents."""
    loader = _agent_loader()
    for name in loader.list_agents():
        click.echo(name)


@cli.command("run")
@click.option(
    "--agent",
    "agent_name",
    required=True,
    help="Agent name (directory under devops_tools).",
)
@click.option(
    "--input",
    "input_text",
    help="Input text for the agent. If omitted, read from stdin.",
)
@click.option(
    "--debug",
    "debug",
    default=False,
    help="Enable debug mode.",
)
def run_command(agent_name: str, input_text: str | None, debug: bool) -> None:
    """Run a specific agent."""
    if input_text is None:
        input_text = click.get_text_stream("stdin").read().strip()
    if not input_text:
        raise click.ClickException("Input text is required.")

    final_text = asyncio.run(run_agent(agent_name, input_text, debug))
    click.echo(final_text)


if __name__ == "__main__":
    cli()
