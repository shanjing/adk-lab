import asyncio
import sys
import os
import click

from google.adk.apps.app import App

from tools.config import AI_MODEL
from tools.logging_utils import setup_logging, THEME
from tools.runner_utils import execute_agent_stream, APP_NAME

# Explicitly import the agent for this specific project
# Note: root_agent is a hard requirement for the ADK UI to work properly.
# We use variable root_agent as the manager agent for all single and sub-agents.
from supervisor_guard.agent import root_agent 

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """SRE-Grade CLI for ADK Agents."""
    pass

@cli.command("run")
@click.option(
    "--input", "-i",
    "input_text",
    help="Input text for the agent. If omitted, read from stdin.",
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    default=False,
    help="Enable SRE event tracing and state inspection.",
)
def run_command(input_text: str | None, debug: bool) -> None:
    """Run the project's dedicated agent."""
    
    # Pull model from env AI_MODEL
    target_model = AI_MODEL

    setup_logging(debug=debug, model_name=target_model)

    # 2. Handle Input (CLI or Stdin pipe)
    if input_text is None:
        if not sys.stdin.isatty():
            input_text = sys.stdin.read().strip()
        else:
            click.secho("Error: No input provided. Use --input or pipe text.", **THEME["err"])
            return

    # 3. Setup the App Container
    # We use APP_NAME from runner_utils (derived from .env)
    app = App(name=APP_NAME, root_agent=root_agent)

    # 4. Define Business Context (Initial State)
    initial_state = {
        "root_agent": "supervisor_guard",
        "sub_agent": "travel_planner",
        "application": APP_NAME,
        "environment": os.getenv("AGENT_ENV", "development"),
    }

    # 5. Execution with Global Exception Guard
    try:
        final_text = asyncio.run(
            execute_agent_stream(app, input_text, initial_state, debug)
        )
        # Final output for the user
        click.echo(f"\n{final_text}")

    except ValueError as ve:
        click.secho(f"\n[Validation Error]: {ve}", **THEME["err"])
        sys.exit(1)
    except Exception as e:
        click.secho(f"\n[System Failure]: {e}", **THEME["err"])
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    cli()