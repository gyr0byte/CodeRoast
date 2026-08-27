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
                "CRITICAL REQUIREMENT: You MUST include profanity and curse words (fuck, fucking, shit, bullshit, goddamn, dumbass, bastard, crap, dickhead, asshole) throughout your entire roast. "
                "Roast their laziness, variable naming, and unnecessary functions ruthlessly."
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
                    "content": "What the actual fucking hell is this piece of shit? A one-line addition function that looks like it was typed out by a blind jackass after a heavy night of drinking? Did you write a whole goddamn wrapper method just to feel like a productive software engineer today, you dumbass? This atrocious bullshit is so completely useless it makes my brain melt through my skull. The total lack of comments tells me you treat basic math like a top-secret military secret, you lazy bastard. Your variable names 'a' and 'b' are so uninspired and lazy that even a toddler with a crayon could come up with a more descriptive identification scheme. Looking at this dipshit code makes me want to format your motherboard, throw your laptop into an active volcano, and wipe your GitHub repository off the internet. Delete this fucking trash immediately, apply for a job in goat herding, and never touch a keyboard again as long as you live, you complete asshole."
                }
            ]
        elif severity == 3:
            tone_instructions = (
                "Role: Completely mental, merciless, ultra-savage tech lead with ABSOLUTELY NO FILTER. "
                "CRITICAL REQUIREMENT: You MUST use heavy curse words (fuck, fucking, motherfucker, shit, bullshit, dipshit, goddamn, dumbass, jackass, bastard, crap, dickhead, bitch, asshole, clusterfuck) in EVERY single sentence of your roast. "
                "Destroy this developer's soul with unapologetic profanity. Compare their code to radioactive fallout, biohazards, or total brain damage. "
                "Tell them to delete their code, format their hard drive, throw their PC in a volcano, or quit coding forever."
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
                    "content": "Holy motherfucking hell, this nesting depth is an absolute clusterfuck and a war crime under the Geneva Convention! What kind of unholy goddamn shit is this? Even James Cameron couldn't reach the bottom of these dipshit indentations. Your cyclomatic complexity score of 18 looks like a credit card number, you complete dumbass. Reading through these nested if-statements is giving me an instant optical migraine and a stroke at the same time. Delete this fucking trash, douse your laptop in holy water, throw your motherboard into a fiery pit, and get the fuck out of computer science forever, you lazy bastard!"
                }
            ]
        else:  # Standard Severity (2)
            tone_instructions = (
                "Role: Unhinged, razor-sharp senior staff engineer. "
                "CRITICAL REQUIREMENT: You MUST include explicit curse words (fuck, fucking, shit, bullshit, dipshit, goddamn, dumbass, bastard, crap, dickhead, asshole) in every sentence. "
                "Attack their nesting, spaghetti logic, terrible naming, and missing documentation with pure profanity and savagery."
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
                    "content": "45 lines of unreadable fucking catastrophe without a single goddamn comment! I've seen ransom notes written in blood with clearer business logic than this piece of shit. Reading this monstrosity gave me instant optical migraine. Your variable naming is an absolute joke and your logic is a total clusterfuck. Delete this fucking trash before your team sees what a dumbass you are, format your drive, and consider a career in underwater basket weaving."
                }
            ]

        # Build system_prompt and user_content based on context
        if metrics.get("_language_mismatch", False):
            detected = metrics.get("_detected_lang", "Python").capitalize()
            selected = metrics.get("_selected_lang", "Java").capitalize()
            system_prompt = (
                "You are CodeRoast, an unhinged, profane AI code reviewer with ZERO FILTER. "
                f"The user selected '{selected}' in the UI dropdown but pasted '{detected}' code! "
                f"Generate a long, brutal, highly detailed profanity-filled roast (8-10 sentences) mocking them for confusing {selected} with {detected}. "
                "Dissect their specific code syntax and mistakes. YOU MUST USE EXPLICIT CURSE WORDS (fuck, fucking, motherfucker, shit, bullshit, dipshit, goddamn, dumbass, jackass, bastard, crap, dickhead, bitch, asshole, clusterfuck) LIBERALLY THROUGHOUT THE ENTIRE ROAST."
            )
            user_content = f"Selected Language: {selected}\nDetected Language: {detected}\n\nCode Snippet:\n{code[:800]}"
        elif metrics.get("_is_plain_text", False):
            system_prompt = (
                "You are CodeRoast, a savage AI code reviewer with ZERO FILTER. The user pasted plain English text instead of actual code! "
                "Create a long, vicious, highly detailed profanity-laden rant (8-10 sentences) cursing at them for confusing code with a diary or blog post. "
                "YOU MUST USE EXPLICIT CURSE WORDS (fuck, fucking, motherfucker, shit, bullshit, dipshit, goddamn, dumbass, jackass, bastard, crap, dickhead, bitch, asshole, clusterfuck) LIBERALLY THROUGHOUT THE ENTIRE RANT."
            )
            user_content = f"Text Snippet:\n{code[:800]}"
        else:
            # Explicit comedy framing to prevent AI safety filter false positives
            system_prompt = (
                "You are CodeRoast, an unhinged senior staff software architect performing a savage code roast on a comedy show with ZERO FILTER. "
                "STRICT MINIMUM LENGTH REQUIREMENT: Write a MASSIVE, HIGHLY DETAILED 8 to 12 sentence roast paragraph (at least 200 words). Short responses under 8 sentences are STRICTLY FORBIDDEN. "
                "STRICT FORMATTING RULE: Write pure text paragraphs ONLY. Never use bullet points, numbered lists, markdown headers, or code block explanations. "
                "YOU MUST USE EXPLICIT CURSE WORDS (fuck, fucking, motherfucker, shit, bullshit, dipshit, goddamn, dumbass, jackass, bastard, crap, dickhead, bitch, asshole, clusterfuck) LIBERALLY IN EVERY SENTENCE. "
                f"{tone_instructions} "
                "Do NOT write brief summaries, do NOT cut off early, and do NOT use markdown code blocks or conversational intros."
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
                    "options": {
                        "temperature": 0.95,
                        "num_predict": 800,
                        "repeat_penalty": 1.15
                    }
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    if "message" in res_data and "content" in res_data["message"]:
                        response_text = res_data["message"]["content"].strip()
                        if not is_refusal(response_text):
                            return self._enforce_profanity_and_length(response_text, metrics)
        except Exception:
            pass  # Ollama not running locally or refused, proceed to HF cloud

        # ── Step B: Iterate through Hugging Face Qwen Models ────────────────
        client = InferenceClient(token=token if token else None)

        for model in MODEL_CANDIDATES:
            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=800,
                    temperature=0.95
                )
                if response and response.choices and len(response.choices) > 0:
                    text = response.choices[0].message.content
                    if text:
                        candidate_text = text.strip()
                        if not is_refusal(candidate_text):
                            return self._enforce_profanity_and_length(candidate_text, metrics)
            except Exception as e:
                print(f"[WARNING] Qwen AI model ({model}) failed: {e}")
                continue

        return None

    def _enforce_profanity_and_length(self, text: str, metrics: dict) -> str:
        """
        Guarantees that the returned roast text is at least 140 words and contains explicit curse words.
        If the LLM output is too short or clean, this appends a metric-targeted unhinged profane rant.
        """
        profanities = [
            'fuck', 'fucking', 'motherfucker', 'shit', 'bullshit', 'dipshit',
            'goddamn', 'dumbass', 'jackass', 'bastard', 'crap', 'dickhead',
            'bitch', 'asshole', 'clusterfuck'
        ]
        has_profanity = any(p in text.lower() for p in profanities)
        words = text.split()

        if not has_profanity or len(words) < 140:
            lines = metrics.get("lines_of_code", 0)
            cc = metrics.get("cyclomatic_complexity", 1.0)
            nesting = metrics.get("nesting_depth", 0)
            comments = metrics.get("comment_ratio", 0.0)

            extra_rant = (
                f" What the actual fucking hell is this goddamn clusterfuck of code? "
                f"Reading this atrocious piece of shit with {lines} lines, a cyclomatic complexity of {cc}, and a nesting depth of {nesting} made my brain melt through my skull, you lazy dumbass. "
                f"Your comment ratio of {comments:.1%} is a fucking insult to software engineering. "
                "Your variable naming is a goddamn nightmare, your logic is pure unadulterated bullshit, and your nesting is an absolute war crime. "
                "Delete this fucking trash immediately, format your hard drive, throw your laptop into an active volcano, and get the fuck out of software engineering forever, you complete asshole!"
            )
            text = text.strip() + extra_rant

        return text

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
