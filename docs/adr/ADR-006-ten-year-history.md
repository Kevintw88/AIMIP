# ADR-006 — Ten-Year Historical Data & Point-in-Time Backtesting

**Project:** AI Market Intelligence Platform (AI-MIDEP)
**Version:** 1.0
**Decision:** ACCEPTED — R06 ten-calendar-year objective
**Status:** Design accepted; actual provider data coverage, access & licensing **NOT YET VERIFIED**
**As of:** 2026-11-09
**Target research window (inclusive):** 2016-11-09 to 2026-11-09 (Asia/Taipei)
**Related:** ADR-001, ADR-003, ADR-004, ADR-005, ADR-003A

## 1. Architectural decision

- Ten years is a **TARGET window**, not a promise every instrument/signal has ten years of genuine traded observations.
- Distinguish `LISTING_ELIGIBLE_10Y` from `FULL_HISTORY_VERIFIED`, `API_ACCESS_VERIFIED`, `LICENSE_APPROVED`, and `PIT_SAFE_VERIFIED`. No source has been downloaded or licensed by this ADR.
- For instruments listed after 2016-11-09, begin at actual listing and retain explicit structural gaps.
- Market data, adjusted OHLCV, total-return, dividends, corporate actions, derivatives and macro/financial release vintages have separate provenance.
- Do not backfill future revisions into point-in-time signals. Historic adjusted bars without historical adjustment vintages are not themselves proof of PIT safety.
- Separate two model families:
  - `BASE_10Y`: authorized, verified long-run prices/turnover/basic factors.
  - `ENRICHED_SHORTER`: derivative positions, fund flows, ETF NAV/active ETF, and shorter/uneven history; any evaluation reports its valid window.
- Unsupported historical periods MUST be missing; synthetic/reconstructed proxies labeled `SYNTHETIC_PROXY` and tested separately from actual tradable returns.
- No paid vendor access is required before the dataset gaps, licenses, and pricing have been confirmed in writing.

## 2. Research universe: 10 instruments

Official TWSE ETF listing record: https://www.twse.com.tw/zh/products/securities/etf/products/list.html
Official ISIN listings: https://isin.twse.com.tw/isin/C_public.jsp?strMode=2
00406A listing reference: https://www.twse.com.tw/zh/ETFortune/etfInfo/00406A

| Symbol | Official listing | Ten-year listing eligibility | Reality / action |
|---|---|---|---|
| 0050 | 2003-06-30 | ELIGIBLE | Verify 2016-11+ daily OHLCV, ETF split 4:1 2025-06-18, dividends, expense assumptions |
| 006208 | 2012-07-17 | ELIGIBLE | Verify 2016-11+ OHLCV, distributions/corporate actions |
| 00631L | 2014-10-31 | ELIGIBLE | Daily 2x mechanics; actual fund bars, not 2× accumulated index returns |
| 00685L | 2017-03-30 | STRUCTURALLY_SHORT | No fund history 2016-11-09 through 2017-03-29 |
| 00632R | 2014-10-31 | ELIGIBLE | Daily inverse 1x and path-dependence; actual fund bars |
| 00406A | 2026-06-11 | STRUCTURALLY_SHORT | New active ETF, no fixed index; no decade of fund returns |
| 00878 | 2020-07-20 | STRUCTURALLY_SHORT | Only post-listing fund history and distributions |
| 2330 | 1994-09-05 | ELIGIBLE | Verify actual daily bars, stock splits/dividends, delisting status |
| 2317 | 1991-06-18 | ELIGIBLE | Same |
| 2454 | 2001-07-23 | ELIGIBLE | Same |

**7/10 listing-eligible; 3/10 structurally short.** This is listing-date evidence only, NOT downloaded data coverage.
Machine-readable `specs/history_coverage_tw.json` contains per-instrument metadata, all source-access/retention/PIT flags still pending.

## 3. Taiwan official/third-party historical availability evidence

### Public / potentially free
1. TWSE accessible individual daily trading archive advertises availability since 2010-01-04; it is a query/download UI, NOT automatic approval for bulk API database ingestion:
   https://accessibility.twse.com.tw/zh/trading/historical/stock-day.html
2. TWSE daily aggregate market trading amount/TAIEX web archive advertises since 1990-01-04:
   https://www.twse.com.tw/zh/trading/historical/fmtqik.html
3. TWSE margin balance page advertises from 2001-01-01:
   https://www.twse.com.tw/zh/trading/margin/mi-margn.html
4. TWSE OpenAPI includes current/periodic report interfaces; DO NOT assume `STOCK_DAY_ALL` is a complete 10-year historical archive:
   https://openapi.twse.com.tw/
5. TAIFEX public daily/annual futures downloads are available, but precise years, contract history, calendar conventions and rights must be checked:
   https://www.taifex.com.tw/cht/3/futDailyMarketView
6. TAIFEX institutional positions public query notes data beginning 2008-04-07 but ordinary online querying generally limits to last 3 years; older material requires application:
   https://www.taifex.com.tw/cht/3/futContractsDateView
7. TAIFEX official information FAQ discusses historical data purchase for older/transaction-level archives and limits on reproduction/redistribution:
   https://www.taifex.com.tw/cht/9/tradersQAIS
8. Official TWSE market data e-shop offers certain historical products:
   https://www.twse.com.tw/zh/products/dataeshop.html
9. Licensed/rights-checked alternate: Fugle historical-candles documentation advertises daily individual equity/ETF prices back to 2010, one request less than a year, and adjusted/unadjusted alternatives. The provider currently advertises free Basic historical endpoint allowance 60/min; **archival/backtest/third-party LLM rights still require contract check**:
   https://developer.fugle.tw/docs/data/http-api/historical/candles/
   https://developer.fugle.tw/docs/pricing/

### Important source limitations
- Online range is not equivalent to licensed bulk download or point-in-time historical revisions.
- `taifex` has separate regular/afterhours sessions and rollover rules; rolling continuous future prices should not be mistaken for executable contract fills.
- For many index/signal sources, exact earliest available observation and 10-year continuity have NOT been individually confirmed. Coverage status remains `HISTORY_UNVERIFIED`.
- Upstream provider current adjusted historical series may be recalculated on new company actions. Save action events with **as-known** timestamps and avoid future adjustment factors in prior signals.
- Independent corporate-action/event source is needed to reconstruct cash distributions and share adjustments. Prices alone are insufficient for correct total return and transaction simulation.

## 4. The 14 signal families and history gaps

| ID | Official/source evidence | Verified historical window indication | 10Y permission/completeness |
|---|---|---|---|
| TAIEX | TWSE aggregate daily trading page | Web archive dates back to 1990 | PENDING |
| TAIWAN50 | TWSE / licensed index administrator | Index historical archive not confirmed | PENDING |
| TPEX_INDEX | TPEx index / licensed prices | Range not verified | PENDING |
| CASH_TURNOVER | TWSE aggregate daily trading page | Web archive dates back to 1990 | PENDING |
| MARKET_BREADTH | TWSE/TPEx daily market statistic | Continuous 2016+ series unverified | PENDING |
| MARGIN_FINANCING | TWSE margin balance archive | Web archive from 2001 | PENDING |
| MARGIN_SHORT | TWSE margin balance archive | Web archive from 2001 | PENDING |
| INSTITUTIONAL_CASH | TWSE public reports / e-shop BFI82U | Paid product lists data start 2004-02-19 | PENDING |
| TAIEX_FUTURES | TAIFEX daily/annual downloads; candidate licensed API | Years per archive and 10y roll data unverified | PENDING |
| FOREIGN_FUTURES_POSITION | TAIFEX institutional contracts by date | 2008+ history exists; web generally only last 3y | **HISTORICAL_ACQUISITION_GAP** |
| OPTIONS_VOLUME_PCR | TAIFEX PCR reports | Current data exists; 10y archive not proven | PENDING |
| OPTIONS_OI_PCR | TAIFEX PCR reports | Current data exists; 10y archive not proven | PENDING |
| ETF_UNITS_FLOW | TWSE / fund company / custody registry | ETF-specific, completeness/version unverified | PENDING |
| ETF_NAV_PREMIUM | TWSE ETF information / fund company | ETF-specific, completeness/version unverified | PENDING |

Signals `PENDING` means availability/permissions/completeness are not certified. No signal category should be marked ready merely due to an available web page.

## 5. Data contracts: price, corporate actions, revisions and PIT

### Canonical raw bar
`instrument_id, trade_date, session_id, open, high, low, close, volume, volume_unit, turnover, currency, vendor_id, dataset_id, observed_at, published_at (nullable), first_seen_at, ingested_at, available_at, revision_id, payload_hash, license_decision_id`.
Never extrapolate `published_at` from `ingested_at`, or infer `first_seen_at` for 2016 from today's download.

### Corporate actions and total returns
- Preserve **original executable OHLCV** separate from `adjusted_price`, adjustment factors, and `total_return_index`.
- Archive (only if licensed) effective date, announcement timestamp, record/ex date, cash dividend, stock dividend, splits/reverse splits, capital reduction, rights issues, ETF unit changes, fees and taxes.
- For 0050 explicitly check 4:1 split on 2025-06-18 (TWSE notice): https://www.twse.com.tw/zh/ETFortune/announcement?company=A00005&date=20250509&fund=0050&seq=1&type=other
- Adjust splits consistently: price divided by ratio and shares multiplied by ratio; cash distributions credited on relevant dates per simulation policy; preserve position value within rounding.
- A *current* adjusted price series may use post-event adjustments across all historical bars. **Never pass future adjustment factors into a historical signal.**
- Fee, bid-ask, applicable transaction tax, dividend withholding and borrow/funding fees should be parameterized. For leveraged/inverse ETFs use actual ETF traded bars and daily-reset/path-dependent analysis rather than constant multi-year leverage multiplication.

### PIT and revision model
- `event_time` / `trade_date`: when market event occurred.
- `published_at`: source evidence-backed release time, NULL if unknown.
- `first_seen_at`: first time the platform observed payload, cannot be backdated.
- `available_at`: conservative verified usable time; if unknown, PIT_VERIFIED=false.
- `ingested_at`: actual ingestion.
- `snapshot_id` / `revision_seq` / `source_version` / `hash`.
- Existing historical reports and forecasts immutable. Corrections append new observations + evaluation runs; prior predictions do not change.
- Strict PIT-safe experiments must provide evidence of historical observation availability and original universe; `PIT_UNVERIFIED` datasets can support exploratory description but not certified unbiased forward-like testing.

### Survivorship and tradability
- Original point-in-time instrument universe includes delisted/suspended constituents for market-wide strategies.
- Prices/volumes on halt days, market calendars, lot sizes, tick sizes, ETF creation/cancellation, limit-up/down and futures margin rules need explicit assumptions.
- No fill can occur at an already-known close on the same day's close signal. Default benchmark: calculate after verified close, transact next eligible market session at supported open/price assumption with transaction costs.
- Avoid using post-2026 ETF constituents or later product disclosures in 2016 predictions.
- Distinguish actual fund history from a `SYNTHETIC_PROXY` index-derived research scenario.

## 6. Acquisition & paid-data decision (NOT a purchase authorization)

### Gate H0 — Free inventory now
Identify dataset IDs, official website historical query, bulk/export method, public open-data licensing, API terms, true earliest downloadable row, date/count coverage, corporate actions, and source revision metadata. No paid subscription.

### Gate H1 — Technical sample validation, no costly history yet
Use documented legitimate free endpoints or manual sample download. Verify small samples at start/middle/end of 10-year window for each of 7 eligible symbols; verify each of 14 signal classes; report gaps. Do not automate scraping that violates terms. Request written clarification for historic storage/backtest/AI inference.

### Gate H2 — Need-based quotations
Ask TWSE Data E-Shop, TAIFEX E-Data Shop / official application path, fund managers and candidate third-party vendors for **exact dataset / period / type of use / retention / historical revisions**. Price must be quoted by vendor or verified checkout; no estimated TAIFEX historical price fabricated.

### Gate H3 — Purchase only when validated
Pay only if dataset is essential to a specified model and cannot be lawfully sourced free; written terms confirm permissible local history, backups, PIT/backtest and if required LLM inference. Prefer one-time historical backfill purchase and separate ongoing daily data policy if economically better; confirm allowed.

### Observed price references (not quotes for required coverage)
- Fugle Basic: advertised no-fee historical candle requests (60/min) conditional on acceptable user terms.
- Fugle Developer: NT$1,499/month; Advanced: NT$2,999/month, mainly higher real-time services. **No reason to buy for daily history until free plan limits/rights fail.**
  https://developer.fugle.tw/docs/pricing/
- TWSE E-Shop institutional cash report BFI82U: visible **NT$1,000 per month of internal-use subscribed data**, data start 2004-02-19, per-order up to 5 years; this is **one product's rate, not an estimate for full 14-signal bundle or an approved 10-year quote**:
  https://eshop.twse.com.tw/zh/product/detail/d31c1b9570ae47058ec83a0bb1ffa419
- TWSE/TAIFEX entire 10-year historical data basket: **QUOTE_REQUIRED**.
- Historical derivatives and institution positions: **QUOTE_REQUIRED**; check whether freely published annual aggregate data covers some requirements.
- API inference provider charges only in AI phase, not R06; personal J-Quants paid plans belong to later Japan phase.

### Cost envelope
- `FREE_FIRST`: NT$0 in new market-data subscriptions, but coverage/permitted use not certified.
- `FUGLE_DEV_OPTION`: NT$1,499/month if later justified by functionality (not ten-year archive license).
- `FUGLE_ADV_OPTION`: NT$2,999/month if later justified (no MVP need).
- `TWSE_BFI82U_OPTION`: NT$1,000 per subscribed month for the documented product; multi-year total requires validated order & terms.
- `TAIFEX_HISTORY_OPTION`: TBD/QUOTE_REQUIRED.
- `ENTERPRISE_PIT_VENDOR_OPTION`: TBD/QUOTE_REQUIRED.
**No amount here implies acquisition approval.**

## 7. Backtesting methodology & acceptance

1. `R06-01` Historical inventory for all 10 + 14 with explicit instrument listing dates, earliest/last accessible dates, licensing state, missing sessions, corporate actions and verified source references.
2. `R06-02` Exactly 7 symbols listing-eligible for 10-year objective; exactly 3 structurally short. Never use pre-listing fund bars.
3. `R06-03` For each required dataset, store rights separately for local storage, backtest, derivatives, backup and third-party AI inference. Unknown => DENY.
4. `R06-04` At least three sampled dates (beginning/middle/end within actual listing window) reconcile OHLCV/volume units against licensed source; verify 100% expected trading dates only after source archive completeness is confirmed.
5. `R06-05` All prices and corporate actions versioned, consistency checked for adjusted and unadjusted series; validate split/dividend arithmetic with fixtures.
6. `R06-06` Strict PIT model rejects unknown publication/availability time for non-price fundamentals and disclosures; revisions cannot leak into earlier folds.
7. `R06-07` Next-session fills, fees/slippage/taxes, ETF daily reset and derivative contract rolls explicitly modeled.
8. `R06-08` Walk-forward split with purging/embargo for overlapping forecast horizons, frozen parameter selection and out-of-sample results.
9. `R06-09` Baselines = buy/hold, deterministic quant-only and optional Quant+AI; no certification of AI benefit without independently matured observations.
10. `R06-10` Reports document sample periods, coverage percentage, exclusions, calendar mismatches, data restrictions, adjusted-price vintage, and statistical uncertainty.
11. `R06-11` Paid data requires documented data gap, supplier entitlement, transparent cost comparison and explicit user approval.
12. `R06-12` Source outage/403 or license mismatch fails closed and does not auto-switch to unlicensed scraped data.

## 8. Not yet proved / unresolved
- Whether accessible archives can be automatically bulk queried and permanently stored for AI-MIDEP's specific purposes.
- Actual ten-year row completeness and provenance for each symbol, fund action and signal.
- A historical **as-of** revision feed for all 14 signals.
- Pricing and entitlement of TAIFEX older institutional-position data, and reliable 10-year PCR / ETF unit/NAV history.
- Provider-specific stock adjustment methodologies and licensing for third-party model use.
- R07 budget, capex for backups/UPS and month-to-month operational spending.

## 9. Source links (checked 2026-11-09)
- TWSE ETF product list: https://www.twse.com.tw/zh/products/securities/etf/products/list.html
- TWSE historical individual price archive: https://accessibility.twse.com.tw/zh/trading/historical/stock-day.html
- TWSE margin history: https://www.twse.com.tw/zh/trading/margin/mi-margn.html
- TWSE aggregate trading: https://www.twse.com.tw/zh/trading/historical/fmtqik.html
- TAIFEX institution history limitation: https://www.taifex.com.tw/cht/3/futContractsDateView
- TAIFEX annual futures downloads: https://www.taifex.com.tw/cht/3/futDailyMarketView
- TAIFEX FAQ: https://www.taifex.com.tw/cht/9/tradersQAIS
- TWSE E-Shop: https://www.twse.com.tw/zh/products/dataeshop.html
- Fugle historical API: https://developer.fugle.tw/docs/data/http-api/historical/candles/
- Fugle pricing: https://developer.fugle.tw/docs/pricing/
- TWSE E-Shop institutional cash example: https://eshop.twse.com.tw/zh/product/detail/d31c1b9570ae47058ec83a0bb1ffa419

**Next:** R07 operational budget, separate backups/UPS, paid data budget cap, AI API cost caps, and official purchasing approvals.
