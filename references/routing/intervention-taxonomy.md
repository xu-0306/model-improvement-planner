# Intervention Taxonomy

Use this reference to choose intervention families before naming specific implementation methods.

## Goal

Route by problem type, evidence, and feasibility rather than by a short list of familiar methods.

## Intervention Families

### Prompt and Control

- prompt redesign
- structured prompting
- decomposition
- reranking
- rejection sampling
- response constraints

### Retrieval and External Knowledge

- retrieval-augmented generation
- search augmentation
- memory systems
- context construction

### Data-Centric

- cleaning
- filtering
- relabeling
- synthetic data generation
- critique-rewrite generation
- hard-negative mining
- curriculum design

### Pretraining and Adaptation

- continued pretraining
- domain adaptation
- language adaptation
- tokenizer adaptation planning
- multimodal adaptation where architecture supports it

### Supervised Learning

- narrow-task SFT
- instruction tuning
- editor-style finetuning
- tool-trace finetuning
- critique-conditioned finetuning

### Distillation

- response distillation
- rationale distillation
- trajectory distillation
- policy distillation
- logit or soft-target distillation

### Preference Optimization

- DPO-family methods
- IPO-family methods
- ORPO-family methods
- KTO-family methods
- SimPO-family methods

### Reward-Driven Optimization

- PPO / RLHF
- RLAIF
- verifier-guided RL
- process-reward optimization
- GRPO-family methods

### Runtime and Serving

- runtime adaptation
- loader work
- tokenizer compatibility work
- quantization planning
- serving optimization

### System Composition

- external ASR + LLM + TTS
- browser controller + LLM + verifier
- tool router + executor + model
- multimodal subsystem composition

### Model Replacement

- stronger base model
- domain-specialized model
- multimodal-native model
- coding-specialized model

### Explicit Deferral

- research plan
- feasibility memo
- infrastructure enablement plan

## Rule

Choose the family first. Choose the specific method second. Choose the PEFT mechanism last.
