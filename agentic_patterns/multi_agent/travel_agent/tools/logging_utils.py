import logging
import json
import sys
import click
import google.adk
import litellm

# Theme for consistent cross-repo observability
THEME = {
    "thought": {"fg": "cyan", "italic": True},
    "call": {"fg": "yellow", "bold": True},
    "res": {"fg": "green"},
    "err": {"fg": "red", "bold": True}
}

# Global Logger for this module
logger = logging.getLogger(__name__)

def setup_logging(debug: bool = False, model_name: str = "unknown"):
    """ADK logging configuration with version and model tracking."""
    log_level = logging.DEBUG if debug else logging.INFO
    
    # base station for all logging
    logging.basicConfig(
        level=log_level,
        format="%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
        stream=sys.stdout,
        force=True,
    )

    adk_ver = getattr(google.adk, "__version__", "unknown")
    litellm_ver = getattr(litellm, "__version__", "unknown")

    # --- STARTUP METADATA ---
    # This ensures every log file/stream starts with the technical context
    logger.info("="*50)
    logger.info(f"SYSTEM STARTUP | Model: {model_name}")
    logger.info(f"ADK Version: {adk_ver} | LiteLLM: {litellm_ver}")
    logger.info("="*50)

    # Mute noisy internal ADK/SQL logic
    silence = logging.DEBUG if debug else logging.WARNING
    logging.getLogger("google.adk").setLevel(silence)
    logging.getLogger("litellm").setLevel(silence)

    # Mute the specific warning about non-text parts in responses
    logging.getLogger("google.genai.types").setLevel(logging.ERROR)

    # Mute noisy internal SQL logic
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
    
    # Mute the underlying async driver (aiosqlite)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)

    # 'core.py' noise from aiosqlite
    logging.getLogger("sqlite3").setLevel(logging.WARNING)

async def log_event(event):
    """Processes ADK events for the CLI trace."""
    if hasattr(event, 'thought') and event.thought:
        click.secho(f"\n[Thought]: {event.thought}", **THEME["thought"])

    calls = event.get_function_calls()
    if calls:
        for call in calls:
            click.secho(f"  ➜ [Tool Call]: {call.name}", **THEME["call"])
            click.secho(f"    [Arguments]: {call.args}", fg="yellow")

    responses = event.get_function_responses()
    if responses:
        for resp in responses:
            click.secho(f"  ✔ [Tool Result]: {resp.name} -> {resp.response}", **THEME["res"])

    if hasattr(event, 'error') and event.error:
        click.secho(f"  ✘ [Error]: {event.error}", **THEME["err"])


def log_session_state(state: dict, label="CURRENT STATE"):
    """
    Diplays session state in a formatted way.
    """
    if state:
        state_json = json.dumps(state, indent=2)
        click.secho(f"\n--- {label} ---", fg="magenta", bold=True)
        click.secho(state_json, fg="magenta")