from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import apply_rls_context
from app.modules.accounts.models import Account, Membership
from app.modules.accounts.schemas import AccountCreate, AccountOut, AccountUpdate, MembershipOut
from app.modules.auth.models import AuditLog
from app.modules.users.models import User
from app.shared.exceptions import ForbiddenError, NotFoundError


def _require_membership(
    db: Session, *, account_id: UUID, user_id: UUID, allowed_roles: set[str] | None = None
) -> tuple[Account, Membership]:
    stmt = (
        select(Account, Membership)
        .join(Membership, Membership.account_id == Account.id)
        .where(
            Account.id == account_id,
            Membership.user_id == user_id,
            Membership.status == "active",
        )
    )
    row = db.execute(stmt).first()
    if not row:
        raise ForbiddenError("Você não tem acesso a esta conta.")
    account, membership = row
    if allowed_roles and membership.role not in allowed_roles:
        raise ForbiddenError("Permissão insuficiente para esta operação.")
    return account, membership


def list_user_accounts(db: Session, *, user_id: UUID) -> list[AccountOut]:
    apply_rls_context(db, user_id=user_id)
    stmt = (
        select(Account, Membership.role)
        .join(Membership, Membership.account_id == Account.id)
        .where(Membership.user_id == user_id, Membership.status == "active")
        .order_by(Account.created_at.asc())
    )
    rows = db.execute(stmt).all()
    return [
        AccountOut(
            id=acc.id,
            name=acc.name,
            type=acc.type,
            owner_user_id=acc.owner_user_id,
            timezone=acc.timezone,
            currency=acc.currency,
            created_at=acc.created_at,
            role=role,
        )
        for acc, role in rows
    ]


def create_account(db: Session, *, owner_user_id: UUID, data: AccountCreate) -> AccountOut:
    apply_rls_context(db, user_id=owner_user_id)
    account = Account(
        name=data.name.strip(),
        type=data.type,
        owner_user_id=owner_user_id,
        timezone=data.timezone,
        currency=data.currency.upper(),
    )
    db.add(account)
    db.flush()

    apply_rls_context(db, user_id=owner_user_id, account_id=account.id)
    membership = Membership(
        account_id=account.id,
        user_id=owner_user_id,
        role="owner",
        status="active",
    )
    db.add(membership)
    db.add(
        AuditLog(
            account_id=account.id,
            user_id=owner_user_id,
            action="account.created",
            metadata_json={"type": account.type},
        )
    )
    db.flush()

    return AccountOut(
        id=account.id,
        name=account.name,
        type=account.type,
        owner_user_id=account.owner_user_id,
        timezone=account.timezone,
        currency=account.currency,
        created_at=account.created_at,
        role="owner",
    )


def get_account_for_user(db: Session, *, account_id: UUID, user_id: UUID) -> AccountOut:
    apply_rls_context(db, user_id=user_id, account_id=account_id)
    account, membership = _require_membership(db, account_id=account_id, user_id=user_id)
    return AccountOut(
        id=account.id,
        name=account.name,
        type=account.type,
        owner_user_id=account.owner_user_id,
        timezone=account.timezone,
        currency=account.currency,
        created_at=account.created_at,
        role=membership.role,
    )


def update_account(
    db: Session, *, account_id: UUID, user_id: UUID, data: AccountUpdate
) -> AccountOut:
    apply_rls_context(db, user_id=user_id, account_id=account_id)
    account, membership = _require_membership(
        db, account_id=account_id, user_id=user_id, allowed_roles={"owner", "admin"}
    )
    if data.name is not None:
        account.name = data.name.strip()
    if data.timezone is not None:
        account.timezone = data.timezone
    if data.currency is not None:
        account.currency = data.currency.upper()

    db.add(
        AuditLog(
            account_id=account.id,
            user_id=user_id,
            action="account.updated",
            metadata_json={"fields": list(data.model_dump(exclude_unset=True).keys())},
        )
    )
    db.flush()
    return AccountOut(
        id=account.id,
        name=account.name,
        type=account.type,
        owner_user_id=account.owner_user_id,
        timezone=account.timezone,
        currency=account.currency,
        created_at=account.created_at,
        role=membership.role,
    )


def delete_account(db: Session, *, account_id: UUID, user_id: UUID) -> None:
    apply_rls_context(db, user_id=user_id, account_id=account_id)
    account, _ = _require_membership(
        db, account_id=account_id, user_id=user_id, allowed_roles={"owner"}
    )
    db.add(
        AuditLog(
            account_id=None,
            user_id=user_id,
            action="account.deleted",
            metadata_json={"deleted_account_id": str(account.id)},
        )
    )
    db.delete(account)
    db.flush()


def export_account_data(db: Session, *, account_id: UUID, user_id: UUID) -> dict:
    apply_rls_context(db, user_id=user_id, account_id=account_id)
    account, membership = _require_membership(db, account_id=account_id, user_id=user_id)
    members = list_account_members(db, account_id=account_id, user_id=user_id)
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {
            "id": str(account.id),
            "name": account.name,
            "type": account.type,
            "timezone": account.timezone,
            "currency": account.currency,
            "created_at": account.created_at.isoformat(),
            "requester_role": membership.role,
        },
        "members": [m.model_dump(mode="json") for m in members],
    }


def list_account_members(db: Session, *, account_id: UUID, user_id: UUID) -> list[MembershipOut]:
    apply_rls_context(db, user_id=user_id, account_id=account_id)
    _require_membership(db, account_id=account_id, user_id=user_id)
    stmt = (
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.account_id == account_id)
        .order_by(Membership.created_at.asc())
    )
    rows = db.execute(stmt).all()
    if not rows:
        raise NotFoundError("Conta não encontrada.")
    return [
        MembershipOut(
            id=m.id,
            account_id=m.account_id,
            user_id=m.user_id,
            role=m.role,
            status=m.status,
            created_at=m.created_at,
            user_email=u.email,
            user_full_name=u.full_name,
        )
        for m, u in rows
    ]

