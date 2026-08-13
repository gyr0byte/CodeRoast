"""
CodeRoast — NLP Quality Classifier
Classifies code into quality buckets using TF-IDF + Random Forest.

Quality Levels:
    0 = Pristine  (rare, almost mythical)
    1 = Acceptable (human wrote this)
    2 = Concerning (coffee needed)
    3 = Disaster   (please seek help)
"""

import os
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

import config


class CodeQualityClassifier:
    """
    Classifies code snippets into 4 quality buckets by combining
    TF-IDF character n-gram features with static analysis metrics.

    Usage:
        clf = CodeQualityClassifier()
        clf.train(code_samples, metric_features, labels)
        quality, confidence = clf.predict_quality(code, metrics)
    """

    QUALITY_LABELS = {
        0: "Pristine",
        1: "Acceptable",
        2: "Concerning",
        3: "Disaster",
    }

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",       # Character n-grams (works well for code)
            ngram_range=(2, 4),       # 2 to 4 character windows
            max_features=5000,        # Cap feature space
            strip_accents="unicode",
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,  # Use all CPU cores
        )
        self._is_fitted = False

    # ─── Training ────────────────────────────────────────────────────────

    def train(self, code_samples: list, metric_features: np.ndarray,
              labels: np.ndarray) -> dict:
        """
        Train the classifier on labeled code samples.

        Args:
            code_samples: List of code strings.
            metric_features: 2D array of static analysis metrics per sample.
            labels: 1D array of quality labels (0-3).

        Returns:
            Dictionary with training metrics (accuracy, cross-val scores).
        """
        # Fit and transform TF-IDF on code text
        tfidf_features = self.vectorizer.fit_transform(code_samples)

        # Combine TF-IDF features with static metrics
        combined = np.hstack([tfidf_features.toarray(), metric_features])

        # Train the Random Forest
        self.classifier.fit(combined, labels)
        self._is_fitted = True

        # Cross-validation scores
        cv_scores = cross_val_score(
            self.classifier, combined, labels, cv=5, scoring="accuracy"
        )

        return {
            "accuracy_mean": round(cv_scores.mean(), 4),
            "accuracy_std": round(cv_scores.std(), 4),
            "cv_scores": cv_scores.tolist(),
        }

    # ─── Prediction ──────────────────────────────────────────────────────

    def prepare_features(self, code: str, metrics: dict) -> np.ndarray:
        """
        Prepare feature vector for a single code sample.

        Args:
            code: The code string.
            metrics: Dictionary from CodeAnalyzer.get_metrics().

        Returns:
            2D numpy array (1 x n_features).
        """
        if not self._is_fitted:
            raise RuntimeError(
                "Classifier not fitted yet. Call train() or load_model() first."
            )

        tfidf_features = self.vectorizer.transform([code])
        metric_values = np.array([
            metrics.get("lines_of_code", 0),
            metrics.get("function_count", 0),
            metrics.get("avg_function_length", 0),
            metrics.get("cyclomatic_complexity", 1),
            metrics.get("naming_score", 50),
            metrics.get("comment_ratio", 0),
            metrics.get("nesting_depth", 0),
            metrics.get("duplicate_code_score", 100),
        ]).reshape(1, -1)

        return np.hstack([tfidf_features.toarray(), metric_values])

    def predict_quality(self, code: str, metrics: dict) -> tuple:
        """
        Predict the quality level of a code snippet.

        Args:
            code: The code string.
            metrics: Dictionary from CodeAnalyzer.get_metrics().

        Returns:
            Tuple of (quality_level: int, confidence: float).
        """
        features = self.prepare_features(code, metrics)
        quality_level = self.classifier.predict(features)[0]
        confidence = self.classifier.predict_proba(features)[0].max()
        return int(quality_level), round(float(confidence), 3)

    def get_quality_label(self, quality_level: int) -> str:
        """Get the human-readable label for a quality level."""
        return self.QUALITY_LABELS.get(quality_level, "Unknown")

    # ─── Evaluation ──────────────────────────────────────────────────────

    def evaluate(self, code_samples: list, metric_features: np.ndarray,
                 labels: np.ndarray) -> dict:
        """
        Evaluate the classifier on a test set.

        Returns:
            Dictionary with classification report and confusion matrix.
        """
        tfidf_features = self.vectorizer.transform(code_samples)
        combined = np.hstack([tfidf_features.toarray(), metric_features])
        predictions = self.classifier.predict(combined)

        report = classification_report(
            labels, predictions,
            target_names=list(self.QUALITY_LABELS.values()),
            output_dict=True,
        )
        conf_matrix = confusion_matrix(labels, predictions).tolist()

        return {
            "classification_report": report,
            "confusion_matrix": conf_matrix,
        }

    # ─── Persistence ─────────────────────────────────────────────────────

    def save_model(self, filename: str = "classifier.pkl") -> str:
        """Save the trained model and vectorizer to disk."""
        filepath = config.MODELS_DIR / filename
        os.makedirs(config.MODELS_DIR, exist_ok=True)

        joblib.dump({
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "is_fitted": self._is_fitted,
        }, filepath)

        return str(filepath)

    def load_model(self, filename: str = "classifier.pkl") -> None:
        """Load a trained model and vectorizer from disk."""
        filepath = config.MODELS_DIR / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"No saved model found at {filepath}. "
                f"Train the model first with train()."
            )

        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.classifier = data["classifier"]
        self.classifier.n_jobs = 1  # Force single thread for cloud container compatibility
        self._is_fitted = data["is_fitted"]
