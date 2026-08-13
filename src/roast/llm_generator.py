"""
CodeRoast — Dynamic LLM Roast Generator
Uses Local GTX 1060 GPU when running locally, and Hugging Face Serverless API when running on Cloud.
"""

import os
import requests
from typing import Optional
import config  # noqa: F401 — Sets HF_HOME first

MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"


class LLMRoastGenerator:
    """
    Generates dynamic, AI-powered code roasts using GTX 1060 local GPU
    or Hugging Face Serverless API when deployed on Cloud.
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
        return token.strip() if token else None

    def _generate_hf_api(self, messages: list) -> Optional[str]:
        """Calls Hugging Face Serverless Inference API (uses 0 MB local RAM, ~1.5s response)."""
        token = self._get_hf_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Endpoint 1: Hugging Face Router API (OpenAI compatible)
        api_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 120,
            "temperature": 0.85,
        }

        try:
            res = requests.post(api_url, headers=headers, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        return content.strip()
            else:
                print(f"[INFO] HF Router status {res.status_code}: {res.text[:150]}")
        except Exception as e:
            print(f"[WARNING] HF Router API call failed: {e}")

        # Endpoint 2: Direct Hugging Face Inference API
        direct_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        prompt_text = f"System: {messages[0]['content']}\nUser: {messages[1]['content']}\nAssistant:"
        direct_payload = {
            "inputs": prompt_text,
            "parameters": {"max_new_tokens": 120, "temperature": 0.85, "return_full_text": False}
        }

        try:
            res = requests.post(direct_url, headers=headers, json=direct_payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text", "")
                    if text:
                        return text.strip()
            else:
                print(f"[INFO] HF Direct API status {res.status_code}: {res.text[:150]}")
        except Exception as e:
            print(f"[WARNING] HF Direct API call failed: {e}")

        return None

    def _load_local_model_if_needed(self) -> bool:
        """Lazy loader for local PyTorch Transformers execution on GPU."""
        if os.path.exists("/mount/src"):
            return False

        if self.local_model is not None:
            return True

        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        local_model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

        try:
            print(f"[INFO] Loading local Qwen LLM model ({local_model_name}) on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(local_model_name, trust_remote_code=True)
            torch_dtype = torch.float16 if self.device.type == "cuda" else torch.bfloat16
            self.local_model = AutoModelForCausalLM.from_pretrained(
                local_model_name,
                torch_dtype=torch_dtype,
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
        - On Local PC: Uses GTX 1060 GPU directly (0.8s execution).
        - On Streamlit Cloud: Uses Hugging Face Serverless API (0 MB RAM).
        """
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

        # 1. On Local PC: Try GTX 1060 GPU model execution first
        if not os.path.exists("/mount/src"):
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
                            max_new_tokens=90,
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

        # 2. On Streamlit Cloud (/mount/src) or fallback: Use Hugging Face Cloud API
        api_roast = self._generate_hf_api(messages)
        if api_roast:
            return api_roast

        return None
