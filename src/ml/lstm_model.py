"""
CodeRoast — LSTM Severity Scorer (PyTorch)
Deep learning model that predicts how severely code deserves to be roasted.

Uses a stacked LSTM to analyze tokenized code and output a severity
score between 0.0 (pristine) and 1.0 (maximum roast deserved).

Switched from TensorFlow to PyTorch for Python 3.14 compatibility
and unified GPU framework (single install with CUDA 11.8).
"""

import os
import re
import numpy as np
from collections import Counter

import config

# Lazy imports — PyTorch is heavy, only load when needed
_torch = None
_nn = None


def _import_torch():
    """Lazy import PyTorch to avoid slow startup when not needed."""
    global _torch, _nn
    if _torch is None:
        import torch
        import torch.nn as nn
        _torch = torch
        _nn = nn
    return _torch, _nn


class LSTMSeverityModel:
    """
    PyTorch LSTM model that predicts roast severity (0.0 to 1.0).

    Architecture:
        Embedding → LSTM(128) → Dropout → LSTM(64) → Dropout
        → Dense(32, ReLU) → Dense(1, Sigmoid)
    """

    def __init__(self, vocab_size: int, max_length: int,
                 embed_dim: int = 64, hidden1: int = 128, hidden2: int = 64):
        torch, nn = _import_torch()

        self.vocab_size = vocab_size
        self.max_length = max_length
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model = _SeverityLSTM(
            vocab_size, embed_dim, hidden1, hidden2
        ).to(self.device)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()

        print(f"[INFO] LSTM device: {self.device}")
        if self.device.type == "cuda":
            print(f"       GPU: {torch.cuda.get_device_name(0)}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 20, batch_size: int = 32) -> dict:
        """
        Train the LSTM model.

        Args:
            X_train: Tokenized + padded code sequences (2D int array).
            y_train: Severity scores (1D float array, 0.0-1.0).
            X_val: Optional validation sequences.
            y_val: Optional validation scores.
            epochs: Number of training epochs.
            batch_size: Training batch size.

        Returns:
            Dictionary with training history.
        """
        torch, nn = _import_torch()

        # Convert to tensors
        X_train_t = torch.LongTensor(X_train).to(self.device)
        y_train_t = torch.FloatTensor(y_train).unsqueeze(1).to(self.device)

        if X_val is not None and y_val is not None:
            X_val_t = torch.LongTensor(X_val).to(self.device)
            y_val_t = torch.FloatTensor(y_val).unsqueeze(1).to(self.device)
        else:
            X_val_t, y_val_t = None, None

        # Training loop
        history = {"loss": [], "val_loss": []}
        best_val_loss = float("inf")
        patience_counter = 0
        patience = 5

        dataset = torch.utils.data.TensorDataset(X_train_t, y_train_t)
        loader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True
        )

        for epoch in range(epochs):
            # Training
            self.model.train()
            epoch_loss = 0.0
            n_batches = 0

            for batch_X, batch_y in loader:
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()
                n_batches += 1

            avg_train_loss = epoch_loss / n_batches
            history["loss"].append(avg_train_loss)

            # Validation
            val_loss_str = ""
            if X_val_t is not None:
                self.model.eval()
                with torch.no_grad():
                    val_out = self.model(X_val_t)
                    val_loss = self.criterion(val_out, y_val_t).item()
                history["val_loss"].append(val_loss)
                val_loss_str = f"  val_loss: {val_loss:.4f}"

                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        print(f"  Early stopping at epoch {epoch + 1}")
                        break

            print(f"  Epoch {epoch + 1}/{epochs}  "
                  f"loss: {avg_train_loss:.4f}{val_loss_str}")

        return {
            "epochs_trained": len(history["loss"]),
            "final_loss": history["loss"][-1],
            "history": history,
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict severity scores for code samples."""
        torch, _ = _import_torch()

        self.model.eval()
        X_t = torch.LongTensor(X).to(self.device)

        with torch.no_grad():
            predictions = self.model(X_t).cpu().numpy().flatten()

        return predictions

    def save(self, filename: str = "lstm_severity.pt") -> str:
        """Save the trained model to disk."""
        torch, _ = _import_torch()
        filepath = config.MODELS_DIR / filename
        os.makedirs(config.MODELS_DIR, exist_ok=True)

        torch.save({
            "model_state_dict": self.model.state_dict(),
            "vocab_size": self.vocab_size,
            "max_length": self.max_length,
        }, str(filepath))

        return str(filepath)

    def load(self, filename: str = "lstm_severity.pt") -> None:
        """Load a trained model from disk."""
        torch, _ = _import_torch()
        filepath = config.MODELS_DIR / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"No saved model found at {filepath}. "
                f"Train the model first."
            )

        checkpoint = torch.load(str(filepath), map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()


class _SeverityLSTM:
    """Internal PyTorch LSTM module. Created via _import_torch()."""
    pass


# Replace _SeverityLSTM at import time with actual nn.Module
def _build_severity_lstm_class():
    """Build the nn.Module class after PyTorch is imported."""
    torch, nn = _import_torch()

    class SeverityLSTM(nn.Module):
        def __init__(self, vocab_size, embed_dim, hidden1, hidden2):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
            self.lstm1 = nn.LSTM(embed_dim, hidden1, batch_first=True)
            self.dropout1 = nn.Dropout(0.3)
            self.lstm2 = nn.LSTM(hidden1, hidden2, batch_first=True)
            self.dropout2 = nn.Dropout(0.3)
            self.fc1 = nn.Linear(hidden2, 32)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(32, 1)
            self.sigmoid = nn.Sigmoid()

        def forward(self, x):
            x = self.embedding(x)
            x, _ = self.lstm1(x)
            x = self.dropout1(x)
            x, _ = self.lstm2(x)
            x = self.dropout2(x[:, -1, :])  # Take last timestep
            x = self.relu(self.fc1(x))
            x = self.sigmoid(self.fc2(x))
            return x

    return SeverityLSTM


# Monkey-patch LSTMSeverityModel to use the real class at init time
_original_init = LSTMSeverityModel.__init__


def _patched_init(self, vocab_size, max_length, embed_dim=64, hidden1=128, hidden2=64):
    torch, nn = _import_torch()
    SeverityLSTM = _build_severity_lstm_class()

    self.vocab_size = vocab_size
    self.max_length = max_length
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    self.model = SeverityLSTM(
        vocab_size, embed_dim, hidden1, hidden2
    ).to(self.device)

    self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
    self.criterion = nn.BCELoss()

    print(f"[INFO] LSTM device: {self.device}")
    if self.device.type == "cuda":
        print(f"       GPU: {torch.cuda.get_device_name(0)}")


LSTMSeverityModel.__init__ = _patched_init


class CodeTokenizer:
    """
    Tokenizes code strings into integer sequences for the LSTM model.

    Builds a vocabulary from training data, then converts code to
    fixed-length integer sequences.
    """

    def __init__(self, max_vocab_size: int = 5000, max_length: int = 200):
        self.max_vocab_size = max_vocab_size
        self.max_length = max_length
        self.word_to_idx = {}
        self.idx_to_word = {}
        self._is_fitted = False

    def fit(self, code_samples: list) -> None:
        """Build vocabulary from a list of code strings."""
        all_tokens = []
        for code in code_samples:
            tokens = self._tokenize_code(code)
            all_tokens.extend(tokens)

        counter = Counter(all_tokens)
        most_common = counter.most_common(self.max_vocab_size - 2)

        self.word_to_idx = {"<PAD>": 0, "<UNK>": 1}
        for idx, (token, _) in enumerate(most_common, start=2):
            self.word_to_idx[token] = idx

        self.idx_to_word = {v: k for k, v in self.word_to_idx.items()}
        self._is_fitted = True

    def transform(self, code_samples: list) -> np.ndarray:
        """
        Convert code strings to padded integer sequences.

        Returns:
            2D numpy array of shape (n_samples, max_length).
        """
        if not self._is_fitted:
            raise RuntimeError("Tokenizer not fitted. Call fit() first.")

        sequences = []
        for code in code_samples:
            tokens = self._tokenize_code(code)
            indices = [
                self.word_to_idx.get(t, 1)  # 1 = <UNK>
                for t in tokens[:self.max_length]
            ]
            padded = indices + [0] * (self.max_length - len(indices))
            sequences.append(padded)

        return np.array(sequences, dtype=np.int32)

    def fit_transform(self, code_samples: list) -> np.ndarray:
        """Fit vocabulary and transform in one step."""
        self.fit(code_samples)
        return self.transform(code_samples)

    @property
    def vocab_size(self) -> int:
        """Return the vocabulary size (including PAD and UNK)."""
        return len(self.word_to_idx)

    @staticmethod
    def _tokenize_code(code: str) -> list:
        """
        Tokenize code into a list of meaningful tokens.
        Splits on whitespace, operators, and punctuation while
        preserving keywords and identifiers.
        """
        tokens = re.findall(
            r"[a-zA-Z_]\w*|[0-9]+\.?[0-9]*|[^\s\w]",
            code
        )
        return tokens
