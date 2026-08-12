# CodeRoast 🔥 — AI That Brutally Reviews Your Code

> *"Your code has been reviewed. The results are not pretty."*

**CodeRoast** is an NLP + Deep Learning powered application that analyzes code quality and delivers brutally honest — and hilariously savage — feedback in the style of a senior developer who has seen too much bad code and has zero patience left.

It combines real static code analysis with NLP-driven natural language generation to produce feedback that is simultaneously technically accurate and entertainingly brutal.

## Features

- **Language Support**: Paste any Python, Java, or JavaScript code snippet.
- **Real-time static analysis**: Measures complexity, line length, naming conventions, and duplication.
- **NLP-generated roasts**: Brutal feedback using a fine-tuned language model and dynamic templates.
- **4-dimension scoring**: Readability, Efficiency, Structure, and Creativity.
- **Severity levels**: Adjust the roast intensity from Gentle Nudge to Full Destruction.

## Tech Stack

- **Core**: Python 3.10+
- **Static Analysis**: `ast`, `radon`, `pylint`, `pyflakes`, `tokenize`
- **NLP Layer**: `nltk`, `textblob`, `scikit-learn`, `transformers` (HuggingFace)
- **Deep Learning**: `tensorflow`, `keras`, `numpy`
- **Frontend & Visualizations**: `streamlit`, `plotly`, `streamlit-ace`

## Setup Instructions

This project is configured to download models to a local `models_cache` directory to conserve system drive space.

### 1. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
To avoid filling up your C drive with CUDA/GPU bloat, it's recommended to install the CPU-only version of PyTorch on Windows:
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```
*(Make sure `streamlit`, `transformers`, etc., are in your `requirements.txt`)*

### 3. Run the App
```powershell
streamlit run app.py
```

## Project Architecture
CodeRoast uses a multi-layered analysis pipeline:
1. **Static Analysis Layer**: Extracts objective metrics via Python AST.
2. **NLP Classification Layer**: Categorizes code quality using TF-IDF and Random Forest.
3. **Deep Learning Severity Scorer**: Uses an LSTM-based model to detect specific patterns that deserve roasting.
4. **Roast Generator**: Combines metrics and severity scores to generate dynamic, template-based roasting.

---
*Built by gyr0byte — Not a person, a process. Always building, never stopping.* 🔥
