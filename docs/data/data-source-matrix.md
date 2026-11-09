# Data Sources — Approval Matrix (initial)
**Every entry PENDING until verified for specific dataset and intended use.** This is a planning inventory, not a license grant.

| Provider | Dataset family | Role | Historical depth | Retention / backtest / external LLM | Purchase timing |
|---|---|---|---|---|---|
| TWSE | equity/ETF OHLCV, margin, corporate action | Taiwan core | VERIFY | PENDING | Free API inspection now; paid data only if gap |
| TAIFEX | futures, options, PCR, institution | Taiwan derivatives core | VERIFY | PENDING | Paid history only when R06 established |
| TPEx | OTC index/equity and margin | Taiwan breadth | VERIFY | PENDING | Later connector |
| Official fund managers | ETF NAV, creation units, dividends | ETF analytics | VERIFY | PENDING | On data coverage gap |
| US licensed market-data API | equity/ETF indices | optional global context/US phase | VERIFY | PENDING | US phase |
| SEC EDGAR | company filings/XBRL | US fundamentals | VERIFY | PENDING | US phase |
| FRED/ALFRED | macro releases/revisions | macro research | VERIFY | **Do not warehouse/LLM-forward unless specifically authorized** | Do not purchase |
| J-Quants V2 | Japanese prices/fundamentals | Japan phase | VERIFY plan | PENDING by license/plan | Free for evaluation; paid later |
| TradingView MCP | personal interactive research | NOT warehouse | N/A | **No automated warehousing/model evaluation** | Optional only |
| OpenBB | connector/framework, not license source | integration candidate | Provider-dependent | Must check underlying provider rights | Spike first |

Required registry fields: `provider_id`, `dataset_id`, `terms_url`, `license_checked_at`, `allow_download`, `allow_storage`, `allow_backtest`, `allow_ai_inference`, `allow_ml_training`, `allow_redistribution`, `allow_backup`, `retention_until`, `status`.
Permission status enum: PENDING / APPROVED / RESTRICTED / DENIED. Default: deny all until evidence recorded.
