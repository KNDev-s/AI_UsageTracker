from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ProviderModelInfo:
    external_id: str
    display_name: str
    active: bool = True


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    models: list[ProviderModelInfo] = field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False
    retry_after_seconds: int | None = None


@dataclass(frozen=True)
class CapabilityUnavailable:
    capability: str
    reason: str


@dataclass(frozen=True)
class NormalizedUsageData:
    model_external_id: str | None
    input_tokens: int | None
    output_tokens: int | None
    cached_tokens: int | None
    reasoning_tokens: int | None
    total_tokens: int | None
    request_count: int | None
    measurement_type: str
    occurred_at: datetime
    external_record_id: str | None = None


class BaseProvider(ABC):
    slug: str

    @abstractmethod
    async def validate_credentials(self, credential_value: str) -> ValidationResult:
        """Validate provider credentials via an official supported endpoint."""

    @abstractmethod
    async def collect_usage(
        self, credential_value: str, start_date: datetime, end_date: datetime
    ) -> list[NormalizedUsageData] | CapabilityUnavailable:
        """Collect usage records when supported by an official provider API."""

    @abstractmethod
    async def collect_quotas(
        self, credential_value: str
    ) -> list[dict] | CapabilityUnavailable:
        """Collect quota snapshots when supported by an official provider API."""

    @abstractmethod
    async def get_models(self, credential_value: str) -> list[ProviderModelInfo]:
        """Discover available models for this credential."""

