"""
stock_analyst – supervisor/root agent (MarginCall-style).
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

from tools.config import AI_MODEL, INCLUDE_THOUGHTS
from .sub_agents.price_fetcher import price_fetcher
from .sub_agents.news_fetcher import news_fetcher
from .sub_agents.financials_fetcher import financials_fetcher
from .sub_agents.technicals_fetcher import technicals_fetcher
from .sub_agents.report_synthesizer import report_synthesizer

# For consistency, python variable and agent name are identical
root_agent = LlmAgent(
    name="stock_analyst",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=1000,
    ),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=INCLUDE_THOUGHTS)
    ),
    instruction="""
    You are a coordinator agent. Delegate user requests to the appropriate specialist.
    You are given the following tools:
    - price_fetcher: ...
    - news_fetcher: ...
    - financials_fetcher: ...
    - technicals_fetcher: ...
    - report_synthesizer: ...
    Use them as needed and synthesize responses for the user.
    """,
    tools=[
        AgentTool(agent=price_fetcher),
        AgentTool(agent=news_fetcher),
        AgentTool(agent=financials_fetcher),
        AgentTool(agent=technicals_fetcher),
        AgentTool(agent=report_synthesizer)
    ],
)
