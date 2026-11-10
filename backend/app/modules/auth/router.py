from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import auth_rate_limiter, constant_time_equals
from app.modules.auth import oauth, service
from app.modules.auth.dependencies import CurrentAuthContext, get_current_auth, require_csrf
from app.modules.auth.schemas import (
    AuthSessionOut,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.shared.exceptions import RateLimitError, UnauthorizedError
from app.shared.schemas import APIResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _enforce_rate_limit(request: Request) -> None:
    settings = get_settings()
    ip = _client_ip(request) or "unknown"
    key = f"{request.url.path}:{ip}"
    if not auth_rate_limiter.allow(
        key,
        max_attempts=settings.auth_rate_limit_max_attempts,
        window_seconds=settings.auth_rate_limit_window_seconds,
    ):
        raise RateLimitError()


def _set_auth_cookies(response: Response, *, raw_session: str, raw_csrf: str) -> None:
    settings = get_settings()
    max_age = settings.session_ttl_hours * 3600
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_session,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=raw_csrf,
        max_age=max_age,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    settings = get_settings()
    for cookie_name in (settings.session_cookie_name, settings.csrf_cookie_name):
        response.delete_cookie(
            key=cookie_name,
            domain=settings.cookie_domain,
            path="/",
        )


@router.post(
    "/register",
    response_model=APIResponse[AuthSessionOut],
    status_code=201,
    dependencies=[Depends(_enforce_rate_limit)],
)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> APIResponse[AuthSessionOut]:
    tokens = service.register_user(
        db,
        payload=payload,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    _set_auth_cookies(
        response, raw_session=tokens.raw_session_token, raw_csrf=tokens.raw_csrf_token
    )
    return APIResponse(data=tokens.session_out)


@router.post(
    "/login",
    response_model=APIResponse[AuthSessionOut],
    dependencies=[Depends(_enforce_rate_limit)],
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> APIResponse[AuthSessionOut]:
    tokens = service.login_user(
        db,
        email=payload.email,
        password=payload.password,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    _set_auth_cookies(
        response, raw_session=tokens.raw_session_token, raw_csrf=tokens.raw_csrf_token
    )
    return APIResponse(data=tokens.session_out)


@router.post(
    "/logout",
    response_model=APIResponse[dict[str, bool]],
    dependencies=[Depends(require_csrf)],
)
def logout(
    request: Request,
    response: Response,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, bool]]:
    service.logout_session(
        db,
        session=auth.session,
        user=auth.user,
        active_account_id=auth.active_account_id,
        ip_address=_client_ip(request),
    )
    _clear_auth_cookies(response)
    return APIResponse(data={"logged_out": True})


@router.post(
    "/refresh",
    response_model=APIResponse[AuthSessionOut],
    dependencies=[Depends(require_csrf)],
)
def refresh(
    response: Response,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[AuthSessionOut]:
    tokens = service.refresh_session(
        db,
        session=auth.session,
        user=auth.user,
        active_account_id=auth.active_account_id,
    )
    _set_auth_cookies(
        response, raw_session=tokens.raw_session_token, raw_csrf=tokens.raw_csrf_token
    )
    return APIResponse(data=tokens.session_out)


@router.get("/me", response_model=APIResponse[AuthSessionOut])
def me(
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[AuthSessionOut]:
    session_out = service.build_auth_session_out(
        db, user=auth.user, active_account_id=auth.active_account_id
    )
    return APIResponse(data=session_out)


@router.post(
    "/verify-email",
    response_model=APIResponse[dict[str, bool]],
    dependencies=[Depends(_enforce_rate_limit)],
)
def verify_email(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, bool]]:
    service.verify_email_token(db, raw_token=payload.token)
    return APIResponse(data={"verified": True})


@router.post(
    "/resend-verification",
    response_model=APIResponse[dict[str, bool]],
    dependencies=[Depends(_enforce_rate_limit), Depends(require_csrf)],
)
def resend_verification(
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, bool]]:
    service.resend_verification_email(db, user=auth.user)
    return APIResponse(data={"sent": True})


@router.post(
    "/forgot-password",
    response_model=APIResponse[dict[str, bool]],
    dependencies=[Depends(_enforce_rate_limit)],
)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, bool]]:
    service.request_password_reset(db, email=payload.email)
    return APIResponse(data={"accepted": True})


@router.post(
    "/reset-password",
    response_model=APIResponse[dict[str, bool]],
    dependencies=[Depends(_enforce_rate_limit)],
)
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, bool]]:
    service.reset_password_with_token(
        db,
        raw_token=payload.token,
        new_password=payload.new_password,
        ip_address=_client_ip(request),
    )
    return APIResponse(data={"reset": True})


@router.get("/google")
def google_login_start() -> RedirectResponse:
    settings = get_settings()
    authorize_url, state_cookie = oauth.create_google_authorization()
    response = RedirectResponse(url=authorize_url, status_code=302)
    response.set_cookie(
        key=oauth.OAUTH_STATE_COOKIE,
        value=state_cookie,
        max_age=600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
    )
    return response


@router.get("/google/callback")
def google_login_callback(
    request: Request,
    code: str = Query(min_length=1),
    state: str = Query(min_length=1),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    signed_state = request.cookies.get(oauth.OAUTH_STATE_COOKIE)
    state_payload = oauth.verify_signed_oauth_cookie(signed_state)
    if not constant_time_equals(state, state_payload.get("state", "")):
        raise UnauthorizedError("Estado OAuth não corresponde à solicitação.")

    userinfo = oauth.exchange_google_code(
        code=code, code_verifier=state_payload["code_verifier"]
    )
    tokens, is_new_user = service.upsert_google_user(
        db,
        google_sub=userinfo["sub"],
        email=userinfo["email"],
        email_verified=bool(userinfo.get("email_verified", False)),
        full_name=userinfo.get("name") or userinfo["email"],
        avatar_url=userinfo.get("picture"),
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )

    dest_path = "/onboarding" if is_new_user else "/dashboard"
    redirect_url = f"{settings.app_base_url.rstrip('/')}{dest_path}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.delete_cookie(
        key=oauth.OAUTH_STATE_COOKIE,
        domain=settings.cookie_domain,
        path="/",
    )
    _set_auth_cookies(
        response, raw_session=tokens.raw_session_token, raw_csrf=tokens.raw_csrf_token
    )
    return response

