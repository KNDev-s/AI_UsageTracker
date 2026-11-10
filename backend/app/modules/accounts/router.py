from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.accounts import service
from app.modules.accounts.schemas import AccountCreate, AccountOut, AccountUpdate, MembershipOut
from app.modules.auth.dependencies import CurrentAuthContext, get_current_auth, require_csrf
from app.shared.schemas import APIResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=APIResponse[list[AccountOut]])
def list_accounts(
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[list[AccountOut]]:
    accounts = service.list_user_accounts(db, user_id=auth.user.id)
    return APIResponse(data=accounts)


@router.post("", response_model=APIResponse[AccountOut], status_code=201, dependencies=[Depends(require_csrf)])
def create_account(
    payload: AccountCreate,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[AccountOut]:
    account = service.create_account(db, owner_user_id=auth.user.id, data=payload)
    return APIResponse(data=account)


@router.get("/{account_id}", response_model=APIResponse[AccountOut])
def get_account(
    account_id: UUID,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[AccountOut]:
    account = service.get_account_for_user(db, account_id=account_id, user_id=auth.user.id)
    return APIResponse(data=account)


@router.patch(
    "/{account_id}",
    response_model=APIResponse[AccountOut],
    dependencies=[Depends(require_csrf)],
)
def update_account(
    account_id: UUID,
    payload: AccountUpdate,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[AccountOut]:
    account = service.update_account(
        db, account_id=account_id, user_id=auth.user.id, data=payload
    )
    return APIResponse(data=account)


@router.delete(
    "/{account_id}",
    response_model=APIResponse[dict[str, bool]],
    dependencies=[Depends(require_csrf)],
)
def delete_account(
    account_id: UUID,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, bool]]:
    service.delete_account(db, account_id=account_id, user_id=auth.user.id)
    return APIResponse(data={"deleted": True})


@router.post(
    "/{account_id}/export",
    response_model=APIResponse[dict],
    dependencies=[Depends(require_csrf)],
)
def export_account(
    account_id: UUID,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    exported = service.export_account_data(db, account_id=account_id, user_id=auth.user.id)
    return APIResponse(data=exported)


@router.get("/{account_id}/members", response_model=APIResponse[list[MembershipOut]])
def list_members(
    account_id: UUID,
    auth: CurrentAuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> APIResponse[list[MembershipOut]]:
    members = service.list_account_members(db, account_id=account_id, user_id=auth.user.id)
    return APIResponse(data=members)
