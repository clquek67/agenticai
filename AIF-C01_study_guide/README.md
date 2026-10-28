# AWS Certified AI Practitioner (AIF-C01) – Study Guide

All 535 practice questions from the AIF-C01 question bank, **grouped by exam domain and topic**. Each topic starts with a short summary of key concepts, followed by every question on that topic with:

- **Q#**: the question number in the original question bank, so you can look up the full wording
- a one-line summary of the scenario
- ✅ the correct answer (option letter + text; hotspot answers written out)
- 💡 why it is correct and why the usual distractors are wrong

> The question wording isn't reproduced here (the source is a copyrighted, commercial question bank). Scenarios are paraphrased and the explanations were written for this guide.

## How to study

1. Read the **Key concepts** block of a topic first; most questions are recall of those tables.
2. Go through the questions, cover the answer line, and try to answer from the one-line scenario.
3. Revisit the [cheat sheet](#last-minute-cheat-sheet) and the [questions with a disputed answer](#questions-with-a-disputed-answer) before the exam.

## Domains & topics

| Domain | Topic | Questions |
|---|---|---|
| [Domain 1 – Fundamentals of AI and ML](01-ai-ml-fundamentals.md) | [AI/ML concepts, learning types & algorithms](01-ai-ml-fundamentals.md#aiml-concepts-learning-types--algorithms) | 41 |
| [Domain 1 – Fundamentals of AI and ML](01-ai-ml-fundamentals.md) | [ML lifecycle, training & MLOps](01-ai-ml-fundamentals.md#ml-lifecycle-training--mlops) | 23 |
| [Domain 1 – Fundamentals of AI and ML](01-ai-ml-fundamentals.md) | [ML evaluation metrics](01-ai-ml-fundamentals.md#ml-evaluation-metrics) | 10 |
| [Domain 1 – Fundamentals of AI and ML](01-ai-ml-fundamentals.md) | [Data labeling & human annotation](01-ai-ml-fundamentals.md#data-labeling--human-annotation) | 4 |
| [Domain 1 – Fundamentals of AI and ML](01-ai-ml-fundamentals.md) | [Amazon SageMaker AI features](01-ai-ml-fundamentals.md#amazon-sagemaker-ai-features) | 29 |
| [Domain 1 – Fundamentals of AI and ML](01-ai-ml-fundamentals.md) | [AWS AI services (pre-trained, no ML expertise needed)](01-ai-ml-fundamentals.md#aws-ai-services-pre-trained-no-ml-expertise-needed) | 27 |
| [Domain 2 – Fundamentals of Generative AI](02-generative-ai-fundamentals.md) | [GenAI core concepts](02-generative-ai-fundamentals.md#genai-core-concepts) | 27 |
| [Domain 2 – Fundamentals of Generative AI](02-generative-ai-fundamentals.md) | [GenAI use cases & business value](02-generative-ai-fundamentals.md#genai-use-cases--business-value) | 21 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Choosing a foundation model](03-applications-of-foundation-models.md#choosing-a-foundation-model) | 11 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Inference parameters](03-applications-of-foundation-models.md#inference-parameters) | 13 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Cost & pricing](03-applications-of-foundation-models.md#cost--pricing) | 9 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Prompt engineering](03-applications-of-foundation-models.md#prompt-engineering) | 28 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [RAG, Knowledge Bases & vector stores](03-applications-of-foundation-models.md#rag-knowledge-bases--vector-stores) | 31 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Model customization](03-applications-of-foundation-models.md#model-customization) | 30 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Agents, AgentCore & MCP](03-applications-of-foundation-models.md#agents-agentcore--mcp) | 14 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Amazon Bedrock platform features](03-applications-of-foundation-models.md#amazon-bedrock-platform-features) | 15 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Bedrock model families](03-applications-of-foundation-models.md#bedrock-model-families) | 11 |
| [Domain 3 – Applications of Foundation Models](03-applications-of-foundation-models.md) | [Evaluating foundation models](03-applications-of-foundation-models.md#evaluating-foundation-models) | 28 |
| [Domain 4 – Guidelines for Responsible AI](04-responsible-ai.md) | [Responsible AI: fairness, bias & human oversight](04-responsible-ai.md#responsible-ai-fairness-bias--human-oversight) | 41 |
| [Domain 4 – Guidelines for Responsible AI](04-responsible-ai.md) | [Explainability, transparency & documentation](04-responsible-ai.md#explainability-transparency--documentation) | 26 |
| [Domain 4 – Guidelines for Responsible AI](04-responsible-ai.md) | [Amazon Bedrock Guardrails](04-responsible-ai.md#amazon-bedrock-guardrails) | 22 |
| [Domain 5 – Security, Compliance and Governance for AI](05-security-compliance-governance.md) | [Security for AI workloads](05-security-compliance-governance.md#security-for-ai-workloads) | 28 |
| [Domain 5 – Security, Compliance and Governance for AI](05-security-compliance-governance.md) | [Prompt attacks](05-security-compliance-governance.md#prompt-attacks) | 9 |
| [Domain 5 – Security, Compliance and Governance for AI](05-security-compliance-governance.md) | [Compliance, auditing & data governance](05-security-compliance-governance.md#compliance-auditing--data-governance) | 37 |
| | **Total** | **535** |

## Last-minute cheat sheet

| If the question says… | Think… |
|---|---|
| Ground answers in company docs / data changes often / reduce hallucination cheaply | **RAG → Bedrock Knowledge Bases** |
| Change tone/style/task behavior with labeled examples | **Fine-tuning** (JSONL prompt-completion pairs) |
| Teach domain knowledge from unlabeled documents | **Continued pre-training** |
| Least effort / lowest cost customization | **Prompt engineering** |
| Multi-step task that calls APIs | **Bedrock Agents** (hosting any framework → **AgentCore**) |
| Live data from external tools | **MCP** / agent action groups |
| Block harmful content, PII, topics, hallucination | **Bedrock Guardrails** |
| More creative ↔ more consistent output | **Temperature ↑ / ↓** |
| Summarization metric / translation metric / semantic similarity | **ROUGE / BLEU / BERTScore** |
| Imbalanced classification metric | **F1** (few false alarms → precision; few misses → recall) |
| Bias detection + explainability | **SageMaker Clarify** |
| Production drift alerts | **SageMaker Model Monitor** |
| Document a model for auditors | **SageMaker Model Cards** |
| Human review of low-confidence predictions | **Amazon A2I** |
| Label training data (managed workforce) | **Ground Truth (Plus)** |
| No-code ML | **SageMaker Canvas** |
| Pre-trained models + templates to deploy/fine-tune | **SageMaker JumpStart** |
| Traffic must not cross the internet | **AWS PrivateLink** |
| Who called which API | **CloudTrail** · metrics/alarms → **CloudWatch** · config compliance → **Config** |
| Evidence for audits mapped to frameworks | **Audit Manager** · AWS's own compliance reports → **Artifact** |
| Find PII in S3 | **Macie** · vulnerabilities → **Inspector** · encryption keys → **KMS** |
| Custom/fine-tuned Bedrock model inference | **Provisioned Throughput** · bulk non-urgent → **Batch** · unpredictable → **On-Demand** |
| Data must stay in a country/Region | **Data residency** |

## Questions with a disputed answer

For these questions the explanation questions or adds context to the source's answer key (marked ⚠ in the topic files). The guide keeps the source's answer, but read the note:

- [Q109](01-ai-ml-fundamentals.md) – Find harmful language in comments without labeled training data
- [Q190](03-applications-of-foundation-models.md) – Bedrock agents lack context and don't reach external services for bookings
- [Q280](03-applications-of-foundation-models.md) – Metric used for summarization FMs
- [Q397](03-applications-of-foundation-models.md) – Reduce hallucinations
- [Q418](05-security-compliance-governance.md) – Report Comprehend endpoints unused for 15+ days
- [Q436](05-security-compliance-governance.md) – Prompting technique to protect against prompt injection
- [Q527](03-applications-of-foundation-models.md) – Generate responses based on company data
