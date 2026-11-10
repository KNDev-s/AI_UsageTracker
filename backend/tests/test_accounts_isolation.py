from fastapi.testclient import TestClient

from app.core.config import get_settings


def _register_and_get_context(client: TestClient, email: str, full_name: str) -> tuple[dict, str, str]:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": full_name},
    )
    assert resp.status_code == 201
    settings = get_settings()
    session_cookie = client.cookies.get(settings.session_cookie_name)
    csrf_cookie = client.cookies.get(settings.csrf_cookie_name)
    assert session_cookie and csrf_cookie
    return resp.json()["data"], session_cookie, csrf_cookie


def test_cross_tenant_account_isolation(client: TestClient) -> None:
    # User A registers
    data_a, sess_a, csrf_a = _register_and_get_context(client, "usera@example.com", "User A")
    account_a_id = data_a["accounts"][0]["id"]

    # Clear cookies and register User B
    client.cookies.clear()
    data_b, sess_b, csrf_b = _register_and_get_context(client, "userb@example.com", "User B")
    account_b_id = data_b["accounts"][0]["id"]
    assert account_a_id != account_b_id

    # User B lists only their own account
    list_b = client.get("/api/v1/accounts")
    assert list_b.status_code == 200
    assert [acc["id"] for acc in list_b.json()["data"]] == [account_b_id]

    # User B cannot access, modify, export, or delete User A's account
    assert client.get(f"/api/v1/accounts/{account_a_id}").status_code == 403
    assert (
        client.patch(
            f"/api/v1/accounts/{account_a_id}",
            json={"name": "Hacked"},
            headers={"X-CSRF-Token": csrf_b},
        ).status_code
        == 403
    )
    assert (
        client.delete(
            f"/api/v1/accounts/{account_a_id}",
            headers={"X-CSRF-Token": csrf_b},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/accounts/{account_a_id}/export",
            headers={"X-CSRF-Token": csrf_b},
        ).status_code
        == 403
    )
    assert client.get(f"/api/v1/accounts/{account_a_id}/members").status_code == 403

    # User B spoofing X-Account-ID header is rejected with 403
    spoof_resp = client.get("/api/v1/auth/me", headers={"X-Account-ID": account_a_id})
    assert spoof_resp.status_code == 403

    # User A can create a second workspace and switch context via X-Account-ID
    settings = get_settings()
    client.cookies.clear()
    client.cookies.set(settings.session_cookie_name, sess_a)
    client.cookies.set(settings.csrf_cookie_name, csrf_a)

    create_resp = client.post(
        "/api/v1/accounts",
        json={"name": "Equipe Alpha", "type": "team", "currency": "USD"},
        headers={"X-CSRF-Token": csrf_a},
    )
    assert create_resp.status_code == 201
    second_account_id = create_resp.json()["data"]["id"]

    switched = client.get("/api/v1/auth/me", headers={"X-Account-ID": second_account_id})
    assert switched.status_code == 200
    assert switched.json()["data"]["active_account_id"] == second_account_id

