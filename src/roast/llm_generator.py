"""
CodeRoast — Dynamic LLM Roast Generator
Supports Hugging Face Serverless Inference API (on Cloud) and local PyTorch Transformers (on Local PC).
"""

import os
import requests
from typing import Optional
import config  # noqa: F401 — Sets HF_HOME first

MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"


class LLMRoastGenerator:
    """
    Generates dynamic, AI-powered code roasts using local Transformers model when running locally,
    or Hugging Face Serverless API when running on Cloud.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.tokenizer = None
        self.local_model = None
        self.device = None
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
        return token

    def _generate_hf_api(self, messages: list) -> Optional[str]:
        """Calls Hugging Face Serverless Inference API (uses 0 MB local RAM)."""
        token = self._get_hf_token()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        api_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.85,
            "top_p": 0.9,
        }

        try:
            res = requests.post(api_url, headers=headers, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        return content.strip()
        except Exception as e:
            print(f"[WARNING] HF Inference API call failed: {e}")

        return None

    def _load_local_model_if_needed(self) -> bool:
        """Lazy loader for local PyTorch Transformers execution."""
        # Never attempt heavy local model download on Streamlit Cloud to prevent freezes/OOM
        if os.path.exists("/mount/src"):
            return False

        if self.local_model is not None:
            return True

        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        local_model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

        try:
            print(f"[INFO] Loading local LLM model ({local_model_name}) on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(local_model_name, trust_remote_code=True)
            torch_dtype = torch.float16 if self.device.type == "cuda" else torch.bfloat16
            self.local_model = AutoModelForCausalLM.from_pretrained(
                local_model_name,
                dtype=torch_dtype,
                low_cpu_mem_usage=True,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True
            )
            if self.device.type != "cuda":
                self.local_model = self.local_model.to(self.device)
            return True
        except Exception as e:
            print(f"[WARNING] Failed to load local LLM model: {e}")
            return False

    def generate_roast(
        self,
        code: str,
        metrics: dict,
        quality_level: int,
        severity: int = 2
    ) -> Optional[str]:
        """
        Generates a dynamic roast text response:
        - On Cloud: Uses Hugging Face Serverless Cloud API (0 MB RAM).
        - On Local PC: Uses local PyTorch Transformers model on CPU/GPU.
        """
        severity_labels = {1: "Gentle & Witty", 2: "Standard Brutal", 3: "No Mercy Savage"}
        sev_label = severity_labels.get(severity, "Standard Brutal")

        system_prompt = (
            "You are CodeRoast, a brutally honest, hilarious senior developer reviewing user code. "
            "Your job is to roast the submitted code based on its metrics. "
            f"Set tone to: {sev_label}. "
            "Be technically accurate, witty, and savage. Keep the roast under 3-4 concise sentences. "
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

        # 1. On Streamlit Cloud: Use HF Serverless Cloud API
        if os.path.exists("/mount/src"):
            return self._generate_hf_api(messages)

        # 2. On Local PC: Use local PyTorch model directly
        if self._load_local_model_if_needed():
            try:
                import torch
                text_prompt = self.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                inputs = self.tokenizer([text_prompt], return_tensors="pt").to(self.device)
                with torch.no_grad():
                    generated_ids = self.local_model.generate(
                        **inputs,
                        max_new_tokens=150,
                        temperature=0.8,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                generated_ids = [
                    output_ids[len(input_ids):]
                    for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
                ]
                response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                return response.strip()
            except Exception as e:
                print(f"[ERROR] Error during local LLM generation: {e}")

        # Fallback to HF Cloud API if local model loading fails
        return self._generate_hf_api(messages)
