"""Manual Auth0 Token Vault exchange test.

it lets you test Auth0 exchange without invoking the whole workflow,
it gives you a deterministic first live integration checkpoint,
it avoids exposing tokens in terminal output."""


import argparse
import json

from services.auth0_token_vault import exchange_auth0_token_for_provider_token


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=["google", "slack"])
    parser.add_argument("--subject-token", required=True)
    parser.add_argument("--scope", action="append", default=[])
    args = parser.parse_args()

    result = exchange_auth0_token_for_provider_token(
        auth0_subject_token=args.subject_token,
        provider=args.provider,
        scopes=args.scope,
    )

    safe_result = {
        key: value
        for key, value in result.items()
        if key != "access_token"
    }

    print(json.dumps(safe_result, indent=2))


if __name__ == "__main__":
    main()
