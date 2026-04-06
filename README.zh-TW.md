# model-improvement-planner

[English README](README.md)

這個 skill 的用途是幫讀取模型判斷，應該怎麼改善一個本地模型，而不是一開始就直接導向 finetuning。它會先診斷問題、做基線測試、選路線，再產出後續需要的 artifacts 或 scripts。

## 這個 skill 能做什麼

- 把模糊的能力需求整理成明確的目標能力、成功標準、失敗模式、部署情境與限制。
- 判斷真正的問題是在 prompt/control、data、objective、runtime、controller、architecture，還是缺少外部系統。
- 在選路線前先檢查本地 workspace、scripts、模型資訊、runtime 與可用工具，而不是先做假設。
- 設計 baseline probes，並把 probe 執行接到已部署 student、raw weights、或 API-only 存取的模型。
- 執行 teacher loop，而且 teacher 就是正在讀這個 skill 的模型自己。
- 把 probe 結果轉成 dataset record，再轉成 Alpaca、ChatML、ShareGPT、DPO 等常見訓練格式。
- 在路線合理後，生成 project-local 的 script plan。
- 當正確答案其實不是訓練時，正確地路由到 runtime adaptation、controller 修復、system composition 或 model replacement。
- 遇到未知需求時進入研究流程，而不是硬套到最接近的既有路線。

## 什麼時候適合使用

當使用者提出這類需求時，就適合用這個 skill：

- 「幫我提升本地模型的 tool use 能力」
- 「判斷這個 checkpoint 應該用 SFT、DPO，還是乾脆換模型」
- 「幫我分辨問題是在 controller 還是在模型本身」
- 「規劃如何提升本地模型的多語、coding、多模態或 structured output 能力」
- 「把目前的 plan 橋接成 probes、dataset 與 project-local scripts」

## 安裝方式

將此 repo clone 到你的 agent skill 目錄。需要 `python3` 3.8+。

| 平台 | 路徑 |
|------|------|
| Claude Code（專案） | `.claude/skills/model-improvement-planner/` |
| Claude Code（全域） | `~/.claude/skills/model-improvement-planner/` |
| Codex | `~/.codex/skills/model-improvement-planner/` |
| Antigravity（全域） | `~/.gemini/antigravity/skills/model-improvement-planner/` |

```bash
git clone https://github.com/xu-0306/model-improvement-planner.git <上方對應路徑>
```

## 專案結構

`SKILL.md` 是入口。支援文件、腳本、評估案例與 artifact contracts 分別在 `references/`、`scripts/` 與 `evaluations/` 底下。
