"""
🔥 CodeRoast — Brutally Honest Code Reviews
Streamlit Chat Interface — ChatGPT / Claude Style
"""

import config  # noqa: F401 — Sets HF_HOME and TF log level first

import streamlit as st
import plotly.graph_objects as go
import os
import sys
import json
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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
from src.roast.templates import GRADE_REACTIONS, NEPALI_ROAST_TEMPLATES

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CodeRoast 🔥",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium Chat CSS ────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp {
        background: linear-gradient(180deg, #08080f 0%, #0e1117 100%);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0c1a 0%, #111827 100%);
        border-right: 1px solid rgba(167, 139, 250, 0.1);
    }

    .sidebar-brand {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8c00 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.7rem;
        font-weight: 900;
        letter-spacing: -0.5px;
    }

    .grade-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 10px 0;
    }
    .grade-letter {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ff4b4b, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .grade-label { color: #aaa; font-size: 0.85rem; }

    .score-row { display: flex; align-items: center; margin: 5px 0; }
    .score-label { width: 85px; color: #aaa; font-size: 0.78rem; }
    .score-bar-bg { flex: 1; height: 5px; background: #333; border-radius: 3px; overflow: hidden; }
    .score-bar-fill { height: 100%; border-radius: 3px; }
    .score-value { width: 30px; text-align: right; color: #ddd; font-weight: 600; font-size: 0.78rem; }

    .welcome-box {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; padding: 120px 20px; text-align: center;
    }
    .welcome-title {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8c00 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem; font-weight: 900; margin-bottom: 8px;
    }
    .welcome-sub { color: #555; font-size: 1.05rem; max-width: 480px; }

    .roast-bubble {
        background: linear-gradient(135deg, #1a0a2e 0%, #0f0a1e 100%);
        border: 1px solid rgba(167, 139, 250, 0.25);
        border-radius: 10px;
        padding: 16px 18px;
        margin: 6px 0;
        line-height: 1.65;
        color: #e0e0e0;
        font-size: 0.95rem;
        box-shadow: 0 4px 20px rgba(167, 139, 250, 0.08);
    }

    .roast-header {
        color: #a78bfa; font-weight: 700; font-size: 0.8rem;
        margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
    }

    .grade-pill {
        display: inline-block;
        background: linear-gradient(135deg, #ff4b4b, #ff8c00);
        color: white; font-weight: 800; font-size: 0.7rem;
        padding: 2px 8px; border-radius: 10px;
    }

    .shame-entry {
        background: #111827; border-left: 3px solid #ef4444;
        padding: 8px 10px; margin: 5px 0; border-radius: 4px; font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Initialize ──────────────────────────────────────────────────────────────

roast_generator = RoastGenerator()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─── Helper Functions ────────────────────────────────────────────────────────

LEADERBOARD_FILE = Path(__file__).parent / "data" / "leaderboard.json"

def load_leaderboard():
    if not LEADERBOARD_FILE.exists():
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_to_leaderboard(code_snippet, language, score, grade, roast_text):
    LEADERBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    board = load_leaderboard()
    code_sub = code_snippet[:150].strip()
    for item in board:
        if item.get("snippet", "") == code_sub:
            return
    board.append({
        "language": language, "score": score, "grade": grade,
        "snippet": code_sub,
        "roast": roast_text[:180] + ("..." if len(roast_text) > 180 else "")
    })
    board.sort(key=lambda x: x["score"])
    board = board[:10]
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(board, f, indent=2)
    except Exception:
        pass

def generate_roast_card_image(grade, score, language, roast):
    width, height = 800, 450
    img = Image.new("RGB", (width, height), color=(14, 17, 23))
    draw = ImageDraw.Draw(img)
    for x in range(width):
        r = int(255 - (x / width) * 100)
        g = int(75 + (x / width) * 100)
        draw.line([(x, 0), (x, 8)], fill=(r, g, 0))
    font = ImageFont.load_default()
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(255, 75, 75), width=2)
    draw.text((40, 40), "CodeRoast - Official Verdict", fill=(255, 140, 0), font=font)
    gc = grade.encode("ascii", "ignore").decode("ascii").strip()
    gs = gc.split(" ")[0] if gc else "F"
    draw.text((40, 90), f"Grade: {gs}", fill=(255, 75, 75), font=font)
    draw.text((200, 90), f"Score: {score}/100", fill=(255, 215, 0), font=font)
    draw.text((400, 90), f"Language: {language}", fill=(170, 170, 170), font=font)
    draw.line([(40, 130), (width - 40, 130)], fill=(51, 51, 51), width=1)
    cr = roast.replace("🤖 [Gemini Flash AI Roast]: ", "").replace("🤖 [Qwen2.5-Coder AI Roast]: ", "").replace("🤖 ", "").encode("ascii", "ignore").decode("ascii")
    words, lines, curr = cr.split(), [], ""
    for w in words:
        if len(curr + " " + w) > 75:
            lines.append(curr); curr = w
        else:
            curr += " " + w if curr else w
    if curr: lines.append(curr)
    y = 150
    for line in lines[:8]:
        draw.text((40, y), line, fill=(220, 220, 220), font=font); y += 24
    draw.text((40, height - 45), "coderoast.dev | @gyr0byte", fill=(136, 136, 136), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def clean_roast(text):
    return (text.replace("🤖 [Gemini Flash AI Roast]: ", "")
            .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
            .replace("🤖 AI Roast: ", "").replace("🤖 ", ""))

# ─── Lazy Model Loaders ──────────────────────────────────────────────────────

@st.cache_resource
def get_classifier():
    try:
        from src.ml.classifier import CodeQualityClassifier
        clf = CodeQualityClassifier()
        clf.load_model()
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
        pass
    return None

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-brand">🔥 CodeRoast AI</div>', unsafe_allow_html=True)
    st.caption("Brutally honest code reviews. You asked for this.")
    st.divider()

    language = st.selectbox("📝 Code Language", ["Python", "Java", "JavaScript"])
    roast_language = st.selectbox("🌐 Roast Language", ["🇬🇧 English", "🇳🇵 Roman Nepali (रोमन नेपाली)"])
    target_lang = "roman_nepali" if "Nepali" in roast_language else "english"
    severity = st.slider("🔥 Roast Severity", 1, 3, 2, help="1 = Mild · 2 = Medium · 3 = Spicy 🌶️")
    use_ai_llm = st.checkbox("🤖 Enable AI Roast", value=True)

    st.divider()
    code_input = st.text_area(
        "📋 Paste Your Code",
        height=180,
        placeholder="def my_function(x):\n    # TODO: write code\n    pass",
    )
    roast_button = st.button("🔥 Roast My Code", type="primary", use_container_width=True)

    # ── Post-Roast Analytics ──────────────────────────────────────────────
    if "latest_scores" in st.session_state:
        st.divider()
        sc = st.session_state.latest_scores
        mt = st.session_state.latest_metrics
        ml = st.session_state.get("latest_model_label", "")

        gl = sc["grade"].split(" ")[0]
        gd = " ".join(sc["grade"].split(" ")[1:])
        st.markdown(f"""
        <div class="grade-card">
            <div class="grade-letter">{gl}</div>
            <div class="grade-label">{gd}</div>
            <div style="color:#666;font-size:0.78rem;margin-top:5px;">Score: {sc['overall']}/100</div>
            <div style="color:#4ade80;font-size:0.7rem;margin-top:3px;">{ml}</div>
        </div>
        """, unsafe_allow_html=True)

        def score_bar(label, value):
            c = "#4ade80" if value >= 75 else "#facc15" if value >= 50 else "#fb923c" if value >= 30 else "#ef4444"
            st.markdown(f"""<div class="score-row"><span class="score-label">{label}</span>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{value}%;background:{c};"></div></div>
            <span class="score-value">{value}</span></div>""", unsafe_allow_html=True)

        score_bar("Readability", sc["readability"])
        score_bar("Efficiency", sc["efficiency"])
        score_bar("Structure", sc["structure"])
        score_bar("Creativity", sc["creativity"])

        with st.expander("📊 Quality Radar", expanded=False):
            fig = go.Figure(data=go.Scatterpolar(
                r=[sc["readability"], sc["efficiency"], sc["structure"], sc["creativity"], sc["readability"]],
                theta=["Readability", "Efficiency", "Structure", "Creativity", "Readability"],
                fill="toself", fillcolor="rgba(255,75,75,0.15)", line=dict(color="#FF4B4B", width=2),
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(range=[0, 100], showticklabels=True, tickfont=dict(size=8, color="#666"), gridcolor="#333"),
                    angularaxis=dict(tickfont=dict(size=9, color="#aaa"), gridcolor="#333"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=35, r=35, t=15, b=15), height=220,
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Raw Metrics"):
            mc = st.columns(2)
            items = [
                ("Lines", mt["lines_of_code"]), ("Functions", mt["function_count"]),
                ("Avg Length", mt["avg_function_length"]), ("Complexity", mt["cyclomatic_complexity"]),
                ("Naming", mt["naming_score"]), ("Comments", f"{mt['comment_ratio']:.1%}"),
                ("Nesting", mt["nesting_depth"]), ("Duplication", mt["duplicate_code_score"]),
            ]
            for i, (n, v) in enumerate(items):
                with mc[i % 2]:
                    st.metric(label=n, value=v)

    # ── Hall of Shame ─────────────────────────────────────────────────────
    st.divider()
    with st.expander("🏆 Hall of Shame"):
        lb = load_leaderboard()
        if not lb:
            st.info("No entries yet. Submit some bad code! 🔥")
        else:
            for rank, entry in enumerate(lb, 1):
                st.markdown(f"""<div class="shame-entry">
                    <span style="color:#f87171;font-weight:600;">#{rank}</span>
                    <span style="color:#9ca3af;">— {entry.get('grade','F')} ({entry.get('score',0)}/100)</span>
                    <div style="color:#6b7280;font-style:italic;margin-top:3px;font-size:0.72rem;">
                        "{entry.get('roast','')[:80]}..."
                    </div>
                </div>""", unsafe_allow_html=True)

    st.divider()
    st.caption("Built by gyr0byte — Always building, never stopping. 🔥")

# ─── Handle Roast Button ─────────────────────────────────────────────────────

if roast_button:
    if not code_input:
        st.warning("Paste some code first! 🔥")
    else:
        with st.spinner("📊 Analyzing code metrics & quality..."):
            lang_key = language.lower()
            analyzer = CodeAnalyzer(code_input, language=lang_key)
            analysis_metrics = analyzer.get_metrics()
            analysis_scores = calculate_scores(analysis_metrics)

            codebert = get_codebert_scorer()
            clf = get_classifier()
            if codebert is not None:
                quality_level, _ = codebert.predict_quality_and_severity(code_input)
                model_label = "🤗 CodeBERT"
            elif clf is not None:
                quality_level, _ = clf.predict_quality(code_input, analysis_metrics)
                model_label = "🌲 Random Forest"
            else:
                ov = analysis_scores["overall"]
                quality_level = 0 if ov >= 75 else 1 if ov >= 55 else 2 if ov >= 35 else 3
                model_label = "📊 Rule-Based"

        if roast_generator.llm_generator is None and use_ai_llm:
            from src.roast.llm_generator import LLMRoastGenerator
            roast_generator.llm_generator = LLMRoastGenerator()

        grade_reaction = roast_generator.get_grade_reaction(
            analysis_scores["grade"], use_llm=use_ai_llm, code=code_input, metrics=analysis_metrics
        )

        st.session_state.chat_history.append({
            "role": "user", "code": code_input, "language": language,
        })
        st.session_state.pending_roast = {
            "metrics": analysis_metrics, "scores": analysis_scores,
            "quality_level": quality_level, "severity": severity,
            "use_ai": use_ai_llm, "target_lang": target_lang,
            "grade_reaction": grade_reaction, "model_label": model_label,
            "code": code_input, "language": language,
        }

# ─── Main Chat Canvas ────────────────────────────────────────────────────────

# Welcome screen
if not st.session_state.chat_history and "pending_roast" not in st.session_state:
    st.markdown("""
    <div class="welcome-box">
        <div style="font-size: 4.5rem;">🔥</div>
        <div class="welcome-title">CodeRoast AI</div>
        <div class="welcome-sub">
            Paste your code in the sidebar and hit <strong>Roast My Code</strong>
            to get brutally honest, AI-powered code reviews.
        </div>
        <div style="color: #444; font-size: 0.85rem; margin-top: 15px;">
            Supports Python · Java · JavaScript &nbsp;|&nbsp; English · Roman Nepali
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.caption(f"📝 {msg['language']}")
            st.code(msg["code"], language=msg["language"].lower())

    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🔥"):
            grade_pill = msg.get("grade", "")
            score_val = msg.get("score", 0)
            st.markdown(f"""<div class="roast-header">
                🔥 CODE ROAST AI &nbsp;
                <span class="grade-pill">{grade_pill.split(' ')[0]} — {score_val}/100</span>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="roast-bubble">{msg['content']}<br><br>
                <em style="color:#888;">— {msg.get('reaction','')}</em>
            </div>""", unsafe_allow_html=True)

            card_bytes = generate_roast_card_image(
                grade=msg.get("grade", "F"), score=msg.get("score", 0),
                language=msg.get("language", "Python"), roast=msg.get("content", "")
            )
            st.download_button(
                "⬇️ Download Roast Card",
                data=card_bytes,
                file_name=f"coderoast_{msg.get('grade','F').split()[0]}.png",
                mime="image/png",
                key=f"dl_{id(msg)}",
            )

# Stream pending roast
if "pending_roast" in st.session_state:
    data = st.session_state.pop("pending_roast")

    with st.chat_message("assistant", avatar="🔥"):
        grade_pill_text = data["scores"]["grade"].split(" ")[0]
        st.markdown(f"""<div class="roast-header">
            🔥 CODE ROAST AI — streaming... &nbsp;
            <span class="grade-pill">{grade_pill_text} — {data['scores']['overall']}/100</span>
        </div>""", unsafe_allow_html=True)

        placeholder = st.empty()

        roast_stream = roast_generator.generate_roast_stream(
            metrics=data["metrics"], quality_level=data["quality_level"],
            severity=data["severity"], code=data["code"],
            use_llm=data["use_ai"], language=data["target_lang"]
        )

        accumulated = ""
        for chunk in roast_stream:
            accumulated += chunk
            cleaned = clean_roast(accumulated)
            placeholder.markdown(f"""<div class="roast-bubble">{cleaned}</div>""", unsafe_allow_html=True)

        final_clean = clean_roast(accumulated)
        placeholder.markdown(f"""<div class="roast-bubble">{final_clean}<br><br>
            <em style="color:#888;">— {data['grade_reaction']}</em>
        </div>""", unsafe_allow_html=True)

        card_bytes = generate_roast_card_image(
            grade=data["scores"]["grade"], score=data["scores"]["overall"],
            language=data["language"], roast=final_clean
        )
        st.download_button(
            "⬇️ Download Roast Card",
            data=card_bytes,
            file_name=f"coderoast_{grade_pill_text}.png",
            mime="image/png",
            key="dl_new",
        )

    # Save to history
    st.session_state.chat_history.append({
        "role": "assistant", "content": final_clean,
        "grade": data["scores"]["grade"], "score": data["scores"]["overall"],
        "reaction": data["grade_reaction"], "language": data["language"],
    })

    # Update sidebar analytics
    st.session_state.latest_scores = data["scores"]
    st.session_state.latest_metrics = data["metrics"]
    st.session_state.latest_model_label = data["model_label"]

    # Save to leaderboard
    save_to_leaderboard(
        code_snippet=data["code"], language=data["language"],
        score=data["scores"]["overall"], grade=data["scores"]["grade"],
        roast_text=final_clean
    )

# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#333;font-size:0.75rem;">'
    'Built by gyr0byte — Not a person, a process. Always building, never stopping. 🔥'
    '</p>',
    unsafe_allow_html=True,
)
