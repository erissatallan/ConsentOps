"""Authentication helpers for the API gateway.

header parsing is its own concern,
it keeps app.py smaller,
it gives us a clear place to later add JWT validation.
"""

from fastapi import Header, HTTPException


def extract_bearer_token(authorization: str | None = Header(default=None)) -> str | None:
    if authorization is None:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")

    return token.strip()
