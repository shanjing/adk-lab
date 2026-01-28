"""
Brilliant Accountant Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from tools.config import AI_MODEL, INCLUDE_THOUGHTS

# For consistency, python variable and agent name are identical
brilliant_accountant = LlmAgent(
    name="brilliant_accountant",
    model=AI_MODEL,
    description="A specialist in analyzing financial statements",
    instruction="""
    You are a placeholder for the Brilliant Accountant agent.
    Currently, you are under construction. 
    Acknowledge the user's request and state that you cannot process financial statements yet.
    """,
)