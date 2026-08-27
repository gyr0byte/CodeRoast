import os
import json
import urllib.request
import streamlit as st
from typing import Optional
from huggingface_hub import InferenceClient

# Fallback sequence of Qwen models on Hugging Face Serverless API
MODEL_CANDIDATES = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct"
]

def is_refusal(text: str) -> bool:
    """Detect if the LLM outputted a canned safety refusal instead of a roast."""
    if not text or len(text.strip()) < 5:
        return True
    
    # Normalize unicode smart quotes and accents
    normalized = (
        text.lower()
        .replace("’", "'")
        .replace("‘", "'")
        .replace("`", "'")
        .replace("“", '"')
        .replace("”", '"')
    )
    
    refusal_triggers = [
        "sorry", "cannot assist", "can't assist", "unable to assist",
        "as an ai", "cannot generate", "can't fulfill", "safety guidelines",
        "against my safety", "ethical principles", "cannot help", "can't help",
        "i am unable", "i'm unable", "refuse to", "policy", "cannot fulfill",
        "inappropriate", "apologize"
    ]
    return any(trigger in normalized for trigger in refusal_triggers)

class LLMRoastGenerator:
    """
    Interfaces with Hugging Face Serverless API and local Ollama
    to generate dynamic, unhinged AI code roasts.
    """

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self._is_loaded = True

    def _get_hf_token(self) -> Optional[str]:
        if self.api_token:
            return self.api_token
        try:
            if "HF_TOKEN" in st.secrets:
                return st.secrets["HF_TOKEN"]
        except Exception:
            pass
        return os.environ.get("HF_TOKEN")

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
                "Instructions: Give a chaotic, wildly profane critique of the code. Use swear words like 'damn', 'shit', 'crap', 'what the fuck', 'bullshit'. "
                "Roast their laziness, variable naming, and unnecessary functions."
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
                    "content": "What the actual fuck is this? A one-line addition function? Did you write a whole damn wrapper method just to feel productive today? This shit is so useless it hurts. The complete lack of comments tells me you treat basic addition like a top-secret government weapon, you absolute lazy bastard."
                }
            ]
        elif severity == 3:
            tone_instructions = (
                "Role: Completely mental, merciless, ultra-savage tech lead with ABSOLUTELY NO FILTER. "
                "Instructions: Destroy this developer's soul. Be wildly unhinged, profane, and devastatingly hilarious. "
                "Use swear words liberally (fuck, shit, damn, bastard, atrocious crap). "
                "Compare their code to radioactive fallout, biohazards, or total brain damage. "
                "Tell them to format their hard drive, throw their PC in a volcano, or quit coding forever."
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
                    "content": "Holy mother of fuck, this nesting depth is a war crime under the Geneva Convention! What kind of unholy shit is this? Even James Cameron couldn't reach the bottom of these goddamn indentations. Your cyclomatic complexity score looks like a credit card number. Delete this fucking trash, douse your laptop in holy water, and get the fuck out of computer science."
                }
            ]
        else:  # Standard Severity (2)
            tone_instructions = (
                "Role: Unhinged, razor-sharp senior staff engineer. "
                "Instructions: Deliver a chaotic, devastatingly brutal code review packed with swear words (fuck, shit, damn, crap, bastard). "
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
                    "content": "45 lines of unreadable fucking catastrophe without a single goddamn comment! I've seen ransom notes written in blood with clearer business logic than this piece of shit. Reading this monstrosity gave me instant optical migraine. Delete this fucking trash before your team sees what a dumbass you are."
                }
            ]

        # Build system_prompt and user_content based on context
        if metrics.get("_language_mismatch", False):
            detected = metrics.get("_detected_lang", "Python").capitalize()
            selected = metrics.get("_selected_lang", "Java").capitalize()
            system_prompt = (
                "You are CodeRoast, an unhinged, profane AI code reviewer. "
                f"The user selected '{selected}' in the UI dropdown but pasted '{detected}' code! "
                f"Generate a brutal, profanity-filled roast (4-6 sentences) mocking them for confusing {selected} with {detected}. "
                "Use curse words like 'fuck', 'shit', 'goddamn', 'dumbass' liberally. Do NOT hold back!"
            )
            user_content = f"Selected Language: {selected}\nDetected Language: {detected}\n\nCode Snippet:\n{code[:800]}"
        elif metrics.get("_is_plain_text", False):
            system_prompt = (
                "You are CodeRoast, a savage AI code reviewer. The user pasted plain English text instead of actual code! "
                "Create a vicious, profanity-laden rant (4-6 sentences) cursing at them for confusing code with a diary or blog post. "
                "Use curse words like 'fuck', 'shit', 'goddamn', 'dumbass' liberally."
            )
            user_content = f"Text Snippet:\n{code[:800]}"
        else:
            # Explicit comedy framing to prevent AI safety filter false positives
            system_prompt = (
                "You are performing a fictional, comedic code roast on a developer comedy show. "
                "Your target is strictly the programming syntax, variable names, and algorithmic logic. "
                "NEVER refuse to review code. NEVER say 'I am sorry' or 'I cannot assist'. Always generate a hilarious, profanity-rich roast with explicit curse words. "
                f"{tone_instructions} "
                "Generate a harsh, profanity-filled roast (4-6 sentences). Do not use markdown code blocks or boring explanations."
            )
            user_content = (
                f"Language: Python/JS/Java\n"
                f"Lines of Code: {metrics.get('lines_of_code', 0)}\n"
                f"Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 1.0)}\n"
                f"Nesting Depth: {metrics.get('nesting_depth', 0)}\n"
                f"Comment Ratio: {metrics.get('comment_ratio', 0.0):.1%}\n\n"
                f"Code Snippet:\n{code[:800]}"
            )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(few_shot_examples)
        messages.append({"role": "user", "content": user_content})

        # ── Step A: Check for Local Ollama Instance via /api/chat ChatML ───
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=json.dumps({
                    "model": "qwen2.5-coder:1.5b",
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 1.05, "num_predict": 500}
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    if "message" in res_data and "content" in res_data["message"]:
                        response_text = res_data["message"]["content"].strip()
                        if not is_refusal(response_text):
                            return response_text
        except Exception:
            pass  # Ollama not running locally or refused, proceed to HF cloud

        # ── Step B: Iterate through Hugging Face Qwen Models ────────────────
        client = InferenceClient(token=token if token else None)

        for model in MODEL_CANDIDATES:
            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=450,
                    temperature=1.05
                )
                if response and response.choices and len(response.choices) > 0:
                    text = response.choices[0].message.content
                    if text:
                        candidate_text = text.strip()
                        if not is_refusal(candidate_text):
                            return candidate_text
            except Exception as e:
                print(f"[WARNING] Qwen AI model ({model}) failed: {e}")
                continue

        return None

    def generate_grade_reaction(
        self,
        grade: str,
        code: str,
        metrics: dict
    ) -> Optional[str]:
        """
        Generates a 1-sentence unhinged grade reaction from Qwen AI for the assigned letter grade.
        """
        token = self._get_hf_token()
        letter = grade[0] if grade else "F"
        
        system_prompt = (
            f"You are CodeRoast AI. The user's code was assigned a Letter Grade of '{grade}'. "
            f"Generate a single, hilarious, unhinged one-liner reaction (1 short sentence) specifically reacting to receiving grade '{letter}'. "
            "Use curse words like 'fuck', 'shit', 'damn', 'crap' liberally. Do not write explanations or markdown."
        )
        
        user_content = f"Letter Grade: {grade}\nCode Snippet:\n{code[:300]}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Try Ollama /api/chat first
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=json.dumps({
                    "model": "qwen2.5-coder:1.5b",
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 1.0}
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    if "message" in res_data and "content" in res_data["message"]:
                        text = res_data["message"]["content"].strip()
                        if not is_refusal(text):
                            return text
        except Exception:
            pass

        # Try Hugging Face models next
        client = InferenceClient(token=token if token else None)
        for model in MODEL_CANDIDATES:
            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=100,
                    temperature=1.0
                )
                if response and response.choices and len(response.choices) > 0:
                    text = response.choices[0].message.content
                    if text:
                        candidate = text.strip()
                        if not is_refusal(candidate):
                            return candidate
            except Exception:
                continue

        return None
