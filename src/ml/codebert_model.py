"""
CodeRoast — Hugging Face CodeBERT Scorer
Uses pre-trained `microsoft/codebert-base` to evaluate code severity & quality.
"""

import os
import torch
import torch.nn as nn
from typing import Tuple, List, Optional
from pathlib import Path
import config  # noqa: F401 — Sets HF_HOME first

MODEL_NAME = "microsoft/codebert-base"
SAVED_MODEL_DIR = config.MODELS_DIR / "codebert_severity"


class CodeBERTScorer:
    """
    CodeBERT-based sequence classification model for code quality and severity assessment.
    """

    def __init__(self, model_dir: Optional[Path] = None):
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = str(model_dir) if model_dir and model_dir.exists() else MODEL_NAME

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path, num_labels=4
            ).to(self.device)
            self._is_loaded = True
        except Exception as e:
            print(f"[WARNING] Could not load CodeBERT model from {self.model_path}: {e}")
            self._is_loaded = False

    def predict_quality_and_severity(self, code: str) -> Tuple[int, float]:
        """
        Predicts quality bucket (0-3) and normalized severity score (0.0 - 1.0).
        0 = Pristine, 1 = Acceptable, 2 = Concerning, 3 = Disaster
        """
        if not self._is_loaded:
            # Fallback heuristic if CodeBERT failed to load
            return 1, 0.5

        self.model.eval()
        inputs = self.tokenizer(
            code,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1).squeeze(0)

        # Quality bucket is argmax
        quality_level = int(torch.argmax(probs).item())

        # Expected severity = weighted average of probabilities (0.0 to 1.0)
        # Quality levels: 0 (clean) -> 0.0 severity, 3 (disaster) -> 1.0 severity
        weights = torch.tensor([0.0, 0.33, 0.66, 1.0], device=self.device)
        severity = float(torch.sum(probs * weights).item())

        return quality_level, round(severity, 4)

    def train_on_dataset(
        self,
        texts: List[str],
        labels: List[int],
        epochs: int = 3,
        batch_size: int = 4,
        lr: float = 2e-5
    ) -> dict:
        """
        Fine-tunes CodeBERT on custom code dataset.
        """
        if not self._is_loaded:
            raise RuntimeError("CodeBERT model is not initialized.")

        from torch.utils.data import DataLoader, Dataset
        from transformers import get_linear_schedule_with_warmup

        class CodeDataset(Dataset):
            def __init__(self, texts, labels, tokenizer):
                self.encodings = tokenizer(
                    texts, padding=True, truncation=True, max_length=512, return_tensors="pt"
                )
                self.labels = torch.tensor(labels, dtype=torch.long)

            def __len__(self):
                return len(self.labels)

            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item["labels"] = self.labels[idx]
                return item

        dataset = CodeDataset(texts, labels, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        total_steps = len(dataloader) * epochs
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

        self.model.train()
        print(f"[INFO] Fine-tuning CodeBERT on {len(texts)} samples ({epochs} epochs, device: {self.device})...")

        for epoch in range(epochs):
            total_loss = 0.0
            for batch in dataloader:
                optimizer.zero_grad()
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                batch_labels = batch["labels"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=batch_labels
                )
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                scheduler.step()

                total_loss += loss.item()

            avg_loss = total_loss / max(1, len(dataloader))
            print(f"  Epoch {epoch + 1}/{epochs} — Loss: {avg_loss:.4f}")

        # Save model
        SAVED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(SAVED_MODEL_DIR)
        self.tokenizer.save_pretrained(SAVED_MODEL_DIR)
        print(f"[SAVED] Fine-tuned CodeBERT saved to: {SAVED_MODEL_DIR}")

        return {"final_loss": avg_loss}
