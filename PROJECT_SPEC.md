# AI Usage Tracker --- Especificação Técnica do Projeto

**Versão:** 1.1\
**Data:** 10 de novembro de 2026\
**Status:** Especificação refinada e aprovada para início da Fase 1\
**Tipo:** Aplicação web progressiva (PWA), multiusuário e preparada para
SaaS\
**Modelo de integração:** BYOK (*Bring Your Own Key*)\
**Infraestrutura:** Docker + Coolify

------------------------------------------------------------------------

## 1. Visão geral

O **AI Usage Tracker** será uma plataforma para centralizar, monitorar e
analisar o consumo de diferentes provedores e ferramentas de
inteligência artificial.

Cada usuário poderá criar sua conta, conectar suas próprias ferramentas
e credenciais de IA e visualizar informações consolidadas sobre
utilização, tokens, custos, cotas, assinaturas, histórico e tendências.

O projeto começará atendendo ao uso pessoal, mas será construído desde o
início com arquitetura multi-tenant, permitindo que outras pessoas
utilizem a plataforma sem acessar os dados umas das outras. A estrutura
também deverá permitir a futura evolução para um SaaS comercial.

### 1.1 Objetivo principal

Oferecer uma visão centralizada e confiável do consumo de IA, ajudando
cada usuário a entender:

-   Quanto está utilizando de cada provedor.
-   Quantos tokens de entrada e saída está consumindo.
-   Quais modelos utiliza com maior frequência.
-   Quanto está gastando efetivamente ou por estimativa.
-   Quais cotas e limites estão disponíveis.
-   Como o consumo evolui ao longo do tempo.
-   Quais oportunidades existem para otimizar custos e utilização.

### 1.2 Princípios do produto

1.  **Multi-tenant desde o início:** os dados de cada conta devem
    permanecer isolados.
2.  **BYOK:** cada usuário conecta suas próprias chaves e contas.
3.  **Transparência dos dados:** diferenciar dados diretos, relatórios
    oficiais, snapshots, estimativas e informações manuais.
4.  **Extensibilidade:** adicionar provedores sem reconstruir o núcleo
    da aplicação.
5.  **Segurança por padrão:** credenciais protegidas e acesso validado
    no backend.
6.  **Evolução incremental:** começar com um MVP funcional e expandir
    conforme a viabilidade das integrações.

------------------------------------------------------------------------

## 2. Decisões de produto e arquitetura

  -----------------------------------------------------------------------
  Tema                                Decisão
  ----------------------------------- -----------------------------------
  Nome                                AI Usage Tracker

  Tipo                                PWA responsiva

  Público inicial                     Uso pessoal e primeiros usuários
                                      convidados

  Modelo de conta                     Conta individual com possibilidade
                                      futura de equipes

  Autenticação                        E-mail/senha e Google

  Onboarding                          Assistente inicial opcional;
                                      usuário pode pular

  Integrações                         BYOK

  Arquitetura                         Multi-tenant

  Frontend                            React + TypeScript + Vite

  Interface                           Tailwind CSS + shadcn/ui

  Gráficos                            Recharts

  Backend                             Python + FastAPI

  ORM                                 SQLAlchemy

  Migrações                           Alembic

  Banco de dados                      PostgreSQL

  Worker                              Python

  Agendamento inicial                 APScheduler

  Infraestrutura                      Docker + Coolify

  Comercialização                     Preparada estruturalmente para
                                      SaaS, sem billing no MVP
  -----------------------------------------------------------------------

### 2.1 Plataformas contempladas

  -----------------------------------------------------------------------
  Plataforma              Escopo                  Prioridade
  ----------------------- ----------------------- -----------------------
  Google Gemini API       Tokens e utilização de  Alta
                          chamadas instrumentadas 

  Google Antigravity      Cotas, limites e        Alta
                          snapshots de utilização 

  Google Gemini App       Plano, mensalidade e    Média
                          informações de limites  
                          disponíveis             

  OpenAI API              Tokens, relatórios de   Futura
                          utilização e custos     

  Anthropic Claude API    Utilização e custos     Futura
                          organizacionais, quando 
                          disponíveis             
  -----------------------------------------------------------------------

**Importante:** assinatura Google AI Pro, Gemini App, Antigravity e
Gemini API são produtos/serviços distintos. A assinatura não deve ser
interpretada automaticamente como créditos de API. A aplicação precisa
representar separadamente APIs pagas por uso e assinaturas com limites
próprios.

------------------------------------------------------------------------

## 3. Escopo funcional

### 3.1 Autenticação e usuários

  ID      Requisito                                         Prioridade
  ------- ------------------------------------------------- ------------
  RF001   Cadastro com e-mail e senha                       Alta
  RF002   Login com e-mail e senha                          Alta
  RF003   Login via Google OAuth 2.0 / OpenID Connect       Alta
  RF004   Recuperação e redefinição de senha                Alta
  RF005   Verificação de e-mail                             Alta
  RF006   Logout e gerenciamento de sessões                 Alta
  RF007   Criação automática de conta individual            Alta
  RF008   Estrutura de associação entre usuários e contas   Alta
  RF009   Convites e membros de equipe                      Futura

Cada usuário novo deverá receber uma conta individual. A modelagem
permitirá contas de equipe futuramente, mas o gerenciamento de equipes
não será necessário no MVP.

### 3.2 Onboarding

No primeiro acesso, apresentar um assistente com as etapas:

1.  Boas-vindas e explicação da plataforma.
2.  Seleção das ferramentas de IA utilizadas.
3.  Cadastro das integrações e credenciais.
4.  Teste de conexão.
5.  Primeira sincronização, quando suportada.
6.  Apresentação do dashboard.

O onboarding deve ser opcional. O usuário poderá pular etapas e utilizar
a aplicação sem conectar um provedor.

### 3.3 Gerenciamento de integrações

-   Listar provedores disponíveis.
-   Adicionar mais de uma integração do mesmo provedor.
-   Definir nome personalizado para cada integração.
-   Cadastrar credenciais.
-   Validar credenciais no backend.
-   Ativar e desativar integrações.
-   Consultar estado da conexão.
-   Consultar data da última sincronização.
-   Atualizar ou revogar credenciais.
-   Excluir integrações.
-   Consultar erros de sincronização sem expor segredos.

### 3.4 Monitoramento de utilização

-   Tokens de entrada.
-   Tokens de saída.
-   Tokens em cache, quando disponíveis.
-   Tokens de raciocínio, quando disponíveis.
-   Total de tokens.
-   Quantidade de requisições.
-   Utilização por provedor.
-   Utilização por modelo.
-   Histórico por período.
-   Cotas e limites.
-   Custos efetivos e estimados.

### 3.5 Custos e assinaturas

-   Cadastro de planos e assinaturas.
-   Registro de mensalidade e ciclo de cobrança.
-   Registro de créditos, quando disponíveis.
-   Cálculo de custos a partir de preços versionados.
-   Separação entre custos reais, estimados e mensalidades.
-   Projeção de despesas.
-   Histórico financeiro por provedor.

### 3.6 Analytics e insights

-   Comparação entre períodos.
-   Variação percentual do consumo.
-   Modelos mais utilizados.
-   Provedores com maior custo.
-   Crescimento atípico de utilização.
-   Eficiência de cache, quando mensurável.
-   Projeção de despesas.
-   Alertas de cotas e limites.
-   Relatórios exportáveis.
-   Identificação de dados incompletos.

------------------------------------------------------------------------

## 4. Requisitos não funcionais

  -----------------------------------------------------------------------
  ID                      Requisito               Critério
  ----------------------- ----------------------- -----------------------
  RNF001                  Segurança               Credenciais protegidas
                                                  e nunca expostas ao
                                                  frontend

  RNF002                  Isolamento              Dados separados por
                                                  conta

  RNF003                  Disponibilidade         Recuperação após
                                                  reinicialização de
                                                  containers

  RNF004                  Responsividade          Desktop, tablet e
                                                  celular

  RNF005                  Performance             Consultas paginadas e
                                                  agregações otimizadas

  RNF006                  Escalabilidade          Novos conectores sem
                                                  refatoração do núcleo

  RNF007                  Manutenibilidade        Código modular, tipado
                                                  e documentado

  RNF008                  Auditoria               Registro de operações
                                                  relevantes

  RNF009                  PWA                     Aplicação instalável

  RNF010                  Consistência            Sincronizações
                                                  idempotentes

  RNF011                  Observabilidade         Logs estruturados e
                                                  estados de
                                                  sincronização

  RNF012                  Privacidade             Exportação e exclusão
                                                  de dados conforme
                                                  política definida
  -----------------------------------------------------------------------

### 4.1 Regras de integridade

Todo registro de utilização deverá identificar, quando aplicável:

-   Conta proprietária.
-   Provedor.
-   Integração de origem.
-   Modelo.
-   Período ou instante de referência.
-   Data da coleta.
-   Origem da informação.
-   Tipo de medição.
-   Nível de confiabilidade.

Tipos de medição:

  Valor               Significado
  ------------------- ----------------------------------------------
  `direct`            Dado obtido diretamente da resposta ou API
  `provider_report`   Dado obtido de relatório oficial do provedor
  `snapshot`          Captura de estado em determinado instante
  `estimated`         Valor calculado por estimativa
  `manual`            Informação inserida pelo usuário

Campos desconhecidos devem ser `NULL`, nunca zero artificial. Ausência
de informação não significa consumo zero.

------------------------------------------------------------------------

## 5. Arquitetura técnica

### 5.1 Stack

  Camada        Tecnologia                 Responsabilidade
  ------------- -------------------------- -----------------------------
  Frontend      React                      Interface
  Linguagem     TypeScript                 Tipagem
  Build         Vite                       Compilação
  UI            Tailwind CSS               Estilização
  Componentes   shadcn/ui                  Componentes visuais
  Gráficos      Recharts                   Analytics
  PWA           vite-plugin-pwa            Instalação
  Backend       FastAPI                    API e regras de negócio
  Linguagem     Python                     Integrações e processamento
  ORM           SQLAlchemy                 Persistência
  Migrações     Alembic                    Versionamento do banco
  Banco         PostgreSQL                 Armazenamento
  Worker        Python                     Sincronização
  Agendamento   APScheduler inicialmente   Tarefas programadas
  Containers    Docker                     Empacotamento
  Deploy        Coolify                    Hospedagem

Redis não é obrigatório no MVP. Se o volume de tarefas crescer, avaliar
Celery ou Dramatiq com Redis.

### 5.2 Organização sugerida do backend

``` text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── encryption.py
│   │   └── database.py
│   ├── modules/
│   │   ├── auth/
│   │   ├── accounts/
│   │   ├── users/
│   │   ├── integrations/
│   │   ├── providers/
│   │   ├── usage/
│   │   ├── quotas/
│   │   ├── costs/
│   │   ├── analytics/
│   │   ├── insights/
│   │   └── subscriptions/
│   ├── adapters/
│   │   ├── base.py
│   │   ├── gemini/
│   │   ├── antigravity/
│   │   ├── openai/
│   │   └── anthropic/
│   ├── workers/
│   │   ├── scheduler.py
│   │   └── sync_worker.py
│   └── shared/
│       ├── exceptions.py
│       └── schemas.py
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

### 5.3 Organização sugerida do frontend

``` text
frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── modules/
│   │   ├── dashboard/
│   │   ├── integrations/
│   │   ├── analytics/
│   │   ├── history/
│   │   ├── insights/
│   │   └── settings/
│   ├── services/
│   ├── hooks/
│   ├── contexts/
│   └── types/
├── public/
└── package.json
```

### 5.4 Arquitetura dos conectores

Cada provedor terá um adaptador independente, implementando um contrato
comum. Exemplo conceitual:

``` python
from abc import ABC, abstractmethod

class BaseProvider(ABC):

    @abstractmethod
    async def validate_credentials(self):
        pass

    @abstractmethod
    async def collect_usage(self, start_date, end_date):
        pass

    @abstractmethod
    async def collect_quotas(self):
        pass

    @abstractmethod
    async def get_models(self):
        pass
```

Nem todo provedor implementará todos os métodos. Recursos não suportados
deverão retornar estado explícito de indisponibilidade, sem gerar dados
fictícios.

------------------------------------------------------------------------

## 6. Banco de dados

A modelagem será multi-tenant desde o início.

### 6.1 Entidades principais

#### `users` --- Usuários

  Campo               Tipo                   Descrição
  ------------------- ---------------------- ---------------------------------
  id                  UUID                   Identificador
  email               VARCHAR                E-mail único
  password_hash       VARCHAR nullable       Hash da senha, quando aplicável
  full_name           VARCHAR                Nome
  avatar_url          TEXT nullable          Foto
  email_verified_at   TIMESTAMPTZ nullable   Verificação
  created_at          TIMESTAMPTZ            Cadastro
  updated_at          TIMESTAMPTZ            Atualização

#### `accounts` --- Contas e espaços de trabalho

  Campo           Tipo          Descrição
  --------------- ------------- ------------------------
  id              UUID          Identificador
  name            VARCHAR       Nome da conta
  type            VARCHAR       `individual` ou `team`
  owner_user_id   UUID          Responsável
  timezone        VARCHAR       Fuso horário
  currency        VARCHAR       Moeda padrão
  created_at      TIMESTAMPTZ   Criação

#### `memberships` --- Participantes

  Campo        Tipo          Descrição
  ------------ ------------- ------------------------------
  id           UUID          Identificador
  account_id   UUID          Conta
  user_id      UUID          Usuário
  role         VARCHAR       `owner`, `admin` ou `member`
  status       VARCHAR       `active` ou `invited`
  created_at   TIMESTAMPTZ   Entrada

#### `providers` --- Catálogo global

  Campo      Tipo      Descrição
  ---------- --------- -----------------------------------
  id         UUID      Identificador
  slug       VARCHAR   `gemini`, `openai`, `anthropic`
  name       VARCHAR   Nome
  category   VARCHAR   `api`, `subscription` ou `hybrid`
  active     BOOLEAN   Disponibilidade

#### `integrations` --- Conexões das contas

  Campo          Tipo                   Descrição
  -------------- ---------------------- ---------------------------
  id             UUID                   Identificador
  account_id     UUID                   Conta proprietária
  provider_id    UUID                   Provedor
  name           VARCHAR                Nome personalizado
  status         VARCHAR                Estado da conexão
  last_sync_at   TIMESTAMPTZ nullable   Última coleta
  last_error     TEXT nullable          Último erro, sem segredos
  created_at     TIMESTAMPTZ            Cadastro

#### `credentials` --- Credenciais protegidas

  Campo               Tipo                   Descrição
  ------------------- ---------------------- --------------------------
  id                  UUID                   Identificador
  integration_id      UUID                   Integração
  encrypted_value     BYTEA                  Credencial criptografada
  key_version         INTEGER                Versão da chave
  credential_type     VARCHAR                API key, OAuth etc.
  last_validated_at   TIMESTAMPTZ nullable   Validação
  expires_at          TIMESTAMPTZ nullable   Expiração

#### `models` --- Modelos de IA

  Campo          Tipo      Descrição
  -------------- --------- ------------------
  id             UUID      Identificador
  provider_id    UUID      Provedor
  external_id    VARCHAR   ID externo
  display_name   VARCHAR   Nome de exibição
  active         BOOLEAN   Disponibilidade

#### `usage_records` --- Registros de utilização

  Campo                Tipo               Descrição
  -------------------- ------------------ -----------------
  id                   UUID               Identificador
  account_id           UUID               Conta
  integration_id       UUID               Integração
  model_id             UUID nullable      Modelo
  source               VARCHAR            Origem
  measurement_type     VARCHAR            Tipo de medição
  input_tokens         BIGINT nullable    Entrada
  output_tokens        BIGINT nullable    Saída
  cached_tokens        BIGINT nullable    Cache
  reasoning_tokens     BIGINT nullable    Raciocínio
  total_tokens         BIGINT nullable    Total
  request_count        INTEGER nullable   Requisições
  cost_amount          NUMERIC nullable   Custo
  currency             VARCHAR nullable   Moeda
  occurred_at          TIMESTAMPTZ        Data do consumo
  collected_at         TIMESTAMPTZ        Data da coleta
  external_record_id   VARCHAR nullable   ID externo

#### `quota_snapshots` --- Histórico de cotas

Campos: `id`, `account_id`, `integration_id`, `model_id`, `quota_limit`,
`quota_used`, `quota_remaining`, `quota_unit`, `reset_at`,
`captured_at`, `measurement_type`.

#### `subscriptions` --- Assinaturas

Campos: `id`, `account_id`, `provider_id`, `integration_id` (nullable),
`plan_name`, `billing_amount`, `billing_currency`, `billing_cycle`,
`renewal_date`, `status`.

#### `pricing_versions` --- Versões de preços por modelo

Campos: `id`, `provider_id`, `model_id`, `version_tag`, `currency`,
`input_price_per_1m`, `output_price_per_1m`, `cached_price_per_1m`
(nullable), `reasoning_price_per_1m` (nullable), `effective_from`,
`effective_to` (nullable), `created_at`.

#### `cost_records` --- Custos

Campos: `id`, `account_id`, `integration_id`, `model_id`,
`usage_record_id` (nullable), `pricing_version_id` (nullable),
`amount`, `currency`, `cost_type`, `period_start`, `period_end`.

Valores de `cost_type`: `actual`, `estimated` e `subscription`.

### 6.2 Entidades complementares

  Tabela                    Finalidade
  ------------------------- -------------------------------------------
  `ingestion_tokens`        Tokens revogáveis para ingestão push/SDK
  `sync_jobs`               Controle e trava das sincronizações
  `insights`                Insights calculados
  `audit_logs`              Auditoria
  `invitations`             Convites para equipes
  `sessions`                Sessões e dispositivos
  `notification_settings`   Preferências de alertas

Campos principais de `ingestion_tokens`: `id`, `account_id`,
`integration_id`, `name`, `token_prefix`, `token_hash`, `last_used_at`,
`revoked_at`, `created_at`.

### 6.3 Relacionamentos

``` mermaid
erDiagram
    USERS ||--o{ MEMBERSHIPS : participates
    ACCOUNTS ||--o{ MEMBERSHIPS : contains
    ACCOUNTS ||--o{ INTEGRATIONS : owns
    PROVIDERS ||--o{ INTEGRATIONS : identifies
    INTEGRATIONS ||--o{ CREDENTIALS : stores
    INTEGRATIONS ||--o{ INGESTION_TOKENS : authorizes
    INTEGRATIONS ||--o{ USAGE_RECORDS : generates
    INTEGRATIONS ||--o{ QUOTA_SNAPSHOTS : tracks
    MODELS ||--o{ USAGE_RECORDS : identifies
    MODELS ||--o{ PRICING_VERSIONS : prices
    PRICING_VERSIONS ||--o{ COST_RECORDS : calculates
    ACCOUNTS ||--o{ SUBSCRIPTIONS : owns
    ACCOUNTS ||--o{ COST_RECORDS : owns
    ACCOUNTS ||--o{ INSIGHTS : receives
    ACCOUNTS ||--o{ SYNC_JOBS : schedules
    ACCOUNTS ||--o{ AUDIT_LOGS : records
```

### 6.4 Regras de modelagem e integridade

-   Todas as tabelas pertencentes a uma conta devem possuir
    `account_id`.
-   Utilizar chaves estrangeiras compostas para impedir relacionamentos
    entre contas diferentes (ex.: `UNIQUE (account_id, id)` nas tabelas
    pai como `integrations` e `usage_records`, referenciadas por
    `(account_id, integration_id)` nas tabelas filhas).
-   Utilizar identificadores de idempotência para evitar registros
    duplicados (ex.: `external_record_id` por integração em coletas e
    ingestão).
-   Armazenar datas em UTC e aplicar o fuso horário na apresentação.
-   Utilizar `NUMERIC` para valores monetários.
-   Utilizar `NULL` para campos desconhecidos.
-   Versionar preços para preservar cálculos históricos.
-   Definir políticas de retenção para dados e logs.

### 6.5 Índices recomendados

-   `users(email)` --- único.
-   `memberships(account_id, user_id)` --- único.
-   `integrations(account_id, id)` --- único (suporte a FKs compostas).
-   `integrations(account_id, provider_id)`.
-   `ingestion_tokens(token_hash)` --- único.
-   `usage_records(account_id, id)` --- único (suporte a FKs compostas).
-   `usage_records(integration_id, external_record_id) WHERE external_record_id IS NOT NULL`
    --- único parcial (idempotência).
-   `usage_records(account_id, occurred_at)`.
-   `usage_records(account_id, integration_id, occurred_at)`.
-   `quota_snapshots(account_id, integration_id, captured_at)`.
-   `cost_records(account_id, period_start)`.
-   `sync_jobs(status, scheduled_at)`.

------------------------------------------------------------------------

## 7. Estratégia de integração por provedor

### 7.1 Google Gemini API

**Estratégia principal:** instrumentação das chamadas à API e captura
dos metadados de utilização retornados.

Campos que podem aparecer em `usageMetadata`:

-   `promptTokenCount`
-   `candidatesTokenCount`
-   `cachedContentTokenCount`
-   `thoughtsTokenCount`
-   `toolUsePromptTokenCount`
-   `totalTokenCount`

A captura será feita nas aplicações instrumentadas via endpoint de
ingestão (`POST /api/v1/usage/ingest`, autenticado por `ingestion_token`
revogável da integração e `idempotency_key`) ou por meio de um
gateway/SDK opcional, sem armazenar conteúdo de prompts. Uma chave de
API não deve ser tratada como garantia de acesso a todo o histórico de
chamadas realizadas em outros aplicativos.

Documentação: https://ai.google.dev/gemini-api/docs

### 7.2 Google Antigravity

Estratégia inicial:

1.  Registrar cotas por modelo quando disponíveis.
2.  Capturar snapshots em intervalos configurados.
3.  Comparar snapshots para estimar alterações de utilização.
4.  Identificar janelas de renovação quando a fonte informar.
5.  Permitir registro manual de informações não acessíveis
    automaticamente.

Não depender de endpoints internos não documentados ou scraping de
interfaces privadas como base de produção. A disponibilidade de uma API
pública e suportada deve ser verificada antes de implementar coleta
automática.

### 7.3 Google Gemini App

Tratar como fonte de informações de plano e limites, não como API de
tokens.

Funcionalidades:

-   Cadastro do plano.
-   Registro da mensalidade.
-   Data de renovação.
-   Registro manual de limites apresentados.
-   Histórico das informações disponíveis.

Não prometer contabilização exata de tokens do Gemini App quando o
provedor não disponibilizar essa métrica.

### 7.4 OpenAI API

Possíveis caminhos:

1.  Instrumentação das chamadas realizadas por aplicações controladas
    pelo usuário.
2.  Relatórios administrativos de utilização e custos, quando a conta e
    as permissões permitirem.

Endpoints organizacionais podem exigir credenciais e permissões
administrativas específicas. Uma API key convencional de projeto não
equivale a uma Admin API Key.

Documentação: https://developers.openai.com/api/docs/

### 7.5 Anthropic Claude

Avaliar os endpoints organizacionais de análise de utilização e custos,
que exigem credenciais e permissões adequadas. Para chamadas
individuais, também será possível capturar metadados de utilização por
instrumentação.

Documentação:
https://platform.claude.com/docs/en/manage-claude/usage-cost-analytics-api

### 7.6 Matriz de cobertura inicial

  ---------------------------------------------------------------------------------------
  Plataforma     Tokens                 Custos         Cotas          Histórico
  -------------- ---------------------- -------------- -------------- -------------------
  Gemini API     Direto, em chamadas    Calculado ou   Conforme fonte Instrumentado
                 instrumentadas         relatório                     
                                        disponível                    

  Antigravity    Parcial/indisponível   Conforme fonte Snapshots      Snapshots
                 em geral                                             

  Gemini App     Não disponível de      Mensalidade    Limites        Manual/disponível
                 forma geral                           informados     

  OpenAI API     Direto/relatório       Relatório ou   Conforme fonte Relatório/API
                                        cálculo                       

  Claude API     Direto/relatório       Relatório ou   Conforme fonte Relatório/API
                                        cálculo                       
  ---------------------------------------------------------------------------------------

A interface deverá mostrar a origem e a confiabilidade dos dados. Não
apresentar métricas como disponíveis sem fonte verificável.

------------------------------------------------------------------------

## 8. API interna

Prefixo geral: `/api/v1`.

Todas as rotas privadas deverão exigir autenticação e contexto de conta
validado no backend (enviado via header `X-Account-ID` ou conta padrão
do usuário, sempre verificado contra `memberships` ativas antes de
estabelecer o contexto da transação).

### 8.1 Autenticação

  Método   Endpoint                      Função
  -------- ----------------------------- -----------------------------
  POST     `/auth/register`              Criar usuário
  POST     `/auth/login`                 Autenticar
  POST     `/auth/logout`                Encerrar sessão
  POST     `/auth/refresh`               Renovar sessão
  GET      `/auth/me`                    Consultar usuário
  POST     `/auth/verify-email`          Confirmar verificação de e-mail
  POST     `/auth/resend-verification`   Reenviar verificação
  POST     `/auth/forgot-password`       Solicitar recuperação
  POST     `/auth/reset-password`        Redefinir senha
  GET      `/auth/google`                Iniciar autenticação Google
  GET      `/auth/google/callback`       Processar retorno OAuth

### 8.2 Contas

  Método   Endpoint                           Função
  -------- ---------------------------------- --------------------------
  GET      `/accounts`                        Listar contas do usuário
  POST     `/accounts`                        Criar conta
  GET      `/accounts/{account_id}`           Consultar conta
  PATCH    `/accounts/{account_id}`           Atualizar conta
  DELETE   `/accounts/{account_id}`           Excluir conta (LGPD)
  POST     `/accounts/{account_id}/export`    Exportar dados (LGPD)
  GET      `/accounts/{account_id}/members`   Consultar participantes

### 8.3 Integrações

  Método   Endpoint                                        Função
  -------- ----------------------------------------------- -------------------------------
  GET      `/integrations/providers`                       Listar provedores
  GET      `/integrations`                                 Listar integrações da conta
  POST     `/integrations`                                 Criar integração
  POST     `/integrations/{id}/validate`                   Validar credencial
  POST     `/integrations/{id}/sync`                       Solicitar sincronização
  GET      `/integrations/{id}/status`                     Consultar estado
  PATCH    `/integrations/{id}`                            Atualizar integração
  DELETE   `/integrations/{id}`                            Remover integração
  GET      `/integrations/{id}/ingestion-tokens`           Listar tokens de ingestão
  POST     `/integrations/{id}/ingestion-tokens`           Gerar token de ingestão
  DELETE   `/integrations/{id}/ingestion-tokens/{tok_id}`  Revogar token de ingestão

### 8.4 Utilização, cotas, custos e analytics

  Método   Endpoint                Função
  -------- ----------------------- ---------------------------------
  POST     `/usage/ingest`         Ingestão push de apps instrumentados
  POST     `/usage/records`        Lançamento manual de utilização
  GET      `/usage/summary`        Resumo de consumo
  GET      `/usage/timeseries`     Série histórica
  GET      `/usage/by-provider`    Consumo por provedor
  GET      `/usage/by-model`       Consumo por modelo
  GET      `/usage/records`        Registros individuais
  GET      `/quotas`               Cotas atuais
  POST     `/quotas`               Registro manual de cotas/limites
  GET      `/quotas/history`       Histórico de cotas
  GET      `/costs/summary`        Resumo financeiro
  GET      `/costs/timeseries`     Evolução de custos
  GET      `/analytics/export`     Exportação CSV/JSON
  GET      `/insights`             Insights
  GET      `/subscriptions`        Listar assinaturas
  POST     `/subscriptions`        Cadastrar assinatura
  PATCH    `/subscriptions/{id}`   Atualizar assinatura
  DELETE   `/subscriptions/{id}`   Remover assinatura

### 8.5 Padronização das respostas

Exemplo:

``` json
{
  "success": true,
  "data": {
    "total_tokens": 15500,
    "input_tokens": 12000,
    "output_tokens": 3500,
    "provider": "gemini"
  },
  "meta": {
    "measurement_type": "direct",
    "currency": "BRL",
    "timezone": "America/Sao_Paulo"
  }
}
```

Padronizar paginação, filtros por período, ordenação, erros e
validações.

------------------------------------------------------------------------

## 9. Segurança e privacidade

Segurança é requisito estrutural e deve ser implementada desde a
primeira versão.

### 9.1 Autenticação

-   Hash de senhas com Argon2id.
-   Google OAuth utilizando OpenID Connect.
-   Sessões com cookies `HttpOnly`, `Secure` (em HTTPS) e `SameSite=Lax`
    (necessário para o redirect de retorno do OAuth e compatível com
    subdomínios `app.` / `api.` sob o mesmo domínio-base).
-   Renovação e expiração controladas.
-   Proteção contra CSRF explícita em rotas mutáveis (ex.: double-submit
    cookie ou validação estrita de `Origin`/header customizado).
-   Rate limiting em autenticação.
-   Verificação de e-mail.
-   Recuperação segura de senha.
-   Não armazenar tokens de sessão em `localStorage`.
-   Service Worker da PWA configurado com estratégia `NetworkOnly` para
    rotas `/api/*` (nunca cachear dados privados ou financeiros offline).

### 9.2 Proteção das credenciais

As chaves de API deverão ser criptografadas antes de serem persistidas.

Fluxo:

1.  Usuário informa a chave.
2.  Backend recebe a credencial por HTTPS.
3.  Backend valida formato e, quando solicitado, testa a conexão.
4.  Credencial é criptografada com criptografia autenticada.
5.  Banco armazena somente o conteúdo criptografado.
6.  Backend descriptografa apenas quando necessário para executar uma
    integração.

Diretrizes:

-   Utilizar AES-256-GCM ou envelope encryption.
-   Manter a chave mestra fora do banco de dados.
-   Proteger a chave mestra por segredo do ambiente ou serviço de
    gerenciamento de segredos.
-   Versionar chaves para permitir rotação.
-   Nunca retornar a credencial original após o cadastro.
-   Exibir somente identificações mascaradas.
-   Nunca registrar credenciais em logs.
-   Permitir revogar e excluir credenciais.

### 9.3 Isolamento multi-tenant

Adotar três camadas:

1.  Verificar se o usuário pertence à conta via `memberships`.
2.  Aplicar filtros obrigatórios por `account_id` no backend.
3.  Utilizar PostgreSQL Row-Level Security (RLS) como proteção
    adicional.

Regras operacionais do RLS com pool de conexões:

-   Aplicar `SET LOCAL app.current_account_id = '<uuid>'` estritamente
    dentro da transação de cada requisição no backend (nunca `SET` em
    nível de sessão, evitando vazamento de contexto no pool).
-   As políticas de RLS devem operar sobre uma role de banco sem
    privilégio `BYPASSRLS` para a API; fluxos pré-autenticação (`login`,
    `register`, `OAuth`) e o `worker` (que itera integrações por conta)
    devem usar contexto explícito e escopado por transação.
-   O contexto da conta deve ser estabelecido pelo backend após validar
    a sessão e a associação do usuário. Nunca confiar exclusivamente em
    um `account_id` enviado pelo frontend.

### 9.4 Auditoria

Registrar operações relevantes:

-   Login e logout.
-   Criação e exclusão de integrações.
-   Alteração de credenciais.
-   Convites e mudanças de membros.
-   Falhas de sincronização.
-   Alterações de configurações financeiras.

Não registrar chaves, tokens de autenticação ou conteúdo de prompts.

### 9.5 LGPD

Planejar:

-   Política de privacidade.
-   Termos de uso.
-   Exportação de informações.
-   Exclusão de conta e dados.
-   Controle de consentimentos aplicáveis.
-   Retenção e descarte.
-   Procedimentos para incidentes de segurança.

------------------------------------------------------------------------

## 10. Dashboard e experiência do usuário

### 10.1 Navegação principal

1.  Dashboard.
2.  Analytics.
3.  Integrações.
4.  Modelos.
5.  Histórico de utilização.
6.  Custos e assinaturas.
7.  Insights.
8.  Configurações.

### 10.2 Indicadores principais

-   Total de tokens.
-   Tokens de entrada.
-   Tokens de saída.
-   Total de requisições.
-   Custo efetivo.
-   Custo estimado.
-   Provedores conectados.
-   Estado das cotas.
-   Última sincronização.

### 10.3 Gráficos

  Gráfico                    Objetivo
  -------------------------- -------------------------------
  Linha temporal             Evolução do consumo
  Barras                     Consumo por provedor
  Barras empilhadas          Entrada versus saída
  Distribuição               Participação por modelo
  Linha temporal             Evolução dos custos
  Comparativo                Período atual versus anterior
  Indicadores de progresso   Utilização de cotas

Filtros previstos:

-   Hoje.
-   Últimos 7 dias.
-   Últimos 30 dias.
-   Mês atual.
-   Mês anterior.
-   Período personalizado.
-   Provedor.
-   Modelo.
-   Tipo de medição.

### 10.4 Insights

No início, utilizar regras determinísticas e cálculos verificáveis.
Exemplos:

-   Aumento percentual de consumo em relação ao período anterior.
-   Concentração de utilização em determinados modelos.
-   Crescimento de custos.
-   Mudança no perfil de utilização.
-   Projeção de despesas.
-   Dados incompletos ou desatualizados.

Posteriormente, adicionar IA generativa para interpretar tendências e
produzir relatórios em linguagem natural. A IA não deve inventar dados
nem substituir os cálculos oficiais.

------------------------------------------------------------------------

## 11. Sincronização e processamento

O sistema combina dois mecanismos complementares:

-   **Ingestão passiva (push):** aplicações instrumentadas enviam
    eventos diretamente para `POST /api/v1/usage/ingest` com
    `ingestion_token` e `idempotency_key`.
-   **Coleta ativa (pull):** o worker (`ai-tracker-worker`) executa
    coletas periódicas independentes para provedores com relatórios ou
    snapshots suportados.

Para confiabilidade operacional, o APScheduler deve usar persistência em
PostgreSQL (`SQLAlchemyJobStore`) combinada com trava de linha em
`sync_jobs` (`SELECT ... FOR UPDATE SKIP LOCKED`) para evitar execuções
duplicadas após reinicializações.

### 11.1 Fluxo

``` mermaid
flowchart TD
    A[Agendador] --> B[Identificar integrações ativas]
    B --> C[Validar conta e credencial]
    C --> D[Executar adaptador do provedor]
    D --> E{Coleta concluída?}
    E -->|Sim| F[Normalizar dados]
    F --> G[Validar e deduplicar]
    G --> H[Persistir no PostgreSQL]
    H --> I[Atualizar agregações]
    I --> J[Atualizar dashboard]
    E -->|Não| K[Registrar erro]
    K --> L[Aplicar política de retry]
```

### 11.2 Frequências iniciais sugeridas

  Processo                             Frequência
  ------------------------------------ ----------------------------------------
  Sincronização de relatórios de API   15 a 60 minutos
  Coleta de cotas                      30 a 60 minutos
  Atualização de insights              Diariamente
  Atualização de preços                Diariamente ou quando houver alteração
  Verificação de integrações           Conforme agendamento

As frequências deverão respeitar limites de requisição e disponibilidade
de cada provedor. Nem toda integração permitirá coleta automática.

### 11.3 Tratamento de falhas

-   Retry com backoff exponencial.
-   Respeitar `Retry-After`.
-   Controlar paginação.
-   Identificar credenciais expiradas.
-   Bloquear temporariamente integrações com falhas repetidas.
-   Registrar a última coleta bem-sucedida.
-   Evitar duplicidade após reprocessamento.
-   Não sobrescrever dados válidos com respostas incompletas.

------------------------------------------------------------------------

## 12. Infraestrutura e implantação

### 12.1 Serviços no Coolify

  Serviço      Container               Responsabilidade
  ------------ ----------------------- ------------------
  Frontend     `ai-tracker-frontend`   PWA
  Backend      `ai-tracker-api`        API
  Worker       `ai-tracker-worker`     Sincronização
  PostgreSQL   `ai-tracker-db`         Banco

Redis poderá ser adicionado posteriormente para filas e cache, caso
necessário.

### 12.2 Ambientes

-   Desenvolvimento local.
-   Homologação.
-   Produção.

Cada ambiente deverá utilizar configurações e credenciais independentes.

### 12.3 Backups

-   Backup automático do PostgreSQL.
-   Armazenamento fora do container.
-   Testes periódicos de restauração.
-   Backups criptografados.
-   Política de retenção definida.

### 12.4 Domínios sugeridos

``` text
app.seudominio.com.br
api.seudominio.com.br
```

Frontend e API deverão operar por HTTPS.

------------------------------------------------------------------------

## 13. Testes e qualidade

  Categoria      Validação
  -------------- ------------------------------
  Unitários      Regras de negócio e cálculos
  Integração     Conectores e banco
  Autenticação   Login, sessão e recuperação
  Segurança      Isolamento entre contas
  API            Contratos e respostas
  Frontend       Componentes e navegação
  E2E            Fluxos completos

### 13.1 Cenários críticos

**Cenário 1 --- Isolamento**

-   Usuário A cria uma integração.
-   Usuário B tenta acessar a integração.
-   O sistema deve impedir o acesso.

**Cenário 2 --- Credencial inválida**

-   Usuário adiciona uma chave inválida.
-   Backend testa a conexão.
-   Integração recebe estado de erro.
-   Nenhum segredo aparece na resposta ou nos logs.

**Cenário 3 --- Sincronização duplicada**

-   Worker processa um relatório.
-   A mesma coleta é executada novamente.
-   Banco não duplica os registros.

**Cenário 4 --- Dados incompletos**

-   Provedor não disponibiliza tokens de raciocínio.
-   Campo permanece `NULL`.
-   Gráficos não interpretam ausência como zero.

**Cenário 5 --- Exclusão de conta**

-   Usuário solicita exclusão.
-   Credenciais são eliminadas ou revogadas conforme aplicável.
-   Dados pessoais são excluídos conforme política de retenção.
-   Processo fica auditável.

------------------------------------------------------------------------

## 14. Roadmap de desenvolvimento

### Fase 1 --- Fundação

-   [x] Criar repositório Git.
-   [x] Criar estrutura frontend e backend.
-   [x] Configurar Docker e ambiente local (incluindo Mailpit para testes
    de e-mail transacional).
-   [x] Configurar PostgreSQL (estrutura Compose, role `ai_tracker_app` sem
    `BYPASSRLS` e políticas RLS).
-   [x] Configurar Alembic (`0001_phase1_foundation`).
-   [x] Implementar cadastro, login, verificação de e-mail e recuperação
    de senha.
-   [x] Implementar Google OAuth.
-   [x] Criar contas individuais.
-   [x] Implementar memberships.
-   [x] Implementar isolamento multi-tenant (camada de aplicação + RLS
    com `SET LOCAL` por transação).
-   [x] Implementar testes automatizados de autenticação e isolamento.
-   [ ] Validar stack completa em Docker e configurar deploy inicial no
    Coolify.

**Entrega:** aplicação acessível, com autenticação e contas isoladas.

### Fase 2 --- Integração Gemini API

-   [ ] Criar catálogo de provedores.
-   [ ] Implementar cadastro de credenciais.
-   [ ] Implementar criptografia.
-   [ ] Implementar tokens de ingestão (`ingestion_tokens`) e endpoint
    `POST /api/v1/usage/ingest`.
-   [ ] Criar adaptador Gemini.
-   [ ] Instrumentar chamadas de API.
-   [ ] Normalizar metadados de utilização.
-   [ ] Registrar tokens e requisições com idempotência.
-   [ ] Implementar worker com persistência de agendamento.
-   [ ] Implementar histórico de sincronização.

**Entrega:** dados reais de utilização instrumentada armazenados por
conta.

### Fase 3 --- Dashboard

-   [ ] Criar indicadores gerais.
-   [ ] Criar gráficos temporais.
-   [ ] Criar histórico de utilização.
-   [ ] Implementar filtros.
-   [ ] Criar comparações entre modelos.
-   [ ] Implementar custos estimados.
-   [ ] Criar estados vazios e de erro.

**Entrega:** dashboard funcional com dados reais.

### Fase 4 --- Ecossistema Google

-   [ ] Cadastro de assinatura Gemini.
-   [ ] Monitoramento Antigravity por fontes suportadas.
-   [ ] Snapshots de cotas.
-   [ ] Registro de informações Gemini App.
-   [ ] Implementar insights iniciais.

**Entrega:** painel consolidado das ferramentas Google com limites de
cobertura documentados.

### Fase 5 --- Expansão

-   [ ] OpenAI API.
-   [ ] Anthropic Claude.
-   [ ] Alertas personalizados.
-   [ ] Relatórios.
-   [ ] Exportação CSV.
-   [ ] Insights com IA.

**Entrega:** suporte ampliado a provedores.

### Fase 6 --- Preparação comercial

-   [ ] Gestão de equipes.
-   [ ] Convites.
-   [ ] Planos e limites.
-   [ ] Painel administrativo.
-   [ ] Billing.
-   [ ] Termos e políticas comerciais.

**Entrega:** estrutura comercial preparada para SaaS.

------------------------------------------------------------------------

## 15. Critérios de conclusão do MVP

O MVP será considerado funcional quando um usuário conseguir:

1.  Criar uma conta.
2.  Entrar com e-mail/senha ou Google.
3.  Criar seu espaço individual.
4.  Pular o onboarding se desejar.
5.  Conectar uma Gemini API.
6.  Registrar automaticamente a utilização das aplicações
    instrumentadas.
7.  Consultar histórico e gráficos.
8.  Visualizar custos estimados.
9.  Manter seus dados isolados dos demais usuários.
10. Acessar a aplicação hospedada no Coolify.

Antigravity e Gemini App terão suas limitações explicitadas e poderão
ser adicionados progressivamente sem bloquear o primeiro MVP.

------------------------------------------------------------------------

## 16. Fora do escopo do MVP

-   Cobrança de usuários.
-   Assinaturas comerciais.
-   Marketplace de integrações.
-   Gestão completa de organizações.
-   Compartilhamento de dashboards.
-   Aplicativos nativos Android e iOS.
-   IA generativa para todos os relatórios.
-   Monitoramento de ferramentas sem interfaces oficiais ou
    instrumentação autorizada.

------------------------------------------------------------------------

## 17. Fontes técnicas oficiais

Consultar estas referências durante a implementação e revisar
periodicamente alterações de APIs:

-   Google Gemini API: https://ai.google.dev/gemini-api/docs
-   Google Gemini API --- Generate Content:
    https://ai.google.dev/api/generate-content
-   Google Antigravity: https://antigravity.google/docs/
-   OpenAI API: https://developers.openai.com/api/docs/
-   OpenAI Usage API:
    https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/usage
-   Anthropic Usage and Cost Analytics:
    https://platform.claude.com/docs/en/manage-claude/usage-cost-analytics-api
-   FastAPI: https://fastapi.tiangolo.com/
-   PostgreSQL Row Security:
    https://www.postgresql.org/docs/current/ddl-rowsecurity.html
-   Coolify: https://coolify.io/docs
-   PWA Plugin for Vite: https://vite-pwa-org.netlify.app/
-   SQLAlchemy: https://docs.sqlalchemy.org/
-   Alembic: https://alembic.sqlalchemy.org/

------------------------------------------------------------------------

## 18. Orientações para iniciar o desenvolvimento com Antigravity

O desenvolvimento deverá ser incremental e orientado pela documentação.

### Regras de execução

1.  Ler esta especificação antes de implementar.
2.  Não tentar construir o projeto inteiro em um único passo.
3.  Trabalhar por fases e entregas pequenas.
4.  Antes de alterar a arquitetura, explicar a necessidade e registrar a
    decisão.
5.  Criar testes para funcionalidades críticas.
6.  Validar isolamento entre contas desde a primeira implementação.
7.  Não utilizar dados fictícios como se fossem dados reais.
8.  Não implementar scraping ou endpoints privados não documentados como
    dependência de produção.
9.  Manter documentação atualizada.
10. Executar testes e validações antes de considerar uma tarefa
    concluída.

### Documentos complementares recomendados

Manter no repositório:

``` text
docs/
├── PROJECT.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
├── DATABASE.md
├── INTEGRATIONS.md
├── SECURITY.md
├── API.md
├── ROADMAP.md
└── DECISIONS.md
```

Este arquivo deverá ser a especificação central. Os documentos
complementares poderão detalhar cada área conforme a implementação
avançar.

### Primeira tarefa recomendada

Iniciar pela **Fase 1 --- Fundação**, implementando:

1.  Estrutura do monorepositório.
2.  Docker Compose para desenvolvimento local.
3.  PostgreSQL e migrações.
4.  Modelo de usuários, contas e memberships.
5.  Cadastro e login.
6.  Google OAuth.
7.  Isolamento de dados por conta.
8.  Testes automatizados dos fluxos de autenticação e isolamento.

Não iniciar as integrações de IA nem o dashboard antes de validar a
fundação.

------------------------------------------------------------------------

## 19. Decisões que exigem validação durante a implementação

Alguns detalhes ainda deverão ser definidos com base nos requisitos
reais de execução:

-   Provedor de e-mail transacional para verificação e recuperação de
    senha.
-   Biblioteca ou serviço de autenticação.
-   Estratégia definitiva de gerenciamento e rotação de chaves de
    criptografia.
-   Disponibilidade de fontes oficiais para coleta do Antigravity e
    Gemini App.
-   Estratégia de instrumentação das chamadas Gemini em aplicações
    externas.
-   Política de retenção e volume de histórico.
-   Limites de uso e planos comerciais futuros.

Essas decisões não bloqueiam o início da Fase 1.

------------------------------------------------------------------------

**Conclusão**

O AI Usage Tracker deverá nascer como uma plataforma multiusuário,
segura e extensível, utilizando o modelo BYOK. A primeira versão terá
foco em autenticação, isolamento de contas, integração com Gemini API,
coleta confiável e dashboard de utilização.

A arquitetura deverá permitir adicionar novos provedores e recursos
comerciais sem comprometer a estrutura central do sistema.

**Diretriz final:** primeiro construir uma base segura e confiável de
coleta de dados; depois transformar esses dados em visualizações,
análises e inteligência.
