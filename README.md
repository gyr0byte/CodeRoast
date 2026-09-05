# CodeRoast 🔥 — AI That Brutally Reviews Your Code

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.61.1-FF4B4B.svg)](https://streamlit.io/)
[![Deep Learning](https://img.shields.io/badge/PyTorch-Sequence%20LSTM-EE4C2C.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Hugging%20Face-CodeBERT%20%26%20Llama%203.2-yellow.svg)](https://huggingface.co/)
[![Gemini Engine](https://img.shields.io/badge/Google%20Gemini-Flash%20Multi--Model%20Fallback-4285F4.svg)](https://ai.google.dev/)
[![Live App](https://img.shields.io/badge/Streamlit%20Cloud-Live%20Demo-brightgreen.svg)](https://coderoast.streamlit.app)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> *"Your code has been reviewed. The results are not pretty."*

**CodeRoast** is an end-to-end Machine Learning, NLP, and Deep Learning powered web application that performs real-time static code quality analysis and generates brutally honest — and hilariously savage — code roasts in both **English** and **Romanized Nepali**.

It combines real static analysis metrics (lines of code, cyclomatic complexity, nesting depth, duplication, naming scores) with machine learning classification models, local GPU LLMs (Meta Llama 3.2 3B via Ollama), and Google Gemini multi-model API chains to deliver code reviews that are technically accurate, culturally rich, and entertainingly savage.

---

## 🌐 Live Web Demo

👉 **Try it live on Streamlit Cloud:** [coderoast.streamlit.app](https://coderoast.streamlit.app)

---

## 🚀 Key Features

- **🌐 Multi-Language Analysis:** Supports **Python**, **Java**, and **JavaScript** code snippets.
- **📊 Real-Time Static AST Analysis:** Calculates Cyclomatic Complexity, Nesting Depth, Line Counts, Comment Ratios, Naming Conventions, and Code Duplication scores.
- **🎁 Easter Egg Engine:** Automatic pattern recognition for famous code tropes (`Hello World`, `FizzBuzz`, `Empty Code`, and `TODO/pass` stubs) with custom sarcastic responses.
- **🇳🇵 Romanized Nepali AI Engine (Gemini Multi-Model Fallback):**
  - Powered by a 4-tier Google Gemini fallback chain (`gemini-2.5-flash` → `gemini-flash-lite-latest` → `gemini-3.5-flash-lite` → `gemini-3.1-flash-lite`).
  - **Sub-4-Second Speed**: Lite model optimization delivers fast (~3.7s) 800+ character Romanized Nepali roasts.
  - **Massive Combinatorial Theme System**: Combines 20 cultural theme pools (Balen Shah dozers, TU exam delays, Nagdhunga jam, Selroti, Wide body scam, etc.), 8 slang sets, 12 persona tones, 8 roast structures, and 7 signature closers for **15,000+ unique roast permutations**.
  - **Strict Content Moderation**: Zero sexual vulgarity policy with hard-coded boundaries.
- **🤖 English AI Engine (Local Meta Llama 3.2 3B via Ollama & Dynamic Theme Engine):**
  - Powered by local `llama3.2:3b` with dynamic theme sampling and 100% GPU VRAM offload.
  - **12 Dynamic Cultural Themes**: Silicon Valley failures, Stack Overflow elitism, r/programminghorror, FAANG interview disasters, Cyberpunk 2077 bugs, Fyre Festival, Enterprise Jira hell, ChatGPT hallucination, Startup delusion, Linus Torvalds PR flames, Friday deploy apocalypses, and Y2K.
  - **10 Tones, 6 Structures, 6 Signature Closers** yielding another **15,000+ unique roast variations**.
- **🖼️ Authentic Classic Impact Font Meme Generator:**
  - Powered by 100+ downloaded meme templates in `assets/memes/` (Left Exit 12 Off Ramp, Drake Hotline Bling, Batman Slap, Two Buttons, Change My Mind, Buff Doge vs Cheems, A-Train, etc.).
  - **Dynamic Template Pools (`MEME_CATALOG`)**: Randomly samples from 25+ template and punchline variations per flaw category (Spaghetti, Complexity, Nesting, Mismatch, Disaster, Praise) so re-roasting the same code produces a **new meme every time**.
  - **Template Visual Zone Alignment**: Uses precise coordinate mapping (`top_y`, `bottom_y`) so text renders directly onto visual elements (e.g. centered on highway exit signs, Drake right panels, etc.).
- **🔊 Web Speech API Voice Narration:** Browser-native text-to-speech player ("Read Roast Aloud") with instant playback, toggle controls, and 0% local server CPU/RAM load.
- **📜 Enforced 75+ Word Length & Clean Safety Filters:**
  - All AI-generated and template fallback roasts are guaranteed to be a minimum of **75 to 120 words** for maximum unhinged detail.
  - Automated regex post-filters and strict system prompt exclusions remove banned offensive terms (`randikhola`, `randi`) while preserving intense developer satire.
- **🎨 Interactive Streamlit Interface:** Features side-by-side code input & roast rendering, source-specific UI backgrounds, visual grade cards (*S to F* with randomized unhinged reactions per grade), Plotly radar charts, and customizable severity sliders.

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
                               │ Hybrid AI Roast Engine   │
                               ├──────────────────────────┤
                               │ 🇳🇵 Nepali: Gemini Chain  │
                               │ 🇬🇧 English: Local Llama  │
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
├── config.py                   # Global configuration & HF/Gemini API keys
├── how_to_start.md             # PowerShell Quick-Start & Service Setup Guide
├── ABOUT.md                    # In-depth Technical Documentation & Architecture Manual
├── CodeRoast_Project_Plan.md   # Project Specification & Architecture Plan
├── requirements.txt            # Project dependencies
├── assets/
│   ├── fonts/
│   │   └── impact.ttf          # Classic Impact Meme Font
│   └── memes/                  # 100+ Classic meme templates (.jpg)
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
    │   ├── llm_generator.py    # Multi-model Gemini & Local Llama/Qwen LLM generator
    │   └── templates.py        # Curated template roasts (English & Nepali)
    └── scoring/
        └── scorer.py           # Multi-dimensional scoring engine
```

---

## 🛠️ Quick Start & Local Setup

### 1. PowerShell One-Liner (Fast Launch)

```powershell
Set-Location D:\CodeRoast; Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned; $env:OLLAMA_MODELS = "D:\CodeRoast\ollama_models"; if (-not (Get-Process -Name ollama -ErrorAction SilentlyContinue)) { Start-Process -FilePath "D:\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden }; & .\venv_gpu\Scripts\streamlit.exe run app.py
```

### 2. Manual Step-by-Step

Refer to [how_to_start.md](how_to_start.md) for full step-by-step instructions.

```powershell
# Activate Python Virtual Environment
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\venv_gpu\Scripts\Activate.ps1

# Run Streamlit App
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

---

## ☁️ Streamlit Cloud Deployment & Secrets

To host on **Streamlit Cloud** with full dynamic AI roasts:
1. Connect your repository to [share.streamlit.io](https://share.streamlit.io/).
2. Set main file path to `app.py`.
3. Add your **Google Gemini API Key** in **App Settings -> Secrets**:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
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
