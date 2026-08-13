"""
CodeRoast — Score Calculator
Converts raw metrics into 4-dimension scores (0-100) and an overall grade.

Dimensions:
    1. Readability  — naming + comments + function length
    2. Efficiency   — cyclomatic complexity
    3. Structure    — nesting depth + duplication
    4. Creativity   — function decomposition (modular design)
"""


def calculate_scores(metrics: dict) -> dict:
    """
    Calculate scores across 4 dimensions from raw code metrics.

    Args:
        metrics: Dictionary from CodeAnalyzer.get_metrics()

    Returns:
        Dictionary with keys: readability, efficiency, structure,
        creativity, overall, grade
    """
    readability = _calc_readability(metrics)
    efficiency = _calc_efficiency(metrics)
    structure = _calc_structure(metrics)
    creativity = _calc_creativity(metrics)

    overall = (readability + efficiency + structure + creativity) / 4

    return {
        "readability": round(readability, 1),
        "efficiency": round(efficiency, 1),
        "structure": round(structure, 1),
        "creativity": round(creativity, 1),
        "overall": round(overall, 1),
        "grade": get_grade(overall),
    }


def _calc_readability(metrics: dict) -> float:
    """
    Readability = 40% naming + 30% comments + 30% function brevity.
    Higher is better.
    """
    naming = metrics.get("naming_score", 50.0) * 0.4
    comments = min(metrics.get("comment_ratio", 0.0) * 500, 100) * 0.3
    brevity = max(0, 100 - metrics.get("avg_function_length", 0)) * 0.3

    return _clamp(naming + comments + brevity)


def _calc_efficiency(metrics: dict) -> float:
    """
    Efficiency = inverse of cyclomatic complexity.
    Complexity of 1 = 100, complexity of 20 = 0.
    """
    complexity = metrics.get("cyclomatic_complexity", 1.0)
    return _clamp(100 - (complexity * 5))


def _calc_structure(metrics: dict) -> float:
    """
    Structure = combination of nesting depth and code duplication.
    50% nesting penalty + 50% duplication score.
    """
    nesting = metrics.get("nesting_depth", 0)
    duplication = metrics.get("duplicate_code_score", 100.0)

    nesting_score = max(0, 100 - (nesting * 10))
    structure = (nesting_score * 0.5) + (duplication * 0.5)

    return _clamp(structure)


def _calc_creativity(metrics: dict) -> float:
    """
    Creativity = function decomposition.
    More functions = more modular = higher score (up to a point).
    """
    func_count = metrics.get("function_count", 0)
    return _clamp(min(func_count * 10, 100))


def get_grade(score: float) -> str:
    """
    Convert an overall score (0-100) to a letter grade with description.

    Grade tiers:
        S  (90+)  — Suspiciously Good
        A  (75+)  — Actually Decent
        B  (60+)  — Barely Acceptable
        C  (45+)  — Concerning
        D  (30+)  — Deeply Troubling
        F  (<30)  — Please Seek Help
    """
    grades = [
        (90, "S — Suspiciously Good"),
        (75, "A — Actually Decent"),
        (60, "B — Barely Acceptable"),
        (45, "C — Concerning"),
        (30, "D — Deeply Troubling"),
        (0,  "F — Please Seek Help"),
    ]

    for threshold, grade in grades:
        if score >= threshold:
            return grade

    return "F — Please Seek Help"


def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))
