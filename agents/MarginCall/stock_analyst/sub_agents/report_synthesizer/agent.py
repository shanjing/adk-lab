"""
report_synthesizer – sub-agent (placeholder).
"""

from google.adk.agents import LlmAgent

from tools.config import AI_MODEL

# For consistency, python variable and agent name are identical
report_synthesizer = LlmAgent(
    name="report_synthesizer",
    model=AI_MODEL,
    description="A specialist agent.",
    instruction="""
    You are a placeholder for the report_synthesizer agent.
    Currently under construction.
    Acknowledge the user's request and state that you cannot process it yet.
    """,
)
