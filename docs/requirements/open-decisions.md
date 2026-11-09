# Outstanding Decisions — as of 2026-11-09
## Confirmed
R01 personal-only. R02 Mac mini M4/32GB/1TB; zero-login self-recovery requirement. R03 Taiwan→US→Japan. R03.5 OpenBB conditional. R04 balanced 10 investment instruments + 14 signals. R05 daily-bar based analysis with multiple polling windows, revision handling, idempotent catch-up, and dataset readiness gates (ADR-005). R06 ten-year 2016-11-09–2026-11-09 research objective with 7 listing-eligible/3 shorter instruments, incremental data purchase gates and PIT controls (ADR-006). R07-01 recurring market data API budget policy is no fixed monthly cap, each quote/license/renewal individually approved (ADR-007 v0.1).
## Blockers before deployment
- BOOT-PoC: cold reboot, FileVault preboot unlock, headless VM, daemon, UPS and restoration, actual ARM64 compatibility; cannot claim production readiness.
- Licenses: each API dataset download, retention, backtest, LLM inference, model training, backup, rate limits and commercial usage.
- Correct instrument metadata and actual permitted data history.
## R05 — Accepted with empirical validation pending
See [ADR-005](../adr/ADR-005-daily-refresh.md) and [Taiwan schedule](../../specs/schedule_tw.json). Official data release SLAs and source-specific metadata must be verified before connector deployment. The schedule checks data availability; it does not guarantee publication.

## R06 — Accepted design, availability not certified
See [ADR-006](../adr/ADR-006-ten-year-history.md) and [machine-readable coverage audit](../../specs/history_coverage_tw.json). 10y target does not imply full licensed archive. Official TWSE historical stock page supports older inquiries, TAIFEX 3-major-institution positions web query is generally 3 years, and all 14 signal categories still require entitlement/row-level history verification.

## R07 — Partially accepted (ADR-007)
R07-01 ACCEPTED: recurring market data subscriptions have no fixed monthly category ceiling; every purchase needs vendor quote, actual license rights, individual owner approval and renewed review on price/rights/renewal change. Approval to use a governance process does **not** approve a dollar amount or any purchase. See [ADR-007](../adr/ADR-007-budget-governance.md) and [budget policy](../../specs/budget_policy.json).

## Next: R07-02 (one-time ten-year historical backfill)
Choose one-time acquisition cap/process. Then R07-03 monthly OpenAI inference budget and R07-04 external encrypted backup SSD/NAS + UPS cost envelopes, separately. All are PENDING; no purchases or new paid API jobs are allowed.

## Before full development
Machine-readable coverage flags remain PENDING; Mac mini headless + FileVault PoC, OpenBB ARM64 spike, release-time contracts, data permissions, corporate actions and empirical completeness all need verification.
## Later
quantitative factor definitions; point-in-time schemas; evaluation methodologies; AI gateway contracts.
## Acquisition
No paid market API required before licensing and historical coverage assessments. J-Quants Free for API research; only purchase Light/Standard when Japan phase historical/daily data requires it. OpenAI API only once permitted AI integration begins.
