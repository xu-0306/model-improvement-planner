# Evaluation-First Workflow

Use this reference before generating training data or recommending optimization.

## Goal

Define how progress will be measured before choosing data or methods.

## Required Evaluation Decisions

Choose:

- baseline probes
- held-out evaluation
- regression checks
- acceptance threshold
- failure signatures

## Evaluation Forms

- benchmark-based
- rubric-based
- execution-based
- verifier-based
- human evaluation
- online evaluation

## Routing Rules

- if no credible evaluator exists, design evaluation before training
- if the evaluator is weak or easy to game, avoid reward-driven methods by default
- if execution-based checks exist, prefer them over style-only judgment
- if the task is system-level, evaluate the whole pipeline rather than only the base model

## Minimum Output

Emit:

- baseline status
- chosen evaluation path
- pass/fail threshold
- main regression risks
