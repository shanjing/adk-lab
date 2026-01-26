"""
The root agent - the supervisor that has to review/approve
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool


from tools.config import AI_MODEL
from tools.travel_policy import check_travel_policy
from .sub_agents.travel_planner.agent import travel_agent # Correct import path

# The root agent - a supervisor that has to review/approve
root_agent = LlmAgent(
    name="supervisor_guard",
    model=AI_MODEL,
    tools=[
        check_travel_policy,
        AgentTool(agent=travel_agent) # ADK handles the handoff now
    ],
    instruction="Check travel policy. If allowed, use the travel_planner tool to create an itinerary."
)