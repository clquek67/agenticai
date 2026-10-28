# Domain 5 – Security, Compliance and Governance for AI

> Exam weight ≈ 14%. IAM, encryption, private networking, prompt-attack threats, logging/auditing and data governance.

**74 questions** in this domain. [← Back to index](README.md)

## Topics

- [Security for AI workloads](#security-for-ai-workloads) (28 questions)
- [Prompt attacks](#prompt-attacks) (9 questions)
- [Compliance, auditing & data governance](#compliance-auditing--data-governance) (37 questions)

---

## Security for AI workloads

### Key concepts

* **Shared responsibility:** AWS secures the cloud (infrastructure, service patching); you secure your data, IAM, encryption, network configuration.
* **IAM** least privilege: restrict which models can be invoked (policies on model ARNs), per-team service roles for data isolation.
* **AWS PrivateLink** (interface VPC endpoints): Bedrock/SageMaker traffic never crosses the public internet. S3 gateway endpoints for SageMaker data flows; SageMaker **network isolation**.
* **KMS** customer managed keys for encryption (custom model artifacts, Q Business index). **Macie** discovers PII in S3. **Inspector** scans for vulnerabilities (EC2, containers, Lambda).
* **Training data privacy:** remove/mask PII *before* training (a model can't unlearn); if confidential data was used, delete the model and retrain. Federated learning keeps data in place.
* **Generative AI Security Scoping Matrix:** consumer app → enterprise app → pre-trained model → fine-tuned model → self-trained model (most ownership).

### Questions (28)

**Q11.** App in a VPC calls Bedrock APIs and traffic must not cross the public internet  
✅ **A. Use AWS PrivateLink to establish a private connection between the Amazon VPC and Amazon Bedrock.**  
💡 AWS PrivateLink (interface VPC endpoint) keeps Bedrock traffic on the AWS network. Signing requests or encrypting traffic still uses the public endpoint.

**Q25.** Teams may only access their own customers' data in S3 for a Bedrock app  
✅ **A. Create an Amazon Bedrock custom service role for each team that has access to only the team's customer data.**  
💡 One custom Bedrock service role per team, scoped to that team's S3 data, enforces least privilege. One shared role with full S3 access, or trusting users to pass a customer name, breaks isolation.

**Q28.** Private access to Bedrock APIs without exposing data to the internet  
✅ **D. Use AWS PrivateLink to configure a private connection between the company’s VPC and Amazon Bedrock.**  
💡 PrivateLink connects the VPC to Bedrock privately. CloudFront is a CDN, Glue is ETL, Lake Formation governs data lakes.

**Q36.** Bedrock FM fails to read SSE-S3 encrypted data in S3  
✅ **A. Ensure that the role that Amazon Bedrock assumes has permission to decrypt data with the correct encryption key.**  
💡 The role Bedrock assumes needs the right S3 (and decryption) permissions. Making the bucket public is insecure; prompts can't fix permissions.

**Q39.** How to use LLMs on Bedrock securely  
✅ **A. Configure AWS Identity and Access Management (IAM) roles and policies by using least privilege access.**  
💡 IAM roles and policies with least-privilege access control who can call which models. Audit Manager, model evaluation and CloudWatch logs don't secure access.

**Q50.** Global company: GenAI-to-FM API calls must never cross the public internet  
✅ **A. AWS PrivateLink**  
💡 AWS PrivateLink provides private VPC endpoints to Bedrock. CloudFront is a CDN, CloudTrail logs calls, Amazon Q is an assistant.

**Q70.** Fine-tuned LLM must never reveal private customer data  
✅ **B. Remove personally identifiable information (PII) from the customer data before fine-tuning the LLM.**  
💡 Remove PII from the training data before fine-tuning: a model can't leak what it never learned. Guardrails only filter at runtime; encrypting the data doesn't stop the model memorizing it.

**Q71.** Restrict which Bedrock models employees can use  
✅ **A. Use AWS Identity and Access Management (IAM) policies to restrict model access.**  
💡 IAM policies can allow/deny bedrock:InvokeModel on specific model ARNs. STS only issues temporary credentials; Inspector scans for vulnerabilities.

**Q83.** How Bedrock protects privacy with third-party models  
✅ **B. User inputs and model outputs are not shared with any third-party model providers.**  
💡 Bedrock does not share prompts or outputs with model providers and doesn't use them to train base models; data stays in AWS.

**Q105.** ML technique for data compliance/privacy during training  
✅ **C. Federated learning**  
💡 Federated learning trains across separate data holders without moving the raw data, so data stays where it must for privacy/compliance.

**Q129.** Automated vulnerability scanning of EC2-based ML infrastructure  
✅ **C. Amazon Inspector**  
💡 Amazon Inspector continuously scans EC2, container images and Lambda for software vulnerabilities (CVEs) and exposure.

**Q162.** Fine-tune on Bedrock with sensitive data that must stay inside the private network  
✅ **C. Use AWS PrivateLink to connect the VPC and Amazon Bedrock.**  
💡 PrivateLink keeps traffic between the VPC and Bedrock off the internet. IAM controls who has access and KMS encrypts data, but neither keeps the network path private.

**Q178.** SageMaker Studio to Bedrock traffic must go through the company VPC  
✅ **C. Configure AWS PrivateLink endpoints for the Amazon Bedrock API endpoints in the VPC that SageMaker Studio is connected to.**  
💡 Create PrivateLink interface endpoints for Bedrock in Studio's VPC. IAM controls permissions, not the network path; Macie isn't a proxy.

**Q195.** Manage the flow of data from S3 to SageMaker Studio notebooks  
✅ **C. Configure SageMaker to use a VPC with an S3 endpoint.**  
💡 Run SageMaker in a VPC with an S3 VPC (gateway) endpoint so data moves privately and can be controlled with endpoint policies. Inspector and Macie don't control data flow; Glacier Deep Archive is cold storage.

**Q203.** Custom Bedrock model was trained on confidential data; stop responses based on it  
✅ **A. Delete the custom model. Remove the confidential data from the training dataset. Retrain the custom model.**  
💡 A model can't "unlearn" data: delete the custom model, remove the confidential data, retrain. Masking or encrypting outputs doesn't remove what the model memorized.

**Q256.** Only authorized personnel may access training data  
✅ **C. AWS Identity and Access Management (IAM)**  
💡 IAM defines who (users/roles) can access which resources (least privilege). KMS encrypts, but access is still granted through IAM/key policies.

**Q274.** Alert whenever sensitive data appears in emails uploaded to S3, least effort  
✅ **A. Configure Amazon Macie to detect sensitive information in the documents that are uploaded to Amazon S3.**  
💡 Amazon Macie automatically discovers sensitive data (PII etc.) in S3 and emits findings to EventBridge for alerts. Regexes or LLMs need development.

**Q278.** Encrypt Bedrock customization artifacts with a company-managed key  
✅ **A. AWS Key Management Service (AWS KMS)**  
💡 AWS KMS customer managed keys. Secrets Manager stores credentials; Macie and Inspector don't encrypt.

**Q283.** Give external customers secure access to a deployed model  
✅ **C. Create a secure API endpoint that customers can use.**  
💡 Expose it through a secure API endpoint (e.g. API Gateway with auth in front of the model). Sharing credentials or embedding the model is insecure.

**Q303.** Discover sensitive data in S3 datasets before sharing with partners  
✅ **B. Amazon Macie**  
💡 Amazon Macie scans S3 for PII and other sensitive data. Data Exchange is for sharing/subscribing to third-party data, not finding sensitive content.

**Q308.** Fine-tune an FM with data kept private in its source Region, cost-effectively (choose two) *(choose two)*  
✅ **B. Use the Amazon Bedrock API. + C. Use AWS PrivateLink and a VPC.**  
💡 Use the Bedrock API (managed fine-tuning inside your Region) over AWS PrivateLink from your VPC. Outposts/on-premises hosting is costly and unnecessary.

**Q311.** Secure Amazon Q Business data (choose two) *(choose two)*  
✅ **A. Enable AWS Key Management Service (AWS KMS) keys for the Amazon Q Business Enterprise index. + E. Configure AWS Identity and Access Management (IAM) for authentication.**  
💡 Encrypt the index with AWS KMS keys and use IAM (with IAM Identity Center) for authentication. Public or cross-account access weakens security; Inspector doesn't authenticate.

**Q315.** Bedrock app in a VPC with no internet access allowed  
✅ **A. AWS PrivateLink**  
💡 AWS PrivateLink interface endpoints reach Bedrock privately. An internet gateway is exactly what's prohibited.

**Q356.** Customer's responsibility when using Bedrock (shared responsibility)  
✅ **C. Securing the company's data in transit and at rest**  
💡 Customers secure their data (encryption in transit/at rest, IAM, network configuration). AWS patches and protects the Bedrock service and infrastructure.

**Q380.** Generative AI Security Scoping Matrix scope with the most security ownership  
✅ **D. Building and training a generative AI model from scratch by using specific data that a customer owns.**  
💡 Scope 5: training your own model from scratch. Scopes: 1 consumer app, 2 enterprise app, 3 pre-trained model, 4 fine-tuned model, 5 self-trained model; responsibility grows with each.

**Q383.** Run SageMaker training/inference isolated from the internet  
✅ **B. Run SageMaker training and inference by using network isolation.**  
💡 Enable network isolation on jobs/containers (plus VPC). IAM roles and encryption don't block internet access.

**Q401.** Share a dataset with a third party without exposing PII  
✅ **B. Apply data masking to the fields that contain PII in the dataset.**  
💡 Mask only the PII fields so the rest stays useful for modeling. Masking or encrypting everything makes the data useless; labeling doesn't protect data.

**Q523.** MCP security practices with the Q Developer CLI (choose two) *(choose two)*  
✅ **A. Keep MCP servers and the Amazon Q Developer CLI updated. + E. Install servers only from trusted sources.**  
💡 Keep MCP servers and the CLI updated, and install servers only from trusted sources. Plain-text secrets, auto-approving all tools and watching only successful activity are bad practices.

---

## Prompt attacks

### Key concepts

* **Prompt injection**: "ignore previous instructions…" overrides system rules. **Jailbreak**: bypass safety to produce harmful content.
* **Prompt leakage / extracting the prompt template**: exposes the hidden system prompt. **Extracting conversation history**: leaks earlier messages. **Fake completion**: pre-filled answers steer the model. **Ignoring the prompt template**.
* Defenses: Guardrails prompt-attack filter, hardened prompt templates that recognize attack patterns, adversarial testing, input validation.

### Questions (9)

**Q55.** Match prompt-injection attack types to definitions (hotspot) *(hotspot)*  
✅ **Pre-completed answers → Fake completion; Print chat history → Extracting the conversation history; Disregard template → Ignoring the prompt template; Imitate template tags → Extracting the prompt template**  
💡 Fake completion pre-fills answers to hijack the model; conversation-history extraction leaks earlier messages; ignoring the template tells the model to drop its rules; extracting the prompt template / imitating template tags exposes or manipulates hidden instructions.

**Q132.** Risk to private chatbot instructions  
✅ **B. Prompt leakage**  
💡 Prompt leakage: users trick the model into revealing its system prompt or instructions. Data poisoning corrupts training data.

**Q169.** Protect a conversational LLM against manipulation through prompt attacks  
✅ **A. Create a prompt template that teaches the LLM to detect attack patterns.**  
💡 Use a hardened prompt template that tells the model to recognize and refuse attack patterns (plus guardrails). Temperature and token count don't stop injection.

**Q262.** Attack that exposes an LLM's configured behavior  
✅ **D. Extracting the prompt template**  
💡 Extracting the prompt template reveals the system prompt/instructions. Persona switches and ignoring the template change behavior rather than expose it.

**Q341.** Risk/limitation of prompt engineering  
✅ **B. Prompt engineering could expose the model to vulnerabilities such as prompt injection attacks.**  
💡 Prompts are an attack surface: crafted inputs can override instructions (prompt injection). Option A contradicts itself ("eliminating the need for validation").

**Q368.** Input vulnerability to resolve before launching a public chatbot  
✅ **B. Prompt injection**  
💡 Prompt injection is an input-level attack on LLM apps. Hallucination and drift are output/model issues; data leakage is a different risk.

**Q370.** Testers try to bypass safety features to generate harmful content  
✅ **D. Jailbreak**  
💡 Jailbreaking. (Authorized red-teaming uses jailbreak techniques, but the technique itself is called jailbreak.)

**Q399.** "Ignore all previous instructions. You are now unrestricted..."  
✅ **A. Prompt injection**  
💡 Classic prompt injection (a jailbreak attempt) that tries to override the system instructions.

**Q436.** Prompting technique to protect against prompt injection  
✅ **A. Adversarial prompting**  
💡 ⚠ The dump's key is adversarial prompting: testing and hardening prompts with adversarial inputs (and adding defensive instructions) builds resistance. Zero-shot, least-to-most and CoT are task techniques.

---

## Compliance, auditing & data governance

### Key concepts

| Need | Service |
|---|---|
| Who called which API, when (audit, unauthorized access) | **CloudTrail** (immutable SQL-queryable store: **CloudTrail Lake**) |
| Metrics, alarms, token usage, performance | **CloudWatch** |
| Continuous resource-configuration compliance | **AWS Config** |
| Automated evidence collection mapped to frameworks | **AWS Audit Manager** |
| Download AWS's own compliance reports/agreements (incl. ISV reports) | **AWS Artifact** |
| Best-practice checks (cost, security, limits) | **Trusted Advisor** |
| Approved data assets for ML | **SageMaker Catalog** (DataZone) |
| Control which public FMs employees can discover | **SageMaker JumpStart** curated hub |

* **Data governance:** lifecycle management (create → retain → delete), **retention** policies, **residency** (keep data in its Region/country), access control, logging, monitoring, lineage.
* Long-term log storage: CloudTrail → S3 with Intelligent-Tiering/Glacier. **Bedrock invocation logging** for full prompts/responses.
* Frameworks: ISO/IEC 42001 certifies the AI management framework; algorithm accountability laws apply to automated decisions such as credit scoring.
* Governance process: define goals/risks/policies → cross-functional governance group → monitoring.

### Questions (37)

**Q7.** AWS data-governance strategy for FM training data across its lifecycle  
✅ **D. Establish data lifecycle policies, access controls, logging, and monitoring.**  
💡 Governance = lifecycle/retention policies + access control + logging + monitoring. The other options (open access, no retention, manual-only review) are anti-patterns.

**Q19.** Service that automatically collects evidence from AWS accounts and builds reports for compliance reviewers  
✅ **B. AWS Audit Manager**  
💡 AWS Audit Manager continuously gathers evidence and maps it to frameworks to produce audit-ready reports. Artifact only provides AWS's own compliance reports; Macie finds sensitive data; Inspector scans for vulnerabilities.

**Q32.** Log every Bedrock API request and keep logs securely for 5 years at the lowest cost (choose two) *(choose two)*  
✅ **A. AWS CloudTrail + D. Amazon S3 Intelligent-Tiering**  
💡 CloudTrail records API calls; deliver its logs to S3 and use S3 Intelligent-Tiering to move rarely accessed logs to cheaper tiers automatically. CloudWatch is costlier for long retention; S3 Standard is the most expensive tier.

**Q63.** Set up AI governance for GenAI document automation (choose two) *(choose two)*  
✅ **A. Set up a regular review process to check that the models' results are accurate and fair and follow company policies. + B. Provide training for all employees who work with AI tools so the employees understand company rules, data handling, and responsible AI use.**  
💡 Regular reviews of output accuracy, fairness and policy compliance, plus responsible-AI training for every employee who uses AI. Governance is the customer's job (not only the cloud provider's), needs more than developers, and must be proactive.

**Q85.** Control employee access to publicly available FMs  
✅ **C. Configure Amazon SageMaker JumpStart to restrict discoverable FMs.**  
💡 SageMaker JumpStart lets admins curate/restrict which public models are discoverable (private hub). Cost Explorer, Artifact and OpenSearch don't control model access.

**Q86.** AI strategy perspective about transparency and avoiding bias  
✅ **A. Responsible use of AI**  
💡 Responsible use of AI covers fairness, transparency and accountability (an AWS Cloud Adoption Framework for AI governance capability).

**Q97.** Highly scalable service to monitor ML system performance  
✅ **A. Amazon CloudWatch**  
💡 CloudWatch collects metrics, logs and alarms for performance monitoring. CloudTrail = API audit; Config = configuration compliance; Trusted Advisor = best-practice checks.

**Q133.** Detect unauthorized Bedrock API actions  
✅ **A. Configure AWS CloudTrail to monitor API activity.**  
💡 CloudTrail records every API call (who, what, when) for audit and detection of unauthorized activity.

**Q138.** Meet regulations for trustworthy AI management  
✅ **D. Ensure fairness, transparency, accountability, and security throughout the lifecycle of each AI solution.**  
💡 Build fairness, transparency, accountability and security into the whole AI lifecycle (cf. ISO/IEC 42001).

**Q149.** Evaluate and document regulatory compliance of Bedrock workloads  
✅ **A. AWS Audit Manager**  
💡 AWS Audit Manager collects evidence and maps it to frameworks (it includes a generative AI best-practices framework). Artifact only gives AWS's own reports; Model Cards document individual models.

**Q167.** What ISO accreditation for AI risk management (e.g. ISO/IEC 42001) means  
✅ **D. The company’s development framework is ISO certified.**  
💡 It certifies the organization's management system / development framework and processes, not each person or each AI system.

**Q179.** Order the steps to set up core AI governance (hotspot) *(hotspot)*  
✅ **Goals/risks/policies → Cross-functional group → Model monitoring**  
💡 First define goals, risks and policies; then form a cross-functional governance group to own them; then set up monitoring to enforce them over time.

**Q194.** Alert when Bedrock request/response usage passes a threshold  
✅ **A. Configure an Amazon CloudWatch alarm to notify the company if the InputTokenCount and OutputTokenCount metrics exceed the threshold.**  
💡 Bedrock publishes InputTokenCount and OutputTokenCount to CloudWatch; set an alarm on them. Latency isn't usage; an account-wide budget isn't specific to Bedrock.

**Q199.** Tamper-proof, queryable record of every API call from SageMaker, Bedrock and IAM  
✅ **C. AWS CloudTrail Lake**  
💡 AWS CloudTrail Lake stores CloudTrail events in an immutable data store you can query with SQL.

**Q207.** Allow only approved data for SageMaker training under policy  
✅ **A. Amazon SageMaker Catalog**  
💡 Amazon SageMaker Catalog (built on Amazon DataZone) governs data assets: publishing, approval and access control for datasets. Clarify = bias; Model Registry = model versions; Model Cards = documentation.

**Q247.** Track when data is created, updated and scheduled for deletion  
✅ **B. Data lifecycle management**  
💡 Data lifecycle management governs data from creation through retention to deletion. Residency = location; observability = data health; logging = access records.

**Q289.** Data residency for customer data from many countries  
✅ **A. Store and process customer data in the AWS Region where the data was originally collected.**  
💡 Store and process data in the Region where it was collected. Centralizing or copying data across Regions can break residency laws.

**Q297.** Continuously check development phases against policies and regulations (choose two) *(choose two)*  
✅ **A. AWS Audit Manager + B. AWS Config**  
💡 Audit Manager automates compliance evidence collection; AWS Config continuously evaluates resource configurations against rules. Inspector = vulnerabilities; CloudWatch = metrics; CloudTrail = API logs (an evidence source, not an assessor).

**Q301.** Download AWS compliance certifications for an auditor  
✅ **D. AWS Artifact**  
💡 AWS Artifact is the self-service portal for AWS compliance reports (SOC, ISO, PCI) and agreements. Audit Manager assesses your own compliance.

**Q304.** Credit-scoring AI expanding to a new region: which laws to review  
✅ **D. Local algorithm accountability laws**  
💡 Local algorithm accountability laws (rules on automated decision-making, fairness and transparency). Health, card-data and education laws don't fit credit scoring.

**Q312.** Reports showing adherence to international regulations for sensitive data  
✅ **B. AWS Artifact**  
💡 AWS Artifact gives AWS's compliance reports (ISO, SOC, PCI etc.) for evidence of the AWS side. Config evaluates resource settings; Macie finds PII.

**Q321.** Audit record of each practitioner's actions in the account  
✅ **A. AWS CloudTrail**  
💡 AWS CloudTrail logs who did what, when, through which API.

**Q339.** Email notifications when ISV compliance reports become available  
✅ **B. AWS Artifact**  
💡 AWS Artifact provides third-party (ISV) compliance reports and can send notifications when new reports arrive.

**Q342.** Data governance for an AI loan-approval system  
✅ **B. Implement data lifecycle management to track and manage AI training data.**  
💡 Data lifecycle management tracks how training data is collected, stored, used, retained and deleted. No audit trails, ignoring residency or synthetic-only data don't meet regulations.

**Q349.** Automate recurring compliance assessments with evidence mapped to frameworks  
✅ **A. AWS Audit Manager**  
💡 AWS Audit Manager.

**Q355.** Patient data must not leave its country  
✅ **A. Data residency**  
💡 Data residency: store and process data within a required geographic boundary (choose the Region).

**Q357.** Investigate which API calls were made, by whom and when, after a cost spike  
✅ **C. AWS CloudTrail**  
💡 CloudTrail logs every Bedrock API call with identity, time and source IP.

**Q366.** Build an AI governance foundation before rolling out GenAI  
✅ **C. Assemble a cross- functional team to develop clear policies and guidelines for AI use, oversight, and compliance.**  
💡 Assemble a cross-functional team (business, tech, legal, risk, compliance) to set policies, oversight and compliance rules first. Building first or relying only on tools/consultants skips the foundation.

**Q386.** Obtain AWS compliance documentation for regulators  
✅ **D. AWS Artifact**  
💡 AWS Artifact.

**Q407.** Characteristic of AI governance frameworks for trustworthy, human-centered AI  
✅ **D. Developing policies and guidelines for data, transparency, responsible AI, and compliance**  
💡 Policies and guidelines for data, transparency, responsible AI and compliance. The other options are business-growth goals.

**Q418.** Report Comprehend endpoints unused for 15+ days  
✅ **B. Amazon CloudWatch**  
💡 CloudWatch metrics (e.g. invocations) with alarms/reports show idle endpoints. ⚠ AWS Trusted Advisor also has a cost check for underutilized Comprehend endpoints, but the dump's key is CloudWatch.

**Q457.** Continuously check SageMaker endpoints against company policies  
✅ **C. AWS Config**  
💡 AWS Config rules continuously evaluate resource configurations (e.g. endpoint encryption, network settings). Audit Manager reports; Artifact gives AWS documents.

**Q462.** Guidelines for how long data is stored and when it's deleted  
✅ **C. Data retention**  
💡 Data retention policy.

**Q471.** Capabilities a chatbot can show compliance for (choose two) *(choose two)*  
✅ **B. Threat detection + C. Data protection**  
💡 Regulatory frameworks care about security controls such as threat detection and data protection. Auto scaling, cost optimization and microservices are architecture/efficiency topics.

**Q476.** PII must stay in the company's AWS Region  
✅ **B. Data residency**  
💡 Data residency.

**Q490.** Identify unauthorized users trying to access Bedrock  
✅ **B. AWS CloudTrail**  
💡 CloudTrail logs every API call, including denied attempts and who made them.

**Q514.** Store Bedrock invocation logs to monitor model inputs and outputs  
✅ **B. Enable model invocation logging in Amazon Bedrock.**  
💡 Enable Bedrock model invocation logging (to S3 and/or CloudWatch Logs). CloudTrail records API metadata, not full prompts/responses.
