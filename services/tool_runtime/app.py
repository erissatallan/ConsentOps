"""Tool runtime dispatcher scaffold.

The goal is normalized execution and routing.
"""

"""
def get_provider_token_via_token_vault(*, user_id: str, provider: str, scopes: list[str]) -> dict:

    PSEUDOCODE:
    1) Resolve user's connected account for provider.
    2) Request user-scoped access token via Auth0 Token Vault API/SDK path.
    3) Validate returned token metadata includes required scopes.
    4) Return token handle/object for adapter use.

    return {
        "token_source": "token_vault",
        "access_token": "REPLACE_WITH_REAL_TOKEN_AT_RUNTIME",
        "scopes": scopes,
    }


def dispatch_action(action: dict, actor_context: dict) -> dict:

    PSEUDOCODE:
    1) Verify idempotency key.
    2) Route to adapter by action prefix.
    3) Acquire provider token via Token Vault.
    4) Enforce timeout and retry policy.
    5) Return normalized execution result.

    provider = action.get("provider", "unknown")
    scopes = action.get("required_scopes", [])

    token_bundle = get_provider_token_via_token_vault(
        user_id=actor_context.get("user_id", "unknown"),
        provider=provider,
        scopes=scopes,
    )

    return {
        "status": "stubbed",
        "action": action,
        "token_source": token_bundle.get("token_source"),
    }

dispatch_action now does real routing.
Unsupported actions fail loudly instead of silently returning junk.
Adapters stay small and provider-specific.
"""


from services.adapters_gmail.app import send_reply
from services.adapters_slack.app import post_message
from services.auth0_token_vault import exchange_auth0_token_for_provider_token

def dispatch_action(action: dict, actor_context: dict) -> dict:
    provider = action.get("provider", "unknown")
    scopes = action.get("required_scopes", [])
    auth0_subject_token = actor_context.get("auth0_subject_token")
    payload = action.get("payload", {})
    if not isinstance(payload, dict):
        raise ValueError("Action payload must be a dictionary")

    token_bundle = exchange_auth0_token_for_provider_token(
        auth0_subject_token=auth0_subject_token,
        provider=provider,
        scopes=scopes,
    )

    action_name = action.get("action")

    if action_name == "slack.post_message":
        result = post_message(
            payload=payload,
            token_bundle=token_bundle,
        )
    elif action_name == "gmail.send_reply":
        result = send_reply(
            message=payload,
            token_bundle=token_bundle,
        )
    else:
        raise ValueError(f"Unsupported action '{action_name}'")

    return {
        "status": "succeeded",
        "action": action_name,
        "provider": provider,
        "token_source": token_bundle.get("token_source"),
        "result": result,
    }
