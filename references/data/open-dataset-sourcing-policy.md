# Open Dataset Sourcing Policy

Use this reference when the route depends on collecting or selecting training or evaluation data.

## Goal

Prefer reusable open data first, keep provenance visible, and avoid escalating to scraping or private data before the user has approved it.

## Source Priority

Search in this order unless the user overrides it:

1. validated local or project datasets
2. open datasets from Hugging Face
3. open datasets or curated corpora from GitHub
4. synthetic data generated through teacher loops
5. user-approved web collection
6. user-provided private or proprietary data

## Dataset Search Rules

- search for the narrowest dataset matching the target capability, language, modality, and deployment constraints
- prefer well-described open datasets over vague mirrors or reposts
- keep evaluation and training suitability separate
- record source URL or repository identifier
- record licensing uncertainty when known

## Image Data Rule

For image capability improvement:

1. search open datasets from Hugging Face first
2. then search GitHub for curated open image datasets or manifests
3. if no suitable source is found, ask the user before collecting images from the web
4. if the user does not approve web collection, ask for user-provided data or emit a bounded defer recommendation

Do not silently crawl images.

## Synthetic Data Rule

Teacher-generated data is acceptable when:

- open data is thin or mismatched
- the base model can already do the task in principle but needs tighter supervision
- the teacher outputs can be quality-gated and exported cleanly

Do not treat synthetic data as provenance-free. Record that it is synthetic and identify the teacher role or source policy.

## Data Separation Rules

Keep these categories separate:

- local/project data
- open public data
- synthetic teacher data
- user-provided private data

Preserve held-out evaluation splits and avoid leakage between training and acceptance data.

## Ask-The-User Triggers

Ask the user before:

- scraping web images or documents
- using unclear-license sources
- mixing private user data into training
- collecting broad crawls when a narrower open dataset may still be enough

## Output Expectations

When the skill finishes the sourcing step, it should be able to state:

- what sources were found
- which sources are suitable for training
- which sources are suitable for evaluation
- what quality or licensing gaps remain
- whether user approval is needed before continuing
