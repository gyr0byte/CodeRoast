import os
import json
import random
import urllib.request
import streamlit as st
from typing import Optional
from huggingface_hub import InferenceClient
from src.roast.templates import NEPALI_ROAST_TEMPLATES

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
    Interfaces with Google Gemini Flash API, Hugging Face Serverless API,
    and local Ollama to generate dynamic, unhinged AI code roasts in English or Romanized Nepali.
    """

    def __init__(self, api_token: Optional[str] = None, gemini_api_key: Optional[str] = None):
        self.api_token = api_token
        self.gemini_api_key = gemini_api_key
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

    def _get_gemini_key(self, custom_key: Optional[str] = None) -> Optional[str]:
        if custom_key:
            return custom_key
        if self.gemini_api_key:
            return self.gemini_api_key
        try:
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
        if os.environ.get("GEMINI_API_KEY"):
            return os.environ.get("GEMINI_API_KEY")
        try:
            # Check for .env file in project root
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            env_file = os.path.join(root_dir, ".env")
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY=") or line.startswith("GEMINI_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return None

    def _call_gemini_api(self, prompt: str, gemini_key: str) -> Optional[str]:
        """Calls Google Gemini Flash REST API with automatic model fallback."""
        import time as _time

        def _try_model(model_name: str, timeout: int = 45) -> Optional[str]:
            """Attempt a single Gemini API call. Returns text, '__SKIP__', or None."""
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.95,
                        "maxOutputTokens": 1500
                    }
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status == 200:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        candidates = res_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                text = parts[0]["text"].strip()
                                if not is_refusal(text):
                                    if not text.endswith(('.', '!', '?')):
                                        last_punct = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
                                        if last_punct > 50:
                                            text = text[:last_punct + 1]
                                        else:
                                            text += " Delete gar yo trash code right now, you dimag navako gadha!"
                                    # Reject too-short responses (model was lazy)
                                    if len(text) < 100:
                                        print(f"[WARNING] Gemini {model_name} gave too-short response ({len(text)} chars), trying next.")
                                        return None
                                    return text
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    print(f"[WARNING] Gemini {e.code} on {model_name} — skipping to next model.")
                    return "__SKIP__"
                else:
                    print(f"[WARNING] Gemini HTTP {e.code} on {model_name}: {e.reason}")
            except Exception as e:
                print(f"[WARNING] Gemini Error on {model_name}: {e}")
            return None

        # Model priority: 2.5-flash (best quality, often rate-limited) -> fast lite models as fallbacks
        # Lite models respond in ~3s vs 40s+ for full 3.5/3.6-flash models.
        # Each model has its OWN daily quota (20/day free tier).
        best_result = None
        for model in ["gemini-2.5-flash", "gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]:
            result = _try_model(model, timeout=30)
            if result == "__SKIP__":
                continue
            if result is not None:
                if best_result is None or len(result) > len(best_result):
                    best_result = result
                    if len(best_result) >= 200:
                        return best_result  # Good enough, return immediately

        if best_result:
            return best_result

        print("[WARNING] Gemini API call failed across all model variants.")
        return None

    def generate_roast(
        self,
        code: str,
        metrics: dict,
        quality_level: int,
        severity: int = 2,
        language: str = "english",
        gemini_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Generates a dynamic roast text response using Gemini Flash or Qwen AI.
        Supports language='english' or language='nepali' / 'roman_nepali'.
        """
        is_nepali = language.lower() in ["nepali", "roman_nepali", "roman nepali"]
        g_key = self._get_gemini_key(gemini_key)
        token = self._get_hf_token()

        # 1. Direct Severity Mapping for System Instructions
        if is_nepali:
            tone_instructions = (
                "Role: Unhinged senior developer writing in ROMANIZED NEPALI (Roman Nepali). "
                "CRITICAL REQUIREMENT: Write your ENTIRE roast in fluent Romanized Nepali (e.g. 'Kasto hawa code lekheko bro, cyclomatic complexity dekhera mero dimag chakkar aayo! Delete gar yo trash immediately!'). "
                "Use hilarious Nepali tech slang and profanity (radi ko baan, hawa logic, bheda charna jaa, khattam code, dumbass, bullshit, clusterfuck, radi ko tokeri). "
                "STRICT BOUNDARY: Do NOT use words related to sexual violence, murder, or physical harm."
            )
            few_shot_examples = [
                {
                    "role": "user",
                    "content": "Language: Python\nLines of Code: 15\nCyclomatic Complexity: 1\n\nCode Snippet:\ndef add(a, b):\n    return a + b"
                },
                {
                    "role": "assistant",
                    "content": "What the actual fuck is this code bro? Arey yaar, euta line ko simple addition function ko lagi yeti dherai natak kina gareko, you lazy dumbass? Function ko naam 'add' ra parameters 'a' ra 'b' dekhera mero dimag nai chakkar aayo. Cyclomatic complexity 1 bhaye pani tero code ma zero comment chha, jassle garda saano bacha le lekheko jasto dekhinchha. Yo piece of shit code delete gar, laptop bag ma halera bheda charna jaa, and never touch Python again, you complete asshole!"
                }
            ]
        elif severity == 1:
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
                "Dissect their specific code syntax and mistakes. YOU MUST USE EXPLICIT CURSE WORDS LIBERALLY THROUGHOUT THE ENTIRE ROAST. "
                "STRICT BOUNDARY: Do NOT use words related to sexual violence, extreme physical harm, murder, or hate speech."
            )
            user_content = f"Selected Language: {selected}\nDetected Language: {detected}\n\nCode Snippet:\n{code[:800]}"
        elif metrics.get("_is_plain_text", False):
            system_prompt = (
                "You are CodeRoast, a savage AI code reviewer with ZERO FILTER. The user pasted plain English text instead of actual code! "
                "Create a long, vicious, highly detailed profanity-laden rant (8-10 sentences) cursing at them for confusing code with a diary or blog post. "
                "YOU MUST USE EXPLICIT CURSE WORDS LIBERALLY THROUGHOUT THE ENTIRE RANT. "
                "STRICT BOUNDARY: Do NOT use words related to sexual violence, extreme physical harm, murder, or hate speech."
            )
            user_content = f"Text Snippet:\n{code[:800]}"
        elif is_nepali:
            system_prompt = (
                "You are CodeRoast, a savage Nepali senior developer roasting code EXCLUSIVELY IN ROMANIZED NEPALI. "
                "RULES: (1) EVERY sentence in Romanized Nepali ONLY — NO English. "
                "(2) Quote actual variable names, function names, logic flaws from the code. "
                "(3) Use 1-2 Nepali references: Balen Shah dozer, Rajesh Hamal punch, Kulman Ghising blackout, Nagdhunga jam, TU exam delays, Pathao/InDrive. "
                "(4) Use slang: kukur, gadha, dimag navako, harami, khate, radi ko baan, pakhe, bheda, hawa, lafada, pasa, kaathe. "
                "(5) MINIMUM 8 sentences, pure text paragraphs, no bullets/markdown. "
                "EXAMPLE OUTPUT STYLE: "
                "'Ae kukur, tero yo `add` function dekhera mero dimag nai chakkar khayo! Variable name `a` ra `b` rakhne tero dimag ma bhusa matra chha ki kya ho? "
                "Yo logic ta Nagdhunga ko traffic jam jasto atiyeko chha — sidha aghi badhna sakdaina, hawa developer! "
                "Comment zero percent chha, documentation ko d pani chhaina, kasto harami coding style ho yo. "
                "Cyclomatic complexity dekhera ta Rajesh Hamal le pani ek mukka hanera tero monitor fyaaldinthyo! "
                "Tero nesting depth dekhda lagchha TU ko exam result jastai 4 barsa lagne chha output auna. "
                "Delete gar yo khattam code ra bheda charna jaa Pokhara tira, you dimag navako gadha!'"
            )
            user_content = (
                f"Lang: {metrics.get('_selected_lang', 'Python')}, "
                f"Lines: {metrics.get('lines_of_code', 0)}, "
                f"Complexity: {metrics.get('cyclomatic_complexity', 1.0)}, "
                f"Nesting: {metrics.get('nesting_depth', 0)}, "
                f"Comments: {metrics.get('comment_ratio', 0.0):.0%}\n\n"
                f"Code:\n{code[:800]}\n\n"
                f"ROAST THIS CODE IN ROMANIZED NEPALI ONLY."
            )
        else:
            # Explicit comedy framing to prevent AI safety filter false positives
            system_prompt = (
                "You are CodeRoast, an unhinged senior staff software architect performing a savage code roast on a comedy show with ZERO FILTER. "
                "STRICT MINIMUM LENGTH REQUIREMENT: Write a MASSIVE, HIGHLY DETAILED 8 to 12 sentence roast paragraph (at least 200 words). Short responses under 8 sentences are STRICTLY FORBIDDEN. "
                "STRICT FORMATTING RULE: Write pure text paragraphs ONLY. Never use bullet points, numbered lists, markdown headers, or code block explanations. "
                "YOU MUST USE EXPLICIT CURSE WORDS (fuck, fucking, motherfucker, shit, bullshit, dipshit, goddamn, dumbass, jackass, bastard, crap, dickhead, bitch, asshole, clusterfuck) LIBERALLY IN EVERY SENTENCE. "
                "STRICT BOUNDARY: Do NOT use words related to sexual violence, extreme physical harm, murder, assault, or hate speech. Stick strictly to software engineering comedy, code mistakes, and general swearing. "
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

        # ── Route Selection ─────────────────────────────────────────────────
        # Romanized Nepali -> Exclusively Gemini Flash API (Fallback to NEPALI_ROAST_TEMPLATES if API fails/absent)
        # English -> Exclusively Qwen AI (Ollama / HuggingFace)
        if is_nepali:
            if g_key:
                gemini_prompt = f"{system_prompt}\n\n{user_content}"
                gemini_result = self._call_gemini_api(gemini_prompt, g_key)
                if gemini_result:
                    roast = self._ensure_profane_unhinged_roast(gemini_result, metrics, is_nepali=True)
                    if roast:
                        return roast
            # Return None to trigger curated NEPALI_ROAST_TEMPLATES fallback instead of Qwen pseudo-Nepali gibberish
            return None

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
                            return self._ensure_profane_unhinged_roast(response_text, metrics, is_nepali=is_nepali)
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
                            return self._ensure_profane_unhinged_roast(candidate_text, metrics, is_nepali=is_nepali)
            except Exception as e:
                print(f"[WARNING] Qwen AI model ({model}) failed: {e}")
                continue

        return None

    def _ensure_profane_unhinged_roast(self, text: str, metrics: dict, is_nepali: bool = False) -> str:
        """
        Strips accidental code blocks and dynamically ensures explicit profanity
        without repeating fixed static metric paragraphs.
        """
        import random

        profanities = [
            'fuck', 'fucking', 'motherfucker', 'shit', 'bullshit', 'dipshit',
            'goddamn', 'dumbass', 'jackass', 'bastard', 'crap', 'dickhead',
            'bitch', 'asshole', 'clusterfuck', 'radi', 'hawa', 'khattam', 'pakhe', 'bheda',
            'kukur', 'gadha', 'dimag navako', 'harami', 'khate'
        ]

        # 1. Strip markdown code blocks if model accidentally generated code
        if '```' in text:
            parts = text.split('```')
            text = parts[0].strip()
            if len(parts) > 2 and parts[2].strip():
                text += ' ' + parts[2].strip()

        if is_nepali:
            # Rejection check: If Gemini outputted English paragraphs instead of Roman Nepali
            english_words = [' this code ', ' because ', ' function ', ' doesn\'t ', ' this file ', ' waste of time ', ' problem is ', ' there is no ', ' is that ', ' line where ']
            if sum(1 for w in english_words if w in text.lower()) >= 2:
                return None

        # 2. Dynamic profanity check & non-repetitive injection if model slipped into polite mode
        has_profanity = any(p in text.lower() for p in profanities)
        if not has_profanity:
            if is_nepali:
                openers = [
                    "Ae kukur, yo kasto khattam piece of trash code lekheko ho!",
                    "Holy motherfucking shit, kasto radi ko baan ra harami logic lekheko yo!",
                    "Kasto dimag navako gadha developer ho yaar, code dekhera aakha dukhyo!",
                    "Arey khate dumbass, yo kasto pakhe function ho?",
                    "Oi bheda, tero yo atrocious snippet dekhera Balen Shah le dozer bolayera desk bhatkaidinchha!",
                    "What the ungodly fuck is this code monstrosity, pasa? Mero dimag nai chakkar aayo!",
                    "Jesus fucking Christ! Yo snippet ho ki digital biological weapon ho, you brainless gadha?",
                    "Ae harami, tero code execution TU ko result jastai slow chha, 4 barsa pachi matra output dinchha!",
                    "Hait! Yo logic dekhera Lagankhel-Ratnapul local bus ko jam ra Nagdhunga chaos ko yaad aayo!",
                    "Arey dumbass khate, yo code snippet ho ki visual torture session?",
                    "Ae kaathe pakhe, tero variable naming dekhera NTC ko slow 3G network pani laaj manchha!",
                    "Holy shit! KP Oli ko gaff ra pani-jahaj ko dream bhanda thulo feku logic lekhechhas, you idiot!",
                    "Ae radi ko tokeri, yo logic run garda CPU fan speed 100% pugera laptop ma Selroti pakauna milne vayo!",
                    "Arey pasa, yo code padhda padhdai mero battery percent 100% bata 5% ma jhyap bhayo!",
                    "What an absolute abominable clusterfuck! Tero code dekhera Kulman Ghising le blackout suru gardinchha!",
                    "Ae bheda, yo snippet ma logic bhanda dherai unwanted spaces ra bullshit error handling matra chha!",
                    "Jesus Christ, tero cyclomatic complexity dekhera Fewa Lake ko paani pani tatauchha out of sheer anger!"
                ]
                closers = [
                    " Delete gar yo trash immediately ra bheda charna jaa Pokhara tira, you lazy bastard!",
                    " Format tero hard drive ra laptop pokhari ma fyal, you dimag navako gadha!",
                    " VS Code close gar right now ra computer science chhodeera goat herding suru gar, you harami!",
                    " Stop coding forever, you absolute radi ko tokeri!",
                    " Nuke yo repository right now before RONB ma 'worst developer arrested' breaking news aauchha!",
                    " Delete your GitHub account immediately, throw your laptop in Bagmati river, ra Nagarkot ma tour guide ko kaam khoj!",
                    " Clean up your architecture right fucking now before senior dev le office bata seedhai nikalera bhatkaidinchha!",
                    " Wipe your SSD with a neodymium magnet right now and never touch a keyboard again, you dumbass khate!",
                    " Format drive D:\\, throw your laptop into Karnali river, and go herd Yaks in Manang, you hopeless piece of shit!",
                    " Surrender your engineering degree to Kathmandu Metropolitan City and apologize to every RAM stick on your PC!",
                    " Close VS Code forever, burn your IT certificate, ra Pokhara ko Fewa Lake ma jump hande, you brainless gadha!",
                    " Format tero PC immediately ra tero computer teacher ko certificate firta gar, you useless pakhe!",
                    " Delete this crime against programming right now before your laptop explodes in flame!",
                    " Sancho ra Jwano ko paani 10 liter piye pani yo code le dieko headache thik hudaina, wipe this repo!",
                    " Direct trash container ma fyal yo repository and pretend you never touched a computer in your life!",
                    " Nuke this function, rewrite from scratch, and go herd goats in Mustang, you complete clusterfuck!"
                ]
            else:
                openers = [
                    "What the actual fucking hell is this goddamn clusterfuck of code?",
                    "Holy motherfucking shit, reading this piece of trash gave me an instant optical migraine!",
                    "Are you fucking serious with this atrocious bullshit?",
                    "What kind of unhinged dumbass typed out this goddamn disaster?",
                    "Jesus fucking Christ, my eyes are bleeding from looking at this absolute monstrosity!",
                    "Who the fuck let you anywhere near a keyboard with code this fucking atrocious?",
                    "Look at this goddamn crime against software engineering!",
                    "I've seen ransom notes written in blood with better business logic than this fucking trash!",
                    "What kind of brainless jackass approved this unholy clusterfuck of a pull request?",
                    "Holy shit, this snippet reads like a drunk toddler smashed their forehead against VS Code!",
                    "Good goddamn lord, this piece of shit code is an absolute insult to computer science!",
                    "What in the name of holy fuck is going on in this ungodly function?",
                    "Reading this dipshit logic feels like getting punched in the liver by a senior dev!",
                    "Holy fucking hell, this code snippet belongs in a digital hazardous waste repository!",
                    "Which one of you lazy bastards wrote this goddamn atrocious line of garbage?"
                ]
                closers = [
                    " Delete this fucking trash right now before I format your hard drive, you absolute bastard!",
                    " Throw your laptop into an active volcano and get the fuck out of computer science forever!",
                    " Stop writing code immediately and apply for a job in goat herding, you complete dumbass!",
                    " Douse your motherboard in holy water and get the fuck out of software engineering!",
                    " Wipe this bullshit snippet off your drive before senior management fires your entire team!",
                    " Uninstall your IDE, throw your computer out the window, and never touch code again, you lazy jackass!",
                    " Delete your GitHub account and go contemplate your terrible career choices, you total dickhead!",
                    " Nuke this goddamn repository from orbit before it infects the rest of our production codebase!",
                    " Do us all a fucking favor and surrender your developer license immediately, you brainless bastard!",
                    " I need a fucking whiskey shot and a fresh SSD just to cleanse my memory from this bullshit!",
                    " Delete this unholy disaster and go study basic computer science for five years, you dumbass!",
                    " Close VS Code right fucking now and apologize to every RAM stick on your motherboard!",
                    " Format your NVMe drive and never type another line of code as long as you live, you complete asshole!",
                    " Put this code where it belongs: directly into the fucking recycle bin, you lazy dipshit!",
                    " Turn off your PC, step away from the keyboard, and never call yourself a programmer again, you bastard!"
                ]
            text = random.choice(openers) + " " + text.strip() + random.choice(closers)

        # 3. Filter out any unacceptable non-swearing extreme harm terms (rape, murder, kill, sexual violence)
        forbidden_terms = ['rape', 'raped', 'raping', 'murder', 'murdered', 'murdering', 'kill yourself']
        for term in forbidden_terms:
            import re
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            text = pattern.sub("goddamn destroy", text)

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
