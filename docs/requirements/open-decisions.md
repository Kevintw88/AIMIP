# Outstanding Decisions — as of 2026-11-09
## Confirmed
R01 personal-only. R02 Mac mini M4/32GB/1TB; zero-login self-recovery requirement. R03 Taiwan→US→Japan. R03.5 OpenBB conditional. R04 balanced 10 investment instruments + 14 signals. R05 daily-bar based analysis with multiple polling windows, revision handling, idempotent catch-up, and dataset readiness gates (ADR-005).
## Blockers before deployment
- BOOT-PoC: cold reboot, FileVault preboot unlock, headless VM, daemon, UPS and restoration, actual ARM64 compatibility; cannot claim production readiness.
- Licenses: each API dataset download, retention, backtest, LLM inference, model training, backup, rate limits and commercial usage.
- Correct instrument metadata and actual permitted data history.
## R05 — Accepted with empirical validation pending
See [ADR-005](../adr/ADR-005-daily-refresh.md) and [Taiwan schedule](../../specs/schedule_tw.json). Official data release SLAs and source-specific metadata must be verified before connector deployment. The schedule checks data availability; it does not guarantee publication.

## Next: R06 — Historical Backtest Horizon and Acquisition
Decide target years (suggest 10-year target, shorter actual ETF history where listed), point-in-time vintage requirements, survivorship-free universe, split/dividend adjustment, historical derivatives and funding data, permitted archival/AI use, pricing for any missing official historical datasets, and a staged purchase gate. Document gaps per dataset and do not claim surrogate ETF performance as actual performance.
## Later
R07 monthly budget and backup hardware; quantitative factor definitions; point-in-time schemas; evaluation methodologies; AI gateway contracts.
## Acquisition
No paid market API required before licensing and historical coverage assessments. J-Quants Free for API research; only purchase Light/Standard when Japan phase historical/daily data requires it. OpenAI API only once permitted AI integration begins.
