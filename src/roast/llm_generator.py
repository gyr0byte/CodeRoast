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
        self._cached_ollama_model = None

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

    def _get_ollama_model(self) -> str:
        """Detect installed model from local Ollama instance, prioritizing llama3.2:3b, with caching."""
        if self._cached_ollama_model is not None:
            return self._cached_ollama_model

        model_name = "llama3.2:3b"
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    installed = [m.get("name", "") for m in data.get("models", [])]
                    for pref in ["llama3.2:3b", "llama3.2", "llama3.2:latest", "llama3.2:1b", "qwen2.5-coder:1.5b", "qwen2.5-coder"]:
                        for inst in installed:
                            if inst == pref or inst.startswith(pref):
                                model_name = inst
                                self._cached_ollama_model = model_name
                                return model_name
                    if installed:
                        model_name = installed[0]
        except Exception:
            pass

        self._cached_ollama_model = model_name
        return model_name

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

    def _extract_code_smells(self, code: str, metrics: dict) -> list:
        """
        Analyze AST metrics and code text to extract specific, named code smells
        for the LLM to roast explicitly by name.
        """
        import re
        smells = []

        # 1. Terrible/lazy variable names
        generic_names = {'temp', 'tmp', 'data', 'val', 'value', 'res', 'result', 'obj', 'foo', 'bar', 'baz', 'stuff', 'thing', 'item', 'x', 'y', 'z', 'a', 'b', 'c', 'n'}
        words = set(re.findall(r'\b[a-zA-Z_]\w*\b', code))
        bad_found = words.intersection(generic_names)
        if bad_found:
            smells.append(f"Lazy generic variable names: {', '.join(sorted(bad_found)[:5])}")

        # 2. Hardcoded / Magic numbers
        magic_numbers = [m for m in re.findall(r'(?<![a-zA-Z0-9_])([0-9]{2,})(?![a-zA-Z0-9_])', code) if m not in ('100', '0')]
        if len(magic_numbers) >= 2:
            smells.append(f"Unexplained magic numbers: {', '.join(magic_numbers[:4])}")

        # 3. Nesting depth
        nesting = metrics.get("nesting_depth", 0)
        if nesting >= 4:
            smells.append(f"Catastrophic indentation ({nesting} nesting levels) — pyramid of doom")
        elif nesting >= 2:
            smells.append(f"Deeply nested logic ({nesting} levels)")

        # 4. Comments / Documentation
        comment_ratio = metrics.get("comment_ratio", 0.0)
        if comment_ratio == 0.0:
            smells.append("Zero comments or docstrings (completely undocumented mystery meat)")
        elif comment_ratio < 0.05:
            smells.append(f"Practically zero documentation ({comment_ratio:.1%} comments)")

        # 5. Cyclomatic Complexity
        cc = metrics.get("cyclomatic_complexity", 1.0)
        if cc >= 8:
            smells.append(f"Dangerously high cyclomatic complexity ({cc})")
        elif cc >= 4:
            smells.append(f"High branching complexity ({cc})")

        # 6. Silent error swallowing or print debugging
        if "except:" in code or "except Exception:" in code:
            if "pass" in code:
                smells.append("Silent exception swallowing (`except ...: pass`)")
        if re.search(r'\bprint\s*\(', code) and metrics.get('language', '').lower() == 'python':
            smells.append("Using raw `print()` statements for debugging instead of proper logging")

        # 7. Function length
        avg_fn_len = metrics.get("avg_function_length", 0)
        if avg_fn_len > 30:
            smells.append(f"Bloated monolithic function ({avg_fn_len} lines avg)")

        if not smells:
            smells.append("Questionable architectural structure and questionable naming")

        return smells

    def _prepare_prompt_and_messages(
        self,
        code: str,
        metrics: dict,
        quality_level: int,
        severity: int = 2,
        language: str = "english",
        grade: Optional[str] = None
    ):
        """
        Builds the system prompt, few-shot examples, and user content for LLM generation.
        """
        is_nepali = language.lower() in ["nepali", "roman_nepali", "roman nepali"]

        # 1. Direct Severity Mapping for System Instructions
        length_rule = (
            " MANDATORY LENGTH REQUIREMENT: Your roast MUST be an extended, unhinged rant of AT LEAST 75 TO 120 WORDS (minimum 5 to 7 full sentences). "
            "Do NOT stop after 1 or 2 short sentences. Go completely crazy and breakdown every code flaw in intense detail!"
        )
        if is_nepali:
            tone_instructions = (
                "Role: Unhinged senior developer writing in ROMANIZED NEPALI (Roman Nepali). "
                "CRITICAL REQUIREMENT: Write your ENTIRE roast in fluent Romanized Nepali (e.g. 'Kasto hawa code lekheko bro, cyclomatic complexity dekhera mero dimag chakkar aayo! Delete gar yo trash immediately!'). "
                "Use hilarious Nepali tech slang and profanity (dimag navako gadha, hawa logic, bheda charna jaa, khattam code, dumbass, bullshit, clusterfuck, pakhe harami, khate). "
                "STRICT EXCLUSION RULE: Absolutely NEVER use the word 'randikhola' or 'randi' under any circumstances." + length_rule
            )
            few_shot_examples = [
                {
                    "role": "user",
                    "content": "Language: Python\nLines of Code: 15\nCyclomatic Complexity: 1\n\nCode Snippet:\ndef add(a, b):\n    return a + b"
                },
                {
                    "role": "assistant",
                    "content": "What the actual fuck is this code bro? Euta line ko addition function ko lagi yeti dherai natak kina gareko, you lazy dumbass? Function ko naam 'add' ra parameters 'a' ra 'b' dekhera dimag nai chakkar aayo. Zero comments, hawa logic! Yo piece of shit code delete gar, laptop bag ma halera bheda charna jaa, ani format gar tero system right now, you complete asshole!"
                }
            ]
        elif severity == 1:
            tone_instructions = (
                "Role: Unhinged, sarcastic senior developer with zero filter. "
                "CRITICAL REQUIREMENT: You MUST include profanity and curse words (fuck, fucking, shit, bullshit, goddamn, dumbass, bastard, crap, dickhead, asshole) throughout your entire roast. "
                "Roast their laziness, variable naming, and unnecessary functions ruthlessly." + length_rule
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
                    "content": "What the actual fuck is this one-line addition function? Did you write a whole goddamn wrapper method just to pretend you're a real engineer today, you dumbass? Your variable names 'a' and 'b' look like a toddler scribbled them with broken crayons. Not a single goddamn comment anywhere, as if basic addition is a classified military secret. Delete this bullshit trash immediately, close your laptop, and go apply for goat herding before anyone on your team sees this."
                }
            ]
        elif severity == 3:
            tone_instructions = (
                "Role: Completely mental, merciless, ultra-savage tech lead with ABSOLUTELY NO FILTER. "
                "CRITICAL REQUIREMENT: You MUST use heavy curse words (fuck, fucking, motherfucker, shit, bullshit, dipshit, goddamn, dumbass, jackass, bastard, crap, dickhead, bitch, asshole, clusterfuck) in EVERY single sentence of your roast. "
                "Destroy this developer's soul with unapologetic profanity. Compare their code to radioactive fallout, biohazards, or total brain damage." + length_rule
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
                    "content": "Holy motherfucking shit, what biological hazard did you drag out of the digital sewer? Look at this goddamn nesting depth — an absolute clusterfuck and a war crime! Cyclomatic complexity 18 with 1.5% comments is pure insult to computer science, you dipshit. Your logic looks like a drunk raccoon smashed your keyboard during an earthquake. Delete this fucking garbage, smash your SSD with a sledgehammer, and never touch code again, you hopeless bastard!"
                }
            ]
        else:  # Standard Severity (2)
            tone_instructions = (
                "Role: Unhinged, razor-sharp senior staff engineer. "
                "CRITICAL REQUIREMENT: You MUST include explicit curse words (fuck, fucking, shit, bullshit, dipshit, goddamn, dumbass, bastard, crap, dickhead, asshole) in every sentence. "
                "Attack their nesting, spaghetti logic, terrible naming, and missing documentation with pure profanity and savagery." + length_rule
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
                    "content": "45 lines of unreadable fucking catastrophe without a single goddamn comment! I've seen ransom notes written in blood with clearer business logic than this piece of shit. Reading this monstrosity gave me instant optical migraine. Your variable naming is an absolute joke and your logic is a total clusterfuck. There is literally no redeeming quality to any of these lines. Delete this fucking trash before your team sees what a dumbass you are, format your drive, and consider a career in underwater basket weaving."
                }
            ]

        # Build system_prompt and user_content based on context
        if metrics.get("_language_mismatch", False):
            detected = metrics.get("_detected_lang", "Python").capitalize()
            selected = metrics.get("_selected_lang", "Java").capitalize()
            if is_nepali:
                system_prompt = (
                    "Role: Unhinged senior developer writing in ROMANIZED NEPALI (Roman Nepali). "
                    f"CRITICAL: The user selected '{selected}' in the UI dropdown but pasted '{detected}' code! "
                    f"Generate a brutal, hilarious roast in ROMANIZED NEPALI mocking them for confusing {selected} with {detected}! "
                    "Use funny Nepali tech slang (dimag navako, hawa logic, bheda, khattam code, dumbass, bullshit, khate). "
                    "STRICT BOUNDARY: Do NOT use words related to sexual violence, extreme physical harm, or hate speech."
                )
            else:
                system_prompt = (
                    "You are CodeRoast, an unhinged, profane AI code reviewer with ZERO FILTER. "
                    f"The user selected '{selected}' in the UI dropdown but pasted '{detected}' code! "
                    f"Generate a long, brutal, highly detailed profanity-filled roast (8-10 sentences) mocking them for confusing {selected} with {detected}. "
                    "Dissect their specific code syntax and mistakes. YOU MUST USE EXPLICIT CURSE WORDS LIBERALLY THROUGHOUT THE ENTIRE ROAST. "
                    "STRICT BOUNDARY: Do NOT use words related to sexual violence, extreme physical harm, murder, or hate speech."
                )
            user_content = f"Selected Language in UI: {selected}\nDetected Code Language: {detected}\n\nCode Snippet:\n{code[:800]}"

        elif metrics.get("_is_plain_text", False):
            system_prompt = (
                "You are CodeRoast, a savage AI code reviewer with ZERO FILTER. The user pasted plain English text instead of actual code! "
                "Create a long, vicious, highly detailed profanity-laden rant (8-10 sentences) cursing at them for confusing code with a diary or blog post. "
                "YOU MUST USE EXPLICIT CURSE WORDS LIBERALLY THROUGHOUT THE ENTIRE RANT. "
                "STRICT BOUNDARY: Do NOT use words related to sexual violence, extreme physical harm, murder, or hate speech."
            )
            user_content = f"Text Snippet:\n{code[:800]}"
        elif is_nepali:
            import random as _rand

            # ═══════════════════════════════════════════════════════════════
            # DYNAMIC THEME PICKER — 20 Cultural Theme Pools
            # Each roast gets 2-3 random themes mixed together for variety
            # ═══════════════════════════════════════════════════════════════
            theme_pools = [
                # Theme 1: Kathmandu chaos & traffic
                "Yo code Kalanki chowk ko scooter chaos jasto chha. Ratnapul ko bus conductor jasto chichchyayera variable declare gareko. NTC ko 3G network bhanda slow algorithm. Bagmati river ko pollution jasto toxic architecture.",
                # Theme 2: Nepali politics & leaders
                "KP Oli ko pani-jahaj dream jasto unrealistic logic. Deuba ko 'arey bhai k bolya' jastai compiler confused. Prachanda ko U-turn jasto flip-flopping conditionals. Rabi Lamichhane ko case jasto tangled spaghetti code.",
                # Theme 3: Nepali student life & TU
                "TU ko exam result jastai 4 barsa lagchha output auna. Hostel ko dal bhat jasto bland function. IOE entrance ko tension jasto nested loops. Lumbini ICT Park ko promise jasto — announce bhayo tara kaam kahilei bhayena.",
                # Theme 4: Nepali food & culture
                "Achar navako momo jasto dry ra tasteless code. Selroti jasto gol-gol infinite loop. Newari bhoj ko level nai chhaina tero architecture ma. Juju Dhau jasto mitho huna sakthyo tara tero logic le bigaaryo.",
                # Theme 5: Balen Shah & infrastructure
                "Balen Shah le dozer chalaayera yo codebase bhatkaidinchha. Melamchi ko paani jasto — pipeline ta chha tara flow aaudaina. Dharahara jastai ek earthquake ma collapse hune fragile structure. Ring Road ko pothole jasto bug-ridden.",
                # Theme 6: Entertainment & sports
                "Rajesh Hamal ko ek mukka le tero monitor nai futnechha. Prakash Saput ko 'Galbandi' jasto dramatic error handling. Nepal vs Namibia cricket match jasto unexpected output. Dayahang Rai ko acting bhanda ni fake tero error messages.",
                # Theme 7: Daily Nepali life
                "Nagdhunga ko traffic jam jasto deadlocked threads. Pathao driver le location nabhete jasto pointer lost. InDrive ko bargaining jasto — k ho yo price negotiation logic? Jwano paani piye pani yo code ko headache thik hudaina. Load-shedding era ko inverter jasto unreliable fallback.",
                # Theme 8: Nepali internet & social media
                "RONB ma breaking news auchha 'developer arrested for crimes against code.' Meme Nepal page ma viral hune level ko cringe code. NEPSE ko share jasto aja bullish bholi bearish — kei consistency chhaina. Tero code Meanwhile in Nepal ma feature hune level ko disaster.",
                # Theme 9: Nepali IT industry & job market
                "Tero code dekhera Leapfrog, Fusemachines sabai le reject handinchha. Upwork ma $3/hour ma ni yo code ko quality paaudaina. Deerwalk ko intern le pani yesto code lekhne haina. Tero LinkedIn profile ma 'Full Stack Developer' lekheko dekhera recruiter haru hasera pagal bhaye.",
                # Theme 10: Nepali festivals & traditions
                "Dashain ko tika lagaune bela tero code review garnu paryo — kasto ashubha! Tihar ko deusi bhailo jastai tero function eutai geet gairacha loop ma. Holi ko rang jasto scattered ra messy variables. Chhath ma ghanta bhar paani ma ubhinu bhanda ni painful yo code padhna.",
                # Theme 11: Nepali geography & landmarks
                "Everest ko height jasto tero nesting depth — oxygen mask chainchha padhna. Pokhara ko paragliding jasto free-falling logic — kei control chhaina. Chitwan ko jungle safari jasto wild ra unpredictable output. Lumbini jastai peace milne bhanthyo tara tero code le ta war suru garyo.",
                # Theme 12: Nepali music & pop culture
                "Vten ko rap jasto aggressive tara meaning zero tero variable names. 1974 AD ko 'Parelima' sun — tero code pani 1974 ko jasto outdated chha. Neetesh Jung Kunwar ko auto-tune jasto — surface ma ramro tara bhitra hollow logic. Arthur Gunn American Idol ma pugyo tara tero code ta audition round mai out huncha.",
                # Theme 13: Nepali transportation & commute
                "Sajha bus ko schedule jasto — kabhi aauncha kabhi aaudaina tero function return. Micro tempo ma 20 jana thuneko jasto tero array ma unnecessary elements. Nepal Airlines ko flight cancel jasto tero API call — promise garera deliver gardaina. Tero code ta rickshaw ko speed ma chaldai cha bullet train ko zamana ma.",
                # Theme 14: Nepali education system
                "SLC (Iron Gate) pass garnu jasto difficult tero code padhna. Tero code review garda HSEB ko 5 subject back bhayo jasto feel hunchha. Bridge course padhera doctor banne jasto — tero code ma shortcut matra chha fundamentals zero. Tero variable naming IOE ko handwriting jasto — lekhne le pani padhna sakdaina.",
                # Theme 15: Nepali economy & daily struggles
                "Dollar ko rate badheko jasto tero bug count din din badhdai cha. Load-shedding 18 ghanta ko jamana jasto tero server uptime. Gas cylinder line jasto — queue ma basera pani output aaudaina. Pasal ma MRP bhanda mahango bechne jasto tero code ma unnecessary overhead.",
                # Theme 16: Nepali weather & seasons
                "Terai ko garmi jasto — tero CPU le pani pasina pochirachha yo code run garda. Kathmandu ko dhulo jasto dusty ra unmaintained codebase. Monsoon ko baadhee jasto overflow error aairachha. Winter ko tundra jasto frozen chha tero logic — kei move nai gardaina.",
                # Theme 17: Nepali family dynamics & relatives
                "Kaka-kaki le 'padh padh' bhane jasto tero senior dev le 'refactor refactor' bhanirachha. Mamaghar jada mamu le chocolate diye jasto — tero function le pani eutai return value matra dinchha. Buhari-sasu ko relation jasto tero frontend-backend communication — duitira frustration. Bhai-tika ma didi le 'ramro code lekh' bhanera ashirwad dinchha tara tero code le sunna manncha?",
                # Theme 18: Nepali news & controversies
                "Wide body scandal jasto tero code ma hidden bugs chha. Baluwatar land grab jasto — memory leak le jagga khairacha tero RAM ko. Fake Bhutanese refugee scam jasto tero authentication logic ma loopholes. Nirmala Panta case jasto — investigation gardai chhas tara bug kahilei bhetdainas.",
                # Theme 19: Nepali proverbs & sayings twisted
                "Hatti aayo hatti aayo, fussa — tero function call pani yestai, promise garera kehi return gardaina. Gorkhali lai dare hannu — tero try-catch block le error lai dare handaina, sidhai crash hunchha. Aafno haath jagannath — tero code ta aafnai haath le nai bigareko. Kukur ko puchchar 12 barsa dhungro ma rakheni — tero coding habit pani yestai, kabhi sudhridaina.",
                # Theme 20: Nepali startup & hustle culture
                "Tero code CTO banne sapana dekhcha tara intern level logic chha. Startup pitch competition ma 'AI-powered disruption' bhanera yo spaghetti code dekhauchas? Ncell ko recharge jasto — paisa kharcha bhayo tara data aayena tero function bata. Tero GitHub green squares dekhera lagcha productive chhas tara yo commit history ho ki crime history?",
            ]

            # Pick 2-3 random themes for maximum variety
            num_themes = _rand.choice([2, 2, 2, 3])
            selected_themes = _rand.sample(theme_pools, num_themes)
            theme_inspiration = " ".join(selected_themes)

            # ═══════════════════════════════════════════════════════════════
            # SLANG SETS — 8 rotating sets of authentic Nepali developer slang
            # ═══════════════════════════════════════════════════════════════
            slang_sets = [
                "kukur, gadha, dimag navako, harami, khate, pakhe, bheda",
                "hawa, khattam, lafada, pasa, kaathe, jhyaap, boka, gidi",
                "chappar, boksi ko chela, sungur, gadha ko baccha, baal xaina, hait, tori",
                "dangadung, futsal cancel, tori budhi, gobar dimag, ghanti bajyo, ullu, bakhra",
                "andha, lato, bahira, mungri, tapori, fataha, langada logic, bokya",
                "murkha, buddhu, thakali thali jasto overloaded, bagmati ko paani jasto unclear, paagal",
                "ban manchhe, junglee coder, kachyaang, suruwal kholdai coding, fohor code, sarkari kaam jasto slow",
                "phokat ko gyaan, nakali developer, jhilke code, falthu function, dherai halla kam kaam",
            ]
            selected_slang = _rand.choice(slang_sets)

            # ═══════════════════════════════════════════════════════════════
            # PERSONALITY TONES — 12 unique roasting personas
            # ═══════════════════════════════════════════════════════════════
            tones = [
                "Roast like a frustrated Nepali senior dev who just saw intern code at 2am.",
                "Roast like a sarcastic Nepali uncle reviewing his nephew's code at Dashain dinner.",
                "Roast like a Nepali tech Twitter troll who lives to destroy bad PRs.",
                "Roast like a savage Nepali standup comedian performing at LOD Kathmandu.",
                "Roast like a Nepali gaming streamer rage-quitting after seeing this code.",
                "Roast like a disappointed Nepali college professor marking final year projects at TU.",
                "Roast like a Nepali rickshaw driver giving life advice while stuck in Lagankhel traffic.",
                "Roast like a Nepali army drill sergeant who just discovered his recruit writes code like this.",
                "Roast like a Kathmandu cafe intellectual sipping overpriced coffee while judging peasant code.",
                "Roast like a bitter Nepali freelancer on Upwork who lost a contract to someone writing code like this.",
                "Roast like a Nepali WhatsApp group uncle who forwards everything but finally found something worth criticizing.",
                "Roast like a Nepali mom comparing this code to how much better the neighbor's son codes.",
            ]
            selected_tone = _rand.choice(tones)

            # ═══════════════════════════════════════════════════════════════
            # ROAST STRUCTURE TEMPLATES — forces the AI to organize its burn
            # ═══════════════════════════════════════════════════════════════
            structures = [
                "Structure: Start with a shocked exclamation, then attack 3 specific code issues, compare each to a Nepali cultural situation, and end with a dramatic verdict telling them to quit coding.",
                "Structure: Open with a fake compliment ('Wah kya code!'), then systematically destroy every function and variable name, weave in cultural references, finish with a devastating one-liner.",
                "Structure: Pretend you're writing a RONB breaking news article about this code disaster — headline, body, and a dramatic conclusion urging the developer to surrender.",
                "Structure: Narrate like a Nepali cricket commentary — 'First over ma nai duck out', describing each code flaw as a batting collapse, building to an innings defeat.",
                "Structure: Write as if this code caused a national emergency — describe the government response, public outrage, and the developer being summoned to Singhadurbar.",
                "Structure: Start with 'Yo code dekhera...' and describe a chain reaction of disasters it causes across Nepal — from Kathmandu to Pokhara to Biratnagar — ending with the whole nation demanding you stop coding.",
                "Structure: Roast like a Nepali movie review — rate each function like a scene, give the overall code a rating, and tell the developer their code flopped harder than a Kollywood C-grade film.",
                "Structure: Build the roast like escalating disasters — start small (pothole), escalate (earthquake), climax (tero code le poora tech industry ruin garyo), end with exile recommendation.",
            ]
            selected_structure = _rand.choice(structures)

            # ═══════════════════════════════════════════════════════════════
            # SIGNATURE CLOSERS — memorable ending lines
            # ═══════════════════════════════════════════════════════════════
            closers = [
                "End with a memorable Nepali-style verdict sentencing them to quit coding forever.",
                "End by recommending a specific alternative career: momo pasal, bheda charaune, Nagarkot tour guide, tempo driver, or daal-bhat cooking.",
                "End with a fake 'breaking news' headline about this developer being banned from all computers in Nepal.",
                "End with a dramatic goodbye letter to their code — 'Alvida tero function, tero loop, tero variable — sabai ko antim sanskar gardinchu.'",
                "End by imagining Balen Shah personally arriving with a dozer to demolish their codebase.",
                "End with 'Tero code ko autopsy report' — listing cause of death for each function.",
                "End by giving their code a Nepali movie title and a star rating (0.5 stars).",
            ]
            selected_closer = _rand.choice(closers)

            system_prompt = (
                f"You are CodeRoast, a savage Nepali developer roasting code EXCLUSIVELY IN ROMANIZED NEPALI. "
                f"PERSONALITY: {selected_tone} "
                f"LANGUAGE RULE: EVERY sentence MUST be Romanized Nepali. NO English paragraphs or explanations. "
                f"CODE ANALYSIS: Quote actual variable names, function names, logic flaws. Be SPECIFIC about what is wrong. "
                f"CULTURAL FLAVOR FOR THIS ROAST: {theme_inspiration} "
                f"SLANG TO USE: {selected_slang}. "
                f"{selected_structure} "
                f"{selected_closer} "
                f"STRICT BOUNDARY: NEVER use explicit sexual vulgarities or offensive phrases (do NOT use words like 'radi', 'radi ko baan', 'kando', 'muji', 'lado', 'bhalu', or 'chikne'). Keep it strictly to software engineering comedy, cultural memes, and non-sexual insults. "
                f"Write 8-12 sentences of pure savage Romanized Nepali. No bullets, no markdown, no code blocks. "
                f"Be CREATIVE and ORIGINAL every time — never repeat the same jokes."
            )
            detected_smells = self._extract_code_smells(code, metrics)
            smells_str = ", ".join(detected_smells[:3])
            user_content = (
                f"Lang: {metrics.get('_selected_lang', 'Python')}, "
                f"Lines: {metrics.get('lines_of_code', 0)}, "
                f"Complexity: {metrics.get('cyclomatic_complexity', 1.0)}, "
                f"Nesting: {metrics.get('nesting_depth', 0)}, "
                f"Comments: {metrics.get('comment_ratio', 0.0):.0%}\n"
                f"Flaws to Roast: {smells_str}\n\n"
                f"Code:\n{code[:800]}\n\n"
                f"ROAST THIS CODE IN ROMANIZED NEPALI ONLY."
            )
        else:
            import random as _rand

            actual_language = metrics.get('_selected_lang', language).capitalize()

            # ── Short keyword-level hints (NOT full paragraphs for Qwen to copy-paste) ──
            flavor_hints = _rand.choice([
                "failed Silicon Valley startup", "Stack Overflow roast", "r/programminghorror post",
                "failed FAANG interview", "Cyberpunk 2077 launch bugs", "Game of Thrones Season 8 betrayal",
                "enterprise Jira nightmare", "ChatGPT hallucination", "3am startup hustle disaster",
                "Linus Torvalds flame war", "Friday deploy PagerDuty apocalypse", "Boeing 737 MAX software disaster"
            ])

            persona_hint = _rand.choice([
                "burnt-out FAANG staff engineer", "Gordon Ramsay reviewing code", "sarcastic Reddit mod",
                "Silicon Valley VC seeing bad code", "drunk CS professor at 2am", "competitive LeetCode grinder",
                "DevOps engineer paged at 3am", "sarcastic British tech journalist",
                "veteran open source maintainer", "sentient AI offended by bad code"
            ])

            closer_hint = _rand.choice([
                "devastating career change recommendation", "fake git commit message",
                "therapy cost calculation", "Rotten Tomatoes score (single digit)",
                "imaginary Glassdoor review", "formal resignation letter from the code itself"
            ])

            system_prompt = (
                f"You are CodeRoast, a savage code roaster on a comedy show. "
                f"Channel the energy of a {persona_hint}. "
                f"Write one continuous profane roast paragraph (8-12 sentences, 200+ words). "
                f"Use curse words (fuck, shit, bullshit, goddamn, dumbass, asshole, clusterfuck) in every sentence. "
                f"Quote actual variable names and function names from the code. Be specific about flaws. "
                f"Draw inspiration from: {flavor_hints}. "
                f"End with: {closer_hint}. "
                f"Language is {actual_language} — do NOT mention other languages. "
                f"No bullet points, no markdown, no helpful advice, no tool suggestions. Pure unhinged comedy roast only."
            )
            detected_smells = self._extract_code_smells(code, metrics)
            smells_str = "\n".join(f"- {s}" for s in detected_smells)
            user_content = (
                f"Language: {actual_language}\n"
                f"Lines of Code: {metrics.get('lines_of_code', 0)}\n"
                f"Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 1.0)}\n"
                f"Nesting Depth: {metrics.get('nesting_depth', 0)}\n"
                f"Comment Ratio: {metrics.get('comment_ratio', 0.0):.1%}\n"
                f"Code Smells Detected to Specifically Target & Roast:\n{smells_str}\n\n"
                f"Code Snippet:\n{code[:800]}"
            )

        if grade and not metrics.get("_is_plain_text", False):
            letter = grade[0] if grade else "F"
            system_prompt += (
                f"\nAt the very end of your roast on a new line, you MUST append: "
                f"[VERDICT]: <one short, devastating one-liner reaction specifically to their Letter Grade of {letter}>"
            )

        return system_prompt, few_shot_examples, user_content, is_nepali

    def generate_roast_stream(
        self,
        code: str,
        metrics: dict,
        quality_level: int = 2,
        severity: int = 2,
        language: str = "english",
        gemini_key: Optional[str] = None,
        grade: Optional[str] = None
    ):
        """
        Yields real-time tokens from local Ollama for English roasts.
        Falls back to generate_roast() if streaming is not available or for Nepali.
        """
        is_nepali = language.lower() in ["nepali", "roman_nepali", "roman nepali"]

        if is_nepali:
            full_roast = self.generate_roast(
                code=code,
                metrics=metrics,
                quality_level=quality_level,
                severity=severity,
                language=language,
                gemini_key=gemini_key,
                grade=grade
            )
            if full_roast:
                words = full_roast.split(" ")
                for i, w in enumerate(words):
                    yield w + (" " if i < len(words) - 1 else "")
            return

        system_prompt, few_shot_examples, user_content, _ = self._prepare_prompt_and_messages(
            code=code,
            metrics=metrics,
            quality_level=quality_level,
            severity=severity,
            language=language,
            grade=grade
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(few_shot_examples)
        messages.append({"role": "user", "content": user_content})

        # Try real Ollama streaming
        try:
            ollama_model = self._get_ollama_model()
            payload = json.dumps({
                "model": ollama_model,
                "messages": messages,
                "stream": True,
                "keep_alive": -1,
                "options": {
                    "num_ctx": 2048,
                    "temperature": 1.05,
                    "top_p": 0.9,
                    "top_k": 50,
                    "repeat_penalty": 1.2,
                    "num_predict": 500
                }
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                if resp.status == 200:
                    buffer = ""
                    checked_refusal = False
                    streamed_any = False
                    for line in resp:
                        if not line:
                            continue
                        chunk = json.loads(line.decode("utf-8"))
                        if "message" in chunk and "content" in chunk["message"]:
                            token = chunk["message"]["content"]
                            if not checked_refusal:
                                buffer += token
                                if len(buffer) >= 40:
                                    if is_refusal(buffer):
                                        print("[Ollama Stream Refusal Detected]: aborting stream")
                                        break
                                    checked_refusal = True
                                    streamed_any = True
                                    yield buffer
                                    buffer = ""
                            else:
                                streamed_any = True
                                yield token
                        if chunk.get("done", False):
                            break
                    if not checked_refusal and buffer:
                        if not is_refusal(buffer):
                            streamed_any = True
                            yield buffer
                    if streamed_any:
                        return
        except Exception as e:
            print(f"[Ollama Stream Error]: {type(e)} {e}")

        # Fallback to non-streaming roast
        full_roast = self.generate_roast(
            code=code,
            metrics=metrics,
            quality_level=quality_level,
            severity=severity,
            language=language,
            gemini_key=gemini_key
        )
        if full_roast:
            words = full_roast.split(" ")
            for i, w in enumerate(words):
                yield w + (" " if i < len(words) - 1 else "")

    def generate_roast(
        self,
        code: str,
        metrics: dict,
        quality_level: int,
        severity: int = 2,
        language: str = "english",
        gemini_key: Optional[str] = None,
        grade: Optional[str] = None
    ) -> Optional[str]:
        """
        Generates a dynamic roast text response using Gemini Flash or Qwen AI.
        Supports language='english' or language='nepali' / 'roman_nepali'.
        """
        system_prompt, few_shot_examples, user_content, is_nepali = self._prepare_prompt_and_messages(
            code=code,
            metrics=metrics,
            quality_level=quality_level,
            severity=severity,
            language=language,
            grade=grade
        )
        g_key = self._get_gemini_key(gemini_key)
        token = self._get_hf_token()

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
            ollama_model = self._get_ollama_model()
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=json.dumps({
                    "model": ollama_model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": -1,
                    "options": {
                        "num_ctx": 2048,
                        "temperature": 1.05,
                        "top_p": 0.9,
                        "top_k": 50,
                        "repeat_penalty": 1.2,
                        "num_predict": 500
                    }
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    if "message" in res_data and "content" in res_data["message"]:
                        response_text = res_data["message"]["content"].strip()
                        if not is_refusal(response_text):
                            return self._ensure_profane_unhinged_roast(response_text, metrics, is_nepali=is_nepali)
        except Exception as e:
            print(f"[Ollama Call Error]: {type(e)} {e}")

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
        Strips accidental code blocks and dynamically ensures explicit profanity.
        """
        import random

        profanities = [
            'fuck', 'fucking', 'motherfucker', 'shit', 'bullshit', 'dipshit',
            'goddamn', 'dumbass', 'jackass', 'bastard', 'crap', 'dickhead',
            'bitch', 'asshole', 'clusterfuck', 'hawa', 'khattam', 'pakhe', 'bheda',
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
                    "Holy motherfucking shit, kasto dimag navako ra harami logic lekheko yo!",
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
                    "Ae dimag navako gadha, yo logic run garda CPU fan speed 100% pugera laptop ma Selroti pakauna milne vayo!",
                    "Arey pasa, yo code padhda padhdai mero battery percent 100% bata 5% ma jhyap bhayo!",
                    "What an absolute abominable clusterfuck! Tero code dekhera Kulman Ghising le blackout suru gardinchha!",
                    "Ae bheda, yo snippet ma logic bhanda dherai unwanted spaces ra bullshit error handling matra chha!",
                    "Jesus Christ, tero cyclomatic complexity dekhera Fewa Lake ko paani pani tatauchha out of sheer anger!"
                ]
                closers = [
                    " Delete gar yo trash immediately ra bheda charna jaa Pokhara tira, you lazy bastard!",
                    " Format tero hard drive ra laptop pokhari ma fyal, you dimag navako gadha!",
                    " VS Code close gar right now ra computer science chhodeera goat herding suru gar, you harami!",
                    " Stop coding forever, you absolute dimag navako pakhe!",
                    " Nuke yo repository right now before RONB ma 'worst developer arrested' breaking news aauchha!",
                    " Delete your GitHub account immediately, throw your laptop in Bagmati river, ra Nagarkot ma tour guide ko kaam khoj!",
                    " Clean up your architecture right fucking now before senior dev le office bata seedhai nikalera bhatkaidinchha!",
                    " Wipe your SSD with a neodymium magnet right now and never touch a keyboard again, you dumbass khate!",
                    " Format drive D:\\, throw your laptop into Karnali river, and go herd Yaks in Manang, you hopeless piece of shit!",
                    " Surrender your engineering degree to Kathmandu Metropolitan City and apologize to every RAM stick on your PC!",
                    " Close VS Code forever, burn your IT certificate, ra Pokhara ko Fewa Lake ma jump hande, you brainless gadha!",
                    " Format tero PC immediately ra tero computer teacher ko certificate firta gar, you useless pakhe!",
                    " Delete this crime against programming right now before your laptop explodes in flame!",
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

        # 3. Filter out forbidden terms (randikhola, randi, rape, murder, etc.)
        forbidden_map = {
            'randikhola': 'mujikhola',
            'randi': 'mujii',
            'rape': 'goddamn destroy',
            'raped': 'goddamn destroyed',
            'raping': 'goddamn destroying',
            'murder': 'destroy',
            'murdered': 'destroyed',
            'murdering': 'destroying'
        }
        import re
        for term, replacement in forbidden_map.items():
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            text = pattern.sub(replacement, text)

        # 4. Anti-Tutorial & Multi-Language Hallucination Sanitizer
        tutorial_patterns = [
            r'You can try using tools like [^.!?]*[.!?]',
            r'Make sure that you take the time to [^.!?]*[.!?]',
            r'If you\'re still having trouble maintaining [^.!?]*[.!?]',
            r'Tools like ESLint or Prettier [^.!?]*[.!?]',
            r'Consider using tools like [^.!?]*[.!?]',
            r'And if you\'re still having trouble [^.!?]*[.!?]'
        ]
        for pat in tutorial_patterns:
            text = re.sub(pat, '', text, flags=re.IGNORECASE)

        active_lang = metrics.get('_selected_lang', 'Python').capitalize()
        text = re.sub(r'Python/JS/Java \(and even some C\+\+ at one point\)', active_lang, text, flags=re.IGNORECASE)
        text = re.sub(r'Python/JS/Java', active_lang, text, flags=re.IGNORECASE)

        return text.strip()

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
            ollama_model = self._get_ollama_model()
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=json.dumps({
                    "model": ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 1.0}
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
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
