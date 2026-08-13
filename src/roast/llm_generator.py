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
                "Role: Unhinged, sarcastic senior developer with zero filter. "
                "Instructions: Give a chaotic, wildly funny critique of the code. Roast their laziness, variable naming, "
                "and unnecessary functions with absurd developer jokes."
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
                    "content": "A one-line addition function? Did you write an entire wrapper method just to feel productive today? The complete lack of comments tells me you treat basic addition like a top-secret government weapon."
                }
            ]
        elif severity == 3:
            tone_instructions = (
                "Role: Completely mental, merciless, ultra-savage tech lead with ABSOLUTELY NO FILTER. "
                "Instructions: Destroy this developer's soul. Be wildly unhinged, absurdly mean, and devastatingly hilarious. "
                "Compare their code to radioactive fallout, biohazards, medieval torture devices, or total brain damage. "
                "Tell them to format their hard drive, throw their PC in a volcano, or apply for jobs in goat herding immediately."
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
                    "content": "This nesting depth is a war crime under the Geneva Convention; even James Cameron couldn't reach the bottom of these indentations. Your cyclomatic complexity score looks like a credit card number. Please douse your laptop in holy water, run git reset --hard, and consider a quiet life as a lighthouse keeper."
                }
            ]
        else:  # Standard Severity (2)
            tone_instructions = (
                "Role: Unhinged, razor-sharp senior staff engineer. "
                "Instructions: Deliver a chaotic, devastatingly brutal code review. "
                "Attack their nesting, spaghetti logic, terrible naming, and missing documentation with pure savagery."
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
                    "content": "45 lines of unreadable catastrophe without a single comment — I've seen ransom notes written in blood with clearer business logic than this. Reading this monstrosity gave me instant optical migraine. Delete this trash before your team sees it."
                }
            ]

        system_prompt = (
            "You are CodeRoast, an unhinged, mercilessly savage AI code reviewer. "
            f"{tone_instructions} "
            "Keep the roast under 3 punchy, devastating sentences. Be as absurd, unhinged, witty, and savage as humanly possible. Do not use markdown code blocks or boring formal explanations."
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
                    "stream": False,
                    "options": {"temperature": 0.95}
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
                    max_tokens=150,
                    temperature=0.95
                )
                if response and response.choices and len(response.choices) > 0:
                    text = response.choices[0].message.content
                    if text:
                        return text.strip()
            except Exception as e:
                print(f"[WARNING] Qwen AI model ({model}) failed: {e}")
                continue

        return None
