"""
CodeRoast — Static Code Analyzer
Extracts objective quality metrics from code snippets.

Supports:
  - Python  → Full AST-based analysis via `ast` and `radon`
  - Java    → Regex-based heuristic analysis
  - JavaScript → Regex-based heuristic analysis
"""

import ast
import re
import tokenize
import io
from collections import Counter
from typing import Optional

try:
    import radon.complexity as radon_cc
except ImportError:
    radon_cc = None


class CodeAnalyzer:
    """
    Analyzes a code snippet and extracts 8 quality metrics.

    Usage:
        analyzer = CodeAnalyzer(code_string, language="python")
        metrics = analyzer.get_metrics()
    """

    SUPPORTED_LANGUAGES = ("python", "java", "javascript")

    def __init__(self, code: str, language: str = "python"):
        self.code = code.strip()
        self.language = language.lower()
        self.lines = self.code.splitlines()
        self.tree: Optional[ast.AST] = None

        if self.language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: '{self.language}'. "
                f"Supported: {self.SUPPORTED_LANGUAGES}"
            )

        # Parse AST for Python only
        if self.language == "python":
            try:
                self.tree = ast.parse(self.code)
            except SyntaxError:
                self.tree = None

    def detect_actual_language(self) -> str:
        """
        Detects whether code is Python, Java, JavaScript, or unknown.
        """
        python_markers = [
            r"\bdef\s+\w+", r"\belif\b", r"\bself\.", r"\bisinstance\s*\(",
            r"^\s*#\s*\w+", r"\bprint\s*\(", r"\b__init__\b", r"\[\s*\w+\s+for\s+\w+\s+in\s+",
            r"\bfrom\s+\w+\s+import\b", r"\bimport\s+\w+", r"\bNone\b", r"\bTrue\b", r"\bFalse\b",
            r"\bpass\b", r"\brange\s*\(", r"\blen\s*\(", r":\s*$"
        ]
        java_markers = [
            r"\bpublic\s+class\b", r"\bpublic\s+static\s+void\b", r"\bSystem\.out\.print",
            r"\bString\[\]\s+args\b", r"\bimport\s+java\.", r"\bprivate\s+final\b",
            r"\bextends\s+\w+\b", r"\bimplements\s+\w+\b", r"\b@Override\b"
        ]
        js_markers = [
            r"\bconsole\.log\b", r"\bconst\s+\w+\s*=", r"\blet\s+\w+\s*=",
            r"\bvar\s+\w+\s*=", r"=>", r"\bdocument\.getElementById\b",
            r"\brequire\s*\(", r"\bmodule\.exports\b", r"\bexport\s+default\b"
        ]

        py_score = sum(1 for m in python_markers if re.search(m, self.code, re.MULTILINE))
        java_score = sum(1 for m in java_markers if re.search(m, self.code, re.MULTILINE))
        js_score = sum(1 for m in js_markers if re.search(m, self.code, re.MULTILINE))

        # Check if Python AST parsing succeeds
        try:
            ast.parse(self.code)
            py_score += 3
        except Exception:
            pass

        if py_score > java_score and py_score > js_score and py_score >= 1:
            return "python"
        elif java_score > py_score and java_score > js_score and java_score >= 1:
            return "java"
        elif js_score > py_score and js_score > java_score and js_score >= 1:
            return "javascript"

        return "unknown"


    def is_valid_code(self) -> bool:
        """
        Check if the input appears to be valid source code rather than plain text.
        """
        if self.language == "python" and self.tree is not None:
            return True

        code_patterns = [
            r"\bdef\s+\w+", r"\bclass\s+\w+", r"\bimport\s+\w+", r"\bfrom\s+\w+\s+import",
            r"\bfunction\s*\w*", r"\bconst\s+\w+", r"\blet\s+\w+", r"\bvar\s+\w+",
            r"\bpublic\s+(?:static\s+)?\w+", r"\bprivate\s+\w+", r"\bprotected\s+\w+",
            r"\bif\s*\(", r"\bfor\s*\(", r"\bwhile\s*\(", r"\breturn\b",
            r"\bprint\s*\(", r"\bconsole\.log\s*\(", r"\bSystem\.out\.print",
            r"=>", r"\{.*\}", r"\b[\w_]+\s*=\s*", r"#include", r"\bpackage\s+\w+",
            r"\bisinstance\s*\("
        ]
        
        matches = sum(1 for pattern in code_patterns if re.search(pattern, self.code, re.IGNORECASE))
        return matches >= 1

    # ─── Public API ──────────────────────────────────────────────────────────

    def get_metrics(self) -> dict:
        """
        Extract all 8 metrics from the code snippet.
        """
        is_code = self.is_valid_code()
        actual_lang = self.detect_actual_language()

        if self.language == "python":
            metrics = self._python_metrics()
        else:
            metrics = self._regex_metrics()

        if not is_code:
            metrics["_is_plain_text"] = True
            metrics["_syntax_error"] = True
        elif actual_lang != "unknown" and actual_lang != self.language:
            metrics["_language_mismatch"] = True
            metrics["_detected_lang"] = actual_lang
            metrics["_selected_lang"] = self.language

        return metrics

    # ─── Python AST-Based Analysis ───────────────────────────────────────────

    def _python_metrics(self) -> dict:
        """Full AST-powered analysis for Python code."""
        return {
            "lines_of_code": len(self.lines),
            "function_count": self._py_count_functions(),
            "avg_function_length": self._py_avg_function_length(),
            "cyclomatic_complexity": self._py_get_complexity(),
            "naming_score": self._py_check_naming_conventions(),
            "comment_ratio": self._py_comment_to_code_ratio(),
            "nesting_depth": self._py_max_nesting_depth(),
            "duplicate_code_score": self._detect_duplication(),
        }

    def _py_count_functions(self) -> int:
        """Count all function definitions (including methods)."""
        if self.tree is None:
            # Fallback: regex count for syntactically invalid Python
            return len(re.findall(r"^\s*def\s+\w+", self.code, re.MULTILINE))
        return sum(
            1 for node in ast.walk(self.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )

    def _py_avg_function_length(self) -> float:
        """Average number of lines per function."""
        if self.tree is None:
            return float(len(self.lines))

        functions = [
            node for node in ast.walk(self.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if not functions:
            return float(len(self.lines))

        lengths = []
        for func in functions:
            start = func.lineno
            end = max(
                getattr(node, "end_lineno", start)
                for node in ast.walk(func)
                if hasattr(node, "end_lineno")
            )
            lengths.append(end - start + 1)

        return round(sum(lengths) / len(lengths), 1)

    def _py_get_complexity(self) -> float:
        """Cyclomatic complexity via radon (average across all blocks)."""
        if radon_cc is None:
            # Fallback: count branching keywords
            return self._fallback_complexity()

        try:
            results = radon_cc.cc_visit(self.code)
            if not results:
                return 1.0
            return round(sum(r.complexity for r in results) / len(results), 1)
        except Exception:
            return self._fallback_complexity()

    def _py_check_naming_conventions(self) -> float:
        """
        Score naming conventions (0-100).
        Checks snake_case for functions/variables, UPPER_CASE for constants.
        """
        if self.tree is None:
            return 50.0  # Can't analyze — give neutral score

        score = 100.0
        penalty = 0

        for node in ast.walk(self.tree):
            # Functions should be snake_case
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = node.name
                if name.startswith("__") and name.endswith("__"):
                    continue  # Dunder methods are fine
                if not self._is_snake_case(name):
                    penalty += 10

            # Variables (assigned names) should be snake_case
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                name = node.id
                # Allow UPPER_CASE for constants (all caps)
                if name.isupper():
                    continue
                if not self._is_snake_case(name) and len(name) > 1:
                    penalty += 5

            # Class names should be PascalCase
            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    penalty += 10

        score = max(0, score - penalty)
        return round(score, 1)

    def _py_comment_to_code_ratio(self) -> float:
        """Ratio of comment lines to total lines."""
        if not self.lines:
            return 0.0

        comment_lines = 0
        in_docstring = False

        try:
            tokens = list(tokenize.generate_tokens(
                io.StringIO(self.code).readline
            ))
            for tok in tokens:
                if tok.type == tokenize.COMMENT:
                    comment_lines += 1
                elif tok.type == tokenize.STRING:
                    # Count docstrings as comments
                    val = tok.string.strip()
                    if val.startswith('"""') or val.startswith("'''"):
                        # Count lines within the docstring
                        comment_lines += tok.end[0] - tok.start[0] + 1
        except tokenize.TokenError:
            # Fallback: count lines starting with #
            comment_lines = sum(
                1 for line in self.lines if line.strip().startswith("#")
            )

        total = len(self.lines)
        if total == 0:
            return 0.0

        return round(comment_lines / total, 3)

    def _py_max_nesting_depth(self) -> int:
        """
        Maximum indentation nesting depth.
        Measures by counting leading whitespace levels.
        """
        if not self.lines:
            return 0

        max_depth = 0
        for line in self.lines:
            stripped = line.rstrip()
            if not stripped or stripped.startswith("#"):
                continue
            # Count leading spaces, convert to indent levels (4 spaces = 1)
            leading_spaces = len(line) - len(line.lstrip())
            depth = leading_spaces // 4
            max_depth = max(max_depth, depth)

        return max_depth

    # ─── Regex-Based Analysis (Java / JavaScript) ────────────────────────────

    def _regex_metrics(self) -> dict:
        """Heuristic analysis for Java and JavaScript using regex."""
        return {
            "lines_of_code": len(self.lines),
            "function_count": self._regex_count_functions(),
            "avg_function_length": self._regex_avg_function_length(),
            "cyclomatic_complexity": self._fallback_complexity(),
            "naming_score": self._regex_naming_score(),
            "comment_ratio": self._regex_comment_ratio(),
            "nesting_depth": self._regex_nesting_depth(),
            "duplicate_code_score": self._detect_duplication(),
        }

    def _regex_count_functions(self) -> int:
        """Count functions/methods using regex patterns."""
        if self.language == "java":
            # Match Java methods: access_modifier return_type methodName(
            pattern = r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\("
        else:
            # JavaScript: function declarations, arrow functions, methods
            pattern = r"(?:function\s+\w+\s*\(|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?function)"

        return len(re.findall(pattern, self.code, re.MULTILINE))

    def _regex_avg_function_length(self) -> float:
        """Estimate average function length by brace matching."""
        # Find function start positions by looking for opening braces after
        # function signatures
        total_lines = len(self.lines)
        func_count = self._regex_count_functions()

        if func_count == 0:
            return float(total_lines)

        # Rough estimate: total non-empty lines / function count
        non_empty = sum(1 for line in self.lines if line.strip())
        return round(non_empty / func_count, 1)

    def _regex_naming_score(self) -> float:
        """Check naming conventions for Java/JavaScript."""
        score = 100.0

        if self.language == "java":
            # Java: methods should be camelCase
            methods = re.findall(
                r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(",
                self.code
            )
            for name in methods:
                if name in ("main", "toString", "equals", "hashCode"):
                    continue
                if not self._is_camel_case(name):
                    score -= 10

            # Java: classes should be PascalCase
            classes = re.findall(r"class\s+(\w+)", self.code)
            for name in classes:
                if not name[0].isupper():
                    score -= 15

        elif self.language == "javascript":
            # JS: functions should be camelCase
            funcs = re.findall(r"function\s+(\w+)", self.code)
            funcs += re.findall(r"(?:const|let|var)\s+(\w+)\s*=", self.code)
            for name in funcs:
                if name.isupper() or name.startswith("_"):
                    continue  # Constants or private convention
                if not self._is_camel_case(name) and not self._is_snake_case(name):
                    score -= 8

        return max(0.0, round(score, 1))

    def _regex_comment_ratio(self) -> float:
        """Count comment lines for Java/JavaScript."""
        if not self.lines:
            return 0.0

        comment_lines = 0
        in_block_comment = False

        for line in self.lines:
            stripped = line.strip()

            if in_block_comment:
                comment_lines += 1
                if "*/" in stripped:
                    in_block_comment = False
                continue

            if stripped.startswith("//"):
                comment_lines += 1
            elif stripped.startswith("/*"):
                comment_lines += 1
                if "*/" not in stripped:
                    in_block_comment = True

        return round(comment_lines / len(self.lines), 3) if self.lines else 0.0

    def _regex_nesting_depth(self) -> int:
        """Measure max brace nesting depth for Java/JavaScript."""
        max_depth = 0
        current_depth = 0

        for char in self.code:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth = max(0, current_depth - 1)

        return max_depth

    # ─── Shared Helpers ──────────────────────────────────────────────────────

    def _fallback_complexity(self) -> float:
        """
        Estimate cyclomatic complexity by counting branching keywords.
        Works for all languages as a fallback.
        """
        if self.language == "python":
            keywords = ["if ", "elif ", "for ", "while ", "except ",
                        "and ", "or ", " if "]
        elif self.language == "java":
            keywords = ["if ", "else if", "for ", "while ", "switch ",
                        "case ", "catch ", "&&", "||", "?"]
        else:  # javascript
            keywords = ["if ", "else if", "for ", "while ", "switch ",
                        "case ", "catch ", "&&", "||", "?", "=>"]

        count = sum(self.code.count(kw) for kw in keywords)
        return max(1.0, float(count))

    def _detect_duplication(self) -> float:
        """
        Detect duplicate code blocks.
        Returns a score from 0-100 (0 = lots of duplication, 100 = no duplication).
        """
        if len(self.lines) < 4:
            return 100.0

        # Check for duplicate line groups (3-line windows)
        window_size = 3
        windows = []
        for i in range(len(self.lines) - window_size + 1):
            window = tuple(
                line.strip() for line in self.lines[i:i + window_size]
                if line.strip()  # Skip empty lines
            )
            if len(window) >= 2:
                windows.append(window)

        if not windows:
            return 100.0

        counts = Counter(windows)
        duplicates = sum(c - 1 for c in counts.values() if c > 1)
        duplication_ratio = duplicates / len(windows)

        # Convert to score: 0% duplication = 100, 50%+ = 0
        score = max(0, 100 - (duplication_ratio * 200))
        return round(score, 1)

    @staticmethod
    def _is_snake_case(name: str) -> bool:
        """Check if a name follows snake_case convention."""
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))

    @staticmethod
    def _is_camel_case(name: str) -> bool:
        """Check if a name follows camelCase convention."""
        return bool(re.match(r"^[a-z][a-zA-Z0-9]*$", name))
