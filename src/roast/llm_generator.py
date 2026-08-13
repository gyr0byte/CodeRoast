"""
CodeRoast — Dynamic LLM Roast Generator
Supports Hugging Face Serverless Inference (32B, 7B, 1.5B, 0.5B Qwen models)
and local Ollama fallback for 100% free, offline AI code roasts.
"""

import os
import json
import urllib.request
from typing import Optional
from huggingface_hub import InferenceClient
import config  # noqa: F401 — Sets HF_HOME first

# Prioritized list of Qwen models (from largest/best down to lightweight/free-tier friendly)
MODEL_CANDIDATES = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
]


class LLMRoastGenerator:
    """
    Generates dynamic, AI-powered code roasts using Qwen models.
    Supports Hugging Face Cloud GPUs and local Ollama.
    """

    def __init__(self, model_name: str = MODEL_CANDIDATES[0]):
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
        Generates a dynamic roast text response using Qwen AI.
        """
        token = self._get_hf_token()

        # 1. Direct Severity Mapping for System Instructions
        if severity == 1:
            tone_instructions = (
                "Role: Playful, mildly sarcastic peer reviewer. "
                "Instructions: Give a light, witty critique of the code metrics. Use gentle teasing "
                "but end on a supportive note reminding them that they can improve."
            )
            few_shot_examples = [
                {
                    "role": "user",
                    "content": (
                        "Language: Python\nLines of Code: 15\nCyclomatic Complexity: 1\nNesting Depth: 0\nComment Ratio: 0.0%\n\n"
                        "Code Snippet:\ndef add(a, b):\n    return a + b"
                    )
                },
                {
                    "role": "assistant",
                    "content": "A simple one-line adder function! It's clean and does exactly what it says, but zero comments? I guess you really wanted to keep the addition math a closely guarded secret. Keep practicing!"
                }
            ]
        elif severity == 3:
            tone_instructions = (
                "Role: Merciless, extremely savage senior developer. "
                "Instructions: Unleash absolute havoc. Use hyperbole, sharp tech analogies, and brutal sarcasm. "
                "Compare the code to historical disasters, trash cans, or pure spaghetti. "
                "Tell them to delete the file, start over, or consider a career shift."
            )
            few_shot_examples = [
                {
                    "role": "user",
                    "content": (
                        "Language: Python\nLines of Code: 120\nCyclomatic Complexity: 18\nNesting Depth: 6\nComment Ratio: 1.5%\n\n"
                        "Code Snippet:\ndef process_data(data):\n    if data:\n        for item in data:\n            if item.status == 'active':\n                ..."
                    )
                },
                {
                    "role": "assistant",
                    "content": "This nesting depth is a literal spelunking hazard; even Christopher Nolan couldn't follow these layers. Indentation so far right it's about to fall off the display. Please delete this, run git reset --hard HEAD~999, and consider a career in botany."
                }
            ]
        else:  # Standard Severity (2)
            tone_instructions = (
                "Role: Sarcastic, honest senior developer. "
                "Instructions: Provide a realistic, technically accurate code review roast. "
                "Use dry humor, developer tropes, and critique the metrics directly without being overly mean."
            )
            few_shot_examples = [
                {
                    "role": "user",
                    "content": (
                        "Language: Python\nLines of Code: 45\nCyclomatic Complexity: 8\nNesting Depth: 4\nComment Ratio: 0.0%\n\n"
                        "Code Snippet:\ndef handle_request(req):\n    ..."
                    )
                },
                {
                    "role": "assistant",
                    "content": "Forty-five lines in a single request handler and not a single comment to guide the lost souls reading it. Complexity is climbing faster than my blood pressure looking at this nesting. Do better."
                }
            ]

        system_prompt = (
            "You are CodeRoast, a hilariously honest code reviewer. "
            f"{tone_instructions} "
            "Keep the roast under 3 concise sentences. Do not use markdown formatting, code blocks, or explanations."
        )

        user_content = (
            f"Language: Python/JS/Java\n"
            f"Lines of Code: {metrics.get('lines_of_code', 0)}\n"
            f"Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 1.0)}\n"
            f"Nesting Depth: {metrics.get('nesting_depth', 0)}\n"
            f"Comment Ratio: {metrics.get('comment_ratio', 0.0):.1%}\n\n"
            f"Code Snippet:\n{code[:800]}"
        )

        # ── Step A: Check for Local Ollama Instance ─────────────────────────
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps({
                    "model": "qwen2.5-coder:1.5b",
                    "prompt": f"{system_prompt}\n\n{user_content}",
                    "stream": False
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    if "response" in res_data and res_data["response"]:
                        return res_data["response"].strip()
        except Exception:
            pass  # Ollama not running locally, proceed to HF cloud

        # ── Step B: Iterate through Hugging Face Qwen Models ────────────────
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(few_shot_examples)
        messages.append({"role": "user", "content": user_content})

        client = InferenceClient(token=token if token else None)

        for model in MODEL_CANDIDATES:
            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=120,
                    temperature=0.85
                )
                if response and response.choices and len(response.choices) > 0:
                    text = response.choices[0].message.content
                    if text:
                        return text.strip()
            except Exception as e:
                print(f"[WARNING] Qwen AI model ({model}) failed: {e}")
                continue

        return None
