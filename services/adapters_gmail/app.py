"""Gmail adapter scaffold."""

import requests

"""
def send_reply(message: dict, token_bundle: dict) -> dict:
    
    PSEUDOCODE:
    1) Build Gmail API payload.
    2) Use token_bundle access token from Token Vault runtime flow.
    3) Send API request.
    4) Return provider message ID and metadata.
    
    return {
        "status": "stubbed",
        "provider": "gmail",
        "message": message,
        "token_source": token_bundle.get("token_source", "unknown"),
    }
"""

def send_reply(message: dict, token_bundle: dict) -> dict:
    subject = message.get("subject")
    body = message.get("body")

    if not subject:
        raise ValueError("Gmail message must include 'subject'.")
    if not body:
        raise ValueError("Gmail message must include 'body'.")

    return {
        "status": "stubbed",
        "provider": "gmail",
        "subject": subject,
        "body_preview": body[:80],
        "token_source": token_bundle.get("token_source", "unknown"),
        "connection": token_bundle.get("connection", "unknown"),
    }
