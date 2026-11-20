# apple-shortcuts-skill

一個讓 AI agent **在沒有 Mac 的情況下，寫出真正能安裝的 Apple 捷徑**的 skill。

大多數 agent 只能告訴你要在捷徑 App 裡點哪些按鈕。這個 skill 教的是完整流程：

1. **設計** — 把工作流程寫成資料，而不是一步步點。其中一個關鍵技巧：用一串有順序的「取代文字（正規表示式）」動作，當作不用條件分支的 if/else 邏輯。
2. **先測邏輯** — 組裝之前，先用 Python 把同一套規則拿真實輸入模擬跑過。
3. **組裝** — 用 [`python-shortcuts`](https://pypi.org/project/python-shortcuts/) 產生未簽署的 `.shortcut`，包含函式庫缺少的「取代文字」動作，以及它沒做的 plist 後處理（分享頁類型、輸入類型、圖示）。
4. **簽署** — iOS 15 之後，未簽署的 `.shortcut` 檔案會被拒絕，只跳一句「無法載入檔案」。簽署可以用 Mac（`shortcuts sign`），或遠端簽署服務如 [Shortcuty Sign](https://sign.shortcuty.app)、RoutineHub HubSign（上傳前必須先取得使用者同意 — agent 要先問）。
5. **交付** — 交給使用者的必須是簽署完成的檔案（驗證開頭是 `AEA1` 魔術字節），使用者點一下就能安裝，再附一個具體的實機測試方式。

## 內容

- [`SKILL.md`](SKILL.md) — skill 本體。放進你的 agent 的 skills 資料夾（Claude Code、Codex、Muse……），agent 就能照著做。
- [`tools/build_template.py`](tools/build_template.py) — 可重用的組裝模板：自訂「取代文字」動作、plist 後處理、組完自動回讀驗證動作清單。
- [`examples/open-in-apple-maps/`](examples/open-in-apple-maps/) — 完整實作範例：把 Google Maps 連結用 Apple 地圖開啟的分享頁捷徑。網路上流傳的原版會**開錯位置** — 它解析的是 `@緯度,經度`（地圖畫面中心），不是 `!3d…!4d…`（地點本身的釘點座標），而且沒有先展開短連結。範例含 `test_logic.py`，用 7 個案例模擬裝置上實際執行的同一套正規表示式鏈。

## 快速開始

```bash
cd examples/open-in-apple-maps
python3 test_logic.py                     # 7 個案例應該全過
python3 -m venv .venv
.venv/bin/pip install python-shortcuts
.venv/bin/python build.py                 # 產出未簽署的 .shortcut
# 接著簽署（見 SKILL.md 第 4 步），再把檔案傳到 iPhone
```

## 需求

- Python 3.10+
- `python-shortcuts`（pip）
- 簽署方式三選一：有 Shortcuts 的 Mac、免帳號的遠端簽署服務、或從已有該捷徑的裝置產生 iCloud 分享連結。

## 授權

MIT — 見 [`LICENSE`](LICENSE)。
