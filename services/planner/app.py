"""Planner service scaffold.
PSEUDOCODE:
1) Normalize intent.
2) Classify intent into known workflow category.
3) Return deterministic action list with required scopes.
4) Include confidence + rationale fields for observability."""

from services.api_gateway.schemas import ActionPlanItem, RiskLevel


def plan_actions(intent: str, actor_context: dict) -> list[ActionPlanItem]:
    normalized_intent = intent.lower().strip()

    if "gmail" in normalized_intent or "email" in normalized_intent:
        return [
            ActionPlanItem(
                action="gmail.send_reply",
                provider="google",
                risk=RiskLevel.medium,
                required_scopes=["gmail.send"],
                payload={
                    "to": "customer@example.com",
                    "subject": "Re: Your request",
                    "body": "Your request has been received and is being processed.",
                },
                reason="User intent requires an outbound email response.",
                confidence=0.91,
            )
        ]

    if "slack" in normalized_intent or "notify" in normalized_intent:
        return [
            ActionPlanItem(
                action="slack.post_message",
                provider="slack",
                risk=RiskLevel.low,
                required_scopes=["slack:chat:write"],
                payload={
                    "channel": "ops-review",
                    "text": "ConsentOps Mesh automated notification",
                },
                reason="User intent requires notifying a Slack channel or thread.",
                confidence=0.94,
            )
        ]

    return [
        ActionPlanItem(
            action="slack.post_message",
            provider="slack",
            risk=RiskLevel.low,
            required_scopes=["slack:chat:write"],
            payload={
                "channel": "ops-review",
                "text": "Fallback workflow triggered for manual review.",
            },
            reason="Fallback workflow: notify operations channel for manual review.",
            confidence=0.60,
        )
    ]
