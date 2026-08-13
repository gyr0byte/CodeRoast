# CodeRoast 🔥 — Technical Documentation & Interview Preparation Guide

Welcome to the comprehensive technical documentation for **CodeRoast**. This document is structured as an in-depth technical manual and project interview preparation guide, detailing every algorithm, architecture, library, data engineering technique, and MLOps trade-off used in the system.

---

## 📌 1. Executive Summary & Problem Statement

### 1.1 Project Overview
**CodeRoast** is an end-to-end Machine Learning, Natural Language Processing (NLP), and Deep Learning system designed to evaluate source code quality and generate automated, humorously savage code reviews.

### 1.2 Motivation & Industry Relevance
Traditional static analysis tools (e.g., SonarQube, ESLint, Pylint) provide dry, mechanical diagnostic reports that developers often ignore. CodeRoast bridges the gap between **rigorous static analysis** and **engaging developer feedback** by converting AST metrics into entertaining, savage roasts powered by state-of-the-art Large Language Models (LLMs).

---

## 🏗️ 2. System Architecture & Component Interaction

CodeRoast follows a **decoupled, modular micro-architecture** consisting of five primary layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           1. UI & Presentation Layer                    │
│                 Streamlit Web App + Plotly Interactivity                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    2. Static Code Analysis Engine                       │
│        Python AST Parser + Multi-Language Regex (LOC, CC, Depth)       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  3. NLP & Deep Learning Scoring Layer                   │
│   ┌─────────────────────┬──────────────────────┬────────────────────┐   │
│   │ TF-IDF + Random     │  PyTorch Sequence    │ 🤗 CodeBERT        │   │
│   │ Forest Classifier   │  Bi-LSTM Model       │ Transformer Model  │   │
│   └─────────────────────┴──────────────────────┴────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                 4. Hybrid Roast Generation Engine                       │
│  🤗 HF Cloud Serverless API (0-RAM) <──fallback──> Local PyTorch / Temp │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                       5. MLOps & Cache Isolation                        │
│            D:\CodeRoast\models_cache\  (HF_HOME Storage Rules)         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 3. Machine Learning & Deep Learning Architectures

### 3.1 Model 1: TF-IDF + Random Forest Code Quality Classifier
- **Purpose:** Categorizes code snippet quality into 4 ordinal levels:
  - `0`: Pristine
  - `1`: Acceptable
  - `2`: Questionable
  - `3`: Disaster
- **Feature Extraction:** `TfidfVectorizer` (Max features: 1000, Sublinear TF scaling, n-gram range: (1, 2)).
- **Algorithm:** `RandomForestClassifier` (100 Decision Trees, Gini Impurity criterion, Max Depth: 15).
- **Memory Footprint:** 340 KB serialized (`models/classifier.pkl`). Runs in < 0.001s using < 1 MB RAM.
- **Mathematical Formula for TF-IDF:**
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

### 3.2 Model 2: PyTorch Stacked Bidirectional LSTM (`LSTMSeverityModel`)
- **Purpose:** Predicts a continuous severity score ($S \in [0, 10]$) based on sequential code token patterns.
- **Tokenizer (`CodeTokenizer`):** Custom code vocabulary builder converting source code into fixed-length integer token sequences ($N=200$).
- **Architecture Layers:**
  1. **Embedding Layer:** Vocabulary Size $V=5000$, Embedding Dimension $E=64$.
  2. **Stacked Bi-LSTM:** 2 Layers, Hidden Dimension $H=128$, Dropout rate $p=0.3$, Bidirectional ($2 \times H = 256$).
  3. **Fully Connected Layer 1:** Linear($256 \to 64$) + ReLU Activation.
  4. **Fully Connected Layer 2:** Linear($64 \to 1$) + Sigmoid scaling to range $[0, 10]$.
- **Loss Function & Optimizer:** Mean Squared Error (MSE Loss), Adam Optimizer ($\text{lr} = 0.001$).

### 3.3 Model 3: Hugging Face CodeBERT (`microsoft/codebert-base`)
- **Purpose:** Contextual sequence classification using a pre-trained transformer built on RoBERTa architecture.
- **Pre-training Domain:** Trained on CodeSearchNet dataset across 6 programming languages (Python, Java, JavaScript, PHP, Ruby, Go).
- **Architecture Specifications:** 12 Transformer Layers, 768 Hidden Dimension, 12 Attention Heads, 125M Parameters.
- **Classification Head:** `RobertaForSequenceClassification` with a custom linear projection head for severity score and quality tier regression.

### 3.4 Model 4: Hugging Face Cloud AI Engine (`Qwen/Qwen2.5-Coder-32B-Instruct`)
- **Purpose:** Generates dynamic, context-aware code roasts in natural language based on static metrics and severity.
- **Serverless Cloud Architecture:** Executes via Hugging Face Serverless Inference API, requiring **0 MB RAM** on Streamlit Cloud containers.
- **Fallback Architecture:** Local PyTorch execution (`Qwen/Qwen2.5-Coder-1.5B-Instruct`) with `low_cpu_mem_usage=True` and `bfloat16` precision when running locally.
- **Sampling Strategy:** Nucleus Sampling ($\text{top\_p} = 0.9$, Temperature $T = 0.85$, Max New Tokens $= 150$).

---

## 🔬 4. Static Code Analysis Algorithms

The static analyzer (`src/analyzer/code_analyzer.py`) computes structural metrics using Python's native `ast` module and regular expression heuristics for Java and JavaScript:

1. **Lines of Code (LOC):** Counts total lines, logical execution lines, blank lines, and comment lines.
2. **Cyclomatic Complexity ($V(G)$):**
   $$V(G) = E - N + 2P$$
   Where $E$ is edges, $N$ is nodes, and $P$ is connected components in the control flow graph. AST counts decision points (`if`, `while`, `for`, `except`, `with`, `assert`, boolean operators).
3. **Nesting Depth:** Max recursion depth calculated by traversing AST block structures (`If`, `For`, `While`, `Try`, `With`).
4. **Naming Score:** Evaluates variable and function identifier compliance against PEP8 / standard conventions (`snake_case` / `camelCase`) using regular expression matching.
5. **Code Duplication Score:** Computes hash similarity across sliding 4-line windows of source code to detect copy-pasted blocks.

---

## 🧰 5. Technology Stack & Dependencies

| Category | Technology / Library | Purpose in CodeRoast |
| :--- | :--- | :--- |
| **Language** | Python 3.10 / 3.14 | Core language runtime |
| **Frontend UI** | Streamlit, Plotly | Interactive web dashboard & charts |
| **Cloud Hosting** | Streamlit Cloud | Live application deployment |
| **Cloud AI API** | Hugging Face Serverless API | 0-RAM serverless LLM generation |
| **Deep Learning** | PyTorch (`torch`) | LSTM model architecture & tensor ops |
| **NLP Transformers** | Hugging Face (`transformers`, `huggingface_hub`) | CodeBERT & Qwen2.5-Coder LLM models |
| **Machine Learning** | Scikit-Learn | TF-IDF Vectorizer & Random Forest Classifier |
| **Static Analysis** | Python `ast`, Radon | Control flow graph & metric extraction |
| **Data Processing** | Pandas, NumPy | Dataset scraping, cleaning, and matrix math |

---

## 🎯 6. Technical Interview Q&A (Project Defense Guide)

### Q1: How does your application handle hardware constraints on free cloud hosting like Streamlit Cloud?
> **Answer:** Streamlit Cloud free containers enforce a strict **1 GB RAM limit**. To prevent Out-Of-Memory (OOM) crashes, we implemented a hybrid architecture:
> 1. **Zero-RAM Scoring:** Quality classification uses our pre-trained **Random Forest model (`classifier.pkl`, 340 KB)** which executes in < 0.001 seconds using < 1 MB RAM.
> 2. **Serverless Cloud AI:** Dynamic AI roasts utilize the **Hugging Face Serverless Inference API** (`Qwen/Qwen2.5-Coder-32B-Instruct`). The LLM runs on Hugging Face's cloud GPUs, consuming 0 MB memory on the Streamlit host.
> 3. **Local Fallback:** Heavy transformer weights (`CodeBERT`, local `Qwen2.5-Coder-1.5B`) are loaded lazily only when sufficient local system RAM is detected.

### Q2: Why did you choose CodeBERT over traditional n-gram models?
> **Answer:** Traditional n-gram TF-IDF models treat code as a "bag of words", ignoring structural semantics, variable scopes, and control flow. CodeBERT is pre-trained using Masked Language Modeling (MLM) and Replace Token Detection (RTD) on millions of code samples, allowing it to capture deep semantic patterns (e.g., detecting an inefficient $O(N^2)$ nested loop even if variable names are obfuscated).

### Q3: How did you optimize the 1.5B Parameter LLM for local machine execution?
> **Answer:** We implemented three key optimizations for local execution:
> 1. **Lazy Loading:** The LLM is only loaded into memory when the user toggles AI Roast mode.
> 2. **Precision Reduction:** We load model weights in `bfloat16`/`float16` precision, reducing memory consumption from ~6 GB (float32) down to ~2.2 GB.
> 3. **Memory Streaming:** We enable `low_cpu_mem_usage=True` in Hugging Face `from_pretrained`, which directly maps tensors without creating duplicate RAM buffers.

### Q4: How is data storage managed to avoid filling up the OS C: drive?
> **Answer:** By default, Hugging Face downloads weights to `~/.cache/huggingface` on the C: drive. In `config.py`, we programmatically override `os.environ["HF_HOME"] = "D:\\CodeRoast\\models_cache"`, ensuring all heavy transformer checkpoints remain isolated on the dedicated storage drive.

### Q5: How does the overall scoring algorithm compute the final letter grade?
> **Answer:** The overall score ($S_{\text{overall}} \in [0, 100]$) is calculated via a weighted linear combination of four sub-scores:
> $$S_{\text{overall}} = 0.35 \times S_{\text{efficiency}} + 0.25 \times S_{\text{structure}} + 0.25 \times S_{\text{readability}} + 0.15 \times S_{\text{creativity}}$$
> Letter grades are mapped using thresholds: **S (90+)**, **A (80–89)**, **B (70–79)**, **C (55–69)**, **D (40–54)**, and **F (<40)**.

---
*Created by gyr0byte for CodeRoast Technical Portfolio Defense.*
