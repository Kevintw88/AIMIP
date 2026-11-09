# ADR-007 — Budget Governance, Procurement and Resilience Spending

**Project:** AI Market Intelligence Platform (AI-MIDEP)  
**Version:** 0.3 (rolling decision record)  
**Date:** 2026-11-09  
**Status:** PARTIALLY_ACCEPTED — R07-01, R07-02 and R07-03 accepted; R07-04 pending  
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

## 3. Confirmed Decision — R07-02 Historical Backfill

**Decision:** `APPROVAL_PER_PURCHASE` with **NO FIXED TOTAL ONE-TIME HISTORICAL-DATA ACQUISITION BUDGET CEILING**.

Purpose: licensed ten-year prices, futures/options, institutional positions, corporate actions and historical revision records for the Taiwan MVP, only if necessary and legally obtainable.

**This decision is not a purchase authorization.** Every historical data order requires a separate item-specific user approval; unapproved spending remains **NT$0**.

Each proposed order must document:
- Exact dataset SKU, provider and **covered years**, required fields and instruments/signals from R04.
- Measured data gaps relative to legally usable official/free data and lower-cost alternatives.
- Verified permitted storage, retention, backups, local research/backtests, external AI inference, model training and redistribution, separately.
- Corporate-action history and whether point-in-time vintages/actual historical publication timestamps are included.
- Full supplier quote including taxes, currency, expiry, repeat purchases, update/renewal obligations, and any additional historical delivery charges.
- Cost-benefit review: which specified backtest/evaluation becomes possible, the sample period gained, and whether an alternative shorter-history model is sufficient.
- Explicit user-approved spend amount **for that exact order**, license and purpose; reroute to approval if data scope, price or usage rights change.

Default `purchase_authorized=false`, `one_time_cap_twd=null` (no category-wide cap), `preapproved_spend_twd=0`, `approved_data_orders=[]`.

A no-fixed-cap decision does **not** waive quotes, license validation, the data acquisition gates in ADR-006, or explicit payment approval. No automatic spending or purchase API is authorized.

## 4. Confirmed Decision — R07-03 OpenAI API Inference Budget (ZERO)

**Decision (2026-11-09):** `ZERO_MONTHLY_BUDGET_NO_PAID_AI`.

- Monthly OpenAI API budget: **NT$0**. Daily budget: **NT$0**. Per-run/per-call budget: **NT$0**.
- `paid_inference_enabled=false`, `external_provider_calls_enabled=false`, `provider_api_keys_approved=false`, `billing_authorized=false`.
- No production OpenAI API project, API keys, paid model allowlist or billing setup is authorized. ChatGPT subscription and API billing are separate.
- Do not call paid embeddings, language, vision, reranking or alternative model vendors. Do not use existing paid credit or free promotional allowances as a loophole: any external AI use requires a separate explicit later decision.
- Only clearly labeled offline `MOCK_ONLY` tests and deterministic non-AI reports are permitted. Never imply a mocked output is actual AI inference.
- Cost control is **application-side fail-closed**; do not rely on vendor-side warnings alone.

### Call authorization / zero-budget preflight
1. Before queueing or sending any potentially billable AI API request, inspect approved model list, data's external inference rights, budget policy version, and remaining monthly/daily/per-run allowance.
2. Under R07-03, **DENY every chargeable request even if estimated tokens/cost are zero or unknown**, record local `AI_BUDGET_PAUSED`, and do not load provider secrets.
3. Deny all retries, alternative model/provider fallback, AI embeddings, and background AI calls.
4. Continue authorized data collection, deterministic Quant, backtests, forecasting settlement and backups unaffected.
5. AI-specific report sections use `AI_DISABLED_ZERO_BUDGET` and must not fabricate AI analyses or forecasts.
6. No API credentials or payments are activated by this documentation.

### Cost monitoring contract
- Limits: `monthly_cap_twd=0`, `daily_cap_twd=0`, `per_run_cap_twd=0`, preapproved spend 0.
- Locally log denied/mock `job_id`, model id (if applicable), estimated input/output tokens, estimated TWD fee with price/FX assumption if known, policy version, denial reason, and timestamp. No externally billed usage is implied when no request is sent.
- Only mark actual billed tokens and fees after permitted provider receipts; omit secrets, licensed raw inputs, prompts and other sensitive data from logs.
- Daily accounting: Asia/Taipei. Monthly invoice reconciliation: supplier-defined cycle; currently assume UTC for planning and verify before any future paid enablement.
- For a future explicit nonzero policy, implement atomic per-call reservations, concurrency controls, post-call reconciliation, provider project alerts and optional enforced hard limits.
- OpenAI's current project limits can issue alerts or optionally enforce hard limits; alerts do not halt traffic and enforced limits may lag. Application-side denial is mandatory even when provider spend is configured to zero.

Official reference: https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform

### R07-03 acceptance criteria (design; NOT runtime-tested)
- AI-001: zero-cost and unknown-cost estimated billable calls are denied before network transmission.
- AI-002: disabled AI does not load keys or perform paid retries/fallbacks.
- AI-003: mock-only calls and denied jobs have non-billable ledgers; actual billed usage only from receipts.
- AI-004: AI-dependent reports explicitly indicate unavailable AI, never fabricated results.
- AI-005: data/quant/backtest/settlement continue independently.
- AI-006: model/data rights still enforced independently of budget.
- AI-007: only future explicit ADR approval can enable nonzero spend and external paid inference.

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
- FIN-02: R07-02 is `ACCEPTED`, has `NO_FIXED_TOTAL_CAP` and `one_time_cap_twd=NULL`, but `purchase_authorized=false` and zero preapproved orders/spend. R07-03 is `ACCEPTED` with NT$0 monthly/daily/per-run caps, no external billable inference. Only R07-04 remains `PENDING` with NULL limits.
- FIN-03: cost categories cannot borrow limits from each other.
- FIN-04: candidate purchases lacking license proof, documented need, quotation or final decision cannot be marked approved.
- FIN-05: recurring subscriptions expose next renewal date and total commitment.
- FIN-06: AI inference API fail-safe when project/app limits are reached; ongoing collector not blocked by AI-only cap.
- FIN-07: no automated checkout, no unattended orders, no API credentials in GitHub.
- FIN-08: no production readiness claim before ADR-002 FileVault/VM/restore proof.
- FIN-09: cost assumptions and FX timestamps surfaced in every price comparison.
- FIN-10: final ADR status becomes ACCEPTED only when the user confirms R07-04. R07-01/02/03 are already confirmed.

## 7. Decision History

| ID | Decision | State | Date |
|---|---|---|---|
| R07-01 | Recurring market-data API: no fixed monthly cap, case-by-case quote + approval | ACCEPTED | 2026-11-09 |
| R07-02 | One-time ten-year historical data: no fixed aggregate cap, per-quote and license-based individual approval, zero preapproved spend | ACCEPTED | 2026-11-09 |
| R07-03 | OpenAI API NT$0 per month/day/run; external billable inference disabled, mock-only testing | ACCEPTED | 2026-11-09 |
| R07-04 | Mac mini backup/UPS equipment and recurring backup budget | PENDING | — |

## 8. Next Action

Confirm **R07-04 Mac mini backup media and UPS procurement/budget**. No backup hardware spending policy has yet been selected; finalize ADR-007 only after user confirmation.
