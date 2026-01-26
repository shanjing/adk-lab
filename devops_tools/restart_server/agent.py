from ipaddress import IPv4Address

from google.adk.tools import FunctionTool
from google.adk.agents import Agent

from pydantic import BaseModel, Field


# 1. Define the Input Schema (Standard Pydantic!)
class RestartServerInput(BaseModel):
    server_ip: str = Field(description="The IP address of the server to restart.")
    force: bool = Field(
        default=False, description="If True, performs a hard reset immediately."
    )


# 2. Define the Python Function
def func_restart_server(args: RestartServerInput):
    try:
        ip = IPv4Address(args.server_ip)
    except ValueError:
        return f"Invalid IP address: {args.server_ip}"
    print(f"Restarting server {ip} with force={args.force}")
    return f"Server {args.server_ip} restarted with force={args.force}"


# 3. Define the Agent
# a demonstration on how to use state's data (dictionary) in the agent's instruction
# when creating the session, we set the {critical_server} and
# {manager_name} in the initial state,
# agents have access to the state of the session
# note: can't use f-string when referring a state key as Python doesn't know it.
# only agent knows to fetch it from the state dictionary.

root_agent = Agent(
    name="restart_server",
    model="gemini-2.0-flash",
    description="A root agent that can restart servers.",
    tools=[func_restart_server],
    instruction="""
    You are a helpful assistant that can restart servers.
    You are given a server IP address and a force flag.
    You need to restart the server with the function func_restart_server.
    Note, there is one critical server {critical_server} 
    that you can never restart, it needs a special approval from the manager {manager_name}.
    """,
)

# Optional alias for runners that look for `agent`.
agent = root_agent
