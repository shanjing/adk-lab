from tools.db import SqlitePolicyService
from tools.logging_utils import logger

# singleton instance
policy_service = SqlitePolicyService()


# --- SUPERVISOR TOOLS ---
def check_travel_policy(user_id: str, target_city: str) -> dict:
    """
    Checks if the user is allowed to travel to the target city.
    """
    is_visited = policy_service.has_visited(user_id, target_city)
    logger.info(f"POLICY CHECK: User={user_id}, City={target_city}, Visited={is_visited}")

    if is_visited:
        return {
            "allowed": False,
            "reason": f"""
            Policy Violation: You have already visited {target_city}. 
            We only allow one trip per city.
            """
        }
    return {
        "allowed": True,
        "reason": "Policy Check Passed."
    }
