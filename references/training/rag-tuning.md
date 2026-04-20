# RAG-Tuning

Use this reference when the serving path depends on retrieval and the model must be trained to use retrieved evidence better.

## Goal

Reserve RAG-tuning for cases where the failure is evidence use, grounding, or distractor handling, not merely missing retrieval plumbing.

## Choose When

- Retrieval is already part of the intended serving path.
- The model sees relevant evidence but still answers weakly or hallucinates.
- Training examples include retrieved context as a first-class input.

Method boundary:
- Use generator-side tuning when retrieval quality is acceptable but evidence use is weak.
- Use dual retriever-generator tuning only when both retrieval quality and grounding behavior are materially failing.

## Avoid When

- The plan is only to add inference-time RAG with no training.
- The retriever cannot produce plausible candidate documents yet.
- The task will not depend on retrieval at deployment.

## Require Before Proceeding

- A baseline retriever or retrieval pipeline.
- Grounded examples that include retrieved context and desired answers.
- Distractors or hard negatives that test evidence selection.
- Evaluation that checks grounding, not only answer overlap.

## Key Risks

- The model memorizes answers instead of using evidence.
- Tuning overfits to one retrieval format or one corpus snapshot.
- Grounding claims are made without citation or evidence-use checks.
- Retriever drift at serving time breaks gains seen during tuning.
