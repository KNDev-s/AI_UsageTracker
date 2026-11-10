from collections.abc import Generator
from uuid import UUID

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


_settings = get_settings()
engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def apply_rls_context(
    db: Session,
    *,
    user_id: UUID | None = None,
    account_id: UUID | None = None,
    bypass: str | None = None,
) -> None:
    """Apply transaction-local PostgreSQL RLS variables via set_config(..., is_local=true).

    Never uses session-level SET so pooled connections never leak tenant context.
    """
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return

    db.execute(
        text(
            "SELECT "
            "set_config('app.current_user_id', :uid, true), "
            "set_config('app.current_account_id', :aid, true), "
            "set_config('app.rls_bypass', :bypass, true)"
        ),
        {
            "uid": str(user_id) if user_id else "",
            "aid": str(account_id) if account_id else "",
            "bypass": bypass or "",
        },
    )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

