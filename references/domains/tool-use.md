# Tool Use and Agent Playbook

Use this reference when the requested capability depends on function calling, tool selection, browser or executor control, multi-step action planning, or broader agent-style behavior.

## Goal

Distinguish model-side tool-use weaknesses from controller, runtime, or environment gaps, then design evaluators and supervision that preserve real execution evidence.

## Start With Decomposition

Break the request into:

- tool selection
- schema understanding
- argument construction
- execution control
- observation handling
- retry and recovery behavior
- multi-step planning
- final answer synthesis

Do not treat "use tools better" as one undifferentiated skill.

## Controller vs Model Diagnosis

Before choosing a training route, decide whether the main failure is:

- bad tool choice
- malformed tool call
- missing or ambiguous schema
- controller state bug
- missing observation feedback
- execution environment instability
- bad final synthesis after good tool use

If the dominant failure is outside the model, prefer controller or environment fixes first.

## Evaluation Targets and Modes

Evaluate tool and agent behavior at the right granularity:

- tool selection
- schema compliance
- argument construction
- action sequencing
- observation use
- retry and recovery behavior
- final answer grounding
- claimed versus observed execution success

Useful evaluation modes include:

- schema-validity checks
- argument-level validation
- action trace review
- environment-state verification
- browser or executor success checks
- final-answer grounding against observed outputs
- human review for edge cases not covered by verifiers

For browser or executor tasks, prefer environment-backed verification over self-reported success.

## Trace Design and Data Shapes

Useful supervision shapes include:

- direct tool-call demonstrations
- trajectory traces with observations
- critique-rewrite over malformed calls
- verifier outcomes on schema and execution validity
- chosen-rejected trajectories
- process-step labels for action planning and recovery

When capturing trajectories:

- preserve tool inputs, tool outputs, and observed state transitions
- keep timestamps or ordering clear when latency or retries matter
- distinguish planned actions from executed actions
- distinguish observed tool failure from model hallucination
- keep final-answer synthesis linked to the actual observations

When exporting traces, record whether schema enforcement happened, whether tool execution actually occurred, and whether retries or fallbacks were used.

## Teacher and Verifier Roles

Common roles:

- `diagnostician`: separate model mistakes from controller mistakes
- `demonstrator`: emit valid tool traces or browser trajectories
- `critique teacher`: explain malformed calls, missing observations, or weak recovery behavior
- `preference judge`: rank trajectories or alternative tool sequences
- `verifier`: own schema checks, execution checks, and final-answer grounding
- `process-reward teacher`: label step quality when order and observation use matter

Use verifier and critique roles together when the student produces near-miss traces.

## Routing Guidance

Prefer:

- prompt, control, and controller fixes when the model almost succeeds but formatting or handoff is weak
- supervised learning when clean tool-call traces exist
- critique-rewrite training when the model makes near-miss calls
- preference optimization when ranking trajectories is easier than writing perfect ones
- reward-driven optimization only when trajectory and execution verifiers are reliable

When the request involves browser or environment actions, treat the system as a composed agent pipeline and evaluate state transitions, not only text outputs.

## Gating Checks

Before scaling training or reward loops, verify:

- schema validation catches malformed calls reliably
- execution success is measured from the environment, not from model claims
- trajectory traces include enough observation state for diagnosis
- controller instrumentation is stable across repeated runs
- hallucinated tool success is visible in the evaluator outputs

## Stop Rules

Stop and redesign the route when:

- the evaluator cannot distinguish valid calls from claimed calls
- controller bugs dominate the observed failures
- browser or executor state is too unstable for reproducible traces
- trajectory logs omit critical observations
- the route is drifting toward RL before trace quality and verifier quality are stable

## Anti-Patterns

- training on claimed tool success instead of observed tool success
- using final-answer grading alone when the action trace is the real failure
- blaming the model for schema ambiguity owned by the controller
- collapsing browser navigation into plain text completion
- using preference or RL methods before trajectory instrumentation is trustworthy

## Decision Rule

For tool and agent requests:

1. diagnose controller versus model responsibility first
2. keep schema and execution evidence explicit
3. use trajectory supervision when step order matters
4. prefer controller or system fixes before expensive optimization when the bottleneck is outside the model
