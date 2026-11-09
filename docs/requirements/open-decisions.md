# Outstanding Decisions — as of 2026-11-09
## Confirmed
R01 personal-only. R02 Mac mini M4/32GB/1TB; zero-login self-recovery requirement. R03 Taiwan→US→Japan. R03.5 OpenBB conditional. R04 balanced 10 investment instruments + 14 signals. R05 daily-bar based analysis with multiple polling windows, revision handling, idempotent catch-up, and dataset readiness gates (ADR-005). R06 ten-year 2016-11-09–2026-11-09 research objective with 7 listing-eligible/3 shorter instruments, incremental data purchase gates and PIT controls (ADR-006). R07-01 recurring market data API budget policy is no fixed monthly cap, each quote/license/renewal individually approved. R07-02 historical one-time data has no fixed total cap; each exact dataset, quotation and license is individually approved (ADR-007 v0.2). R07-03 OpenAI API has a zero monthly/daily/per-call budget and all external paid inference is disabled (ADR-007 v0.3). R07-04 is existing-assets-first with zero new procurement budget, but hardware/offsite/restore tests and any actual purchases remain open (ADR-007 v1.0).
## Blockers before deployment
- BOOT-PoC: cold reboot, FileVault preboot unlock, headless VM, daemon, UPS and restoration, actual ARM64 compatibility; cannot claim production readiness.
- Licenses: each API dataset download, retention, backtest, LLM inference, model training, backup, rate limits and commercial usage.
- Correct instrument metadata and actual permitted data history.
## R05 — Accepted with empirical validation pending
See [ADR-005](../adr/ADR-005-daily-refresh.md) and [Taiwan schedule](../../specs/schedule_tw.json). Official data release SLAs and source-specific metadata must be verified before connector deployment. The schedule checks data availability; it does not guarantee publication.

## R06 — Accepted design, availability not certified
See [ADR-006](../adr/ADR-006-ten-year-history.md) and [machine-readable coverage audit](../../specs/history_coverage_tw.json). 10y target does not imply full licensed archive. Official TWSE historical stock page supports older inquiries, TAIFEX 3-major-institution positions web query is generally 3 years, and all 14 signal categories still require entitlement/row-level history verification.

## R07 — Budget policy ACCEPTED (ADR-007 v1.0)

R07-01 ACCEPTED: market data recurring subscriptions have no fixed category cap; every actual provider purchase requires quotation, rights verification and individual approval.

R07-02 ACCEPTED: ten-year historical data has no fixed *aggregate* acquisition cap, but each dataset and payment amount needs separate approval. Preapproved spend remains zero.

R07-03 ACCEPTED: OpenAI API monthly/daily/per-run NT$0. External billable AI is disabled; MOCK_ONLY and deterministic non-AI research are allowed.

R07-04 ACCEPTED policy: existing backup media/NAS/UPS first; new equipment purchase budget NT$0. **Inventory, encryption/key handling, offsite location/recurring cost, UPS availability and clean restore have not been verified.** No hardware purchase or offsite paid subscription is authorized.

See [ADR-007](../adr/ADR-007-budget-governance.md) and [budget policy](../../specs/budget_policy.json).

## Next: ARR-001 Architecture Readiness Review and Phase 0 gates

See [ARR-001](../reviews/ARR-001-R01-R07.md), [Codex Phase 0 acceptance](../phase0/PHASE0-ACCEPTANCE.md), and [machine-readable gates](../../specs/readiness_gates.json).

All R01–R07 decisions are accepted; Phase 0 plan is ready, **execution NOT AUTHORIZED**, production NO-GO. Separate explicit approval is required for scoped Phase 0, access to the physical Mac, intentional power-outage testing, any privileged system changes or any live market dataset ingestion. No paid API jobs, equipment orders or autonomous payments are permitted.

## Before full development
Machine-readable coverage flags remain PENDING; Mac mini headless + FileVault PoC, OpenBB ARM64 spike, release-time contracts, data permissions, corporate actions and empirical completeness all need verification.
## Later
quantitative factor definitions; point-in-time schemas; evaluation methodologies; AI gateway contracts.
## Acquisition
No paid market API required before licensing and historical coverage assessments. J-Quants Free for API research; only purchase Light/Standard when Japan phase historical/daily data requires it. OpenAI API only once permitted AI integration begins.
