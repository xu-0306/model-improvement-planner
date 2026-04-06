# Cold-Start Playbook

Use this reference when runtime support is unclear and you need a safe default path before writing any discovery artifact or external scaffold.

## Minimum Intake Fact Sheet

Collect only the facts needed to decide whether support already exists and whether new runtime work is safe:

- requested runtime id or adapter name
- model identifier or local artifact path
- model family hint, if known
- checkpoint or weight format
- tokenizer format
- target action: inference, training, or both
- device or hardware constraints
- runtime or library constraints
- known blockers, missing files, or error symptoms

Leave unknown facts empty. Do not replace missing facts with guesses.

## Default Stop Or Continue Rules

Continue when all of these are true:

- the requested runtime target is identifiable
- the model artifacts can be classified at a basic level
- the intended action is clear
- no critical blocker remains hidden behind a guess

Stop and report missing facts when any of these are true:

- runtime identity is ambiguous
- checkpoint or tokenizer format is still unknown and affects loading
- the request mixes inference and training support but only one path is evidenced
- the environment constraint would change the implementation path
- existing support cannot be confirmed or ruled out safely

## Default Response Bundle

When support is missing or uncertain, return one compact bundle:

- intake fact sheet
- support-exists check result
- continue or stop decision
- missing facts list
- next action
- artifact locations, if any were created

Keep the bundle concise and explicit about uncertainty.

When support already exists, return the same bundle but replace the scaffold action with a reuse verdict and the evidence that justified reuse.

## Default Artifact Location Convention

Use a stable, reviewable layout outside the skill package:

- base directory: `artifacts/model-improvement-planner/<target-slug>/`
- discovery artifact: `artifacts/model-improvement-planner/<target-slug>/model-discovery.json`
- scaffold directory: `artifacts/model-improvement-planner/<target-slug>/runtime-scaffold/`
- scaffold manifest: `artifacts/model-improvement-planner/<target-slug>/runtime-scaffold/scaffold_manifest.json`
- notes or assumptions: `artifacts/model-improvement-planner/<target-slug>/runtime-scaffold/SCAFFOLD_NOTE.md`
- dataset export: `artifacts/model-improvement-planner/<target-slug>/dataset-records.jsonl`
- evaluator export: `artifacts/model-improvement-planner/<target-slug>/evaluator-payloads.jsonl`

If the host project already has a stronger convention, follow it consistently and note the override.

## Existing Runtime Support Check

Use this procedure before writing a new scaffold:

1. Search the host project for the requested runtime id, adapter name, or model family hint.
2. Look for existing loader, adapter, wrapper, or manifest files that already claim support.
3. Compare the existing support target against the actual checkpoint format, tokenizer format, and requested action.
4. Reuse existing support only if the evidence matches the requested model and action.
5. If evidence is incomplete, treat support as unconfirmed and fall back to discovery.

Do not infer support from brand names, nearby files, or partially similar adapters.

## Support Gate

You may claim the target is supported only when one of these paths is satisfied:

- reuse path: existing support has concrete evidence and the declared runtime matches the target artifacts and requested action
- scaffold path: a discovery artifact exists, a new scaffold was generated, and scaffold validation succeeded

If neither path is satisfied, stop and report the missing evidence instead of claiming support.
