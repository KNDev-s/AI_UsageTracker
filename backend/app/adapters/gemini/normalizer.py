from datetime import datetime, timezone
from typing import Any

from app.adapters.base import NormalizedUsageData


def normalize_gemini_model_id(raw_model: str | None) -> str | None:
    if not raw_model:
        return None
    cleaned = raw_model.strip()
    if cleaned.startswith("models/"):
        cleaned = cleaned[len("models/") :]
    return cleaned or None


def normalize_gemini_usage_metadata(
    *,
    model: str | None,
    usage_metadata: dict[str, Any] | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cached_tokens: int | None = None,
    reasoning_tokens: int | None = None,
    total_tokens: int | None = None,
    request_count: int | None = 1,
    occurred_at: datetime | None = None,
    external_record_id: str | None = None,
) -> NormalizedUsageData:
    """Normalize Gemini API usageMetadata strictly preserving NULL for missing fields.

    Never converts unknown/absent token fields into artificial zeros.
    """
    meta = usage_metadata or {}

    resolved_input = input_tokens
    if resolved_input is None and "promptTokenCount" in meta:
        prompt_cnt = meta.get("promptTokenCount")
        tool_cnt = meta.get("toolUsePromptTokenCount")
        if prompt_cnt is not None:
            resolved_input = int(prompt_cnt) + (int(tool_cnt) if tool_cnt is not None else 0)

    resolved_output = output_tokens
    if resolved_output is None and meta.get("candidatesTokenCount") is not None:
        resolved_output = int(meta["candidatesTokenCount"])

    resolved_cached = cached_tokens
    if resolved_cached is None and meta.get("cachedContentTokenCount") is not None:
        resolved_cached = int(meta["cachedContentTokenCount"])

    resolved_reasoning = reasoning_tokens
    if resolved_reasoning is None and meta.get("thoughtsTokenCount") is not None:
        resolved_reasoning = int(meta["thoughtsTokenCount"])

    resolved_total = total_tokens
    if resolved_total is None and meta.get("totalTokenCount") is not None:
        resolved_total = int(meta["totalTokenCount"])

    ts = occurred_at or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    return NormalizedUsageData(
        model_external_id=normalize_gemini_model_id(model),
        input_tokens=resolved_input,
        output_tokens=resolved_output,
        cached_tokens=resolved_cached,
        reasoning_tokens=resolved_reasoning,
        total_tokens=resolved_total,
        request_count=request_count,
        measurement_type="direct",
        occurred_at=ts,
        external_record_id=external_record_id,
    )

