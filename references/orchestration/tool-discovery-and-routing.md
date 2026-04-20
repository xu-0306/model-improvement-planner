# Tool Discovery And Routing

Use this reference when the skill needs live facts, research, backend execution, or data collection and must decide which currently available tool surface should handle the step.

## Goal

Choose tools dynamically from the current session and workspace instead of hardcoding a fixed skill, MCP, or runtime map.

## Discovery Order

Inspect in this order:

1. bundled references in this skill
2. local workspace docs, configs, and evidence surfaces
3. current-session skills
4. current-session MCP servers, templates, and resources
5. callable local runtimes or exposed endpoints
6. external web or documentation access

Record the resulting inventory before route-critical research or execution begins.

## Core Decision Rule

For each step, ask:

1. what evidence or action is needed now
2. what tools are actually available now
3. which available tool is narrow enough to complete only that step
4. whether the result needs to be carried forward into the planning bundle

Do not start from a remembered tool name. Start from the needed evidence or action.

## Tool Selection Priorities

### Local References

Prefer first when:

- the current repo already contains routing, training, evaluation, or policy guidance
- the question is about this skill's own workflow
- the user asked for a bounded local recommendation

### Current-Session Skills

Prefer when:

- the task matches a specialized skill and that skill is visible in the current session
- the step depends on domain-specific workflow guidance, not just generic web search
- the skill reduces prompt complexity or protects correctness

Do not assume a skill exists because it existed in a previous session.

### MCP Tools And Resources

Prefer when:

- the current task needs live docs, structured external resources, or environment-specific integration surfaces
- the MCP tool returns more structured evidence than generic browsing
- the step depends on an active integration rather than a static reference

### Backend Adapters

Prefer when:

- the step is empirical probing against a local or exposed model
- the model is callable through a discoverable runtime or endpoint
- baseline evidence is needed before route selection

### External Web Research

Prefer only after local references, session skills, and MCP options are insufficient.

Use for:

- official documentation
- model cards not already present locally
- primary papers
- stack-specific compatibility research
- open dataset discovery

## Typical Routing Patterns

### Route-Critical Research

1. read bundled references
2. inspect local model card or project docs
3. use discoverable skills or MCP tools if available
4. browse official external sources only for unresolved route-critical gaps
5. record confirmed facts, unresolved facts, and route implications in the planning bundle

### Baseline Probing

1. inspect tool inventory
2. confirm callable backend
3. define a compact probe set and evaluation mode
4. execute probes with the narrowest available backend
5. carry results into the evaluation and facts sections of the plan

### Data Sourcing

1. inspect local datasets and workspace surfaces
2. search open datasets from Hugging Face or GitHub
3. if no suitable open source exists, stop and ask the user before scraping or using private data

## Recording Requirements

Whenever the skill chooses a tool, record:

- tool category
- concrete tool name or evidence surface
- why it was selected
- what step it supports
- what part of the planning bundle should capture the result

If the choice materially affects route selection, carry it into the facts, evaluation, or intervention sections of the plan.

## Anti-Patterns

- assuming a skill or MCP server exists without discovering it in the current session
- browsing the web before reading local references
- using a larger tool surface than the step requires
- converting a missing tool into a hallucinated capability claim
- continuing to route selection when the required evidence tool is unavailable and no bounded fallback exists

## Stop Conditions

See `references/orchestration/stop-and-confirmation-policy.md` for the full stop and confirmation policy.

Stop here specifically when:

- the required tool surface is unavailable and no bounded fallback exists
- the missing tool would materially change the route choice
