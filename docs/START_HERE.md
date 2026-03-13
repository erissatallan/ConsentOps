# START HERE: Guided Development Plan

This file is your execution script. Replace pseudocode with production code in the exact order below.

## 1) Outcome For Sprint 1 (Happy Path)

Build one complete run:
1. User submits intent to API Gateway.
2. Planner converts intent into proposed actions.
3. Policy service marks each action as `auto` or `approval_required`.
4. Orchestrator executes auto-approved actions via tool runtime.
5. Tool runtime gets scoped provider token via Auth0 Token Vault.
6. Audit service records all events.
7. API returns run timeline.

## 2) Immediate Build Order

1. Implement common schemas in `services/api_gateway/schemas.py`.
2. Implement `POST /v1/runs` in API gateway.
3. Implement planner `plan_actions(intent)`.
4. Implement policy `evaluate_plan(plan, actor_context)`.
5. Implement orchestrator state machine for happy path only.
6. Implement tool runtime dispatcher with two no-op adapters.
7. Add Auth0 Token Vault token acquisition wrapper in tool runtime.
8. Add audit event append function.
9. Add one integration test for full chain.

## 3) Rules While Implementing

1. Keep every service function pure where possible.
2. Accept explicit inputs; avoid hidden globals.
3. Emit one audit event for every state transition.
4. Fail closed on policy uncertainty.
5. Use idempotency keys for tool executions.
6. Never pass raw provider credentials from frontend to backend.

## 4) Auth0 Connection Setup Gate (Do This Before Live Tool Calls)

1. Create connection (Google/Slack or another provider).
2. Request default scopes needed by your tools.
3. Include user profile + offline access equivalents for refresh/token lifecycle.
4. Toggle Connected Accounts / Token Vault for that connection.
5. Enable that connection on the Auth0 app used by ConsentOps Mesh.

If a provider is not available as built-in integration, use custom OAuth2 or OIDC connection.

## 5) What To Replace First

Each service file contains `PSEUDOCODE:` blocks.
Replace them in this order:
1. HTTP validation.
2. Domain logic.
3. Persistence.
4. Observability.
5. Retries/timeouts.

## 6) Definition of Done For This Phase

1. `POST /v1/runs` returns a stable run object.
2. Planner returns deterministic action list for known intents.
3. Policy marks high-risk actions as approval required.
4. Tool runtime executes at least one Gmail and one Slack action stub.
5. Audit timeline can be queried by run ID.
6. Token Vault-backed token retrieval is wired in one adapter path.
