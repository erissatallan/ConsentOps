# ConsentOps Mesh (AWS + Python)

ConsentOps Mesh is a serverless microservices platform for policy-gated AI agent actions across enterprise tools.

This repository is intentionally scaffolded for guided development:
- You will implement real code by replacing pseudocode stubs.
- Each service starts with explicit TODOs and contracts.
- We prioritize hackathon shipping speed and judging alignment.

## Project Layout

- `docs/START_HERE.md`: Guided development sequence (day 1 to MVP).
- `docs/ARCHITECTURE.md`: Service boundaries and event contracts.
- `docs/AUTH0_INTEGRATIONS_NOTES.md`: Auth0 AI integrations and Token Vault requirements.
- `services/*`: Individual microservices with pseudocode entrypoints.
- `infra/`: IaC placeholders for AWS deployment.

## Auth0 Integration Baseline (Required)

For hackathon eligibility and secure tool execution, the implementation must:
1. Use Auth0 Token Vault for third-party API access.
2. Configure Connections for each external provider (for example Google, Slack).
3. Enable Connected Accounts / Token Vault for each connection.
4. Request required scopes, including profile and offline access equivalents where applicable.
5. Enable each connection on the AI app in Auth0.

Reference: https://auth0.com/ai/docs/integrations/overview

## First Steps

1. Read `docs/START_HERE.md`.
2. Read `docs/AUTH0_INTEGRATIONS_NOTES.md`.
3. Implement `services/api_gateway/app.py` endpoints.
4. Implement planner -> policy -> orchestrator happy path.
5. Add Gmail and Slack adapter actions.
6. Add audit event persistence and workflow timeline.

## Runtime Baseline

- Python 3.12+
- FastAPI for HTTP services
- Pydantic for schemas
- boto3 for AWS integrations
- pytest for service-level tests

