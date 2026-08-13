"""
CodeRoast — Model Training Orchestration
Trains both the NLP quality classifier and the LSTM severity scorer.

Usage:
    python -m src.ml.train

This script:
    1. Loads the dataset from data/processed/code_samples.csv
    2. Extracts static analysis metrics for each sample
    3. Trains the TF-IDF + Random Forest classifier
    4. Trains the LSTM severity scorer
    5. Saves both models to models/
    6. Prints evaluation metrics
"""

import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import config
from src.analyzer.code_analyzer import CodeAnalyzer
from src.ml.classifier import CodeQualityClassifier
from src.ml.lstm_model import CodeTokenizer, LSTMSeverityModel


def load_dataset(filepath: str = None) -> pd.DataFrame:
    """
    Load the training dataset.

    Expected CSV columns:
        - code: The code snippet string
        - language: python, java, or javascript
        - quality_label: 0-3 quality level
        - severity_score: 0.0-1.0 roast severity
    """
    if filepath is None:
        filepath = config.DATA_PROCESSED_DIR / "code_samples.csv"

    if not os.path.exists(filepath):
        print(f"[ERROR] Dataset not found at: {filepath}")
        print("Run the GitHub scraping script first:")
        print("  python data/scrape_github.py")
        sys.exit(1)

    df = pd.read_csv(filepath)
    print(f"[INFO] Loaded {len(df)} samples from {filepath}")
    print(f"       Languages: {df['language'].value_counts().to_dict()}")
    print(f"       Quality distribution: {df['quality_label'].value_counts().to_dict()}")
    return df


def extract_metrics_batch(df: pd.DataFrame) -> np.ndarray:
    """
    Extract static analysis metrics for all code samples in the dataset.

    Returns:
        2D numpy array of shape (n_samples, 8) — one row per sample.
    """
    print("[INFO] Extracting metrics for all samples...")
    metric_keys = [
        "lines_of_code", "function_count", "avg_function_length",
        "cyclomatic_complexity", "naming_score", "comment_ratio",
        "nesting_depth", "duplicate_code_score",
    ]

    all_metrics = []
    for idx, row in df.iterrows():
        try:
            analyzer = CodeAnalyzer(row["code"], language=row.get("language", "python"))
            metrics = analyzer.get_metrics()
            all_metrics.append([metrics.get(k, 0) for k in metric_keys])
        except Exception as e:
            # Default metrics for unparseable code
            all_metrics.append([0, 0, 0, 1.0, 50.0, 0.0, 0, 100.0])

        if (idx + 1) % 100 == 0:
            print(f"       Processed {idx + 1}/{len(df)} samples...")

    print(f"[INFO] Metrics extracted for {len(all_metrics)} samples.")
    return np.array(all_metrics, dtype=np.float32)


def train_quality_classifier(df: pd.DataFrame, metric_features: np.ndarray) -> None:
    """Train and save the TF-IDF + Random Forest classifier."""
    print("\n" + "=" * 60)
    print("TRAINING: NLP Quality Classifier (TF-IDF + Random Forest)")
    print("=" * 60)

    clf = CodeQualityClassifier()

    # Split into train/test
    from sklearn.model_selection import train_test_split
    X_code = df["code"].tolist()
    y = df["quality_label"].values

    X_code_train, X_code_test, X_met_train, X_met_test, y_train, y_test = \
        train_test_split(X_code, metric_features, y, test_size=0.2, random_state=42,
                         stratify=y)

    # Train
    results = clf.train(X_code_train, X_met_train, y_train)
    print(f"\n[RESULTS] Cross-validation accuracy: "
          f"{results['accuracy_mean']:.4f} ± {results['accuracy_std']:.4f}")

    # Evaluate on test set
    eval_results = clf.evaluate(X_code_test, X_met_test, y_test)
    print("\n[RESULTS] Test Set Classification Report:")
    for label, metrics in eval_results["classification_report"].items():
        if isinstance(metrics, dict):
            print(f"  {label:15s}  precision={metrics['precision']:.3f}  "
                  f"recall={metrics['recall']:.3f}  f1={metrics['f1-score']:.3f}")

    print(f"\n[RESULTS] Confusion Matrix:")
    for row in eval_results["confusion_matrix"]:
        print(f"  {row}")

    # Save model
    path = clf.save_model()
    print(f"\n[SAVED] Classifier saved to: {path}")


def train_lstm_severity(df: pd.DataFrame) -> None:
    """Train and save the LSTM severity scorer (PyTorch)."""
    print("\n" + "=" * 60)
    print("TRAINING: LSTM Severity Scorer (PyTorch)")
    print("=" * 60)

    code_samples = df["code"].tolist()
    severity_scores = df["severity_score"].values.astype(np.float32)

    # Tokenize code
    print("[INFO] Tokenizing code samples...")
    tokenizer = CodeTokenizer(max_vocab_size=5000, max_length=200)
    X = tokenizer.fit_transform(code_samples)
    y = severity_scores

    # Split
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42,
    )

    print(f"[INFO] Vocab size: {tokenizer.vocab_size}")
    print(f"[INFO] Train: {len(X_train)}, Validation: {len(X_val)}")

    # Build and train model
    lstm = LSTMSeverityModel(
        vocab_size=tokenizer.vocab_size,
        max_length=tokenizer.max_length,
    )

    results = lstm.train(
        X_train, y_train, X_val, y_val,
        epochs=20, batch_size=32,
    )

    print(f"\n[RESULTS] Epochs trained: {results['epochs_trained']}")
    print(f"[RESULTS] Final loss: {results['final_loss']:.4f}")

    # Evaluate MAE on validation set
    predictions = lstm.predict(X_val)
    mae = np.mean(np.abs(predictions - y_val))
    print(f"[RESULTS] Validation MAE: {mae:.4f} (target: < 0.15)")

    # Save model
    path = lstm.save()
    print(f"\n[SAVED] LSTM model saved to: {path}")

    # Save tokenizer
    import joblib
    tokenizer_path = config.MODELS_DIR / "tokenizer.pkl"
    joblib.dump(tokenizer, tokenizer_path)
    print(f"[SAVED] Tokenizer saved to: {tokenizer_path}")


def main():
    """Run the full training pipeline."""
    print("CodeRoast — Model Training Pipeline")
    print("=" * 60)

    # 1. Load dataset
    df = load_dataset()

    # 2. Extract metrics
    metric_features = extract_metrics_batch(df)

    # 3. Train quality classifier
    train_quality_classifier(df, metric_features)

    # 4. Train LSTM severity scorer
    train_lstm_severity(df)

    print("\n" + "=" * 60)
    print("All models trained and saved to:", config.MODELS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
