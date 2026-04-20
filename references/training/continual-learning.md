# Continual Learning

Use this reference when updates are sequential and retention of earlier behavior is part of the requirement.

## Goal

Reserve continual learning for repeated updates where forgetting must stay within a defined budget.

## Choose When

- The model will be updated more than once over time.
- Preserving prior capabilities is an explicit requirement.
- New-task gain and old-task retention both matter.

Mitigation boundary:
- Use replay when old examples can be retained safely.
- Use regularization when old data are limited but retention still matters.
- Use distillation-based retention when a previous model can act as the reference for old behavior.

## Avoid When

- The work is really one more fine-tuning stage with no retention requirement.
- The main goal is corpus adaptation rather than bounded forgetting.
- The change is narrow enough for model editing instead.

## Require Before Proceeding

- A defined update sequence or update cadence.
- A retained benchmark for older behavior.
- A stated forgetting budget or regression threshold.
- A named mitigation family: replay, regularization, distillation, or a justified combination.

## Key Risks

- Catastrophic forgetting is discovered too late because only the newest task was measured.
- Regularization preserves parameters without preserving behavior.
- Replay introduces privacy, licensing, or contamination problems.
- Retention safeguards block needed adaptation on the new task.
