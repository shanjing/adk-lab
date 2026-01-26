from google.adk.agents import LlmAgent
from tools.config import AI_MODEL
from tools.travel_policy import check_travel_policy


# The Guard Agent
root_agent = LlmAgent(
    name="supervisor_guard",
    model=AI_MODEL,
    description="A strict policy enforcement agent.",
    tools=[check_travel_policy],
    instruction=(
        "You are the Travel Policy Supervisor.\n\n"
        "YOUR GOAL:\n"
        "1. Extract the `user_id` and the `target_city` from the request.\n"
        "2. CALL `check_travel_policy(user_id, target_city)`.\n"
        "3. IF policy is 'allowed': False -> You MUST reject the request. Explain why.\n"
        "4. IF policy is 'allowed': True -> You MUST output exactly: 'DELEGATE_TO_WORKER: <city>'.\n"
        "   Do not provide travel info yourself. Just delegate."
    ),
)