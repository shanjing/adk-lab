from tools.db import SqlitePolicyService
from pydantic import BaseModel, Field

import logging
logger = logging.getLogger(__name__)


class PolicyCheckInput(BaseModel):
    user_id: str = Field(
        ..., description="The ID of the user requesting travel."
    )
    target_city: str = Field(
        ..., description="The city the user is requesting to travel to."
    )


# singleton instance
policy_service = SqlitePolicyService()


# --- SUPERVISOR TOOLS ---
def check_travel_policy(args: PolicyCheckInput) -> dict:
    """
    Checks if the user is allowed to travel to the target city.
    parameters:
        user_id: The ID of the user requesting travel.
        target_city: The city the user is requesting to travel to.
    """
    is_visited = policy_service.has_visited(args.user_id, args.target_city)
    logger.info(
        "POLICY CHECK: User=%s, City=%s, Visited=%s",
        args.user_id,
        args.target_city,
        is_visited,
    )

    if is_visited:
        return {
            "allowed": False,
            "reason": f"""
            Policy Violation: You have already visited {args.target_city}.
            We only allow one trip per city.
            """,
        }
    return {"allowed": True, "reason": "Policy Check Passed."}


def record_visit(args: PolicyCheckInput) -> dict:
    """
    Records a successful trip for the user (idempotent).
    parameters:
        user_id: The ID of the user who completed the trip booking.
        target_city: The city that was booked.
    """
#    args = PolicyCheckInput(user_id=user_id, target_city=target_city)
    if policy_service.has_visited(args.user_id, args.target_city):
        return {"recorded": False, "reason": "Trip already recorded."}
    policy_service.record_visit(args.user_id, args.target_city)
    return {"recorded": True, "reason": "Trip recorded."}
