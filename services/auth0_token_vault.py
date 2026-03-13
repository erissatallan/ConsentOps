"""Auth0 Token Vault integration seam.

This module is intentionally split out so the rest of the codebase does not
need to know the details of Token Vault exchange.

This is the correct abstraction boundary.
The tool runtime should depend on a Token Vault client, not on Auth0 internals.
When we wire the real HTTP exchange later, one file changes instead of five.
"""

from services.settings import settings

class TokenVaultExchangeError(Exception):
    """Raised when a Token Vault exchange cannot be completed."""

def get_connection_name_for_provider(provider: str) -> str:
    if provider == "google":
        return settings.auth0_google_connection
    if provider == "slack":
        return settings.auth0_slack_connection
    raise TokenVaultExchangeError(f"Unsupported provider '{provider}'")

def exchange_auth0_token_for_provider_token(
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
        "token_source": "token_vault",
        "provider": provider,
        "connection": connection,
        "access_token": f"stub-token-for-{provider}",
        "scopes": scopes
    }