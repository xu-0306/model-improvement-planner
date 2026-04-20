# Distillation Patterns

Use this reference when distillation is already selected and the remaining question is what teacher signal to transfer.

## Goal

Pick the lightest distillation pattern that preserves the behavior the student actually needs.

## Choose When

- A stronger teacher already exists and is good enough to supervise a smaller or cheaper student.
- The deployment target benefits from compression more than from serving the teacher directly.
- The main signal comes from teacher behavior, not from new human supervision.

Pattern boundary:
- Use response distillation by default.
- Add rationale distillation only when intermediate reasoning helps and the student can absorb it.
- Use trajectory distillation only when ordered tool use or multi-step behavior matters.
- Use soft-target distillation only when logits or distributions are available and worth the extra complexity.

## Avoid When

- The teacher is not trustworthy enough to become training signal.
- The real problem is missing data quality, evaluator quality, or base-model mismatch.
- A direct model replacement is cheaper than maintaining a student.
- Rich teacher traces are being added only because they look more sophisticated.

## Require Before Proceeding

- A clear statement of what must transfer: final answers, reasoning hints, trajectories, or distributions.
- Evidence that the student has enough capacity for that signal shape.
- Held-out evaluation against the target deployment behavior.
- A comparison against a simpler non-distillation baseline.

## Key Risks

- The student copies teacher style instead of capability.
- Teacher mistakes become durable targets.
- Trace-heavy supervision overwhelms a small student.
- Soft-target complexity adds cost without real gain.
