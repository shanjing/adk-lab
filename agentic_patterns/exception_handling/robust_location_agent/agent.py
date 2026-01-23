import os
import uuid
import asyncio
from dotenv import load_dotenv
from pathlib import Path

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from google.genai import types

from google.adk.tools import google_maps_grounding, google_search

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(funcName)s %(lineno)d | %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Env & Model
# --------------------------------------------------
load_dotenv()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")

db_path = Path(__file__).resolve().parent / "exception_handling.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
db_path.touch(exist_ok=True)

logger.info("Using SQLite database at: %s", db_path)

# --------------------------------------------------
# Agent 1: Primary handler (precise lookup)
# --------------------------------------------------
primary_handler = LlmAgent(
    name="primary_handler",
    model=AI_MODEL,
    instruction=(
        "Your job is to retrieve precise location information.\n"
        "\n"
        "Steps:\n"
        "1. Attempt to use `google_maps_grounding` with the user's address.\n"
        "2. If the tool succeeds, store the result in state['location_result'].\n"
        "3. If the tools succeeds, update set :state['location_provided_by'] to 'primary_handler'\n"
        "4. If the tool fails or returns unusable data, set:\n"
        "   state['primary_location_failed'] = True\n"
        "\n"
        "Do NOT fabricate results."
    ),
    tools=[google_maps_grounding],
)

# --------------------------------------------------
# Agent 2: Fallback handler (general area lookup)
# --------------------------------------------------
fallback_handler = LlmAgent(
    name="fallback_handler",
    model=AI_MODEL,
    instruction=(
        "Check state['primary_location_failed'].\n"
        "\n"
        "- If it is True:\n"
        "  1. Extract the city or general area from the user's original query.\n"
        "  2. Use `google_search` to look up the general area.\n"
        "  3. Store the result in state['location_result'].\n"
        "  4. If the tools succeeds, update set :state['location_provided_by'] to 'fallback_handler'\n"
        "\n"
        "- If it is not True, update state['primary_handler:status'to 'Successful!'"
    ),
    tools=[google_search],
)

# --------------------------------------------------
# Agent 3: Final response presenter
# --------------------------------------------------
response_agent = LlmAgent(
    name="response_agent",
    model=AI_MODEL,
    instruction=(
        "Review state['location_result'].\n"
        "\n"
        "- If it exists, present the information clearly ,concisely and" 
        "state the source of the information.\n"
        "- If it does not exist or is empty, apologize and state that the "
        "location could not be retrieved."
    ),
)

# --------------------------------------------------
# Sequential Agent
# --------------------------------------------------
root_agent = SequentialAgent(
    name="robust_location_agent",
    sub_agents=[
        primary_handler,
        fallback_handler,
        response_agent,
    ],
)
