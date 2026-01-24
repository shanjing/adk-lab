import json
from google.genai import types
from typing import Iterable, List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d | %(funcName)s | %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)


async def dump_state(
    session_service, app_name, user_id, session_id, label="Current State"
):
    """Display the current session state in a formatted way."""
    try:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        # Format the output with clear sections
        logger.info(f"\n{'-' * 10} {label} {'-' * 10}")
        logger.info(f"State: {json.dumps(session.state, indent=2)}")
        logger.info("-" * (22 + len(label)))
    except Exception as e:
        logger.error(f"Error displaying state: {e}")


async def dump_event(event):
    """Display the event in a formatted way."""
    logger.info(f"{'=' * 22} Event {'=' * 22}")
    logger.info(f"{'Event ID':<13}: {event.id}")
    logger.info(f"{'Author':<13}: {event.author}")
    logger.info(
        "Event Content:\n"
        f"{json.dumps(event.content, indent=2, default=str)}"
    )
    logger.info("=" * 51)

    # Check for final response after specific parts
    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            logger.info("----------AGENT RESPONSE----------")
            logger.info(f"{final_response}")
        else:
            logger.info(
                f"==> Final Agent Response: [No text content in final event]"
            )

    return final_response

def show_agent_result(events: Iterable) -> str:
    """
    Extract final text from ADK events.
    Safe for streaming and non-streaming runs.
    """
    for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                return "".join(
                    p.text for p in event.content.parts if p.text
                )
    return ""


def reconstruct_state(event_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Replays a list of event logs to reconstruct the final session state.
    Args:
        event_log: A list of dictionary events (e.g., from JSON logs or SQLite).
    Returns:
        A dictionary representing the final aggregated state of the session.
    """
    # Start with an empty Blackboard
    current_state: Dict[str, Any] = {}
    
    for event in event_log:
        # Check if this event has a state change.
        # Logic handles both flat events and nested payload structures.
        delta: Dict[str, Any] = (
            event.get('state_delta') or 
            event.get('payload', {}).get('state_delta')
        )
        
        if delta:
            # Merge the delta into the current state
            current_state.update(delta)
            
    return current_state