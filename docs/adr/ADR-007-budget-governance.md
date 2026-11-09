# ADR-007 — Budget Governance, Procurement and Resilience Spending

**Project:** AI Market Intelligence Platform (AI-MIDEP)  
**Version:** 0.1 (rolling decision record)  
**Date:** 2026-11-09  
**Status:** PARTIALLY_ACCEPTED — R07-01 accepted, R07-02/03/04 pending  
**Related:** ADR-001, ADR-002, ADR-003A, ADR-006

## 1. Confirmed Decision — R07-01 Recurring Market Data APIs

**Decision:** `APPROVAL_PER_PURCHASE` with **NO FIXED GLOBAL MONTHLY MARKET-DATA BUDGET CEILING**.

This means **no automatic buying, no implied spending authorization, and zero unapproved spending**.
For each provider/dataset/plan, explicit owner approval is necessary before payment or activating a renewal. An open-ended category budget does not permit a contract or subscription.

All monetary purchases must have:
- Provider, plan/SKU, dataset IDs, intended markets and model dependency.
- Precise fee, billing currency, VAT/sales tax, upfront and recurring amounts, payment/renewal frequency.
- Quote URL/reference, quote timestamp, expiry and dated evidence of pricing.
- Dataset license and exact rights to download, archive, backup, research/backtest, external LLM inference, local ML training and redistribution.
- Earliest and latest history, publication/vintage limitations, refresh intervals, rate limits and cancellation/refund rules.
- Documented gap relative to authorized free public data and lower-cost alternatives.
- Estimated first-month, 3-month and 12-month **total commitment / TCO** (with exchange-rate assumptions dated at estimate time).
- Named decision: `APPROVED` or `REJECTED`; approved amount, period, allowed plan and renewal mode.
- Approval evidence with immutable date and actor; no implicit approval from this ADR.

## 2. Procurement Controls

### Hard rules
- `PENDING` and `UNQUOTED` are **not** permission to purchase.
- No automatic checkout, credit card access, vendor order or subscription change by Codex/agent.
- Changes in price, tax, license, entitlement, plan, storage/AI rights or renewal period require renewed approval.
- Prefer shortest legally compliant subscription needed to verify the source; never assume a full year is mandatory.
- Approval applies only to exact SKU, dataset, use case, spending ceiling and time interval.
- Market data subscriptions, one-time licensed backfill, LLM inference, backups/UPS and power expenses tracked in separate cost centers.
- Do not add unsupported vendor price numbers; quote-required costs remain null.
- Historical data approval must satisfy ADR-006; original software/open-source license never conveys underlying market-data rights.

### Purchasing decision states
`DISCOVERY -> NEED_CONFIRMED -> RIGHTS_VERIFIED -> QUOTED -> COMPARISON_COMPLETE -> AWAITING_APPROVAL -> APPROVED/REJECTED -> PURCHASED -> ACTIVE -> RENEWAL_REVIEW -> EXPIRED/CANCELLED`.

**Important:** `APPROVED` only means decision approval. Actual payment still requires a separate explicit user-initiated action.

### Budget vs. cost monitoring
- Budget approvals are commitments/ceilings, not spent totals.
- Track `committed_twd`, `actual_billed_twd`, `estimated_accrued_twd`, `renewal_risk_twd` separately and reconcile with invoices.
- Store original currency/amount and FX assumption with timestamp; do not treat projected FX rate as a bill.
- Alerts: proposed default 50%, 80%, 100% of each approved spending ceiling; thresholds are policy proposals, not a current user-selected LLM cap.
- Auto-renewal OFF by default where vendor allows; remind for manual review prior to renewal. No background reminders scheduled by this ADR.

## 3. R07-02 Historical Backfill — PENDING

Purpose: licensed ten-year price/derivatives/institution position/corporate-action history for Taiwan MVP.

**User decision required:** one-time acquisition budget approach/cap. Alternatives:
1. No purchases before separate quote review.
2. NT$10,000 total cap, any purchase separately approved.
3. NT$30,000 total cap, any purchase separately approved.
4. No fixed total cap; each official quote approved separately.

No option is selected here. `purchase_authorized=false`, `one_time_cap_twd=null` until user confirms. Do not treat an example price from ADR-006 as a quote for complete ten-year archive.

## 4. R07-03 AI API Inference — PENDING

Separate from ChatGPT subscription and from historical data subscriptions.

Design candidate:
- Dedicated provider project/API key scoped to AI-MIDEP, usage logging, model allowlist.
- `daily_tokens_cap`, `monthly_inference_cap_twd`, `per_run_cost_cap_twd`, reserve/commit accounting, retry limits, prompt/response caching policy as permitted.
- If cap is reached: suspend **optional AI inference**, preserve ingestion/quant/backtesting and return `AI_BUDGET_PAUSED`. Never claim scheduled AI report completed when disabled.
- Provider-side spend alerts **plus** optional hard limit, with independent application-side pre-call cost estimate and conservative block. Billing enforcement may be delayed and billing conversion requires an FX estimate.

Official updated OpenAI project spend rules: https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform
No monthly ceiling or account subscription is authorized yet.

## 5. R07-04 Mac mini Backup & UPS — PENDING

Mac mini M4 32GB/1TB, 24×7 unattended from ADR-002.
- Select existing NAS / external SSD / encrypted off-device storage; account for backup capacity, retention and licensed data deletion.
- Consider USB/HID-manageable UPS that supports safe shutdown, cold-boot power recovery and connected networking gear.
- Backup/UPS purchases require explicit user price cap and approval; no hidden hardware assumptions.
- FileVault and headless VM reboot PoC is a **separate technical blocker**; a UPS does not resolve pre-boot disk unlock or Docker Desktop user-login dependency.
- At least one independent encrypted backup, restoration verification, and key management.
- Suggested accounting: `backup_capex_twd`, `ups_capex_twd`, `recurring_offsite_backup_twd`, but values TBD.

## 6. Acceptance / Procurement Audit

- FIN-01: R07-01 records **NO_FIXED_CAP + PER_PURCHASE_APPROVAL** and zero preapproved vendors.
- FIN-02: R07-02/03/04 remain `PENDING`, with NULL limits rather than invented caps.
- FIN-03: cost categories cannot borrow limits from each other.
- FIN-04: candidate purchases lacking license proof, documented need, quotation or final decision cannot be marked approved.
- FIN-05: recurring subscriptions expose next renewal date and total commitment.
- FIN-06: AI inference API fail-safe when project/app limits are reached; ongoing collector not blocked by AI-only cap.
- FIN-07: no automated checkout, no unattended orders, no API credentials in GitHub.
- FIN-08: no production readiness claim before ADR-002 FileVault/VM/restore proof.
- FIN-09: cost assumptions and FX timestamps surfaced in every price comparison.
- FIN-10: final ADR status becomes ACCEPTED only when the user confirms R07-02, R07-03 and R07-04.

## 7. Decision History

| ID | Decision | State | Date |
|---|---|---|---|
| R07-01 | Recurring market-data API: no fixed monthly cap, case-by-case quote + approval | ACCEPTED | 2026-11-09 |
| R07-02 | One-time 10-year history acquisition ceiling / process | PENDING | — |
| R07-03 | OpenAI inference monthly spending control | PENDING | — |
| R07-04 | Mac mini backup/UPS equipment and recurring backup budget | PENDING | — |

## 8. Next Action

Confirm **R07-02 one-time ten-year historical backfill budget approach**. Then confirm R07-03, then R07-04 in separate short decisions. After all are confirmed, finalize this ADR and the corresponding machine-readable spec in GitHub.
