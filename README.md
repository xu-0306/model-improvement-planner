# model-improvement-planner

[繁體中文 README](README.zh-TW.md)

`model-improvement-planner` is a public planning and routing skill for local-model improvement work. It helps an agent diagnose the real bottleneck, define evaluation before optimization, and choose the narrowest viable intervention instead of defaulting to finetuning.

## What this skill does

- Normalize a vague improvement request into a concrete target capability, success condition, deployment context, and failure surface.
- Separate model-side problems from prompting, controller, runtime, retrieval, tool, serving, or architecture problems.
- Work evaluation-first: define baseline probes, held-out checks, and stop rules before proposing data or training work.
- Choose the narrowest rational route, including prompting, tooling, data cleanup, finetuning, distillation, system composition, model replacement, or explicit stop/defer.
- Produce a bounded planning bundle with the diagnosis, confirmed versus missing facts, evaluation plan, route decision, rejected alternatives, and next actions.
- Use the public references as optional depth, loading only the parts needed for the current route.

## When to use it

Use this skill for requests such as:

- "Figure out whether this checkpoint needs prompting changes, finetuning, or model replacement."
- "Diagnose whether the failure is in the model, the controller, or the serving stack."
- "Give me an evaluation-first improvement plan instead of a generic training recipe."
- "Decide whether this multimodal or speech request is actually a system-composition problem."
- "Tell me the smallest next step that is evidence-gated and worth trying first."

## Public skill shape

The public skill surface is intentionally small:

- `SKILL.md`: the main planning and routing workflow
- `references/`: public decision support, output guidance, and planning examples

If a `legacy/` directory is present, it contains historical private-tooling material and is not part of the public skill core.

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

## Reference guide

Start from `SKILL.md`, then read only the references needed for the current request:

- `references/routing/`: capability intake, evaluation-first flow, intervention taxonomy, and route selection
- `references/orchestration/`: stop rules, tool-routing checks, and unknown-requirement research guidance
- `references/output-shapes.md`: minimal public output bundle shapes
- `references/examples/planning-examples.md`: short planning-first examples
- `references/probes/`, `references/data/`, `references/training/`, `references/domains/`: route-specific depth loaded only when needed
