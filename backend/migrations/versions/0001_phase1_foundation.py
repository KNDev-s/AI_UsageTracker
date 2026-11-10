"""Phase 1 foundation: users, accounts, memberships, sessions, auth_tokens, audit_logs, RLS.

Revision ID: 0001_phase1_foundation
Revises:
Create Date: 2026-11-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_phase1_foundation"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("google_sub", sa.String(length=255), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("google_sub", name=op.f("uq_users_google_sub")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_accounts_owner_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
    )
    op.create_index(op.f("ix_accounts_owner_user_id"), "accounts", ["owner_user_id"])

    op.create_table(
        "memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_memberships_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_memberships_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_memberships")),
        sa.UniqueConstraint("account_id", "user_id", name="uq_memberships_account_user"),
        sa.UniqueConstraint("account_id", "id", name="uq_memberships_account_id_id"),
    )
    op.create_index(op.f("ix_memberships_account_id"), "memberships", ["account_id"])
    op.create_index(op.f("ix_memberships_user_id"), "memberships", ["user_id"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("csrf_token_hash", sa.String(length=64), nullable=False),
        sa.Column("active_account_id", sa.Uuid(), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["active_account_id"],
            ["accounts.id"],
            name=op.f("fk_sessions_active_account_id_accounts"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"])
    op.create_index(op.f("ix_sessions_token_hash"), "sessions", ["token_hash"], unique=True)

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_auth_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_auth_tokens_token_hash")),
    )
    op.create_index(op.f("ix_auth_tokens_user_id"), "auth_tokens", ["user_id"])
    op.create_index(op.f("ix_auth_tokens_token_type"), "auth_tokens", ["token_type"])
    op.create_index(op.f("ix_auth_tokens_token_hash"), "auth_tokens", ["token_hash"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_audit_logs_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(op.f("ix_audit_logs_account_id"), "audit_logs", ["account_id"])
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"])
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"])
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"])

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_tracker_app') THEN
                    GRANT SELECT, INSERT, UPDATE, DELETE
                    ON users, accounts, memberships, sessions, auth_tokens, audit_logs
                    TO ai_tracker_app;
                END IF;
            END $$;
            """
        )

        # Row-Level Security on tenant-scoped tables
        for tbl in ("accounts", "memberships", "audit_logs"):
            op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")

        # accounts policies
        op.execute(
            """
            CREATE POLICY accounts_select_policy ON accounts FOR SELECT USING (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR owner_user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
                OR id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
                OR EXISTS (
                    SELECT 1 FROM memberships m
                    WHERE m.account_id = accounts.id
                      AND m.user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
                      AND m.status = 'active'
                )
            );
            """
        )
        op.execute(
            """
            CREATE POLICY accounts_insert_policy ON accounts FOR INSERT WITH CHECK (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR owner_user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
            );
            """
        )
        op.execute(
            """
            CREATE POLICY accounts_modify_policy ON accounts FOR UPDATE USING (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
            ) WITH CHECK (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
            );
            """
        )
        op.execute(
            """
            CREATE POLICY accounts_delete_policy ON accounts FOR DELETE USING (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
            );
            """
        )

        # memberships policies
        op.execute(
            """
            CREATE POLICY memberships_select_policy ON memberships FOR SELECT USING (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
                OR account_id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
            );
            """
        )
        op.execute(
            """
            CREATE POLICY memberships_write_policy ON memberships FOR ALL USING (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR account_id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
            ) WITH CHECK (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR account_id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
            );
            """
        )

        # audit_logs policies
        op.execute(
            """
            CREATE POLICY audit_logs_select_policy ON audit_logs FOR SELECT USING (
                account_id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
                OR (
                    account_id IS NULL
                    AND user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
                )
            );
            """
        )
        op.execute(
            """
            CREATE POLICY audit_logs_insert_policy ON audit_logs FOR INSERT WITH CHECK (
                current_setting('app.rls_bypass', true) = 'auth_bootstrap'
                OR account_id = NULLIF(current_setting('app.current_account_id', true), '')::uuid
                OR (
                    account_id IS NULL
                    AND user_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
                )
            );
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for tbl in ("audit_logs", "memberships", "accounts"):
            op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")
    op.drop_table("audit_logs")
    op.drop_table("auth_tokens")
    op.drop_table("sessions")
    op.drop_table("memberships")
    op.drop_table("accounts")
    op.drop_table("users")

