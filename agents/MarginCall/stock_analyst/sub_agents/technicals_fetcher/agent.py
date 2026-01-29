"""
technicals_fetcher – sub-agent that fetches technical indicators for a stock
"""

from google.adk.agents import LlmAgent

from tools.config import AI_MODEL
from tools.fetch_technical_indicators import fetch_technical_indicators

# For consistency, python variable and agent name are identical
technicals_fetcher = LlmAgent(
    name="technicals_fetcher",
    model=AI_MODEL,
    description="A technicals fetcher agent",
    instruction="""
    You are a technicals fetcher agent.
    You will be given a stock symbol.
    Use the 'fetch_technical_indicators' tool to fetch the technical indicators.
    Return the technical indicators in the 'technical_indicators' output key with the following format:
    {
        "status": "success",
        "technical_indicators": [
            "technical_indicator": "Technical indicator",
        ]
    }
    If the tool fails, return the error message in the 'error_message' output key with the following format:
    {
        "status": "error",
        "error_message": "Error fetching technical indicators: Error message"
    }
    """,
    tools=[fetch_technical_indicators],
    output_key="technical_indicators",
)
