# Model Editing Method Taxonomy

Use this reference when the requested change is a narrow post-hoc update rather than a broader training run.

## Goal

Decide whether a targeted edit is justified and, if so, keep the edit scope narrow.

## Choose When

- The request is a bounded fact, relation, or small behavior correction.
- Preserving nearby behavior matters as much as making the target change.
- A fast targeted update is preferable to broad retraining.

Method boundary:
- Use direct parameter edits only for small, well-scoped updates.
- Prefer memory-backed or overlay-style edits when reversibility and accumulation matter.
- Treat multi-step editors as a last resort for structured updates that cannot be expressed as a simple edit.

## Avoid When

- The real need is domain adaptation, style shift, or broad capability gain.
- Many updates will accumulate and interference is likely.
- Retrieval or explicit memory can solve the issue more safely.
- The runtime cannot support the chosen edit mechanism.

## Require Before Proceeding

- An exact statement of what should change and what must stay unchanged.
- Locality and specificity checks, not just one before-after prompt.
- A rollback path for bad edits or edit interference.
- Evidence that the requested change is narrow enough for editing at all.

## Key Risks

- Collateral regressions outside the edit scope.
- False confidence from success on a single prompt.
- Sequential edits interfere with one another.
- A narrow edit mechanism is forced onto a broad problem.
