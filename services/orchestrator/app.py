"""Orchestrator scaffold."""

"""
def execute_run(run_id: str, policy_annotated_plan: list[dict]) -> dict:

    PSEUDOCODE:
    1) Emit run.policy_evaluated.
    2) Loop through actions in order.
    3) If decision == approval_required, pause run and emit run.awaiting_approval.
    4) If allow, dispatch action to tool runtime.
    5) Emit success/failure events and finalize run.

    return {"run_id": run_id, "status": "in_progress", "actions": policy_annotated_plan}

deny ends the run immediately.
approval_required pauses the run immediately.
allow executes through the runtime.
"""

from services.api_gateway.schemas import PolicyDecisionType, RunStatus
from services.audit.app import append_event
from services.tool_runtime.app import dispatch_action


def execute_run(run_id: str, policy_annotated_plan: list[dict], actor_context: dict) -> dict:
    timeline = [
        append_event(
            run_id=run_id,
            event_type="run.execution_started",
            status=RunStatus.executing,
            payload={"action_count": len(policy_annotated_plan)},
        )
    ]

    for item in policy_annotated_plan:
        decision = item.get("decision")
        action_name = item.get("action")

        if decision == PolicyDecisionType.deny:
            timeline.append(
                append_event(
                    run_id=run_id,
                    event_type="run.action_denied",
                    status=RunStatus.failed,
                    payload={
                        "action": action_name,
                        "policy_reason": item.get("policy_reason"),
                    },
                )
            )
            return {
                "run_id": run_id,
                "status": RunStatus.failed,
                "timeline": timeline,
            }

        if decision == PolicyDecisionType.approval_required:
            timeline.append(
                append_event(
                    run_id=run_id,
                    event_type="run.awaiting_approval",
                    status=RunStatus.awaiting_approval,
                    payload={
                        "action": action_name,
                        "policy_reason": item.get("policy_reason"),
                    },
                )
            )
            return {
                "run_id": run_id,
                "status": RunStatus.awaiting_approval,
                "timeline": timeline,
            }

        timeline.append(
            append_event(
                run_id=run_id,
                event_type="run.action_started",
                status=RunStatus.executing,
                payload={"action": action_name},
            )
        )

        result = dispatch_action(item, actor_context)

        timeline.append(
            append_event(
                run_id=run_id,
                event_type="run.action_succeeded",
                status=RunStatus.executing,
                payload={
                    "action": action_name,
                    "result": result,
                },
            )
        )

    timeline.append(
        append_event(
            run_id=run_id,
            event_type="run.completed",
            status=RunStatus.completed,
            payload={},
        )
    )

    return {
        "run_id": run_id,
        "status": RunStatus.completed,
        "timeline": timeline,
    }
