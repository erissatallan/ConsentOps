"""Audit service scaffold."""

"""def append_event(run_id: str, event_type: str, payload: dict) -> dict:

    PSEUDOCODE:
    1) Validate event type and payload shape.
    2) Persist immutable event with timestamp.
    3) Return event ID and run sequence number.

    return {"run_id": run_id, "event_type": event_type, "payload": payload}
    
append_event becomes the one place all services write timeline entries.
get_events gives the API something real to return.

The audit service should return the same event type the API already exposes.
We add event_id and timestamp now so the shape is stable before persistence.
"""

from datetime import UTC, datetime
from uuid import uuid4

from services.api_gateway.schemas import RunStatus, RunTimelineEvent


def append_event(
    run_id: str,
    event_type: str,
    status: RunStatus,
    payload: dict,
    ) -> RunTimelineEvent:

    return RunTimelineEvent(
        event_type=event_type,
        status=status,
        detail={
            "event_id": str(uuid4()),
            "run_id": run_id,
            "timestamp": datetime.now(UTC).isoformat(),
            **payload,
        },
    )
