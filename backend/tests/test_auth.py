import re
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.email import email_service
from app.modules.auth import oauth


def _extract_token_from_last_email() -> str:
    assert email_service.outbox, "Expected an email in outbox"
    body = email_service.outbox[-1].body_text
    match = re.search(r"token=([A-Za-z0-9\-_]+)", body)
    assert match, f"Token not found in email body: {body}"
    return match.group(1)


def _csrf_headers(client: TestClient) -> dict[str, str]:
    settings = get_settings()
    csrf = client.cookies.get(settings.csrf_cookie_name)
    assert csrf, "Expected CSRF cookie to be set"
    return {"X-CSRF-Token": csrf}


def test_register_login_verify_and_logout_flow(client: TestClient) -> None:
    # 1. Register
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Igor@Example.com",
            "password": "StrongPassword123!",
            "full_name": "Igor Silva",
        },
    )
    assert reg_resp.status_code == 201
    body = reg_resp.json()
    assert body["success"] is True
    assert body["data"]["user"]["email"] == "igor@example.com"
    assert "password_hash" not in body["data"]["user"]
    assert len(body["data"]["accounts"]) == 1
    assert body["data"]["accounts"][0]["type"] == "individual"
    assert body["data"]["accounts"][0]["role"] == "owner"

    settings = get_settings()
    assert client.cookies.get(settings.session_cookie_name)
    assert client.cookies.get(settings.csrf_cookie_name)

    # Duplicate registration fails with 409
    dup_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "igor@example.com",
            "password": "StrongPassword123!",
            "full_name": "Igor Duplicate",
        },
    )
    assert dup_resp.status_code == 409

    # 2. Verify email from outbox token
    verify_token = _extract_token_from_last_email()
    verify_resp = client.post("/api/v1/auth/verify-email", json={"token": verify_token})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["data"]["verified"] is True

    # Reusing the same verification token fails
    reuse_resp = client.post("/api/v1/auth/verify-email", json={"token": verify_token})
    assert reuse_resp.status_code == 422

    # 3. Check /auth/me shows verified timestamp
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["user"]["email_verified_at"] is not None

    # 4. Logout without CSRF fails, with CSRF succeeds
    bad_logout = client.post("/api/v1/auth/logout")
    assert bad_logout.status_code == 403

    ok_logout = client.post("/api/v1/auth/logout", headers=_csrf_headers(client))
    assert ok_logout.status_code == 200

    # Session is revoked
    after_logout = client.get("/api/v1/auth/me")
    assert after_logout.status_code == 401

    # 5. Login with wrong password fails; right password succeeds
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "igor@example.com", "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401

    ok_login = client.post(
        "/api/v1/auth/login",
        json={"email": "igor@example.com", "password": "StrongPassword123!"},
    )
    assert ok_login.status_code == 200


def test_refresh_rotates_session_and_password_reset_revokes_sessions(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "reset@example.com",
            "password": "OldPassword123!",
            "full_name": "Reset User",
        },
    )
    settings = get_settings()
    first_session = client.cookies.get(settings.session_cookie_name)

    # Refresh rotates session cookie
    refresh_resp = client.post("/api/v1/auth/refresh", headers=_csrf_headers(client))
    assert refresh_resp.status_code == 200
    second_session = client.cookies.get(settings.session_cookie_name)
    assert second_session and second_session != first_session

    # Forgot password works silently even for unknown emails
    unknown_resp = client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@example.com"}
    )
    assert unknown_resp.status_code == 200

    email_service.clear_outbox()
    forgot_resp = client.post(
        "/api/v1/auth/forgot-password", json={"email": "reset@example.com"}
    )
    assert forgot_resp.status_code == 200
    reset_token = _extract_token_from_last_email()

    reset_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewPassword456!"},
    )
    assert reset_resp.status_code == 200

    # Previous session must now be revoked
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401

    # Login with new password works
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "reset@example.com", "password": "NewPassword456!"},
    )
    assert login_resp.status_code == 200


def test_auth_rate_limiting(client: TestClient) -> None:
    for _ in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.com", "password": "bad"},
        )
        assert resp.status_code == 401

    limited = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "bad"},
    )
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "rate_limited"


def test_google_oauth_flow(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")
    get_settings.cache_clear()

    def fake_exchange(*, code: str, code_verifier: str) -> dict:
        assert code == "auth-code-123"
        assert len(code_verifier) > 20
        return {
            "sub": "google-sub-999",
            "email": "oauth.user@example.com",
            "email_verified": True,
            "name": "OAuth User",
            "picture": "https://example.com/avatar.png",
        }

    monkeypatch.setattr(oauth, "exchange_google_code", fake_exchange)

    start_resp = client.get("/api/v1/auth/google", follow_redirects=False)
    assert start_resp.status_code == 302
    location = start_resp.headers["location"]
    parsed = urlparse(location)
    params = parse_qs(parsed.query)
    assert parsed.netloc == "accounts.google.com"
    assert "state" in params
    assert params["code_challenge_method"] == ["S256"]

    # Tampered state must be rejected
    bad_cb = client.get(
        "/api/v1/auth/google/callback",
        params={"code": "auth-code-123", "state": "tampered-state"},
        follow_redirects=False,
    )
    assert bad_cb.status_code == 401

    # Valid state creates user + session and redirects to /onboarding
    ok_cb = client.get(
        "/api/v1/auth/google/callback",
        params={"code": "auth-code-123", "state": params["state"][0]},
        follow_redirects=False,
    )
    assert ok_cb.status_code == 302
    assert ok_cb.headers["location"].endswith("/onboarding")

    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["user"]["email"] == "oauth.user@example.com"
    assert me_resp.json()["data"]["user"]["email_verified_at"] is not None

    # Second OAuth login redirects to /dashboard
    start_resp_2 = client.get("/api/v1/auth/google", follow_redirects=False)
    state_2 = parse_qs(urlparse(start_resp_2.headers["location"]).query)["state"][0]
    ok_cb_2 = client.get(
        "/api/v1/auth/google/callback",
        params={"code": "auth-code-123", "state": state_2},
        follow_redirects=False,
    )
    assert ok_cb_2.status_code == 302
    assert ok_cb_2.headers["location"].endswith("/dashboard")

    get_settings.cache_clear()

