# Domain 2 – Fundamentals of Generative AI

> Exam weight ≈ 24%. Tokens, embeddings, transformers and diffusion, what GenAI is good and bad at, and how to measure its business value.

**48 questions** in this domain. [← Back to index](README.md)

## Topics

- [GenAI core concepts](#genai-core-concepts) (27 questions)
- [GenAI use cases & business value](#genai-use-cases--business-value) (21 questions)

---

## GenAI core concepts

### Key concepts

* **Token** = unit of text the model reads/writes (word, subword, character). Pricing and limits are in tokens.
* **Context window** = max tokens per request. Inputs beyond it fail or get truncated.
* **Embedding** = numeric vector capturing meaning; similar meaning → nearby vectors (cosine similarity).
* **Transformers** use **self-attention** (parallel, context-aware) and power LLMs. **Diffusion** models generate images by iterative denoising. **GANs** generate synthetic data. **BERT** = masked-word prediction (fill in blanks). **Multimodal** = several data types (text, image, audio, video).
* **Limitations:** **hallucination** (plausible but false), **nondeterminism** (same prompt → different output), bias/toxicity, IP/plagiarism, cost, interpretability.
* LLMs are **stateless**: multi-turn chat works by resending conversation history in the prompt.

### Questions (27)

**Q20.** What tokenization is used for in NLP  
✅ **C. To break text into smaller units for processing**  
💡 Tokenization splits text into units (words, subwords, characters) that the model processes. It is not encryption, compression or translation.

**Q24.** Summarizer fails on some books  
✅ **D. The input tokens exceed the model’s context size.**  
💡 Each model has a maximum context window (input tokens). Long books exceed it, so the request fails or gets truncated; chunk the text or pick a model with a larger context window.

**Q37.** Same prompt gives different answers, sometimes with false facts (choose two) *(choose two)*  
✅ **B. Nondeterminism + C. Hallucination**  
💡 Different outputs for the same input = nondeterminism (sampling). False information stated confidently = hallucination.

**Q92.** Multi-turn Bedrock chatbot must use earlier customer messages  
✅ **B. Add messages to the model prompt.**  
💡 LLMs are stateless; you pass the conversation history in the prompt (e.g. the messages list in the Converse API). Invocation logging only records calls; Provisioned Throughput only buys capacity.

**Q99.** Generative AI use case for multimodal models  
✅ **D. Process different data types, such as images, audio, and video.**  
💡 Multimodal models process (and/or generate) several data types (text, images, audio, video) in one model.

**Q108.** What tokens are  
✅ **A. Tokens are the basic units of input and output that a generative AI model operates on, representing words, subwords, or other linguistic units.**  
💡 Tokens are the basic units of input/output (words, subwords, characters). Embeddings are the numeric vectors; weights are parameters; prompts are instructions.

**Q113.** Model with limited training data gives plausible but wrong answers  
✅ **C. Hallucinations**  
💡 That's hallucination: confident, fluent output that isn't factually supported.

**Q142.** Disadvantage of GenAI in production  
✅ **D. Hallucinations and inaccuracies**  
💡 Hallucinations and inaccuracies. GenAI is non-deterministic and compute-hungry, so "deterministic" and "negligible compute" are false.

**Q170.** GenAI app produces incorrect information  
✅ **D. Hallucination**  
💡 Hallucination. Drift = data/concept changes over time; data leakage = training data leaking into test sets or outputs.

**Q181.** Suggest words to fill in missing text  
✅ **D. BERT-based models**  
💡 BERT is trained with masked-language modeling (predicting hidden words using context on both sides), exactly this task.

**Q187.** Same input gives different outputs during testing  
✅ **A. The LLM is acting in a nondeterministic way.**  
💡 LLMs are nondeterministic because tokens are sampled (temperature, top-p).

**Q213.** Marketing content sounds factual but is wrong  
✅ **B. Hallucination**  
💡 Hallucination. Overfitting/underfitting are training issues for predictive models.

**Q221.** Characteristic of transformer models  
✅ **C. Transformer-based language models use self-attention mechanisms to capture contextual relationships.**  
💡 Self-attention captures relationships between all tokens in parallel. Convolutions are CNNs; one-element-at-a-time loops are RNNs; transformers also handle images and audio.

**Q225.** Purpose of vector embeddings  
✅ **C. Providing the ability to mathematically compare texts**  
💡 Embeddings turn text into numeric vectors so semantic similarity can be computed mathematically (e.g. cosine similarity). Splitting text = chunking/tokenization; word counts = bag of words.

**Q263.** GenAI produces output unrelated to the input or task  
✅ **B. Hallucinations**  
💡 Hallucinations.

**Q268.** Match model types to ad-content tasks (hotspot) *(hotspot)*  
✅ **Images → Diffusion; Slogans → Transformer; Brand placement → Object detection**  
💡 Diffusion models generate high-quality images; transformers generate text (slogans); object detection verifies where brand elements appear.

**Q269.** What embeddings are  
✅ **D. A numerical method for data representation in a reduced dimensionality space**  
💡 Numerical vector representations of data in a (relatively) low-dimensional space that preserve semantic meaning.

**Q271.** Numeric representations of real-world objects and concepts  
✅ **A. Embeddings**  
💡 Embeddings.

**Q290.** Generate thousands of consistent product-description paragraphs daily  
✅ **B. A transformer-based model**  
💡 Transformer-based LLMs generate coherent text at scale. Diffusion and GANs mainly generate images; VAEs are used for compression/generation of simpler data.

**Q353.** Automatically complete partial sentences in records  
✅ **A. Use a large language model (LLM) trained on data from the records.**  
💡 An LLM trained (or fine-tuned) on the records' text predicts the next words: text completion. Vision, k-NN and RL don't fit.

**Q392.** Model may present convincing but wrong financial facts  
✅ **B. Possibility of generating plausible-sounding but potentially false information**  
💡 That's the hallucination limitation: plausible-sounding but false output.

**Q403.** Different responses for the same input across calls  
✅ **B. Nondeterminism**  
💡 Nondeterminism.

**Q411.** Real-time speech-to-speech agent (audio in, audio out)  
✅ **C. Transformer-based**  
💡 Transformer-based speech models (e.g. Amazon Nova Sonic) handle streaming audio sequences. Diffusion is for images; encoder-/decoder-only are sub-types, not the best overall answer.

**Q425.** Correct description of embeddings  
✅ **A. Embeddings represent data as high-dimensional vectors that capture semantic relationships.**  
💡 High-dimensional vectors that capture semantic relationships. B describes search/RAG, C describes quantization, D describes a vector database.

**Q465.** Product descriptions sometimes contain incorrect information  
✅ **B. Hallucinations**  
💡 Hallucinations.

**Q494.** Generate synthetic data based on existing data  
✅ **A. Generative adversarial network (GAN)**  
💡 GANs (generator vs discriminator) produce realistic synthetic samples. XGBoost is gradient-boosted trees; ResNet classifies images; WaveNet generates audio.

**Q511.** AI-produced budget contains incorrect numbers  
✅ **A. Hallucinations**  
💡 Hallucinations: confident but wrong output.

---

## GenAI use cases & business value

### Key concepts

* Good fits: summarization, content/code generation, chatbots/assistants, text-to-SQL, image/video generation, multi-turn conversation.
* Not GenAI: forecasting, classification, clustering, rule-based recommenders, dashboards (traditional ML/analytics).
* **Advantages:** adaptability (handles new inputs without rewriting rules), speed to value with prebuilt assistants.
* **Business metrics:** conversion rate (sales impact), average order value, click-through rate (engagement), retention rate, average call duration / handle time (agent effort), cost per conversation (financial impact), first-contact resolution.

### Questions (21)

**Q2.** LLM app that reads legal documents and pulls out the key points  
✅ **C. Develop a summarization chatbot.**  
💡 Extracting key points from long text is summarization. NER only tags entities (names, dates); recommendation and translation are different tasks.

**Q26.** Shopping assistant must understand follow-up questions phrased differently  
✅ **A. Generates context-aware replies during multi-turn conversations**  
💡 GenAI keeps conversational context across multiple turns. It doesn't guarantee identical answers, can't be accurate without product data, and doesn't remove the need for human review.

**Q88.** Practical use case for generative AI  
✅ **B. Employing a chatbot to provide human-like responses to customer queries in real time**  
💡 A chatbot that creates human-like replies generates new content. Demand forecasting is classic ML, dashboards are analytics, rule-based engines aren't ML.

**Q91.** Support system must keep working as products and policies change, without being rebuilt  
✅ **B. Adaptability to incorporate updated information**  
💡 Adaptability: the system can take in updated information (e.g. via RAG over refreshed sources) without rebuilding the model.

**Q100.** Produce code from natural-language comments  
✅ **B. Text generation**  
💡 That's text generation: the model generates new text (code) from a prompt. Completion only continues existing text; summarization and classification don't create code.

**Q114.** GenAI for marketing that must increase revenue within 6 months  
✅ **C. Implement a prebuilt AI assistant solution and measure its impact on customer satisfaction.**  
💡 A prebuilt AI assistant delivers value quickly and lets you measure impact; training a custom FM takes too long. Interviews and benchmarking are useful but don't produce results within 6 months.

**Q144.** Extract key insights from large policy documents  
✅ **C. Summarization**  
💡 Summarization condenses long documents into key points. Regression, clustering and classification don't generate text.

**Q220.** Concise overview of medication reviews  
✅ **B. Create medication review summaries by using Amazon Bedrock large language models (LLMs).**  
💡 Summarization with an LLM on Amazon Bedrock. Rekognition = images; Personalize = recommendations; classification doesn't create overviews.

**Q236.** Measure the assistant's direct impact on sales  
✅ **A. The conversion rate of customers who purchase products after AI assistant interactions**  
💡 Conversion rate after assistant interactions ties directly to revenue. Interaction counts and sentiment are indirect; NLU accuracy is a technical metric.

**Q248.** Match business metrics to recommendation goals (hotspot) *(hotspot)*  
✅ **Engagement → CTR; Purchase value → AOV; Returning users → Retention rate**  
💡 CTR = engagement with recommendations; AOV = value of purchases; retention rate = users coming back.

**Q334.** Order steps to automate product-database updates from text+image guides (hotspot) *(hotspot)*  
✅ **Upload to S3 → Process with Nova multimodal → Insert into database**  
💡 Files must land in storage first, then a multimodal model extracts the information, then results are written to the database.

**Q338.** Analyze sentiment of large volumes of unstructured text feedback  
✅ **A. Use a large language model (LLM) to perform natural language processing (NLP) for sentiment analysis.**  
💡 An LLM (or NLP service such as Comprehend) classifies sentiment. Regression, recommenders and time series don't fit.

**Q405.** Business metric for reducing agent effort during calls  
✅ **B. Average call duration**  
💡 Average call duration (handle time) directly reflects agent effort per call. First-contact resolution relates more to customer outcomes; attrition and web engagement are indirect.

**Q419.** Non-technical staff turn natural-language text into SQL queries  
✅ **A. Generative pre-trained transformers (GPT)**  
💡 Generative pre-trained transformers (LLMs) do text-to-SQL generation. ResNet = images; SVM = classification; WaveNet = audio generation.

**Q439.** Measure recommendation impact on sales revenue  
✅ **D. Conversion rate**  
💡 Conversion rate (recommendations → purchases).

**Q467.** Business objective to evaluate fewer agent actions per question  
✅ **B. Average call duration**  
💡 Average call duration falls as agents need fewer steps.

**Q481.** Which task uses generative AI  
✅ **A. Summarizing customer complaints**  
💡 Summarizing complaints generates new text. Classification, segmentation and forecasting are traditional ML.

**Q498.** Replace complex hard-coded complaint logic to scale across markets  
✅ **B. Adaptability**  
💡 Adaptability: GenAI generalizes to new products, languages and formats without rewriting rules. GenAI is less predictable and less explainable, not more.

**Q502.** Measure the chatbot's financial effect on operations  
✅ **C. Cost for each customer conversation**  
💡 Cost per customer conversation (compare with human-handled cost). Inquiry counts and AHT are operational; training cost is one-off.

**Q534.** A generative AI use case  
✅ **B. Creating photorealistic images from text descriptions for digital marketing**  
💡 Creating photorealistic images from text for marketing. Intrusion detection, indexing and forecasting aren't generative.

**Q535.** Use AI to boost software development productivity  
✅ **D. Use a natural language processing (NLP) tool to generate code.**  
💡 Use an NLP/GenAI tool (e.g. Amazon Q Developer) that generates code from natural language. Binary classifiers can't write reviews; "code forecasting" isn't a real technique.
