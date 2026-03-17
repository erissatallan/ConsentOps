"""Auth0 Token Vault integration seam.

This module is intentionally split out so the rest of the codebase does not
need to know the details of Token Vault exchange.

This is the correct abstraction boundary.
The tool runtime should depend on a Token Vault client, not on Auth0 internals.
When we wire the real HTTP exchange later, one file changes instead of five.
"""

import requests
import json
from services.settings import settings

class TokenVaultExchangeError(Exception):
    """Raised when a Token Vault exchange cannot be completed."""

def get_connection_name_for_provider(provider: str) -> str:
    if provider == "google":
        return settings.auth0_google_connection
    if provider == "slack":
        return settings.auth0_slack_connection
    raise TokenVaultExchangeError(f"Unsupported provider '{provider}'")

def _validate_live_config() -> None:
    invalid_values = {
        "AUTH0_DOMAIN": not settings.auth0_domain.strip() or settings.auth0_domain == "example.us.auth0.com",
        "AUTH0_CLIENT_ID": settings.auth0_client_id in {"", "placeholder-client-id"},
        "AUTH0_CLIENT_SECRET": settings.auth0_client_secret in {"", "placeholder-client-secret"},        
    }

    missing = [key for key, is_invalid in invalid_values.items() if is_invalid]
    if missing:
        raise TokenVaultExchangeError(
            f"Live Token Vault mode requires valid settings for: {', '.join(missing)}."
        )

def _exchange_stub(
    *,
    auth0_subject_token: str,
    provider: str,
    scopes: list[str],
) -> dict:
    """
    Placeholder for the real Auth0 Token Vault exchange.

    Real implementation plan:
    1. Use the authenticated user's Auth0 token as the subject token.
    2. Exchange it server-side for a provider token tied to the configured connection.
    3. Return only provider token material needed by the adapter call.

    For now, we keep this deterministic so the rest of the system can be built.
    """
    if not auth0_subject_token:
        raise TokenVaultExchangeError("Missing Auth0 subject token for Token Vault exchange.")

    connection = get_connection_name_for_provider(provider)

    return {
        "token_source": "token_vault_stub",
        "provider": provider,
        "connection": connection,
        "access_token": f"stub-token-for-{provider}",
        "scopes": scopes
    }

def _exchange_live(
    *,
    auth0_subject_token: str,
    provider: str,
    scopes: list[str]
) -> dict:

    _validate_live_config()

    if not auth0_subject_token:
        raise TokenVaultExchangeError("Missing Auth0 subject token for Token Vault exchange.")

    connection = get_connection_name_for_provider(provider)
    token_url = f"https://{settings.auth0_domain}/oauth/token"

    form_data = {
            "grant_type": "urn:auth0:params:oauth:grant-type:token-exchange:federated-connection-access-token",
        "client_id": settings.auth0_client_id,
        "client_secret": settings.auth0_client_secret,
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "subject_token": auth0_subject_token,
        "requested_token_type": "http://auth0.com/oauth/token-type/federated-connection-access-token",
        "connection": connection,
    }

    try:
        response = requests.post(
            token_url,
            data=form_data,
            timeout=settings.auth0_token_vault_timeout_seconds,
        )
    except requests.RequestException as exc:
        raise TokenVaultExchangeError(f"Auth0 Token Vault exchange request failed: {exc}") from exc

    if response.status_code != 200:
        raise TokenVaultExchangeError(
            f"Auth0 Token Vault exchange failed with status {response.status_code}: {response.text}"
        )

    try:
        body = response.json()
    except json.JSONDecodeError as exc:
        raise TokenVaultExchangeError("Auth0 Token Vault exchange returned non-JSON response.") from exc
    access_token = body.get("access_token")
    if not access_token:
        raise TokenVaultExchangeError("Auth0 Token Vault exchange succeeded but no access_token was returned.")

    returned_scope = body.get("scope")
    granted_scopes = returned_scope.split() if isinstance(returned_scope, str) else scopes

    return {
        "token_source": "token_vault_live",
        "provider": provider,
        "connection": connection,
        "access_token": access_token,
        "scopes": scopes,
        "requested_scopes": scopes,
        "expires_in": body.get("expires_in"),
        "issued_token_type": body.get("issued_token_type") or body.get("token_type"),
    }    

def exchange_auth0_token_for_provider_token(
    *,
    auth0_subject_token: str,
    provider: str,
    scopes: list[str],
) -> dict:
    mode = settings.auth0_token_vault_mode.lower().strip()

    if mode == "stub":
        return _exchange_stub(
            auth0_subject_token=auth0_subject_token,
            provider=provider,
            scopes=scopes            
        )

    if mode == "live":
        return _exchange_live(
            auth0_subject_token=auth0_subject_token,
            provider=provider,
            scopes=scopes
        )

    raise TokenVaultExchangeError(
        f"Unsupported AUTH0_TOKEN_VAULT_MODE '{settings.auth0_token_vault_mode}'."
    )
