# model-improvement-planner

[English README](README.md)

`model-improvement-planner` 是一個公開的 planning/routing skill，用於本地模型能力改善規劃。它幫 agent 先判斷真正瓶頸、先定義 evaluation，再選擇最窄且合理的介入方式，而不是預設直接進入 finetuning。

## 這個 skill 做什麼

- 把模糊的改善需求整理成明確的目標能力、成功條件、部署情境與失敗面。
- 區分問題究竟在模型本身，還是在 prompting、controller、runtime、retrieval、tool、serving 或 architecture。
- 採用 evaluation-first：先定義 baseline probes、held-out checks 與 stop rules，再討論資料或訓練。
- 選擇最窄且合理的路線，包括 prompting、tooling、data cleanup、finetuning、distillation、system composition、model replacement，或明確 stop/defer。
- 產出有邊界的 planning bundle，包含 diagnosis、已確認與未確認事實、evaluation plan、路線決策、排除方案與下一步。
- 只在需要時載入公開 references，避免把所有變體細節一次塞進主流程。

## 什麼時候適合使用

適合用在這類請求：

- 「判斷這個 checkpoint 應該先改 prompting、做 finetuning，還是直接換模型」
- 「診斷失敗點是在模型、controller，還是 serving stack」
- 「給我一份 evaluation-first 的改善規劃，不要 generic training recipe」
- 「判斷這個 multimodal 或 speech 需求是不是其實是 system composition 問題」
- 「告訴我最小、且有證據門檻支撐的下一步」

## 公開版 skill 形態

公開版 skill 刻意保持精簡：

- `SKILL.md`：主 planning/routing workflow
- `references/`：公開決策支援、輸出形狀指引與規劃示例

若 repo 內有 `legacy/` 目錄，它代表歷史私有工具鏈或舊文檔，不屬於公開 skill 核心。

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

## References 導覽

先從 `SKILL.md` 進入，再只讀當前請求真正需要的 references：

- `references/routing/`：能力 intake、evaluation-first 流程、介入分類與路線選擇
- `references/orchestration/`：stop rules、tool-routing 檢查與未知需求研究指引
- `references/output-shapes.md`：公開版最小輸出形狀
- `references/examples/planning-examples.md`：短版 planning-first 示例
- `references/probes/`、`references/data/`、`references/training/`、`references/domains/`：僅在需要特定路線深度時再讀
