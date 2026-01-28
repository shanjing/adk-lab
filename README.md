**Agentic Development Lab**

This repository is an experimentation with the Google Agent Development Kit (ADK). It serves both as a reference for agentic design patterns and as a workspace for building practical, production-oriented DevOps / SRE agents.

**Repository Structure**
```
.
├── agentic_patterns
│   ├── exception_handling
│   ├── function_calling
│   ├── multi_agent
│   └── README.md
├── devops_tools
│   ├── __init__.py
│   ├── common
│   ├── log_analyzer
│   ├── main.py
│   └── restart_server
├── env.example
├── misc
│   ├── pydantic_lab
│   └── README.md
├── pyproject.toml
├── README.md
└── requirements.txt
```


*agentic_patterns/*

Purpose: Educational reference (textbook-style).

What’s inside:
Self-contained implementations of core patterns from Agentic Design Patterns.

Notes:
Each script is intentionally standalone and focused on demonstrating a single concept (for example: function calling, exception handling, or control flow).

*devops_tools/*

Purpose: Production-intent agents.

What’s inside:
Operational agents designed for real SRE workflows, such as log analysis and cluster or infrastructure management.

Structure
Follows standard software engineering conventions, with clear separation between:
Agent definitions
Runners / execution entrypoints

*misc/*

Purpose: Sandbox.

What’s inside:
Isolated experiments used to test ideas and dependencies (for example: Pydantic, async/await behavior, or third-party libraries) before promoting them into patterns or production tools.

**Setup Environment**

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
**Running Agents**

DevOps Tools
Run via the main entrypoint from repo root dir, for example:
```
python -m devops_tools.main run --agent restart_server --input "server 192.168.254.26 force"
```

Agentic Patterns
Run individual scripts directly, for example:
```
python agentic_patterns/function_calling/search_agent.py
```
