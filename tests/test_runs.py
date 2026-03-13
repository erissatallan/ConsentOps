from fastapi.testclient import TestClient

from services.api_gateway.app import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_gmail_run_pauses_for_approval_without_requiring_token_exchange():
    response = client.post(
        "/v1/runs",
        json={
            "intent": "Send an email reply to the customer.",
            "actor_context": {
                "user_id": "user_123",
                "tenant_id": "tenant_demo",
                "granted_scopes": ["gmail.send"],
                "connected_accounts": ["google"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "awaiting_approval"
    assert any(event["event_type"] == "run.awaiting_approval" for event in body["timeline"])


def test_slack_run_requires_auth0_subject_token_for_live_dispatch():
    response = client.post(
        "/v1/runs",
        json={
            "intent": "Notify Slack that the incident has been acknowledged.",
            "actor_context": {
                "user_id": "user_123",
                "tenant_id": "tenant_demo",
                "granted_scopes": ["slack:chat:write"],
                "connected_accounts": ["slack"],
            },
        },
    )

    assert response.status_code >= 400


def test_slack_run_succeeds_with_auth0_subject_token():
    response = client.post(
        "/v1/runs",
        json={
            "intent": "Notify Slack that the incident has been acknowledged.",
            "actor_context": {
                "user_id": "user_123",
                "tenant_id": "tenant_demo",
                "granted_scopes": ["slack:chat:write"],
                "connected_accounts": ["slack"],
                "auth0_subject_token": "dummy-auth0-token",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert any(event["event_type"] == "run.action_succeeded" for event in body["timeline"])
