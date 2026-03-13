"""Slack adapter scaffold."""

"""
def post_message(payload: dict, token_bundle: dict) -> dict:
    PSEUDOCODE:
    1) Resolve channel and thread context.
    2) Use token_bundle access token from Token Vault runtime flow.
    3) Send chat.postMessage.
    4) Return ts/channel metadata.

    return {
        "status": "stubbed",
        "provider": "slack",
        "payload": payload,
        "token_source": token_bundle.get("token_source", "unknown"),
    }
"""

def post_message(payload: dict, token_bundle: dict) -> dict:
    channel = payload.get("channel")
    text = payload.get("text")

    if not channel:
        raise ValueError("Slack payload must include 'channel'.")
    if not text:
        raise ValueError("Slack payload must include 'text'.")

    return {
        "status": "stubbed",
        "provider": "slack",
        "channel": channel,
        "text": text,
        "token_source": token_bundle.get("token_source", "unknown"),
        "connection": token_bundle.get("connection", "unknown"),
    }
