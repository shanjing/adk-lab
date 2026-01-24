Agentic Development Lab

This repository is an experimentation with the Google Agent Development Kit (ADK). It serves both as a reference for agentic design patterns and as a workspace for building practical, production-oriented DevOps / SRE agents.

Repository Structure

agentic_patterns/

Purpose
Educational reference (textbook-style).

What’s inside
Self-contained implementations of core patterns from Agentic Design Patterns.

Notes
Each script is intentionally standalone and focused on demonstrating a single concept (for example: function calling, exception handling, or control flow).

devops_tools/

Purpose
Production-intent agents.

What’s inside
Operational agents designed for real SRE workflows, such as log analysis and cluster or infrastructure management.

Structure
Follows standard software engineering conventions, with clear separation between:

Agent definitions

Runners / execution entrypoints

misc/

Purpose
Sandbox.

What’s inside
Isolated experiments used to test ideas and dependencies (for example: Pydantic, async/await behavior, or third-party libraries) before promoting them into patterns or production tools.

Setup

Environment

Bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Running Agents

Agentic Patterns
Run individual scripts directly, for example:
python agentic_patterns/function_calling/search_agent.py

DevOps Tools
Run via the main entrypoint, for example:
python devops_tools/main.py
