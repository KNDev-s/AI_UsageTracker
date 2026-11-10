from datetime import datetime, timezone
from typing import Any
import uuid

import httpx


class GeminiUsageReporter:
    """Lightweight client helper to report Gemini API usageMetadata to AI Usage Tracker."""

    def __init__(self, *, tracker_api_url: str, ingestion_token: str, timeout: float = 5.0) -> None:
        self.ingest_url = f"{tracker_api_url.rstrip('/')}/usage/ingest"
        self.ingestion_token = ingestion_token
        self.timeout = timeout

    @staticmethod
    def extract_usage_metadata(response_obj: Any) -> dict[str, int | None]:
        """Extract usageMetadata from either a dict or a google-genai response object."""
        if isinstance(response_obj, dict):
            raw = response_obj.get("usageMetadata") or response_obj.get("usage_metadata") or {}
            return dict(raw)

        meta = getattr(response_obj, "usage_metadata", None)
        if meta is None:
            return {}

        mapping = {
            "promptTokenCount": getattr(meta, "prompt_token_count", None),
            "candidatesTokenCount": getattr(meta, "candidates_token_count", None),
            "cachedContentTokenCount": getattr(meta, "cached_content_token_count", None),
            "thoughtsTokenCount": getattr(meta, "thoughts_token_count", None),
            "toolUsePromptTokenCount": getattr(meta, "tool_use_prompt_token_count", None),
            "totalTokenCount": getattr(meta, "total_token_count", None),
        }
        return {k: v for k, v in mapping.items() if v is not None}

    def report(
        self,
        *,
        model: str,
        response_obj: Any,
        idempotency_key: str | None = None,
        occurred_at: datetime | None = None,
        source: str = "gemini_sdk",
    ) -> httpx.Response:
        usage_metadata = self.extract_usage_metadata(response_obj)
        payload = {
            "model": model,
            "usage_metadata": usage_metadata,
            "request_count": 1,
            "occurred_at": (occurred_at or datetime.now(timezone.utc)).isoformat(),
            "idempotency_key": idempotency_key or str(uuid.uuid4()),
            "source": source,
        }
        with httpx.Client(timeout=self.timeout) as client:
            return client.post(
                self.ingest_url,
                headers={"Authorization": f"Bearer {self.ingestion_token}"},
                json=payload,
            )

