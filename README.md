# AI Usage Tracker

Plataforma PWA multi-tenant (modelo BYOK — *Bring Your Own Key*) para centralizar, monitorar e analisar o consumo, custos, cotas e assinaturas de provedores de inteligência artificial.

Consulte a especificação completa em [PROJECT_SPEC.md](./PROJECT_SPEC.md) e o registro de decisões em [docs/DECISIONS.md](./docs/DECISIONS.md).

## Estrutura do monorepositório

```text
AI_UsageTracker/
├── backend/            # FastAPI + SQLAlchemy + Alembic + PostgreSQL (RLS)
├── frontend/           # React + TypeScript + Vite + Tailwind + PWA
├── postgres/           # Script de inicialização da role sem BYPASSRLS
├── docs/               # Documentos complementares e ADRs
├── docker-compose.yml  # Stack local (PostgreSQL, Mailpit, API, Frontend)
└── .env.example        # Variáveis de ambiente de referência
```

## Executando com Docker Compose (recomendado)

1. Copie `.env.example` para `.env` e ajuste as variáveis conforme necessário:
   ```bash
   cp .env.example .env
   ```
2. Suba todos os serviços:
   ```bash
   docker compose up --build
   ```
3. Acessos locais:
   - Frontend (PWA): `http://localhost:5173`
   - Backend API: `http://localhost:8000` (`/api/docs` em desenvolvimento)
   - Mailpit (captura de e-mails locais): `http://localhost:8025`

## Executando testes do backend localmente

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

Para executar a suíte contra uma instância real do PostgreSQL (validando também as políticas de RLS), defina `TEST_DATABASE_URL`:

```bash
TEST_DATABASE_URL="postgresql+psycopg://ai_tracker_app:ai_tracker_app_dev_password@localhost:5432/ai_usage_tracker" pytest -v
```

