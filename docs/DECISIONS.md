# Registro de Decisões Arquiteturais (ADR) — AI Usage Tracker

## ADR-001: Refinamentos na especificação v1.1 antes da Fase 1
- **Data:** 2026-11-10
- **Contexto:** Revisão técnica de `PROJECT_SPEC.md` v1.0 identificou lacunas operacionais para a execução segura do MVP.
- **Decisão:**
  1. Formalizar `POST /api/v1/usage/ingest` e a entidade `ingestion_tokens` para suportar instrumentação push da Gemini API sem expor chaves BYOK ou sessões de usuário.
  2. Formalizar regras de RLS no PostgreSQL com `SET LOCAL app.current_account_id` / `app.current_user_id` dentro de transações explícitas e role dedicada sem `BYPASSRLS` (`ai_tracker_app`).
  3. Definir chaves únicas `(account_id, id)` para suportar chaves estrangeiras compostas multi-tenant e índice único parcial em `usage_records(integration_id, external_record_id)` para idempotência.
  4. Definir `SameSite=Lax` para cookies `HttpOnly` (compatibilidade com retorno de redirect Google OAuth e subdomínios `app.` / `api.`) + proteção CSRF por double-submit cookie / validação de `Origin`, e política `NetworkOnly` no Service Worker para `/api/*`.
  5. Adicionar Mailpit ao ambiente Docker local para viabilizar testes de verificação de e-mail (`RF005`) e recuperação de senha (`RF004`) desde a Fase 1.

## ADR-002: Driver PostgreSQL (`psycopg` v3) e SQLAlchemy síncrono/assíncrono na Fase 1
- **Data:** 2026-11-10
- **Contexto:** Compatibilidade com Python 3.15 e suporte a execução de migrações Alembic e testes de RLS.
- **Decisão:** Utilizar `psycopg[binary]` v3 com SQLAlchemy 2.0, garantindo suporte nativo a PostgreSQL 16 e portabilidade no empacotamento Docker.

## ADR-003: Fluxo controlado de bootstrap de autenticação sob PostgreSQL RLS
- **Data:** 2026-11-10
- **Contexto:** Durante cadastro (`/auth/register`), login (`/auth/login`) e callback OAuth, o usuário ainda não possui uma sessão ou contexto de conta definido, mas o sistema precisa ler/criar registros em `accounts` e `memberships` sem conceder `BYPASSRLS` à role da aplicação.
- **Decisão:** As políticas de RLS de `accounts` e `memberships` permitem acesso quando:
  - `app.current_user_id` corresponde ao `user_id` / `owner_user_id` ou existe membership ativa; ou
  - `app.rls_bypass` é definido localmente dentro da transação controlada do serviço de autenticação (`SET LOCAL app.rls_bypass = 'auth_bootstrap'`), jamais exposto a rotas de negócio comuns.

