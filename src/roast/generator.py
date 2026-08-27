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
        use_llm: bool = False,
        language: str = "english",
        gemini_key: Optional[str] = None
    ) -> str:
        """
        Generate a roast based on code metrics and quality assessment.

        Args:
            metrics: Dictionary from CodeAnalyzer.get_metrics()
            quality_level: 0 (Pristine) to 3 (Disaster)
            severity: 1 (Gentle), 2 (Standard), 3 (No Mercy)
            code: Original code string for LLM generation
            use_llm: Whether to attempt dynamic LLM text generation
            language: "english" or "roman_nepali"
            gemini_key: Optional Google Gemini API key for free cloud LLM generation

        Returns:
            A string containing the complete roast.
        """
        is_nepali = language.lower() in ["nepali", "roman_nepali", "roman nepali"]

        # Try dynamic LLM generation first if requested
        if use_llm and self.llm_generator is not None and code:
            from src.roast.llm_generator import is_refusal
            ai_roast = self.llm_generator.generate_roast(
                code=code,
                metrics=metrics,
                quality_level=quality_level,
                severity=severity,
                language=language,
                gemini_key=gemini_key
            )
            if ai_roast and not is_refusal(ai_roast):
                tag = "🤖 [Gemini Flash AI Roast]: " if gemini_key else "🤖 [Qwen2.5-Coder AI Roast]: "
                return f"{tag}{ai_roast}"

        # Static Nepali Fallback Template Matrix
        if is_nepali:
            from src.roast.templates import NEPALI_ROAST_TEMPLATES
            nepali_list = NEPALI_ROAST_TEMPLATES.get(severity, NEPALI_ROAST_TEMPLATES[2])
            return random.choice(nepali_list)

        roast_parts = []

        # ── Check for language mismatch ─────────────────────────────────
        if metrics.get("_language_mismatch", False):
            detected = metrics.get("_detected_lang", "Python").capitalize()
            selected = metrics.get("_selected_lang", "Java").capitalize()
            template = random.choice(self.templates.get("language_mismatch", []))
            roast_parts.append(template.format(detected=detected, selected=selected))
            return self._finalize(roast_parts, severity)

        # ── Check for plain text or syntax errors ───────────────────────
        if metrics.get("_is_plain_text", False):
            roast_parts.append(random.choice(self.templates["plain_text"]))
            return self._finalize(roast_parts, severity)

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

    def get_grade_reaction(
        self,
        grade: str,
        use_llm: bool = False,
        code: str = "",
        metrics: dict = None
    ) -> str:
        """
        Get a one-liner reaction for the letter grade (from Qwen AI if active, or template fallback).
        """
        if use_llm and self.llm_generator is not None and code:
            ai_reaction = self.llm_generator.generate_grade_reaction(grade, code, metrics or {})
            if ai_reaction:
                return ai_reaction

        letter = grade[0] if grade else "F"
        reactions = GRADE_REACTIONS.get(letter, ["No comment."])
        if isinstance(reactions, list):
            return random.choice(reactions)
        return reactions

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
