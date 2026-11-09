# AGENTS.md — AI-MIDEP Codex Rules
## Status
This repository is in **specification freeze preparation**. Do not begin application development until the user approves R06–R07, data licensing, and Phase 0 initiation. R05 has been accepted as a schedule and data-freshness specification, not tested production behavior.

## Scope
- Single user; Taiwan → US → Japan; Taiwan MVP 10 investment instruments + 14 market signal categories.
- Mac mini M4, 32GB RAM, 1TB SSD; host macOS, proposed headless Linux ARM64 VM, **unattended recovery unverified**.
- OpenBB V5 *conditional* adapter, not an unconditional runtime dependency.
- ADR-005: daily-bar analysis with multiple dataset-aware polls, delayed-release and corrections checks, append-only revisions, immutable forecasts. Schedule is not a publication SLA.
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
## Change process
- Each ADR needs decision, scope, constraints, alternatives, validation status, follow-up.
- Preserve explicitly unresolved decisions as PENDING/BLOCKED; never silently treat proposals as proven.
- Tests of static spec verify consistency only, not external API rights or hardware.
- Do not edit deployment security choices without user approval.
- Explain every change in Traditional Chinese; use English code identifiers.
