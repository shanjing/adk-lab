"""
The root agent - the supervisor that has to review/approve
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

from tools.config import AI_MODEL, INCLUDE_THOUGHTS
from tools.travel_policy import check_travel_policy
from .sub_agents.travel_planner.agent import travel_planner
from .sub_agents.tour_guide.agent import tour_guide


#tour_guide_tool = AgentTool(agent=tour_guide)
#tour_guide_tool.description = "Call this to handle travel requests. Pass the user's query in the 'request' field."

root_agent = LlmAgent(
    name="supervisor_guard",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=1000,
    ),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=INCLUDE_THOUGHTS)
    ),
    tools=[
        check_travel_policy,
        AgentTool(agent=travel_planner),
        AgentTool(agent=tour_guide),
    ],
    instruction="""
    You are a strict Gatekeeper and a tourist guide.
    1. EXTRACT 'user_id' and 'target_city' from the user input.
    2. CALL 'check_travel_policy' with ONLY the user_id and target_city.
    3. IF 'allowed' is True:
       - Inform the user the trip is approved.
       - IMMEDIATELY call the 'travel_planner' tool.
       - Tell the travel_planner the user_id and to_city = target_city.
    4. IF 'allowed' is False:
       - Stop. 
       - Inform the user they have already visited this city.
       - The policy disallows multiple trips to the same city.
    5. Once the travel_planner books the flight and hotel:
       - Tell the user the itinerary.
       - Tell the user the weather forecast for the city = to_city.
       - Call the 'tour_guide' tool to recommend one tourist attraction and its google maps location.

    """,
)
