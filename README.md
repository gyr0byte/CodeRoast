# CodeRoast 🔥 — AI That Brutally Reviews Your Code

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.61.1-FF4B4B.svg)](https://streamlit.io/)
[![Deep Learning](https://img.shields.io/badge/PyTorch-Sequence%20LSTM-EE4C2C.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Hugging%20Face-CodeBERT%20%26%20Qwen2.5--Coder-yellow.svg)](https://huggingface.co/)
[![Live App](https://img.shields.io/badge/Streamlit%20Cloud-Live%20Demo-brightgreen.svg)](https://coderoast.streamlit.app)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> *"Your code has been reviewed. The results are not pretty."*

**CodeRoast** is an end-to-end Machine Learning, NLP, and Deep Learning powered web application that performs real-time static code quality analysis and generates brutally honest — and hilariously savage — code roasts.

It combines real static analysis metrics (lines of code, cyclomatic complexity, nesting depth, duplication, naming scores) with machine learning classification models and open-source Large Language Models (LLMs) to deliver feedback that is both technically spot-on and entertainingly savage.

---

## 🌐 Live Web Demo

👉 **Try it live on Streamlit Cloud:** [coderoast.streamlit.app](https://coderoast.streamlit.app)

---

## 🚀 Key Features

- **🌐 Multi-Language Analysis:** Supports **Python**, **Java**, and **JavaScript** code snippets.
- **📊 Real-time Static AST Analysis:** Calculates Cyclomatic Complexity, Nesting Depth, Line Counts, Comment Ratios, Naming Conventions, and Code Duplication scores.
- **🌲 Lightweight Random Forest Classifier:** Predicts code quality tiers (*Pristine, Acceptable, Questionable, Disaster*) based on NLP code tokenization (`classifier.pkl`, 340 KB).
- **⚡ PyTorch Sequence LSTM:** Custom PyTorch model trained to score code severity on a 0–10 continuous scale.
- **🤗 Hugging Face CodeBERT (`microsoft/codebert-base`):** Pre-trained transformer sequence classifier providing deep semantic understanding of code structure.
- **🤖 Hugging Face Cloud AI LLM (`Qwen/Qwen2.5-Coder-32B-Instruct`):** Generates dynamic, AI roasts via Hugging Face Serverless API (using 0 MB local RAM on free cloud hosting), with automatic fallback to local PyTorch execution.
- **🎨 Interactive Streamlit Interface:** Features visual grade cards (*S to F*), Plotly sub-metric radar & bar charts, and adjustable roast severity sliders.

---

## 🏗️ System Architecture

```
                               ┌──────────────────────────┐
                               │     User Code Input      │
                               │  (Python / JS / Java)    │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │  Static Analysis Engine  │
                               │ (AST, CC, LOC, Naming)   │
                               └────────────┬─────────────┘
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
┌─────────────────────┐        ┌─────────────────────────┐        ┌─────────────────────┐
│  TF-IDF + Random    │        │  PyTorch Sequence LSTM  │        │ 🤗 CodeBERT Model   │
│  Forest Classifier  │        │   Severity Scorer       │        │  (Sequence Classifier)│
└──────────┬──────────┘        └────────────┬────────────┘        └──────────┬──────────┘
           │                                │                                │
           └────────────────────────────────┼────────────────────────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │ Dynamic AI Roast Engine  │
                               │ (HF Cloud API / Local)   │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │   Streamlit Web App UI   │
                               └──────────────────────────┘
```

---

## 📂 Project Structure

```text
CodeRoast/
├── app.py                      # Main Streamlit Dashboard Application
├── config.py                   # Global configuration & HF cache isolation
├── requirements.txt            # Project dependencies
├── documentation.md            # Technical Interview Preparation Guide
├── CodeRoast_Project_Plan.md   # Project Specification & Architecture Plan
├── data/
│   ├── scrape_github.py        # GitHub API repository scraper
│   ├── preprocess_dataset.py   # Dataset feature extractor & cleaning
│   ├── raw/
│   │   └── scraped_code.csv    # Raw GitHub code snippets
│   └── processed/
│       └── code_samples.csv    # Tokenized dataset with quality labels
├── models/
│   ├── classifier.pkl          # Trained Random Forest classifier
│   ├── lstm_severity.pt        # Trained PyTorch LSTM severity model
│   └── tokenizer.pkl           # Code vocabulary tokenizer
├── notebooks/
│   ├── 1_eda_code_dataset.ipynb   # Exploratory Data Analysis & Visualizations
│   ├── 2_nlp_classifier.ipynb     # TF-IDF + Classifier Training & Metrics
│   └── 3_lstm_severity.ipynb      # PyTorch LSTM & CodeBERT Model Evaluation
└── src/
    ├── analyzer/
    │   ├── code_analyzer.py    # Multi-language static analyzer
    │   └── metrics.py          # Cyclomatic & structural metrics
    ├── ml/
    │   ├── classifier.py       # Random Forest quality classifier
    │   ├── lstm_model.py       # PyTorch LSTM architecture
    │   ├── codebert_model.py   # Hugging Face CodeBERT wrapper
    │   └── train.py            # Training pipeline orchestrator
    ├── roast/
    │   ├── generator.py        # Hybrid Roast Generator
    │   ├── llm_generator.py    # HF Serverless API + Local LLM generator
    │   └── templates.py        # Curated template roasts
    └── scoring/
        └── scorer.py           # Multi-dimensional scoring engine
```

---

## 🛠️ Installation & Local Setup

### 1. Clone Repository & Create Virtual Environment
```powershell
git clone https://github.com/gyr0byte/CodeRoast.git
cd CodeRoast

python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
# Install PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
pip install -r requirements.txt
```

---

## 💻 Running the Application

Launch the Streamlit web dashboard:
```powershell
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

---

## ☁️ Streamlit Cloud Deployment & Secrets

To host on **Streamlit Cloud** with full dynamic AI roasts:
1. Connect your repository to [share.streamlit.io](https://share.streamlit.io/).
2. Set main file path to `app.py`.
3. *(Optional)* Add a free Hugging Face User Access Token in **App Settings -> Secrets**:
   ```toml
   HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxx"
   ```

---

## 📓 Portfolio & Jupyter Notebooks

This repository includes 3 fully documented Jupyter notebooks ready for portfolio inspection:

1. **`notebooks/1_eda_code_dataset.ipynb`** — Exploratory Data Analysis of scraped GitHub code samples.
2. **`notebooks/2_nlp_classifier.ipynb`** — Feature engineering, TF-IDF vectorization, and Random Forest classifier training.
3. **`notebooks/3_lstm_severity.ipynb`** — Sequence modeling with PyTorch LSTM and Hugging Face CodeBERT.

---

## ⚙️ ML Pipeline Orchestration

To re-train the models from scratch on new code snippets:

```powershell
# 1. Scrape GitHub Repositories
python -m data.scrape_github

# 2. Preprocess & Extract Features
python -m data.preprocess_dataset

# 3. Train Classifier & PyTorch LSTM Models
python -m src.ml.train
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built by **gyr0byte** — Not a person, a process. Always building, never stopping.* 🔥
