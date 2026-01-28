import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from .logging_utils import log_event, log_session_state, logger

# Load the .env relative to the project root
load_dotenv(dotenv_path=Path(os.getcwd()) / ".env")

# In project .env set AGENT_APP_NAME, USER_ID, AGENT_ENV
# Derive DB naming from environment variables
APP_NAME = os.getenv("AGENT_APP_NAME", "noname_app")
DB_PATH = Path(os.getcwd()) / f"{APP_NAME}_sessions.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Singleton Session Service
session_service = DatabaseSessionService(db_url=DB_URL)


def build_user_message(text: str) -> dict:
    """
    Standardizes input for the ADK runner.
    1. Role: 'user' is mandatory for LiteLLM and multi-turn routing.
    2. Parts: Must be a list to allow for future multi-modal (image/file) expansion.
    3. Dict Format: More serializable for logging than raw class objects.
    Note:
    # Using the dictionary format is often more robust for the runner's internal mapping
    # later add support for other message types, such as images, files, etc.
    """"
    if not text or not text.strip():
        # Fail fast on invalid input before hitting the API
        raise ValueError("User input text cannot be empty.")

    return {"role": "user", "content": {"parts": [{"text": text}]}}


async def execute_agent_stream(app, input_text, initial_state=None, debug=False):
    """
    (Runner Utility) Executes an agent stream with logging and state inspection.
    Args:
        app: The ADK app to execute.
        input_text: The user input text to send to the agent.
        initial_state: The initial state to start the session with.
        debug: Whether to enable debug mode.
    Returns:
        The final response text.
    """
    if debug:
    runner = Runner(app=app, session_service=session_service)
    session_id = str(uuid.uuid4())
    user_id = os.getenv("USER_ID", "default_user")

    await session_service.create_session(
        app_name=app.name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state or {},
    )
    if debug:
        # 1. Inspect STARTING state
        curr_session = await session_service.get_session(app.name, user_id, session_id)
        log_session_state(curr_session.state, label="PRE-FLIGHT STATE")

    try:
        final_text_parts = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=build_user_message(input_text),
        ):
            if debug:
                await log_event(event)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text_parts.append(part.text)
            
    except Exception as e:
        logger.error(f"Error executing agent stream: {e}")
        raise e

    finally:
        if debug:
            # 2. Inspect FINAL state
            final_session = await session_service.get_session(app.name, user_id, session_id)
            log_session_state(final_session.state, label="POST-FLIGHT STATE")

    return "".join(final_text_parts) if final_text_parts else "(no final response text)"