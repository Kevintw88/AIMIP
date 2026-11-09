# ADR-003A — Reuse-First OpenBB Strategy
**Status:** Accepted — CONDITIONAL Adoption; **Spike:** PENDING
## Decision
Prefer OpenBB V5 for reusable finance provider interfaces, selected data SDK/REST/MCP and existing analytical tools. Keep AI-MIDEP's own `MarketDataProvider` abstraction and provider-agnostic normalized schemas.
**OpenStock is UI/UX reference only**; do not fork as platform base.
## Taiwan first
Official TWSE/TAIFEX/TPEx connectors must remain viable without OpenBB. Consider OpenBB provider extensions only after comparative spike; J-Quants provider later.
## Non-reusable core
License Gateway, point-in-time storage/revisions, risk factors specific to market/ETF, backtest accounting, immutable forecast registry, forward evaluation, champion–challenger and deployment security.
## OSS-01 to OSS-09 pre-adoption gate
Install pinned OpenBB V5 on Linux ARM64; start SDK/REST/MCP; prototype one authorized Taiwan dataset; compare native adapter and extension complexity; demonstrate fail-closed license controls and tool allowlists; test memory under 16GB VM budget; simulate failures; verify no dependency lock-in.
## Legal
Open source software license does not convey provider market-data rights. No agent may bypass data authorization. Do not allow OpenBB MCP to access unauthorized raw datasets.
## Fallback
Native connectors for Taiwan; OpenBB optional for selected US/global feeds. Preserve platform contracts without code rewrite.
