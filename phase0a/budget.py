"""Phase 0A 的離線成本守門與稽核契約（ADR-007）。"""

from collections.abc import Mapping, MutableSequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


@dataclass(frozen=True)
class AiRequest:
    job_id: UUID
    request_id: UUID
    operation: str
    provider_id: str | None = None
    model_id: str | None = None
    estimated_input_tokens: int | None = None
    estimated_output_tokens: int | None = None
    estimated_cost_twd: Decimal | None = None
    synthetic_input: bool = False
    external_inference_right: bool = False
    is_retry: bool = False
    is_fallback: bool = False
    has_credit: bool = False


@dataclass(frozen=True)
class AiAuditEntry:
    job_id: UUID
    request_id: UUID
    recorded_at_utc: datetime
    policy_version: str | None
    status: str
    reason: str
    model_id: str | None
    model_approved: bool
    external_inference_right: bool
    estimated_input_tokens: int | None
    estimated_output_tokens: int | None
    estimated_cost_twd: Decimal | None


@dataclass(frozen=True)
class AiDecision:
    status: str
    mock_output: str | None
    report_status: str = "AI_DISABLED_ZERO_BUDGET"


def _section(policy: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = policy.get(key)
    return value if isinstance(value, Mapping) else {}


def _valid_amount(amount: object) -> bool:
    return isinstance(amount, Decimal) and amount.is_finite() and amount >= 0


def _safe_token_count(count: object) -> int | None:
    return count if type(count) is int and count >= 0 else None


def run_ai_preflight(
    policy: Mapping[str, object],
    request: AiRequest,
    *,
    audit: MutableSequence[AiAuditEntry],
    now: datetime,
) -> AiDecision:
    """記錄本機決策後才回傳，且只產生明確標示的合成結果。"""
    if now.utcoffset() is None:
        raise ValueError("audit time must include a timezone")
    if not isinstance(request.job_id, UUID) or not isinstance(request.request_id, UUID):
        raise ValueError("audit requires UUID job and request identifiers")

    ai = _section(policy, "r07_03")
    version = "1.0" if policy.get("version") == "1.0" else None
    zero_policy = (
        policy.get("adr") == "ADR-007"
        and version == "1.0"
        and ai.get("status") == "ACCEPTED"
        and ai.get("policy") == "ZERO_MONTHLY_BUDGET_NO_PAID_AI"
        and all(
            type(ai.get(key)) is int and ai[key] == 0
            for key in ("monthly_cap_twd", "daily_cap_twd", "per_run_cap_twd", "preapproved_spend_twd")
        )
        and all(
            ai.get(key) is False
            for key in (
                "paid_inference_enabled", "external_provider_calls_enabled",
                "provider_api_keys_approved", "billing_authorized",
            )
        )
        and ai.get("model_allowlist") == []
    )
    mock = (
        zero_policy
        and ai.get("offline_mock_inference_allowed") is True
        and request.operation == "MOCK_ONLY"
        and request.synthetic_input is True
        and request.provider_id is None
        and request.model_id is None
        and request.is_retry is False
        and request.is_fallback is False
        and request.has_credit is False
    )
    status = "MOCK_ONLY" if mock else "AI_BUDGET_PAUSED"
    reason = "SYNTHETIC_OFFLINE_FIXTURE" if mock else "EXTERNAL_AI_DISABLED"
    if not zero_policy:
        reason = "UNRECOGNIZED_PHASE0A_AI_POLICY"

    audit.append(AiAuditEntry(
        job_id=request.job_id,
        request_id=request.request_id,
        recorded_at_utc=now.astimezone(timezone.utc),
        policy_version=version,
        status=status,
        reason=reason,
        model_id="phase0a-fixture" if mock else None,
        model_approved=False,
        external_inference_right=request.external_inference_right is True,
        estimated_input_tokens=_safe_token_count(request.estimated_input_tokens),
        estimated_output_tokens=_safe_token_count(request.estimated_output_tokens),
        estimated_cost_twd=request.estimated_cost_twd if _valid_amount(request.estimated_cost_twd) else None,
    ))
    return AiDecision(status, "MOCK_ONLY: phase0a synthetic fixture" if mock else None)


class PurchaseKind(StrEnum):
    BACKUP_HARDWARE = "BACKUP_HARDWARE"
    UPS = "UPS"
    OFFSITE_SUBSCRIPTION = "OFFSITE_SUBSCRIPTION"


@dataclass(frozen=True)
class Quote:
    vendor: str
    item: str
    reference: str
    amount_twd: Decimal
    expires_on: date


@dataclass(frozen=True)
class PurchaseProposal:
    kind: PurchaseKind
    quote: Quote | None = None
    explicit_owner_approval: bool = False


@dataclass(frozen=True)
class ProcurementDecision:
    blockers: tuple[str, ...]
    status: str = "BLOCKED"


def evaluate_procurement(
    policy: Mapping[str, object], proposal: PurchaseProposal, *, as_of: date,
) -> ProcurementDecision:
    """列出採購缺項。Phase 0A 僅驗證提案，所有採購保持封鎖。"""
    infra = _section(policy, "r07_04")
    blockers = ["PHASE0A_NO_PROCUREMENT"]
    if not isinstance(proposal.kind, PurchaseKind):
        return ProcurementDecision((*blockers, "UNRECOGNIZED_PURCHASE_KIND"))

    if proposal.kind is PurchaseKind.OFFSITE_SUBSCRIPTION:
        cap = infra.get("offsite_backup_monthly_cap_twd")
        authorized = infra.get("offsite_subscription_authorized")
    else:
        cap = infra.get("new_purchase_budget_twd")
        authorized = infra.get("equipment_purchase_authorized")

    if type(cap) is not int or cap < 0:
        blockers.append("BUDGET_UNDECIDED")
    elif cap == 0:
        blockers.append("ZERO_PURCHASE_BUDGET")

    quote = proposal.quote
    if not (
        isinstance(quote, Quote)
        and all(isinstance(field, str) and field.strip() for field in (quote.vendor, quote.item, quote.reference))
        and _valid_amount(quote.amount_twd)
        and type(quote.expires_on) is date
        and quote.expires_on >= as_of
    ):
        blockers.append("VALID_QUOTE_REQUIRED")
    elif type(cap) is int and cap > 0 and quote.amount_twd > cap:
        blockers.append("QUOTE_EXCEEDS_CATEGORY_BUDGET")

    if proposal.explicit_owner_approval is not True:
        blockers.append("OWNER_APPROVAL_REQUIRED")
    if authorized is not True:
        blockers.append("CATEGORY_NOT_AUTHORIZED")
    return ProcurementDecision(tuple(blockers))
