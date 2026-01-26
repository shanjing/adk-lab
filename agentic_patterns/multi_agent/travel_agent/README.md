## travel_agent : a multi agent example
This agent demonstrates the pattern of using adk's AgentTool to call sub-agents
Agents can derive its tool functions schemas via function interface.
It has a sqlite session service to store sessions for replay.
Agents also have memory for tools' validations (one trip per city policy)

### structure 
```
travel_agent
├── adk_agent_memory.db
├── main.py
├── README.md
├── supervisor_guard
│   ├── __init__.py
│   ├── agent.py
│   └── sub_agents
│       ├── __init__.py
│       └── travel_planner
├── tools
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── logging_utils.py
│   ├── schemas.py
│   ├── travel_apps.py
│   ├── travel_policy.py
│   └── utilities.py
└── travel_agent_sessions.db

```
### agents
* supervisor_guard (root_agent)
* travel_planner (sub_agent)
```
root_agent = LlmAgent(
    name="supervisor_guard",
    model=AI_MODEL,
    tools=[
        check_travel_policy,
        AgentTool(agent=travel_agent),
    ],
    ...)
```
```
travel_agent = LlmAgent(
    name="travel_planner",
    model=AI_MODEL,
    description="A specialist in booking flights and checking weather.",
    tools=[
        get_5_day_weather, 
        search_flights, 
        search_hotels,
        record_visit,
    ],
    ...)
```

### tools
* check_travel_policy, record_visit
* get_5_day_weather, search_flights, search_hotels, record_visit,

### schemas
```
class PolicyCheckInput(BaseModel):
    user_id: str = Field(
        ..., description="The ID of the user requesting travel."
    )
    target_city: str = Field(
        ..., description="The city the user is requesting to travel to."
    )
class WeatherInput(BaseModel):
    city: str = Field(..., description="The city to get the weather for.")

class FlightSearchInput(BaseModel):
    to_city: str = Field(..., description="The city to fly to.")   

class HotelSearchInput(BaseModel):
    city: str = Field(..., description="The city to find a hotel in.")
```

