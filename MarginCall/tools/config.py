import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

# Explicitly define the source
CLOUD_MODEL = os.getenv("CLOUD_AI_MODEL")
LOCAL_MODEL = os.getenv("LOCAL_AI_MODEL", "gemma3:27b")

LOCAL_LLM = False

if CLOUD_MODEL:
    # We are in Cloud Mode
    AI_MODEL = CLOUD_MODEL
    AI_MODEL_NAME = CLOUD_MODEL
else:
    # We are in Local Mode
    # Instantiate the wrapper for the Agent, but keep the name for the Logger
    AI_MODEL = LiteLlm(model=LOCAL_MODEL)
    AI_MODEL_NAME = f"local:{LOCAL_MODEL}"
    LOCAL_LLM = True

INCLUDE_THOUGHTS = os.getenv("INCLUDE_THOUGHTS", "false").lower() == "true"

ROOT_AGENT = os.getenv("ROOT_AGENT", "SET_ROOT_AGENT_NAME_HERE")
SUB_AGENTS = os.getenv("SUB_AGENTS", "SUB_AGENT_1,SUB_AGENT_2,SUB_AGENT_3").strip().split(",")
# Export AI_MODEL for the Agent and AI_MODEL_NAME for the Logger
