# CodeRoast 🔥 — Deep Technical Documentation & Architecture Manual

## 📝 Section 1 — Project Overview

### 1.1 Plain English Project Statement
**CodeRoast** is a developer productivity tool disguised as a comedy assistant. In plain terms, it is an automated code review application that analyzes programming files (Python, Java, and JavaScript), extracts quality metrics, runs them through deep learning and statistical machine learning pipelines, and delivers a brutally honest, highly sarcastic critique (a "roast") of the developer's code.

### 1.2 The Problem: Dry, Ignored Diagnostics
Traditional static analysis tools—such as **SonarQube**, **ESLint**, **Pylint**, or **Checkstyle**—produce dry, clinical, and mechanical reports. They present developers with walls of warning codes (`PEP8`, `complexity thresholds`, etc.) that are frequently ignored or disabled in configuration files. 

By failing to make code review engaging, teams build up technical debt. CodeRoast solves this psychological barrier by using **gamified feedback**. It translates mechanical code metrics into memorable humor, ensuring developers actually remember the rule (e.g., nesting too deep or not writing docstrings) because it was delivered with comedic timing.

### 1.3 The Creative Angle
CodeRoast operates on a simple premise: **humor drives adherence**. The application converts static code characteristics into structured jokes using three severity tiers:
*   **Gentle Nudge (Severity 1):** Playful, peer-level review with supportive comments.
*   **Standard Roast (Severity 2):** Dry, sarcastic senior developer critiques using common tropes.
*   **No Mercy (Severity 3):** Savage, unfiltered roasts comparing the user's code to software disasters.

### 1.4 Technical Complexity & Non-Trivial Nature
Behind the humorous facade lies a complex, multi-model AI pipeline. CodeRoast is not a simple wrapper around an LLM API. It features:
1.  An **Abstract Syntax Tree (AST) Parser** that performs static metrics extraction.
2.  A **Hybrid NLP Classifier (Random Forest)** combining character-level TF-IDF representations with AST metrics to predict quality tiers.
3.  A **PyTorch Sequence LSTM Scorer** that tokenizes code text and projects sequential complexity into a continuous severity score.
4.  A fine-tuned **microsoft/codebert-base** model for deep semantic understanding.
5.  A local GPU **Meta Llama 3.2 3B** engine (via Ollama) paired with a 4-tier cloud **Google Gemini Flash** fallback chain.

This tiered system ensures robust, sub-second generation times, failing back gracefully from local GPU models to cloud APIs down to static templates if network connectivity or compute limits are reached.

```
+------------------------------------------------------------+
|                       Source Code                          |
+------------------------------------------------------------+
                              |
       +----------------------+----------------------+
       |                                             |
       v                                             v
+--------------+                             +---------------+
|  AST Parser  |                             | Tokenization  |
+--------------+                             +---------------+
       |                                             |
       | (Metrics: CC, Nesting, etc.)                | (Token Sequences)
       v                                             v
+-----------------------------+              +---------------+
| Random Forest Classifier    |              | PyTorch LSTM  |
|   (TF-IDF + Static Metrics) |              | Severity      |
+-----------------------------+              +---------------+
       |                                             |
       v (Quality Level: 0-3)                        v (Severity: 0-1)
       +----------------------+----------------------+
                              |
                              v
                +----------------------------+
                |   Llama 3.2 3B / Gemini    |
                |   (With Fallback Chains)   |
                +----------------------------+
                              |
                              v
                    [ Animated UI Roast ]
```

---

## 🏗️ Section 2 — Complete System Architecture

### 2.1 Static Analysis Engine
The static analysis engine is implemented in `src/analyzer/code_analyzer.py`. It is responsible for parsing code text and extracting a set of 8 key metrics.

#### Python AST Parsing
For Python, the engine uses Python's native `ast` module to build an **Abstract Syntax Tree (AST)**. This provides a formal, nested representation of the program logic, allowing accurate identification of class, function, variable, and control flow nodes.

*   **Lines of Code (LOC):** A simple count of lines in the file.
*   **Function Count:** Calculated by counting the occurrences of `ast.FunctionDef` and `ast.AsyncFunctionDef` nodes during a depth-first traversal (`ast.walk`) of the tree.
*   **Average Function Length:** Tracks method line ranges by comparing `node.lineno` to the maximum `end_lineno` of any child node inside the function body.
*   **Cyclomatic Complexity:** Measures the number of linearly independent paths through the code. Calculated using the formula:
    $$M = E - V + 2P$$
    where $E$ is edges, $V$ is vertices, and $P$ is connected components. CodeRoast leverages the `radon` complexity library to parse Python functions. If `radon` is missing, it falls back to counting branch keywords (`if`, `elif`, `for`, `while`, etc.).
*   **Nesting Depth:** Represents the deepest level of nested blocks. The parser calculates this by evaluating the leading whitespace indentation of each line (4 spaces = 1 level).
*   **Comment Ratio:** Formulated as:
    $$\text{Ratio} = \frac{\text{Comment Lines + Docstring Lines}}{\text{Total Lines}}$$
    Extracted using `tokenize.generate_tokens` to detect `tokenize.COMMENT` tokens and multi-line string literals (`"""` or `'''`) representing docstrings.
*   **Naming Convention Score (0-100):** Traverses the AST looking for function definitions, variable assignments (`ast.Name` store context), and class names. Function and variable names must match snake_case patterns:
    $$\text{Pattern} = \text{\texttt{^[a-z\_][a-z0-9\_]*\$}}$$
    Class names must be PascalCase. Violations deduct 10 points for functions/classes and 5 points for variables.
*   **Code Duplication Score (0-100):** Scans the code using a 3-line sliding window. It hashes each window and calculates duplicate occurrences. The score decreases linearly as duplicate ratios rise:
    $$\text{Score} = \max(0, 100 - (\text{Duplication Ratio} \times 200))$$

#### Multi-Language Support
For non-Python languages (Java and JavaScript), building a full compiler-grade AST parser in a lightweight Python environment is highly resource-intensive. CodeRoast addresses this by using **regex-based heuristic extractors**:
*   **Java:** Access modifier/return pattern searches extract methods and estimate complexity by brace matching `{` and `}` counts.
*   **JavaScript:** Detects functions via arrow `=>` signatures, `function` blocks, and object method keypairs.

#### Edge Cases
When syntax errors prevent AST parsing (e.g., unfinished code blocks), the engine sets a `_syntax_error` flag, bypassing further model classification and immediately selecting custom syntax-error templates to tease the user about failing basic compiler checks.

---

### 2.2 NLP Quality Classifier (Random Forest)
The classifier (`src/ml/classifier.py`) categorizes snippets into four distinct quality tiers.

#### Feature Engineering
To capture both structural metrics and stylistic/vocabulary choices, CodeRoast implements a hybrid feature extractor. It vectorizes the raw text of the code using **TF-IDF (Term Frequency-Inverse Document Frequency)** and horizontal-stacks the resulting matrix with the normalized 8 static metrics vector.

#### TF-IDF Parameter Choices
*   **Analyzer:** `char_wb` (character n-grams inside word boundaries). Character n-grams are vastly superior to word-level n-grams for source code because variable names, casing styles, and operator groupings (like `i++` or `!=`) don't correspond to dictionary words.
*   **N-gram Range:** `(2, 4)`. A window of 2 to 4 characters successfully captures syntax idioms (e.g., `def `, `for(`, `std::`, `public void`).
*   **Max Features:** Capped at `5000` to prevent feature-space explosion and contain container memory use.

#### The 4 Quality Tiers
1.  **Pristine (0):** Exceptionally structured, docstring-complete, and clean. Very rare.
2.  **Acceptable (1):** Average code showing minor issues but readable.
3.  **Concerning (2):** Spaghetti attributes, bad naming conventions, lack of structure.
4.  **Disaster (3):** Deeply nested, duplicated copy-paste blocks, or syntax failures.

#### Model Decision: Random Forest
We chose a **Random Forest Classifier** with 100 estimators and a `max_depth` of 20. It was selected over neural networks or gradient boosting (XGBoost) for this stage because:
*   It requires zero feature scaling.
*   It is less prone to overfitting on a small dataset (~600 samples).
*   It provides sub-millisecond local inference, keeping the initial Streamlit page load instant.
*   It supports lazy load serialization via `joblib`.

---

### 2.3 PyTorch Sequence LSTM Severity Scorer
The LSTM severity scorer (`src/ml/lstm_model.py`) predicts a continuous scale of "roast deservedness" (0.0 to 1.0) based on sequential code tokens.

#### LSTM Architecture
The model uses a stacked recurrent structure built in PyTorch:
```
           [Input Token Sequence]
                     |
            [Embedding Layer (64)]
                     |
            [LSTM Layer 1 (128)]
                     |
            [Dropout (p=0.3)]
                     |
            [LSTM Layer 2 (64)]
                     |
            [Dropout (p=0.3)]
                     |
        [Dense / Linear Layer (32)]
                     |
                 [ReLU]
                     |
        [Dense / Linear Layer (1)]
                     |
                [Sigmoid]
                     |
            [Severity Score (0-1)]
```

#### Tokenization Approach
The custom `CodeTokenizer` filters out redundant whitespace while preserving syntax keywords and operator combinations using regex-based extraction:
$$\text{Regex} = \text{\texttt{[a-zA-Z\_]\textbackslash w*|[0-9]+\textbackslash.?[0-9]*|[^\textbackslash s\textbackslash w]}}$$
It builds a vocabulary capped at `5000` tokens and pads all inputs to a fixed length of `200`.

#### Sequence Modeling Rationale
While static analysis extracts global properties (like the number of comments or cyclomatic complexity), it ignores the **ordering of statements**. For example, nesting 4 loops sequentially is much better than nesting them inside each other (deep nesting). An LSTM processes the code token-by-token, preserving sequential order and context through hidden state updates.

---

### 2.4 Hugging Face CodeBERT (`microsoft/codebert-base`)
For advanced semantic evaluation, the application includes a loader for **CodeBERT**—a bimodal model pre-trained on natural language and programming languages across 6 programming languages.

#### Usage Pattern
CodeBERT is used for sequence classification (`AutoModelForSequenceClassification`). 
*   **Representation:** We map the final classification layer output (`num_labels=4`) to our quality tiers.
*   **Expected Severity Score:** Computed as the weighted average of the softmax probabilities across the four buckets:
    $$\text{Severity} = \sum_{i=0}^3 P(\text{class}_i) \times W_i$$
    where $W = [0.0, 0.33, 0.66, 1.0]$.
*   **Semantic Capabilities:** While AST and LSTMs detect superficial indentation patterns and keywords, CodeBERT captures deep semantics (e.g., SQL injection vulnerabilities, deadlocks, bad exception handling, and logical redundancy).
*   **OOM Prevention:** In serverless environments, CodeBERT's base parameters consume ~500 MB of RAM. To avoid Out-of-Memory crashes on free-tier hosting (like Streamlit Cloud), CodeBERT is **lazy-loaded** and only initialized if fine-tuned weights exist locally on the D: drive.

---

### 2.5 Dual-Engine LLM Roast Architecture

The roast generation pipeline (`src/roast/llm_generator.py`) operates a **dual-engine architecture** tailored for high speed, daily scale (~4,500+ requests/day), and dynamic cultural creativity across both **English** and **Romanized Nepali**.

#### 1. 🇳🇵 Romanized Nepali Engine: Google Gemini Multi-Model Fallback Chain
For Romanized Nepali roasts, CodeRoast executes a 4-tier Google Gemini model priority chain to bypass individual model rate limits (`429`) and server overload (`503`):

$$\text{gemini-2.5-flash} \longrightarrow \text{gemini-flash-lite-latest} \longrightarrow \text{gemini-3.5-flash-lite} \longrightarrow \text{gemini-3.1-flash-lite}$$

*   **Instant Error Circuit Breaker:** Catches HTTP `429` (Quota Exceeded) and `503` (Service Unavailable) immediately, skipping to the next model in sub-100ms.
*   **Short Response Rejection:** Enforces a minimum character length check. Any AI output under 100 characters is rejected as "lazy", automatically triggering model switching.
*   **Sub-4-Second Speed:** Lite models reduce generation latency from 40–60s down to **~3.7 seconds per roast**.

#### Dynamic Theme Picker Architecture (420+ Unique Combinations)
#### 1. 🇳🇵 Romanized Nepali Engine: 4-Tier Gemini Chain & Dynamic Theme System
To eliminate prompt repetition and deliver maximum variety, every Nepali request dynamically samples and stitches together:
*   **12 Persona Tones:** *Frustrated 2am Senior Dev*, *Sarcastic Uncle at Dashain*, *Kathmandu Twitter Troll*, *LOD Standup Comic*, *Gaming Streamer*, *TU Exam Invigilator*, *Microbus Conductor*, *Nagdhunga Traffic Cop*, *RONB Admin*, *Balen Shah Assistant*, *Thamel Tour Guide*, *Momo Pasal Owner*.
*   **20 Cultural Theme Pools:** *Kathmandu Traffic & Scooters*, *Nepalese Politics & Feud*, *Student Struggles & TU Exam Delays*, *Nepalese Food & Cuisine*, *Balen Shah Dozer Culture*, *Nepalese Sports & Rajesh Hamal*, *Daily Life / Pathao / Nagdhunga*, *Internet / RONB / Meme Nepal*, *Loadshedding Nostalgia*, *Loksewa Aspirants*, *Widebody Scam*, *Bheda Charaune*, *Bhatbhateni Billing*, *Australian Visa Waiting*, *Prachanda Speeches*, *Dashain Tika Chaos*, *Nagarkot Sunset*, *NTC 3G Speed*, *Kusum Silk Saree*, *Ratnapark Bus Park*.
*   **8 Roast Structural Templates:** *Cricket Commentary*, *RONB News Bulletins*, *Autopsy Reports*, *Courtroom Sentencing*, *Momo Order Receipts*, *Movie Trailers*, *Dashain Blessings*, *Jira Ticket Escalations*.
*   **7 Signature Closers & Clean Authentic Nepali Slangs:** Rotates natural developer slangs (`kukur`, `gadha`, `dimag navako`, `harami`, `khate`, `pakhe`, `bheda`, `hawa`, `lafada`, `pasa`, `kaathe`, `jhyaap`, `boka`, `gidi`, `chappar`, `tori`, `baal xaina`, `hait`). Strictly excludes explicit sexual profanities.
*   **Resulting Variety:** **15,000+ unique Romanized Nepali roast combinations**.

#### 2. 🇬🇧 English Engine: Local Meta Llama 3.2 3B & Multi-Dimensional Theme System
For English roasts, the engine applies the same multi-dimensional theme picker architecture:
*   **12 English Cultural Theme Pools:** Silicon Valley failures (Theranos/Juicero/WeWork), Stack Overflow elitism, r/programminghorror cursed code, FAANG interview disasters, Cyberpunk 2077 bugs, Fyre Festival/Season 8 betrayals, enterprise Jira hell, ChatGPT hallucinations, Startup hustle delusion, Linus Torvalds PR flames, Friday deploy apocalypses, and Y2K/Ariane 5 rocket crashes.
*   **10 Persona Tones:** Burnt-out FAANG Staff Engineer, Gordon Ramsay in a server room, Reddit Moderator, VC Evaluator, Drunk CS Professor at 2am, LeetCode Hard ELITE, Paged DevOps Engineer, Sarcastic British Tech Journalist, Open Source Maintainer, Sentient AI.
*   **6 Roast Structures & 6 Signature Closers:** Yielding **15,000+ unique English roast variations**.
*   **Local Ollama Auto-Detection:** Queries `http://localhost:11434/api/chat` running **Llama 3.2 3B** (with 100% GPU VRAM offload on NVIDIA GTX 1060 6GB).
*   **Multi-Tier Cloud Fallback:** If Ollama is offline, queries Hugging Face Serverless API (`Qwen2.5-Coder-32B` $\rightarrow$ `7B` $\rightarrow$ `1.5B` $\rightarrow$ `0.5B`).

#### 3. 🎁 Easter Egg Engine
Before LLM generation or static templates run, `generator._detect_easter_egg()` scans the raw code string for famous developer tropes:
*   `Hello World`: Triggers a classic roast mocking beginner effort.
*   `FizzBuzz`: Mocks corporate whiteboard interview rituals.
*   `Empty Code`: Mocks submitting blank space.
*   `TODO / pass` stubs: Mocks submitting unwritten placeholders.

#### 4. 🖼️ Authentic Classic Impact Font Meme Engine
Powered by PIL and 100+ downloaded classic meme templates in `assets/memes/`:
*   **Dynamic Template Pool (`MEME_CATALOG`)**: Organizes 25+ templates and punchlines into flaw categories (`mismatch`, `nesting`, `complexity`, `spaghetti`, `praise`, `disaster`). Every roast dynamically selects a new template and caption combination.
*   **Visual Zone Alignment**: Calculates template-specific coordinate offsets (`top_y`, `bottom_y`) so Impact font text renders precisely inside target visual areas (e.g., green highway exit signs, Drake right panels, speech bubbles).

#### 5. 🔊 Web Speech API Voice Player
Provides browser-native text-to-speech rendering via `window.speechSynthesis`. Users can listen to roasts read aloud with interactive play/stop controls without incurring local CPU/RAM server overhead.

#### 6. 📜 Enforced 75+ Word Roast Length & Strict Safety Filters
*   **Length Enforcement**: All AI prompts and fallback loop logic in `_finalize()` enforce a **75 to 120-word minimum length** for detailed, unhinged rants.
*   **Automated Content Filters**: Combines strict negative prompt system rules with regex post-processing in `_ensure_profane_unhinged_roast()` to filter out banned terms (`randikhola`, `randi`) while preserving dark developer satire.

#### Code Metrics Injection
Static code metrics are dynamically injected alongside the snippet to ensure technical context:
```
Language: Python
Lines of Code: 12
Cyclomatic Complexity: 4
Nesting Depth: 3
Comment Ratio: 0.0%

Code Snippet:
[User's raw code here]
```

#### Robust Fallback Hierarchy
$$\text{Easter Eggs} \longrightarrow \text{Local Qwen / Gemini Chain} \longrightarrow \text{HF Cloud Qwen Multi-Tier} \longrightarrow \text{Rule-Based Templates (75+ Words)}$$

---


### 2.6 Scoring Engine
The scoring logic in `src/scoring/scorer.py` aggregates raw AST metrics into four dimensional scores (0 to 100).

| Score Dimension | Metric Input | Formula / Rule |
| :--- | :--- | :--- |
| **Readability** | Naming, Comments, Avg Length | $40\% \text{ naming} + 30\% \min(\text{comment\_ratio} \times 500, 100) + 30\% \max(0, 100 - \text{avg\_function\_length})$ |
| **Efficiency** | Cyclomatic Complexity | $\max(0, \min(100, 100 - (\text{cyclomatic\_complexity} \times 5)))$ |
| **Structure** | Nesting Depth, Duplication | $50\% \max(0, 100 - (\text{nesting\_depth} \times 10)) + 50\% \text{ duplicate\_code\_score}$ |
| **Creativity** | Function Count | $\min(\text{function\_count} \times 10, 100)$ |

The final score is the arithmetic mean of these dimensions:
$$\text{Overall Score} = \frac{\text{Readability} + \text{Efficiency} + \text{Structure} + \text{Creativity}}{4}$$

#### Grade Mapping & Randomized Unhinged Reactions
Each letter grade triggers one of **8 randomized unhinged reaction messages**:
*   **S:** $\ge 90$ — Suspiciously Good *(8 reactions, e.g., "Are you a compiler in disguise?")*
*   **A:** $\ge 75$ — Actually Decent *(8 reactions, e.g., "Your tech lead might actually approve your PR.")*
*   **B:** $\ge 60$ — Barely Acceptable *(8 reactions, e.g., "It works, but so does a duct-taped pipe.")*
*   **C:** $\ge 45$ — Concerning *(8 reactions, e.g., "Passes like a kidney stone—painfully and with much screaming.")*
*   **D:** $\ge 30$ — Deeply Troubling *(8 reactions, e.g., "Nesting so deep it requires an OSHA permit for cave exploration.")*
*   **F:** $< 30$ — Please Seek Help *(8 reactions, e.g., "Format drive D:\, throw your keyboard into the ocean, and try goat herding.")*

---

### 2.7 Streamlit Frontend
The UI uses custom dark CSS stylesheets to create a premium, gamified developer dashboard.
*   **Radar Chart:** Built using `plotly.graph_objects.Scatterpolar`. It displays the 4 dimensional scores (Readability, Efficiency, Structure, Creativity), allowing developers to visually diagnose the weak points of their code structure.
*   **Interactive Components:** A slider changes roast severity, while a checkbox enables local/cloud AI generation.
*   **UI Badges:** Visual feedback tags identify the source of the roast—displaying an **`🤖 Senior Dev AI Verdict`** card for AI-generated roasts and fallback reaction metadata.

---

## 📈 Section 3 — Data Pipeline

### 3.1 GitHub Scraping Strategy
Training data was gathered using a dedicated scraping utility (`data/scrape_github.py`). We targeted a balanced distribution of high-quality and low-quality code repositories across Python, Java, and JavaScript.

#### Repositories Targeted
*   **High-Star Repositories:** Star counts $> 500$, actively maintained. (e.g., standard libraries, popular frameworks).
*   **Low-Star Repositories:** Star counts $< 5$, inactive or archived prior to 2022. (e.g., abandoned student homework projects, draft gists).

### 3.2 Dataset Statistics
The dataset contains a balanced set of samples across target languages:
*   **Total Samples:** ~600 function blocks.
*   **Split by Language:** 200 Python, 200 Java, 200 JavaScript.
*   **Quality Label Assignment:** High-star repositories were assigned label 0 (Pristine) or 1 (Acceptable). Low-star repositories were assigned label 2 (Concerning) or 3 (Disaster).
*   **Severity Label Assignment:** Continuous values scaled from $0.0$ to $0.3$ for high-quality repos, and $0.5$ to $1.0$ for low-quality repos.

### 3.3 Preprocessing & Deduplication
To prevent model distortion, `data/preprocess_dataset.py` processes raw snippets through the following steps:
1.  **Normalization:** Removes trailing whitespaces and surrounding blank lines.
2.  **Deduplication:** Normalizes all whitespace blocks into single spaces and computes an MD5 checksum:
    $$\text{Hash} = \text{MD5}(\text{Normalized Code Text})$$
    Duplicate rows with matching hashes are dropped.
3.  **Class Balancing:** Class sizes are balanced via random undersampling to avoid class bias in the Random Forest.

---

## ⚙️ Section 4 — Model Training Details

### 4.1 Random Forest Quality Classifier
*   **Hardware / Environment:** Local Intel Core i7-8750H, 12 threads.
*   **Training Time:** ~2.1 seconds.
*   **Hyperparameters:** `n_estimators=100`, `max_depth=20`, `min_samples_split=5`.
*   **Convergence & Overfitting:** Checked via 5-fold cross-validation. Cross-validation accuracy settled at $0.842 \pm 0.024$. The relatively small depth limit (`max_depth=20`) prevented the trees from overfitting on the sparse TF-IDF vectors.

### 4.2 PyTorch Sequence LSTM Severity Scorer
*   **Hardware / Environment:** NVIDIA GTX 1060 (6GB VRAM), CUDA 11.8.
*   **Training Time:** ~4.5 minutes.
*   **Hyperparameters:**
    *   Learning Rate: $0.001$ (Adam Optimizer)
    *   Loss Function: Binary Cross Entropy Loss (`BCELoss`)
    *   Dropout: $0.3$ on recurrent outputs
    *   Epochs: 20 (with early stopping patience of 5 epochs)
    *   Batch Size: 32
*   **Learning Curves:** Converged smoothly from an initial loss of $0.69$ down to a validation loss of $0.18$.
*   **Validation Mean Absolute Error (MAE):** $0.114$ (below the $0.15$ target).

### 4.3 Hugging Face CodeBERT Fine-Tuning
*   **Training Time:** ~18 minutes (fine-tuned for 2 epochs).
*   **Hyperparameters:** Batch size of 4, learning rate $2 \times 10^{-5}$ with a linear warmup scheduler.
*   **Performance:** Achieved a validation cross-entropy loss of $0.412$.

---

## ⚖️ Section 5 — Technical Decisions & Tradeoffs

### 5.1 Why PyTorch over TensorFlow for LSTM?
PyTorch was chosen to ensure support for modern environments (such as Python 3.12+). TensorFlow's dependency graph on Windows is often brittle, whereas PyTorch provides clean installation pipelines, direct CUDA bindings, and a Pythonic API that is easier to debug and structure lazily.

### 5.2 Why Random Forest over XGBoost?
XGBoost requires careful hyperparameter tuning and is highly sensitive to class imbalances. Random Forest is robust to noise, operates out-of-the-box with TF-IDF arrays, and loads instantly using simple joblib pickles.

### 5.3 Why Character n-grams over Word n-grams?
Code syntax is highly custom. Developers write variables like `user_profile_data`, `userData`, or `usrProfile`. Word tokenizers treat these as completely separate tokens, leading to out-of-vocabulary issues. Character n-grams decompose names into sub-words (e.g., `user`, `data`, `prof`), allowing the classifier to recognize syntax patterns even in novel variables.

### 5.4 Why Three Models Instead of One?
A single model is either too slow, too heavy, or too simplistic:
*   AST extraction is fast and deterministic but misses code semantics.
*   Random Forest and LSTMs are fast and run locally but lack general reasoning.
*   LLMs have high reasoning capability but are slow and subject to rate limits.
By combining them, we create a hybrid architecture that balances speed, cost, and intelligence.

### 5.5 Why Streamlit over Flask?
For a visual analytics app, Streamlit provides a rich UI wrapper out-of-the-box, allowing us to focus on ML engineering and prompt quality rather than writing custom HTML/React wrappers.

### 5.6 What would you do differently with more compute/time?
With a high-end dedicated GPU (e.g., NVIDIA RTX 4090), we would fine-tune a local **Qwen2.5-Coder-7B-Instruct** parameter model using LoRA (Low-Rank Adaptation) on a custom dataset of 10,000 developer code reviews, completely eliminating the need for external APIs.

---

## 🚀 Section 6 — Deployment Architecture

### 6.1 Streamlit Cloud & Resource Management
CodeRoast is deployed on Streamlit Cloud. Because free instances have a **1 GB RAM limit**, hosting large transformer models (like CodeBERT or local Qwen weights) on the container is impossible and will cause immediate container crashes.

To solve this, CodeRoast runs an **API-First, Serverless Architecture**:
*   The heavy LLM logic runs on Hugging Face’s Serverless Cloud GPU network (0 MB local RAM usage).
*   CodeBERT only initializes if fine-tuned weights exist locally, falling back to the lightweight Random Forest classifier if memory pressure is detected.
*   The PyTorch model is lazy-loaded, only consuming RAM when a user runs an analysis.

### 6.2 Local Execution Setup
To run CodeRoast locally on your machine, follow these steps:

1.  **Clone the Repository:**
    ```powershell
    git clone https://github.com/gyr0byte/CodeRoast.git
    cd CodeRoast
    ```
2.  **Initialize Virtual Environment (D: Drive recommended to avoid C: drive bloat):**
    ```powershell
    python -m venv venv_gpu
    .\venv_gpu\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```
4.  **Set Environment Variables:**
    To use Qwen cloud generation, save your Hugging Face access token inside `.streamlit/secrets.toml`:
    ```toml
    # .streamlit/secrets.toml
    HF_TOKEN = "your_huggingface_token_here"
    ```
    This also configures `HF_HOME`, `PIP_CACHE_DIR`, and `UV_CACHE_DIR` to redirect package caching to the project directory, keeping your C: drive clean.
5.  **Run Streamlit:**
    ```powershell
    streamlit run app.py
    ```

---

## 📊 Section 7 — Results & Evaluation

### 7.1 Classifier Performance Metrics
The hybrid Random Forest model was evaluated against baseline models:

| Model | Accuracy | F1-Score | Inference Latency |
| :--- | :---: | :---: | :---: |
| TF-IDF + Logistic Regression | 74.2% | 0.731 | **0.5ms** |
| TF-IDF + Random Forest | **84.2%** | **0.835** | 1.8ms |
| CodeBERT (Fine-Tuned) | 88.6% | 0.881 | 180.0ms |

### 7.2 Sample Roasts

#### Case 1: Pristine Input (Python)
```python
def add_numbers(first_value: int, second_value: int) -> int:
    """Adds two integers and returns the result."""
    return first_value + second_value
```
*   **Overall Score:** 92.5 (S Grade)
*   **Qwen AI Roast:** *"Well, someone actually knows what type hints and docstrings are. This is suspiciously clean. Did you copy this from standard library code?"*

#### Case 2: Disaster Input (Python Spaghetti)
```python
def calc(x):
 if x > 0:
  for i in range(x):
   if i % 2 == 0:
    if i < 10:
     print(i)
```
*   **Overall Score:** 22.0 (F Grade)
*   **Qwen AI Roast:** *"This nesting depth is a literal spelunking hazard. Four indentation layers for a print statement? Please reset your head and format this before the compiler files a restraining order."*

---

## 🛠️ Section 8 — Challenges & Solutions

### 8.1 Windows Path Bloat
*   **Problem:** Installing PyTorch and Hugging Face packages cached gigabytes of wheels inside `C:\Users\<User>\AppData\Local\uv\cache`, bloating the system partition.
*   **Solution:** Configured `config.py` to intercept execution at startup, programmatically redirecting `HF_HOME`, `PIP_CACHE_DIR`, and `UV_CACHE_DIR` to the project directory on the D: drive.

### 8.2 Rate Limiting on Free Serverless Endpoints
*   **Problem:** During active use, Hugging Face Serverless endpoints returned status `429 Too Many Requests`.
*   **Solution:** Built a dual-endpoint failover routing mechanism in `llm_generator.py` that catches API exceptions and automatically redirects requests to a secondary model (`Qwen/Qwen2.5-72B-Instruct`).

---

## 🧠 Section 9 — What I Learned

*   **ML Pipelines are 90% Data:** Collecting, parsing, and cleaning 600 clean code blocks was far harder than training the Random Forest. Good formatting and deduplication make or break a classifier.
*   **PyTorch vs. TensorFlow:** PyTorch's eager execution and dynamic graph model make prototyping neural network dimensions much more intuitive than dealing with compiled Keras states.
*   **LLM Grounding:** Raw LLMs tend to give generic coding advice. Passing concrete AST metrics in the user prompt forces the model to write specific, contextual, and realistic jokes.

---

## 🗺️ Section 10 — Future Roadmap

*   **VS Code Extension:** Pack the AST analysis engine and a local lightweight model into an extension that roasts code in real-time inside your editor.
*   **Deeper Language Support:** Integrate full parsers for TypeScript, C++, and Go.
*   **Refinement of Local Execution:** Build a Quantized GGUF execution layer (using llama.cpp) to allow fast local execution on low-memory GPUs (like the GTX 1060).

---

## 🎓 Section 11 — How to Interview for This Project

This section serves as a technical interview preparation guide.

### 20 Technical Q&As

#### Q1: Why did you combine TF-IDF with static metrics instead of just using the raw text?
*   **Answer:** Raw text vectorization captures vocabulary but is blind to structural nesting depth and cyclomatic complexity. Stacking both matrices lets the model learn stylistic signatures (via character TF-IDF) and mathematical complexity (via AST metrics) simultaneously.

#### Q2: Explain the math behind Cyclomatic Complexity.
*   **Answer:** It is a graph theory metric. We map code blocks to a control flow graph (CFG). The complexity is $M = E - V + 2P$, representing the count of decision points (if statements, loops) plus one.

#### Q3: Why did you use `char_wb` as the analyzer in TF-IDF?
*   **Answer:** `char_wb` creates character n-grams only within word boundaries. This ensures we don't merge operators from one statement with keywords from another, preserving identifier roots.

#### Q4: Why is there an LSTM in the pipeline if you have Llama 3.2 / Gemini?
*   **Answer:** While LLMs generate rich text, the local PyTorch LSTM model runs instantly on CPU/GPU without prompt generation overhead to compute an objective mathematical severity score (0.0 to 1.0) and select static templates if AI endpoints are offline.

#### Q5: What is the purpose of the Sigmoid activation at the end of the LSTM?
*   **Answer:** Sigmoid squeezes the final linear output between 0.0 and 1.0, mapping perfectly to a normalized percentage representing the roast intensity.

#### Q6: How does token padding affect your LSTM performance?
*   **Answer:** We pad sequences to a length of 200. Padding tokens are ignored during loss calculations via `padding_idx=0` in the embedding layer to avoid gradient bias.

#### Q7: Why not use word embeddings like Word2Vec?
*   **Answer:** Word2Vec is trained on natural language. Code contains custom names (e.g., `fetchData`) that aren't in natural language dictionaries, causing out-of-vocabulary failures. Character-level tokenization solves this.

#### Q8: How did you select the threshold for early stopping in the LSTM?
*   **Answer:** We set a validation patience of 5. If the validation Binary Cross-Entropy loss doesn't decrease for 5 consecutive epochs, training terminates to prevent overfitting.

#### Q9: What does the weighted average of CodeBERT probabilities represent?
*   **Answer:** CodeBERT outputs probabilities for 4 quality buckets. By multiplying these by weights $[0.0, 0.33, 0.66, 1.0]$ and summing them, we get a continuous severity score representing the expected badness of the code.

#### Q10: How do you handle syntax errors in your AST parser?
*   **Answer:** If `ast.parse` throws a `SyntaxError`, the analyzer sets a syntax error flag. The app skips the ML pipeline and selects a specialized critique mocking the developer's syntax.

#### Q11: Why Random Forest instead of a neural net for the quality classification?
*   **Answer:** Random Forest has low inference latency, is easily serializable, handles heterogeneous features (floats + sparse TF-IDF arrays), and is robust to overfitting.

#### Q12: How does the system handle multi-language parsing?
*   **Answer:** Python uses native AST syntax traversals. Java and JavaScript use heuristic regular expression patterns to match method boundaries and estimate structures.

#### Q13: What does the Creativity score measure?
*   **Answer:** It evaluates modularity. It increases linearly with the number of functions (capped at 100), rewarding code decomposition over monolithic blocks.

#### Q14: Explain the risk of rate-limiting with Hugging Face Serverless API and how you handled it.
*   **Answer:** The free serverless API returns HTTP 429 when rate-limited. We catch this exception in our client code and failover to a larger alternate model (`Qwen/Qwen2.5-72B-Instruct`).

#### Q15: What is a dunder method in Python, and how does your naming checker treat them?
*   **Answer:** Double underscore methods (e.g., `__init__`, `__str__`) are built-in hooks. The naming scoring script ignores them to avoid false naming convention penalties.

#### Q16: How did you scrape the data?
*   **Answer:** Used the GitHub Search API to find repos with $>500$ stars (high quality) and $<5$ stars (low quality), extracted individual methods using ASTs/regexes, and filtered for lengths between 5 and 100 lines.

#### Q17: Why did you redirect pip/uv cache folders?
*   **Answer:** By default, they cache downloads on the C: drive. Setting `UV_CACHE_DIR` and `PIP_CACHE_DIR` variables to the D: drive isolates the project and keeps the system partition clean.

#### Q18: What metric represents how balanced your dataset is?
*   **Answer:** We evaluated class distributions and forced equal size counts across all 4 quality classes using random undersampling.

#### Q19: What is the benefit of using `microsoft/codebert-base`?
*   **Answer:** CodeBERT is pre-trained on programming code syntax. It understands structural and semantic relationships better than traditional BERT models trained on standard English text.

#### Q20: What did the Plotly Radar Chart show?
*   **Answer:** It plots scores across Readability, Efficiency, Structure, and Creativity, showing the structural strengths and weaknesses of the code.

### 📝 Whiteboard Architecture
If asked to whiteboard, sketch the **Three-Tiered Roasting Pipeline**:
1.  **Ingestion:** Source Code Input $\rightarrow$ Language Detection.
2.  **Analysis Branch:**
    *   *Static:* AST Parser $\rightarrow$ 8 Metrics.
    *   *Dynamic:* Vectorizer + RF Classifier / PyTorch LSTM Scorer $\rightarrow$ Quality (0-3) & Severity (0-1).
3.  **Synthesis:** Quality + Severity + Code $\rightarrow$ Prompt Engine $\rightarrow$ Llama 3.2 3B (Local GPU) / Gemini Flash $\rightarrow$ Humorous UI output.

### 🎯 Key Numbers to Cite
*   **Dataset Size:** ~600 curated code snippets.
*   **Cross-Validation Accuracy:** 84.2%.
*   **LSTM Validation MAE:** 0.114.
*   **Model Latency:** ~1-2ms local ML, ~1.2s cloud generation.

---

## 🤝 Section 12 — Project Stats & Acknowledgements

*   **Total Development Time:** ~14 Days (Enrichment Session).
*   **Total Git Commits:** 53+.
*   **Core Frameworks:** Streamlit, PyTorch, Scikit-Learn, Hugging Face Hub, Plotly, Radon.
*   **Enrichment Program:** Built for the IIC Summer Enrichment Class (Applied AI & Data Analysis).
*   **Personal Note:** This project represents a milestone in my ML journey—transitioning from basic notebook scripting to building complete, end-to-end local/serverless hybrid deep learning deployments.

---

*"Your code has been reviewed. The results are not pretty. But at least now you know why."*
