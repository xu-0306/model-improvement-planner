# Model Merging Guide

Use this reference when the route combines existing checkpoints instead of running another training job.

## Goal

Use merging only when compatible source checkpoints already exist and combining them is lower risk than new optimization.

## Choose When

- Multiple relevant checkpoints already exist from the same base family.
- Avoiding another training run is a real cost or latency advantage.
- The merged model can be tested against each source capability after combination.

Method boundary:
- Start with simple task arithmetic as the baseline.
- Use conflict-aware or sparsified merges only when naive merging shows clear interference and evaluation justifies the extra complexity.

## Avoid When

- Base models, tokenizers, or checkpoint formats are not compatible enough.
- One existing checkpoint already dominates the others.
- The real need is new data, a new objective, or a smaller student.

## Require Before Proceeding

- A clear inventory of what is being merged: full checkpoints, deltas, or adapters.
- Compatibility across base model family and tokenizer assumptions.
- Evaluation against the best single-source checkpoint, not only against the base model.
- Regression checks for every source capability that matters.

## Key Risks

- Parameter interference hides behind one good headline score.
- A lucky coefficient works on one benchmark but not on the real task mix.
- Export or serving behavior differs from what training-time tests suggested.
- Merging is used where model replacement would be simpler.
