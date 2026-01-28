"""
Tour Guide Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from tools.config import AI_MODEL, INCLUDE_THOUGHTS

# The Worker Agent
tour_guide = LlmAgent(
    name="tour_guide",
    model=AI_MODEL,
    description="A tourist attractions agent",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=INCLUDE_THOUGHTS)
    ),
    tools=[
        google_search,
    ],
    instruction=(
        """
        You are a tourist guide for the given city.
        Use google_search to recommend one attractive place and its location in google maps.
        """
    )
)