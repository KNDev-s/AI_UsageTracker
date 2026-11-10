from datetime import datetime
import httpx

from app.adapters.base import (
    BaseProvider,
    CapabilityUnavailable,
    NormalizedUsageData,
    ProviderModelInfo,
    ValidationResult,
)
from app.adapters.gemini.normalizer import normalize_gemini_model_id

GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProviderAdapter(BaseProvider):
    slug = "gemini"

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=15.0, transport=self._transport)

    async def validate_credentials(self, credential_value: str) -> ValidationResult:
        if not credential_value or len(credential_value.strip()) < 10:
            return ValidationResult(
                valid=False,
                error_code="invalid_format",
                error_message="Formato de chave Gemini API inválido.",
                retryable=False,
            )

        try:
            async with self._build_client() as client:
                response = await client.get(
                    GEMINI_MODELS_URL,
                    headers={"x-goog-api-key": credential_value.strip()},
                    params={"pageSize": 100},
                )
        except httpx.TimeoutException:
            return ValidationResult(
                valid=False,
                error_code="provider_timeout",
                error_message="Tempo limite excedido ao validar chave na Google Gemini API.",
                retryable=True,
            )
        except httpx.RequestError:
            return ValidationResult(
                valid=False,
                error_code="network_error",
                error_message="Falha de rede ao consultar a Google Gemini API.",
                retryable=True,
            )

        if response.status_code == 200:
            payload = response.json()
            models: list[ProviderModelInfo] = []
            for raw in payload.get("models", []):
                ext_id = normalize_gemini_model_id(raw.get("name"))
                if not ext_id:
                    continue
                display_name = raw.get("displayName") or ext_id
                models.append(ProviderModelInfo(external_id=ext_id, display_name=display_name))
            return ValidationResult(valid=True, models=models)

        if response.status_code in (400, 401, 403):
            return ValidationResult(
                valid=False,
                error_code="invalid_credentials",
                error_message="Credencial Gemini API inválida ou sem permissão.",
                retryable=False,
            )

        if response.status_code == 429:
            retry_after_raw = response.headers.get("Retry-After")
            retry_after = int(retry_after_raw) if retry_after_raw and retry_after_raw.isdigit() else 60
            return ValidationResult(
                valid=False,
                error_code="rate_limited",
                error_message="Limite de requisições atingido na Gemini API.",
                retryable=True,
                retry_after_seconds=retry_after,
            )

        return ValidationResult(
            valid=False,
            error_code=f"provider_http_{response.status_code}",
            error_message=f"Gemini API retornou status inesperado ({response.status_code}).",
            retryable=response.status_code >= 500,
        )

    async def get_models(self, credential_value: str) -> list[ProviderModelInfo]:
        res = await self.validate_credentials(credential_value)
        return res.models if res.valid else []

    async def collect_usage(
        self, credential_value: str, start_date: datetime, end_date: datetime
    ) -> list[NormalizedUsageData] | CapabilityUnavailable:
        return CapabilityUnavailable(
            capability="historical_usage_pull",
            reason=(
                "A Google Gemini API não expõe histórico retroativo via API Key; "
                "use o endpoint POST /api/v1/usage/ingest ou o helper GeminiUsageReporter."
            ),
        )

    async def collect_quotas(
        self, credential_value: str
    ) -> list[dict] | CapabilityUnavailable:
        return CapabilityUnavailable(
            capability="quotas_pull",
            reason="Cotas detalhadas da Gemini API não são disponibilizadas por API Key padrão.",
        )

