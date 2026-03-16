from services import auth0_token_vault


class DummyResponse:
    def __init__(self, status_code: int, payload: dict, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


def test_exchange_stub_returns_stubbed_provider_token(monkeypatch):
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_token_vault_mode", "stub")

    result = auth0_token_vault.exchange_auth0_token_for_provider_token(
        auth0_subject_token="dummy-auth0-token",
        provider="slack",
        scopes=["slack:chat:write"],
    )

    assert result["token_source"] == "token_vault_stub"
    assert result["provider"] == "slack"
    assert result["connection"] == auth0_token_vault.settings.auth0_slack_connection


def test_exchange_live_posts_to_auth0(monkeypatch):
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_token_vault_mode", "live")
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_domain", "example.us.auth0.com")
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_client_id", "client-id")
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_client_secret", "client-secret")
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_google_connection", "google-oauth2")

    captured = {}

    def fake_post(url, data, timeout):
        captured["url"] = url
        captured["data"] = data
        captured["timeout"] = timeout
        return DummyResponse(
            200,
            {
                "access_token": "provider-access-token",
                "expires_in": 3600,
                "issued_token_type": "http://auth0.com/oauth/token-type/federated-connection-access-token",
            },
        )

    monkeypatch.setattr(auth0_token_vault.requests, "post", fake_post)

    result = auth0_token_vault.exchange_auth0_token_for_provider_token(
        auth0_subject_token="auth0-access-token",
        provider="google",
        scopes=["gmail.send"],
    )

    assert captured["url"] == "https://example.us.auth0.com/oauth/token"
    assert captured["data"]["grant_type"] == "urn:auth0:params:oauth:grant-type:token-exchange:federated-connection-access-token"
    assert captured["data"]["subject_token_type"] == "urn:ietf:params:oauth:token-type:access_token"
    assert captured["data"]["requested_token_type"] == "http://auth0.com/oauth/token-type/federated-connection-access-token"
    assert captured["data"]["connection"] == "google-oauth2"
    assert result["token_source"] == "token_vault_live"
    assert result["access_token"] == "provider-access-token"


def test_exchange_live_raises_on_auth0_error(monkeypatch):
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_token_vault_mode", "live")

    def fake_post(url, data, timeout):
        return DummyResponse(401, {}, text="unauthorized")

    monkeypatch.setattr(auth0_token_vault.requests, "post", fake_post)

    try:
        auth0_token_vault.exchange_auth0_token_for_provider_token(
            auth0_subject_token="bad-token",
            provider="slack",
            scopes=["slack:chat:write"],
        )
        assert False, "Expected TokenVaultExchangeError"
    except auth0_token_vault.TokenVaultExchangeError as exc:
        assert "failed with status 401" in str(exc)


def test_exchange_live_raises_on_request_exception(monkeypatch):
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_token_vault_mode", "live")

    def fake_post(url, data, timeout):
        raise auth0_token_vault.requests.RequestException("network down")

    monkeypatch.setattr(auth0_token_vault.requests, "post", fake_post)

    try:
        auth0_token_vault.exchange_auth0_token_for_provider_token(
            auth0_subject_token="auth0-access-token",
            provider="slack",
            scopes=["slack:chat:write"],
        )
        assert False, "Expected TokenVaultExchangeError"
    except auth0_token_vault.TokenVaultExchangeError as exc:
        assert "request failed" in str(exc)


def test_exchange_live_raises_on_non_json_response(monkeypatch):
    monkeypatch.setattr(auth0_token_vault.settings, "auth0_token_vault_mode", "live")

    class NonJsonResponse:
        status_code = 200
        text = "ok"

        def json(self):
            raise auth0_token_vault.json.JSONDecodeError("bad json", "doc", 0)

    def fake_post(url, data, timeout):
        return NonJsonResponse()

    monkeypatch.setattr(auth0_token_vault.requests, "post", fake_post)

    try:
        auth0_token_vault.exchange_auth0_token_for_provider_token(
            auth0_subject_token="auth0-access-token",
            provider="slack",
            scopes=["slack:chat:write"],
        )
        assert False, "Expected TokenVaultExchangeError"
    except auth0_token_vault.TokenVaultExchangeError as exc:
        assert "non-JSON response" in str(exc)

