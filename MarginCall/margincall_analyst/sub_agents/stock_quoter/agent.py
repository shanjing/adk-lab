"""
Stock Quoter Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types
from tools.config import AI_MODEL, INCLUDE_THOUGHTS

# For consistency, python variable and agent name are identical
stock_quoter = LlmAgent(
    name="stock_quoter",
    model=AI_MODEL,
    description="A specialist in getting real time stock quote",
    instruction="""
    You are a placeholder for the Stock Quoter agent.
    Currently, you are under construction. 
    Acknowledge the user's request and state that you cannot process stock quotes yet.
    """,
)
