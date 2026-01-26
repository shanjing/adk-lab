"""
Tour Guide Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from tools.config import AI_MODEL

# The Worker Agent
tour_guide = LlmAgent(
    name="tour_guide",
    model=AI_MODEL,
    description="A specialist in recommending tourist attractions",
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