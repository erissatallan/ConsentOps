"""Orchestrator scaffold."""


def execute_run(run_id: str, policy_annotated_plan: list[dict]) -> dict:
    """
    PSEUDOCODE:
    1) Emit run.policy_evaluated.
    2) Loop through actions in order.
    3) If decision == approval_required, pause run and emit run.awaiting_approval.
    4) If allow, dispatch action to tool runtime.
    5) Emit success/failure events and finalize run.
    """
    return {"run_id": run_id, "status": "in_progress", "actions": policy_annotated_plan}
