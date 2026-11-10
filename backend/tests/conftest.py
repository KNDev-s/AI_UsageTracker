from collections.abc import Generator
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Force testing environment before importing app settings
os.environ["APP_ENV"] = "testing"
os.environ["COOKIE_SECURE"] = "false"
os.environ["AUTH_RATE_LIMIT_MAX_ATTEMPTS"] = "5"
os.environ["AUTH_RATE_LIMIT_WINDOW_SECONDS"] = "60"

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_db  # noqa: E402
from app.core.email import email_service  # noqa: E402
from app.core.security import auth_rate_limiter  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture()
def db_session_factory(tmp_path: Path):
    db_file = tmp_path / "test_phase1.db"
    test_db_url = os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{db_file.as_posix()}"

    os.environ["DATABASE_URL"] = test_db_url
    os.environ["DATABASE_MIGRATION_URL"] = test_db_url
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "migrations")
    )
    command.upgrade(alembic_cfg, "head")

    connect_args = {"check_same_thread": False} if test_db_url.startswith("sqlite") else {}
    engine = create_engine(test_db_url, connect_args=connect_args, future=True)
    TestingSessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    try:
        yield TestingSessionLocal
    finally:
        engine.dispose()
        get_settings.cache_clear()


@pytest.fixture()
def client(db_session_factory) -> Generator[TestClient, None, None]:
    email_service.clear_outbox()
    auth_rate_limiter.reset()

    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        db = db_session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    email_service.clear_outbox()
    auth_rate_limiter.reset()

