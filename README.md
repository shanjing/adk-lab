# adk-lab

Reusable utilities and reference implementations for building
agentic systems using **Google ADK (1.21+)**.

This repository serves two complementary purposes:

1. **`adk_lab`** — a small, reusable Python package that provides
   utilities and helpers for ADK-based agent development.
2. **`agentic_patterns`** — a curated set of runnable reference
   implementations of common agentic design patterns built on
   top of Google ADK.

---

## Repository Structure

├── adk_lab/ # Reusable ADK utilities (Python package)
├── agentic_patterns/ # Reference implementations of agentic patterns
├── pyproject.toml
└── README.md


---

## adk_lab (Python package)

The `adk_lab` package contains reusable helpers intended to be
imported by other projects, as well as by the reference
implementations in this repository.

Typical usage:

```python
from adk_lab.utilities import show_agent_result

The package is intentionally small and focused, and targets
Google ADK version 1.21+ semantics.

#For local development or experimentation:

pip install -e .

#Install from Github

pip install git+https://github.com/YOURNAME/adk-lab.git

## agentic_patterns (reference implementations)

The agentic_patterns/ directory contains runnable reference
implementations of common agentic design patterns, including:

Session and state management

Routing and delegation

Sequential chaining and composition

Reflection / critique loops

Parallel fan-out / fan-in execution


This repository is:

Educational, but not introductory

Focused on architectural patterns and execution models

Aligned with Google ADK 1.21+ behavior

It is not a production-ready application, but the utilities

and patterns may be adapted for production use.

#License

MIT

