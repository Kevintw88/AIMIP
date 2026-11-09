# ADR-003 — Market Implementation Sequence
**Status:** Accepted · **Date:** 2026-11-09
1. **Taiwan**: TWSE + TAIFEX (and TPEx where relevant); complete legal data ingestion → feature/risk → point-in-time backtest → immutable forecast → forward evaluation.
2. **United States**: market/sector/AI infrastructure, authorized price and SEC fundamentals, macro where legally usable.
3. **Japan**: JPX/J-Quants, BOJ/JGB/FX/financials/dividends; verify Japanese data plan terms.
Early US leading indicators are optional for TW analyses and must not block Taiwan-only signals; timestamp cross-market knowledge correctly.
No market shares unverified thresholds, factor weights or trading rules.
## Gate for Taiwan full loop
Licenses approved for needed operations, sufficient price/corporate action history, reproducible signals, transaction cost-aware walk-forward, benchmark comparisons, immutable forecasts and measured settlement.
