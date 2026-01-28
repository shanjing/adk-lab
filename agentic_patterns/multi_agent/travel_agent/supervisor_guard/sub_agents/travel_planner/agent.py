"""
Travel Planner Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from tools.config import AI_MODEL, INCLUDE_THOUGHTS
from tools.travel_apps import get_5_day_weather, search_flights, search_hotels
from tools.travel_policy import record_visit
from supervisor_guard.sub_agents.tour_guide.agent import tour_guide

# The Worker Agent
travel_planner = LlmAgent(
    name="travel_planner",
    model=AI_MODEL,
    description="A specialist in booking flights and checking weather.",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=INCLUDE_THOUGHTS)
    ),
    tools=[
        get_5_day_weather, 
        search_flights, 
        search_hotels,
        record_visit,
    ],
    instruction=""" You are a travel planning specialist.
        Your goal is to provide a comprehensive itinerary including weather and flights.
        After you successfully book both a flight and a hotel, 
        - call 'record_visit' with the user_id and target_city to persist the trip.
        """,
)