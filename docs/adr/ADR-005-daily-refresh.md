# ADR-005 — Taiwan Daily Data Refresh, Freshness & Correction Policy

**Project:** AI Market Intelligence Platform (AI-MIDEP)  
**Status:** ACCEPTED (business policy), integration and source SLAs PENDING  
**Decision:** R05 B — 日線研究、多次檢查、補抓與修訂  
**Date:** 2026-11-09 · **Version:** 1.0  
**Related:** ADR-001, ADR-002, ADR-003, ADR-003A, ADR-004, R06

## 1. Decision / Non-goals
- 以每日收盤（日線）資料計算台灣市場正式量化訊號；每日多次詢問資料來源是否齊備並處理補發、修訂。
- 收集排程≠資料發布 SLA；**不將預設檢查時刻視為交易所已公布**，以逐資料集 readiness gate 判斷。
- 不將過期資料當最新資料，不補造缺漏行情，不使用尚未被當時研究流程知悉的數據。
- 第一版不含逐筆/分鐘級即時行情、盤中自動交易與交易所即時授權 feed。
- 外部資料源在核准「下載、保存、回測、外部 AI 推論」各用途前，維持 PENDING/RESTRICTED 並拒絕該用途。
- 本 ADR 的 schedule 是**設計規格**，尚未部署 Prefect，也沒有證明官方資料 API 的準時更新或可回補能力。

## 2. Exchange and session semantics
- 所有時間資料以 UTC 儲存（RFC3339，附 offset），畫面與排程以 `Asia/Taipei` 呈現。
- Taiwan market calendars: TWSE / TAIFEX / TPEx 分開建模，包含交易所休市、補班、特殊停止交易及臨時公告。
- 台股集中市場正常現貨交易約 09:00–13:30，但此不保證任意 OpenAPI dataset 於 13:30 完成。資料更新依 dataset。
- 台灣期貨的日盤、晚盤/夜盤與部分商品特殊收盤時刻、交易日期歸屬需依 TAIFEX 交易日曆與商品規則；不可將夜盤觀測誤歸屬至本機日期。
- 對每個來源標準化 `market`, `session_id`, `trade_date`, `instrument_id`, `dataset_id`；查不到 session/date mapping 時阻止正式入庫與計分。

## 3. Proposed polls (Asia/Taipei) — NOT exchange guarantees
| Time | Poll / job | Objective |
|---|---|---|
| 07:30 | previous-day + overnight reconciliation | 前一個完整交易日、期貨夜盤與可選美股前導資料；缺值保留 |
| 08:00 | pre-market report gate | 只用可證明此前已取得/發布的快照；若不完整，發布標記為 DEGRADED 的摘要或不發布完整風險分數 |
| 13:50 | TWSE initial check | 日行情候選與來源 readiness；不得宣稱此時必定有完整終值 |
| 14:30 | TWSE and TAIFEX poll | 現貨/期貨價量、必要資料項 |
| 15:30 | first completeness gate | Core close candidate；視必要資料完整性判斷是否 READY |
| 16:30 | institutions and financing poll | 法人、融資融券；交易所公布時點依實際資料集 |
| 18:30 | TAIFEX late-session/revisions | 補發、延遲資訊、變更 |
| 20:30 | reconciliation and quality gate | 依資料集品質報告與已授權資料產生可用版本 |
| 23:00 | revisions and matured forecast settlement | 比對版本；只結算已到期且真實結果完整的預測 |

Schedule parameters are machine-readable in `specs/schedule_tw.json`. **08:00、15:30、20:30、23:00 是平台檢查與產出候選的時刻，並非所有來源的強制截止。**

## 4. Per-dataset freshness policy
每個 dataset 必須具備：
- `provider_id`, `dataset_id`, `source_endpoint_or_reference`, `license_decision_id`
- `calendar_id`, `session_rule`, `trade_date`, `expected_key_set`, `required_fields`
- `first_poll_at`, `last_success_at`, `first_seen_at`, `published_at`（來源有證據才填）
- `ingested_at`, `available_at`（採能證明為當時已可用的保守時間）, `source_revision_id`（如可得）
- `payload_hash`, `schema_version`, `normalizer_version`, `row_count`, `quality_status`, `availability_status`

Unknown source publication time must remain NULL, not backfilled from assumed closing time. `first_seen_at` is first observed by our system; not a substitute for historical real-world availability. Historical backtest without point-in-time vintage must be tagged `PIT_UNVERIFIED` and excluded from PIT-safe training/testing.

### State machine
`NOT_DUE -> PENDING -> PARTIAL -> READY` (on quality and license approval); `READY -> CORRECTED` when source changes; `STALE` when due freshness exceeded; `RESTRICTED` on disallowed use; `UNAVAILABLE` when unreachable or retries exhausted. `CORRECTED` triggers append-only revision + re-evaluation and may return to `READY` for the newer version. State status describes data readiness; usage permission is checked separately and always fail-closed.

`READY` requires: permitted use; correct trading date/session; complete required instrument keys and fields; valid units and non-negative volumes where defined; no unhandled duplicates; valid corporate actions; provenance, content checksum and timestamp fields; freshness threshold evaluated against actual source evidence. Zero values may be legitimate; do not replace with missing.

### Data-to-report gates
- `CRITICAL`: required per-report datasets missing => full report withheld or shown with explicit DEGRADED and no numerical claim dependent on unavailable data.
- `OPTIONAL`: missing data => affected factor disabled; unaffected Taiwan-only factors may still be READY.
- A report must identify each factor's dataset version, as-of cutoff, missing data and authorization basis.
- AI-only enrichment may not bypass the same data/freshness/license checks.

## 5. Retries, catch-up and rate limits
- Source poll is idempotent at (provider, dataset, trade_date, session, query/parameter hash); revisions distinguished by content hash or source revision.
- On transient 5xx/network: bounded retries with exponential backoff + jitter (proposal: 2, 5, 15 min) and alert after exhaustion.
- On HTTP 429: respect `Retry-After` and provider quota; no parallel burst to overcome limits.
- On 4xx authentication/permission: stop and alert, no brute-force retry.
- Late release or `PENDING`: retry at next configured poll rather than overwriting data with stale values.
- After host failure / macOS reboot, enumerate missed market sessions and scheduled jobs, restore from last durable watermark, and safely replay eligible tasks; do not silently backdate `first_seen_at`.
- License expired/revoked => stop ingestion and downstream operations as required; evaluate permitted retention/deletion of already-held data.

## 6. Reconciliation and append-only revisions
Proposed follow-up checks after each trade date: `T+1, T+2, T+5, T+20` **market trading days**, and on explicit upstream correction notifications; configurable per dataset and subject to rate limits and permissions. R06 determines how far historical rescan/backfill can reach. ETF dividends and corporate actions may require a longer verified reconciliation period.
- Persist original permitted raw versions with checksums, and create new immutable versions when content differs. Do not overwrite past observations or previously published forecasts.
- Normalization is deterministic, versioned, and reconstructible.
- Recompute dependent factors/backtests/reports for the corrected view, *but* preserve historical forecasts based on the information actually known when published.
- Subsequent amended report references `supersedes_report_id`; preserve prior report and clearly label correction reason.
- Do not settle predictions until the evaluation horizon and relevant outcome price series are complete; after a price correction, create a new evaluation run with link to prior scoring and unchanged original probability.

## 7. Contract examples (logical)
`ingestion_runs`: run_id, dataset_id, scheduled_at, started_at, ended_at, status, error_code, retry_count, license_decision_id, quality_summary.
`dataset_snapshots`: snapshot_id, dataset_id, trade_date, session_id, revision_seq, payload_hash, first_seen_at, published_at nullable, available_at, ingested_at, source_uri, license_decision_id.
`dataset_watermarks`: provider_id, dataset_id, session_id, last_verified_trade_date, last_success_at, last_checked_at, source_content_hash, due_state.
`quality_issues`: severity, dataset_id, trade_date, observed_at, issue_code, affected_keys, remediation_status.
`report_revisions`: report_id, based_on_snapshot_ids, as_of, published_at, supersedes_report_id nullable, report_state.

## 8. Error handling / observability
Track freshness lag, source latency, API success/failure by dataset, 429 rates, missing instrument ratio, zero-row anomaly, correction frequency, stale-report count, catch-up backlog, permission denials, backup success and last successful scheduled run.
No secrets, private holdings or raw licensed payloads in operational logs. Host health monitoring remains subject to ADR-002 PoC.

## 9. Acceptance tests (design)
- R05-01: no holiday / no valid session => no false missing-data alerts, unless an official revised-release is expected.
- R05-02: 13:50 empty dataset => PENDING, not fabricated READY.
- R05-03: late 20:30 availability => quality pass & READY without overwriting original state history.
- R05-04: same payload retrieved repeatedly => one logical data version, repeated run audit records allowed.
- R05-05: corrected T+2 row => new revision and amended report; old forecast immutable.
- R05-06: restart after >2 days => correct catch-up and idempotent outcomes.
- R05-07: malformed dates, sessions, schema drift, duplicate keys, missing required instruments => PARTIAL/UNAVAILABLE with alert.
- R05-08: API 429 => backoff and quota enforcement; no aggressive retry.
- R05-09: license not approved => stop prohibited ingest/storage/backtest/LLM use.
- R05-10: prior US context stale => Taiwan-only report still possible, cross-market model explicitly UNAVAILABLE.
- R05-11: unknown historical publication time => PIT_UNVERIFIED and prohibited from PIT-safe model evaluation.
- R05-12: all reports include as-of, input snapshot IDs and freshness status.

## 10. External evidence and validation TODO
Official sources:
- TWSE OpenAPI: https://openapi.twse.com.tw/ (dataset names, **not** their freshness SLA)
- TWSE market hours: https://www.twse.com.tw/zh/products/information/information.html
- TAIFEX OpenAPI: https://openapi.taifex.com.tw/
- TAIFEX FAQ (specific disclosure schedules, permission and historical depth): https://www.taifex.com.tw/cht/9/tradersQAIS

Before connector implementation, check live schema, availability timing empirically, official API terms, trading session calendars and actual permitted historical ranges **per dataset**. Some TAIFEX reports publish later and offer limited historical querying; do not generalize any one dataset's schedule.

## 11. Open items / dependency
- **R06 next:** historical backtest horizon, PIT-vintage availability, adjusted pricing, corrections horizon, backfill licensing and paid acquisition gate.
- **R07:** cloud/API budget, backup media, UPS, 24×7 availability targets.
- ADR-002: Mac mini restart/FileVault/headless VM PoC.
- ADR-003A: OpenBB ARM64 + provider license spike.
