"""ConsentOps Mesh API Gateway (pseudocode scaffold)

PSEUDOCODE:
1) Validate payload against RunCreateRequest schema.
2) Build run_id and initial run context.
3) Call planner service with intent + actor context.
4) Call policy service to annotate planned actions.
5) Call orchestrator to start execution.
6) Return run summary DTO.

Why this version is good:
It gives you a real typed endpoint immediately.
It lets us test planner and policy through one request.
It creates a timeline we can later move into the audit service with minimal refactoring.
"""

from uuid import uuid4

from fastapi import FastAPI

from services.api_gateway.schemas import (
    RunCreateRequest,
    RunCreateResponse,
    RunStatus,
    RunTimelineEvent,
)
from services.planner.app import plan_actions
from services.policy.app import evaluate_plan


app = FastAPI(title="ConsentOps Mesh API")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/v1/runs", response_model=RunCreateResponse)
def create_run(payload: RunCreateRequest) -> RunCreateResponse:
    run_id = str(uuid4())  # considering it's asynchronous communication with various clients, can't expect chronological ids

    timeline = [
        RunTimelineEvent(
            event_type="run.created",
            status=RunStatus.created,
            detail={"intent": payload.intent}
        )
    ]

    plan = plan_actions(payload.intent, payload.actor_context.model_dump())
    timeline.append(
        RunTimelineEvent(
            event_type="run.planned",
            status=RunStatus.planned,
            detail={"planned_action_count": len(plan)}
        )
    )

    policy_decisions = evaluate_plan(plan, payload.actor_context.model_dump())
    timeline.append(
        RunTimelineEvent(
            event_type="run.policy_evaluated",
            status=RunStatus.policy_evaluated,
            detail={"decision_count": len(policy_decisions)}
        )
    )

    final_status = RunStatus.completed
    if any(decision.decision == "approval_required" for decision in policy_decisions):
        final_status = RunStatus.awaiting_approval
    elif any(decision.decision == "deny" for decision in policy_decisions):
        final_status = RunStatus.failed

    timeline.append(  # ~finally
        RunTimelineEvent(
            event_type="run.status_resolved",
            status=final_status,
            detail={"run_id": run_id}
        )
    )

    return RunCreateResponse(
        run_id=run_id,
        status=final_status,
        intent=payload.intent,
        plan=plan,
        policy_decisions=policy_decisions,
        timeline=timeline
    )   
