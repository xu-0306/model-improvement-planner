# Finetuning Method Taxonomy

Use this reference when the teacher must identify which post-training or finetuning family fits the capability gap.

## Goal

Recognize the optimization family before designing questions, labels, verifiers, or training scripts.

## Method Families

### Continued Pretraining

What it is:

- additional next-token training on unlabeled domain or task-adjacent corpora before downstream tuning

Choose it when:

- the model lacks domain vocabulary, corpus style, factual coverage, or context patterns
- small amounts of SFT are not enough because the base model is far from the target distribution

Prerequisites:

- enough clean unlabeled data
- deduplication, contamination checks, and licensing review

Common failure modes:

- catastrophic forgetting
- overfitting to narrow domain style
- leaking benchmark or task answers into the corpus

Representative sources:

- Gururangan et al., *Don't Stop Pretraining* (2020): https://aclanthology.org/2020.acl-main.740/

### Supervised Finetuning

What it is:

- direct supervised learning on input-output demonstrations

Choose it when:

- desired behavior is easy to demonstrate directly
- the main gap is task behavior, formatting, tool use, or response policy

Prerequisites:

- high-quality demonstrations
- consistent labeling policy

Common failure modes:

- stylistic overfitting
- noisy labels becoming hard constraints
- verbose answers that look aligned but are not more correct

Representative sources:

- Ouyang et al., *Training Language Models to Follow Instructions with Human Feedback* (2022): https://arxiv.org/abs/2203.02155
- Zhou et al., *LIMA* (2023): https://arxiv.org/abs/2305.11206

### Instruction Tuning

What it is:

- a generalizing form of SFT built around instruction-response records across many tasks

Choose it when:

- the teacher must act as a broad assistant or data generator
- the target is multi-task instruction following rather than one narrow behavior

Prerequisites:

- broad task coverage
- mixture control, filtering, and deduplication

Common failure modes:

- mixture imbalance
- repetitive templates
- synthetic data drift

Representative sources:

- Wei et al., *Finetuned Language Models Are Zero-Shot Learners* (2021): https://arxiv.org/abs/2109.01652
- Chung et al., *Scaling Instruction-Finetuned Language Models* (2022): https://arxiv.org/abs/2210.11416
- Wang et al., *Self-Instruct* (2023): https://aclanthology.org/2023.acl-long.754/

### Distillation

What it is:

- transferring behavior from a stronger teacher into a smaller or cheaper student

Choose it when:

- deployment requires a smaller or faster model
- a strong teacher already exists
- answer traces, rationales, or soft targets are available

Prerequisites:

- reliable teacher quality
- prompts aligned with deployment distribution
- filtering for bad teacher outputs

Common failure modes:

- student copies teacher style instead of capability
- teacher mistakes are amplified
- rationale traces exceed student capacity

Representative sources:

- Hsieh et al., *Distilling Step-by-Step!* (2023): https://aclanthology.org/2023.findings-acl.507/
- Gu et al., *MiniLLM* (2023): https://arxiv.org/abs/2306.08543

### Parameter-Efficient Finetuning

Use PEFT when the objective is already chosen but memory, storage, or deployment constraints make full finetuning unattractive.

#### Adapters

What it is:

- small trainable modules inserted into the network while the base model stays frozen

Choose it when:

- modular task isolation or multi-task reuse matters

Prerequisites:

- runtime support for adapter modules

Common failure modes:

- extra inference overhead
- limited capacity relative to stronger PEFT variants

Representative sources:

- Houlsby et al., *Parameter-Efficient Transfer Learning for NLP* (2019): https://proceedings.mlr.press/v97/houlsby19a.html
- Zhang et al., *LLaMA-Adapter* (2023): https://arxiv.org/abs/2303.16199

#### Prefix Tuning And Prompt Tuning

What it is:

- learned continuous prompts or prefixes with frozen model weights

Choose it when:

- task adaptation must stay extremely lightweight
- prompt-like control is desirable

Prerequisites:

- stable prompt/prefix support in the runtime

Common failure modes:

- weak performance on smaller models
- sensitivity to prompt length and initialization

Representative sources:

- Li and Liang, *Prefix-Tuning* (2021): https://aclanthology.org/2021.acl-long.353/
- Lester et al., *The Power of Scale for Parameter-Efficient Prompt Tuning* (2021): https://aclanthology.org/2021.emnlp-main.243/

#### BitFit

What it is:

- tuning only bias parameters

Choose it when:

- you need an ultra-light baseline

Prerequisites:

- very limited update budget

Common failure modes:

- insufficient capacity for complex generation or alignment shifts

Representative source:

- Zaken et al., *BitFit* (2021): https://arxiv.org/abs/2106.10199

#### IA3

What it is:

- learned activation scaling rather than full low-rank updates

Choose it when:

- you want lighter-weight adaptation than LoRA with more capacity than BitFit

Prerequisites:

- support for target-module scaling

Common failure modes:

- module-selection sensitivity
- weaker default ecosystem than LoRA

Representative source:

- Liu et al., *Few-Shot Parameter-Efficient Fine-Tuning is Better and Cheaper than In-Context Learning* (2022): https://arxiv.org/abs/2205.05638

#### LoRA Family

What it is:

- low-rank weight updates on a frozen base model

Choose it when:

- you need a strong general PEFT baseline

Prerequisites:

- compatible training and serving stack
- target-module choice

Common failure modes:

- poor rank or target-module choices
- assuming PEFT fixes a bad objective or weak data

Representative sources:

- Hu et al., *LoRA* (2022): https://openreview.net/forum?id=nZeVKeeFYf9
- Dettmers et al., *QLoRA* (2023): https://arxiv.org/abs/2305.14314
- Zhang et al., *AdaLoRA* (2023): https://arxiv.org/abs/2303.10512
- Liu et al., *DoRA* (2024): https://arxiv.org/abs/2402.09353
- Meng et al., *PiSSA* (2024): https://arxiv.org/abs/2404.02948

### Preference Optimization

Use this family when relative quality judgments are easier to obtain than gold answers.

#### PPO / RLHF

What it is:

- reward-model-based optimization with explicit online policy updates

Choose it when:

- you need explicit reward modeling
- reranking, exploration, or longer-horizon credit assignment matters

Prerequisites:

- reward data
- stable SFT starting point
- observability for reward failures

Common failure modes:

- reward hacking
- unstable optimization
- KL drift

Representative sources:

- Stiennon et al., *Learning to Summarize from Human Feedback* (2020): https://arxiv.org/abs/2009.01325
- Ouyang et al., *Training Language Models to Follow Instructions with Human Feedback* (2022): https://arxiv.org/abs/2203.02155

#### Direct Preference Methods

What it is:

- offline optimization on relative preference data without a full RL loop

Choose it when:

- pairwise or binary preference data exists
- a simpler baseline than PPO/RLHF is preferred

Prerequisites:

- chosen/rejected or acceptable/unacceptable data

Common failure modes:

- label noise
- weak data support outside the training distribution
- length or style bias

Representative sources:

- Rafailov et al., *Direct Preference Optimization* (2023): https://arxiv.org/abs/2305.18290
- Gheshlaghi Azar et al., *A General Theoretical Paradigm to Understand Learning from Human Preferences* (2024): https://arxiv.org/abs/2310.12036
- Hong et al., *ORPO* (2024): https://arxiv.org/abs/2403.07691
- Ethayarajh et al., *Model Alignment as Prospect Theoretic Optimization* (2024): https://arxiv.org/abs/2402.01306
- Meng et al., *SimPO* (2024): https://arxiv.org/abs/2405.14734
- Calandriello et al., *Online Direct Preference Optimization* (2024): https://arxiv.org/abs/2403.08635

### Reasoning RL And Verifier-Guided Post-Training

Use this family when success can be scored by a verifier or reward source and the target capability depends on search, planning, or reasoning quality.

#### Outcome-Level RL

What it is:

- policy optimization against final-answer reward or verifier outcomes

Choose it when:

- the task is verifiable
- final correctness is cheap enough to score at scale

Prerequisites:

- reliable verifier
- monitoring for length and reward bias

Common failure modes:

- reward hacking
- overlong answers
- poor transfer when the base model is weak

Representative sources:

- Shao et al., *DeepSeekMath* (2024): https://arxiv.org/abs/2402.03300
- Open-Reasoner-Zero (2025): https://arxiv.org/abs/2503.24290

#### GRPO-Family Methods

What it is:

- group-based policy optimization variants that compare multiple samples per task

Choose it when:

- the task has a strong verifier
- group sampling is operationally feasible

Prerequisites:

- stable sampling pipeline
- reward-quality audits

Common failure modes:

- length bias
- gains that mostly come from filtering rather than the objective
- instability from poor group design

Representative sources:

- Guo et al., *DeepSeek-R1* (2025): https://arxiv.org/abs/2501.12948
- *Understanding R1-Zero-Like Training* / Dr.GRPO (2025): https://arxiv.org/abs/2503.20783
- *DAPO* (2025): https://arxiv.org/abs/2503.14476
- *Group Sequence Policy Optimization* (2025): https://arxiv.org/abs/2507.18071
- *A Minimalist Approach to LLM Reasoning: from Rejection Sampling to Reinforce* (2025): https://arxiv.org/abs/2504.11343

#### Process Supervision And Process Rewards

What it is:

- scoring or labeling intermediate reasoning steps instead of only final answers

Choose it when:

- final-answer reward is too sparse
- step quality matters
- lucky guesses hide bad reasoning

Prerequisites:

- inspectable intermediate steps
- stable step-label or implicit-reward contract

Common failure modes:

- over-rewarding verbosity
- judge bias at step level
- forcing one valid strategy too narrowly

Representative sources:

- Lightman et al., *Let's Verify Step by Step* (2023): https://arxiv.org/abs/2305.20050
- Wang et al., *Math-Shepherd* (2023/2024): https://arxiv.org/abs/2312.08935
- *PRIME* (2025): https://arxiv.org/abs/2502.01456

## Routing Reminder

- Choose the objective family first.
- Choose the supervision shape second.
- Choose full finetuning versus PEFT third.
- Choose distillation when deployment constraints dominate and a stronger teacher already exists.

Do not collapse everything into `SFT`, `DPO`, `GRPO`, or `LoRA` by default.
