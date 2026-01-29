"""
news_fetcher – sub-agent (placeholder).
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.tools import google_search

from tools.config import AI_MODEL

# For consistency, python variable and agent name are identical
news_fetcher = LlmAgent(
    name="news_fetcher",
    model=AI_MODEL,
    description="A stock news fetcher agent",
    instruction="""
    You are a stock news fetcher agent.
    You will be given a stock symbol.
    Use the 'google_search' tool to fetch the stock news.
    Limit to 3 news articles, total number of characters to 300.
    The news should be in the following format:
    [
        {
            "title": "Stock news title",
            "url": "Stock news url",
            "snippet": "Stock news snippet"
        },
    Return the stock news in the 'stock_news' output key with the following format:
    {
        "status": "success",
        "news": [
            {
                "title": "Stock news title",
                "url": "Stock news url",
                "snippet": "Stock news snippet"
            },
            {
                "title": "Stock news title",
                "url": "Stock news url",
                "snippet": "Stock news snippet"
            }
    }
    """,
    tools=[google_search],
    output_key="stock_news",
)
