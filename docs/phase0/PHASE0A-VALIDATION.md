# Phase 0A 離線驗證與證據索引

依 [ARR-001](../reviews/ARR-001-R01-R07.md)、[驗收規格](PHASE0-ACCEPTANCE.md) 與 [AGENTS.md](../../AGENTS.md) 執行。使用者已授權本 PR 的合成資料契約、靜態檢查及 GitHub Actions。Mac mini 唯讀盤點須先取得存取權限。付費 API、未授權真實行情、採購、下單、FileVault 變更、系統 LaunchDaemon 安裝與斷電測試均超出本次範圍。

## 重現方式

在 PR 對應的版本，以 Python 3.12 執行下列指令。

```sh
git rev-parse HEAD
python3 --version
python3 scripts/validate_specs.py
python3 -B scripts/run_phase0a_tests.py
```

測試僅使用 Python 標準函式庫、本儲存庫規格與合成測試資料。測試程序拒絕 Python socket、DNS 與啟動外部程序的事件，即使程式攔下例外，測試程序也會以非零結束。CI 的 GitHub checkout 與 Python 環境準備是獨立步驟。執行時間、平台、SHA、個別測試輸出及 CI 連結記於 PR 證據欄與 [Specification Validation 日誌](https://github.com/Kevintw88/AIMIP/actions/workflows/spec-validation.yml)。`specs/readiness_gates.json` 保留 ARR-001 基準，執行證據按 PR 的 SHA 及 GitHub Actions run 查核，待決策人審閱。

## Phase 0A 涵蓋矩陣

| 關卡 | 設定與測資 | 預期結果及證據 |
|---|---|---|
| PH0-S01 | `specs/instruments.json`、`signals.json`、`history_coverage_tw.json` | `test_phase0_catalog` 驗證 10 個標的、14 類訊號、穩定識別碼、7/3 上市資格與資料授權待審。 |
| PH0-S02 | `specs/schedule_tw.json` 與合成交易日、夜盤、延遲及修訂資料 | `test_phase0_market` 驗證跨休市日、補抓、重試及配額、T+1/T+2/T+5/T+20、重放冪等性與不可變歷史。真實發布時限待驗證。 |
| PH0-S03 | 0050 4:1 合成拆分與假設現金股利 | `test_phase0_market` 驗證原始價格、拆分與股利生效時間、無未來調整洩漏、次一交易日模擬成交及費用。 |
| PH0-S04 | 缺失、延遲及修訂的合成時間戳 | `test_phase0_data` 驗證截至時間查詢，分開處理來源發布、首次已知與匯入時間，拒絕缺乏 PIT 證據的資料。 |
| PH0-S05 | 合成 Mock Connector 和資料集用途授權 | `test_phase0_data` 驗證未知授權預設拒絕、用途分開授權，切換 mock 來源仍走同一守門。 |
| PH0-S06 | `specs/budget_policy.json` 與合成推論請求 | `test_phase0_budget` 驗證每日、每月、單次 NT$0，外部零估價、未知估價、抵用額、重試、備援與 embeddings 在送出前拒絕；保留本地稽核、`MOCK_ONLY` 及確定性流程。 |
| PH0-S07 | GitHub Actions、乾淨的 Linux runner、Python 3.12 | GitHub run 記錄 checkout SHA、UTC、平台、完整靜態與離線測試結果。 |
| PH0-S08 | `specs/budget_policy.json` 與合成硬體／離站提案 | `test_phase0_budget` 驗證預算 0 或未知、缺報價、缺明確核准，以及 Phase 0A 禁採購限制。 |

## 未執行或阻擋的關卡

| 關卡 | 狀態 | 缺少的證據或條件 |
|---|---|---|
| PH0-H01–H04 | `NOT_RUN` | 尚未取得 Mac mini 存取權限。硬體、OS、FileVault、網路、VM 候選、備份媒體、UPS 及離站費用待盤點。後續高風險操作須另行審核安全計畫。 |
| PH0-B01–B08 | `NOT_RUN` | 主機電源恢復、登入前服務、ARM64 VM、FileVault 解鎖、三次冷開機、故障恢復、獨立加密還原與 UPS 訊號都需要後續實機驗證。 |
| PH0-O01–O04 | `NOT_RUN` | 未執行 OpenBB V5 實際擴充、ARM64 匯入與 API/MCP、Native 對照及實際整合守門。離線資料契約證據歸於 S04/S05。 |
| PH0-O05 | `BLOCKED` | 任何真實資料使用前須逐資料集查核條款、取得授權並記錄允許用途。十年資料列覆蓋及真實 PIT 版本仍未知。 |

ARR-001 的 8 個生產阻擋項目維持開啟。離線修訂、PIT 與費用守門證據適用於 Phase 0A。生產放行仍需驗證無人登入恢復、加密備份還原、私有服務配置、ARM64 相容性與資料權利，並經決策人審閱。
