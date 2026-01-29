"""
news_fetcher – sub-agent (placeholder).
"""

from google.adk.agents import LlmAgent

from tools.config import AI_MODEL

# For consistency, python variable and agent name are identical
news_fetcher = LlmAgent(
    name="news_fetcher",
    model=AI_MODEL,
    description="A specialist agent.",
    instruction="""
    You are a placeholder for the news_fetcher agent.
    Currently under construction.
    Acknowledge the user's request and state that you cannot process it yet.
    """,
)
