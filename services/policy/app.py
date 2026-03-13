"""Policy evaluation scaffold.
   The goal is to create defensible policy decisions that can be audited and explained.
   Project core trust model:
   - Missing provider connection is a hard deny.
   - Missing scopes is a hard deny.
   - Medium/high risk becomes approval_required.
   - Only low-risk, fully scoped actions auto-run.


def evaluate_plan(action_plan: list[dict], actor_context: dict) -> list[dict]:
    
    PSEUDOCODE:
    1) For each action, check actor scopes and tenant policy.
    2) Classify decision as allow / deny / approval_required.
    3) Deny by default when data is missing.
    4) Return policy annotations for orchestrator.
    
    decisions = []
    for item in action_plan:
        decision = {**item, "decision": "allow" if item.get("risk") == "low" else "approval_required"}
        decisions.append(decision)
    return decisions
"""

from services.api_gateway.schemas import (
    ActionPlanItem,
    PolicyDecision,
    PolicyDecisionType,
    RiskLevel,
)

def evaluate_plan(action_plan: list[ActionPlanItem], actor_context: dict) -> list[PolicyDecision]:
    granted_scopes = set(actor_context.get("granted_scopes", []))
    connected_accounts = set(actor_context.get("connected_accounts", []))

    decisions: list[PolicyDecision] = []

    for item in action_plan:
        if item.provider not in connected_accounts:
            decisions.append(
                PolicyDecision(
                    **item.model_dump(),
                    decision=PolicyDecisionType.deny,
                    policy_reason=f"Missing connected account for provider '{item.provider}'",
                )
            )
            continue

        missing_scopes = [scope for scope in item.required_scopes if scope not in granted_scopes]
        if missing_scopes:
            decisions.append(
                PolicyDecision(
                    **item.model_dump(),
                    decision=PolicyDecisionType.deny,
                    policy_reason=f"Missing required scopes: {', '.join(missing_scopes)}.",
                )
            )
            continue

        if item.risk in {RiskLevel.medium, RiskLevel.high}:
            decisions.append(
                PolicyDecision(
                    **item.model_dump(),
                    decision=PolicyDecisionType.approval_required,
                    policy_reason="Action exceeds auto-execution threshold and requires approval.",
                )
            )
            continue

        decisions.append(
            PolicyDecision(
                **item.model_dump(),
                decision=PolicyDecisionType.allow,
                policy_reason="Action is low risk and all required scopes are available.",
            )
        )

    return decisions
