# Code Playbook

Use this reference when the requested capability concerns code generation, code repair, repository-grounded assistance, execution-aware reasoning, or tool-augmented programming behavior.

## Goal

Route coding requests by evaluator strength, repository grounding needs, tool dependencies, and supervision shape before recommending optimization.

## Start With Decomposition

Break the request into:

- code synthesis
- code editing or repair
- repository grounding
- execution and test compliance
- tool use such as search, build, or test commands
- planning across multiple files

Do not reduce all coding work to one benchmark or one training recipe.

## Evaluation Targets and Modes

Evaluate coding requests at the narrowest layer that still matches deployment reality.

Common targets:

- single-function synthesis
- patch generation
- bug fixing
- repository-grounded editing
- test repair
- tool-assisted coding
- multi-file planning and execution

Prefer the strongest available signal:

- unit tests
- compile checks
- lint or type checks
- schema or diff validators
- repository-grounded review
- human review only when stronger signals are unavailable

If public benchmarks are used, check language fit, framework fit, repository similarity, tool dependency mismatch, and contamination risk.

## Repository Grounding

Check whether the requested improvement depends on:

- codebase context
- local conventions
- build system behavior
- file graph awareness
- tool outputs such as tests or static analysis

If the user cares about a real codebase, include repository-grounded evaluation and artifacts that reference real files, diffs, test outputs, or tool traces.

Do not rely on public coding benchmarks alone when the actual task is repository-specific.

## Data Shapes and Teacher Roles

Useful supervision shapes include:

- instruction-response coding pairs
- critique-rewrite patch records
- chosen-rejected code candidates
- verifier outcomes from tests, compile checks, or linting
- tool-assisted repair traces
- repository-grounded issue-to-patch demonstrations

Suggested routing:

- use instruction-response or direct patch pairs when the target behavior is easy to demonstrate
- use critique-rewrite when the student already produces near-miss code
- use verifier-result data when checks are stable and the task is strongly executable
- use preference pairs when ranking candidate patches is easier than writing a full gold patch
- use trajectory traces when tool use or multi-step debugging matters

Common teacher roles:

- `diagnostician`: classify code failures and missing context
- `demonstrator`: produce patch-ready or file-aware solutions
- `critique teacher`: explain why a patch fails and how to repair it
- `preference judge`: rank candidate patches or traces
- `verifier`: own test, compile, lint, or structured validation evidence

When designing teacher prompts, keep repository context explicit, state file scope and allowed edit scope, and keep raw verifier evidence separate from corrected code.

## Routing Guidance

Prefer:

- supervised learning when good demonstrations or edits exist
- data-centric cleanup when examples are noisy or poorly grounded
- distillation when a stronger teacher consistently solves the tasks
- preference optimization when ranking candidate patches is easier than authoring gold patches
- reward-driven optimization only when tests or verifiers are stable and hard to game

Do not jump to RL because code has tests. Check whether test coverage is sufficient, whether the verifier can be gamed, and whether the student already has acceptable imitation quality.

## Gating Checks

Before scaling data generation or training, verify:

- the evaluator catches the dominant real failures
- the repository context provided to the model matches the actual task
- tool traces contain real execution evidence rather than claimed success
- test or lint checks are stable across reruns
- preference labels reflect real quality, not only stylistic bias

## Stop Rules

Stop and redesign the route when:

- the evaluator is weaker than the target task
- repository-grounded tasks are being judged only by generic benchmarks
- tests are too sparse to support reward-driven optimization
- synthetic coding data drifts away from real repository structure
- the model failure is mostly tool or controller related rather than code knowledge related

## Anti-Patterns

- using style-only rubrics for executable tasks
- treating all coding as single-file text generation
- training on patches without preserving test outcomes
- using RL from weak tests before supervised quality is credible
- blaming the base model when repository context or tooling is the real bottleneck

## Decision Rule

For coding requests:

1. define the evaluator first
2. distinguish code knowledge from tool or controller gaps
3. prefer repository-grounded evidence when the real task is local
4. use stronger methods only after direct supervised routes and verifiers are credible
