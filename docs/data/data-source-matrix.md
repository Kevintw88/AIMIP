# Data Sources — Approval Matrix (initial)
**Every entry PENDING until verified for specific dataset and intended use.** This is a planning inventory, not a license grant.

| Provider | Dataset family | Role | Historical depth | Retention / backtest / external LLM | Purchase timing |
|---|---|---|---|---|---|
| TWSE | equity/ETF OHLCV, margin, corporate action | Taiwan core | Website advertises individual price from 2010, margin from 2001; API history/rights VERIFY | PENDING | Inspect free website and Data E-Shop; buy only if data gap |
| TAIFEX | futures, options, PCR, institution | Taiwan derivatives core | Public annual futures downloads, institution position online queries generally 3y; older access APPLY/QUOTE | PENDING | First examine free annual reports, then request older data quotation |
| TPEx | OTC index/equity and margin | Taiwan breadth | VERIFY | PENDING | Later connector |
| Official fund managers | ETF NAV, creation units, dividends | ETF analytics | Listed ETF lifespan and action-history depth differ | PENDING | On data coverage gap |
| US licensed market-data API | equity/ETF indices | optional global context/US phase | VERIFY | PENDING | US phase |
| SEC EDGAR | company filings/XBRL | US fundamentals | VERIFY | PENDING | US phase |
| FRED/ALFRED | macro releases/revisions | macro research | VERIFY | **Do not warehouse/LLM-forward unless specifically authorized** | Do not purchase |
| J-Quants V2 | Japanese prices/fundamentals | Japan phase | VERIFY plan | PENDING by license/plan | Free for evaluation; paid later |
| TradingView MCP | personal interactive research | NOT warehouse | N/A | **No automated warehousing/model evaluation** | Optional only |
| Fugle | historical TW stock/ETF daily candles | Optional price backfill | Docs advertise individual listed stock/ETF daily since 2010; API limit <1y/query; exact ticker/history rights VERIFY | PENDING | Free Basic advertised 60 history requests/min; paid developer NT$1,499/mo only if needed |
| OpenBB | connector/framework, not license source | integration candidate | Provider-dependent | Must check underlying provider rights | Spike first |

Evidence and purchase gates: [ADR-006 ten-year history](../adr/ADR-006-ten-year-history.md), [R06 coverage inventory](../../specs/history_coverage_tw.json). Official TWSE E-Shop institutional cash report BFI82U shows historical product starting 2004 and NT$1,000 per subscribed internal-use month, which must not be assumed to price all history. **No vendor access/usage rights approved.**

Required registry fields: `provider_id`, `dataset_id`, `terms_url`, `license_checked_at`, `allow_download`, `allow_storage`, `allow_backtest`, `allow_ai_inference`, `allow_ml_training`, `allow_redistribution`, `allow_backup`, `retention_until`, `status`.
Permission status enum: PENDING / APPROVED / RESTRICTED / DENIED. Default: deny all until evidence recorded.
