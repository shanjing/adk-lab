import asyncio
import sys
import os
import click

from google.adk.apps.app import App
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

from tools.config import AI_MODEL, INCLUDE_THOUGHTS, LOCAL_LLM, ROOT_AGENT, SUB_AGENTS
from tools.logging_utils import setup_logging, THEME
from tools.runner_utils import execute_agent_stream, APP_NAME

# We use variable root_agent as the manager agent for all single and sub-agents.
from margincall_analyst.agent import root_agent
from margincall_analyst.sub_agents.stock_quoter.agent import stock_quoter
from margincall_analyst.sub_agents.market_whisper.agent import market_whisper
from margincall_analyst.sub_agent.brilliant_accountant.agent import brilliant_accountant

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """CLI for ADK Agents."""
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
    help="Enable event tracing and state inspection.",
)
@click.option(
    "--thoughts", "-t", "show_thoughts",
    is_flag=True, help="Show agent's inner reasoning."
)
@click.option(
    "--stock", "-s",
    "stock_symbol",
    help="Optional stock symbol to analyze.",
    default=None,
)
def run_command(input_text: str | None, debug: bool, show_thoughts: bool = False) -> None:
    """Run the project's dedicated agent."""
    
    # Pull model from env AI_MODEL
    target_model = AI_MODEL

    # if debug is on, show_thoughts is on
    include_thoughts = show_thoughts or (debug and INCLUDE_THOUGHTS)
    # Update thinking_config for all agents (root and sub-agents) via planner
    agents_to_update = [root_agent, stock_quoter, market_whisper, brilliant_accountant]
    for agent in agents_to_update:
        if agent.planner and isinstance(agent.planner, BuiltInPlanner):
            agent.planner.thinking_config = types.ThinkingConfig(include_thoughts=include_thoughts)

    # Log models' events and state
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
        "root_agent": ROOT_AGENT,
        "sub_agent": SUB_AGENTS,
        "application": APP_NAME,
        "environment": os.getenv("AGENT_ENV", "development"),
        "model_name": target_model,
        "local_llm": LOCAL_LLM,
        "include_thoughts": include_thoughts,
        "stock_symbol": stock_symbol,
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