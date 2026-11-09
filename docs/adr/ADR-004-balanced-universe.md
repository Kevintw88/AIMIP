# ADR-004 — Balanced Taiwan MVP Universe
**Status:** Accepted scope; **Coverage and licensing:** PENDING
## Decision
Layer A: 10 proposed research instruments; Layer B: 14 market-signal categories. This is not equivalent to 24 time series. Machine-readable seeds: `specs/instruments.json` and `specs/signals.json`.
## Instruments
P0: 0050, 00631L, 00685L, 00632R, 00406A.
P1: 006208, 00878, 2330, 2317, 2454.
Names/types are provisional seed metadata, verify with official exchange at ingestion; instrument IDs independent of display symbols.
## Market signals (14 categories)
TAIEX, Taiwan 50, TPEx index, cash market turnover, market breadth, margin financing, short margin, institutional cash net flows, Taiwan index futures, foreign institutional futures positions, options volume PCR, options open-interest PCR, ETF units/creations/redemptions, ETF NAV/premium-discount.
## Mandatory caveats
- Daily leveraged/inverse funds: path-dependent daily reset; never multiply long-horizon index return by leverage factor.
- Active ETFs may lack an index and sufficient live history. Never represent synthetic proxy backtest as actual fund return.
- Separate observed price vs adjusted total-return series and FX conversion assumptions.
- Only known-as-of observations may be used in forecasts.
- Signals must be tagged AVAILABLE / DATA_PENDING / RESTRICTED / UNAVAILABLE, with permission-specific enforcement.
## Verification
Validate each ticker/exchange/product type/listing date/source, feed history, units, dividends/splits, publication timing, storage/backtest/AI rights before enabling production collection. The seed is not a real-time exchange lookup.
## Acceptance
Exactly 10 instruments, exactly 14 categories, unique stable IDs, explicit layer/priority/source candidates and no data source recorded as license-approved until verified.
