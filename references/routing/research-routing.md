# Research Routing

Use this reference when the request depends on unstable, stack-specific, poorly evidenced, or novel facts that do not fit existing playbooks cleanly.

## Goal

Gather the minimum external evidence needed to avoid bad method selection, especially when the request is novel enough that the nearest familiar template may be misleading.

## Novel-Request Rule

When the request does not fit existing playbooks cleanly:

1. do not force it into a known task label immediately
2. decompose the request into inputs, outputs, sub-capabilities, dependencies, and evaluation signals
3. test whether the current base model can plausibly support the target in principle
4. if architectural fit is doubtful, compare system composition, architecture adaptation, and model replacement before training
5. research official docs, model cards, papers, and stack docs before naming a route
6. emit a bounded output if the route is still uncertain

## Research Is Mandatory When

- the request depends on a specific model family, runtime, library, or framework
- the request concerns current best practices
- the task depends on multimodal, speech, browser, or tool ecosystems
- local references do not clearly cover the request
- runtime or training feasibility is uncertain
- the request is novel enough that the correct route family is unclear

## Source Priority

1. official documentation
2. model cards
3. primary research papers
4. maintainer-authored repositories
5. benchmark documentation
6. secondary summaries only as fallback

## Capture These Outputs

- confirmed facts
- unresolved facts
- source list
- implications for route selection
- unsupported assumptions

When certainty stays low, emit one of:

- research plan
- capability decomposition memo
- evaluation design plan
- feasibility memo
- system-composition recommendation
- model-replacement recommendation

## Research Boundaries

- do not replace missing evidence with intuition
- do not cite popularity as proof of compatibility
- do not assume the user's named method is current best practice
- do not continue to execution when the missing evidence would change the route materially
- do not force a new problem into SFT because demonstrations seem easy to imagine
- do not force a text-only model into speech or vision work without architecture evidence
- do not present an unresearched route as implementation-ready
