"""
Margin Call Analyst Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

from tools.config import AI_MODEL, INCLUDE_THOUGHTS
from sub_agents.stock_quoter import stock_quoter
from sub_agents.market_whisper import market_whisper
from sub_agents.brilliant_accountant import brilliant_accountant

# For consistency, python variable and agent name are identical
root_agent = LlmAgent(
    name="margincall_analyst",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=1000,
    ),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=INCLUDE_THOUGHTS)
    ),
    instruction="""
    You are a senior stock analyst.
    You will be given a stock symbol or derive a stock symbol from the user's request.
    You will provide the latest financial summary of the stock by that stock symbol.
    These summaries can include (but not limited to) the following:
    - Latest stock price
    - Latest market news
    - Latest financial statements
    - Latest financial forecasts
    You are given the following tools:
    - stock_quoter: to get the latest stock price
    - market_whisper: to get the latest market news
    - brilliant_accountant: to analyze the financial statements and forecasts
    """,
    tools=[
        AgentTool(agent=stock_quoter),
        AgentTool(agent=market_whisper),
        AgentTool(agent=brilliant_accountant)
        ],
)