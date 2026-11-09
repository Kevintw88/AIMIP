"""PH0-S06 與 PH0-S08，僅使用合成請求、報價與採購提案。"""

import json
import unittest
from contextlib import ExitStack
from dataclasses import asdict, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from phase0a.budget import (
    AiRequest,
    PurchaseKind,
    PurchaseProposal,
    Quote,
    evaluate_procurement,
    run_ai_preflight,
)
from phase0a.data import (
    DatasetKey,
    LicenseDecision,
    LicenseRegistry,
    LicenseStatus,
    MockConnector,
    Observation,
    ObservationStore,
    Operation,
)


POLICY_PATH = Path(__file__).resolve().parents[1] / "specs" / "budget_policy.json"
NOW = datetime(2026, 11, 9, 9, 0, tzinfo=timezone(timedelta(hours=8)))
AS_OF = NOW.date()
REQUEST = AiRequest(UUID(int=1), UUID(int=2), "TEXT")
QUOTE = Quote("synthetic-vendor", "synthetic-item", "synthetic-quote", Decimal(10), date(2026, 11, 10))


class OfflineBudgetTest(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.audit = []
        stack = self.enterContext(ExitStack())
        for target in ("socket.socket", "socket.create_connection", "socket.getaddrinfo", "subprocess.Popen", "os.getenv"):
            guard = stack.enter_context(patch(target, side_effect=AssertionError(f"unexpected call: {target}")))
            self.addCleanup(guard.assert_not_called)

    def preflight(self, request):
        return run_ai_preflight(self.policy, request, audit=self.audit, now=NOW)


class ZeroPaidAiTests(OfflineBudgetTest):
    def test_external_ai_stops_before_dispatch_for_every_cost_or_variant(self):
        variants = {
            "unknown estimate": REQUEST,
            "zero estimate": replace(REQUEST, estimated_cost_twd=Decimal(0)),
            "positive estimate": replace(REQUEST, estimated_cost_twd=Decimal("0.10")),
            "retry": replace(REQUEST, is_retry=True),
            "alternate provider": replace(REQUEST, provider_id="synthetic-alt", is_fallback=True),
            "credit": replace(REQUEST, has_credit=True),
            "embeddings": replace(REQUEST, operation="EMBEDDING"),
            "vision": replace(REQUEST, operation="VISION"),
            "reranking": replace(REQUEST, operation="RERANK"),
            "unknown operation": replace(REQUEST, operation="UNKNOWN"),
            "explicit data permission": replace(REQUEST, external_inference_right=True),
        }
        for name, request in variants.items():
            with self.subTest(name=name):
                prior_audit_count = len(self.audit)
                result = self.preflight(request)
                self.assertEqual(result.status, "AI_BUDGET_PAUSED")
                self.assertEqual(result.report_status, "AI_DISABLED_ZERO_BUDGET")
                self.assertIsNone(result.mock_output)
                self.assertEqual(len(self.audit), prior_audit_count + 1)
                self.assertEqual(self.audit[-1].status, "AI_BUDGET_PAUSED")
                self.assertEqual(self.audit[-1].estimated_cost_twd, request.estimated_cost_twd)

    def test_audit_records_only_sanitized_metadata_and_estimates(self):
        request = replace(
            REQUEST,
            provider_id="synthetic-secret-provider",
            model_id="synthetic-secret-model",
            estimated_input_tokens=42,
            estimated_output_tokens=0,
            estimated_cost_twd=Decimal("0.25"),
        )
        self.preflight(request)
        entry = self.audit[-1]
        self.assertEqual(entry.job_id, request.job_id)
        self.assertEqual(entry.request_id, request.request_id)
        self.assertEqual(entry.policy_version, "1.0")
        self.assertEqual(entry.recorded_at_utc, datetime(2026, 11, 9, 1, tzinfo=timezone.utc))
        self.assertEqual(entry.reason, "EXTERNAL_AI_DISABLED")
        self.assertFalse(entry.model_approved)
        self.assertFalse(entry.external_inference_right)
        self.assertEqual(entry.estimated_input_tokens, 42)
        self.assertEqual(entry.estimated_output_tokens, 0)
        self.assertEqual(entry.estimated_cost_twd, Decimal("0.25"))
        self.assertNotIn("synthetic-secret", repr(entry))
        self.assertFalse(any("actual" in key or "billed" in key for key in asdict(entry)))

        malformed = replace(
            request, estimated_input_tokens=-1, estimated_output_tokens=True,
            estimated_cost_twd=Decimal("NaN"),
        )
        self.preflight(malformed)
        entry = self.audit[-1]
        self.assertIsNone(entry.estimated_input_tokens)
        self.assertIsNone(entry.estimated_output_tokens)
        self.assertIsNone(entry.estimated_cost_twd)

    def test_mock_is_deterministic_and_cannot_route_to_external_provider(self):
        request = replace(REQUEST, operation="MOCK_ONLY", synthetic_input=True)
        first = self.preflight(request)
        second = self.preflight(request)
        self.assertEqual(first, second)
        self.assertEqual(first.status, "MOCK_ONLY")
        self.assertTrue(first.mock_output.startswith("MOCK_ONLY:"))
        self.assertEqual(first.report_status, "AI_DISABLED_ZERO_BUDGET")
        self.assertEqual([entry.status for entry in self.audit], ["MOCK_ONLY"] * 2)
        self.assertEqual(self.audit[-1].model_id, "phase0a-fixture")

        for fields in (
            {"synthetic_input": False}, {"provider_id": "synthetic-alt"},
            {"model_id": "synthetic-external"}, {"is_retry": True},
            {"is_fallback": True}, {"has_credit": True},
        ):
            with self.subTest(fields=fields):
                decision = self.preflight(replace(request, **fields))
                self.assertEqual(decision.status, "AI_BUDGET_PAUSED")
                self.assertIsNone(decision.mock_output)

    def test_missing_or_raised_budget_cannot_enable_external_inference(self):
        self.policy["r07_03"].update(
            monthly_cap_twd=100, daily_cap_twd=100, per_run_cap_twd=100,
            paid_inference_enabled=True, external_provider_calls_enabled=True,
            provider_api_keys_approved=True, billing_authorized=True,
            model_allowlist=["synthetic-model"],
        )
        request = replace(REQUEST, model_id="synthetic-model", external_inference_right=True)
        self.assertEqual(self.preflight(request).status, "AI_BUDGET_PAUSED")
        self.assertEqual(self.audit[-1].reason, "UNRECOGNIZED_PHASE0A_AI_POLICY")
        del self.policy["r07_03"]
        mock = replace(REQUEST, operation="MOCK_ONLY", synthetic_input=True)
        self.assertEqual(self.preflight(mock).status, "AI_BUDGET_PAUSED")

    def test_ai_pause_leaves_mock_ingestion_and_pit_quant_available(self):
        timestamp = NOW.astimezone(timezone.utc)
        dataset = DatasetKey("mock:phase0a-budget", "synthetic-quote")
        registry = LicenseRegistry([LicenseDecision(
            dataset, "fixture-only", LicenseStatus.APPROVED,
            frozenset({Operation.DOWNLOAD, Operation.STORAGE, Operation.RETENTION, Operation.BACKTEST}),
            timestamp, "synthetic fixture",
        )])
        row = Observation(
            dataset, "SYNTHETIC", timestamp.date(), "day", timestamp,
            timestamp, timestamp, timestamp, timestamp, "r1", 10,
        )
        connector = MockConnector(dataset, [row])
        store = ObservationStore(registry)

        decision = self.preflight(REQUEST)
        self.assertEqual(decision.status, "AI_BUDGET_PAUSED")
        with self.assertRaises(PermissionError):
            registry.require(dataset, Operation.AI_INFERENCE, now=timestamp)
        rows = connector.fetch(registry, row.trade_date, row.session_id, now=timestamp)
        store.append_many(rows, now=timestamp)
        selected = store.as_of(
            dataset, row.instrument_id, row.trade_date, row.session_id,
            cutoff=timestamp, now=timestamp,
        )
        self.assertEqual(selected, row)
        self.assertEqual(selected.value * 2, 20)


class NoProcurementTests(OfflineBudgetTest):
    def evaluate(self, kind, **fields):
        return evaluate_procurement(self.policy, PurchaseProposal(kind, **fields), as_of=AS_OF)

    def test_hardware_and_ups_cannot_use_other_budget_categories(self):
        for kind in (PurchaseKind.BACKUP_HARDWARE, PurchaseKind.UPS):
            with self.subTest(kind=kind):
                for quote in (QUOTE, replace(QUOTE, amount_twd=Decimal(0))):
                    result = self.evaluate(kind, quote=quote, explicit_owner_approval=True)
                    self.assertEqual(result.status, "BLOCKED")
                    self.assertIn("ZERO_PURCHASE_BUDGET", result.blockers)
                    self.assertIn("CATEGORY_NOT_AUTHORIZED", result.blockers)

    def test_offsite_unknown_budget_stays_undecided_even_with_quote_and_approval_claim(self):
        result = self.evaluate(PurchaseKind.OFFSITE_SUBSCRIPTION, quote=QUOTE, explicit_owner_approval=True)
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("BUDGET_UNDECIDED", result.blockers)
        self.assertIn("CATEGORY_NOT_AUTHORIZED", result.blockers)

    def test_missing_quote_and_owner_approval_are_independent_blockers(self):
        self.policy["r07_04"].update(
            new_purchase_budget_twd=100, equipment_purchase_authorized=True,
            offsite_backup_monthly_cap_twd=100, offsite_subscription_authorized=True,
        )
        for kind in PurchaseKind:
            with self.subTest(kind=kind):
                no_quote = self.evaluate(kind, explicit_owner_approval=True)
                self.assertIn("VALID_QUOTE_REQUIRED", no_quote.blockers)
                self.assertNotIn("OWNER_APPROVAL_REQUIRED", no_quote.blockers)
                no_approval = self.evaluate(kind, quote=QUOTE)
                self.assertIn("OWNER_APPROVAL_REQUIRED", no_approval.blockers)
                self.assertNotIn("VALID_QUOTE_REQUIRED", no_approval.blockers)
                complete = self.evaluate(kind, quote=QUOTE, explicit_owner_approval=True)
                self.assertEqual(complete.status, "BLOCKED")
                self.assertEqual(complete.blockers, ("PHASE0A_NO_PROCUREMENT",))

    def test_invalid_or_expired_quotes_and_truthy_strings_fail_closed(self):
        for quote in (
            replace(QUOTE, amount_twd=Decimal("NaN")),
            replace(QUOTE, amount_twd=Decimal(-1)),
            replace(QUOTE, reference=" "),
            replace(QUOTE, expires_on=date(2026, 11, 8)),
        ):
            with self.subTest(quote=quote):
                result = self.evaluate(PurchaseKind.UPS, quote=quote, explicit_owner_approval="yes")
                self.assertIn("VALID_QUOTE_REQUIRED", result.blockers)
                self.assertIn("OWNER_APPROVAL_REQUIRED", result.blockers)
        result = self.evaluate("UNKNOWN", quote=QUOTE, explicit_owner_approval=True)
        self.assertIn("UNRECOGNIZED_PURCHASE_KIND", result.blockers)

    def test_quote_must_fit_its_own_category_cap(self):
        self.policy["r07_04"].update(
            new_purchase_budget_twd=100, equipment_purchase_authorized=True,
            offsite_backup_monthly_cap_twd=5, offsite_subscription_authorized=True,
        )
        result = self.evaluate(PurchaseKind.OFFSITE_SUBSCRIPTION, quote=QUOTE, explicit_owner_approval=True)
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("QUOTE_EXCEEDS_CATEGORY_BUDGET", result.blockers)
