"""
Market Whisper Agent
"""

from google.adk.agents import LlmAgent

from tools.config import AI_MODEL

# For consistency, python variable and agent name are identical
market_whisper = LlmAgent(
    name="market_whisper",
    model=AI_MODEL,
    description="A specialist in summarizing market news for a given stock",
    instruction="""
    You are a specialist in summarizing market news for a given stock.
    You will be given a stock symbol and you will need to summarize the market news for that stock.
    You only provide up to 3 news items for the given stock within the last 7 days
    Your summary should be concise and to the point, and should be no more than 200 words.
    You should use the following format:
    - Stock: <stock symbol>
    - News: <news item 1>
    - News: <news item 2>
    - News: <news item 3>
    - Summary: <summary of the news>
    """,
)