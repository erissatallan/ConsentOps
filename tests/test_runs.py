from fastapi.testclient import TestClient
from services.api_gateway.app import app
from services.adapters_gmail.app import send_reply

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_gmail_run_pauses_for_approval_without_requiring_token_exchange():
    # should keep working without it, because no token exchange occurs before approval
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
    assert body["plan"][0]["payload"]["to"] == "customer@example.com"
    assert body["plan"][0]["payload"]["subject"] == "Re: Your request"
    assert body["status"] == "awaiting_approval"
    assert any(event["event_type"] == "run.awaiting_approval" for event in body["timeline"])

def test_slack_run_rejects_invalid_authorization_header():
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
        headers={"Authorization": "Token not-a-bearer-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Authorization header format."

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
                "connected_accounts": ["slack"]
            },
        },
        headers={"Authorization": "Bearer dummy-auth0-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["plan"][0]["payload"]["channel"] == "ops-review"
    assert body["plan"][0]["payload"]["text"] == "ConsentOps Mesh automated notification"
    assert body["status"] == "completed"
    assert any(event["event_type"] == "run.action_succeeded" for event in body["timeline"])

def test_gmail_adapter_requires_recipient():
    try:
        send_reply(
            message={"subject": "Hello", "body": "World"},
            token_bundle={"token_source": "token_vault", "connection": "google-oauth2"},
        )
        assert False, "Expected ValueError for missing recipient"
    except ValueError as exc:
        assert "must include 'to'" in str(exc)
