# Domain 3 – Applications of Foundation Models

> Exam weight ≈ 28% (the biggest domain). Choosing FMs, inference parameters, cost, prompt engineering, RAG and vector stores, customization (fine-tuning, continued pre-training), agents, Bedrock features and FM evaluation.

**190 questions** in this domain. [← Back to index](README.md)

## Topics

- [Choosing a foundation model](#choosing-a-foundation-model) (11 questions)
- [Inference parameters](#inference-parameters) (13 questions)
- [Cost & pricing](#cost--pricing) (9 questions)
- [Prompt engineering](#prompt-engineering) (28 questions)
- [RAG, Knowledge Bases & vector stores](#rag-knowledge-bases--vector-stores) (31 questions)
- [Model customization](#model-customization) (30 questions)
- [Agents, AgentCore & MCP](#agents-agentcore--mcp) (14 questions)
- [Amazon Bedrock platform features](#amazon-bedrock-platform-features) (15 questions)
- [Bedrock model families](#bedrock-model-families) (11 questions)
- [Evaluating foundation models](#evaluating-foundation-models) (28 questions)

---

## Choosing a foundation model

### Key concepts

* **Latency / inference speed** for real-time use, often achieved with smaller models; **small language models** on edge devices.
* **Modality** (text, image, video, audio input/output), **context window / max tokens** (varies by model), **concurrency**, cost, customization support, language support.
* Pick the **smallest model that meets the quality bar** (cost and sustainability).

### Questions (11)

**Q81.** Model characteristic for real-time responses  
✅ **C. Inference speed**  
💡 Inference speed (latency) decides whether users get answers in real time. Training time and complexity matter less once the model is deployed.

**Q104.** Choose a model for real-time service quotes  
✅ **D. Model latency and optimized inference speed**  
💡 Real time means low latency and fast inference matter most.

**Q111.** How much information fits in one prompt  
✅ **B. Context window**  
💡 The context window (in tokens) is the maximum input (and often output) a model can handle per request.

**Q121.** Choose an FM that outputs both images and descriptions  
✅ **D. Modality**  
💡 Modality = the kinds of input/output a model supports (text, image, audio, video).

**Q147.** Call emergency services within 30 seconds of a crash with a pre-trained model  
✅ **B. Model size**  
💡 Smaller models infer faster (lower latency), which is critical for a hard time limit. Customization isn't wanted; cost and temperature don't drive speed.

**Q398.** Investment summaries within seconds, with consistent formatting and accuracy  
✅ **A. Inference latency with regulatory compliance and consistency capabilities**  
💡 You need low inference latency plus consistency/compliance capabilities. Multimodal, code or dialogue features aren't the requirement.

**Q448.** Term for how fast an FM processes requests and delivers output  
✅ **B. Inference latency**  
💡 Inference latency.

**Q459.** Choose a model to convert a booking system between programming languages  
✅ **A. Syntax, semantic understanding, and code optimization capabilities**  
💡 Look for strong syntax and semantic understanding of both languages plus code-optimization ability. Creativity or raw speed matter less.

**Q488.** Lowest-latency language inference on edge devices  
✅ **A. Deploy optimized small language models (SLMs) on edge devices.**  
💡 Run optimized small language models (SLMs) locally on the device. LLMs are too big for edge hardware; central APIs add network latency.

**Q497.** Match FM characteristics to definitions (hotspot) *(hotspot)*  
✅ **Prompt size → Context windows; Time to output → Latency; Simultaneous users → Concurrency**  
💡 How much fits in one prompt → context window; time to produce output → latency; many simultaneous users → concurrency.

**Q507.** What can differ across Bedrock LLMs for the same prompt  
✅ **A. Maximum token count**  
💡 Maximum token count (context window/output limit) varies by model. Temperature-style controls, on-demand inference and Guardrails work across models.

---

## Inference parameters

### Key concepts

| Parameter | Effect |
|---|---|
| **Temperature** ↑ | More random, diverse and creative output. ↓ → more deterministic/consistent (0 ≈ greedy) |
| **Top K** | Sample only from the K most likely next tokens |
| **Top P** | Sample from the smallest set of tokens whose probabilities add up to P |
| **Max tokens / response length** | Caps output length |
| **Stop sequences** | Strings that end generation |
| **Generation steps** (diffusion) | More denoising steps → more detail |
| **CFG scale** (diffusion) | Higher → image follows the prompt more closely |

Prompt changes (not parameters) control language, format, tone and length instructions.

### Questions (13)

**Q5.** Chatbot responses must be short and in a specific language  
✅ **A. Adjust the prompt.**  
💡 The prompt is the cheapest lever for format, length and language. Temperature and Top K change randomness, not language or length; changing model size doesn't target the requirement.

**Q30.** LLM outputs not diverse enough  
✅ **A. Temperature**  
💡 Raise temperature to increase randomness and variety. Batch size, learning rate and optimizer are training settings, not generation settings.

**Q137.** Same question gives answers with different length, tone and content; least overhead fix  
✅ **A. Lower the temperature parameter when making API calls to the LLM.**  
💡 Lower the temperature to make output more deterministic, a one-parameter change. Templates help but take more work; caching or retry loops add infrastructure.

**Q173.** Control how detailed or abstract generated images are  
✅ **C. Generation step**  
💡 In diffusion models, the number of generation (denoising) steps controls detail: more steps = more refined images. Batch size and checkpoints are training concepts.

**Q183.** Parameter that limits how many candidate next tokens are considered  
✅ **B. Top K**  
💡 Top K samples only from the K most likely tokens. Temperature reshapes probabilities; max tokens limits length.

**Q188.** More consistent sentiment-analysis outputs  
✅ **A. Decrease the temperature value.**  
💡 Decrease temperature for more deterministic outputs. Output length doesn't change consistency.

**Q202.** More diverse and creative LLM outputs  
✅ **A. Increase the temperature value.**  
💡 Increase temperature. Decreasing Top K makes output less diverse; response or prompt length doesn't affect creativity.

**Q275.** LLM responses as deterministic and stable as possible  
✅ **A. Configure the application to automatically set the temperature parameter to 0 when submitting the prompt to the LLM.**  
💡 Set temperature to 0 (near-greedy decoding). Asking the model in text to "be deterministic" doesn't control sampling.

**Q298.** Inference parameter that controls creativity  
✅ **A. Temperature**  
💡 Temperature. Top K also affects diversity, but temperature is the primary creativity control.

**Q397.** Reduce hallucinations  
✅ **C. Decrease the temperature inference parameter for the model.**  
💡 ⚠ The dump's key is lowering temperature: less random sampling means fewer made-up tokens. It helps somewhat; the stronger real-world fixes are RAG/grounding and Guardrails contextual grounding checks. No FM is "trained not to hallucinate".

**Q500.** Creative and short marketing emails  
✅ **C. Increase the temperature and decrease the response length.**  
💡 Increase temperature (creativity) and decrease max response length (shortness).

**Q501.** Make output more deterministic  
✅ **A. Decreasing the temperature**  
💡 Decrease temperature. Learning rate is a training parameter; stop sequences and token count control length.

**Q519.** Stable Diffusion images are random and lack specific details  
✅ **C. Increase the classifier-free guidance (CFG) scale.**  
💡 Increase the CFG (classifier-free guidance) scale so the image follows the prompt more closely. More steps refine quality but not prompt adherence.

---

## Cost & pricing

### Key concepts

* **On-Demand**: pay per input/output token, no commitment. Best for unpredictable/low or bursty usage.
* **Provisioned Throughput**: reserved model units (hourly, 1- or 6-month commitment). Required for **custom (fine-tuned) models** and good for steady high volume.
* **Batch inference**: asynchronous JSONL jobs in S3, ~50% cheaper. For non-urgent bulk/scheduled work.
* **Prompt caching**: reuse long repeated prefixes (system prompts) → lower cost and latency.
* Cost drivers: number of tokens, model size. Reduce prompt length, right-size the model.

### Questions (9)

**Q84.** Same long system prompt is sent with every request, raising cost and latency, without changing the model  
✅ **B. Use prompt caching with checkpoints for the inference.**  
💡 Prompt caching stores the repeated prefix at a cache checkpoint, so later requests reuse it: fewer billed input tokens and lower latency. Fine-tuning changes the model; Guardrails and KBs don't cache prompts.

**Q136.** Daily few-shot call with 10 examples; reduce monthly cost  
✅ **B. Decrease the number of tokens in the prompt.**  
💡 On-demand pricing is per token, so fewer prompt tokens (fewer/shorter examples) lowers cost. Provisioned Throughput is expensive for one call a day; fine-tuning also needs Provisioned Throughput.

**Q153.** Bedrock pricing with a limited budget and no long-term commitment  
✅ **A. On-Demand**  
💡 On-Demand is pay-per-token with no commitment. Provisioned Throughput needs a (1- or 6-month or hourly) capacity purchase; Bedrock has no Spot pricing.

**Q208.** Cost-effective FMs for summarization, code generation and assistants  
✅ **A. Select the smallest model that meets the performance requirements for each specific use case.**  
💡 Use the smallest model that meets each use case's quality bar ("right-size" the model). The largest model everywhere or custom FMs are wasteful; batch doesn't fit interactive assistants.

**Q216.** Bedrock pricing for weekly catalog updates  
✅ **C. Batch**  
💡 Batch inference is asynchronous and roughly 50% cheaper than On-Demand for selected models, ideal for scheduled bulk jobs. Provisioned Throughput is wasteful for weekly bursts.

**Q258.** Serve a fine-tuned Bedrock model with steady traffic, most cost-effectively  
✅ **D. Purchase Provisioned Throughput for the model on Amazon Bedrock.**  
💡 Custom Bedrock models need Provisioned Throughput; for steady, predictable traffic it's also the efficient option. You can't export Bedrock-tuned models to EC2/Lambda.

**Q396.** Generate synthetic responses for many prompts via API; no urgency; least effort  
✅ **B. Use Amazon Bedrock batch inference. Generate responses asynchronously.**  
💡 Bedrock batch inference: submit a JSONL file of prompts in S3 and get results asynchronously (and cheaper). Lambda loops or agents mean extra development.

**Q413.** Pilot with low usage and unpredictable future demand; minimize cost  
✅ **C. Use Amazon Bedrock with On-Demand Throughput.**  
💡 Bedrock On-Demand: pay per token, no commitment, scales automatically. Provisioned Throughput and self-hosted GPUs cost money even when idle.

**Q455.** What drives Bedrock inference cost  
✅ **A. Number of tokens consumed**  
💡 Number of tokens processed (input + output) under On-Demand pricing. Training data size and time are customization costs.

---

## Prompt engineering

### Key concepts

* **Zero-shot**: no examples. **One-shot**: one example. **Few-shot**: several examples (format, labels, style).
* **Chain-of-thought**: "think step by step", shows its reasoning. **Prompt chaining**: split a task into sequential prompts. **ReAct**: reasoning + actions/tool calls (live data). **Tree of thoughts**: explore branches.
* **System prompt**: defines role, tone and boundaries. **Prompt components**: task, role/persona, response style, success criteria.
* **Negative prompts** (image models such as Nova Canvas / Stable Diffusion): what *not* to include.
* Prompt engineering is the **cheapest, least-effort** customization (before RAG, then fine-tuning, then continued pre-training).

### Questions (28)

**Q8.** Pre-trained model must write marketing content in the brand voice  
✅ **C. Create effective prompts that provide clear instructions and context to guide the model's generation.**  
💡 Clear prompts with instructions and context steer tone and messaging without retraining. Changing architecture or pre-training a new model is costly and unnecessary.

**Q42.** Match prompt-design components (Nova) to definitions (hotspot) *(hotspot)*  
✅ **Use case → Task; Persona → Role; Tone/format → Response style; Metrics → Success criteria**  
💡 Task = what to do; Role = the persona to adopt; Response style = tone/format/structure; Success criteria = how to judge the output. Defining these makes iterative prompt refinement measurable.

**Q67.** Generate product descriptions in a format shown by examples  
✅ **D. Few-shot prompting**  
💡 Few-shot prompting gives several examples so the model copies the pattern. Zero-shot has no examples, one-shot only one; chain-of-thought is about reasoning steps.

**Q87.** Few-shot examples for intent detection  
✅ **C. Pairs of user messages and correct user intents**  
💡 Examples must map inputs to the target: user message → correct intent.

**Q103.** Change answer style depending on the user's age range, with the least effort  
✅ **B. Add a role description to the prompt context that instructs the model of the age range that the response should target.**  
💡 Add a role/audience instruction in the prompt ("explain for a 10-year-old"). No training needed; chain-of-thought and post-summarizing don't set style reliably.

**Q135.** Startup wants minimal upfront cost while customizing responses  
✅ **A. Prompt engineering**  
💡 Prompt engineering needs no training or infrastructure. Fine-tuning and pre-training cost money upfront; RAG adds a vector store and pipeline.

**Q139.** App must show its reasoning steps before the final answer  
✅ **B. Chain-of-thought prompting**  
💡 Chain-of-thought prompting ("think step by step") makes the model show intermediate reasoning.

**Q214.** Classify text sentiment as positive/negative with an LLM  
✅ **A. Provide examples of text passages with corresponding positive or negative labels in the prompt followed by the new text passage to be classified.**  
💡 Few-shot prompting: labeled examples followed by the new passage. Explaining how LLMs work doesn't help; unrelated examples confuse the model.

**Q260.** Match prompting techniques to descriptions (hotspot) *(hotspot)*  
✅ **Few examples → Few-shot; Step-by-step → Chain-of-thought; No examples → Zero-shot**  
💡 A few examples → few-shot; step-by-step reasoning → chain-of-thought; no examples → zero-shot.

**Q261.** Term for instructions given to an FM  
✅ **A. Prompt**  
💡 A prompt.

**Q318.** Support chatbot must match the company tone  
✅ **C. Refine the prompt until the FM produces the desired responses.**  
💡 Iteratively refine the prompt until responses match the tone. Token limits, batching and higher temperature don't set tone.

**Q347.** Improve accuracy of a Bedrock app most cost-effectively  
✅ **D. Use prompt engineering.**  
💡 Prompt engineering costs nothing extra. Fine-tuning, retraining or a new FM all cost training money.

**Q391.** Match prompt templates to techniques (hotspot) *(hotspot)*  
✅ **No examples → Zero-shot; Example images → Few-shot; Step by step → Chain-of-thought**  
💡 Classify with no examples → zero-shot. Three labeled example images then classify → few-shot. "Think step by step" → chain-of-thought.

**Q409.** Break a complex task into subtasks sent to an LLM one after another  
✅ **B. Prompt chaining**  
💡 Prompt chaining: the output of one prompt feeds the next. Tree of thoughts explores branching reasoning paths; RAG retrieves data.

**Q415.** Chatbot must check live inventory and return product location  
✅ **D. Reasoning and acting (ReAct) prompting**  
💡 ReAct (reason + act) interleaves reasoning with tool calls (e.g. inventory API) and uses the results. Zero-/few-shot can't fetch live data.

**Q430.** Generate technical-manual text with the least development effort  
✅ **C. Create specialized prompts for a pre-trained, general purpose LLM.**  
💡 Prompt a pre-trained general-purpose LLM with specialized prompts. Any training or fine-tuning is more effort.

**Q445.** Image FM generates images unrelated to the prompt  
✅ **B. Use negative prompts.**  
💡 Negative prompts tell image models what not to generate, steering away from unwanted content. Ambiguous prompts make it worse.

**Q446.** Keep specific items out of Nova Canvas images  
✅ **C. Use a negative prompt.**  
💡 Use a negative prompt (the negativeText parameter) listing what to exclude. Temperature isn't an image control here.

**Q452.** "Show its work by explaining its reasoning step by step"  
✅ **A. Chain-of-thought prompting**  
💡 Chain-of-thought prompting.

**Q456.** Assistant gives generic, irrelevant product suggestions  
✅ **A. Use few-shot prompting to add domain-specific context and explicit instructions.**  
💡 Few-shot prompting with domain context and explicit instructions. Hiding reasoning or changing formality doesn't add relevance.

**Q460.** Match techniques to use cases (hotspot) *(hotspot)*  
✅ **External sources → RAG; Unseen tasks → Zero-shot; Limited data → Few-shot**  
💡 External sources → RAG. Generalize to unseen tasks without examples → zero-shot. Limited examples for new tasks → few-shot.

**Q466.** Exclude characteristics from Nova Canvas output  
✅ **B. Negative prompts**  
💡 Negative prompts. Mask/inpainting/outpainting prompts edit specific regions of an image.

**Q468.** Generated images must not contain specific attributes  
✅ **C. Negative prompting**  
💡 Negative prompting.

**Q469.** Complex problems needing detailed, step-by-step reasoning  
✅ **D. Chain-of-thought prompting**  
💡 Chain-of-thought prompting.

**Q470.** Meeting summaries miss key decisions and commitments; use context engineering  
✅ **B. Structure the prompt to include action item examples that have been reviewed and approved.**  
💡 Put reviewed, approved examples of action items in the prompt, so the model knows what to capture. A bigger context window doesn't teach what matters; fine-tuning isn't context engineering.

**Q475.** Concise, feature-specific product descriptions  
✅ **B. Create prompts for each product category that highlight the key features. Include the desired output format and length for each prompt response.**  
💡 Category-specific prompts that highlight key features and specify output format and length. One generic prompt plus manual edits doesn't scale.

**Q509.** Improve a bank account-opening chatbot with prompt engineering  
✅ **C. Few-shot prompting**  
💡 Few-shot prompting with examples drawn from the public bank documents guides answers.

**Q510.** Primary purpose of system prompts  
✅ **C. To define the role and behavioral boundaries of AI**  
💡 Define the AI's role, tone and behavioral boundaries for the conversation.

---

## RAG, Knowledge Bases & vector stores

### Key concepts

* **RAG** = retrieve relevant chunks from your data at query time and add them to the prompt → grounded, current, citable answers **without retraining**; reduces hallucination.
* **Ingestion pipeline:** parse → **chunk** (smaller, coherent pieces → more relevant retrieval) → **embed** (embedding model) → write to vector store. Content embeddings/indexing can run offline in batches; query embedding, retrieval and generation run live.
* **Amazon Bedrock Knowledge Bases** = managed RAG. **Vector stores:** OpenSearch Service/Serverless (k-NN), Aurora PostgreSQL (pgvector), Neptune Analytics, MemoryDB, S3 Vectors. **Kendra** for intelligent search.
* Multimodal search → multimodal embeddings model.
* Choose RAG over fine-tuning when data **changes often** or must be **cited**.

### Questions (31)

**Q10.** Chat over product-manual PDFs, most cost-effective  
✅ **D. Upload PDF documents to an Amazon Bedrock knowledge base. Use the knowledge base to provide context when users submit prompts to Amazon Bedrock.**  
💡 A Bedrock Knowledge Base indexes the PDFs once and retrieves only relevant chunks per question (RAG). Stuffing PDFs into every prompt costs tokens and hits context limits; fine-tuning is expensive and goes stale.

**Q34.** Ground a pre-trained LLM's answers in authoritative company data  
✅ **C. Retrieval Augmented Generation (RAG)**  
💡 RAG retrieves relevant facts at query time and adds them to the prompt, so answers are accurate and traceable to sources. Prompt engineering alone can't supply new facts.

**Q40.** Improve accuracy of a model that relies on rapidly changing inventory data  
✅ **C. Retrieval Augmented Generation (RAG)**  
💡 RAG fetches the latest inventory at inference time; retraining or transfer learning can't keep up with constant changes. One-shot prompting adds an example, not fresh data.

**Q59.** HR-policy chatbot over a large document base  
✅ **A. Use Retrieval Augmented Generation (RAG).**  
💡 RAG retrieves the relevant policy passages and grounds answers in them. Few-shot prompting can't supply all the documents; temperature/token tweaks don't add knowledge.

**Q72.** OpenSearch feature that enables vector-database apps  
✅ **C. Scalable index management and nearest neighbor search capability**  
💡 k-NN (nearest-neighbor) vector search over scalable indexes is what makes OpenSearch work as a vector store for semantic search and RAG.

**Q95.** Vector database for natural-language image search with nearest-neighbor queries  
✅ **D. Amazon OpenSearch Service**  
💡 OpenSearch Service supports vector (k-NN) similarity search. Comprehend, Personalize and Polly aren't vector stores.

**Q128.** Airline chatbot using LLMs and a knowledge base with the least development effort  
✅ **B. Develop a Retrieval Augmented Generation (RAG) agent by using Amazon Bedrock.**  
💡 A RAG agent on Bedrock (Knowledge Bases + Agents) is managed and needs no model training. Autopilot is for tabular ML; fine-tuning is more effort and doesn't keep the knowledge current.

**Q140.** Use documents as a RAG knowledge base  
✅ **B. Create embeddings from document chunks.**  
💡 Split documents into chunks and create embeddings stored in a vector DB, so semantic search can find relevant chunks.

**Q184.** Search application for queries containing text and images  
✅ **A. Multi-modal embedding model**  
💡 A multimodal embedding model (e.g. Titan Multimodal Embeddings) puts text and images in the same vector space for similarity search. Generation models create content rather than search vectors.

**Q223.** Argument for RAG when leaders think it adds complexity  
✅ **C. RAG decreases hallucinations.**  
💡 RAG grounds answers in retrieved facts, reducing hallucinations (and needs no retraining). It doesn't speed up inference or training.

**Q232.** Product Q&A assistant over a big catalog with little labeled data, least effort  
✅ **A. Use a Retrieval Augmented Generation (RAG) architecture to query the product database at runtime. Provide relevant, unmodified product descriptions as context for the foundation model (FM).**  
💡 RAG queries the product database at runtime and passes relevant descriptions to the FM. No training needed; fine-tuning or building FMs is heavier and goes stale.

**Q233.** Technique combining LLMs with external knowledge bases  
✅ **C. Retrieval Augmented Generation (RAG)**  
💡 Retrieval Augmented Generation (RAG).

**Q234.** Service that stores embeddings in a vector database for RAG  
✅ **B. Amazon OpenSearch Service**  
💡 Amazon OpenSearch Service (also OpenSearch Serverless, Aurora PostgreSQL pgvector, Neptune Analytics, MemoryDB, S3 Vectors). Ground Truth, Transcribe, Textract are not vector stores.

**Q252.** Agents ask FAQ questions that change over time; most cost-effective answers  
✅ **D. Use Retrieval Augmented Generation (RAG) with prompt engineering techniques.**  
💡 RAG plus prompt engineering pulls current answers from an updatable knowledge source, with no retraining. Regular fine-tuning or pre-training is costly.

**Q324.** Add company context to a Bedrock FM most cost-effectively  
✅ **A. Use Amazon Bedrock Knowledge Bases.**  
💡 Bedrock Knowledge Bases (managed RAG). Custom models need training and Provisioned Throughput; agents are for actions.

**Q346.** Database for storing and querying embeddings as vectors  
✅ **B. Amazon Aurora PostgreSQL**  
💡 Aurora PostgreSQL with the pgvector extension stores and searches vectors. Athena, Redshift and EMR are analytics services.

**Q350.** Order Bedrock Knowledge Base ingestion steps (hotspot) *(hotspot)*  
✅ **Parse → Chunk → Embed → Write to vector store**  
💡 Ingestion = parse documents (text, tables, images) → chunk → embed chunks → write vectors to the vector store. Retrieval with RAG happens later at query time, not during ingestion.

**Q354.** LLM research report cites references that don't exist  
✅ **C. Use Retrieval Augmented Generation (RAG) techniques.**  
💡 Hallucinated citations: ground the LLM with RAG over trusted sources so references come from real documents. Higher temperature increases hallucination.

**Q362.** RAG pipeline steps to run as offline batch jobs for daily content (choose two) *(choose two)*  
✅ **A. Generation of content embeddings + C. Creation of the search index**  
💡 Generating content embeddings and building/updating the search index can run offline in batches. Query embedding, retrieval and response generation must happen live per user request.

**Q374.** Medical summaries contain credible-looking inaccuracies  
✅ **B. Implement Retrieval Augmented Generation (RAG) to ground responses.**  
💡 Use RAG to ground summaries in the actual patient records/approved sources. Bigger models still hallucinate.

**Q378.** Purpose of chunking in RAG  
✅ **C. To improve the contextual relevancy of results retrieved from the vector index**  
💡 Smaller, coherent chunks make retrieval more precise and relevant (and fit in the context window). It is not mainly about storage cost.

**Q393.** Real-time contextual answers from company policies, most cost-effectively  
✅ **C. Implement Retrieval Augmented Generation (RAG) for in-context responses.**  
💡 RAG retrieves relevant policy text into the prompt. Retraining, fine-tuning and pre-training are costly and need repeating when policies change.

**Q404.** Automatically retrieve relevant product documentation for agents (choose two) *(choose two)*  
✅ **B. Amazon Bedrock + D. Amazon Kendra**  
💡 Amazon Kendra provides intelligent (semantic) enterprise search over documents; Bedrock (e.g. Knowledge Bases or RAG with Kendra as retriever) generates answers from it.

**Q410.** Service with vector storage and vector search for Bedrock  
✅ **B. Amazon OpenSearch Service**  
💡 Amazon OpenSearch Service (k-NN). DynamoDB, ElastiCache (classic) and Redshift aren't the expected answer here.

**Q444.** Policy chatbot must reflect frequent updates in near real time  
✅ **C. Create a Retrieval Augmented Generation (RAG) workflow by using Amazon Bedrock Knowledge Bases.**  
💡 RAG with Bedrock Knowledge Bases: re-sync the data source and answers immediately use new policies. Fine-tuning would need repeating each change.

**Q461.** Accurate description of RAG  
✅ **B. A process by which large language models (LLMs) reference external authoritative knowledge bases to enhance the relevance and accuracy of LLM responses without re-training**  
💡 The LLM references external authoritative knowledge at query time to improve relevance/accuracy without retraining.

**Q483.** Convert private data into vectors before storing them in OpenSearch  
✅ **C. Text embeddings model**  
💡 A text embeddings model (e.g. Titan Text Embeddings) produces vectors.

**Q495.** Supplement a Titan model with private company data  
✅ **C. Create an Amazon Bedrock knowledge base.**  
💡 Create a Bedrock knowledge base (RAG). Logging or temperature changes don't add knowledge.

**Q513.** Advantage of RAG for NLP  
✅ **A. RAG can use external knowledge sources to generate more accurate and informative responses.**  
💡 Uses external knowledge sources for more accurate, informative answers. It doesn't speed up training and isn't a speech or vision technique.

**Q520.** LLM limitation that RAG targets for factual correctness  
✅ **A. Hallucinations**  
💡 Hallucinations.

**Q521.** Purpose of chunking in RAG  
✅ **B. Splitting large documents into smaller sections to enhance search efficiency**  
💡 Split large documents into smaller sections for efficient, relevant retrieval (and to fit embedding/context limits).

---

## Model customization

### Key concepts

| Technique | Data | Purpose |
|---|---|---|
| **Fine-tuning** (instruction / supervised) | **Labeled** prompt→completion pairs (JSONL) | Improve a specific task, style or tone |
| **Continued pre-training** | **Unlabeled** domain text | Teach domain knowledge/vocabulary; keep the model current |
| **Distillation** | Teacher model outputs | Transfer knowledge from a large model to a smaller one |
| **Transfer learning** | Reuse a pre-trained model | Adapt to a new related task |
| **RLHF** | Human ratings/preferences | Align behavior with human values/feedback |
| **Data augmentation** | Synthetic variations | Expand scarce/imbalanced labeled data |

Effort order: prompt engineering < RAG < fine-tuning < continued pre-training < pre-training from scratch.

### Questions (30)

**Q47.** Benefit of ongoing (continued) pre-training of an FM  
✅ **B. Improved model performance over time**  
💡 Continued pre-training keeps feeding the model new domain data, so its knowledge and performance improve over time. It adds training cost and time; it doesn't simplify the model.

**Q54.** Multilingual, multi-dialect FM that follows responsible AI  
✅ **B. Implement continued pre-training on a diverse multi-language and multi-dialect dataset.**  
💡 Continued pre-training on a diverse, multi-language, multi-dialect corpus gives broad coverage and less bias. Prompt templates don't teach languages; per-language models or sequential distillation are complex and fragmented.

**Q61.** Data needed to fine-tune an LLM to refine output style  
✅ **C. Samples of pairs of input and output messages**  
💡 Fine-tuning is supervised: you need labeled prompt → desired-response pairs so the model learns the mapping and style.

**Q75.** Match customization methods to descriptions (hotspot) *(hotspot)*  
✅ **Labeled data → Fine-tuning; Unlabeled domain data → Continued pre-training; Large-to-small → Distillation**  
💡 Fine-tuning uses labeled data for specific tasks. Continued pre-training uses unlabeled domain text. Distillation transfers knowledge from a large "teacher" model to a smaller "student".

**Q102.** Use 100 high-quality conversations to teach a chatbot the company tone  
✅ **D. Create an Amazon Bedrock fine-tuning job.**  
💡 A Bedrock fine-tuning job on prompt-response examples adapts style and tone. Personalize is recommendations; HyperPod pre-training is far too heavy; TensorRT only speeds up inference.

**Q112.** Bedrock customization: tasks/examples vs domain documents vs unlabeled data over time (hotspot) *(hotspot)*  
✅ **Task performance → Fine-tuning; Domain documents → Continued pre-training; More unlabeled data over time → Continued pre-training**  
💡 Labeled task examples → fine-tuning. Raw domain documents and ongoing unlabeled data → continued pre-training.

**Q123.** Adapt pre-trained models to new related tasks instead of training from scratch  
✅ **B. Use transfer learning.**  
💡 Transfer learning reuses what a pre-trained model learned and adapts it to a new task.

**Q124.** Keep an FM current with regular updates on recent data  
✅ **B. Continuous pre-training**  
💡 Continued (continuous) pre-training periodically trains the FM on new unlabeled data.

**Q125.** Adapt an FM trained for one task to a different but related task  
✅ **C. Transfer learning**  
💡 Transfer learning (e.g. fine-tuning the existing model on the new task). Hyperparameter tuning only optimizes settings; pre-training starts from scratch.

**Q145.** Familiarize an LLM with medical topics using medical papers  
✅ **A. Continuous pre-training**  
💡 Continued pre-training on unlabeled domain text teaches vocabulary and domain knowledge.

**Q152.** Pick customization approach per situation (hotspot) *(hotspot)*  
✅ **New domain-specific task → Model fine-tuning; Limited labeled data → Data augmentation; Only unlabeled data → Continued pre-training**  
💡 A new task → fine-tune on labeled examples. Too little labeled data → data augmentation to create more. Only unlabeled data → continued pre-training.

**Q158.** Data format to fine-tune a text-to-text FM for tone  
✅ **B. JSONL file that contains prompt-completion pairs**  
💡 Bedrock fine-tuning expects JSONL with prompt-completion pairs, one example per line.

**Q172.** Supervised training on a small labeled task-specific dataset  
✅ **A. Fine-tuning**  
💡 That's fine-tuning. Pre-training uses huge unlabeled datasets.

**Q229.** Customize third-party LLMs on a collection of regulatory documents  
✅ **D. Continued pre-training**  
💡 Unlabeled domain documents → continued pre-training. Fine-tuning needs labeled prompt-completion pairs.

**Q238.** Benefit of fine-tuning an FM  
✅ **D. Fine-tuning improves the performance of the FM on a specific task by further training the FM on new labeled data.**  
💡 Improves performance on a specific task by further training on labeled data. It doesn't retrain from scratch, shrink the model or refresh general knowledge.

**Q241.** Benefit of ongoing pre-training  
✅ **B. Improves model performance over time**  
💡 Model performance improves over time as it learns from new data. (Same idea as Q47.)

**Q265.** FM struggles with complex scientific terms even after prompt engineering  
✅ **B. Use domain adaptation fine-tuning to adapt the FM to complex scientific terms.**  
💡 Domain-adaptation fine-tuning (training on domain text) teaches the vocabulary. Removing the terms destroys the content; inference parameters don't add knowledge.

**Q277.** What continued pre-training is  
✅ **B. The process of providing unlabeled data to a pre-trained language model to improve the model’s domain knowledge**  
💡 Further training a pre-trained model on unlabeled domain data to improve domain knowledge. (Labeled task data = fine-tuning; training from scratch = pre-training.)

**Q285.** Customize an FM with internal documents  
✅ **B. Continued pre-training**  
💡 Continued pre-training on the (unlabeled) documents. Distillation shrinks models; classification/regression are ML tasks.

**Q294.** Moderation LLM aligned with company values that adapts to new trends within 3 months  
✅ **D. Conduct reinforcement learning from human feedback (RLHF) by using real-time input from skilled moderators.**  
💡 RLHF with real-time feedback from skilled moderators aligns the model with company values and keeps it learning about new content. Historical data or generic ethics can't capture emerging trends.

**Q314.** Customize an FM with a high-quality labeled dataset to categorize images and extract specs  
✅ **C. Perform fine-tuning**  
💡 Labeled data → fine-tuning. Continued pre-training uses unlabeled data; agents and prompting don't train.

**Q317.** Domain knowledge missing; only unlabeled data available  
✅ **C. Continued pre-training**  
💡 Continued pre-training on the unlabeled domain data. Supervised fine-tuning needs labels; full training from scratch is wasteful.

**Q388.** Order techniques from least to most effort (hotspot) *(hotspot)*  
✅ **Prompt engineering → RAG → Fine-tuning → Continued pre-training**  
💡 Prompt engineering (just prompts) → RAG (add retrieval) → fine-tuning (labeled data + training) → continued pre-training (large unlabeled corpus + training).

**Q417.** Prepare data for instruction-based fine-tuning on a domain  
✅ **C. Create pairs of questions and answers that specifically address topics related to the company's industry domain.**  
💡 Create instruction/question → answer pairs about the domain. A merged document file suits continued pre-training; few-shot prompts are not training data.

**Q435.** How to fine-tune a Bedrock FM for search accuracy  
✅ **A. Provide labeled data with the prompt field and the completion field.**  
💡 Provide labeled JSONL records with "prompt" and "completion" fields. Provisioned Throughput is for serving, not training; journals/textbooks (unlabeled) = continued pre-training.

**Q440.** Training dataset format for Bedrock text-to-text fine-tuning  
✅ **A. A JSON file with labeled data**  
💡 JSON Lines with labeled prompt/completion records. Unlabeled text is for continued pre-training.

**Q454.** Train on labeled data to adapt to industry terminology and requirements  
✅ **B. Fine-tuning**  
💡 Fine-tuning (labeled). Continued pre-training would use unlabeled data; quantization shrinks models.

**Q477.** Fine-tune an FM and deploy it on Bedrock for internal use  
✅ **D. Use Amazon SageMaker AI to customize the FM. Then, import the trained model into Amazon Bedrock.**  
💡 Customize the model in SageMaker AI, then bring it to Bedrock with Custom Model Import. (Bedrock's own fine-tuning is another path, but it isn't offered here.)

**Q506.** Use employee feedback to refine a fine-tuned assistant  
✅ **C. Use reinforcement learning from human feedback (RLHF).**  
💡 RLHF uses human ratings/preferences as a reward signal to align responses. Distillation shrinks models; prompt routing picks models.

**Q527.** Generate responses based on company data  
✅ **C. Fine-tune a custom model on company data.**  
💡 ⚠ The dump's key is fine-tuning a custom model on company data, because every other option is a plain pre-trained model with no company data. On real questions, check whether RAG / Knowledge Bases is offered; for changing or factual company data RAG is usually the better choice.

---

## Agents, AgentCore & MCP

### Key concepts

* **Amazon Bedrock Agents**: an FM plans multi-step tasks and calls APIs (**action groups**: API schema + Lambda) and knowledge bases. Use for "process the request and invoke APIs" scenarios. Accuracy can be tuned through **advanced prompts**.
* **Amazon Bedrock AgentCore**: framework/model-agnostic platform to deploy and operate agents. Runtime (serverless hosting), Memory (context across sessions), Gateway (APIs → tools), Identity, Code Interpreter, Browser tool, Observability (dashboards).
* **Model Context Protocol (MCP)**: open standard connecting assistants to tools and live data. Host = app embedding the assistant; client = manages connections; server = exposes tools/resources. Security: trusted sources only, keep updated, don't auto-approve tools, no plain-text secrets.

### Questions (14)

**Q14.** Convert queries to OpenSearch requests, create CSVs and upload to S3 with the least operational effort  
✅ **A. Create an AI agent to perform the required steps.**  
💡 A multi-step task that calls tools/APIs is what an AI agent does. A single FM with few-shot prompting can't execute actions; custom code without AI can't interpret natural-language queries.

**Q15.** Key benefit of Bedrock Agents for high-volume customer support  
✅ **B. Automation of repetitive tasks and orchestration of complex workflows**  
💡 Agents automate repetitive tasks and orchestrate multi-step workflows (calling APIs, knowledge bases). They don't create custom FMs or auto-pick models.

**Q16.** GenAI app must process requests and invoke reservation APIs  
✅ **A. Agents**  
💡 Bedrock Agents interpret the request and call APIs via action groups. Knowledge Bases retrieve documents, Guardrails filter content, prompt routing picks a model.

**Q35.** Deploy agents built with different frameworks and models on flexible infrastructure  
✅ **C. Amazon Bedrock AgentCore**  
💡 Amazon Bedrock AgentCore is a framework- and model-agnostic runtime for hosting and operating agents (runtime, memory, identity, gateway, observability). Bedrock Agents is the managed agent builder; Flows chains prompts.

**Q48.** Assistant must evaluate data sources, call external APIs, generate and rank response options  
✅ **D. Agents**  
💡 Multi-step reasoning plus API calls = Bedrock Agents. Knowledge Bases only retrieve; Prompt Management stores prompts; streaming only changes how output is delivered.

**Q106.** App must orchestrate multiple actions and API calls to make reservations  
✅ **A. Agents for Amazon Bedrock**  
💡 Agents for Amazon Bedrock plan steps and call APIs. Playgrounds are for testing; Personalize and Rekognition are unrelated.

**Q156.** Improve a Bedrock agent's accuracy with specific examples  
✅ **A. Modify the advanced prompts for the agent to include the examples.**  
💡 Edit the agent's advanced prompts (prompt templates for pre-processing, orchestration, etc.) to include few-shot examples. Guardrails filter content; Ground Truth labels data for training.

**Q190.** Bedrock agents lack context and don't reach external services for bookings  
✅ **D. Custom API to provide more context**  
💡 Give the agent a custom API (an action group with an API schema + Lambda) so it can fetch context and act. ⚠ MCP is a newer standard for tool access too, but the dump's key is the custom API.

**Q210.** Assistant must check live inventory in the warehouse system  
✅ **B. Model Context Protocol (MCP)**  
💡 Model Context Protocol (MCP) is an open standard for connecting assistants to external tools and live data sources. RAG retrieves indexed documents (not live system state); fine-tuning and prompting add no live data.

**Q325.** Deploy an agentic report generator with high scalability and the least overhead  
✅ **C. Use Amazon Bedrock AgentCore Runtime to deploy the solution.**  
💡 Bedrock AgentCore Runtime is serverless, scalable hosting for agents built with any framework. EC2, SageMaker endpoints or manual API Gateway wiring add operations work.

**Q333.** Match AgentCore components (hotspot) *(hotspot)*  
✅ **Dashboards → Observability; Secure code → Code Interpreter; Browser runtime → Browser tool**  
💡 Observability = dashboards and traces of agent behavior; Code Interpreter = secure sandboxed code execution; Browser tool = serverless browser for agents. (Runtime hosts agents, Gateway turns APIs into tools, Memory stores context, Identity handles auth.)

**Q344.** App to check open claims, get claim details and access claim documents  
✅ **B. Use Agents for Amazon Bedrock with Amazon Bedrock knowledge bases to build the application.**  
💡 Bedrock Agents (actions such as looking up claims through APIs) + Bedrock Knowledge Bases (retrieving claim documents).

**Q389.** AgentCore feature to keep context across interactions without managing infrastructure  
✅ **C. Memory**  
💡 AgentCore Memory gives managed short- and long-term memory. Gateway exposes tools; Browser and Code Interpreter are tools.

**Q441.** Match MCP components to functions (hotspot) *(hotspot)*  
✅ **App environment → MCP host; Manages connections → MCP client; Exposes tools/data → MCP server**  
💡 The MCP host is the application that embeds the assistant (e.g. the IDE with Q Developer); the MCP client lives inside the host and manages connections to servers; the MCP server exposes tools, resources and prompts.

---

## Amazon Bedrock platform features

### Key concepts

* Serverless, API access to many FMs (Amazon Nova/Titan, Anthropic, Meta, Mistral, Stability…). Your data isn't shared with model providers or used to train base models.
* **Prompt Management** (reusable templates with variables, tools config), **Intelligent Prompt Routing** (one endpoint picks the model), **Flows** (chain steps), **Playgrounds**, **PartyRock** (free no-code learning playground).
* **Custom models**: fine-tuning / continued pre-training jobs read data from **S3**; serve via **Provisioned Throughput**. **Custom Model Import** brings your own weights (e.g. trained in SageMaker).
* **Model invocation logging** captures full prompts/responses (to S3/CloudWatch Logs).

### Questions (15)

**Q51.** Save and reuse system instructions for daily FM use in Bedrock  
✅ **D. Prompt management**  
💡 Bedrock Prompt Management stores, versions and reuses prompts. Playgrounds are for experiments, Knowledge Bases hold documents for RAG, Guardrails filter content.

**Q52.** Use a custom (fine-tuned) Bedrock model for inference  
✅ **A. Purchase Provisioned Throughput for the custom model.**  
💡 Custom models in Bedrock are served through purchased Provisioned Throughput (a dedicated capacity commitment). Model Registry and SageMaker endpoints are SageMaker-side concepts.

**Q58.** Use FMs to automate location-based product descriptions and recommendations in a call center  
✅ **C. Amazon Bedrock**  
💡 Amazon Bedrock gives API access to FMs for generating text. Macie finds sensitive data, Transcribe converts speech to text, Textract reads documents.

**Q174.** Service that makes FMs available to build and scale GenAI apps  
✅ **B. Amazon Bedrock**  
💡 Amazon Bedrock: serverless API access to FMs from Amazon and third parties.

**Q192.** Requirement for using a custom (fine-tuned) model through Bedrock  
✅ **A. Purchase Provisioned Throughput for the custom model.**  
💡 Bedrock custom models are invoked through Provisioned Throughput, which must be purchased first. (Same concept as Q52.)

**Q284.** Where to upload a validation dataset for a Bedrock custom model  
✅ **A. Amazon S3**  
💡 Amazon S3: Bedrock reads training and validation datasets from S3.

**Q292.** Run proprietary FM weights on a managed service without infrastructure  
✅ **B. Amazon Bedrock Custom Model Import**  
💡 Amazon Bedrock Custom Model Import brings your own weights (supported architectures such as Llama, Mistral) into serverless Bedrock. EC2/Lambda need infrastructure management; JumpStart hosts catalog models.

**Q313.** Service that helps choose FMs for GenAI use cases  
✅ **B. Amazon Bedrock**  
💡 Amazon Bedrock offers many FMs, a playground and model evaluation to compare them.

**Q343.** Reusable slogan template with a per-product description inserted  
✅ **A. Prompt management**  
💡 Bedrock Prompt Management supports templates with variables ({{product_description}}) filled in at runtime.

**Q359.** Generate hotel descriptions in a consistent brand style  
✅ **D. Amazon Bedrock**  
💡 Amazon Bedrock FMs generate text in a consistent style (with prompts/templates). Comprehend analyzes text; it doesn't write it.

**Q363.** Reusable Prompt Management prompt must call an external API  
✅ **B. Use a tools configuration.**  
💡 A tools configuration (function/tool definitions) lets the prompt invoke external tools. Variables insert text; stop sequences end output.

**Q416.** One endpoint; Bedrock should pick the best model per request  
✅ **C. Amazon Bedrock prompt router**  
💡 Bedrock Intelligent Prompt Routing sends each prompt to the model (within a family) that best balances quality and cost.

**Q423.** Service with a broad range of high-performing FMs  
✅ **A. Amazon Bedrock**  
💡 Amazon Bedrock.

**Q453.** Develop and deploy with FMs with the least development effort  
✅ **A. Amazon Bedrock**  
💡 Amazon Bedrock: serverless, API-based access to FMs. SageMaker needs more ML engineering; PartyRock is a learning playground.

**Q458.** Learn about GenAI apps in an experimental environment, most cost-effectively  
✅ **C. Amazon Bedrock PartyRock**  
💡 Amazon Bedrock PartyRock is a free, no-code playground for building GenAI apps. Q Business, Q Developer and JumpStart are production tools.

---

## Bedrock model families

### Key concepts

| Model | Use |
|---|---|
| **Nova Micro** | Text-only, cheapest/fastest |
| **Nova Lite** | Low-cost multimodal (text, image, video in) |
| **Nova Pro / Premier** | More capable multimodal; fine-tunable (Pro) |
| **Nova Canvas** / Titan Image Generator / Stable Diffusion | Image generation (negative prompts, inpainting) |
| **Nova Reel** | Video generation |
| **Nova Sonic** | Real-time speech-to-speech |
| **Titan Embeddings / Multimodal Embeddings** | Vectors for RAG / search |

### Questions (11)

**Q60.** Generate creative video content with the least operational effort  
✅ **C. Use the Amazon Nova Reel model on Amazon Bedrock to generate videos.**  
💡 Amazon Nova Reel generates video directly. Titan Image Generator and Nova Canvas create images (you'd still have to edit them into video); Nova Pro is a multimodal understanding model that outputs text.

**Q76.** Classify equipment from images using text descriptions, with the least overhead  
✅ **B. Use a multimodal model on Amazon Bedrock to classify the images by providing the text descriptions.**  
💡 A multimodal FM on Bedrock can take the image plus the text descriptions and classify zero-/few-shot, with no training pipeline. All other options require training a model.

**Q93.** Let students add illustrations to stories  
✅ **A. Use Amazon Bedrock Stable Diffusion 3.5 Large to generate images based on text inputs.**  
💡 A text-to-image model such as Stable Diffusion 3.5 Large on Bedrock generates images from story text. Polly = speech; Rekognition analyzes existing images.

**Q197.** Choose between Nova Micro and Nova Lite to process documents and images cheaply  
✅ **C. Nova Micro supports only text. Nova Lite supports images, videos, and text.**  
💡 Nova Micro is text-only (cheapest, fastest); Nova Lite is a low-cost multimodal model (text, image, video). Images need Nova Lite.

**Q239.** Bedrock FM that can be fine-tuned for text, image and video understanding  
✅ **A. Amazon Nova Pro**  
💡 Amazon Nova Pro (also Nova Lite) is multimodal and supports fine-tuning. Nova Micro is text-only; Titan Text Express is text; Titan Multimodal Embeddings produces embeddings.

**Q306.** Nova models for ad videos plus a shopping assistant; low cost, latency tolerated (choose two) *(choose two)*  
✅ **B. Amazon Nova Reel + C. Amazon Nova Micro**  
💡 Nova Reel generates video; Nova Micro is the cheapest text model for the assistant. Canvas makes images; Sonic is real-time speech; Premier is the most capable (and costliest).

**Q365.** Cheapest multilingual, multimodal Nova model  
✅ **A. Nova Lite**  
💡 Nova Lite: low-cost multimodal (text, image, video input). Nova Pro costs more; Canvas (images) and Reel (video) are generation models.

**Q376.** Input is text or a photo of a question; output is a written answer with explanation  
✅ **B. Large multi-modal language model**  
💡 A large multimodal LLM accepts images and text and produces text. Pure CV models don't write explanations; diffusion makes images; TTS makes audio.

**Q482.** Chatbot that takes text and image inputs  
✅ **A. Amazon Bedrock**  
💡 Amazon Bedrock with a multimodal LLM (e.g. Nova, Claude). Comprehend is text-only analysis; Rekognition analyzes images but doesn't chat.

**Q508.** Identify company products in social media images  
✅ **D. Multimodal understanding large language model (LLM)**  
💡 A multimodal understanding LLM interprets images. Diffusion generates images; text embeddings and multilingual LLMs don't see images.

**Q529.** Tutor app takes text or a photo of a question and returns a written explanation  
✅ **B. Multimodal LLM**  
💡 A multimodal LLM (image + text in, text out).

---

## Evaluating foundation models

### Key concepts

| Metric | Use |
|---|---|
| **ROUGE** | Summarization: overlap/recall vs reference summaries |
| **BLEU** | Translation: n-gram precision vs reference translations (relative comparison) |
| **BERTScore** | Semantic similarity using embeddings (meaning, not exact words) |
| **Perplexity** | Language-model confidence |
| **FID** | Image generation quality |
| RAG: **context relevance**, **recall/coverage** (retrieval); **faithfulness**, correctness, completeness (generation) |
| Responsible AI: toxicity, harmfulness, stereotyping, refusal |

* **Bedrock model evaluation**: automatic (built-in datasets/metrics), **human** (your team or AWS-managed, for subjective style), **LLM-as-a-judge**, plus RAG evaluations. SageMaker Clarify FMEval for JumpStart models.
* Real-world performance: A/B testing; domain-specific benchmarks; alignment with business use cases.

### Questions (28)

**Q6.** Automated metric comparing generated summaries with human reference summaries  
✅ **B. Recall-Oriented Understudy for Gisting Evaluation (ROUGE)**  
💡 ROUGE measures n-gram overlap between a generated summary and reference summaries. F1 is for classification, perplexity measures language-model confidence, FID scores generated images.

**Q33.** Metric for LLM summary quality  
✅ **C. Recall-Oriented Understudy for Gisting Evaluation (ROUGE)**  
💡 ROUGE is the standard summarization metric (overlap with reference summaries). Recall and AUC are classification metrics; MSE is regression.

**Q57.** Evaluate summaries for semantic similarity and coverage of key info (choose two) *(choose two)*  
✅ **B. BERTScore + E. Recall-Oriented Understudy for Gisting Evaluation (ROUGE)**  
💡 BERTScore compares contextual embeddings, so it captures meaning even with different wording. ROUGE measures how much of the reference content (n-grams) the summary covers. BLEU is precision-oriented and aimed at translation; F1/accuracy are classification metrics.

**Q79.** Metric for translation quality of summaries in multiple languages  
✅ **B. Bilingual evaluation understudy (BLEU)**  
💡 BLEU compares generated text with reference translations (n-gram precision), the classic translation metric. ROUGE targets summarization; AUC and precision are classification metrics.

**Q116.** Bedrock automatic evaluation metric for summarization accuracy  
✅ **C. BERTScore**  
💡 BERTScore measures semantic similarity to reference text, which Bedrock uses for accuracy on summarization. AUC/F1 are classification metrics; real-world knowledge (RWK) score applies to open-ended Q&A.

**Q134.** Measure whether rewritten text resembles provided readable example versions  
✅ **C. Recall-Oriented Understudy for Gisting Evaluation (ROUGE) score**  
💡 ROUGE compares generated text with reference texts by n-gram overlap. Loss and latency don't measure similarity to references.

**Q150.** Evaluate an FM's performance in real-world use  
✅ **A. Conducting A/B testing with users in a controlled environment**  
💡 A/B testing with real users measures actual behavior and outcomes in production-like conditions. Accuracy on training data is misleading (overfitting); SME review is offline.

**Q180.** Test a medical model against labeled radiology reports  
✅ **B. Domain-specific benchmark testing**  
💡 Domain-specific benchmark testing: evaluating against a labeled dataset from the target domain.

**Q205.** Evaluate accuracy of an image-classification FM  
✅ **B. Measure the model's accuracy against a predefined benchmark dataset.**  
💡 Measure accuracy on a predefined labeled benchmark dataset.

**Q209.** Compare output toxicity of several JumpStart LLMs with the least overhead  
✅ **B. Automatic model evaluation**  
💡 Automatic model evaluation (SageMaker Clarify FMEval / Bedrock evaluation) has built-in toxicity metrics. Human or crowd evaluation costs more effort; RLHF is a training technique.

**Q215.** Improve and evaluate a RAG assistant that gives incomplete/inaccurate answers  
✅ **D. Confirm that the retrieved documents are relevant and that the final answers are accurate.**  
💡 Evaluate both stages: retrieval (are the retrieved documents relevant?) and generation (is the final answer accurate/faithful?). Bedrock's RAG evaluation covers both. Looking only at final answers or at latency misses the root cause.

**Q222.** Have a team of scientists evaluate GenAI outputs  
✅ **C. Use model evaluation on Amazon Bedrock.**  
💡 Amazon Bedrock model evaluation supports human-based evaluation jobs with your own work team (as well as automatic evaluation).

**Q249.** Compare generated research summaries with human summaries  
✅ **C. Recall-Oriented Understudy for Gisling Evaluation (ROUGE)**  
💡 ROUGE measures overlap with human reference summaries. BLEU is for translation; accuracy/F1 for classification.

**Q257.** Did fine-tuning improve help-desk answer accuracy?  
✅ **C. F1 score**  
💡 F1 (often token-level F1 between generated and reference answers) balances precision and recall for Q&A accuracy. Time to first token is latency; word error rate is for speech recognition.

**Q280.** Metric used for summarization FMs  
✅ **A. F1 score**  
💡 ⚠ The dump's answer is F1, because ROUGE scores are reported as recall, precision and F1. If ROUGE is an option on the real exam, choose ROUGE. BLEU is for translation; MSE for regression.

**Q293.** Measure whether a teen chatbot uses creative spellings and abbreviations  
✅ **D. Bilingual Evaluation Understudy (BLEU) score**  
💡 BLEU checks exact n-gram matches with reference text, so it rewards reproducing the exact surface forms (slang spellings). BERTScore compares meaning and would ignore spelling style.

**Q309.** Evaluate LLM translations of training manuals  
✅ **A. Bilingual Evaluation Understudy (BLEU)**  
💡 BLEU is the standard machine-translation metric.

**Q360.** Choose a Bedrock model whose style employees prefer  
✅ **B. Evaluate the models by using a human workforce and custom prompt datasets.**  
💡 Human evaluation with your own workforce and custom prompts captures subjective preferences. Built-in datasets, leaderboards and latency don't measure your employees' taste.

**Q387.** Bedrock Knowledge Base evaluation metric for avoiding hallucination  
✅ **D. Faithfulness**  
💡 Faithfulness: is the response supported by the retrieved text? Harmfulness, stereotyping and refusal are responsible-AI metrics.

**Q400.** Match Bedrock evaluation job types to uses (hotspot) *(hotspot)*  
✅ **Built-in datasets → Automatic; SMEs → Human reviewers; Another model → Judge model**  
💡 Built-in benchmark datasets → automatic evaluation. SMEs scoring outputs → human-reviewer jobs. Another model scoring with explanations → LLM-as-a-judge jobs.

**Q431.** Compare a translation tool against human translations on the same documents  
✅ **B. Use the Bilingual Evaluation Understudy (BLEU) score to estimate the relative translation quality of the two methods.**  
💡 BLEU gives relative quality (comparing systems on the same references); it doesn't measure absolute translation quality.

**Q432.** Automatic metric for translations vs human references across languages  
✅ **B. Bilingual Evaluation Understudy (BLEU) score**  
💡 BLEU.

**Q443.** Measure whether retrieved policy documents apply to the question (retrieve-only RAG)  
✅ **B. Context relevance**  
💡 Context relevance scores how relevant retrieved passages are to the query. Faithfulness, correctness and completeness judge generated answers.

**Q463.** RAG must retrieve all relevant documents without missing any  
✅ **B. Recall**  
💡 Recall (retrieved relevant ÷ all relevant). Precision would measure how many retrieved documents are relevant; MRR measures ranking.

**Q473.** Evaluate and monitor accuracy and relevance of RAG-generated insights  
✅ **A. Review the model's outputs by using human evaluation and automated tools to measure the accuracy and relevance of the generated insights.**  
💡 Combine human evaluation with automated evaluation tools that score accuracy and relevance. Adding context, tuning parameters or watching latency doesn't measure quality.

**Q491.** Determine whether an FM meets business objectives  
✅ **C. Assess the model's alignment with specific use cases.**  
💡 Assess how well it fits the specific use cases (business-aligned evaluation). Benchmarks, architecture and compute are technical, not business, measures.

**Q496.** LLM-as-a-judge metric for how fully responses address every part of the prompt  
✅ **B. Completeness**  
💡 Completeness. "Following instructions" checks adherence to explicit instructions; refusal checks declined answers; ROUGE isn't a judge metric.

**Q526.** Built-in LLM-as-a-judge metric for survey summarization  
✅ **C. Faithfulness**  
💡 Faithfulness: is the summary consistent with and supported by the source text? Context relevance/coverage are RAG retrieval metrics; RMSE is regression.
