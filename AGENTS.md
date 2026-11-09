# AGENTS.md — AI-MIDEP Codex Rules
## Status
This repository is in **specification freeze preparation**. Do not begin application development until the user approves *all* R07-01/02/03/04 (R07-01/02/03 approved; only R07-04 pending), data licensing, and Phase 0 initiation. R06 historical target is approved but data gaps/rights/PIT proof are NOT resolved. R05 has been accepted as a schedule and data-freshness specification, not tested production behavior.

## Scope
- Single user; Taiwan → US → Japan; Taiwan MVP 10 investment instruments + 14 market signal categories.
- Mac mini M4, 32GB RAM, 1TB SSD; host macOS, proposed headless Linux ARM64 VM, **unattended recovery unverified**.
- OpenBB V5 *conditional* adapter, not an unconditional runtime dependency.
- ADR-005: daily-bar analysis with multiple dataset-aware polls, delayed-release and corrections checks, append-only revisions, immutable forecasts. Schedule is not a publication SLA.
- ADR-006: 2016-11-09–2026-11-09 ten-year objective only; 7 listing-eligible and 3 structurally short instruments. No dataset is certified for retention, ten-year completeness, or PIT-safe historical vintages.
- ADR-007 PARTIAL: R07-01 recurring market-data APIs have NO_FIXED_MONTHLY_CAP; R07-02 one-time historical data has NO_FIXED_TOTAL_CAP. Both are *approval policies*, not spending approval. For each order, confirm the exact data gap, provider quotation, permitted license uses, coverage, price, and explicit user approval. R07-03 OpenAI API is ACCEPTED at NT$0 per month/day/call, with all external billable inference disabled; R07-04 backup/UPS remains PENDING. No new purchases, subscriptions or paid jobs are authorized.
- No live brokerage order execution, no public data redistribution.
## Hard rules
1. Unknown provider usage license = DENY. Separate permissions for download, retention, local storage, historical backtest, third-party LLM inference, ML training, redistribution, backups.
2. Do not automate TradingView MCP extraction, caching, model evaluation or data warehousing.
3. Do not assume official endpoint names, historical depth, publication SLAs, or trading symbols without fresh contract checks.
4. No invented data, prices, financial results, timestamps or API endpoints.
5. Record observation timestamp, source publication time, *first known availability* time, ingestion time and revision when supplied; unknown fields must be explicitly null, never fabricated.
6. Point-in-time safe models; preserve split/dividend handling, original vs adjusted prices, transaction costs, ETF leverage daily resetting, delistings, no look-ahead.
7. Published forecasts are immutable; calculate outcomes separately; champion upgrades require independent validation and human approval.
8. No automatic login, FileVault deactivation or storing of unlock secrets. Unattended boot + encryption conflict requires explicit approval.
9. No API key commits, .env secrets, live trading or uncontrolled external LLM forwarding.
10. Verify Linux/ARM64, dependencies, and provider rights via PoC before marking production-capable.
11. Use exchange trading calendars, distinct observation / publication / first-seen / ingestion timestamps and explicit unknowns; never infer that a poll time equals publication time.
12. Poll/retry with provider quotas, idempotent backfill, T+1/T+2/T+5/T+20 trading-day checks only when permitted; preserve revisions and report amendments without editing original forecasts.
13. Do not treat listing dates as fetched OHLCV coverage, web query start as API authorization, current adjusted prices as PIT vintages, or synthetic index histories as true ETF prices.
14. No paid data purchases before approved R07 category decision, confirmed dataset gap, supplier quote, rights review and explicit user authorization.
15. Never confuse no fixed category-wide ceiling with unlimited authority: unapproved spend is zero. Never autonomously purchase, auto-renew, register billing methods, enable paid inference or alter the user's subscription.
16. R07-03 zero-budget AI preflight: refuse all external billable inference before any provider call or queue submission, even if cost is estimated zero/unknown or credit exists. Deny retries, embeddings and alternate paid providers. Offline MOCK_ONLY testing is permitted but cannot masquerade as live AI output.
17. Keep a local audit of blocked/mock calls with estimated token and cost data, no actual billing claims without receipts. AI_BUDGET_PAUSED must not interrupt data ingestion, deterministic quant, backtesting or forecast settlement.
## Change process
- Each ADR needs decision, scope, constraints, alternatives, validation status, follow-up.
- Preserve explicitly unresolved decisions as PENDING/BLOCKED; never silently treat proposals as proven.
- Tests of static spec verify consistency only, not external API rights or hardware.
- Do not edit deployment security choices without user approval.
- Explain every change in Traditional Chinese; use English code identifiers.
