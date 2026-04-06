# Dynamic Script Generation

Use this reference when the skill should generate project-local scripts instead of pretending bundled scripts already cover the current environment.

## Goal

Generate the minimum project-local execution surface needed for the chosen route while keeping the skill package itself generic.

## Preconditions

Do not generate project-local scripts until all of these are true:

- the capability route is justified
- the current environment has been inspected
- required inputs and outputs are known at a bounded level
- the needed tools or runtimes are either available now or explicitly missing

If any of those remain route-critical unknowns, emit scaffold-only scripts or stop with a bounded recommendation.

## What Should Be Generated

Prefer small, single-purpose scripts such as:

- source collection
- dataset generation
- dataset curation
- evaluation execution
- training launch wrapper
- runtime wrapper

Do not generate one giant orchestration script unless the environment already has a clear single-entry workflow.

## Script Readiness Levels

### `scaffold_only`

Use when:

- the route is selected but one or more execution details remain unresolved
- downstream commands depend on user approval or missing credentials
- the current environment does not yet prove a runnable path

Expected behavior:

- prints intent, inputs, and unresolved gaps
- does not claim runnable correctness

### `runnable_bounded`

Use when:

- the next step has concrete inputs, outputs, and available tools
- the script can be locally validated without pretending the whole project is complete

Expected behavior:

- accepts explicit arguments
- writes bounded outputs
- exposes a validation command

## Required Script Header Information

Every generated script should declare or imply:

- purpose
- required inputs
- expected outputs
- required runtimes or tools
- validation command or acceptance check
- failure boundary

## Derivation Rules

Generate scripts from:

- discovered training surfaces
- discovered serving surfaces
- discovered dataset surfaces
- discovered evaluation surfaces
- route family
- supervision shape
- current tool inventory

Do not derive scripts from abstract method names alone.

## Export Rules

The generated plan should record for each script:

- script id
- path
- script kind
- purpose
- inputs
- outputs
- readiness level
- required tools
- validation command
- unresolved preconditions

If the current `generated_script_plan` contract is missing fields needed for this, extend the contract before claiming readiness.

## Typical Flow

1. choose route
2. inspect environment and tool inventory
3. determine next bounded step
4. generate the smallest script set needed for that step
5. validate or dry-run the generated output
6. only then expose the script as the next execution artifact

## Anti-Patterns

- generating scripts before route selection
- generating scripts that assume hidden tools or credentials
- generating scripts inside the skill package instead of the project-local artifact path
- treating generated placeholders as runnable commands
- generating training launchers before dataset and evaluation surfaces are sufficiently clear
