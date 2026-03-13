# Architecture (AWS + Python)

## Services

1. API Gateway Service
2. Planner Service
3. Policy Service
4. Orchestrator Service
5. Tool Runtime Service
6. Gmail Adapter Service
7. Slack Adapter Service
8. Audit Service

## Event Types

1. `run.created`
2. `run.planned`
3. `run.policy_evaluated`
4. `run.action_started`
5. `run.action_succeeded`
6. `run.action_failed`
7. `run.awaiting_approval`
8. `run.completed`

## State Machine (Simplified)

1. CREATED
2. PLANNED
3. POLICY_EVALUATED
4. EXECUTING
5. AWAITING_APPROVAL
6. COMPLETED
7. FAILED

## Auth0 + Token Vault Execution Pattern

1. User authenticates with Auth0.
2. User connects provider account through an Auth0 Connection.
3. ConsentOps service receives user-scoped Auth0 context.
4. Tool runtime requests provider access token through Token Vault path.
5. Adapter calls provider API using short-lived scoped token.
6. Adapter returns normalized result; audit logs token source as `token_vault` (not token value).

## AWS Mapping

1. API Gateway + Lambda: ingress
2. Step Functions: orchestration
3. SQS/EventBridge: async action queueing
4. DynamoDB or Postgres: run + event persistence
5. CloudWatch: logs/metrics/traces

## Security Notes

1. Deny execution when required connection is missing.
2. Deny execution when requested scope is not granted.
3. Deny execution when policy decision is uncertain.
4. Log only token metadata, never token secrets.

