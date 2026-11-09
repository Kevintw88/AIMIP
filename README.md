# AI Market Intelligence Platform (AI-MIDEP)

> **Architecture baseline v1.4 · 2026-11-09 · Specification only — NOT production-ready**

個人自用的跨市場投資研究平台：合法資料蒐集 → Point-in-Time 量化訊號 → 回測 → AI 輔助研究 → 不可變預測 → 到期評估與模型改善。

## 決策狀態

| ID | 決策 | 狀態 |
|---|---|---|
| ADR-001 | 個人自用、單使用者、禁止真實自動下單 | Accepted |
| ADR-002 | Mac mini M4 32GB/1TB；完全無人值守為硬性要求 | Accepted requirements; **boot/FileVault/VM PoC BLOCKED** |
| ADR-003 | 台灣 → 美國 → 日本，先建立台灣完整閉環 | Accepted |
| ADR-003A | OpenBB V5 有條件複用；Native Connector 保留 | Conditional; **ARM64/授權 Spike PENDING** |
| ADR-004 | 台灣 MVP：10 個研究標的與 14 類市場訊號 | Accepted scope; **資料覆蓋與授權待驗證** |
| R05 | 更新頻率、資料可用時間與排程 | Next decision |

## 文件索引
- [Codex 協作規則](AGENTS.md)
- [ADR-001 個人研究](docs/adr/ADR-001-personal-use.md)
- [ADR-002 Mac mini 無人值守](docs/adr/ADR-002-mac-mini-headless.md)
- [ADR-003 市場建置順序](docs/adr/ADR-003-market-order.md)
- [ADR-003A OpenBB 複用策略](docs/adr/ADR-003A-openbb-conditional.md)
- [ADR-004 R04 平衡型研究範圍](docs/adr/ADR-004-balanced-universe.md)
- [資料來源與授權待驗證](docs/data/data-source-matrix.md)
- [待決事項與 R05](docs/requirements/open-decisions.md)
- [Instrument Master seed](specs/instruments.json)
- [Signal Catalog seed](specs/signals.json)
- [規格校驗腳本](scripts/validate_specs.py)

## 已確定
- 台灣優先、日線研究、跨市場前導資料為可選依賴。
- 使用 PostgreSQL 管理記錄，Parquet/DuckDB 供授權範圍內之批次研究。
- 確定性程式計算績效；LLM 解讀、提出可驗證假設，**不得改寫已發布預測**。
- 資料使用權限預設 DENY，另行確認 storage/backtest/AI inference/training 權限。
- Mac mini 完全無人值守仍為**待實機證明**，不可因 Docker 啟動成功就標示已驗收。

## 不在目前階段
不執行行情抓取、不配置正式 API Key、不購買付費資料、不實作交易下單，也不宣稱任何投資預測結果已被證實。

## 規格驗證
在具 Python 3.12+ 的環境執行：
```bash
python3 scripts/validate_specs.py
```
或在 GitHub Actions 使用「Specification Validation」。這只驗證目前 catalog 與 ADR 的一致性，**不是**資料供應商、ARM64、VM 自動啟動或交易策略功能測試。
