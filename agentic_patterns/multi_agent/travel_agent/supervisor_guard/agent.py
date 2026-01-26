"""
The root agent - the supervisor that has to review/approve
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool


from tools.config import AI_MODEL
from tools.travel_policy import check_travel_policy
from .sub_agents.travel_planner.agent import travel_planner
from .sub_agents.tour_guide.agent import tour_guide


root_agent = LlmAgent(
    name="supervisor_guard",
    model=AI_MODEL,
    tools=[
        check_travel_policy,
        AgentTool(agent=tour_guide),
        AgentTool(agent=travel_planner),
    ],
    instruction="""
    You are a strict Gatekeeper and a tourist guide if the user is allowed to travel to the given city.
    1. EXTRACT 'user_id' and 'target_city' from the user input.
    2. Greet the user by name, say something to make him/her feel welcome.
    3. CALL 'check_travel_policy' with ONLY the user_id and target_city.
    3. IF 'allowed' is True:
       - Inform the user the trip is approved.
       - IMMEDIATELY call the 'travel_planner' tool.
       - Tell the travel_planner the user_id and target_city.
    4. IF 'allowed' is False:
       - Stop. 
       - Inform the user they have already visited this city.
       - The policy disallows multiple trips to the same city.
    5. Once the travel_planner books the flight and hotel:
       - Tell the user the itinerary.
       - Tell the user the weather forecast for the city.
       - Call the 'tour_guide' tool to recommend one tourist attraction and its location in google maps.

    DO NOT explain what you cannot do (like booking).
    """,
)
