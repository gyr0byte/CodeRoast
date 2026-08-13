"""
CodeRoast — Static Analysis Module
Extracts objective code quality metrics using AST parsing (Python)
and regex-based analysis (Java, JavaScript).
"""

from src.analyzer.code_analyzer import CodeAnalyzer
from src.analyzer.metrics import normalize_score, METRIC_THRESHOLDS

__all__ = ["CodeAnalyzer", "normalize_score", "METRIC_THRESHOLDS"]
