import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

# Explicitly define the source
CLOUD_MODEL = os.getenv("CLOUD_AI_MODEL")
LOCAL_MODEL = os.getenv("LOCAL_LLM_MODEL", "gemma3:27b")

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

# Export AI_MODEL for the Agent and AI_MODEL_NAME for the Logger