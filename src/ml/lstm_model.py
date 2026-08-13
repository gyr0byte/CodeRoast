"""
CodeRoast — LSTM Severity Scorer
Deep learning model that predicts how severely code deserves to be roasted.

Uses a stacked LSTM to analyze tokenized code and output a severity
score between 0.0 (pristine) and 1.0 (maximum roast deserved).
"""

import os
import numpy as np

import config

# Lazy imports — TensorFlow is heavy, only load when needed
_tf = None
_keras = None


def _import_tensorflow():
    """Lazy import TensorFlow to avoid slow startup when not needed."""
    global _tf, _keras
    if _tf is None:
        import tensorflow as tf
        _tf = tf
        _keras = tf.keras
    return _tf, _keras


def build_roast_severity_model(vocab_size: int, max_length: int):
    """
    Build and compile the LSTM severity scoring model.

    Args:
        vocab_size: Size of the code token vocabulary.
        max_length: Maximum sequence length (tokens per code sample).

    Returns:
        Compiled tf.keras.Model.
    """
    tf, keras = _import_tensorflow()

    model = keras.Sequential([
        keras.layers.Embedding(vocab_size, 64, input_length=max_length),
        keras.layers.LSTM(128, return_sequences=True),
        keras.layers.Dropout(0.3),
        keras.layers.LSTM(64),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dense(1, activation="sigmoid"),  # Severity score 0-1
    ])

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def train_severity_model(model, X_train: np.ndarray, y_train: np.ndarray,
                         X_val: np.ndarray = None, y_val: np.ndarray = None,
                         epochs: int = 20, batch_size: int = 32) -> dict:
    """
    Train the LSTM severity model.

    Args:
        model: Compiled Keras model from build_roast_severity_model().
        X_train: Tokenized + padded code sequences (2D array).
        y_train: Severity scores (1D array, 0.0-1.0).
        X_val: Optional validation sequences.
        y_val: Optional validation scores.
        epochs: Number of training epochs.
        batch_size: Training batch size.

    Returns:
        Dictionary with training history.
    """
    tf, keras = _import_tensorflow()

    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss" if X_val is not None else "loss",
            patience=5,
            restore_best_weights=True,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss" if X_val is not None else "loss",
            factor=0.5,
            patience=3,
        ),
    ]

    validation_data = None
    if X_val is not None and y_val is not None:
        validation_data = (X_val, y_val)

    history = model.fit(
        X_train, y_train,
        validation_data=validation_data,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    return {
        "epochs_trained": len(history.history["loss"]),
        "final_loss": history.history["loss"][-1],
        "final_accuracy": history.history["accuracy"][-1],
        "history": {k: [float(v) for v in vals]
                    for k, vals in history.history.items()},
    }


def predict_severity(model, X: np.ndarray) -> np.ndarray:
    """
    Predict severity scores for code samples.

    Args:
        model: Trained Keras model.
        X: Tokenized + padded code sequences.

    Returns:
        1D array of severity scores (0.0 to 1.0).
    """
    predictions = model.predict(X, verbose=0)
    return predictions.flatten()


def save_severity_model(model, filename: str = "lstm_severity.h5") -> str:
    """Save the trained LSTM model to disk."""
    filepath = config.MODELS_DIR / filename
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    model.save(str(filepath))
    return str(filepath)


def load_severity_model(filename: str = "lstm_severity.h5"):
    """Load a trained LSTM model from disk."""
    tf, keras = _import_tensorflow()
    filepath = config.MODELS_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"No saved model found at {filepath}. "
            f"Train the model first."
        )

    return keras.models.load_model(str(filepath))


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
        from collections import Counter

        # Tokenize all code
        all_tokens = []
        for code in code_samples:
            tokens = self._tokenize_code(code)
            all_tokens.extend(tokens)

        # Build vocabulary from most common tokens
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
            # Pad to max_length
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
        import re
        # Split on whitespace, operators, and punctuation
        tokens = re.findall(
            r"[a-zA-Z_]\w*|[0-9]+\.?[0-9]*|[^\s\w]",
            code
        )
        return tokens
