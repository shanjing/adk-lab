# Kubernetes Operations Agent

This project demonstrates using Pydantic models to enforce data integrity within a Sequential Agent pipeline.

## Architecture

The system utilizes a chain of three specialized agents:
1. `log_investigator` (Input Analysis)
2. `sre_architect` (Fix Generation)
3. `email_notifier` (Notification)

## Core Design Principles

### 1. The Blackboard Pattern (Shared Knowledge)
The architecture strictly separates **Conversation** from **Technical Data** to ensure fidelity.
- **Conversation (Chat Output):** Agents pass natural language summaries (e.g., "Error found, proceeding to fix") to drive the control flow.
- **Technical Data (Shared State):** Critical artifacts—such as Pod IDs or configurations—are written directly to the session state. Tools read from this trusted source to prevent hallucinations common in purely text-based handoffs.

### 2. Schema Strategy (Gatekeeper vs. Guide)
- **Input Schema:** The `input_schema` is intentionally omitted for the entry agent. This prevents the system from acting as a rigid gatekeeper, allowing it to accept natural language queries.
- **Tool Schema:** Internal handoffs rely on the ADK's automatic introspection. The agent dynamically learns how to format data for functions by analyzing the tool's signature, independent of entry validation.

### 3. Reliable Functions (Simple Interface, Strong Validation)
- **Interface:** Tools are designed to accept primitive inputs (strings/integers) to minimize friction for the LLM.
- **Validation:** Internal logic immediately "rehydrates" these inputs into strict Pydantic models. This ensures that the code enforces safety constraints even if the agent provides unstructured text.

### 4. Flexible User Input (Intelligent Router)
- **Mechanism:** By omitting the entry schema, the first agent functions as an "Intelligent Router."
- **Function:** It parses plain English (e.g., "Check the auth service") and maps the intent to the technical parameters defined in the tools.
- **Benefit:** This enables a ChatOps experience where the agent handles the translation from human language to technical execution.

## Technical Note: Under the Hood

**Automatic Instruction Injection**
The ADK automatically scans function signatures to generate system instructions. This eliminates the need to manually prompt the AI on data structure requirements for every tool.

**Data Integrity via Shared State**
Passing technical identifiers through chat output introduces a risk of mutation ("The Telephone Game"). This project uses a Pass-by-Reference model via `session.state`, pointing downstream agents to the immutable, original data point discovered in the initial step.

**Why No Input Schema for an agent is often better?**
In the specific case of log_investigator, the input_schema is optional and better to be removed.

Old Logic (Rigid): User: "Check auth pod." System: Error or Force Parse -> input_schema validation -> Agent -> Tool. Risk: If the user query is vague, the input_schema parser might fail before the Agent even gets a chance to "think."

New Logic (Agentic): User: "Check auth pod." System: Pass -> Agent reads text. Agent thinks: "User wants to check auth. My tool fetch_k8s_logs needs a pod_name. I will extract 'auth' and call the tool." Result: The Agent handles the transformation dynamically.

**Debug Example: ADK-Generated Instruction**
The following demonstrates the agent can derive the data schema from the its function's interface.
Under the hood, the agent peeks its function's interface and understands it needs to provide 
issue_summary:str to the function 
generate_k8s_manifest( tool_context: ToolContext, req: FixRequestSchema) -> str:

```json
{
  "model": "gemini-2.0-flash",
  "config": {
    "http_options": {
      "headers": {
        "x-goog-api-client": "google-adk/1.21.0 gl-python/3.11.9",
        "user-agent": "google-adk/1.21.0 gl-python/3.11.9"
      }
    }
  },
  "system_instruction": "You are a SRE. Use function generate_k8s_manifest to generate a YAML fix for the reported issue. You are an agent. Your internal name is \"sre_architect\".",
  "tools": [
    {
      "function_declarations": [
        {
          "description": "Generates a fix manifest using the saved context.",
          "name": "generate_k8s_manifest",
          "parameters": {
            "type": "OBJECT",
            "properties": {
              "req": {
                "type": "OBJECT",
                "properties": {
                  "issue_summary": {
                    "type": "STRING"
                  }
                }
              }
            },
            "required": [
              "req"
            ]
          }
        }
      ]
    }
  ]
}
```