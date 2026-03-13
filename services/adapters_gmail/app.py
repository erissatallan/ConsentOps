"""Gmail adapter scaffold."""

import requests


def send_reply(message: dict, token_bundle: dict) -> dict:
    """
    PSEUDOCODE:
    1) Build Gmail API payload.
    2) Use token_bundle access token from Token Vault runtime flow.
    3) Send API request.
    4) Return provider message ID and metadata.
    """
    return {
        "status": "stubbed",
        "provider": "gmail",
        "message": message,
        "token_source": token_bundle.get("token_source", "unknown"),
    }
