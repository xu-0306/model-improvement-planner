# Supervision Shapes

Use this reference when mapping available data signal to a training family.

## Goal

Identify the strongest reliable supervision signal first, then choose the simplest method that matches it.

## Signal to Method Map

| Signal | Usually points to | Do not assume |
| --- | --- | --- |
| Unlabeled corpus | continued pretraining, domain adaptation, relabeling before supervised tuning | raw data quality or task alignment |
| Demonstration pair or instruction-response pair | supervised fine-tuning, imitation | consistent correctness or preference strength |
| Critique-rewrite | correction tuning, rewrite tuning, mistake-aware supervised tuning | critique quality matches rewrite quality |
| Chosen-rejected | preference optimization, pairwise reward learning | absolute scores or calibrated margins |
| Binary acceptable-unacceptable | filtering, safety classifier, coarse reward signal | reliable ranking between positives |
| Scalar reward | reward modeling, reranking, score-based filtering | scores are comparable across raters or tasks |
| Verifier result | correctness filtering, rejection sampling, verifier-guided search | verified means fully high quality |
| Process-step labels or trajectories | process supervision, tool-use distillation, trajectory learning | local success implies global success |
| Soft targets or teacher distributions | distillation | stack can support target alignment cheaply |

## Choose When

- Use direct supervised tuning when you have reliable target outputs.
- Use preference methods when comparisons are easier to collect than gold answers.
- Use verifier-driven methods when correctness can be checked externally.
- Use distillation when teacher outputs or distributions are the primary signal.
- Use relabeling or continued pretraining when only unlabeled corpora exist.

## Avoid When

- Different signal strengths are mixed as if they were the same label type.
- Weak synthetic labels are treated as equivalent to trusted human or verifier labels.
- Converted data are promoted to stronger supervision without checking error rate.

## Require Before Proceeding

- A clear label definition for each signal type.
- A small audited sample showing actual label quality.
- Separation between training signal quality tiers.
- Evaluation that matches the claimed supervision strength.

## Key Risks

- Noisy labels dominate apparent gains.
- Style imitation is mistaken for capability gain.
- Data contamination or duplication inflates results.
- Converted supervision is trusted beyond what it supports.
