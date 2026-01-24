"""
This agent is a simple log analyzer that can be used to analyze logs from a K8s cluster.
It uses a sequential agent to analyze the logs and generate a fix manifest.

Structured data is enforced by the pydantic models.

The agent is designed to be used in a sequential manner.
The first agent is the log analyzer, which will analyze the logs and generate a summary of the logs.
The second agent is the fix architect, which will generate a fix manifest based on the summary of the logs.

The two agents use ToolContext to access session state to share data between them.
Since the ToolContext is a singleton, the data is shared between the two agents,
there is no output schema.
"""
import logging
import os
import sys
from pydantic import BaseModel, Field


# --- 1. ADK IMPORTS (The "Runtime" Layer) ---
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import ToolContext

import dotenv

dotenv.load_dotenv()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")

logging.basicConfig(
    level=logging.INFO,
    format='%(funcName)s | %(lineno)d | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("sre_pipeline")

# --- 2. DECLARATIVE CONTRACTS (The "What") ---
# Schema for Agent A's input (Forces structured thinking)
class LogQuerySchema(BaseModel):
    namespace: str = Field(default="kube-system", description="The K8s namespace (e.g., 'kube-system').")
    pod_name: str = Field(..., description="The target pod name.")
    lines: int = Field(100, description="Lines of logs to fetch.")

# Schema for Agent B's input (Agent B is triggered by the previous agent's findings)
class FixRequestSchema(BaseModel):
    issue_summary: str = Field(..., description="Summary of the error found.")

class EmailPayloadSchema(BaseModel):
    message_note: str = Field(..., description="A note about the email.")
    # Note: We do NOT ask the LLM for address/subject here, 
    # we enforce those in code or state for consistency.
"""
class EmailNotificationSchema(BaseModel):
    address: str = Field(..., description="The email address to send the notification to.")
    subject: str = Field(..., description="The subject of the email.")
    body: str = Field(..., description="The body of the email.")
    attachments: list[str] = Field(..., description="The attachments of the email.")
"""
# --- 3. IMPERATIVE TOOLS (The "How" & Side Effects) ---
def fetch_k8s_logs(
    tool_context: ToolContext, 
    query: LogQuerySchema
    ) -> str:
    """Fetches logs and saves context (Pod ID/NS) to session state."""
    
    # [Imperative Side Effect] Important:
    # The model, per its input_schema (LogQuerySchema), will extract 
    # the pod name and namespace and optionally the line number
    #  from the user's query/input from chat box.
    # The the model then calls this function providing query argments.
    # We silently save the specific targeting info to the session.
    tool_context.session.state["target_pod"] = query.pod_name
    tool_context.session.state["target_namespace"] = query.namespace
    tool_context.session.state["target_line"] = query.lines
    
    logger.info(f"  [Tool] Fetching logs for {query.pod_name} in namespace {query.namespace}...")
    # Mocking the K8s API response
    return f"Logs retrieved. Found CRITICAL error: {query.pod_name} in namespace {query.namespace} due to OOMKilled."

def generate_k8s_manifest(
    tool_context: ToolContext,
    req: FixRequestSchema
    ) -> str:
    """Generates a fix manifest using the saved context."""
    
    # [Imperative Context Retrieval]
    # We pull the pod name from session.state, NOT from the prompt.
    # This prevents the 'Telephone Game' where LLMs hallucinate IDs.
    pod = tool_context.session.state.get("target_pod", "unknown-pod")
    ns = tool_context.session.state.get("target_namespace", "default")
    
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

def send_notification_email(
    tool_context: ToolContext, 
    payload: EmailPayloadSchema) -> str:
    """
    Sends a notification email using the generated manifest and context.
    """
    # [State Retrieval] Enriches the email with facts the LLM might miss
    pod = tool_context.session.state.get("target_pod", "UNKNOWN")
    ns = tool_context.session.state.get("target_namespace", "default")
    
    # [Secure Config] Don't let LLM guess the email address
    to_address = "chaos_sre@twtr.com" 
    
    email_body = f"""
    ---------------------------------------------------
    TO: {to_address}
    SUBJECT: [Auto-Fix] Incident Resolved for {pod}
    ---------------------------------------------------
    Cluster Context: {ns}/{pod}
    
    SRE Note:
    {payload.message_note}
    
    (Manifest applied successfully)
    ---------------------------------------------------
    """
    
    logger.info(f"Sending email to {to_address}")
    return "Email notification sent successfully."


# --- 4. AGENT DEFINITIONS ---

# Agent 1: The Investigator (User input -> structured search)
log_investigator_agent = Agent(
    name="log_investigator",
    model=AI_MODEL,
    instruction="""
    You are an Log Investigator. 
    Analyze the user request and use 'fetch_k8s_logs' to find errors.
    Summarize the error concisely for the next agent.
    """,
    tools=[fetch_k8s_logs],
    input_schema=LogQuerySchema, # parse user chat input into LogQuerySchema, optional 
    output_key="log_summary" # passes text to agent sre_architect
)

# Agent 2: The Architect (text input -> YAML Output)
sre_agent = Agent(
    name="sre_architect",
    model=AI_MODEL,
    instruction="""
    You are a SRE, Kubernetes expert. 
    You will receive an error summary from the log investigator agent.
    Call function generate_k8s_manifest to 
     generate a YAML fix for the reported issue.
    """,
    tools=[generate_k8s_manifest],
    # No input schema for this agent
    # It accepts the text output from the log investigator agent.
    output_key="fix_manifest"
)
# Ageng 3: The Email Notifier (text input -> action)
email_notifier_agent = Agent(
    name="email_notifier",
    model=AI_MODEL,
    instruction="""
    You are a Notification Bot.
    You will receive a K8s manifest.
    Call 'send_notification_email' to notify the team.
    Extract a brief note about what the fix does for the 'message_note' argument.
    """,
    tools=[send_notification_email],
    # No input_schema: It accepts the YAML text from Agent 2
    output_key="email_sent",
)
# Orchestrator: The Root Agent (Sequential pattern)
root_agent = SequentialAgent(
    name="log_analyzer",
    sub_agents=[log_investigator_agent, sre_agent, email_notifier_agent]
)

# Optional alias for runners that look for `agent`.
agent = root_agent