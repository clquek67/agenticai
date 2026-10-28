# Domain 1 – Fundamentals of AI and ML

> Exam weight ≈ 20%. AI/ML terminology, learning types, the ML lifecycle, evaluation metrics and the AWS AI/ML services you can use off the shelf.

**134 questions** in this domain. [← Back to index](README.md)

## Topics

- [AI/ML concepts, learning types & algorithms](#aiml-concepts-learning-types--algorithms) (41 questions)
- [ML lifecycle, training & MLOps](#ml-lifecycle-training--mlops) (23 questions)
- [ML evaluation metrics](#ml-evaluation-metrics) (10 questions)
- [Data labeling & human annotation](#data-labeling--human-annotation) (4 questions)
- [Amazon SageMaker AI features](#amazon-sagemaker-ai-features) (29 questions)
- [AWS AI services (pre-trained, no ML expertise needed)](#aws-ai-services-pre-trained-no-ml-expertise-needed) (27 questions)

---

## AI/ML concepts, learning types & algorithms

### Key concepts

* **AI ⊃ ML ⊃ Deep learning.** AI = machines mimicking human problem solving; ML = learning patterns from data; DL = multi-layer neural networks.
* **Supervised** (labeled data): classification (binary = 2 classes, multiclass = many) and regression (numeric value). **Unsupervised** (no labels): clustering (k-means), anomaly detection (autoencoders, Random Cut Forest), dimensionality reduction (PCA). **Reinforcement learning**: an agent learns from rewards by trial and error.
* **k-NN** = supervised classifier (nearest labeled neighbors). **K-means** = unsupervised clustering. Don't mix them up.
* **Interpretable models**: linear/logistic regression (coefficients) and decision trees (rules). Neural networks are black boxes.
* **Data types**: structured/tabular (rows and columns), unstructured (text, images, audio, video), time series (values over time → forecasting, e.g. DeepAR), labeled vs unlabeled.
* **Fields**: NLP (text: sentiment, classification, NER), computer vision (images: detection, defects), speech (Transcribe/Polly).
* **When not to use ML:** deterministic math (probabilities, image rotation) is better done with plain code.

### Questions (41)

**Q3.** Classify genes into 20 categories and document how the model's internals drive the output  
✅ **A. Decision trees**  
💡 Decision trees are white-box models: each split is a readable rule. Neural networks are black boxes; linear/logistic regression are interpretable but linear regression predicts numbers and logistic regression is mainly binary.

**Q44.** Pick ML approach per use case: CLV, churn likelihood, customer grouping (hotspot) *(hotspot)*  
✅ **CLV → Regression; Churn → Classification; Grouping → Clustering**  
💡 Lifetime value is a continuous number → regression. Will/won't churn is a category → classification. Grouping without labels → clustering (unsupervised).

**Q64.** Data type for predicting internet disruptions from speed measurements during the day  
✅ **C. Time series data**  
💡 Measurements indexed by time are time-series data, the right input for spotting daily patterns and forecasting.

**Q69.** Match AI, ML, deep learning to descriptions (hotspot) *(hotspot)*  
✅ **Human problem solving → AI; Data-driven predictions → ML; Neural networks → Deep learning**  
💡 AI is the broadest field (mimicking human problem solving); ML is a subset that learns from data to predict; deep learning is a subset of ML using multi-layer neural networks.

**Q77.** Chatbot that improves itself from interactions and feedback  
✅ **B. Reinforcement learning with rewards for positive customer feedback**  
💡 Reinforcement learning learns from rewards (e.g. positive customer feedback) over time. Supervised learning needs fixed labeled sets; unsupervised clustering doesn't improve responses.

**Q89.** App for visually impaired users that hears speech and answers by voice  
✅ **A. Use a deep learning neural network to perform speech recognition.**  
💡 Speech recognition is done by deep-learning neural networks (e.g. Amazon Transcribe; Polly for voice output). Numeric pattern search and image classification don't process speech.

**Q101.** Automatically group similar customers and products  
✅ **A. Unsupervised learning**  
💡 Grouping without predefined labels is clustering, i.e. unsupervised learning.

**Q107.** Petabytes of unlabeled data; group customers into tiers  
✅ **B. Unsupervised learning**  
💡 No labels → unsupervised learning (clustering) to find natural segments.

**Q118.** Interpretable model for loan risk  
✅ **B. Logistic regression model**  
💡 Logistic regression gives clear coefficients per feature and is a classic interpretable binary classifier. Deep learning is a black box; k-means and Random Cut Forest are unsupervised.

**Q119.** Classify flowers from petal/sepal measurements (Iris)  
✅ **A. K-nearest neighbors (k-NN)**  
💡 k-NN is a supervised classifier that labels a point by its nearest neighbors. K-means clusters without labels; ARIMA forecasts time series; linear regression predicts numbers.

**Q126.** Decide whether reviews are positive, negative or neutral  
✅ **D. Classification**  
💡 Sentiment with fixed labels is a (multi-class) classification task.

**Q130.** Sentiment analysis is a subset of which field  
✅ **C. Natural language processing (NLP)**  
💡 Natural language processing (NLP).

**Q141.** Technique that trains on data labeled with correct outputs  
✅ **A. Supervised learning**  
💡 Supervised learning learns the mapping from inputs to known labels.

**Q154.** Large labeled image dataset for animal classification  
✅ **A. Supervised learning**  
💡 Labeled data → supervised learning. Active learning is about choosing which new data to label, which they won't do.

**Q163.** Data type for demand forecasting with SageMaker DeepAR  
✅ **C. Time series data**  
💡 DeepAR is a recurrent-neural-network forecasting algorithm for time-series data.

**Q168.** Group customers by purchase history and preferences  
✅ **B. Clustering**  
💡 Clustering (unsupervised).

**Q182.** Detect abnormal sensor patterns with no labels  
✅ **D. Autoencoders**  
💡 Autoencoders learn to reconstruct normal data; high reconstruction error signals an anomaly (unsupervised). Classification/regression need labels.

**Q200.** Lead-scoring model whose variable weights employees can view and adjust  
✅ **A. Logistic regression model**  
💡 Logistic regression has one readable coefficient (weight) per feature that domain experts can inspect and tweak. Neural nets, PCA-based models and k-NN have no adjustable per-feature weights.

**Q201.** Model type that makes numeric predictions  
✅ **B. Regression**  
💡 Regression predicts continuous numeric values. Diffusion and transformers are architectures; multimodal describes data types.

**Q212.** AI that inspects products for damage or defects  
✅ **C. Computer vision**  
💡 Computer vision: interpreting images/video (e.g. Amazon Lookout for Vision, Rekognition Custom Labels).

**Q227.** Automatically identify and categorize animals in photos  
✅ **A. Object detection**  
💡 Object detection locates and labels objects in images (e.g. Rekognition labels). NER is for text; inpainting fills in image regions.

**Q282.** Match data formats to descriptions (hotspot) *(hotspot)*  
✅ **Not annotated → Unlabeled; Predefined schema → Structured; Grid of rows/fields → Tabular**  
💡 Raw data without annotations/targets = unlabeled. Data following a schema = structured. Rows-and-columns grid = tabular.

**Q310.** Detect whether an IP address is from a suspicious source  
✅ **C. Develop an anomaly detection system.**  
💡 Anomaly detection flags behavior that deviates from normal patterns. NER and speech recognition are unrelated; forecasting predicts future values.

**Q336.** Group customers by demographics and buying patterns  
✅ **B. K-means**  
💡 K-means clustering (unsupervised). k-NN, decision trees and SVMs are supervised.

**Q337.** Rotate and transpose images, most efficiently  
✅ **B. Create an AWS Lambda function to perform the transformations.**  
💡 These are deterministic math operations; a simple Lambda function (e.g. with an image library) does them without ML. Don't use AI when plain code solves the problem.

**Q371.** Supervised vs unsupervised per technique (hotspot) *(hotspot)*  
✅ **Binary → Supervised; Multi-class → Supervised; K-means → Unsupervised; Dimensionality reduction → Unsupervised**  
💡 Classification (binary or multi-class) needs labels → supervised. K-means and dimensionality reduction (PCA) need no labels → unsupervised.

**Q377.** Detect subtle surface defects in product images  
✅ **B. Computer vision**  
💡 Computer vision (e.g. defect detection/anomaly detection on images).

**Q379.** Example of unsupervised learning  
✅ **A. Clustering data points into groups based on their similarity**  
💡 Clustering by similarity. Image recognition and price prediction are supervised; text generation is generative (self-supervised).

**Q384.** Best use case for binary classification  
✅ **C. Detecting spam emails**  
💡 Spam vs not spam has exactly two classes. Pricing is regression; recommendations and marketing segmentation aren't binary.

**Q394.** Match ML technologies to datasets (hotspot) *(hotspot)*  
✅ **Reviews → NLP; Animal images → Computer vision; Daily sales → Time series forecasting**  
💡 Text reviews → NLP; labeled animal images → computer vision; daily sales volumes → time-series forecasting.

**Q402.** Example of unsupervised learning  
✅ **A. A model that groups customers based on their purchase history**  
💡 Grouping customers by purchase history (clustering). Dogs vs cats and house prices are supervised; chess by trial and error is reinforcement learning.

**Q412.** Educational game computing simple marble probabilities  
✅ **C. Use code that will calculate probability by using simple rules and computations.**  
💡 Basic arithmetic rules in code; ML would be unnecessary, costly and less accurate. Don't use ML for deterministic calculations.

**Q442.** Predict heart disease with features and a known target label  
✅ **B. Supervised learning**  
💡 Labeled target → supervised learning (binary classification).

**Q479.** Group customers by demographics and buying patterns  
✅ **B. K-means**  
💡 K-means clustering.

**Q487.** Classify free-text feedback into categories  
✅ **B. Natural language processing (NLP)**  
💡 NLP (text classification).

**Q505.** Example of structured data  
✅ **C. A CSV file that consists of measurement data**  
💡 A CSV of measurements (rows and columns with a schema). Forum text, videos and transcripts are unstructured.

**Q515.** Image classification on a custom dataset with the least effort  
✅ **B. Use a pre-trained deep learning model. Fine-tune the model on the dataset.**  
💡 Transfer learning: fine-tune a pre-trained deep-learning vision model. Hand-built features, SVMs or GANs take more work.

**Q518.** Match data types to use cases (hotspot) *(hotspot)*  
✅ **Sentiment → Text; Traffic signs → Image; Ad campaigns → Tabular; Stock prices → Time series**  
💡 Social posts → text; traffic signs → images; demographics and purchase history → tabular; historical prices → time series.

**Q522.** Match ML techniques to tasks (hotspot) *(hotspot)*  
✅ **Answer correct? → Binary; Number of species → Regression; Car model → Multiclass**  
💡 Correct/incorrect → binary classification; species count (a number) → regression; car model (many classes) → multiclass classification.

**Q532.** Label each card transaction fraudulent or not  
✅ **C. Binary classification**  
💡 Binary classification.

**Q533.** Find culture-growth regions in images with no labels  
✅ **C. Clustering**  
💡 Clustering (unsupervised grouping of similar pixels/regions, i.e. segmentation without labels).

---

## ML lifecycle, training & MLOps

### Key concepts

* **Lifecycle:** business goal → frame the ML problem → collect data → **EDA** (statistics, correlation, visuals) → **preprocess** (clean/filter) → **feature engineering** (create/select inputs) → train → tune → **evaluate** → deploy → **monitor** → retrain.
* **Labeling** = attaching the target value to records. **Inference** = using a trained model on new data.
* **Overfitting** = great on training data, poor on new data → more/varied data, more regularization, fewer epochs, simpler model. **Underfitting** = poor on both → more features/complexity/training.
* **Epochs** = passes over the training data; more epochs can raise accuracy (until overfitting).
* **Pre-training** = training from random weights on huge unlabeled data. Compliance/data rules shape what data you may collect.
* **MLOps**: automation, infrastructure as code (repeatable, consistent environments), versioning, continuous monitoring in production.

### Questions (23)

**Q21.** Order the ML lifecycle steps (hotspot) *(hotspot)*  
✅ **Prepare data → Train → Test → Deploy**  
💡 Data must exist and be clean before training; a trained model is evaluated before it is put into production.

**Q38.** Raise model accuracy up to a target level during training  
✅ **B. Increase the epochs.**  
💡 More epochs (full passes over the data) let the model keep learning until it reaches the target; watch for overfitting. Temperature is an inference setting.

**Q45.** Tag transaction records as "personal" or "business"  
✅ **B. Data labeling**  
💡 Attaching the target category to each record is data labeling. Encoding converts categories to numbers; normalization rescales values; balancing evens out class counts.

**Q53.** GenAI lifecycle stage that tests accuracy  
✅ **D. Evaluation**  
💡 The evaluation stage runs tests and benchmarks against held-out data before deployment.

**Q74.** Order the lifecycle for a new custom model (hotspot) *(hotspot)*  
✅ **Define business objective → Process data → Develop and train → Deploy**  
💡 Every ML project starts with the business problem, then data collection/processing, then model development/training, then deployment (followed by monitoring).

**Q143.** Which task is inference in a readmission-prediction scenario  
✅ **D. Use a trained model to predict patient readmission.**  
💡 Inference = using the trained model on new data to make predictions. Gathering data, finding patterns and evaluating are earlier lifecycle steps.

**Q155.** Use feature engineering for house-price prediction  
✅ **C. Create or select relevant features for model training.**  
💡 Feature engineering = creating, transforming and selecting the input variables most useful for prediction. Hyperparameter tuning and data collection are different steps.

**Q160.** Dataset to train an assistant for a specific content area  
✅ **A. Diverse conversations that use relevant terminology**  
💡 Diverse conversations that use the domain's terminology. Sales time series, news sentiment and ID pairs don't teach domain dialogue.

**Q165.** Lifecycle phase that determines compliance and regulatory requirements  
✅ **C. Data collection**  
💡 The dump's answer is data collection: that is when you decide which data you may legally collect and use (privacy, consent, residency). Some sources place it under business goal identification, so read the question carefully.

**Q231.** What happens in the deployment phase  
✅ **C. Makes the model available in a live environment for end users to access**  
💡 The model is made available in production for users/applications. Choosing data and retraining belong to other phases.

**Q237.** Randomly initialize weights, train on massive web data with a language-modeling objective  
✅ **B. Pre-training**  
💡 That's pre-training: building the base FM from scratch on large unlabeled data.

**Q251.** A deployed object-detection model analyzes a new image  
✅ **B. Inference**  
💡 Inference: using a trained model on new data.

**Q272.** Model great on training data, much worse in production  
✅ **C. Increase the volume of data that is used in training.**  
💡 That's overfitting / poor generalization. More (and more varied) training data helps the model generalize. Training longer usually makes overfitting worse.

**Q273.** Good on training data, poor on evaluation data  
✅ **D. The model is overfit.**  
💡 Overfitting: the model memorized training noise. Underfitting would be poor on both.

**Q295.** Churn model good on training data, poor on new data  
✅ **B. Increase the regularization parameter to decrease model complexity.**  
💡 Overfitting → increase regularization to reduce complexity. More features or epochs make overfitting worse.

**Q300.** Meaning of inference  
✅ **B. The use of a trained model to make predictions or decisions on unseen data**  
💡 Using a trained model to make predictions on new, unseen data.

**Q408.** Order the well-architected ML workload steps (hotspot) *(hotspot)*  
✅ **Define business goal → Develop → Deploy → Monitor**  
💡 Business goal/problem framing → develop (data, train, evaluate) → deploy → monitor.

**Q424.** Filtering patient voice recordings by duration and language  
✅ **B. Data preprocessing**  
💡 Data preprocessing (cleaning/filtering the collected data). Collection already happened; feature engineering creates model inputs.

**Q447.** Benefit of infrastructure as code in MLOps  
✅ **C. IaC streamlines the deployment of scalable and consistent ML workloads in cloud environments.**  
💡 Repeatable, versioned, consistent and scalable deployment of ML environments. It doesn't replace tuning or guarantee cheap/powerful instances.

**Q449.** Next step after collecting data  
✅ **C. Data preprocessing**  
💡 Data preprocessing (cleaning, handling missing values, transforming). Tuning and evaluation come after training.

**Q472.** Scenario showing overfitting  
✅ **A. A stock prediction model decreases in accuracy after testing on new data.**  
💡 Accuracy drops on new data after doing well in training. The other options describe too few features or too little data (underfitting/bias).

**Q484.** MLOps best practice with an open-source pre-trained sentiment model  
✅ **C. Continuously monitor outputs in production.**  
💡 Continuously monitor outputs in production to catch drift and degradation. Labeling or tuning isn't required for a pre-trained model.

**Q512.** Correlation matrix, statistics and visualizations on new data  
✅ **C. Exploratory data analysis**  
💡 Exploratory data analysis (EDA), done before preprocessing and feature engineering.

---

## ML evaluation metrics

### Key concepts

| Metric | Use |
|---|---|
| **Accuracy** | correct ÷ total. Misleading on imbalanced data |
| **Precision** = TP/(TP+FP) | When false positives are costly (wasted fraud reviews) |
| **Recall** = TP/(TP+FN) | When missing positives is costly (missed disease, missed documents) |
| **F1** | Harmonic mean of precision and recall; best single metric for imbalanced binary classification |
| **Confusion matrix** | Full breakdown of TP/FP/TN/FN for classifiers |
| **AUC-ROC** | Classifier ranking quality across thresholds |
| **MSE / RMSE / R²** | Regression only |
| **Average response time / latency** | Runtime efficiency |

### Questions (10)

**Q4.** Measure how many plant-disease images were classified correctly  
✅ **B. Accuracy**  
💡 Accuracy = correct predictions / all predictions, the natural metric for classification. R-squared and RMSE are regression metrics; learning rate is a hyperparameter, not a metric.

**Q13.** Metric for a binary churn-prediction classifier  
✅ **A. F1 score**  
💡 F1 balances precision and recall, ideal for binary classification (especially imbalanced). MSE and R-squared are regression metrics; training time isn't a quality metric.

**Q157.** Metric = correctly classified items ÷ all classified items  
✅ **A. Accuracy**  
💡 That is the definition of accuracy. Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 = harmonic mean of precision and recall.

**Q198.** Imbalanced classes; measure the balance between detecting and labeling correctly  
✅ **D. F1 score**  
💡 F1 (harmonic mean of precision and recall) is robust to class imbalance; accuracy can be misleading when one class dominates.

**Q244.** 5% buyers; model is 95% accurate but rarely finds buyers  
✅ **B. F1 score**  
💡 Accuracy is misleading on imbalanced data (predicting "no" every time scores 95%). F1 combines precision and recall for the minority class.

**Q296.** Evaluate a production churn classifier against actual behavior  
✅ **C. F1 score**  
💡 F1 (precision + recall) for a binary classifier. RMSE is regression; ROI is business; BLEU is translation.

**Q316.** Measure a deep-learning image material classifier  
✅ **A. Confusion matrix**  
💡 A confusion matrix shows TP/FP/TN/FN per class. Correlation matrix analyzes features; R2/MSE are regression metrics.

**Q327.** What F1 measures  
✅ **A. Model precision and recall**  
💡 The harmonic mean of precision and recall.

**Q331.** Minimize time reviewing flagged transactions that aren't fraud  
✅ **C. Precision**  
💡 Precision = TP/(TP+FP); high precision means few false positives. Recall would minimize missed fraud instead.

**Q420.** Metric for runtime efficiency of AI models  
✅ **C. Average response time**  
💡 Average response time (latency). Training metrics and CSAT don't measure runtime efficiency.

---

## Data labeling & human annotation

### Key concepts

* **SageMaker Ground Truth**: you build labeling jobs and choose a workforce (Amazon Mechanical Turk for public/non-sensitive data, private team, or vendors). Supports active learning to auto-label.
* **SageMaker Ground Truth Plus**: fully managed. AWS supplies an expert workforce and workflow; no labeling apps or workforce to manage.
* **Amazon A2I** (Augmented AI): human *review of predictions* (e.g. low confidence), unlike Ground Truth, which *labels training data*.

### Questions (4)

**Q22.** Generate eyewear images with high accuracy and minimal incorrect annotations  
✅ **A. Human-in-the-loop validation by using Amazon SageMaker Ground Truth Plus**  
💡 SageMaker Ground Truth Plus is a managed labeling service with expert human reviewers (human-in-the-loop), giving high-quality annotations. The others don't validate labels.

**Q46.** Get labeled samples from mostly unlabeled, non-confidential transaction data (choose two) *(choose two)*  
✅ **C. Use an Amazon SageMaker Ground Truth labeling job with Amazon Mechanical Turk workers. + E. Run an Amazon SageMaker AI labeling job.**  
💡 SageMaker Ground Truth labeling jobs (human workers such as the public Amazon Mechanical Turk workforce, fine for non-confidential data) produce labels. Batch inference and distributed training don't create ground-truth labels; OCR is for reading text in images.

**Q243.** Human-feedback labeling without building apps or managing a workforce  
✅ **B. Amazon SageMaker Ground Truth Plus**  
💡 SageMaker Ground Truth Plus is fully managed: AWS provides the expert workforce and workflow. Data Wrangler prepares data; Macie finds PII.

**Q369.** User-friendly labeling interface for custom computer-vision models  
✅ **A. Amazon SageMaker Ground Truth**  
💡 SageMaker Ground Truth provides labeling UIs and workflows (bounding boxes, segmentation) with human labelers.

---

## Amazon SageMaker AI features

### Key concepts

| Feature | What it is for |
|---|---|
| **Canvas** | No-code ML (build, predict, forecast) for business users |
| **Data Wrangler** | Low-code data preparation |
| **Feature Store** | Central, shareable store of ML features |
| **JumpStart** | Hub of pre-trained/foundation models, solution templates, notebooks; one-click deploy/fine-tune; admins can curate which models are visible |
| **Clarify** | Bias detection (pre- and post-training) + explainability (SHAP); FM evaluation |
| **Model Monitor** | Detects data/model-quality/bias/feature-attribution drift in production; alerts |
| **Model Registry** | Version, catalog and approve models |
| **Model Cards** | Document intended use, risks, metrics (governance) |
| **Ground Truth** | Data labeling |
| **Automatic Model Tuning / Autopilot** | Automated hyperparameter tuning / AutoML |
| **Unified Studio** | One collaborative environment for data + AI (incl. Bedrock) |

**Inference options:** real-time (low latency, persistent endpoint) · serverless (no infrastructure, scales to zero, intermittent traffic) · asynchronous (payloads up to 1 GB, up to 1 h processing, near real-time) · batch transform (large offline datasets on a schedule, no endpoint).

### Questions (29)

**Q68.** Deploy a price-prediction model without managing servers  
✅ **D. Deploy the model by using an Amazon SageMaker endpoint.**  
💡 SageMaker endpoints (including serverless inference) are fully managed hosting. EC2/EKS require managing infrastructure; CloudFront + S3 serves static content.

**Q98.** Fine-tune an open-source LLM for text categorization with the least effort  
✅ **B. Use Amazon SageMaker JumpStart to create a training job.**  
💡 SageMaker JumpStart offers pre-built fine-tuning for open models with a few clicks/lines. Custom scripts or EC2 notebooks take more work; PartyRock is a no-code playground, not a training service.

**Q127.** Quickly deploy and use an FM inside the team's VPC  
✅ **B. Amazon SageMaker JumpStart**  
💡 SageMaker JumpStart deploys pre-trained FMs to endpoints in your VPC with a few clicks. A raw SageMaker endpoint needs you to bring and package the model.

**Q131.** Gigabytes of data daily; predictions needed once a day  
✅ **A. Batch inference**  
💡 Batch inference (Batch Transform) processes large datasets on a schedule with no always-on endpoint. Real-time is for low-latency single requests; async is for large single payloads.

**Q175.** Pick inference mode per use case (hotspot) *(hotspot)*  
✅ **Chatbot intent → Real-time; Weekend GB of files → Batch transform; Low-latency API → Real-time**  
💡 Interactive, low-latency needs → real-time endpoints. Scheduled processing of large files → batch transform.

**Q193.** Inference quality degraded after 4 months; want alerts and to prevent a repeat  
✅ **B. Retrain the model. Monitor model drift by using Amazon SageMaker Model Monitor.**  
💡 Retrain on fresh data and use SageMaker Model Monitor to detect data/model-quality drift and alert (via CloudWatch). Clarify focuses on bias/explainability; Feature Store and JumpStart don't monitor.

**Q196.** Food-waste/sales model that must keep getting more accurate  
✅ **A. Use Amazon SageMaker AI and iterate with the most recent data.**  
💡 Use SageMaker AI to retrain iteratively on the most recent data (continuous improvement / MLOps). Personalize is for recommendations; CloudWatch and Rekognition don't train models.

**Q242.** Long-running production model gives inconsistent responses; evaluate bias and drift  
✅ **A. Amazon SageMaker Model Monitor**  
💡 SageMaker Model Monitor watches production for data-quality drift, model-quality drift, bias drift and feature-attribution drift (it uses Clarify under the hood). Clarify alone is for point-in-time analysis.

**Q266.** Detect changes in model quality across many models  
✅ **D. Amazon SageMaker Model Monitor**  
💡 SageMaker Model Monitor compares production behavior with a baseline and alerts on quality drift.

**Q276.** Model Monitor shows data drift beyond threshold  
✅ **C. Re-train the model with fresh data.**  
💡 Retrain with fresh data that reflects the new distribution. Restarting the endpoint or changing sensitivity hides the problem.

**Q281.** 1 GB payloads, up to 1 hour processing, near real-time  
✅ **C. Asynchronous inference**  
💡 Asynchronous inference queues requests and supports payloads up to 1 GB and up to 1 hour of processing. Real-time is limited to small payloads and 60 s; serverless is also small and short; batch is not near real-time.

**Q291.** Deploy a custom recommendation model and watch for quality drift  
✅ **D. Amazon SageMaker Model Monitor**  
💡 SageMaker Model Monitor detects model-quality drift in production. Clarify explains/finds bias; Rekognition and Comprehend are pre-built AI services.

**Q307.** Store, manage and version many ML models  
✅ **C. Amazon SageMaker Model Registry**  
💡 SageMaker Model Registry catalogs model versions, metadata and approval status for deployment.

**Q322.** Alerts when production model performance drifts  
✅ **B. Amazon SageMaker Model Monitor**  
💡 SageMaker Model Monitor with CloudWatch alerts. A2I is human review; Trusted Advisor gives best-practice checks.

**Q323.** No-code demand forecasting on internal and external data  
✅ **D. Import the data into Amazon SageMaker Canvas. Build ML models and demand forecast predictions by selecting the values in the data from SageMaker Canvas.**  
💡 SageMaker Canvas is a point-and-click, no-code ML tool (including forecasting). Built-in algorithms need code; Personalize is for recommendations.

**Q326.** Match SageMaker features to uses (hotspot) *(hotspot)*  
✅ **Choose suitable model → Model Cards; Low-code data prep → Data Wrangler; Find bias → Clarify**  
💡 Model Cards summarize model details to help choose a model; Data Wrangler = low-/no-code data prep; Clarify = bias/imbalance detection.

**Q351.** Monthly, not time-sensitive inference without persistent endpoints  
✅ **C. Batch transform**  
💡 Batch transform spins up compute for the job and shuts down after; cheapest for periodic offline workloads.

**Q361.** Inference on multi-GB archived datasets; results not needed immediately  
✅ **A. Batch transform**  
💡 Batch transform. Async is for individual large requests; real-time/serverless are for immediate responses.

**Q375.** Match SageMaker features to uses (hotspot) *(hotspot)*  
✅ **No-code data prep → Canvas; Prebuilt fraud solution → JumpStart; Human labeling → Ground Truth**  
💡 Canvas = visual, no-code data prep and ML; JumpStart = pre-built solutions (e.g. fraud detection templates) and models; Ground Truth = human labeling.

**Q385.** Advantage of a pre-trained model over a custom one  
✅ **C. Faster time to deployment**  
💡 Faster time to deployment. Custom models give more control and possibly higher task accuracy.

**Q434.** Host an image-classification model for a web app without managing infrastructure  
✅ **A. Use Amazon SageMaker Serverless Inference to deploy the model.**  
💡 SageMaker Serverless Inference auto-provisions and scales compute (scales to zero). CloudFront/API Gateway can't host models; AWS Batch is for batch jobs.

**Q437.** Match SageMaker resources to lifecycle steps (hotspot) *(hotspot)*  
✅ **Versioning → Model Registry; Predictions → Serverless Inference**  
💡 Model versions → SageMaker Model Registry. Using the current model for predictions → an inference option such as Serverless Inference.

**Q438.** One collaborative environment for data and AI development  
✅ **B. Amazon SageMaker Unified Studio**  
💡 Amazon SageMaker Unified Studio brings data, analytics, ML and GenAI (Bedrock) development together with shared, governed projects.

**Q450.** Monthly trend reports on a month of collected patient data, most cost-effectively  
✅ **B. Batch transform**  
💡 Batch transform processes the whole dataset offline on a schedule, with no idle endpoint.

**Q451.** Pre-trained FMs, solution templates and example notebooks to deploy and fine-tune quickly  
✅ **B. Amazon SageMaker JumpStart**  
💡 SageMaker JumpStart. The Bedrock model catalog gives serverless FMs but not solution templates/notebooks; Canvas is no-code ML.

**Q486.** Satisfaction prediction model with fully automated tuning  
✅ **B. Amazon SageMaker AI**  
💡 SageMaker AI Automatic Model Tuning (hyperparameter optimization) / Autopilot.

**Q516.** Predict employee attrition without code or ML knowledge  
✅ **A. SageMaker Canvas**  
💡 SageMaker Canvas (no-code ML).

**Q525.** Share and manage features (variables) across teams  
✅ **A. Amazon SageMaker Feature Store**  
💡 SageMaker Feature Store: a central repository of features for training and inference, shared across teams.

**Q530.** Build and deploy ML models without code  
✅ **A. Amazon SageMaker Canvas**  
💡 SageMaker Canvas.

---

## AWS AI services (pre-trained, no ML expertise needed)

### Key concepts

| Need | Service |
|---|---|
| Text from scanned docs/PDFs/forms | **Textract** |
| NLP: sentiment, entities, PII, toxicity in text | **Comprehend** (medical text → **Comprehend Medical**) |
| Speech → text, subtitles, call analytics | **Transcribe** (clinical notes → **AWS HealthScribe**) |
| Text → speech | **Polly** |
| Translation | **Translate** |
| Image/video analysis, content moderation | **Rekognition** |
| Chatbots (voice/text intents) | **Lex** |
| Intelligent enterprise search | **Kendra** |
| Recommendations / personalized ranking | **Personalize** |
| Graph data (fraud rings) | **Neptune** |
| GenAI assistant over company data | **Amazon Q Business** |
| GenAI coding assistant (code, tests, docs, AWS help) | **Amazon Q Developer** |
| GenAI BI dashboards & executive summaries | **Amazon Q in QuickSight** |

### Questions (27)

**Q18.** Extract info from patient records and create concise summaries  
✅ **A. Use Amazon Comprehend Medical to extract relevant medical entities and relationships. Apply rule-based logic to structure and format summaries.**  
💡 Amazon Comprehend Medical extracts medical entities (conditions, medications, tests) and relationships from text. Personalize = recommendations, Textract = OCR, Kendra = search.

**Q56.** Service that builds BI reports and auto-generates executive summaries  
✅ **A. Amazon Q in QuickSight**  
💡 Amazon Q in QuickSight adds generative BI: natural-language questions, dashboards and executive summaries. Rekognition = images, Textract = documents, Polly = speech.

**Q94.** Convert PDF resumes to plain text automatically  
✅ **A. Amazon Textract**  
💡 Amazon Textract extracts text, forms and tables from documents and PDFs (OCR+). Transcribe is for audio; Lex is chatbots; Personalize is recommendations.

**Q109.** Find harmful language in comments without labeled training data  
✅ **B. Use Amazon SageMaker AI built-in algorithms to train the model.**  
💡 ⚠ The dump's key (B, SageMaker AI built-in algorithms) is weak: training a model normally needs labels, and B and C are effectively the same option. In practice the best fit is Amazon Comprehend's pre-trained toxicity detection, which isn't offered. For the exam remember: harmful/toxic text → Comprehend; harmful images/video → Rekognition content moderation.

**Q122.** GenAI speech-to-text to help clinicians dictate clinical notes  
✅ **D. AWS HealthScribe**  
💡 AWS HealthScribe transcribes clinical conversations and generates clinical notes with generative AI (HIPAA-eligible). Polly is text-to-speech.

**Q151.** AI assistant for employees to query internal data  
✅ **D. Amazon Q Business**  
💡 Amazon Q Business is a managed GenAI assistant that connects to company data sources with access controls. Lex builds bots but needs you to wire up the data and LLM yourself.

**Q164.** Add multilingual subtitles and voice-overs to films (choose two) *(choose two)*  
✅ **A. Use Amazon Transcribe and Amazon Translate to generate subtitles in other languages. + C. Use Amazon Polly to generate voice-overs in other languages.**  
💡 Transcribe (speech → text) + Translate (text → other languages) produce subtitles; Polly (text → speech) produces voice-overs. Textract reads documents, not audio; Translate doesn't produce audio.

**Q166.** How Amazon Q Developer boosts developer productivity  
✅ **A. Create software snippets, reference tracking, and open source license tracking.**  
💡 Q Developer generates code, tracks references to open-source code it was trained on and flags licenses, and scans code for security issues. Serverless execution is Lambda; speech-to-text is Transcribe.

**Q171.** Use case for intelligent document processing (IDP)  
✅ **D. Automatically extract and format data from scanned files**  
💡 IDP automatically extracts and structures data from scanned documents (e.g. Textract + Comprehend + A2I).

**Q191.** GenAI that writes code for software tests, with the least effort  
✅ **C. Amazon Q Developer**  
💡 Amazon Q Developer is the managed coding assistant (code, unit tests, reviews, upgrades). Q Business is for enterprise knowledge; building a Bedrock agent takes more work.

**Q224.** Personalized search results for each e-commerce user  
✅ **A. Amazon Personalize**  
💡 Amazon Personalize provides real-time personalized ranking and recommendations. Kendra is enterprise search but not per-user personalization.

**Q230.** Determine sentiment from written reviews (choose two) *(choose two)*  
✅ **B. Amazon Comprehend + D. Amazon Bedrock**  
💡 Amazon Comprehend has built-in sentiment analysis; an LLM on Bedrock can also classify sentiment. Lex = chatbots, Polly = speech, Rekognition = images.

**Q245.** Extract text from millions of PDFs in S3, summarize and index (choose two) *(choose two)*  
✅ **B. Amazon Bedrock + E. Amazon Textract**  
💡 Textract extracts text from PDFs; Bedrock FMs summarize. Translate, Transcribe and Polly handle language/audio, not documents.

**Q246.** Graph-based ML tool for fraud investigations  
✅ **C. Amazon Neptune**  
💡 Amazon Neptune is a graph database with Neptune ML (graph neural networks) for relationship-based fraud patterns.

**Q255.** Auto-generate graphs of top-selling products over 12 months  
✅ **C. Amazon Q in Amazon QuickSight**  
💡 Amazon Q in QuickSight builds visuals and dashboards from natural-language questions.

**Q264.** Use an FM to cut time spent writing application code  
✅ **A. Use Amazon Q Developer to generate real-time inline code suggestions.**  
💡 Amazon Q Developer gives real-time inline code suggestions in the IDE. CodeGuru does code review/profiling; Knowledge Bases and Personalize don't suggest code.

**Q267.** Help a team with little AWS Glue experience build a solution  
✅ **A. Amazon Q Developer**  
💡 Amazon Q Developer explains services, generates code (including Glue ETL scripts), and guides you through AWS tasks.

**Q286.** Provide subtitles for animated content  
✅ **C. Amazon Transcribe**  
💡 Amazon Transcribe converts speech to time-stamped text (it can generate subtitle files). Translate only translates text; Polly is text-to-speech.

**Q348.** Generate real-time code and unit tests to ship faster  
✅ **B. Amazon Q Developer**  
💡 Amazon Q Developer.

**Q358.** Quickly create test cases and documentation for code  
✅ **C. Use Amazon Q Developer in an integrated development environment (IDE).**  
💡 Amazon Q Developer in the IDE generates tests and docs. Uploading code to unknown online tools is a security risk.

**Q406.** Analyze and extract key information from call audio  
✅ **B. Transcribe call recordings by using Amazon Transcribe.**  
💡 Amazon Transcribe converts recordings to text (Transcribe Call Analytics adds sentiment, issues, summaries). Comprehend works on text that already exists.

**Q414.** Publish English articles in other languages  
✅ **B. Use the Amazon Translate real-time translation feature.**  
💡 Amazon Translate (neural machine translation, real-time and batch).

**Q422.** Create product descriptions in multiple languages  
✅ **A. Amazon Translate**  
💡 Amazon Translate automates translating the descriptions.

**Q433.** Extract structured and unstructured data from scanned PDFs and forms  
✅ **D. Amazon Textract**  
💡 Amazon Textract (text, forms, tables, handwriting).

**Q489.** Movie recommendations from account history  
✅ **D. Amazon Personalize**  
💡 Amazon Personalize.

**Q493.** Enterprise search over large volumes of education materials  
✅ **C. Amazon Kendra**  
💡 Amazon Kendra: ML-powered intelligent enterprise search with natural-language queries.

**Q499.** Restrict Amazon Q Business to company-approved topics  
✅ **C. Amazon Q Business application guardrails**  
💡 Amazon Q Business application guardrails (global controls and topic-specific rules). Indexes hold data; cross-account access shares it.
