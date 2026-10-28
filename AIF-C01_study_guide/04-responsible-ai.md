# Domain 4 – Guidelines for Responsible AI

> Exam weight ≈ 14%. Fairness, bias, explainability/transparency, human oversight and safety guardrails.

**89 questions** in this domain. [← Back to index](README.md)

## Topics

- [Responsible AI: fairness, bias & human oversight](#responsible-ai-fairness-bias--human-oversight) (41 questions)
- [Explainability, transparency & documentation](#explainability-transparency--documentation) (26 questions)
- [Amazon Bedrock Guardrails](#amazon-bedrock-guardrails) (22 questions)

---

## Responsible AI: fairness, bias & human oversight

### Key concepts

* **AWS responsible-AI dimensions:** fairness, explainability, privacy & security, safety, controllability, veracity & robustness, governance, transparency.
* **Bias sources:** unrepresentative/imbalanced data (**sampling bias**), historical bias, measurement bias. Fix: diverse, balanced data, measure imbalance (**Clarify** pre-training metrics), augment minority classes, retrain/fine-tune with better data, fairness metrics.
* **Human-in-the-loop:** **A2I** for reviewing predictions (confidence thresholds), human review of outputs (post-processing).
* **Other risks:** IP/copyright infringement, plagiarism, hallucination in high-stakes uses, environmental impact (efficient models, **Trainium/Inferentia** instances).
* **Governance groundwork:** responsible-AI training for staff, regular reviews, cross-functional teams.

### Questions (41)

**Q9.** Minimize the environmental impact of a GenAI recommendation app  
✅ **A. Optimize the deployed model architecture to prioritize computational efficiency during model inference.**  
💡 Making inference computationally efficient (smaller/optimized model) directly cuts energy use. Running more models or more locations increases consumption.

**Q12.** Lower bias and toxicity during post-processing (after generation)  
✅ **A. Human-in-the-loop**  
💡 Human-in-the-loop review of outputs catches biased/toxic content after the model has produced it. Data augmentation, feature engineering and adversarial training act before/during training.

**Q27.** Resume screening trained on data not representative of all demographics  
✅ **A. Fairness**  
💡 Unrepresentative data leads to unequal treatment of groups, which is the fairness dimension of responsible AI.

**Q29.** Training data should reflect a diverse global user base  
✅ **A. Balance class representation in the dataset.**  
💡 Balance class/group representation so every group is adequately represented. A single-region dataset, oversampling the majority or dropping minorities makes bias worse.

**Q31.** Unbiased loan model across demographics  
✅ **D. Measure class imbalance on the training dataset. Adapt the training process accordingly.**  
💡 Measure class imbalance in the training data (e.g. SageMaker Clarify pre-training bias metrics) and adapt training (resampling, reweighting). Copying historical results repeats historical bias.

**Q41.** Small, age-imbalanced loan dataset (mostly middle-aged); age feature removed  
✅ **A. The model will inaccurately predict outcomes for younger and older age groups.**  
💡 Without the age feature and with few young/old examples, the model learns mostly middle-aged patterns and predicts poorly for younger and older applicants. Removing a feature doesn't automatically remove bias or reduce data needs.

**Q43.** Responsible, fair GenAI loan-approval output  
✅ **A. Review the training data to check for biases. Include data from all demographics in the training data.**  
💡 Check training data for bias and include all demographics. More layers doesn't add fairness, secrecy hurts transparency, and a static test set misses drift.

**Q49.** Legal risk of GenAI content based on trending social media  
✅ **A. Copyright infringement claims if the GenAI tool produces content too similar to existing training data**  
💡 Output too similar to copyrighted training data can lead to IP/copyright infringement claims. Bias is an ethical risk rather than the legal one asked about.

**Q73.** Human review of ML predictions with adjustable confidence thresholds  
✅ **B. Amazon Augmented AI (Amazon A2I)**  
💡 Amazon Augmented AI (A2I) routes low-confidence predictions to human reviewers based on thresholds you set and can tune.

**Q80.** Theft-detection model disproportionately flags one ethnic group  
✅ **B. Sampling bias**  
💡 Sampling bias: the training data doesn't represent the population fairly, so one group is over-flagged. Measurement bias = faulty measurement; observer/confirmation bias are human judgement biases.

**Q90.** Data collection practice that reduces bias in a recommender  
✅ **C. Ensure that the data is balanced and collected from a diverse group.**  
💡 Collect balanced data from a diverse group. Limiting to past buyers or a narrow demographic skews the model; public data isn't automatically unbiased.

**Q96.** Core responsible-AI dimensions for equitable hiring (choose two) *(choose two)*  
✅ **A. Fairness + E. Transparency**  
💡 Fairness (equal outcomes across groups) and transparency (being clear about how decisions are made). Tolerance, flexibility and open source aren't AWS responsible-AI dimensions.

**Q110.** Match responsible-AI principles to loan-app actions (hotspot) *(hotspot)*  
✅ **Encrypt/isolate → Privacy and security; Population impact → Fairness; Unexpected data → Robustness**  
💡 Encryption and network isolation → privacy & security. Checking impact across population groups → fairness. Testing with unexpected inputs → robustness.

**Q115.** Fine-tuned loan LLM favors one demographic; fix most cost-effectively  
✅ **A. Include more diverse training data. Fine-tune the model again by using the new data.**  
💡 Add more diverse, balanced data and fine-tune again. Pre-training a new LLM is very expensive; RAG and Trusted Advisor don't fix learned bias.

**Q120.** Customers with short credit history always flagged high risk regardless of income  
✅ **B. The training data included historical data for only customers that have a long credit history.**  
💡 The training data contained only customers with long credit histories, so the model never learned how short-history applicants behave and treats them as risky.

**Q146.** Team training needed to make AI fair and explainable  
✅ **C. Training on bias awareness and responsible AI**  
💡 Training on bias awareness and responsible AI. Coding, encryption or algorithm training don't target fairness or explainability.

**Q177.** Student copies GenAI output into essays  
✅ **C. Plagiarism**  
💡 Plagiarism: presenting AI-generated work as one's own.

**Q186.** Check a dataset for bias before training  
✅ **A. Use Amazon SageMaker Clarify to compute pre-training bias metrics.**  
💡 SageMaker Clarify pre-training bias metrics (e.g. class imbalance, DPL) analyze the data itself. Post-training metrics need a model; Model Cards only document.

**Q189.** Mechanisms to monitor and steer AI behavior  
✅ **C. Controllability**  
💡 Controllability: the ability to monitor and steer system behavior. Safety = preventing harm; explainability = understanding outputs.

**Q206.** Collect minimal data and delete training data after a retention period  
✅ **A. Privacy and security**  
💡 Data minimization and retention limits are privacy and security practices.

**Q211.** Detect bias in a loan model and explain its predictions  
✅ **A. Amazon SageMaker Clarify**  
💡 SageMaker Clarify does both bias detection (pre-/post-training) and explainability (SHAP). Data Wrangler prepares data; Model Cards and AI Service Cards document.

**Q219.** AWS-aligned responsible-AI strategy for hiring  
✅ **C. Test the AI solution to ensure that it does not discriminate against any protected groups.**  
💡 Test that the system doesn't discriminate against protected groups. Fully automated decisions, training only on past hires (historical bias) and secrecy all violate responsible AI.

**Q226.** Match responsible-AI characteristics to chatbot design actions (hotspot) *(hotspot)*  
✅ **Anonymize PII → Privacy and security; Explainable decisions → Transparency; Guardrails against harm → Safety**  
💡 Anonymizing personal data → privacy & security. Explainable decisions → transparency. Guardrails preventing harmful output/misuse → safety.

**Q235.** Increase customer confidence in an agent answering from product manuals  
✅ **B. Including referenced product manual links in the response**  
💡 Cite sources: include links to the referenced manual sections so users can verify (transparency). A self-reported confidence number isn't verifiable.

**Q250.** Ensure impartial resume screening across demographics (choose two) *(choose two)*  
✅ **B. Fairness + C. Explainability**  
💡 Fairness (equal treatment) and explainability (understanding and justifying why candidates were selected, so bias can be found).

**Q287.** Responsible data prep for fine-tuning (choose two) *(choose two)*  
✅ **A. Include demographically diverse data sources to improve model fairness. + B. Apply consistent labeling standards across the training dataset.**  
💡 Use demographically diverse sources (fairness) and consistent labeling standards (quality/reliability). Volume over quality, synthetic-only data or fewer labels reduce quality.

**Q305.** Match services to responsible-AI use cases (hotspot) *(hotspot)*  
✅ **Human feedback → Ground Truth; Safeguards → Bedrock Guardrails; Bias detection → Clarify**  
💡 Ground Truth brings human feedback into the ML lifecycle; Bedrock Guardrails apply safeguards that follow policy; Clarify detects bias during data prep and training.

**Q332.** LLM app that generates citations and checks for plagiarism  
✅ **A. Intellectual property infringement**  
💡 It mitigates intellectual property (copyright) infringement.

**Q335.** Image-generation training data is biased by certain attributes  
✅ **A. Data augmentation for imbalanced classes**  
💡 Data augmentation for under-represented classes balances the dataset. Monitoring only detects; RAG and watermarking don't fix training bias.

**Q340.** Job recommendations differ by gender for equivalent profiles  
✅ **D. Fairness**  
💡 Fairness: equivalent people should get equivalent outcomes regardless of protected attributes.

**Q367.** Some fraud predictions need human review before action  
✅ **C. Amazon Augmented AI (Amazon A2I)**  
💡 Amazon Augmented AI (A2I) creates human review workflows triggered by conditions such as low confidence.

**Q373.** EC2 instance family with the least environmental impact for LLM training  
✅ **D. Amazon EC2 Trn series**  
💡 Trn (AWS Trainium) instances are purpose-built for training with better energy efficiency. P/G = GPU; C = general compute.

**Q382.** Evaluate moderation LLM for bias with least admin effort  
✅ **D. Benchmark datasets**  
💡 Use existing benchmark datasets designed for bias/fairness evaluation (e.g. BOLD, CrowS-Pairs in FMEval). Building your own from user content or logs takes effort.

**Q390.** Make sure all demographics' food preferences are in the dataset  
✅ **B. Diversity**  
💡 Diversity (representativeness) of the dataset.

**Q428.** Responsible development of a document-processing LLM (choose two) *(choose two)*  
✅ **A. Include fairness metrics for model evaluation. + C. Modify the training data to mitigate bias.**  
💡 Evaluate with fairness metrics and modify the training data to reduce bias. Temperature, overfitting and prompting are performance topics.

**Q429.** Chatbot must not return inappropriate images  
✅ **A. Implement moderation APIs.**  
💡 Use content moderation APIs (e.g. Amazon Rekognition content moderation) to filter images before returning them.

**Q464.** Insect-bite photos from all genders, ethnicities and regions  
✅ **A. Fairness**  
💡 Fairness: the model should work equally well for everyone (diverse, representative data).

**Q474.** Legal risk of using FMs to review and negotiate contracts  
✅ **A. Providing contract analysis that is incorrect**  
💡 Incorrect contract analysis (hallucination) could cause legal and financial harm. The other options are protections or optimizations, not risks.

**Q492.** Ensure the app isn't biased toward any user group  
✅ **B. Model fairness**  
💡 Model fairness.

**Q517.** Investigate gender-stereotyped toy recommendations  
✅ **D. Amazon SageMaker Clarify**  
💡 SageMaker Clarify measures bias in data and model predictions.

**Q531.** Responsible loan-discount model that minimizes bias (choose two) *(choose two)*  
✅ **A. Detect imbalances or disparities in the data. + C. Evaluate the model's behavior so that the company can provide transparency to stakeholders.**  
💡 Detect imbalances/disparities in the data, and evaluate model behavior to give stakeholders transparency. Scheduling, latency and ROUGE ("100% accurate") don't address bias.

---

## Explainability, transparency & documentation

### Key concepts

* **SageMaker Clarify** → explain predictions (SHAP feature attributions, partial dependence plots) and detect bias.
* **SageMaker Model Cards** → document *your* model: purpose, owners, data, metrics, limitations, risks (audits, governance).
* **AWS AI Service Cards** → AWS's documentation of *its own* AI services.
* Interpretability vs performance trade-off: simpler models (linear/logistic regression, decision trees) are easier to explain; neural networks can be more accurate but are less interpretable.
* Open-source models offer visibility into architecture and code. Transparency helps find bias but never removes the need for validation.

### Questions (26)

**Q1.** Report that makes trained forecasting models transparent and explainable to stakeholders  
✅ **B. Partial dependence plots (PDPs)**  
💡 PDPs show how changing one feature moves the prediction, which non-technical readers can follow. Training code, sample data and convergence tables describe how the model was built, not why it predicts what it does.

**Q23.** Benefit of SageMaker Model Cards  
✅ **B. Standardizing information about a model’s purpose, performance, and limitations.**  
💡 Model Cards standardize documentation of a model's intended use, performance, risks and limitations, supporting governance and transparency. They don't store models or reduce compute.

**Q65.** Service that gives transparency into model decisions and documents explanations  
✅ **A. Amazon SageMaker Model Cards**  
💡 SageMaker Model Cards document purpose, training details, performance and explainability information. Rekognition, Comprehend and Lex are AI services, not governance tools.

**Q66.** Make a customized diagnostic FM transparent and explainable for regulators  
✅ **B. Generate simple metrics, reports, and examples by using Amazon SageMaker Clarify.**  
💡 SageMaker Clarify produces explainability reports (feature attributions/SHAP) and bias metrics. Inspector scans for vulnerabilities; Macie discovers PII.

**Q117.** Make a credit-limit model's decisions transparent to customers  
✅ **B. Apply explainable AI techniques to show customers which factors influenced the model’s decision.**  
💡 Explainable-AI techniques (e.g. feature attributions with SHAP / SageMaker Clarify) show which factors drove each decision. Higher accuracy doesn't remove the need for transparency.

**Q159.** Neural net replaces decision tree: more accurate, less explainable  
✅ **C. Higher performance for lower interpretability**  
💡 The trade-off is higher performance for lower interpretability.

**Q161.** Explain how a loan-review model makes decisions for regulators  
✅ **A. Amazon SageMaker Clarify**  
💡 SageMaker Clarify provides explainability (SHAP feature attributions) and bias reports. Model Monitor tracks drift; Rekognition and Comprehend are AI services.

**Q176.** Feature that records model details for governance and reporting  
✅ **A. Amazon SageMaker Model Cards**  
💡 SageMaker Model Cards document intended use, training data, metrics, risk ratings. Debugger inspects training; Model Monitor watches production drift.

**Q185.** Transparency advantage of open-source models  
✅ **B. Open source models provide visibility into model architecture and code implementation.**  
💡 You can inspect the architecture, code (and often weights/training details). Open source doesn't guarantee better performance, unbiased output or automatic explanations.

**Q217.** Document a loan model's decision process for audits  
✅ **B. Amazon SageMaker Model Card**  
💡 SageMaker Model Cards record intended use, data, metrics, explainability and risk details for auditors.

**Q253.** Term for understanding how a model makes predictions  
✅ **A. Model interpretability**  
💡 Model interpretability. Interoperability is about systems working together.

**Q259.** Treatment recommender must show its rationale to doctors and patients  
✅ **A. Explainability**  
💡 Explainability: users can understand why the system recommended something.

**Q270.** What SageMaker Clarify provides  
✅ **D. Identifies potential bias during data preparation**  
💡 Bias detection during data preparation (and post-training) plus explainability. RAG is Bedrock KBs; production monitoring is Model Monitor; documentation is Model Cards.

**Q279.** Make a friend-recommendation model transparent and explainable, efficiently  
✅ **B. Use Amazon SageMaker Clarify to enhance the explainability of model recommendations.**  
💡 SageMaker Clarify provides feature-attribution explanations for predictions.

**Q288.** Most explainable ML technique  
✅ **A. Linear regression**  
💡 Linear regression: each coefficient shows exactly how a feature affects the output. SVMs, RCF and neural nets are harder to interpret.

**Q302.** Document a model's purpose, owners and limitations  
✅ **D. Amazon SageMaker Model Cards**  
💡 SageMaker Model Cards. AWS AI Service Cards document AWS's own AI services, not your models.

**Q319.** Standardized documentation of model versions and development history across partners  
✅ **C. Track the model changes by using Amazon SageMaker Model Cards.**  
💡 SageMaker Model Cards provide standardized, versioned documentation of a model's lifecycle. Git tracks code, not standardized model governance info.

**Q328.** Show how input features influence a topic classifier on SageMaker  
✅ **B. SageMaker Clarify**  
💡 SageMaker Clarify feature attributions (SHAP). Feature Store stores features; Ground Truth labels data.

**Q352.** Document the business problem, data assumptions, training considerations and risks  
✅ **B. Model Cards**  
💡 SageMaker Model Cards. Registry = versions; Monitor = drift; Model Dashboard = overview of deployed models.

**Q364.** SageMaker features for transparency and explainability (choose two) *(choose two)*  
✅ **A. SageMaker Model Cards + C. SageMaker Clarity**  
💡 Model Cards (documentation) and Clarify (explanations and bias; "Clarity" in the option is a typo for Clarify). Pipelines automate; Model Monitor tracks drift; Debugger inspects training.

**Q381.** Result of more model transparency  
✅ **D. Enhanced ability to identify bias and improve model governance**  
💡 Easier to identify bias and improve governance. It never removes validation, compliance monitoring or all bias.

**Q421.** Explainability and transparency when choosing a model (choose two) *(choose two)*  
✅ **A. Model evaluation + C. AI model service cards**  
💡 Model evaluation (compare models on performance and responsible-AI metrics) and AI Service Cards (AWS documentation of intended use, limitations, design choices).

**Q427.** Give stakeholders transparency and explainability  
✅ **A. Present the model Shapley values.**  
💡 Shapley (SHAP) values show each feature's contribution to predictions. Accuracy and confusion matrices measure performance, not reasoning.

**Q485.** Factor related to explainability of AI decisions  
✅ **A. Model complexity**  
💡 Model complexity: simpler models are easier to explain.

**Q503.** Auditable documentation when sharing custom models with other teams  
✅ **C. Create Amazon SageMaker Model Cards with intended uses and training and inference details.**  
💡 SageMaker Model Cards: standardized records of intended use and training/inference details. AI Service Cards are AWS's documentation of its own services.

**Q504.** Explain model predictions to customers and stakeholders  
✅ **D. Amazon SageMaker Clarify**  
💡 SageMaker Clarify explainability reports.

---

## Amazon Bedrock Guardrails

### Key concepts

| Policy | Blocks / detects |
|---|---|
| **Content filters** | Hate, insults, sexual, violence, misconduct, **prompt attacks** (jailbreak/injection) |
| **Denied topics** | Whole subjects you define (politics, investment/legal advice) |
| **Word filters** | Specific words/phrases, profanity |
| **Sensitive information filters** | PII (block or mask), custom regex |
| **Contextual grounding check** | Hallucinations: response not grounded in the source (needs source, query, response) |
| **Automated Reasoning checks** | Validate responses against formal policy rules |

Works on inputs and outputs; usable for non-Bedrock models through the **ApplyGuardrail API**; metrics in CloudWatch. Amazon Q Business has its own application guardrails.

### Questions (22)

**Q17.** Block patient personal data in Bedrock responses and be notified of violations  
✅ **C. Use Guardrails for Amazon Bedrock to filter content. Set up Amazon CloudWatch alarms for notification of policy violations.**  
💡 Guardrails for Amazon Bedrock has sensitive-information (PII) filters; its metrics in CloudWatch can drive alarms. Macie scans S3, not model output; CloudTrail logs API calls, not content.

**Q62.** Use Bedrock to stop users posting discriminatory content  
✅ **B. Block interactions related to predefined topics.**  
💡 Bedrock Guardrails can deny predefined topics and filter hate/insult content, blocking those interactions. Restricting conversations only to approved topics is too broad.

**Q78.** Prevent a compliance chatbot from hallucinating  
✅ **B. Configure Amazon Bedrock Guardrails to evaluate user inputs and model responses.**  
💡 Bedrock Guardrails evaluates inputs and responses; contextual grounding checks flag answers not supported by the source. AWS Config, Fraud Detector and Audit Manager don't touch model output.

**Q82.** Configurable safety rules for tutoring LLM apps with the least effort  
✅ **C. Amazon Bedrock Guardrails**  
💡 Bedrock Guardrails provide ready-made, configurable content filters, denied topics, word filters and PII handling. Playgrounds are for testing; Clarify measures bias; JumpStart is a model hub.

**Q148.** Stop the FM answering political questions  
✅ **A. Amazon Bedrock Guardrails**  
💡 Bedrock Guardrails denied topics block a whole subject (e.g. politics) in inputs and outputs.

**Q204.** Bedrock guardrail for politically influenced content in a newsletter  
✅ **B. Denied topics**  
💡 Denied topics block a defined subject area such as politics. Word filters match exact words; content filters cover hate/violence/sexual/insults/misconduct/prompt attacks; sensitive-info filters are for PII.

**Q218.** Block or mask sensitive data and detect hallucinations with the least overhead  
✅ **C. Use Amazon Bedrock Guardrails to implement safeguards for the application based on use cases.**  
💡 Bedrock Guardrails provides sensitive-information filters (block/mask PII) and contextual grounding checks (hallucination detection), fully managed. Lambda/EC2 evaluators are custom work.

**Q228.** Chatbot should answer only product questions, least overhead  
✅ **A. Set guardrails on the LLM prompt template.**  
💡 Put guardrails/constraints in the prompt template (or use Bedrock Guardrails denied topics). Custom classification logic is more work; temperature doesn't restrict topics.

**Q240.** Block offensive content for a model hosted on SageMaker JumpStart  
✅ **B. Amazon Bedrock Guardrails**  
💡 Bedrock Guardrails can also protect models outside Bedrock through the ApplyGuardrail API. CloudWatch, Inspector and Config don't filter content.

**Q254.** Prevent hate, insults, sexual content and violence in a Bedrock assistant  
✅ **C. Configure Guardrails for Amazon Bedrock to filter harmful content.**  
💡 Bedrock Guardrails content filters cover exactly these categories (plus misconduct and prompt attacks), with configurable strength.

**Q299.** Redact PII from Bedrock summaries  
✅ **B. Sensitive information filters**  
💡 Guardrails sensitive-information filters detect PII and can mask or block it. Contextual grounding detects hallucinations; automated reasoning checks validate facts against policies.

**Q320.** Filter harmful content and block PII in a Bedrock assistant with the least overhead  
✅ **B. Amazon Bedrock Guardrails**  
💡 Bedrock Guardrails: content filters + sensitive-information filters, in one managed feature.

**Q329.** Content categories Bedrock Guardrails content filters cover (choose two) *(choose two)*  
✅ **A. Hate + C. Violence**  
💡 Built-in content filter categories: hate, insults, sexual, violence, misconduct, prompt attack. Politics, gambling and religion would need custom denied topics.

**Q330.** Agent must not disclose PII  
✅ **A. Amazon Bedrock Guardrails**  
💡 Bedrock Guardrails sensitive-information filters (block or mask PII). Flows chain steps; Knowledge Bases retrieve; Data Automation extracts content from documents/media.

**Q345.** Chatbot vulnerable to prompt injection; least-effort protection  
✅ **B. Use Amazon Bedrock Guardrails content filters and denied topics.**  
💡 Bedrock Guardrails content filters (including the prompt-attack filter) and denied topics. Fine-tuning or switching models takes more work; CoT doesn't secure anything.

**Q372.** Enforce compliance rules on every response before delivery  
✅ **C. Amazon Bedrock Guardrails Automated Reasoning policy checks**  
💡 Guardrails Automated Reasoning checks validate responses against formal policy rules mathematically. Chunking, judge scoring and flow aliases don't enforce rules at runtime.

**Q395.** Responsible AI for a GenAI app answering patients' medical questions  
✅ **A. Guardrails for Amazon Bedrock**  
💡 Guardrails for Amazon Bedrock enforce safety policies on inputs and outputs. Inspector, Rekognition and Trusted Advisor don't govern GenAI output.

**Q426.** Guardrail policy to stop users bypassing safety features  
✅ **C. Prompt attacks**  
💡 The prompt attacks filter detects jailbreaks and prompt injection. Denied topics block subjects; grounding checks hallucinations; sensitive-info filters handle PII.

**Q478.** Match Bedrock Guardrails policies to mitigation actions (hotspot) *(hotspot)*  
✅ **Hate/insults/violence → Content filters; Investment/legal advice → Denied topics; Specific terms → Word filters; Ungrounded info → Contextual grounding check**  
💡 Harm categories → content filters; whole subjects like investment/legal advice → denied topics; specific offensive terms → word filters; unsupported claims → contextual grounding check.

**Q480.** Children's story app must keep content and topics age-appropriate  
✅ **C. Guardrails for Amazon Bedrock**  
💡 Guardrails for Amazon Bedrock (content filters, denied topics, word filters).

**Q524.** Filter harmful content in chatbot prompts and responses  
✅ **A. Amazon Bedrock Guardrails**  
💡 Amazon Bedrock Guardrails.

**Q528.** Three inputs to a Bedrock contextual grounding check  
✅ **A. User query, model response, and grounding source**  
💡 The grounding source, the user query and the model response. The check scores grounding (is the response supported by the source?) and relevance (does it answer the query?).
