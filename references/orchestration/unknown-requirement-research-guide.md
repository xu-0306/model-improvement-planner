# Unknown Requirement Research Guide

Use this reference when a request does not match any current routing or domain playbook. Do not force-fit it into a familiar method; treat the unknown as a discovery problem.

## Recognize Unknown Requirements

1. Confirm that the request does not align with existing routing documents or domain playbooks.
2. Declare explicitly that the bundled references do not cover this scenario before proceeding.
3. Enter the research flow rather than guessing a method; log the uncertainty in `research_evidence` or `tool_inventory`.

## Decompose the Request

Break the unknown need into stable axes:

- Input modality (text, image, audio, tool state, etc.)
- Output modality (text, code, structured data, tool call, etc.)
- Capability nature (knowledge, reasoning, localization, etc.)
- Required sub-capabilities (tool chaining, multimodal grounding, safety)
- Architecture impact (does the base model itself need change?)
- Tool/system dependencies (external services, runtime adapters, API access)

Use this decomposition to identify which facets require evidence before route selection.

## Research Strategy

Follow these ordered steps, recording source, rationale, and route impact for each:

1. `grep`/search bundled references for partial coverage before calling any external tool.
2. Search the current workspace (model cards, docs, configs) for clues about the requested capability.
3. If still unresolved, query the current session's skills or MCP tools for facts or structured data.
4. Use `search_web` or equivalent browsing against official documentation (model cards, framework docs, release notes) that speaks directly to the capability or stack.
5. Inspect relevant academic papers or benchmarks when official docs are absent or incomplete.
6. Review open-source implementations on Hugging Face or GitHub that mirror the desired behavior.

For every step, note: source identity, why it was necessary, and how it shifts the route choice.

## From Research to Execution

1. Design a bounded solution (training plan, system composition, runtime adaptation, etc.) supported by the confirmed facts.
2. Emit project-local scripts or artifacts only when the research justifies the path and the environment can host it.
3. If uncertainty remains, output a bounded recommendation (research plan, capability decomposition, evaluation memo) instead of pretending to reach execution readiness.

Always map the research findings into `research_evidence` with `route_implications`, `unresolved_facts`, and `recommended_followups`.

## Research Stop Conditions

Stop researching and emit a bounded recommendation when:

- all six research steps have been exhausted without finding a confirmed path
- more than two critical facts remain unresolved after external search
- the research has consumed more than three distinct source types without convergence
- the user's request depends on a capability that no discovered model, tool, or system composition can plausibly provide

In these cases, output a `research_evidence` artifact with `status: insufficient_evidence`, list the unresolved facts, and ask the user for direction before continuing.

## Anti-Patterns

- Claiming "can do this" without documented evidence or research.
- Pretending the closest known route fully covers the request without verifying the gaps.
- Recommending SFT before comparing available tool or system interventions.
- Signaling execution-ready artifacts when key facts are still speculative.
