"""
Travel Planner Agent
"""
from google.adk.agents import LlmAgent
from tools.config import AI_MODEL
from tools.travel_apps import get_5_day_weather, search_flights, search_hotels

# The Worker Agent
travel_agent = LlmAgent(
    name="travel_planner",
    model=AI_MODEL,
    description="A helpful travel planner.",
    tools=[get_5_day_weather, search_flights, search_hotels],
    instruction=(
        "You are a Travel Planning Worker.\n"
        "The Supervisor has already approved this trip.\n"
        "Plan the trip using available tools (weather, flights, hotels).\n"
        "Provide a concise itinerary."
    ),
)