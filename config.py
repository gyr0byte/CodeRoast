# config.py — Must be imported BEFORE transformers/torch anywhere in the app
# This ensures all model downloads and caches stay on D drive.

import os
from pathlib import Path

# ─── Project Paths ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

# ─── Redirect HuggingFace cache to D drive ───────────────────────────────────
# This prevents model weights from being downloaded to C:\Users\<You>\.cache\
os.environ["HF_HOME"] = str(PROJECT_ROOT / "models_cache")

# ─── Suppress noisy framework logs ────────────────────────────────────────────
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Silence HuggingFace tokenizer warnings
