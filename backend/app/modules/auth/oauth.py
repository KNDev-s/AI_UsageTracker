import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.shared.exceptions import AppException, UnauthorizedError

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
OAUTH_STATE_COOKIE = "ai_tracker_oauth_state"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _sign_payload(payload: dict) -> str:
    settings = get_settings()
    encoded = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(
        settings.secret_key.encode("utf-8"),
        encoded.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded}.{_b64url(sig)}"


def verify_signed_oauth_cookie(cookie_value: str | None) -> dict:
    if not cookie_value or "." not in cookie_value:
        raise UnauthorizedError("Estado OAuth ausente ou inválido.")
    encoded, sig_b64 = cookie_value.split(".", 1)
    settings = get_settings()
    expected_sig = hmac.new(
        settings.secret_key.encode("utf-8"),
        encoded.encode("ascii"),
        hashlib.sha256,
    ).digest()
    try:
        provided_sig = _b64url_decode(sig_b64)
    except Exception as exc:
        raise UnauthorizedError("Assinatura OAuth inválida.") from exc

    if not hmac.compare_digest(expected_sig, provided_sig):
        raise UnauthorizedError("Assinatura OAuth inválida.")

    try:
        payload = json.loads(_b64url_decode(encoded).decode("utf-8"))
    except Exception as exc:
        raise UnauthorizedError("Payload OAuth inválido.") from exc

    if payload.get("exp", 0) < int(time.time()):
        raise UnauthorizedError("Fluxo de login Google expirado. Tente novamente.")
    return payload


def create_google_authorization() -> tuple[str, str]:
    settings = get_settings()
    if not settings.google_oauth_enabled:
        raise AppException(
            status_code=503,
            code="google_oauth_not_configured",
            message="Google OAuth não está configurado neste ambiente.",
        )

    state = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(48)
    code_challenge = _b64url(hashlib.sha256(code_verifier.encode("ascii")).digest())

    cookie_token = _sign_payload(
        {
            "state": state,
            "code_verifier": code_verifier,
            "exp": int(time.time()) + 600,
        }
    )

    params = {
        "client_id": settings.google_oauth_client_id,
        "redirect_uri": settings.google_oauth_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}", cookie_token


def exchange_google_code(*, code: str, code_verifier: str) -> dict:
    settings = get_settings()
    with httpx.Client(timeout=15.0) as client:
        token_resp = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "code": code,
                "code_verifier": code_verifier,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_oauth_redirect_uri,
            },
        )
        if token_resp.status_code != 200:
            raise UnauthorizedError("Falha ao validar código de autorização com o Google.")
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise UnauthorizedError("Token de acesso do Google ausente.")

        userinfo_resp = client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_resp.status_code != 200:
            raise UnauthorizedError("Não foi possível obter perfil do Google.")
        userinfo = userinfo_resp.json()

    if not userinfo.get("sub") or not userinfo.get("email"):
        raise UnauthorizedError("Dados essenciais do Google OIDC não retornados.")
    return userinfo

