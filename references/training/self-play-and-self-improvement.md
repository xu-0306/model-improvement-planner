# Self-Play and Self-Improvement

Use this reference when the route depends on iterative self-generated supervision rather than direct external labels.

## Goal

Choose self-play only when the loop itself is the intervention and there is an external way to tell whether it is helping.

## Choose When

- A reasonably strong seed model already exists.
- Direct human or teacher supervision is limited, but the model can generate useful candidates.
- An independent acceptance surface exists outside the self-play loop.

Loop boundary:
- Use self-play fine-tuning when later iterations learn from stronger earlier candidates.
- Use self-judging loops only when those judgments are checked against an external evaluator.
- Use self-synthesized alignment data only when the goal is broad data expansion, not one narrow task fix.

## Avoid When

- A better external teacher already exists.
- The model is still too weak to generate useful supervision.
- The same model family would generate, judge, and declare success without outside checks.

## Require Before Proceeding

- Separate proposer and judge roles, even if both come from the same family.
- Held-out evaluation that is not produced by the loop itself.
- Checks for deduplication, collapse, and judge drift across iterations.
- A stop rule tied to diminishing returns or visible instability.

## Key Risks

- Self-imitation is mistaken for improvement.
- Judge leakage rewards the model's own rubric instead of real quality.
- Diversity collapses while average loop scores rise.
- Synthetic data drift moves the model away from real user inputs.
