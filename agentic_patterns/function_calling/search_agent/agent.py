from google.adk.agents import Agent
from google.adk.tools import google_search


root_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="search agent",
    instruction="""
    You are a helpful assistant that can use the following tools:
    - google_search
    """,
    tools=[google_search],
)
