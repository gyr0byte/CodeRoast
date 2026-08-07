# CodeRoast 🔥 — AI That Brutally Reviews Your Code

> *"Your code has been reviewed. The results are not pretty."*

---

## Project Overview

**CodeRoast** is an NLP + Deep Learning powered application that analyzes code quality and delivers brutally honest — and hilariously savage — feedback in the style of a senior developer who has seen too much bad code and has zero patience left.

It combines real static code analysis with NLP-driven natural language generation to produce feedback that is simultaneously technically accurate and entertainingly brutal.

**Type:** End-to-end ML/NLP application with Streamlit frontend  
**Domain:** NLP + Deep Learning + Static Code Analysis  
**Difficulty:** Advanced undergraduate / Early graduate  
**Timeline:** 4 weeks  
**Deployment:** Streamlit Cloud (free)

---

## The Core Idea

Most code reviewers are dry and boring. CodeRoast gives you:

- Real technical metrics — complexity, readability, efficiency
- Genuine actionable feedback — what is actually wrong and why
- Brutal delivery — "This function is doing 7 jobs. So is my intern. Neither should be."
- A scoring system across 4 dimensions
- Comparison to famous bad code examples from history

---

## Features

### Core Features (Must Have)
- [ ] Paste any Python, Java, or JavaScript code snippet
- [ ] Real-time static analysis — complexity, line length, naming conventions, duplication
- [ ] NLP-generated roast using fine-tuned language model
- [ ] 4-dimension scoring: Readability, Efficiency, Structure, Creativity
- [ ] Severity levels — Gentle Nudge → Mild Concern → Full Destruction

### Enhanced Features (Nice to Have)
- [ ] Side-by-side before/after — roasted code vs suggested improvement
- [ ] "Hall of Shame" — save and share your worst scores
- [ ] Code smell detector with funny names for each smell
- [ ] Historical roast log — track your improvement over time
- [ ] "Roast Battle" mode — compare two code snippets head to head

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│                  Streamlit Frontend                      │
│         Code Input → Analysis → Roast Display           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  ANALYSIS PIPELINE                       │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Static    │  │     NLP     │  │  Deep Learning  │ │
│  │  Analysis   │  │  Pipeline   │  │    Classifier   │ │
│  │   Layer     │  │   Layer     │  │     Layer       │ │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘ │
│         │                │                   │          │
│         └────────────────┴───────────────────┘          │
│                          │                               │
│                          ▼                               │
│              ┌───────────────────────┐                  │
│              │   Roast Generator     │                  │
│              │  (Template + LLM)     │                  │
│              └───────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │    Output Layer       │
              │  Score + Roast Text   │
              │  + Suggestions        │
              └───────────────────────┘
```

---

## Tech Stack

### Core Language
```
Python 3.10+
```

### Static Analysis
```
ast          — Python Abstract Syntax Tree parsing
radon        — Cyclomatic complexity measurement
pylint       — Code quality metrics
pyflakes     — Error detection
tokenize     — Token-level analysis
```

### NLP Layer
```
nltk         — Text preprocessing, tokenization
textblob     — Sentiment and pattern analysis
sklearn      — TF-IDF vectorization
transformers — HuggingFace for pre-trained models
```

### Deep Learning Layer
```
tensorflow   — Model building and training
keras        — High-level neural network API
numpy        — Numerical operations
```

### Frontend & Deployment
```
streamlit    — Web application framework
plotly       — Interactive score visualizations
streamlit-ace — Code editor component in browser
```

### Development Tools
```
pandas       — Dataset management
jupyter      — Notebook-based development
git          — Version control
```

---

## Pipeline — Step by Step

### Step 1 — Static Analysis Layer

Extract objective metrics from code using AST:

```python
import ast
import radon.complexity as radon_cc

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)
    
    def get_metrics(self) -> dict:
        return {
            'lines_of_code': len(self.code.splitlines()),
            'function_count': self._count_functions(),
            'avg_function_length': self._avg_function_length(),
            'cyclomatic_complexity': self._get_complexity(),
            'naming_score': self._check_naming_conventions(),
            'comment_ratio': self._comment_to_code_ratio(),
            'nesting_depth': self._max_nesting_depth(),
            'duplicate_code_score': self._detect_duplication(),
        }
    
    def _count_functions(self) -> int:
        return sum(1 for node in ast.walk(self.tree) 
                   if isinstance(node, ast.FunctionDef))
    
    def _get_complexity(self) -> float:
        results = radon_cc.cc_visit(self.code)
        if not results:
            return 1.0
        return sum(r.complexity for r in results) / len(results)
    
    def _check_naming_conventions(self) -> float:
        # Check snake_case for functions, UPPER for constants
        score = 100.0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower():
                    score -= 10
        return max(0, score)
```

---

### Step 2 — NLP Classification Layer

Train a classifier to categorize code quality level:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class CodeQualityClassifier:
    """
    Classifies code into quality buckets:
    0 = Pristine (rare, almost mythical)
    1 = Acceptable (human wrote this)
    2 = Concerning (coffee needed)
    3 = Disaster (please seek help)
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',  # character n-grams work well for code
            ngram_range=(2, 4),
            max_features=5000
        )
        self.classifier = RandomForestClassifier(n_estimators=100)
    
    def prepare_features(self, code: str, metrics: dict) -> np.ndarray:
        # Combine TF-IDF features with static metrics
        tfidf_features = self.vectorizer.transform([code])
        metric_features = np.array(list(metrics.values())).reshape(1, -1)
        return np.hstack([tfidf_features.toarray(), metric_features])
    
    def predict_quality(self, code: str, metrics: dict) -> tuple:
        features = self.prepare_features(code, metrics)
        quality_level = self.classifier.predict(features)[0]
        confidence = self.classifier.predict_proba(features)[0].max()
        return quality_level, confidence
```

---

### Step 3 — Deep Learning Severity Scorer

LSTM-based model to detect specific patterns that deserve roasting:

```python
import tensorflow as tf
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

def build_roast_severity_model(vocab_size: int, max_length: int) -> tf.keras.Model:
    """
    Predicts roast severity score (0.0 to 1.0)
    Higher score = more brutal roast deserved
    """
    model = Sequential([
        Embedding(vocab_size, 64, input_length=max_length),
        LSTM(128, return_sequences=True),
        Dropout(0.3),
        LSTM(64),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')  # severity score
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model
```

---

### Step 4 — Roast Generator

The fun part. Template-based generation with dynamic slot filling:

```python
import random

class RoastGenerator:
    
    ROAST_TEMPLATES = {
        'high_complexity': [
            "This function has a cyclomatic complexity of {score}. "
            "So does my anxiety. Neither is healthy.",
            
            "I've seen spaghetti with less nesting than this. "
            "And at least spaghetti is delicious.",
            
            "Your function does {count} things. "
            "So does a Swiss Army knife. "
            "At least the knife is intentional.",
        ],
        'bad_naming': [
            "Variable named '{name}'? Bold choice. "
            "Did you lose a bet?",
            
            "I see you named your function '{name}'. "
            "I've seen more descriptive cave paintings.",
            
            "'{name}' tells me absolutely nothing about what this does. "
            "Neither does reading the function body, to be fair.",
        ],
        'no_comments': [
            "Zero comments. Future you will hate present you. "
            "It is a rite of passage at this point.",
            
            "I assume the lack of comments means the code "
            "is so self-explanatory that... wait, no it is not.",
        ],
        'too_long': [
            "This function is {lines} lines long. "
            "So is the list of things wrong with it.",
            
            "At {lines} lines, this function has more responsibilities "
            "than I do. And I'm an AI.",
        ],
        'praise': [
            "Wait. This is actually decent. "
            "I need a moment. I was not prepared for this.",
            
            "Clean code detected. Are you sure you wrote this?",
        ]
    }
    
    def generate_roast(self, metrics: dict, quality_level: int, 
                       severity: float) -> str:
        roast_parts = []
        
        # Select relevant roast categories based on metrics
        if metrics['cyclomatic_complexity'] > 10:
            template = random.choice(
                self.ROAST_TEMPLATES['high_complexity']
            )
            roast_parts.append(
                template.format(score=metrics['cyclomatic_complexity'])
            )
        
        if metrics['avg_function_length'] > 50:
            template = random.choice(self.ROAST_TEMPLATES['too_long'])
            roast_parts.append(
                template.format(lines=metrics['avg_function_length'])
            )
        
        if metrics['comment_ratio'] < 0.05:
            roast_parts.append(
                random.choice(self.ROAST_TEMPLATES['no_comments'])
            )
        
        if quality_level == 0:
            roast_parts.append(random.choice(self.ROAST_TEMPLATES['praise']))
        
        return ' '.join(roast_parts) if roast_parts else self._default_roast()
    
    def _default_roast(self) -> str:
        return ("I have analyzed your code. "
                "I have questions. Mostly 'why'.")
```

---

### Step 5 — Scoring System

```python
def calculate_scores(metrics: dict) -> dict:
    """
    Returns scores 0-100 for each dimension
    Higher = better (unfortunately)
    """
    
    readability = (
        metrics['naming_score'] * 0.4 +
        min(metrics['comment_ratio'] * 500, 100) * 0.3 +
        max(0, 100 - metrics['avg_function_length']) * 0.3
    )
    
    efficiency = max(0, 100 - (metrics['cyclomatic_complexity'] * 5))
    
    structure = max(0, 100 - (metrics['nesting_depth'] * 10))
    
    creativity = min(metrics['function_count'] * 10, 100)
    
    overall = (readability + efficiency + structure + creativity) / 4
    
    return {
        'readability': round(readability, 1),
        'efficiency': round(efficiency, 1),
        'structure': round(structure, 1),
        'creativity': round(creativity, 1),
        'overall': round(overall, 1),
        'grade': _get_grade(overall)
    }

def _get_grade(score: float) -> str:
    grades = {
        90: "S — Suspiciously Good",
        75: "A — Actually Decent",
        60: "B — Barely Acceptable",
        45: "C — Concerning",
        30: "D — Deeply Troubling",
        0:  "F — Please Seek Help"
    }
    for threshold, grade in grades.items():
        if score >= threshold:
            return grade
    return "F — Please Seek Help"
```

---

### Step 6 — Streamlit Frontend

```python
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="CodeRoast 🔥",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 CodeRoast")
st.subheader("Brutally honest code reviews. You asked for this.")

col1, col2 = st.columns([1, 1])

with col1:
    code_input = st.text_area(
        "Paste your code here. We will not judge you. "
        "(We will absolutely judge you.)",
        height=400,
        placeholder="def my_function(x):\n    # TODO: write code\n    pass"
    )
    
    language = st.selectbox(
        "Language",
        ["Python", "Java", "JavaScript"]
    )
    
    severity = st.slider(
        "Roast Severity",
        min_value=1, max_value=3,
        value=2,
        help="1 = Gentle, 2 = Standard, 3 = No Mercy"
    )
    
    roast_button = st.button("🔥 Roast My Code", type="primary")

with col2:
    if roast_button and code_input:
        with st.spinner("Analyzing your code... (taking deep breaths)"):
            
            # Run pipeline
            analyzer = CodeAnalyzer(code_input)
            metrics = analyzer.get_metrics()
            scores = calculate_scores(metrics)
            roast = roast_generator.generate_roast(
                metrics, quality_level, severity
            )
            
            # Display scores
            st.subheader(f"Grade: {scores['grade']}")
            
            # Radar chart
            fig = go.Figure(data=go.Scatterpolar(
                r=[scores['readability'], scores['efficiency'],
                   scores['structure'], scores['creativity']],
                theta=['Readability', 'Efficiency', 
                       'Structure', 'Creativity'],
                fill='toself',
                line_color='#FF4B4B'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # The roast
            st.error(f"🔥 **CodeRoast Says:** {roast}")
```

---

## Dataset Strategy

### For NLP Classifier Training

**Option 1 — GitHub Code Quality Dataset (Recommended)**
Scrape GitHub repos rated by stars and contributor feedback. High-star repos = good code. Low-star abandoned repos = bad code.

**Option 2 — CodeSearchNet Dataset**
Microsoft's open dataset of code with docstrings. Available on HuggingFace.

**Option 3 — Build Your Own (Most Fun)**
Manually label 500-1000 code snippets across 4 quality levels. Use your OOP Purity Analyzer framework as a guide. Yes — this connects directly to your research paper. 😄

### Roast Template Dataset
Manually write 20-30 roast templates per category. The quality of these templates is what makes the app genuinely funny vs generically snarky.

---

## 4-Week Roadmap

### Week 1 — Foundation
```
Day 1-2:  Set up project structure, install dependencies
Day 3-4:  Build CodeAnalyzer — AST parsing, metric extraction
Day 5-6:  Test on 10 code snippets manually, validate metrics
Day 7:    Commit clean foundation, write initial README
```

### Week 2 — ML Pipeline
```
Day 1-2:  Collect/prepare training dataset (500+ samples)
Day 3-4:  Build and train NLP classifier (TF-IDF + Random Forest)
Day 5-6:  Build and train LSTM severity scorer
Day 7:    Evaluate both models, confusion matrix, F1 scores
```

### Week 3 — Roast Generator + Integration
```
Day 1-2:  Write 100+ roast templates across all categories
Day 3-4:  Build RoastGenerator class, integrate with pipeline
Day 5-6:  Build Streamlit frontend with Plotly radar chart
Day 7:    End-to-end testing with real code examples
```

### Week 4 — Polish + Deploy
```
Day 1-2:  Improve roast quality, add more templates
Day 3:    Deploy to Streamlit Cloud
Day 4-5:  Test with classmates' code (with permission 😄)
Day 6:    Write final README, record demo video
Day 7:    Present
```

---

## Project Structure

```
coderoast/
├── src/
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── code_analyzer.py      ← Static analysis
│   │   └── metrics.py            ← Metric calculations
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── classifier.py         ← NLP quality classifier
│   │   ├── lstm_model.py         ← Deep learning severity
│   │   └── train.py              ← Training scripts
│   ├── roast/
│   │   ├── __init__.py
│   │   ├── generator.py          ← Roast generation
│   │   └── templates.py          ← All roast templates
│   └── scoring/
│       ├── __init__.py
│       └── scorer.py             ← Score calculation
├── notebooks/
│   ├── 1_eda_code_dataset.ipynb
│   ├── 2_nlp_classifier.ipynb
│   └── 3_lstm_severity.ipynb
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   ├── classifier.pkl
│   └── lstm_severity.h5
├── app.py                        ← Streamlit app entry point
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Evaluation Metrics

### Model Performance
| Metric | Target |
|---|---|
| Classifier Accuracy | > 80% |
| Classifier F1 Score | > 0.78 |
| LSTM Severity MAE | < 0.15 |

### User Experience
| Metric | Target |
|---|---|
| Analysis time | < 3 seconds |
| Roast relevance | Technically accurate |
| Roast humor | Makes at least one person laugh 😄 |

---

## Known Challenges and Solutions

| Challenge | Solution |
|---|---|
| AST parsing fails on syntax errors | Wrap in try-except, provide syntax error roast |
| Java/JS analysis (no AST in Python) | Use regex-based analysis for non-Python |
| Roasts feel repetitive | Large template pool + randomization |
| Model overfits small dataset | Cross-validation + regularization |
| Deployment GPU requirements | Use lightweight models, CPU inference |

---

## Future Extensions

- **Multi-language support** — C++, Go, Rust
- **PR Review mode** — analyze entire pull requests
- **Team leaderboard** — whose code gets roasted least
- **IDE plugin** — VS Code extension for real-time roasting
- **API endpoint** — integrate into CI/CD pipelines
- **Fine-tuned LLM** — replace templates with actual GPT-style generation

---

## Connection to Academic Work

This project directly extends your existing research:

- **OOP Purity Analyzer** — same GitHub scraping infrastructure
- **Research paper methodology** — quantitative scoring framework
- **NLP skills** — from Sheryians NLP video
- **Deep Learning** — LSTM from RNN video
- **Statistics** — metric normalization and scoring

CodeRoast is not just a fun project. It is evidence of an undergraduate researcher who can implement, deploy, and explain ML systems end to end.

---

## The Demo Script (For Presentation)

```
1. Open Streamlit app live in browser
2. Paste your own worst code from Year 1 (the Java calculator 😄)
3. Hit "Roast My Code"
4. Watch the radar chart fill in
5. Read the roast out loud
6. Invite classmate to paste their code
7. Compare scores
8. Explain the pipeline technically
9. Show the notebooks with model evaluation
10. Drop the mic
```

---

*Built by gyr0byte — Not a person, a process. Always building, never stopping.* 🔥

---

**Repository:** github.com/gyr0byte/coderoast  
**Deployment:** coderoast.streamlit.app  
**Status:** Building


# Important To Do — Keep Everything on D Drive
 
Setup checklist for CodeRoast so the venv, pip cache, and HuggingFace model
weights all live on D drive instead of filling up C drive.
 
---
 
## 1. Create the venv on D drive
 
```powershell
cd D:\coderoast
python -m venv venv
venv\Scripts\activate
```
 
---
 
## 2. Redirect pip's cache to D drive
 
Set this once, permanently, so every future `pip install` uses D drive:
 
```powershell
pip config set global.cache-dir D:\pip_cache
```
 
(Alternative — one-off per install instead of permanent):
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu --cache-dir D:\pip_cache
```
 
---
 
## 3. Install CPU-only torch (avoid GPU/CUDA bloat)
 
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers streamlit
```
 
> ⚠️ Do NOT run plain `pip install torch` on Windows — it pulls the GPU/CUDA
> version by default (~2–2.5 GB). The command above installs the CPU-only
> build (~250 MB).
 
---
 
## 4. Redirect HuggingFace model cache to project folder (Option A)
 
Create a `config.py` file in the project root (`D:\coderoast\config.py`):
 
```python
# config.py — must be imported BEFORE transformers/torch anywhere in the app
import os
from pathlib import Path
 
PROJECT_ROOT = Path(__file__).parent
os.environ["HF_HOME"] = str(PROJECT_ROOT / "models_cache")
```
 
Then, at the very top of `app.py` (before any `transformers`/`torch` import):
 
```python
import config  # sets HF_HOME first
 
from transformers import AutoModel, AutoTokenizer
```
 
This makes all downloaded model weights land in:
```
D:\coderoast\models_cache\
```
 
---
 
## 5. Add the cache folder to `.gitignore`
 
Open `.gitignore` and add:
 
```
models_cache/
venv/
```
 
This stops multi-hundred-MB model files (and the venv itself) from being
committed to GitHub.
 
---
 
## 6. Quick verification checklist
 
- [ ] `venv` folder exists inside `D:\coderoast\`
- [ ] `pip config list` shows `global.cache-dir = D:\pip_cache`
- [ ] `torch.__version__` does NOT show `+cu###` (confirms CPU-only build)
- [ ] After first model download, check `D:\coderoast\models_cache\hub\` has
      the model files (not `C:\Users\<You>\.cache\huggingface`)
- [ ] `models_cache/` and `venv/` appear in `.gitignore`
---
 
## Expected disk usage after setup (all on D drive)
 
| Item | Approx. Size |
|---|---|
| venv (torch CPU + transformers + deps) | ~300–400 MB |
| Small NLP model (e.g. DistilBERT-sized) | ~250–450 MB |
| pip cache | varies, safe to delete anytime |
| **Total** | **~600 MB – 1 GB** |
 
C drive stays untouched by any of this once steps 1–4 are done.