"""Auth0 OAuth helpers for development login flow."""

from urllib.parse import urlencode

import requests

from services.settings import settings


class Auth0OAuthError(Exception):
    """Raised when the Auth0 OAuth flow fails."""


def build_authorize_url() -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.auth0_client_id,
            "redirect_uri": settings.auth0_redirect_uri,
            "scope": settings.auth0_login_scope,
            "audience": settings.auth0_audience,
        }
    )
    return f"https://{settings.auth0_domain}/authorize?{query}"


def exchange_code_for_tokens(code: str) -> dict:
    token_url = f"https://{settings.auth0_domain}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.auth0_client_id,
        "client_secret": settings.auth0_client_secret,
        "code": code,
        "redirect_uri": settings.auth0_redirect_uri,
    }

    try:
        response = requests.post(
            token_url,
            json=payload,
            timeout=settings.auth0_token_vault_timeout_seconds,
        )
    except requests.RequestException as exc:
        raise Auth0OAuthError(f"Auth0 token exchange request failed: {exc}") from exc

    if response.status_code != 200:
        raise Auth0OAuthError(
            f"Auth0 token exchange failed with status {response.status_code}: {response.text}"
        )

    body = response.json()
    if "access_token" not in body:
        raise Auth0OAuthError("Auth0 token exchange succeeded but no access_token was returned.")

    return body
