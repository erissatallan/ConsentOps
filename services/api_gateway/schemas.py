"""Shared API schemas (to be implemented)."""

# PSEUDOCODE:
# - Create Pydantic models:
#   - RunCreateRequest
#   - RunCreateResponse
#   - ActionPlanItem
#   - PolicyDecision
#   - RunTimelineEvent
# - Add strict validators for intent text, actor ID, tenant ID.
# - Add enum types for risk and run statuses.'

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class RunStatus(str, Enum):
    created = "created"
    planned = "planned"
    policy_evaluated = "policy_evaluated"
    executing = "executing"
    awaiting_approval = "awaiting_approval"
    completed = "completed"
    failed = "failed"

class PolicyDecisionType(str, Enum):
    allow = "allow"
    deny = "deny"
    approval_required = "approval_required"

class ActorContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    user_id: str = Field(min_length=3, max_length=128)
    tenant_id: str = Field(min_length=2, max_length=128)
    granted_scopes: list[str] = Field(default_factory=list)
    connected_accounts: list[str] = Field(default_factory=list)

    @field_validator("user_id", "tenant_id")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("identifier must not be empty")
        return cleaned

class ActionPlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=3, max_length=128)
    provider: str = Field(min_length=2, max_length=64)
    risk: RiskLevel
    required_scopes: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(min_length=3, max_length=500)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("action", "provider", "reason")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be empty")
        return cleaned

class PolicyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    provider: str
    risk: RiskLevel
    required_scopes: list[str]
    payload: dict[str, Any]
    reason: str
    confidence: float
    decision: PolicyDecisionType
    policy_reason: str

class RunTimelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str
    status: RunStatus
    detail: dict[str, Any] = Field(default_factory=dict)

class RunCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str = Field(min_length=10, max_length=1000)
    actor_context: ActorContext

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("intent must be at least 10 characters")
        return cleaned

class RunCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: RunStatus
    intent: str
    plan: list[ActionPlanItem]
    policy_decisions: list[PolicyDecision]
    timeline: list[RunTimelineEvent]



