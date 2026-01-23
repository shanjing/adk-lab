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
robust_location_agent = SequentialAgent(
    name="robust_location_agent",
    sub_agents=[
        primary_handler,
        fallback_handler,
        response_agent,
    ],
)

# --------------------------------------------------
# main(): Runner execution
# --------------------------------------------------
async def main() -> None:
    session_service = SqliteSessionService(db_path=str(db_path))
    app = App(name="location_app", root_agent=robust_location_agent)
    runner = Runner(app=app, session_service=session_service)

    user_id = "user-2"
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name="location_app",
        user_id=user_id,
        session_id=session_id,
        state={"Introduction": "This is a test for location_app."}
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text="Find the exact location of 1600 Amphitheatre Parkway, Mountain View, CA")]
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        current_session = await session_service.get_session(
            app_name="location_app",
            user_id=user_id,
            session_id=session_id,
        )
        logger.info("The current session.state is:")
        logger.info(current_session.state)

        logger.info("The event is:")
        logger.info(event.model_dump_json(indent=2))

        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(
                part.text for part in event.content.parts if part.text
            )
            logger.info(final_text)



if __name__ == "__main__":
    asyncio.run(main())
