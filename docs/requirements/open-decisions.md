# Outstanding Decisions — as of 2026-11-09
## Confirmed
R01 personal-only. R02 Mac mini M4/32GB/1TB; zero-login self-recovery requirement. R03 Taiwan→US→Japan. R03.5 OpenBB conditional. R04 balanced 10 investment instruments + 14 signals. R05 daily-bar based analysis with multiple polling windows, revision handling, idempotent catch-up, and dataset readiness gates (ADR-005). R06 ten-year 2016-11-09–2026-11-09 research objective with 7 listing-eligible/3 shorter instruments, incremental data purchase gates and PIT controls (ADR-006).
## Blockers before deployment
- BOOT-PoC: cold reboot, FileVault preboot unlock, headless VM, daemon, UPS and restoration, actual ARM64 compatibility; cannot claim production readiness.
- Licenses: each API dataset download, retention, backtest, LLM inference, model training, backup, rate limits and commercial usage.
- Correct instrument metadata and actual permitted data history.
## R05 — Accepted with empirical validation pending
See [ADR-005](../adr/ADR-005-daily-refresh.md) and [Taiwan schedule](../../specs/schedule_tw.json). Official data release SLAs and source-specific metadata must be verified before connector deployment. The schedule checks data availability; it does not guarantee publication.

## R06 — Accepted design, availability not certified
See [ADR-006](../adr/ADR-006-ten-year-history.md) and [machine-readable coverage audit](../../specs/history_coverage_tw.json). 10y target does not imply full licensed archive. Official TWSE historical stock page supports older inquiries, TAIFEX 3-major-institution positions web query is generally 3 years, and all 14 signal categories still require entitlement/row-level history verification.

## Next: R07 — Budget, backups and purchase approvals
Confirm **monthly market-data budget cap (TWD)**, **one-time historical backfill cap**, **LLM inference budget**, **dedicated backup disk/NAS/UPS cap**, procurement approvals, quote comparison, fallback for cost overruns and how many monthly API subscriptions are acceptable. Recommended default before quote: no paid market data, use legal free sources and mocks.

## Before full development
Machine-readable coverage flags remain PENDING; Mac mini headless + FileVault PoC, OpenBB ARM64 spike, release-time contracts, data permissions, corporate actions and empirical completeness all need verification.
## Later
quantitative factor definitions; point-in-time schemas; evaluation methodologies; AI gateway contracts.
## Acquisition
No paid market API required before licensing and historical coverage assessments. J-Quants Free for API research; only purchase Light/Standard when Japan phase historical/daily data requires it. OpenAI API only once permitted AI integration begins.
