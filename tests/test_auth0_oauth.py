from services.api_gateway import auth0_oauth


class DummyResponse:
    def __init__(self, status_code: int, payload: dict, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


def test_build_authorize_url_contains_expected_values(monkeypatch):
    monkeypatch.setattr(auth0_oauth.settings, "auth0_domain", "dev-h3ju1czcy8nqnfmx.us.auth0.com")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_client_id", "client-id")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_redirect_uri", "http://127.0.0.1:8000/auth/callback")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_login_scope", "openid profile email offline_access")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_audience", "https://api.consentops.local")

    url = auth0_oauth.build_authorize_url()

    assert url.startswith("https://dev-h3ju1czcy8nqnfmx.us.auth0.com/authorize?")
    assert "response_type=code" in url
    assert "client_id=client-id" in url
    assert "redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fauth%2Fcallback" in url


def test_exchange_code_for_tokens_success(monkeypatch):
    monkeypatch.setattr(auth0_oauth.settings, "auth0_domain", "dev-h3ju1czcy8nqnfmx.us.auth0.com")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_client_id", "client-id")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_client_secret", "client-secret")
    monkeypatch.setattr(auth0_oauth.settings, "auth0_redirect_uri", "http://127.0.0.1:8000/auth/callback")

    def fake_post(url, json, timeout):
        return DummyResponse(
            200,
            {
                "access_token": "auth0-user-access-token",
                "refresh_token": "refresh-token",
                "scope": "openid profile email offline_access",
                "token_type": "Bearer",
                "expires_in": 86400,
            },
        )

    monkeypatch.setattr(auth0_oauth.requests, "post", fake_post)

    result = auth0_oauth.exchange_code_for_tokens("sample-code")
    assert result["access_token"] == "auth0-user-access-token"


def test_exchange_code_for_tokens_raises_on_auth0_error(monkeypatch):
    monkeypatch.setattr(auth0_oauth.settings, "auth0_domain", "dev-h3ju1czcy8nqnfmx.us.auth0.com")

    def fake_post(url, json, timeout):
        return DummyResponse(401, {}, text="unauthorized")

    monkeypatch.setattr(auth0_oauth.requests, "post", fake_post)

    try:
        auth0_oauth.exchange_code_for_tokens("bad-code")
        assert False, "Expected Auth0OAuthError"
    except auth0_oauth.Auth0OAuthError as exc:
        assert "failed with status 401" in str(exc)
