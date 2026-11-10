from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import apply_rls_context, get_db
from app.core.security import constant_time_equals, hash_token
from app.modules.accounts.models import Membership
from app.modules.auth.models import UserSession
from app.modules.users.models import User
from app.shared.exceptions import ForbiddenError, UnauthorizedError


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass
class CurrentAuthContext:
    user: User
    session: UserSession
    active_account_id: UUID | None
    active_role: str | None


def get_current_auth(
    request: Request,
    db: Session = Depends(get_db),
    x_account_id: str | None = Header(default=None, alias="X-Account-ID"),
) -> CurrentAuthContext:
    settings = get_settings()
    raw_session_token = request.cookies.get(settings.session_cookie_name)
    if not raw_session_token:
        raise UnauthorizedError("Sessão ausente ou expirada.")

    token_hash = hash_token(raw_session_token)
    row = db.execute(
        select(UserSession, User)
        .join(User, User.id == UserSession.user_id)
        .where(UserSession.token_hash == token_hash)
    ).first()
    if not row:
        raise UnauthorizedError("Sessão inválida.")

    session, user = row
    now = datetime.now(timezone.utc)
    if session.revoked_at is not None or ensure_utc(session.expires_at) <= now:
        raise UnauthorizedError("Sessão expirada ou encerrada.")

    apply_rls_context(db, user_id=user.id)

    requested_account_id: UUID | None = None
    if x_account_id:
        try:
            requested_account_id = UUID(x_account_id)
        except ValueError as exc:
            raise ForbiddenError("Cabeçalho X-Account-ID inválido.") from exc

    target_account_id = requested_account_id or session.active_account_id
    active_role: str | None = None

    if target_account_id is not None:
        membership = db.execute(
            select(Membership).where(
                Membership.account_id == target_account_id,
                Membership.user_id == user.id,
                Membership.status == "active",
            )
        ).scalar_one_or_none()
        if membership is None:
            if requested_account_id is not None:
                raise ForbiddenError("Você não pertence à conta solicitada.")
            target_account_id = None
        else:
            active_role = membership.role

    if target_account_id is None:
        fallback_membership = db.execute(
            select(Membership)
            .where(Membership.user_id == user.id, Membership.status == "active")
            .order_by(Membership.created_at.asc())
        ).scalars().first()
        if fallback_membership is not None:
            target_account_id = fallback_membership.account_id
            active_role = fallback_membership.role

    if target_account_id is not None:
        apply_rls_context(db, user_id=user.id, account_id=target_account_id)

    return CurrentAuthContext(
        user=user,
        session=session,
        active_account_id=target_account_id,
        active_role=active_role,
    )


def require_csrf(
    request: Request,
    auth: CurrentAuthContext = Depends(get_current_auth),
) -> None:
    settings = get_settings()
    cookie_csrf = request.cookies.get(settings.csrf_cookie_name)
    header_csrf = request.headers.get("X-CSRF-Token")

    if not cookie_csrf or not header_csrf:
        raise ForbiddenError("Token CSRF ausente.", code="csrf_missing")

    if not constant_time_equals(cookie_csrf, header_csrf):
        raise ForbiddenError("Token CSRF inválido.", code="csrf_mismatch")

    if not constant_time_equals(hash_token(header_csrf), auth.session.csrf_token_hash):
        raise ForbiddenError("Token CSRF não corresponde à sessão.", code="csrf_invalid")

