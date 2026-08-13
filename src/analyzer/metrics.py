"""
CodeRoast — Metric Helpers & Normalization
Constants, thresholds, and utility functions used by CodeAnalyzer.
"""

# ─── Metric Thresholds ──────────────────────────────────────────────────────
# These define what "good" vs "bad" looks like for each metric.
# Used by the scoring system to map raw values to 0-100 scores.

METRIC_THRESHOLDS = {
    "cyclomatic_complexity": {
        "good": 5,       # <= 5 is clean
        "moderate": 10,  # 5-10 is acceptable
        "bad": 20,       # > 20 is spaghetti
    },
    "avg_function_length": {
        "good": 15,      # <= 15 lines per function
        "moderate": 30,  # 15-30 is okay
        "bad": 50,       # > 50 is a novel
    },
    "nesting_depth": {
        "good": 3,       # <= 3 levels
        "moderate": 5,   # 3-5 levels
        "bad": 8,        # > 8 is an inception dream
    },
    "comment_ratio": {
        "good": 0.15,    # >= 15% comments
        "moderate": 0.05, # 5-15% is bare minimum
        "bad": 0.02,     # < 2% is documentation-free zone
    },
    "naming_score": {
        "good": 80,      # >= 80% conventions followed
        "moderate": 60,  # 60-80% is sloppy
        "bad": 40,       # < 40% is chaos
    },
}


def normalize_score(value: float, lower_is_better: bool = True,
                    min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Normalize a raw metric value to a 0-100 score.

    Args:
        value: The raw metric value.
        lower_is_better: If True, lower raw values produce higher scores
                         (e.g., complexity). If False, higher raw values
                         produce higher scores (e.g., comment ratio).
        min_val: The minimum expected raw value.
        max_val: The maximum expected raw value.

    Returns:
        Normalized score between 0 and 100.
    """
    # Clamp to range
    clamped = max(min_val, min(value, max_val))

    # Normalize to 0-1
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (clamped - min_val) / (max_val - min_val)

    # Invert if lower is better (e.g., complexity: low = good = high score)
    if lower_is_better:
        normalized = 1.0 - normalized

    return round(normalized * 100, 1)


def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))
