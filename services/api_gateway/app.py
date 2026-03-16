"""ConsentOps Mesh API Gateway."""

from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException

from services.api_gateway.auth import extract_bearer_token
from services.api_gateway.schemas import (
    RunCreateRequest,
    RunCreateResponse,
    RunStatus,
    RunTimelineEvent,
)
from services.auth0_token_vault import TokenVaultExchangeError
from services.orchestrator.app import execute_run
from services.planner.app import plan_actions
from services.policy.app import evaluate_plan


app = FastAPI(title="ConsentOps Mesh API")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/v1/runs", response_model=RunCreateResponse)
def create_run(
    payload: RunCreateRequest,
    auth0_subject_token: str | None = Depends(extract_bearer_token)
    ) -> RunCreateResponse:
    run_id = str(uuid4())

    timeline = [
        RunTimelineEvent(
            event_type="run.created",
            status=RunStatus.created,
            detail={"intent": payload.intent}
        )
    ]

    actor_context = payload.actor_context.model_dump()
    actor_context["auth0_subject_token"] = auth0_subject_token

    plan = plan_actions(payload.intent, actor_context)
    timeline.append(
        RunTimelineEvent(
            event_type="run.planned",
            status=RunStatus.planned,
            detail={"planned_action_count": len(plan)}
        )
    )

    policy_decisions = evaluate_plan(plan, actor_context)
    timeline.append(
        RunTimelineEvent(
            event_type="run.policy_evaluated",
            status=RunStatus.policy_evaluated,
            detail={"decision_count": len(policy_decisions)}
        )
    )

    try:
        orchestration_result = execute_run(
            run_id=run_id,
            policy_annotated_plan=[decision.model_dump() for decision in policy_decisions],
            actor_context=actor_context,
        )
    except TokenVaultExchangeError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    timeline.extend(orchestration_result["timeline"])
    final_status = orchestration_result["status"]

    timeline.append(
        RunTimelineEvent(
            event_type="run.status_resolved",
            status=final_status,
            detail={"run_id": run_id},
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
