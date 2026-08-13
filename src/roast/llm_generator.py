"""
CodeRoast — Dynamic LLM Roast Generator
Uses Hugging Face Serverless InferenceClient (Qwen2.5-Coder-32B-Instruct Cloud GPUs).
"""

import os
from typing import Optional
from huggingface_hub import InferenceClient
import config  # noqa: F401 — Sets HF_HOME first

MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"


class LLMRoastGenerator:
    """
    Generates dynamic, AI-powered code roasts using Hugging Face Serverless API
    (Sub-2 second response via Cloud GPUs, 0 MB local RAM used).
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._is_loaded = True

    def _get_hf_token(self) -> Optional[str]:
        token = os.environ.get("HF_TOKEN")
        if not token:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "HF_TOKEN" in st.secrets:
                    token = st.secrets["HF_TOKEN"]
            except Exception:
                pass
        return token.strip() if token else None

    def generate_roast(
        self,
        code: str,
        metrics: dict,
        quality_level: int,
        severity: int = 2
    ) -> Optional[str]:
        """
        Generates a dynamic roast text response using Qwen2.5-Coder on HF Cloud GPU.
        """
        token = self._get_hf_token()
        severity_labels = {1: "Gentle & Witty", 2: "Standard Brutal", 3: "No Mercy Savage"}
        sev_label = severity_labels.get(severity, "Standard Brutal")

        system_prompt = (
            "You are CodeRoast, a brutally honest, hilarious senior developer reviewing user code. "
            "Your job is to roast the submitted code based on its metrics. "
            f"Set tone to: {sev_label}. "
            "Be technically accurate, witty, and savage. Keep the roast under 3 concise sentences. "
            "Do not output markdown code blocks or explanations, just the roast text."
        )

        user_content = (
            f"Language: Python/JS/Java\n"
            f"Lines of Code: {metrics.get('lines_of_code', 0)}\n"
            f"Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 1.0)}\n"
            f"Nesting Depth: {metrics.get('nesting_depth', 0)}\n"
            f"Comment Ratio: {metrics.get('comment_ratio', 0.0):.1%}\n\n"
            f"Code Snippet:\n{code[:800]}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Primary Hugging Face Serverless GPU model: Qwen2.5-Coder-32B-Instruct
        try:
            client = InferenceClient(token=token if token else None)
            response = client.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=120,
                temperature=0.85
            )
            if response and response.choices and len(response.choices) > 0:
                text = response.choices[0].message.content
                if text:
                    return text.strip()
        except Exception as e:
            print(f"[WARNING] Primary Qwen AI roast generation failed: {e}")

        # Secondary Hugging Face Serverless GPU model: Qwen2.5-72B-Instruct
        try:
            client = InferenceClient(token=token if token else None)
            response = client.chat_completion(
                messages=messages,
                model="Qwen/Qwen2.5-72B-Instruct",
                max_tokens=120,
                temperature=0.85
            )
            if response and response.choices and len(response.choices) > 0:
                text = response.choices[0].message.content
                if text:
                    return text.strip()
        except Exception as e:
            print(f"[WARNING] Secondary Qwen AI roast generation failed: {e}")

        return None
