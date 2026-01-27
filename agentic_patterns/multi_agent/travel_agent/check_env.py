import logging
import os
from tools.logging_utils import setup_logging
from tools.config import AI_MODEL, AI_MODEL_NAME

def run_sanity_check():
    # 1. Test Logging Initialization
    # We simulate a 'debug' run to see the startup metadata
    setup_logging(debug=True, model_name=AI_MODEL_NAME)
    
    # Get a local logger to test propagation
    logger = logging.getLogger(__name__)
    logger.info("--- SANITY CHECK START ---")

    # 2. Test Environment Variables
    app_name = os.getenv("AGENT_APP_NAME")
    if not app_name:
        logger.warning("AGENT_APP_NAME is missing from .env! Using default.")
    else:
        logger.info(f"Environment Loaded: APP_NAME={app_name}")

    # 3. Test Model Configuration
    logger.info(f"Targeting Model: {AI_MODEL_NAME}")
    
    # Check if AI_MODEL is a string (Cloud) or an Object (Local/LiteLLM)
    model_type = "STRING (Cloud)" if isinstance(AI_MODEL, str) else "OBJECT (Local/LiteLLM)"
    logger.info(f"Model Object Type: {model_type}")

    # 4. Final Verdict
    click_success = "\033[92mPASSED\033[0m" # ANSI Green
    print(f"\nConfiguration Sanity Check: {click_success}")

if __name__ == "__main__":
    run_sanity_check()
