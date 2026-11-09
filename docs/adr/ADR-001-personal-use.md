# ADR-001 — Personal Research Platform
**Status:** Accepted · **Date:** 2026-11-09
## Decision
AI-MIDEP 是單人、私人、非商業投資研究系統，涵蓋台灣、美國、日本市場。提供每日資料研究、量化訊號、回測、AI 分析與預測績效評估。**不包含真實自動下單、對外售賣訊號、公開 API 再散布、企業多租戶**。
## Data and security boundary
- 所有資料集分別審查 download / local-storage / backtest / AI-inference / AI-training / redistribution / retention / backup。
- 未核准用途預設拒絕（fail closed），即使已擁有個人訂閱也不代表允許永久建庫。
- 非公開研究 Dashboard；最小權限、私人 VPN、憑證隔離、可追溯稽核。
- LLM 不得覆寫確定性計算；只有通過授權資料可交第三方 API。
## Non-goals
公開商業化、券商自動交易、即時 Tick/HFT、未授權新聞內容集中儲存。
## Validation
政策設計已接受；個別來源授權尚待資料供應商條款檢查。
