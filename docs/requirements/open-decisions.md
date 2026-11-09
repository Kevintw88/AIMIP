# Outstanding Decisions — as of 2026-11-09
## Confirmed
R01 personal-only. R02 Mac mini M4/32GB/1TB; zero-login self-recovery requirement. R03 Taiwan→US→Japan. R03.5 OpenBB conditional. R04 balanced 10 investment instruments + 14 signals.
## Blockers before deployment
- BOOT-PoC: cold reboot, FileVault preboot unlock, headless VM, daemon, UPS and restoration, actual ARM64 compatibility; cannot claim production readiness.
- Licenses: each API dataset download, retention, backtest, LLM inference, model training, backup, rate limits and commercial usage.
- Correct instrument metadata and actual permitted data history.
## Next: R05 — Frequency / Freshness
Decide day-bar cutoff, reporting schedules, late releases, revise windows, rerun rules, fail-open/closed states, and whether any intraday analysis is permitted. **Proposed default**: daily close-based signals; sources may publish after close, only issue report when available; late data marks DEGRADED and retries.
## Later
R06 historical period and survivorship-free acquisition plan; R07 monthly budget and backup hardware; quantitative factor definitions; point-in-time schemas; evaluation methodologies; AI gateway contracts.
## Acquisition
No paid market API required before licensing and historical coverage assessments. J-Quants Free for API research; only purchase Light/Standard when Japan phase historical/daily data requires it. OpenAI API only once permitted AI integration begins.
