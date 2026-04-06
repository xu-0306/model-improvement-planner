# Teacher-Loop Execution Guide

Use this document when the reading model needs to turn a plan into a concrete teacher loop that feeds dataset, evaluator, and artifact pipelines.

## Teacher-as-Self Architecture

The running reading model is the teacher. It does not call a separate teacher endpoint. The same Claude/GPT instance that produced the plan must:

- send probes to the student through the backend adapter it can reach
- collect the student replies and populate `probe-results.jsonl`
- self-evaluate each reply, producing scores, diagnoses, corrections, or verifier judgements
- emit the repaired responses, corrections, or rewards into dataset-level artifacts without assuming any extra model

Every loop cycle stays within the current process: communicate with the student, review the answers, correct them, and write dataset records or evaluator payloads.

## Loop Steps

1. **Confirm backend availability.** Verify the student backend defined by `backend_config.json` responds; if not, generate or update the config before moving on.
2. **Load or author probe-specs.** Use the probe spec template to build or refresh a JSONL set that matches the target capability.
3. **Run `scripts/run_capability_probes.py`.** Pass the probe specs plus the backend config to emit fresh `probe-results.jsonl` and a summary.
4. **Gather probe results.** Read every entry in `probe-results.jsonl`, capturing prompts, student output, and metadata.
5. **Self-review each result.** For each `probe_result`:
   - score the answer (`score`, `passed`, `comments`)
   - categorize errors (hallucination, format failure, omission, etc.)
   - produce a corrected or exemplar response when appropriate
6. **Convert into dataset records.** Map (probe input, student response, teacher correction) into the dataset envelope and append to `dataset-records.jsonl`.
7. **Validate dataset contract.** Validate each emitted record against the `dataset_record` schema before keeping it in `dataset-records.jsonl`. Use `scripts/validate_contracts.py` on per-record JSON exports or a small local validation loop before appending the line.
8. **Check loop sufficiency.** If data count, score averages, or diversity thresholds are missing, loop back to Step 2 with new probe specs.

## Prompt Templates for Teacher Roles

Use placeholders (`<target_capability>`, `<probe_context>`, `<student_output>`) so the prompts stay domain-neutral.

1. **Critique teacher**
   ```text
   Role: Critique teacher
   Target: <target_capability>
   Evidence: probe input (<probe_context>), student response (<student_output>)
   Return: score (0-1), passed flag, observed defects, rewrite guidance, corrected output
   Constraints: keep output short, label each defect, supply a concise correction
   ```
2. **Demonstrator**
   ```text
   Role: Demonstrator
   Target: <target_capability>
   Evidence: probe input (<probe_context>) without a usable student attempt
   Return: exemplar response, style notes, difficulty tag, abstain rule if uncertain
   Constraints: do not reuse student text, keep instructions clear for imitation
   ```
3. **Verifier**
   ```text
   Role: Verifier
   Target: <target_capability>
   Evidence: student output (<student_output>) and required constraints
   Return: verdict (pass/fail/abstain), checks run, failed checks, evidence, confidence
   Constraints: prefer explicit checks, do not guess missing facts
   ```
4. **Preference judge**
   ```text
   Role: Preference judge
   Target: <target_capability>
   Evidence: candidate A (<candidate_a>) vs candidate B (<candidate_b>) from the same probe
   Return: chosen_candidate, rejected_candidate, comparison_basis, confidence
   Constraints: justify the choice using observable quality differences
   ```
5. **Diagnostician**
   ```text
   Role: Diagnostician
   Target: <target_capability>
   Evidence: probe summary, student outputs, existing defect pattern
   Return: failure_modes, missing_skills, confidence, suggested_next_probes
   Constraints: do not prescribe a training method yet, keep observations audit-friendly
   ```

## Mapping Probe Results to Dataset Records

Translate each `probe_result` into a `dataset_record` entry, then into framework-specific wrappers only after dataset validation:

- `probe_result.input` -> `dataset_record.input`, then `instruction` or `messages[0].content` during conversion
- `probe_result.student_response` -> include under `supervision.rejected_candidate`, `candidates`, or discard after diagnostics when the route is pure SFT
- teacher correction (critique, rewrite, demonstration) -> `dataset_record.target`, then `output` or `messages[1].content` during conversion
- `probe_result.metadata` -> `dataset_record.metadata.source_provenance`

Keep the envelope contract-stable: include `contract`, `schema_version`, `input`, `target`/`supervision`, metadata with `teacher_role` or `teacher_roles`, `confidence`, and provenance.

## Quality Gate

Each loop should stop when:

- dataset count reaches the lower bound (e.g., the target route requests at least 50 records or a route-specific threshold)
- average teacher score across the latest batch clears the planned threshold (e.g., at least 0.7)
- the dataset covers diverse failure modes or input variants defined in the probe plan
- at least one alternate teacher role has been evaluated (switch roles when scores stagnate or new errors appear)
- no single probe family dominates the records unless the capability requires it

If any gate is unmet, continue looping with fresh probes; if the teacher cannot map responses into dataset records with artifacts, record the blocker in `open_questions` and pause for user confirmation.

When the teacher's confidence on a particular review is low (e.g., the domain is ambiguous, the rubric is unclear, or the teacher cannot determine correctness), mark the record with `confidence: low` and exclude it from the training dataset. Prefer abstaining over emitting noisy labels. If low-confidence reviews exceed half the batch, pause the loop and ask the user for clarification or a refined rubric before continuing.
