import os
from pydantic import BaseModel, Field

# --- 1. ADK IMPORTS (The "Runtime" Layer) ---
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.runners import InMemoryRunner  # Local runner for testing
from google.adk.models.google_llm import Gemini # Or VertexAI, depending on your auth

import dotenv

dotenv.load_dotenv()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")
# --- 2. DECLARATIVE CONTRACTS (The "What") ---

# Schema for Agent A's input (Forces structured thinking)
class LogQuerySchema(BaseModel):
    namespace: str = Field(..., description="The K8s namespace (e.g., 'kube-system').")
    pod_name: str = Field(..., description="The target pod name.")
    lines: int = Field(100, description="Lines of logs to fetch.")

# Schema for Agent B's input (Agent B is triggered by the previous agent's findings)
class FixRequestSchema(BaseModel):
    issue_summary: str = Field(..., description="Summary of the error found.")

# --- 3. IMPERATIVE TOOLS (The "How" & Side Effects) ---

def fetch_k8s_logs(ctx: ToolContext, query: LogQuerySchema) -> str:
    """Fetches logs and saves context (Pod ID/NS) to session state."""
    
    # [Imperative Side Effect]
    # We silently save the specific targeting info to the session.
    # The LLM doesn't need to repeat this back to us; we trust the code.
    ctx.session.state["target_pod"] = query.pod_name
    ctx.session.state["target_ns"] = query.namespace
    
    print(f"  [Tool] Fetching logs for {query.pod_name}...")
    # Mocking the K8s API response
    return f"Logs retrieved. Found CRITICAL error: 'CrashLoopBackOff' due to OOMKilled."

def generate_k8s_manifest(ctx: ToolContext, req: FixRequestSchema) -> str:
    """Generates a fix manifest using the saved context."""
    
    # [Imperative Context Retrieval]
    # We pull the pod name from State, NOT from the prompt.
    # This prevents the 'Telephone Game' where LLMs hallucinate IDs.
    pod = ctx.session.state.get("target_pod", "unknown-pod")
    ns = ctx.session.state.get("target_ns", "default")
    
    return f"""
    apiVersion: v1
    kind: Pod
    metadata:
      name: {pod}
      namespace: {ns}
    spec:
      # Fix for: {req.issue_summary}
      resources:
        limits:
          memory: "2Gi"
    """

# --- 4. AGENT DEFINITIONS ---

# Agent A: The Investigator
analyzer_agent = Agent(
    name="log_analyzer",
    model="gemini-1.5-pro", # String reference or Model object
    instruction="You are an SRE. Use the log tool to find errors. Summarize the root cause.",
    tools=[fetch_k8s_logs],
    input_schema=LogQuerySchema 
)

# Agent B: The Architect
fixer_agent = Agent(
    name="fix_architect",
    model="gemini-1.5-pro",
    instruction="You are a K8s Architect. Generate a YAML fix for the reported issue.",
    tools=[generate_k8s_manifest]
)

# --- 5. THE WORKFLOW EXECUTION ---

def run_sre_pipeline(user_prompt: str):
    runner = InMemoryRunner()
    session_id = runner.create_session()
    
    print(f"Starting SRE Pipeline for: '{user_prompt}'\n")

    # === STEP 1: ANALYZE ===
    # We use 'output_key' to strictly capture the finding description
    print("--- Step 1: Running Analyzer ---")
    result_a = runner.run_agent(
        session_id=session_id,
        agent=analyzer_agent,
        input_text=user_prompt,
        output_key="analysis_finding" # <--- DECLARATIVE HANDOFF
    )
    
    # The text "CrashLoopBackOff due to OOMKilled" is now in session.state['analysis_finding']
    finding = runner.get_session(session_id).state.get("analysis_finding")
    print(f"  [Output] Finding: {finding}\n")

    # === STEP 2: FIX ===
    # We manually construct the handoff prompt
    print("--- Step 2: Running Fixer ---")
    handoff_prompt = f"The issue is: {finding}. Generate a fix."
    
    result_b = runner.run_agent(
        session_id=session_id,
        agent=fixer_agent,
        input_text=handoff_prompt
    )
    
    print(f"  [Output] Final Fix:\n{result_b.text}")

# --- Test Run ---
if __name__ == "__main__":
    # Simulating a user typing this into the chat
    # Note: The JSON string format is required if input_schema is set on Agent A
    input_json = '{"namespace": "prod", "pod_name": "checkout-service-x92", "lines": 50}'
    run_sre_pipeline(input_json)