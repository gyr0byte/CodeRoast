"""
CodeRoast — Roast Generator
Combines metrics and severity to produce dynamic, template-based roasts.
"""

import random
import re
from src.roast.templates import (
    ROAST_TEMPLATES,
    SEVERITY_MODIFIERS,
    GRADE_REACTIONS,
)


from src.roast.llm_generator import LLMRoastGenerator


class RoastGenerator:
    """
    Generates roasts by selecting and filling templates based on
    code analysis metrics, quality level, and severity setting,
    or using a local Hugging Face LLM if enabled.

    Usage:
        generator = RoastGenerator()
        roast = generator.generate_roast(metrics, quality_level=2, severity=2, use_llm=True)
    """

    def __init__(self, load_llm: bool = False):
        self.templates = ROAST_TEMPLATES
        self.severity_modifiers = SEVERITY_MODIFIERS
        self.llm_generator = None
        if load_llm:
            try:
                self.llm_generator = LLMRoastGenerator()
                if not self.llm_generator._is_loaded:
                    self.llm_generator = None
            except Exception:
                self.llm_generator = None

    def generate_roast(
        self,
        metrics: dict,
        quality_level: int,
        severity: int = 2,
        code: str = "",
        use_llm: bool = False
    ) -> str:
        """
        Generate a roast based on code metrics and quality assessment.

        Args:
            metrics: Dictionary from CodeAnalyzer.get_metrics()
            quality_level: 0 (Pristine) to 3 (Disaster)
            severity: 1 (Gentle), 2 (Standard), 3 (No Mercy)
            code: Original code string for LLM generation
            use_llm: Whether to attempt dynamic LLM text generation

        Returns:
            A string containing the complete roast.
        """
        # Try dynamic LLM generation first if requested
        if use_llm and self.llm_generator is not None and code:
            ai_roast = self.llm_generator.generate_roast(code, metrics, quality_level, severity)
            if ai_roast:
                return f"🤖 AI Roast: {ai_roast}"

        roast_parts = []

        # ── Check for syntax errors (Python AST failed) ─────────────────
        if metrics.get("_syntax_error", False):
            roast_parts.append(random.choice(self.templates["syntax_error"]))
            return self._finalize(roast_parts, severity)

        # ── Complexity roast ─────────────────────────────────────────────
        complexity = metrics.get("cyclomatic_complexity", 1.0)
        if complexity > 10:
            template = random.choice(self.templates["high_complexity"])
            roast_parts.append(
                template.format(
                    score=complexity,
                    count=int(complexity),
                )
            )

        # ── Function length roast ────────────────────────────────────────
        avg_length = metrics.get("avg_function_length", 0)
        if avg_length > 50:
            template = random.choice(self.templates["too_long"])
            roast_parts.append(
                template.format(lines=int(avg_length))
            )

        # ── Comment ratio roast ──────────────────────────────────────────
        comment_ratio = metrics.get("comment_ratio", 0.0)
        if comment_ratio < 0.05:
            template = random.choice(self.templates["no_comments"])
            roast_parts.append(
                template.format(ratio=round(comment_ratio * 100, 1))
            )

        # ── Naming conventions roast ─────────────────────────────────────
        naming_score = metrics.get("naming_score", 100.0)
        if naming_score < 60:
            template = random.choice(self.templates["bad_naming"])
            # Try to find a bad variable name to feature in the roast
            bad_name = self._find_bad_name(metrics)
            roast_parts.append(
                template.format(name=bad_name)
            )

        # ── Nesting depth roast ──────────────────────────────────────────
        nesting = metrics.get("nesting_depth", 0)
        if nesting > 5:
            template = random.choice(self.templates["deep_nesting"])
            roast_parts.append(
                template.format(depth=nesting)
            )

        # ── Duplication roast ────────────────────────────────────────────
        dup_score = metrics.get("duplicate_code_score", 100.0)
        if dup_score < 50:
            roast_parts.append(
                random.choice(self.templates["duplicate_code"])
            )

        # ── Too few functions roast ──────────────────────────────────────
        func_count = metrics.get("function_count", 0)
        loc = metrics.get("lines_of_code", 0)
        if func_count <= 1 and loc > 30:
            template = random.choice(self.templates["too_few_functions"])
            roast_parts.append(
                template.format(count=func_count, lines=loc)
            )

        # ── Praise for genuinely good code ───────────────────────────────
        if quality_level == 0 and not roast_parts:
            roast_parts.append(random.choice(self.templates["praise"]))

        # ── Fallback: use general roast if nothing triggered ─────────────
        if not roast_parts:
            roast_parts.append(random.choice(self.templates["general"]))

        return self._finalize(roast_parts, severity)

    def get_grade_reaction(self, grade: str) -> str:
        """
        Get a one-liner reaction for the letter grade.

        Args:
            grade: Full grade string like "S — Suspiciously Good"

        Returns:
            A reaction string.
        """
        letter = grade[0] if grade else "F"
        return GRADE_REACTIONS.get(letter, "No comment.")

    def _finalize(self, roast_parts: list, severity: int) -> str:
        """
        Combine roast parts and add a severity modifier.
        Limits output to at most 3 roast segments to avoid overwhelming.
        """
        # Cap at 3 roasts to keep it punchy
        if len(roast_parts) > 3:
            roast_parts = random.sample(roast_parts, 3)

        # Add severity modifier
        modifier_level = max(1, min(severity, 3))
        modifier = random.choice(self.severity_modifiers[modifier_level])
        roast_parts.append(modifier)

        return " ".join(roast_parts)

    @staticmethod
    def _find_bad_name(metrics: dict) -> str:
        """
        Try to find a specific bad variable name to feature in the roast.
        Falls back to a generic placeholder if none found.
        """
        bad_names = metrics.get("_bad_names", [])
        if bad_names:
            return random.choice(bad_names)
        return "x"  # Classic bad name
