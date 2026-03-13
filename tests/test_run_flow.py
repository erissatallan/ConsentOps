"""
Why this test now:

It locks the business behavior before we introduce real network calls.
It protects the approval boundary, which is central to the hackathon pitch.
It gives us confidence to refactor toward live Auth0 integration later.
"""

from fastapi.testclient import TestClient
from services.api_gateway.app import app

client = TestClient(app)

def test_slack_run_completes():
    response = client.post(
        "/v1/runs",
        json={
            "intent": "Notify Slack that the incident has been acknowledged.",
            "actor_context": {
                "user_id": "user_123",
                "tenant_id": "tenant_demo",
                "granted_scopes": ["slack:chat:write"],
                "connected_accounts": ["slack"],
                "auth0_subject_token": "fake-auth0-token",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert any(event["event_type"] == "run.completed" for event in body["timeline"])

def test_gmail_run_requires_approval():
    response = client.post(
        "/v1/runs",
        json={
            "intent": "Send an email reply to the customer.",
            "actor_context": {
                "user_id": "user_123",
                "tenant_id": "tenant_demo",
                "granted_scopes": ["gmail.send"],
                "connected_accounts": ["google"],
                "auth0_subject_token": "fake-auth0-token",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "awaiting_approval"
    assert any(event["event_type"] == "run.awaiting_approval" for event in body["timeline"])












