"""
CodeRoast — Dynamic LLM Roast Generator
Uses pre-trained `Qwen/Qwen2.5-Coder-1.5B-Instruct` from Hugging Face for dynamic, AI-generated code roasts.
"""

import torch
from typing import Optional
import config  # noqa: F401 — Sets HF_HOME first

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


class LLMRoastGenerator:
    """
    Generates dynamic, AI-powered code roasts using a local lightweight LLM.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name

        try:
            print(f"[INFO] Loading LLM Roast Model ({self.model_name}) on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            
            torch_dtype = torch.float16 if self.device.type == "cuda" else torch.float32
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch_dtype,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True
            )
            if self.device.type != "cuda":
                self.model = self.model.to(self.device)

            self._is_loaded = True
            print("[INFO] LLM Roast Model loaded successfully!")
        except Exception as e:
            print(f"[WARNING] Failed to load LLM model ({self.model_name}): {e}")
            self._is_loaded = False

    def generate_roast(
        self,
        code: str,
        metrics: dict,
        quality_level: int,
        severity: int = 2
    ) -> Optional[str]:
        """
        Generates a dynamic roast text response.
        Returns None if model is unavailable.
        """
        if not self._is_loaded:
            return None

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

        try:
            text_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            inputs = self.tokenizer([text_prompt], return_tensors="pt").to(self.device)

            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.8,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Strip prompt tokens
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response.strip()
        except Exception as e:
            print(f"[ERROR] Error during LLM generation: {e}")
            return None
