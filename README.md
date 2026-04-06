# model-improvement-planner

[繁體中文 README](README.zh-TW.md)

This skill helps a reading model figure out how to improve a local model without jumping straight to finetuning. It diagnoses the problem, tests the baseline, chooses a sensible path, and produces the next artifacts or scripts needed to move forward.

## What this skill can do

- Normalize a vague capability request into explicit target capability, success criteria, failure modes, deployment context, and constraints.
- Diagnose whether the real problem is in prompt/control, data, objective, runtime, controller, architecture, or missing external subsystems.
- Inspect the local environment, workspace, scripts, and model metadata before assuming execution paths exist.
- Design baseline probes before route selection, then connect those probes to a served model, raw weights, or API-only student endpoint.
- Run a teacher-loop workflow where the reading model itself acts as teacher, critic, verifier, demonstrator, or preference judge.
- Convert probe outputs into dataset records and then into common training formats such as Alpaca, ChatML, ShareGPT, or DPO-style datasets.
- Generate project-local script plans after the route is justified.
- Route correctly when the answer is not training, including runtime adaptation, controller fixes, system composition, or model replacement.
- Handle previously unseen requests by entering a research workflow instead of forcing the request into the closest familiar pattern.

## When to use it

Use this skill when the user asks for things like:

- "Improve my local model's tool use."
- "Figure out whether this checkpoint needs SFT, DPO, or model replacement."
- "Diagnose whether the failure is in the controller or the model."
- "Plan how to improve a local model's multilingual, coding, multimodal, or structured-output behavior."
- "Bridge my current plan into probes, datasets, and project-local scripts."

## Installation

Clone this repo into your agent's skill directory. Requires `python3` 3.8+.

| Platform | Path |
|----------|------|
| Claude Code (project) | `.claude/skills/model-improvement-planner/` |
| Claude Code (global) | `~/.claude/skills/model-improvement-planner/` |
| Codex | `~/.codex/skills/model-improvement-planner/` |
| Antigravity (global) | `~/.gemini/antigravity/skills/model-improvement-planner/` |

```bash
git clone https://github.com/xu-0306/model-improvement-planner.git <path-from-table>
```

## Project structure

`SKILL.md` is the entry point. Supporting references, scripts, evaluations, and artifact contracts are organized under `references/`, `scripts/`, and `evaluations/`.
