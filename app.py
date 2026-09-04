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


def generate_roast_audio(text: str, lang_code: str = "en") -> Optional[bytes]:

    """Generate Text-to-Speech MP3 audio bytes using gTTS."""
    clean_text = (
        text.replace("🤖 [Gemini Flash AI Roast]: ", "")
        .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
        .replace("🤖 AI Roast: ", "")
        .replace("🤖 ", "")
    )
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


MEME_CATALOG = {
    "mismatch": [
        {
            "template": "drake_hotline_bling.jpg",
            "top": "SELECTING {sel} IN THE UI DROPDOWN",
            "bottom": "PASTING {det} CODE LIKE A TOTAL CHAD!",
            "top_y": 0.14, "bottom_y": 0.65
        },
        {
            "template": "theyre_the_same_picture.jpg",
            "top": "PAM: CORPORATE WANTS YOU TO FIND THE DIFFERENCE",
            "bottom": "{sel} DROPDOWN vs {det} CODE (THEY ARE THE SAME)",
            "top_y": 0.08, "bottom_y": 0.76
        },
        {
            "template": "two_buttons.jpg",
            "top": "PRESS BUTTON FOR {sel} OR PASTES {det}?",
            "bottom": "COMPILER: TOTAL CONFUSION UNLOCKED!",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "change_my_mind.jpg",
            "top": "{det} CODE IN A {sel} DROPDOWN IS REVOLUTIONARY",
            "bottom": "CHANGE MY MIND",
            "top_y": 0.12, "bottom_y": 0.75
        },
        {
            "template": "trade_offer.jpg",
            "top": "I RECEIVE: {sel} DROPDOWN CHOICE",
            "bottom": "YOU GIVE: {det} CODE SPAGHETTI!",
            "top_y": 0.10, "bottom_y": 0.75
        }
    ],
    "nesting": [
        {
            "template": "running_away_balloon.jpg",
            "top": "ME TRYING TO WRITE CLEAN LOGIC",
            "bottom": "NESTING DEPTH LEVEL {nesting} (INCEPTION)!",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "drake_hotline_bling.jpg",
            "top": "1-LEVEL FLAT CONTROL FLOW",
            "bottom": "{nesting} NESTED FOR-LOOPS INSIDE AN IF STATEMENT!",
            "top_y": 0.14, "bottom_y": 0.65
        },
        {
            "template": "left_exit_12_off_ramp.jpg",
            "top": "EARLY RETURN PATTERN",
            "bottom": "INDENTING {nesting} LEVELS DEEP INTO OBLIVION!",
            "top_y": 0.18, "bottom_y": 0.76
        },
        {
            "template": "expanding_brain.jpg",
            "top": "1 IF STATEMENT",
            "bottom": "{nesting} LEVELS OF DEEP NESTED INCEPTION!",
            "top_y": 0.08, "bottom_y": 0.78
        }
    ],
    "complexity": [
        {
            "template": "batman_slapping_robin.jpg",
            "top": "MY CODE WORKS FINE BRO!",
            "bottom": "CYCLOMATIC COMPLEXITY IS {comp} YOU DUMBASS!",
            "top_y": 0.08, "bottom_y": 0.75
        },
        {
            "template": "roll_safe_think_about_it.jpg",
            "top": "CANNOT HAVE LOGIC BUGS",
            "bottom": "IF COMPLEXITY IS {comp} AND NO ONE CAN READ IT!",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "left_exit_12_off_ramp.jpg",
            "top": "SIMPLE DECISION TREES",
            "bottom": "CYCLOMATIC COMPLEXITY {comp} NIGHTMARE!",
            "top_y": 0.18, "bottom_y": 0.76
        },
        {
            "template": "panik_kalm_panik.jpg",
            "top": "CODE COMPILES WITHOUT ERRORS",
            "bottom": "COMPLEXITY SCORE IS {comp}! PANIK!",
            "top_y": 0.10, "bottom_y": 0.75
        }
    ],
    "spaghetti": [
        {
            "template": "left_exit_12_off_ramp.jpg",
            "top": "CLEAN REUSABLE FUNCTIONS",
            "bottom": "ONE {loc}-LINE MONOLITHIC SPAGHETTI FUNCTION!",
            "top_y": 0.18, "bottom_y": 0.76
        },
        {
            "template": "drake_hotline_bling.jpg",
            "top": "BREAKING CODE INTO MULTIPLE MODULES",
            "bottom": "WRITING ONE GIANT {loc}-LINE FUNCTION TO RULE ALL!",
            "top_y": 0.14, "bottom_y": 0.65
        },
        {
            "template": "buff_doge_vs._cheems.jpg",
            "top": "SENIOR DEV: 10-LINE MODULAR UTILITY",
            "bottom": "YOU: ONE {loc}-LINE GOD FUNCTION IN 1 FILE!",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "clown_applying_makeup.jpg",
            "top": "I WILL REFACTOR THIS FUNCTION LATER",
            "bottom": "IT IS NOW {loc} LINES LONG AND UNTOUCHABLE!",
            "top_y": 0.08, "bottom_y": 0.75
        },
        {
            "template": "a_train_hitting_a_school_bus.jpg",
            "top": "CLEAN SOFTWARE ARCHITECTURE",
            "bottom": "YOUR {loc}-LINE MONOLITHIC FUNCTION!",
            "top_y": 0.10, "bottom_y": 0.75
        }
    ],
    "praise": [
        {
            "template": "epic_handshake.jpg",
            "top": "SENIOR ARCHITECT & YOUR CLEAN CODE",
            "bottom": "GRADE {grade} PERFECT PEP8 ARCHITECTURE!",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "buff_doge_vs._cheems.jpg",
            "top": "YOUR CODE (GRADE {grade} GIGACHAD)",
            "bottom": "OTHER STUDENTS SPAGHETTI CODE",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "leonardo_dicaprio_cheers.jpg",
            "top": "CHEERS TO WRITE CLEAN CODE",
            "bottom": "GRADE {grade} LEGENDARY ARCHITECTURE!",
            "top_y": 0.08, "bottom_y": 0.75
        }
    ],
    "disaster": [
        {
            "template": "disaster_girl.jpg",
            "top": "ME PUSHING CODE TO PRODUCTION",
            "bottom": "GRADE {grade}: ENTIRE SERVER BURNING DOWN!",
            "top_y": 0.08, "bottom_y": 0.75
        },
        {
            "template": "drake_hotline_bling.jpg",
            "top": "WRITING WORKING BUG-FREE CODE",
            "bottom": "PASTING SYNTAX ERRORS & PRAYING TO GOD!",
            "top_y": 0.14, "bottom_y": 0.65
        },
        {
            "template": "roll_safe_think_about_it.jpg",
            "top": "CANNOT FAIL CODE REVIEW",
            "bottom": "IF YOU RECEIVE GRADE {grade} AND REJECT IT ALL!",
            "top_y": 0.10, "bottom_y": 0.75
        },
        {
            "template": "clown_applying_makeup.jpg",
            "top": "JUST ONE MORE QUICK FIX BEFORE SUBMITTING",
            "bottom": "FINAL GRADE {grade}: EVERYTHING IS BROKEN!",
            "top_y": 0.08, "bottom_y": 0.75
        },
        {
            "template": "hide_the_pain_harold.jpg",
            "top": "SMILE AND PRETEND IT WORKS",
            "bottom": "COMPILER VERDICT: GRADE {grade} DISASTER!",
            "top_y": 0.08, "bottom_y": 0.75
        }
    ]
}


def generate_code_meme(metrics: dict, grade: str, language: str) -> bytes:
    """Generate an authentic classic Impact Font meme using templates from assets/memes with dynamic pool selection and precise template alignment."""
    import os, random
    grade_clean = grade.encode("ascii", "ignore").decode("ascii").strip()
    grade_str = grade_clean.split()[0] if grade_clean else "F"
    complexity = metrics.get("cyclomatic_complexity", 1)
    nesting = metrics.get("max_nesting_depth", 0)
    loc = metrics.get("lines_of_code", 0)
    is_mismatch = metrics.get("_language_mismatch", False)
    
    sel_lang = metrics.get("_selected_lang", "JAVA").upper()
    det_lang = metrics.get("_detected_lang", "PYTHON").upper()
    
    # ── Category Selection ───────────────────────────────────────────
    if is_mismatch:
        category = "mismatch"
    elif nesting >= 3:
        category = "nesting"
    elif complexity >= 5:
        category = "complexity"
    elif loc > 30:
        category = "spaghetti"
    elif grade_str in ["S", "A"]:
        category = "praise"
    else:
        category = "disaster"
        
    meme_item = random.choice(MEME_CATALOG[category])
    template_name = meme_item["template"]
    
    top_text = meme_item["top"].format(sel=sel_lang, det=det_lang, nesting=nesting, comp=complexity, loc=loc, grade=grade_str)
    bottom_text = meme_item["bottom"].format(sel=sel_lang, det=det_lang, nesting=nesting, comp=complexity, loc=loc, grade=grade_str)
    
    top_y_pct = meme_item.get("top_y", 0.10)
    bottom_y_pct = meme_item.get("bottom_y", 0.75)
    
    meme_dir = "assets/memes"
    template_path = os.path.join(meme_dir, template_name)
    if not os.path.exists(template_path):
        files = [f for f in os.listdir(meme_dir) if f.endswith(".jpg")] if os.path.exists(meme_dir) else []
        template_path = os.path.join(meme_dir, files[0]) if files else None
        
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
    st.caption("🤖 Model: Qwen2.5-Coder (Local GPU) / Gemini Flash (Nepali API)")

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
            use_llm=use_ai_llm,
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
                language=target_lang
            )


            accumulated_text = ""
            for chunk in roast_stream:
                accumulated_text += chunk
                clean_accum = (
                    accumulated_text
                    .replace("🤖 [Gemini Flash AI Roast]: ", "")
                    .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
                    .replace("🤖 AI Roast: ", "")
                    .replace("🤖 ", "")
                )

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


            st.session_state["roast_text"] = accumulated_text
            roast_text = accumulated_text
            clean_roast_text = (
                roast_text
                .replace("🤖 [Gemini Flash AI Roast]: ", "")
                .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
                .replace("🤖 AI Roast: ", "")
                .replace("🤖 ", "")
            )
        else:
            roast_text = st.session_state.get("roast_text", "")
            clean_roast_text = (
                roast_text
                .replace("🤖 [Gemini Flash AI Roast]: ", "")
                .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
                .replace("🤖 AI Roast: ", "")
                .replace("🤖 ", "")
            )
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
            language=language
        )
        st.image(meme_img_bytes, use_container_width=True)
        
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
