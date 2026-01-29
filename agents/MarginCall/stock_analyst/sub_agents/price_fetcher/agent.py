"""
price_fetcher – sub-agent (placeholder).
"""

from google.adk.agents import LlmAgent

from tools.config import AI_MODEL

# For consistency, python variable and agent name are identical
price_fetcher = LlmAgent(
    name="price_fetcher",
    model=AI_MODEL,
    description="A specialist agent.",
    instruction="""
    You are a placeholder for the price_fetcher agent.
    Currently under construction.
    Acknowledge the user's request and state that you cannot process it yet.
    """,
)
