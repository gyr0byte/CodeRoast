"""
🔥 CodeRoast — Brutally Honest Code Reviews
Streamlit application entry point.

This must be the first import to ensure HF_HOME is set before
any ML libraries are loaded.
"""

import config  # noqa: F401 — Sets HF_HOME and TF log level first

import streamlit as st
import plotly.graph_objects as go
import os
import sys
import json
import io
import base64
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont


# Ensure src is importable
sys.path.insert(0, os.path.dirname(__file__))

import importlib
from src.analyzer.code_analyzer import CodeAnalyzer
from src.scoring.scorer import calculate_scores, get_grade
import src.roast.templates
import src.roast.generator
import src.roast.llm_generator
importlib.reload(src.roast.templates)
importlib.reload(src.roast.generator)
importlib.reload(src.roast.llm_generator)
from src.roast.generator import RoastGenerator


def clean_roast_tags(text: str) -> str:
    """Universally strip AI model prefixes like '🤖 [Llama 3.2 AI Roast]: ' from roast text."""
    import re
    return re.sub(r"^🤖\s*(\[[^\]]+\]:)?\s*", "", text).strip()


def generate_roast_audio(text: str, lang_code: str = "en") -> Optional[bytes]:
    """Generate Text-to-Speech MP3 audio bytes using gTTS."""
    clean_text = clean_roast_tags(text)
    try:
        from gtts import gTTS
        import io
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception as e:
        print("[TTS Error]:", e)
        return None


def draw_impact_caption(draw, text: str, width: int, y_start: int, font, is_bottom: bool = False):
    """Draw classic white uppercase meme text with thick black outline centered at y_start."""
    import textwrap
    text = text.upper()
    lines = textwrap.wrap(text, width=22)
    stroke_w = 4
    line_h = 38
    
    if is_bottom:
        total_h = len(lines) * line_h
        y_pos = y_start - total_h - 10
    else:
        y_pos = y_start

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x_pos = (width - line_w) // 2
        draw.text((x_pos, y_pos), line, font=font, fill=(255, 255, 255), stroke_width=stroke_w, stroke_fill=(0, 0, 0))
        y_pos += line_h


def extract_code_elements(code: str, metrics: dict):
    """Extract key identifiers, variables, and magic numbers to weave into memes."""
    import re
    fn_matches = re.findall(r'(?:def|function)\s+([a-zA-Z_]\w*)', code)
    func_name = fn_matches[0] if fn_matches else "your_code"

    generic_names = ['temp', 'tmp', 'data', 'val', 'value', 'res', 'result', 'obj', 'foo', 'bar', 'baz', 'item', 'arr', 'num']
    words = re.findall(r'\b[a-zA-Z_]\w*\b', code)
    found_generic = [w for w in words if w.lower() in generic_names]
    if found_generic:
        bad_var = found_generic[0]
    else:
        single_letters = [w for w in words if len(w) == 1 and w.isalpha() and w.lower() not in ('a', 'i')]
        bad_var = single_letters[0] if single_letters else "data"

    magic_nums = [m for m in re.findall(r'(?<![a-zA-Z0-9_])([0-9]{2,})(?![a-zA-Z0-9_])', code) if m not in ('100', '0', '1')]
    magic_num = magic_nums[0] if magic_nums else "999"

    return func_name, bad_var, magic_num


def generate_code_meme(
    metrics: dict,
    grade: str,
    language: str,
    code: str = "",
    target_lang: str = "english",
    template_override: Optional[str] = None
) -> bytes:
    """Generate an authentic classic Impact Font meme using template-specific punchlines and actual code flaws."""
    import os, random
    grade_clean = grade.encode("ascii", "ignore").decode("ascii").strip()
    grade_str = grade_clean.split()[0] if grade_clean else "F"
    complexity = int(metrics.get("cyclomatic_complexity", 1))
    nesting = int(metrics.get("nesting_depth", metrics.get("max_nesting_depth", 0)))
    loc = int(metrics.get("lines_of_code", 0))
    is_mismatch = metrics.get("_language_mismatch", False)

    sel_lang = metrics.get("_selected_lang", "JAVA").upper()
    det_lang = metrics.get("_detected_lang", "PYTHON").upper()
    is_nepali = target_lang.lower() in ["nepali", "roman_nepali", "roman nepali"]

    func_name, bad_var, magic_num = extract_code_elements(code, metrics)

    # ── 1. Fetch Downloaded Templates ──────────────────────────────────
    meme_dir = "assets/memes"
    all_files = sorted([f for f in os.listdir(meme_dir) if f.endswith((".jpg", ".png"))]) if os.path.exists(meme_dir) else []
    if not all_files:
        all_files = ["left_exit_12_off_ramp.jpg", "drake_hotline_bling.jpg"]

    # Non-repeating Session Memory Tracking
    if template_override and template_override in all_files:
        template_name = template_override
    else:
        try:
            import streamlit as st
            if "seen_memes" not in st.session_state:
                st.session_state["seen_memes"] = []
            available = [f for f in all_files if f not in st.session_state["seen_memes"]]
            if not available:
                st.session_state["seen_memes"] = []
                available = all_files
            template_name = random.choice(available)
            st.session_state["seen_memes"].append(template_name)
        except Exception:
            template_name = random.choice(all_files)

    # ── 2. Precise Visual Zone Coordinate Offsets ───────────────────────
    COORD_MAP = {
        "left_exit_12_off_ramp.jpg": (0.18, 0.76),
        "drake_hotline_bling.jpg": (0.14, 0.65),
        "drake.jpg": (0.14, 0.65),
        "drake_blank.jpg": (0.14, 0.65),
        "two_buttons.jpg": (0.10, 0.75),
        "change_my_mind.jpg": (0.12, 0.75),
        "batman_slapping_robin.jpg": (0.08, 0.75),
        "theyre_the_same_picture.jpg": (0.08, 0.76),
        "clown_applying_makeup.jpg": (0.08, 0.75),
        "disaster_girl.jpg": (0.08, 0.75),
        "a_train_hitting_a_school_bus.jpg": (0.10, 0.75),
        "expanding_brain.jpg": (0.08, 0.78),
        "panik_kalm_panik.jpg": (0.10, 0.75),
        "trade_offer.jpg": (0.10, 0.75),
        "buff_doge_vs._cheems.jpg": (0.10, 0.75),
        "running_away_balloon.jpg": (0.10, 0.75),
        "hide_the_pain_harold.jpg": (0.08, 0.75),
        "roll_safe_think_about_it.jpg": (0.10, 0.75),
        "roll_safe.jpg": (0.10, 0.75),
        "epic_handshake.jpg": (0.10, 0.75),
        "leonardo_dicaprio_cheers.jpg": (0.08, 0.75),
        "uno_draw_25_cards.jpg": (0.10, 0.75),
        "woman_yelling_at_cat.jpg": (0.08, 0.75),
        "is_this_a_pigeon.jpg": (0.10, 0.75),
        "is_this_butterfly.jpg": (0.10, 0.75),
        "spiderman_pointing_at_spiderman.jpg": (0.10, 0.75),
        "spider_man_triple.jpg": (0.10, 0.75),
        "grus_plan.jpg": (0.08, 0.78),
        "cmon_do_something.jpg": (0.10, 0.75),
        "boardroom_meeting_suggestion.jpg": (0.08, 0.75),
        "futurama_fry.jpg": (0.10, 0.75),
        "flex_tape.jpg": (0.10, 0.75),
        "gus_fring_we_are_not_the_same.jpg": (0.10, 0.75),
        "distracted_boyfriend.jpg": (0.10, 0.75),
        "surprised_pikachu.jpg": (0.10, 0.75),
        "this_is_fine.jpg": (0.08, 0.75),
        "anakin_padme_4_panel.jpg": (0.08, 0.75),
        "bernie_sanders_once_again_asking.jpg": (0.10, 0.75),
        "bernie_i_am_once_again_asking_for_your_support.jpg": (0.10, 0.75),
        "all_my_homies_hate.jpg": (0.10, 0.75),
        "types_of_headaches_meme.jpg": (0.08, 0.75),
        "pawn_stars_best_i_can_do.jpg": (0.10, 0.75),
        "yall_got_any_more_of_that.jpg": (0.10, 0.75),
        "you_know,_im_something_of_a_scientist_myself.jpg": (0.08, 0.75),
        "who_killed_hannibal.jpg": (0.08, 0.75),
        "bike_fall.jpg": (0.08, 0.75),
        "mother_ignoring_kid_drowning_in_a_pool.jpg": (0.08, 0.75)
    }
    top_y_pct, bottom_y_pct = COORD_MAP.get(template_name, (0.08, 0.76))

    # ── 3. Template-Specific Hilarious Joke Engine ──────────────────────
    TEMPLATE_JOKES = {
        "batman_slapping_robin.jpg": {
            "en": [
                ("ROBIN: 'IT WORKS ON MY LOCALHOST BRO—'", f"BATMAN: 'SHUT UP, YOU HAVE {nesting} LEVELS OF NESTING!'"),
                ("ROBIN: 'I WILL RENAME {bad_var} TOMORROW—'", "BATMAN: 'SHUT UP AND USE MEANINGFUL IDENTIFIERS!'"),
                (f"ROBIN: 'COMPLEXITY {complexity} IS NORMAL—'", f"BATMAN: 'NOT EVEN JAMES CAMERON CAN REACH YOUR INDENTATION!'"),
                ("ROBIN: 'COMMENTS ARE FOR WEAKLINGS—'", "BATMAN: 'SHUT UP, NO ONE ON THE TEAM CAN READ THIS!'"),
                (f"ROBIN: 'GRADE {grade_str} IS PASSING RIGHT?—'", "BATMAN: 'FORMAT YOUR SSD IMMEDIATELY!'")
            ],
            "np": [
                ("ROBIN: 'DAI MERO LOCALHOST MA CHALYO—'", f"BATMAN: 'OYE PAKHE, {nesting} LEVEL KO INDENTATION KASLE MERGE GARCHHA!'"),
                (f"ROBIN: 'VARIABLE KO NAAM {bad_var} TA HO—'", "BATMAN: 'CHUP LAG! TERO YESTO HAWAL CODE BAGMATI MA FAL!'"),
                (f"ROBIN: 'GRADE {grade_str} AAYE PANI CHALCHHA—'", "BATMAN: 'LOKSEWA KO FORM BHARNA JAA RIGHT NOW!'")
            ]
        },
        "drake_hotline_bling.jpg": {
            "en": [
                ("WRITING MEANINGFUL NAMES & COMMENTS", f"NAMING EVERYTHING '{bad_var}' & PRAYING IN PROD"),
                ("BREAKING CODE INTO 10-LINE HELPERS", f"ONE {loc}-LINE GOD FUNCTION WITH {nesting} NESTED LOOPS"),
                ("PROPER ERROR HANDLING AND LOGGING", f"TRY: {func_name}() EXCEPT: PASS"),
                ("USING FLAT CONTROL FLOW PATTERNS", f"PYRAMID OF DOOM (GRADE {grade_str} DISASTER)")
            ],
            "np": [
                ("DOCSTRING RA PROPER LOGIC LEKHNE", f"'{bad_var}' LEKHERA LAPTOP BHEDA CHARNA LAGNE"),
                ("CLEAN FUNCTIONS BANAYERA MERGE GARNE", f"ZERO COMMENT HALERA {loc} LINE SPAGHETTI DUMP GARNE")
            ]
        },
        "two_buttons.jpg": {
            "en": [
                (f"FIX CYCLOMATIC COMPLEXITY ({complexity})", "PUSH TO PROD ON FRIDAY & TURN OFF PHONE"),
                ("WRITE 1 HELPFUL COMMENT", f"RENAME '{bad_var}' TO '{bad_var}2' AND CALL IT REFACTORED"),
                (f"ADMIT CODE IS GRADE {grade_str}", "BLAME THE COMPILER FOR NOT GETTING YOUR GENIUS")
            ],
            "np": [
                ("CODE REFACTOR GARERA MERGE GARNE", "LOKSEWA KO FORM BHARERA BHEDA CHARNA JANE"),
                ("EUTA MATRAI COMMENT THAPNE", "LAPTOP BAGMATI MA FALERA SUKHA PAUNE")
            ]
        },
        "uno_draw_25_cards.jpg": {
            "en": [
                (f"WRITE 1 HELPFUL COMMENT IN {func_name}()", "OR DRAW 25 CARDS"),
                (f"FLATTEN YOUR {nesting}-LEVEL INDENTATION", "OR DRAW 25 CARDS"),
                (f"STOP USING MAGIC NUMBER {magic_num}", "OR DRAW 25 CARDS"),
                (f"RENAME VARIABLE '{bad_var}' TO AN ACTUAL WORD", "OR DRAW 25 CARDS")
            ],
            "np": [
                ("CODE MA EUTA HELPFUL COMMENT LEKHNE", "KI CHUPCHAP 25 WATA CARD TANNE"),
                (f"'{bad_var}' KO SATTA REAL NAAM LEKHNE", "KI 25 CARDS TANERA BHEDA CHARNA JANE")
            ]
        },
        "left_exit_12_off_ramp.jpg": {
            "en": [
                ("STRAIGHT: WRITE CLEAN MODULAR CODE", f"EXIT: {loc} LINES OF UNTESTED SPAGHETTI AT 3 AM"),
                ("STRAIGHT: PROPER LOGGING", f"EXIT: PRINT('{bad_var}') ON EVERY SINGLE LINE"),
                ("STRAIGHT: FLAT CONTROL FLOW", f"EXIT: INDENTATION LEVEL {nesting} STRAIGHT INTO OBLIVION")
            ],
            "np": [
                ("SIDHA: CLEAN ARCHITECTURE RA TESTS", f"EXIT: KATHMANDU KO TRAFFIC JASTO {nesting}-LEVEL NESTING")
            ]
        },
        "trade_offer.jpg": {
            "en": [
                (f"TRADE OFFER: I RECEIVE YOUR {func_name}()", f"YOU RECEIVE: OUT OF MEMORY CRASH & GRADE {grade_str}"),
                ("TRADE OFFER: I RECEIVE ZERO COMMENTS", "YOU RECEIVE: PAGERDUTY ALARM AT 3:15 AM")
            ],
            "np": [
                (f"TRADE OFFER: TERO YESTO {func_name}()", "RESULT: COMPILER KO INSTANT HEART ATTACK")
            ]
        },
        "woman_yelling_at_cat.jpg": {
            "en": [
                (f"SENIOR DEV: 'WHY IS COMPLEXITY {complexity}?!'", "ME: 'I ADDED A COMMENT IN MY HEART'"),
                (f"LEAD: 'DID YOU NAME A VARIABLE {bad_var}?!'", "ME: 'HE HAS A VERY NICE PERSONALITY'"),
                (f"REVIEWER: 'WHO WROTE THIS {loc}-LINE MONSTROSITY?!'", "ME: 'IT COMPILES ONCE EVERY FULL MOON'")
            ],
            "np": [
                (f"SENIOR: 'COMPLEXITY {complexity} KINA BHO?!'", "ME: 'MAILE TA SARKARI EXAM KO LAXAN DEKHEKO CHHU'"),
                (f"LEAD: '{bad_var} KASLE LEKHEKO HO?!'", "ME: 'PASSION LE LEKHEKO BRO'")
            ]
        },
        "disaster_girl.jpg": {
            "en": [
                (f"MY GRADE {grade_str} CODE CURRENTLY BURNING PRODUCTION", "ME: 'NOT MY PROBLEM, WORKED ON LOCALHOST'"),
                (f"DEPLOYED '{func_name}' WITH {nesting} NESTED LOOPS", "ME HEADING TO THE WEEKEND ON AIRPLANE MODE")
            ],
            "np": [
                ("PRODUCTION SERVER MA AAGO LAGDAI CHHA", "ME: 'MERI BASSAI HERDAI CHIYA KHANA GAYEKO'")
            ]
        },
        "flex_tape.jpg": {
            "en": [
                (f"MASSIVE MEMORY CRASH & COMPLEXITY {complexity}", "SLAPPING 'TRY: ... EXCEPT: PASS' ON TOP"),
                (f"MEMORY LEAK IN {loc}-LINE GOD FUNCTION", "SLAPPING TIME.SLEEP(5) AND PRAYING TO GOD")
            ],
            "np": [
                ("PRODUCTION SERVER KO LOGIC PURAI DUBYO", "CHUPCHAP EXCEPT EXCEPTION: PASS HALERA BASNE")
            ]
        },
        "change_my_mind.jpg": {
            "en": [
                (f"NAMING VARIABLES '{bad_var}' IS A CRY FOR HELP", "CHANGE MY MIND"),
                (f"NESTING DEPTH {nesting} IS A WAR CRIME", "CHANGE MY MIND"),
                (f"GRADE {grade_str} MEANS YOU SHOULD RETIRE YOUR KEYBOARD", "CHANGE MY MIND")
            ],
            "np": [
                ("TERO CODING BHANDA BHEDA CHARAUNA JANE RAMRO", "CHANGE MY MIND")
            ]
        },
        "roll_safe.jpg": {
            "en": [
                ("YOU CANNOT HAVE BUGS IN YOUR UNIT TESTS", "IF YOU NEVER WRITE ANY UNIT TESTS AT ALL"),
                ("NO ONE CAN CRITICIZE YOUR COMMENTS", "IF YOU NEVER WRITE A SINGLE COMMENT")
            ],
            "np": [
                ("TEST FAIL HUNE DAR NAI HUDAINA", "YADI TEST NAI LEKHIYENA BHANE")
            ]
        },
        "gus_fring_we_are_not_the_same.jpg": {
            "en": [
                ("YOU WROTE ZERO COMMENTS BECAUSE YOU ARE LAZY", "I WROTE ZERO COMMENTS TO CONFUSE THE ENEMY. WE ARE NOT THE SAME."),
                (f"YOU WROTE {loc} LINES BECAUSE YOU CANNOT MODULARIZE", "I WROTE IT TO BREAK THE REVIEWER'S WILL. WE ARE NOT THE SAME.")
            ],
            "np": [
                ("TAILE ZERO COMMENT HAWAL LE GARDHA LEKHIS", "MAILE SENIOR LAI RUAUNA LEKHE. WE ARE NOT THE SAME.")
            ]
        },
        "buff_doge_vs._cheems.jpg": {
            "en": [
                ("1969: 'WE CODED APOLLO 11 IN ASSEMBLY'", f"YOU: 'MY {loc}-LINE {func_name}() NEEDS A THERAPIST'"),
                ("VETERAN DEV: 'MEMORY MANAGEMENT IN C'", f"YOU: 'CANNOT INVERT BINARY TREE WITHOUT {bad_var}'")
            ],
            "np": [
                ("1969 MA APOLLO GUIDANCE COMPUTER CHALAYO", f"TERO 10 LINE CODE MA CYCLOMATIC SCORE {complexity}")
            ]
        },
        "distracted_boyfriend.jpg": {
            "en": [
                (f"ME LOOKING AT: {nesting}-LEVEL DEEP NESTED LOOPS", "MY UNATTENDED CLEAN PEP8 CODE CRYING"),
                (f"ME: NAMING EVERYTHING '{bad_var}' AT 3 AM", "MEANINGFUL VARIABLE NAMES CRYING IN THE CORNER")
            ],
            "np": [
                (f"CHITRA: KATHMANDU TRAFFIC JASTO {nesting}-LEVEL INDENTATION", "CLEAN DOCUMENTATION LAI BAAL CHHAINA")
            ]
        },
        "surprised_pikachu.jpg": {
            "en": [
                (f"*COMMITS {loc} LINES WITH 0 COMMENTS & MAGIC NUM {magic_num}*", f"*COMPILER THROWS GRADE {grade_str}* PIKACHU FACE"),
                (f"*USES '{bad_var}' FOR 5 DIFFERENT UNRELATED PURPOSES*", "*OUTPUT IS NAN* PIKACHU FACE")
            ],
            "np": [
                ("*ZERO COMMENT HALERA MAIN BRANCH MA PUSH GARCHHA*", "*SERVER CRASH BHAYERA BOSS LE GALI GAREKO HERDAI*")
            ]
        },
        "this_is_fine.jpg": {
            "en": [
                (f"COMPLEXITY: {complexity} | GRADE: {grade_str} | ZERO TESTS", "THIS IS FINE. EVERYTHING IS TOTALLY NORMAL."),
                (f"ALL {loc} LINES CURRENTLY CORRUPTING DATABASE", "THIS IS FINE. SLOWLY SIPS COFFEE.")
            ],
            "np": [
                ("SERVER PURAI DHWANGSTA BHAISAKYO", "THIS IS FINE. CHUPCHAP CHIYA KHANA GAYEKO.")
            ]
        },
        "anakin_padme_4_panel.jpg": {
            "en": [
                (f"ME: 'I JUST DEPLOYED {func_name}() TO PRODUCTION'", "PADME: 'YOU TESTED WITH REAL DATA RIGHT? ...RIGHT?!'")
            ],
            "np": [
                ("ME: 'MAILE PRODUCTION BRANCH MA MERGE HANI DEYE'", "PADME: 'TEST TA GARYAU HOLA NI? ...HOINA?!'")
            ]
        },
        "bernie_sanders_once_again_asking.jpg": {
            "en": [
                ("I AM ONCE AGAIN ASKING YOU", "TO WRITE AT LEAST ONE GODDAMN COMMENT"),
                ("I AM ONCE AGAIN ASKING YOU", f"TO STOP USING '{bad_var}' AS A VARIABLE NAME")
            ],
            "np": [
                ("MA PHERI EKDAM BINAMRA ANURODH GARCHHU", "KRPAYA EUTA MATRAI COMMENT LEKHI DEU")
            ]
        },
        "clown_applying_makeup.jpg": {
            "en": [
                ("'IT IS JUST A QUICK 5-MINUTE SCRIPT'", f"'IT IS NOW {loc} LINES OF UNMAINTAINABLE HORROR'")
            ],
            "np": [
                ("'2 MINUTE KO KAM HO, TURUNTAI SAKCHHU'", f"'AHILE LEVEL {nesting} PYRAMID BANERA RATI KO 3 BAJYO'")
            ]
        },
        "boardroom_meeting_suggestion.jpg": {
            "en": [
                ("BOSS: 'HOW DO WE REDUCE PRODUCTION BUGS?'", f"DEV: 'DELETE {func_name}() BEFORE SENIORS SEE IT'")
            ],
            "np": [
                ("BOSS: 'SERVER PERFORMANCE KINA DOWN BHO?'", f"DEV: 'TYO TERO {bad_var} WALA CODE LE GARDHA'")
            ]
        },
        "a_train_hitting_a_school_bus.jpg": {
            "en": [
                (f"BUS: YOUR DELICATE {func_name}() LOGIC", "A-TRAIN: REAL-WORLD PRODUCTION TRAFFIC")
            ],
            "np": [
                ("BUS: TERO CHOTTO FUNCTION", "A-TRAIN: KATHMANDU KO KHALASI SPEED")
            ]
        },
        "theyre_the_same_picture.jpg": {
            "en": [
                ("PAM: FIND THE DIFFERENCE BETWEEN THESE TWO", "PICTURE 1: YOUR CODE | PICTURE 2: DIGITAL SEWAGE")
            ],
            "np": [
                ("PAM: DUI WATA CHITRA MA DIFFERENCE K CHHA?", "PHOTO 1: TERO CODE | PHOTO 2: TUKUCHA KHOLA KO DHAL")
            ]
        },
        "is_this_a_pigeon.jpg": {
            "en": [
                (f"*PASTES {loc} LINES OF SPAGHETTI WITH NO COMMENTS*", "'IS THIS SENIOR SOFTWARE ARCHITECTURE?'")
            ],
            "np": [
                (f"*{nesting} LEVEL KO NESTED LOOP LEKHERA*", "'YO K ARTIFICIAL INTELLIGENCE HO?'")
            ]
        },
        "one_does_not_simply.jpg": {
            "en": [
                ("ONE DOES NOT SIMPLY MERGE", f"A FUNCTION WITH CYCLOMATIC COMPLEXITY {complexity}")
            ],
            "np": [
                ("ONE DOES NOT SIMPLY RUN", "A FUNCTION WITH ZERO COMMENTS RA ZERO LOGIC")
            ]
        },
        "panik_kalm_panik.jpg": {
            "en": [
                ("CODE CRASHES IN DEMO (PANIK)", "EXCEPT: PASS (KALM) -> DATABASE CORRUPTED (PANIK!)")
            ],
            "np": [
                ("DEMO MA CODE CRASH BHO (PANIK)", "RESTART GAREKO CHALYO (KALM) -> DATA SAB GAYO (PANIK!)")
            ]
        },
        "grim_reaper_knocking_door.jpg": {
            "en": [
                ("MEMORY LEAK -> CPU MELTDOWN -> SERVER FIRE", "NEXT DOOR: YOUR ENTIRE PROGRAMMING CAREER")
            ],
            "np": [
                ("FUNCTION CRASH -> SERVER DOWN -> DATABASE DUBYO", "ABO NEXT NUMBER: TERO PROGRAMMING CAREER")
            ]
        },
        "all_my_homies_hate.jpg": {
            "en": [
                (f"FUCK CYCLOMATIC COMPLEXITY {complexity}", f"ALL MY HOMIES HATE INDENTATION LEVEL {nesting}")
            ],
            "np": [
                ("TERO YESTO HAWAL LOGIC LAI BYCOT", "SABAI SATHI MILERA LAPTOP BAGMATI MA FALNE")
            ]
        },
        "types_of_headaches_meme.jpg": {
            "en": [
                ("MIGRAINE, HYPERTENSION, STRESS...", f"READING YOUR {loc} LINES OF CODE WITH ZERO COMMENTS")
            ],
            "np": [
                ("MIGRAINE, HIGH BP, STRESS...", "TERO YESTO KANDAL CODE HERERA AAKHA FUTNU")
            ]
        },
        "pawn_stars_best_i_can_do.jpg": {
            "en": [
                ("YOU: 'I WORKED 40 HOURS ON THIS CODE'", f"RICK: 'BEST I CAN DO IS GRADE {grade_str} & A RECYCLE BIN'")
            ],
            "np": [
                ("DEV: '40 GHANTA LAGAYERA LEKHEKO FUNCTION HO DAI'", f"RICK: 'BEST I CAN DO IS GRADE {grade_str} ANI BHEDA CHARNA JA'")
            ]
        },
        "who_killed_hannibal.jpg": {
            "en": [
                (f"*COMMITS {loc} LINES WITH 0 TESTS DIRECTLY TO MAIN*", "'WHY WOULD CI/CD PIPELINE DO THIS TO US?'")
            ],
            "np": [
                ("*TEST NAI NAGARI MAIN MA MERGE HANDEKO*", "'SERVER KINA DOWN BHAYO KHOI KASLE HERNE?'")
            ]
        },
        "bike_fall.jpg": {
            "en": [
                (f"*SHOVES '{bad_var}' AND {nesting} LOOPS INTO FRONT SPOKES*", "'FUCKING RUNTIME ALWAYS RUINING MY LIFE'")
            ],
            "np": [
                ("*HAWA LOGIC LEKHERA FRONT TYRE MA DANDA HALYO*", "'BAGMATI MA DHAL CHHA, CODE MA KASKO DOSH'")
            ]
        },
        "mother_ignoring_kid_drowning_in_a_pool.jpg": {
            "en": [
                ("MOM: NEW FRONTEND BUTTON ANIMATION", "SKELETON AT BOTTOM: YOUR ZERO WRITTEN COMMENTS")
            ],
            "np": [
                ("MOM: UI RA CSS COLORS", "SKELETON: CODE KO COMMENTS RA DOCUMENTATION")
            ]
        },
        "epic_handshake.jpg": {
            "en": [
                (f"YOUR VARIABLE '{bad_var}' 🤝 A DRUNK TODDLER'S SCRAWL", "MUTUAL DISREGARD FOR THE ENGLISH ALPHABET")
            ],
            "np": [
                ("TERO CODE 🤝 TUKUCHA KHOLA KO DHAL", "DONO MA EUTAI GANDHA CHHA")
            ]
        },
        "leonardo_dicaprio_cheers.jpg": {
            "en": [
                (f"CHEERS TO PUSHING GRADE {grade_str} CODE DIRECTLY TO PROD", "MAY THE ON-CALL ENGINEER REST IN PEACE")
            ],
            "np": [
                ("CHEERS TO YESTO KANDAL CODE IN PRODUCTION", "BHOLI BIHANA DISASTER HERNA JANE")
            ]
        },
        "cmon_do_something.jpg": {
            "en": [
                (f"*POKES {func_name}() WITH A STICK*", "'C'MON, RETURN SOMETHING OTHER THAN NULL'")
            ],
            "np": [
                (f"*DANDA LE TERO {func_name} LAI CHUDAI*", "'C'MON, ZERO DIVISION BHANDA ARU KEI RETURN GAR'")
            ]
        },
        "grus_plan.jpg": {
            "en": [
                (f"1. WRITE {func_name}() | 2. SKIP ALL UNIT TESTS", "3. PRODUCTION CRASHES | 4. PRODUCTION CRASHES?!")
            ],
            "np": [
                ("1. FUNCTION LEKHNE | 2. ZERO COMMENTS HALNE", "3. SERVER AAGO LAGYO | 4. SERVER AAGO LAGYO?!")
            ]
        }
    }

    # Alias synonyms for closely related templates
    TEMPLATE_JOKES["drake.jpg"] = TEMPLATE_JOKES["drake_hotline_bling.jpg"]
    TEMPLATE_JOKES["drake_blank.jpg"] = TEMPLATE_JOKES["drake_hotline_bling.jpg"]
    TEMPLATE_JOKES["roll_safe_think_about_it.jpg"] = TEMPLATE_JOKES["roll_safe.jpg"]
    TEMPLATE_JOKES["is_this_butterfly.jpg"] = TEMPLATE_JOKES["is_this_a_pigeon.jpg"]
    TEMPLATE_JOKES["spider_man_triple.jpg"] = TEMPLATE_JOKES.get("spiderman_pointing_at_spiderman.jpg", TEMPLATE_JOKES["batman_slapping_robin.jpg"])
    TEMPLATE_JOKES["bernie_i_am_once_again_asking_for_your_support.jpg"] = TEMPLATE_JOKES["bernie_sanders_once_again_asking.jpg"]

    # Check if selected template has a dedicated joke pool
    lang_key = "np" if is_nepali else "en"
    if template_name in TEMPLATE_JOKES:
        joke_candidates = TEMPLATE_JOKES[template_name].get(lang_key) or TEMPLATE_JOKES[template_name].get("en")
        top_text, bottom_text = random.choice(joke_candidates)
    else:
        # ── 4. Dynamic Code-Specific Fallback Engine ────────────────────
        if is_mismatch:
            if is_nepali:
                top_text = f"DROPDOWN MA {sel_lang} SELECT GAREKO THIYO"
                bottom_text = f"PASTE GAREKO CODE CHAI {det_lang} SPAGHETTI!"
            else:
                top_text = f"UI DROPDOWN SAYS {sel_lang}"
                bottom_text = f"PASTED {det_lang} SPAGHETTI LIKE A CHAD!"
        elif nesting >= 3:
            if is_nepali:
                top_text = f"KATHMANDU TRAFFIC JASTO {nesting}-LEVEL INDENTATION"
                bottom_text = f"GOOD LUCK READING {func_name}() AFTER 2 BEERS"
            else:
                top_text = f"NESTING DEPTH LEVEL {nesting} (INCEPTION HORROR)"
                bottom_text = f"COMPILER CRYING WHILE PARSING {func_name}()"
        elif complexity >= 5:
            if is_nepali:
                top_text = f"CYCLOMATIC COMPLEXITY {complexity} BHAYO BRO"
                bottom_text = "MERO AAKHA MA AASHU AAYO YO DEKHERA"
            else:
                top_text = f"CYCLOMATIC COMPLEXITY {complexity} IS DANGEROUS"
                bottom_text = f"YOUR LOGIC LOOKS LIKE A BOWL OF WET NOODLES"
        elif loc > 30:
            if is_nepali:
                top_text = f"EUTAI FILE MA {loc} LINE KO SPAGHETTI"
                bottom_text = "REFACTOR NAGARE KO BHEDA CHARNA JA"
            else:
                top_text = f"ONE {loc}-LINE MONOLITHIC CRIME SCENE"
                bottom_text = f"RENAME '{func_name}' TO 'ENTERPRISE_DISASTER()'"
        elif grade_str in ["S", "A"]:
            if is_nepali:
                top_text = f"SENIOR DEV LOOKING AT GRADE {grade_str} LOGIC"
                bottom_text = "ABSOLUTE CINEMA ARCHITECTURE BRO!"
            else:
                top_text = f"YOUR CODE (GRADE {grade_str} GIGACHAD)"
                bottom_text = "CLEAN PEP8 LOGIC WORTHY OF A SALARY RAISE"
        else:
            if is_nepali:
                top_text = f"ME: 'MERO {func_name}() CHALCHHA TRUST ME'"
                bottom_text = f"COMPILER: GRADE {grade_str} DISASTER IN PROD!"
            else:
                top_text = f"DEV: 'IT RUNS ON LOCALHOST TRUST ME'"
                bottom_text = f"LINTER: GRADE {grade_str} CATASTROPHE IN PROD"
    
    template_path = os.path.join(meme_dir, template_name)
    if template_path and os.path.exists(template_path):
        img = Image.open(template_path).convert("RGB")
    else:
        img = Image.new("RGB", (750, 500), color=(15, 23, 42))
        
    target_w = 750
    w_percent = (target_w / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((target_w, h_size), Image.Resampling.LANCZOS)
    
    draw = ImageDraw.Draw(img)
    
    # Load Impact font (bundled or system)
    font_path = os.path.join("assets", "fonts", "impact.ttf")
    if not os.path.exists(font_path) and os.path.exists(r"C:\Windows\Fonts\impact.ttf"):
        font_path = r"C:\Windows\Fonts\impact.ttf"
        
    try:
        font = ImageFont.truetype(font_path, size=36)
    except Exception:
        font = ImageFont.load_default()
        
    # Render Classic Impact Font Meme Text with exact template visual zone alignment
    top_y_pos = int(h_size * top_y_pct)
    bottom_y_pos = int(h_size * bottom_y_pct)
    
    draw_impact_caption(draw, top_text, target_w, top_y_pos, font, is_bottom=False)
    draw_impact_caption(draw, bottom_text, target_w, bottom_y_pos, font, is_bottom=False)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()








# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CodeRoast 🔥 | AI Code Review Workspace",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for Option 1 AI Code Review Workspace ─────────────────────────

st.markdown("""
<style>
    /* Dark workspace theme */
    .stApp {
        background-color: #0b0d12;
        color: #e2e8f0;
    }

    /* Top Workspace Header */
    .workspace-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 18px;
        background: #131722;
        border: 1px solid #1e293b;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    .workspace-title {
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.5px;
    }

    /* Neon Metric Pills Bar */
    .neon-pill-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 14px;
    }

    .neon-pill {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: #131722;
        color: #cbd5e1;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
        border: 1.5px solid #334155;
        transition: all 0.3s ease;
    }

    .neon-pill-grade-f {
        border-color: #ef4444;
        color: #f87171;
        background: rgba(239, 68, 68, 0.12);
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.35);
    }

    .neon-pill-grade-s {
        border-color: #10b981;
        color: #34d399;
        background: rgba(16, 185, 129, 0.12);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
    }

    .neon-pill-grade-a {
        border-color: #3b82f6;
        color: #60a5fa;
        background: rgba(59, 130, 246, 0.12);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.35);
    }

    .neon-pill-complexity {
        border-color: #a855f7;
        color: #c084fc;
        background: rgba(168, 85, 247, 0.1);
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.3);
    }

    .neon-pill-lines {
        border-color: #06b6d4;
        color: #22d3ee;
        background: rgba(6, 182, 212, 0.1);
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
    }

    .neon-pill-comments {
        border-color: #f59e0b;
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.1);
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
    }

    /* Chatbot Message Styling */
    .chat-bubble-assistant {
        background: linear-gradient(135deg, #2e1065 0%, #0f172a 100%);
        border: 1.5px solid #a855f7;
        border-radius: 12px;
        padding: 18px;
        color: #f1f5f9;
        font-size: 1rem;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
    }

    .chat-bubble-template {
        background: linear-gradient(135deg, #451a03 0%, #0f172a 100%);
        border: 1.5px solid #f59e0b;
        border-radius: 12px;
        padding: 18px;
        color: #f1f5f9;
        font-size: 1rem;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.2);
    }

    /* Thinking / Cooking Pulse Animation */
    @keyframes pulseText {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }
    .thinking-loader {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #c084fc;
        font-weight: 500;
        font-size: 1.05rem;
        padding: 12px 0;
        animation: pulseText 1.2s infinite ease-in-out;
    }

    /* Smooth Fade-In for Roast Streaming Text */
    @keyframes fadeInText {
        from {
            opacity: 0.5;
            transform: translateY(3px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .roast-stream-content {
        animation: fadeInText 0.35s ease-out;
    }



    /* Score bars */
    .score-row {
        display: flex;
        align-items: center;
        margin: 8px 0;
    }

    .score-label {
        width: 120px;
        color: #aaa;
        font-size: 0.9rem;
    }

    .score-bar-bg {
        flex: 1;
        height: 8px;
        background: #333;
        border-radius: 4px;
        overflow: hidden;
    }

    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    .score-value {
        width: 50px;
        text-align: right;
        color: #ddd;
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Top Workspace Header ───────────────────────────────────────────────────

st.markdown("""
<div class="workspace-header">
    <div>
        <span class="workspace-title">🔥 CODEROAST</span>
        <span style="color: #64748b; margin-left: 10px; font-size: 0.95rem;">| AI Code Inspector & Review Chat</span>
    </div>
    <div style="font-size: 0.85rem; color: #94a3b8;">
        <span>🤖 AI Review Engine Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Initialize ──────────────────────────────────────────────────────────────

roast_generator = RoastGenerator()

@st.cache_resource
def get_classifier():
    try:
        from src.ml.classifier import RandomCodeClassifier
        clf = RandomCodeClassifier()
        return clf
    except Exception:
        return None

@st.cache_resource
def get_codebert_scorer():
    try:
        from src.ml.codebert_model import CodeBERTScorer, SAVED_MODEL_DIR
        if SAVED_MODEL_DIR.exists():
            scorer = CodeBERTScorer(model_dir=SAVED_MODEL_DIR)
            if scorer._is_loaded:
                return scorer
    except Exception:
        return None
    return None

# ─── Sidebar Controls ────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    language = st.selectbox("Code Language", ["Python", "Java", "JavaScript"], index=0)
    roast_language = st.selectbox("Roast Tone", ["🇬🇧 English", "🇳🇵 Roman Nepali (रोमन नेपाली)"], index=0)
    target_lang = "roman_nepali" if "Nepali" in roast_language else "english"
    
    severity = st.slider("Roast Severity", 1, 3, 2, help="1 = Gentle, 2 = Standard, 3 = No Mercy")
    use_ai_llm = st.checkbox("🤖 Enable Dynamic AI Roast", value=True)
    
    st.markdown("---")
    st.caption("🤖 Model: Llama 3.2 3B (Local GPU) / Gemini Flash (Nepali API)")

    # ─── Roast History / Session Memory Panel ─────────────────────────
    if "roast_history" not in st.session_state:
        st.session_state["roast_history"] = []

    if st.session_state["roast_history"]:
        st.markdown("---")
        st.markdown(f"### 📜 Roast History ({len(st.session_state['roast_history'])})")
        with st.expander("View Past Roasts", expanded=False):
            for idx, item in enumerate(reversed(st.session_state["roast_history"])):
                real_num = len(st.session_state["roast_history"]) - idx
                grade = item.get("grade", "F")
                ts = item.get("time", "")
                preview = item.get("code_preview", "Code")
                st.markdown(f"**#{real_num}: [{grade}]** `{ts}` — `{preview}`")
                st.caption(f"_{item.get('roast', '')[:85]}..._")
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    if st.button("Load Code", key=f"hist_load_{idx}", use_container_width=True):
                        st.session_state["code_input"] = item.get("code", "")
                        st.rerun()
                with col_h2:
                    if st.button("Replay", key=f"hist_replay_{idx}", use_container_width=True):
                        st.session_state["code_input"] = item.get("code", "")
                        st.session_state["roast_text"] = item.get("roast", "")
                        st.session_state["grade_reaction"] = item.get("grade_reaction", "")
                        st.session_state["metrics"] = item.get("metrics")
                        st.session_state["scores"] = item.get("scores")
                        st.session_state["has_results"] = True
                        st.session_state["is_new_roast"] = False
                        st.rerun()
                st.markdown("---")
            if st.button("🗑️ Clear History", key="clear_hist_btn", use_container_width=True):
                st.session_state["roast_history"] = []
                st.rerun()

# ─── Split Screen Layout (Option 1) ──────────────────────────────────────────

col1, col2 = st.columns([1.1, 1], gap="medium")

# Session state setup
has_results = st.session_state.get("has_results", False)
metrics = st.session_state.get("metrics", None)
scores = st.session_state.get("scores", None)
grade_reaction = st.session_state.get("grade_reaction", "")
model_used_label = st.session_state.get("model_used_label", "")

with col1:
    st.markdown("##### 💻 Code Inspection Studio")

    # 1. Neon Metric Pills Header
    if has_results and scores and metrics:
        grade_letter = scores["grade"].split()[0]
        grade_pill_class = "neon-pill-grade-s" if grade_letter in ["S", "A"] else ("neon-pill-grade-a" if grade_letter in ["B", "C"] else "neon-pill-grade-f")
        cc_val = int(metrics.get("cyclomatic_complexity", 1))
        loc_val = metrics.get("lines_of_code", 0)
        comment_val = f"{metrics.get('comment_ratio', 0):.0%}"
        nesting_val = metrics.get("nesting_depth", 0)

        st.markdown(f"""
        <div class="neon-pill-bar">
            <div class="neon-pill {grade_pill_class}">GRADE {grade_letter}</div>
            <div class="neon-pill neon-pill-complexity">Complexity: {cc_val}</div>
            <div class="neon-pill neon-pill-lines">Lines: {loc_val}</div>
            <div class="neon-pill neon-pill-comments">Comments: {comment_val}</div>
            <div class="neon-pill">Nesting: {nesting_val}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="neon-pill-bar">
            <div class="neon-pill">GRADE --</div>
            <div class="neon-pill neon-pill-complexity">Complexity: --</div>
            <div class="neon-pill neon-pill-lines">Lines: --</div>
            <div class="neon-pill neon-pill-comments">Comments: --</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. IDE Code Input Editor
    code_input = st.text_area(
        "Code Editor",
        value=st.session_state.get("code_input", ""),
        height=320,
        placeholder="def calculate_something(x):\n    if x == 0:\n        return 'Error!'\n    else:\n        y = x * x + 10\n        return y",
        label_visibility="collapsed",
    )

    # Preset Sample Buttons
    preset_cols = st.columns([1, 1, 1])
    with preset_cols[0]:
        if st.button("📄 Hello World", use_container_width=True):
            st.session_state["code_input"] = "def hello():\n    print('Hello World!')"
            st.rerun()
    with preset_cols[1]:
        if st.button("⚡ FizzBuzz", use_container_width=True):
            st.session_state["code_input"] = "for i in range(1, 101):\n    if i % 15 == 0:\n        print('FizzBuzz')\n    elif i % 3 == 0:\n        print('Fizz')\n    elif i % 5 == 0:\n        print('Buzz')\n    else:\n        print(i)"
            st.rerun()
    with preset_cols[2]:
        if st.button("🍝 Spaghetti", use_container_width=True):
            st.session_state["code_input"] = "def do_stuff(a, b, c, d, e):\n    if a > 0:\n        if b < 10:\n            for i in range(c):\n                if d:\n                    e += 1\n                    if e > 100:\n                        return e\n    return 0"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    roast_button = st.button("🔥 Roast My Code", type="primary", use_container_width=True)

    # 3. AST Metrics & Radar Chart Expander
    if has_results and scores:
        with st.expander("📊 AST Code Metrics Breakdown & Radar Chart", expanded=False):
            # Score Bars
            def score_bar(label: str, value: float):
                color = "#4ade80" if value >= 75 else ("#facc15" if value >= 50 else ("#fb923c" if value >= 30 else "#ef4444"))
                st.markdown(f"""
                <div class="score-row">
                    <span class="score-label">{label}</span>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width: {value}%; background: {color};"></div>
                    </div>
                    <span class="score-value">{value}</span>
                </div>
                """, unsafe_allow_html=True)

            score_bar("Readability", scores["readability"])
            score_bar("Efficiency", scores["efficiency"])
            score_bar("Structure", scores["structure"])
            score_bar("Creativity", scores["creativity"])

            # Radar Chart
            fig = go.Figure(data=go.Scatterpolar(
                r=[scores["readability"], scores["efficiency"], scores["structure"], scores["creativity"], scores["readability"]],
                theta=["Readability", "Efficiency", "Structure", "Creativity", "Readability"],
                fill="toself",
                fillcolor="rgba(168, 85, 247, 0.2)",
                line=dict(color="#a855f7", width=2),
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(range=[0, 100], gridcolor="#334155"),
                    angularaxis=dict(gridcolor="#334155"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=250,
                margin=dict(l=40, r=40, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

# ─── Execute Analysis when Button Clicked ────────────────────────────────────

if roast_button:
    if not code_input:
        st.warning("Paste some code first. I need something to roast. 🔥")
    else:
        with st.spinner("📊 Analyzing AST Code Metrics & Quality..."):
            analyzer = CodeAnalyzer(code_input, language=language.lower())
            metrics = analyzer.get_metrics()
            scores = calculate_scores(metrics)

            if metrics.get("_is_plain_text", False):
                st.warning("⚠️ Non-Code Text Detected: Snippet looks like plain text prose.")
            elif metrics.get("_language_mismatch", False):
                detected = metrics.get("_detected_lang", "Python").capitalize()
                selected = metrics.get("_selected_lang", "Java").capitalize()
                st.warning(f"⚠️ Language Mismatch: Selected {selected}, but snippet looks like {detected}!")

            codebert_scorer = get_codebert_scorer()
            classifier = get_classifier()

            if codebert_scorer is not None:
                quality_level, _ = codebert_scorer.predict_quality_and_severity(code_input)
                model_used_label = "🤗 Hugging Face CodeBERT"
            elif classifier is not None:
                quality_level, _ = classifier.predict_quality(code_input, metrics)
                model_used_label = "🌲 Random Forest Quality Classifier"
            else:
                overall = scores["overall"]
                quality_level = 0 if overall >= 75 else (1 if overall >= 55 else (2 if overall >= 35 else 3))
                model_used_label = "📊 Rule-Based Static Analysis"

        if roast_generator.llm_generator is None and use_ai_llm:
            from src.roast.llm_generator import LLMRoastGenerator
            roast_generator.llm_generator = LLMRoastGenerator()

        grade_reaction = roast_generator.get_grade_reaction(
            scores["grade"],
            use_llm=False,
            code=code_input,
            metrics=metrics
        )

        st.session_state["metrics"] = metrics
        st.session_state["scores"] = scores
        st.session_state["quality_level"] = quality_level
        st.session_state["severity"] = severity
        st.session_state["code_input"] = code_input
        st.session_state["use_ai_llm"] = use_ai_llm
        st.session_state["target_lang"] = target_lang
        st.session_state["grade_reaction"] = grade_reaction
        st.session_state["model_used_label"] = model_used_label
        st.session_state["has_results"] = True
        st.session_state["is_new_roast"] = True
        st.rerun()

# ─── Right Column: AI Roast Verdict ─────────────────────────────────────────

with col2:
    st.markdown("##### 🔥 AI Roast Verdict")

    if has_results and st.session_state.get("metrics"):
        metrics = st.session_state["metrics"]
        scores = st.session_state["scores"]
        grade_reaction = st.session_state["grade_reaction"]
        target_lang = st.session_state.get("target_lang", "english")
        use_ai_llm = st.session_state.get("use_ai_llm", True)
        code_sub = st.session_state.get("code_input", "")

        # Live Typewriter Roast Container
        roast_box_placeholder = st.empty()
        card_class = "chat-bubble-assistant" if use_ai_llm else "chat-bubble-template"

        if st.session_state.get("is_new_roast", False):
            st.session_state["is_new_roast"] = False

            # Instantly display purple glowing card with animated thinking/cooking state
            thinking_msg = "⚡ Analyzing AST metrics... Cooking a brutal verdict..." if target_lang == "english" else "⚡ AST metrics हेर्दै... AI roast तयार पार्दै..."
            roast_box_placeholder.markdown(f"""
            <div class="{card_class}">
                <div style="font-size: 1.05rem; font-weight: bold; color: #a78bfa; margin-bottom: 10px;">
                    🤖 Senior Dev AI Verdict:
                </div>
                <div class="thinking-loader">
                    {thinking_msg} 💭
                </div>
            </div>
            """, unsafe_allow_html=True)

            if roast_generator.llm_generator is None and use_ai_llm:
                from src.roast.llm_generator import LLMRoastGenerator
                roast_generator.llm_generator = LLMRoastGenerator()

            roast_stream = roast_generator.generate_roast_stream(
                metrics=metrics,
                quality_level=st.session_state.get("quality_level", 2),
                severity=st.session_state.get("severity", 2),
                code=code_sub,
                use_llm=use_ai_llm,
                language=target_lang,
                grade=scores.get("grade", "F") if scores else "F"
            )

            accumulated_text = ""
            for chunk in roast_stream:
                accumulated_text += chunk

                # Live detection of [VERDICT]: tag
                if "[VERDICT]:" in accumulated_text:
                    display_roast, live_verdict = accumulated_text.split("[VERDICT]:", 1)
                    clean_accum = clean_roast_tags(display_roast)
                    if live_verdict.strip():
                        grade_reaction = live_verdict.strip().strip('"').strip("'")
                        st.session_state["grade_reaction"] = grade_reaction
                else:
                    clean_accum = clean_roast_tags(accumulated_text)

                roast_box_placeholder.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size: 1.05rem; font-weight: bold; color: #a78bfa; margin-bottom: 10px;">
                        🤖 Senior Dev AI Verdict:
                    </div>
                    <div class="roast-stream-content">
                        {clean_accum}
                    </div>
                    <br><br>
                    <em style="color: #94a3b8; font-size: 0.9rem;">— {grade_reaction}</em>
                </div>
                """, unsafe_allow_html=True)

            if "[VERDICT]:" in accumulated_text:
                final_roast, final_verdict = accumulated_text.split("[VERDICT]:", 1)
                clean_roast_text = clean_roast_tags(final_roast)
                if final_verdict.strip():
                    grade_reaction = final_verdict.strip().strip('"').strip("'")
                    st.session_state["grade_reaction"] = grade_reaction
            else:
                clean_roast_text = clean_roast_tags(accumulated_text)

            st.session_state["roast_text"] = clean_roast_text
            roast_text = clean_roast_text

            # Record in session history
            import datetime
            if "roast_history" not in st.session_state:
                st.session_state["roast_history"] = []

            history_entry = {
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "grade": scores["grade"].split()[0] if scores else "F",
                "code": code_sub,
                "code_preview": (code_sub.strip().splitlines()[0][:30] if code_sub.strip() else "code"),
                "roast": clean_roast_text,
                "grade_reaction": grade_reaction,
                "metrics": metrics,
                "scores": scores
            }
            if not st.session_state["roast_history"] or st.session_state["roast_history"][-1].get("roast") != clean_roast_text:
                st.session_state["roast_history"].append(history_entry)
        else:
            roast_text = st.session_state.get("roast_text", "")
            clean_roast_text = clean_roast_tags(roast_text)
            roast_box_placeholder.markdown(f"""
            <div class="{card_class}">
                <div style="font-size: 1.05rem; font-weight: bold; color: #a78bfa; margin-bottom: 10px;">
                    🤖 Senior Dev AI Verdict:
                </div>
                {clean_roast_text}
                <br><br>
                <em style="color: #94a3b8; font-size: 0.9rem;">— {grade_reaction}</em>
            </div>
            """, unsafe_allow_html=True)

        # ─── 🔊 Read Aloud Voice Player ─────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🔊 Read Aloud Voice Narration")

        # Engine 1: HTML5 Web Speech API Interactive Button
        import streamlit.components.v1 as components
        js_text = json.dumps(clean_roast_text)
        speech_html = f"""
        <div style="font-family: system-ui, -apple-system, sans-serif; display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <button id="speechBtn" onclick="toggleSpeech()" style="
                background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
                color: #ffffff;
                border: none;
                padding: 12px 22px;
                border-radius: 10px;
                font-weight: 700;
                font-size: 1rem;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
                transition: all 0.2s ease;
            ">
                <span id="btnIcon" style="font-size: 1.2rem;">🔊</span>
                <span id="btnText">Read Roast Aloud</span>
            </button>
        </div>

        <script>
        var synth = window.speechSynthesis;
        
        function toggleSpeech() {{
            if (synth.speaking) {{
                synth.cancel();
                document.getElementById('btnText').innerText = 'Read Roast Aloud';
                document.getElementById('btnIcon').innerText = '🔊';
                return;
            }}
            
            var text = {js_text};
            var utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            
            utterance.onend = function() {{
                document.getElementById('btnText').innerText = 'Read Roast Aloud';
                document.getElementById('btnIcon').innerText = '🔊';
            }};
            
            utterance.onerror = function() {{
                document.getElementById('btnText').innerText = 'Read Roast Aloud';
                document.getElementById('btnIcon').innerText = '🔊';
            }};

            document.getElementById('btnText').innerText = 'Stop Speech';
            document.getElementById('btnIcon').innerText = '⏹️';
            
            synth.speak(utterance);
        }}
        </script>
        """
        components.html(speech_html, height=65)


        # ─── 🎨 AI Custom Code Meme ──────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🎨 AI Custom Code Meme")
        
        meme_img_bytes = generate_code_meme(
            metrics=metrics,
            grade=scores["grade"],
            language=language,
            code=code_sub,
            target_lang=target_lang
        )
        st.image(meme_img_bytes, use_container_width=True)

        meme_btn_col1, meme_btn_col2 = st.columns([1, 1])
        with meme_btn_col1:
            if st.button("🎲 Roll Another Meme", use_container_width=True):
                st.rerun()
        with meme_btn_col2:
            st.download_button(
                label="📥 Download Custom Meme (PNG)",
                data=meme_img_bytes,
                file_name=f"coderoast_meme_{scores['grade'].split()[0]}.png",
                mime="image/png",
                use_container_width=True
            )




    else:
        # Default placeholder when app starts
        st.markdown("""
        <div class="chat-bubble-assistant">
            👋 <strong>CodeRoast AI Reviewer Online!</strong><br><br>
            Paste your source code in the <strong>Code Inspection Studio</strong> on the left, select your options, and click <strong>🔥 Roast My Code</strong> to generate your live roast verdict!
        </div>
        """, unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; color: #475569; font-size: 0.8rem;">'
    'Built by gyr0byte — Not a person, a process. Always building, never stopping. 🔥'
    '</p>',
    unsafe_allow_html=True,
)
