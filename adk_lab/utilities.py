from google.genai import types
from typing import Iterable


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
