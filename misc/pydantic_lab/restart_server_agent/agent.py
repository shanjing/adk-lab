from ipaddress import IPv4Address

from google.adk.tools import FunctionTool
from google.adk.agents import Agent

from pydantic import BaseModel, Field
from devtools import debug

# 1. Define the Input Schema (Standard Pydantic!)
class RestartServerInput(BaseModel):
    server_ip: IPv4Address = Field(
        description="The IP address of the server to restart."
    )
    force: bool = Field(
        default=False,
        description="If True, performs a hard reset immediately."
    )

# 2. Define the Python Function
def my_restart_python_function(args: RestartServerInput):
    print(f"Restarting server {args.server_ip} with force={args.force}")
    return f"Server {args.server_ip} restarted with force={args.force}"


# 3. Wrap it in an ADK Tool
restart_tool = FunctionTool(func=my_restart_python_function)
debug(restart_tool)

root_agent = Agent(
    name="restart_server_agent",
    model="gemini-2.0-flash",
    description="A root agent that can restart servers.",
    tools=[restart_tool],
    instruction="You are a helpful assistant that can restart servers."
)
debug(root_agent)