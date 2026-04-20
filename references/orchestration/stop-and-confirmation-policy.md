# Stop And Confirmation Policy

Use this reference when deciding whether the skill should continue autonomously, stop with a bounded recommendation, or ask the user for confirmation.

## Goal

Keep the skill autonomous for low-risk local work while preventing silent escalation into costly, irreversible, or user-sensitive actions.

## Safe To Continue Without Asking

The skill may continue autonomously for:

- reading bundled references
- inspecting the local model directory
- inspecting the workspace
- drafting capability briefs and evaluation plans
- planning probes
- searching for existing local datasets
- searching for open datasets from clearly open sources such as Hugging Face or GitHub

## Must Ask The User First

Ask before:

- scraping images or broad web corpora
- relying on user-private or proprietary data not yet provided
- starting long-running or expensive training
- using unclear-license data
- taking destructive or irreversible actions
- adopting a system-composition route that depends on new external services the user has not approved

## Must Stop And Emit A Bounded Recommendation

Stop instead of asking for a speculative yes/no when:

- architecture fit is still unresolved
- route-critical research is incomplete
- the correct next step is still unclear between training, system composition, and model replacement
- no trustworthy evaluator exists for the claimed optimization route
- the currently available tools cannot gather the evidence needed to proceed safely

Emit:

- missing facts
- why they matter
- the narrowest safe next step
- what user input or environment change would unblock progress

## Confirmation Style

When asking the user:

- state exactly what action requires approval
- state why current open sources are insufficient
- state the safer alternatives
- ask only for the minimum decision needed to continue

Example shape:

```text
Open datasets from Hugging Face and GitHub did not cover the target image domain well enough.
The next possible step is collecting images from the web.
Do you want to allow web image collection, or would you prefer to provide a dataset directly?
```

## Anti-Patterns

- silently scraping the web because open datasets were thin
- turning user silence into approval
- asking the user to choose a route before baseline evidence exists
- continuing to training because the remaining gap feels small
