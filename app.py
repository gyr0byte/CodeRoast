"""
🔥 CodeRoast — Brutally Honest Code Reviews
Streamlit Chat Interface — Custom High-Fidelity Theme (Matching Mockup)
"""

import config  # noqa: F401 — Sets HF_HOME and TF log level first

import streamlit as st
import plotly.graph_objects as go
import os
import sys
import json
import io
import time
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
    page_title="CodeRoast AI 🔥",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for Exact Mockup Match ───────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Body & Background */
    .stApp {
        background-color: #0b0c12 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #13141f !important;
        border-right: 1px solid #232538 !important;
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }

    .sidebar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.2rem;
    }
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .sidebar-section-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 0.8rem;
        margin-bottom: 0.2rem;
        letter-spacing: -0.2px;
    }

    .sidebar-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }

    .metrics-card {
        background: #181a28;
        border: 1px solid #26293e;
        border-radius: 12px;
        padding: 10px;
        margin-top: 0.4rem;
    }

    /* Main Chat Section */
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 1px solid #1e2030;
        margin-bottom: 20px;
    }
    .chat-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc;
    }

    /* User Message Card */
    .user-msg-container {
        background: #171926;
        border: 1px solid #25283d;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .user-msg-header {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 10px;
    }
    .user-msg-text {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin-top: 10px;
    }

    /* AI Assistant Card */
    .ai-msg-wrapper {
        display: flex;
        gap: 14px;
        margin-bottom: 24px;
    }
    .ai-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #25163a;
        border: 1px solid #6d28d9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .ai-content-box {
        flex-grow: 1;
    }

    .ai-roast-card {
        background: linear-gradient(135deg, #1c1533 0%, #130f24 100%);
        border: 1px solid #7c3aed;
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.18);
        border-radius: 16px;
        padding: 18px 22px;
        color: #f1f5f9;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .ai-roast-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .ai-roast-status {
        color: #c4b5fd;
        letter-spacing: 0.3px;
    }
    .ai-roast-badge {
        background: rgba(124, 58, 237, 0.3);
        border: 1px solid #7c3aed;
        color: #ff8c00;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Action Buttons Row */
    .action-buttons-row {
        display: flex;
        gap: 10px;
        margin-top: 12px;
    }

    .action-btn {
        background: #171926;
        border: 1px solid #2e324c;
        color: #cbd5e1;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .action-btn-primary {
        border-color: #d97706;
        color: #f59e0b;
    }

    /* Welcome / Empty State */
    .welcome-container {
        text-align: center;
        padding: 80px 20px;
    }
    .welcome-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8c00 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* Custom Input Controls Styling */
    .stSelectbox > div > div {
        background-color: #171926 !important;
        border: 1px solid #2a2d42 !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }

    .stTextArea textarea {
        background-color: #12131c !important;
        border: 1px solid #232538 !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    /* Severity Slider customization */
    .stSlider > div {
        padding-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Initialize State ────────────────────────────────────────────────────────

roast_generator = RoastGenerator()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "latest_metrics" not in st.session_state:
    # Default metrics for initial radar display
    st.session_state.latest_metrics = {
        "lines_of_code": 15, "function_count": 1, "avg_function_length": 15,
        "cyclomatic_complexity": 2, "naming_score": 75, "comment_ratio": 0.0,
        "nesting_depth": 1, "duplicate_code_score": 100
    }
if "latest_scores" not in st.session_state:
    st.session_state.latest_scores = {
        "readability": 65, "efficiency": 80, "structure": 70, "creativity": 60, "overall": 70, "grade": "B Good"
    }

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

# ─── Lazy Model Loaders ───────────────────────────────────────────────────────

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

# ─── Sidebar (Matching Mockup Left Panel) ────────────────────────────────────

with st.sidebar:
    # Sidebar Header
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-title">🔥 CodeRoast AI</div>
        <div style="color: #64748b; cursor: pointer; font-size: 0.9rem;">«</div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Project Settings
    st.markdown('<div class="sidebar-section-title">Project Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">LANGUAGE</div>', unsafe_allow_html=True)
    language = st.selectbox("Language Selector", ["Python", "Java", "JavaScript"], label_visibility="collapsed")

    # 2. Severity Slider
    st.markdown('<div class="sidebar-section-title">Severity Slider</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; margin-bottom: 2px;">
        <span>Mild</span><span>Medium</span><span>Spicy</span>
    </div>
    """, unsafe_allow_html=True)
    severity = st.slider("Severity Level", 1, 3, 2, label_visibility="collapsed")

    # 3. Roast Metrics (Radar Chart Card)
    st.markdown('<div class="sidebar-section-title">Roast Metrics</div>', unsafe_allow_html=True)
    
    sc = st.session_state.latest_scores
    fig = go.Figure(data=go.Scatterpolar(
        r=[sc["readability"], sc["efficiency"], sc["structure"], sc["creativity"], sc["readability"]],
        theta=["Readability", "Performance", "Security", "Code Style", "Readability"],
        fill="toself",
        fillcolor="rgba(167, 139, 250, 0.25)",
        line=dict(color="#a78bfa", width=2),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor="#2a2d42"),
            angularaxis=dict(tickfont=dict(size=8, color="#94a3b8"), gridcolor="#2a2d42"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=25, t=15, b=15),
        height=180,
    )
    
    st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Parameter Controls (Collapsible)
    with st.expander("Parameter Controls", expanded=False):
        roast_language = st.selectbox("Roast Output", ["🇬🇧 English", "🇳🇵 Roman Nepali"])
        target_lang = "roman_nepali" if "Nepali" in roast_language else "english"
        use_ai_llm = st.checkbox("Enable Dynamic AI", value=True)

    # 5. Code Input & Trigger Button
    st.markdown('<div class="sidebar-section-title">Code Input</div>', unsafe_allow_html=True)
    code_input = st.text_area(
        "Code Input",
        height=140,
        placeholder="def calculate_area(radius):\n    pi = 3.14159\n    return pi * radius * radius",
        label_visibility="collapsed"
    )
    
    roast_button = st.button("🔥 Roast Code", type="primary", use_container_width=True)

    # Hall of Shame expander in sidebar
    with st.expander("🏆 Hall of Shame", expanded=False):
        lb = load_leaderboard()
        if not lb:
            st.caption("No entries yet. Submit bad code! 🔥")
        else:
            for rank, entry in enumerate(lb[:5], 1):
                st.markdown(f"""
                <div style="background:#171926; border-left:3px solid #ef4444; padding:6px 10px; margin:4px 0; border-radius:4px; font-size:0.75rem;">
                    <span style="color:#f87171; font-weight:700;">#{rank} {entry.get('grade','F')}</span> ({entry.get('score',0)}/100)
                    <div style="color:#94a3b8; font-style:italic; margin-top:2px;">"{entry.get('roast','')[:60]}..."</div>
                </div>
                """, unsafe_allow_html=True)

# ─── Handle Roast Processing ─────────────────────────────────────────────────

if roast_button:
    if not code_input:
        st.sidebar.warning("Paste code first!")
    else:
        with st.spinner("Analyzing AST Metrics..."):
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

        st.session_state.latest_scores = analysis_scores
        st.session_state.latest_metrics = analysis_metrics

        curr_time = time.strftime("%I:%M %p")
        st.session_state.chat_history.append({
            "role": "user", "code": code_input, "language": language, "time": curr_time
        })
        st.session_state.pending_roast = {
            "metrics": analysis_metrics, "scores": analysis_scores,
            "quality_level": quality_level, "severity": severity,
            "use_ai": use_ai_llm, "target_lang": target_lang,
            "grade_reaction": grade_reaction, "model_label": model_label,
            "code": code_input, "language": language, "time": curr_time
        }

# ─── Main Chat Canvas (Matching Mockup Center) ───────────────────────────────

# Top Chat Header Bar
st.markdown("""
<div class="chat-header">
    <div class="chat-title">Chat</div>
    <div style="color: #64748b; font-size: 1.2rem; cursor: pointer;">⚙️</div>
</div>
""", unsafe_allow_html=True)

# Welcome State
if not st.session_state.chat_history and "pending_roast" not in st.session_state:
    st.markdown("""
    <div class="welcome-container">
        <div style="font-size: 3.8rem; margin-bottom: 10px;">🔥</div>
        <div class="welcome-title">CodeRoast AI</div>
        <p style="color: #94a3b8; font-size: 1.05rem; max-width: 500px; margin: 0 auto 25px auto;">
            Enter your code in the sidebar panel and click <strong>Roast Code</strong> to generate a real-time AI code review.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Render Chat Thread
for idx, msg in enumerate(st.session_state.chat_history):
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-msg-container">
            <div class="user-msg-header">USER - {msg.get('time', '10:15 AM')} ({msg['language']})</div>
        </div>
        """, unsafe_allow_html=True)
        st.code(msg["code"], language=msg["language"].lower())
        st.markdown('<div class="user-msg-text">Rate this function for me!</div><br>', unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        clean_text = msg["content"]
        card_bytes = generate_roast_card_image(
            grade=msg.get("grade", "F"), score=msg.get("score", 0),
            language=msg.get("language", "Python"), roast=clean_text
        )

        st.markdown(f"""
        <div class="ai-msg-wrapper">
            <div class="ai-avatar">🔥</div>
            <div class="ai-content-box">
                <div class="ai-roast-card">
                    <div class="ai-roast-header">
                        <span class="ai-roast-status">CODE ROAST AI</span>
                        <div class="ai-roast-badge">🔥 VERDICT COMPLETED</div>
                    </div>
                    <div>{clean_text}</div>
                    <br>
                    <div style="color: #94a3b8; font-style: italic; font-size: 0.85rem;">— {msg.get('reaction','')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons Row
        c1, c2, c3, _ = st.columns([1.6, 1.2, 1.2, 3])
        with c1:
            st.download_button("📥 Download Card", data=card_bytes, file_name=f"coderoast_{idx}.png", mime="image/png", key=f"dl_{idx}")

# Handle Streaming Pending Roast
if "pending_roast" in st.session_state:
    data = st.session_state.pop("pending_roast")

    # Render User Message first
    st.markdown(f"""
    <div class="user-msg-container">
        <div class="user-msg-header">USER - {data.get('time', '10:15 AM')} ({data['language']})</div>
    </div>
    """, unsafe_allow_html=True)
    st.code(data["code"], language=data["language"].lower())
    st.markdown('<div class="user-msg-text">Rate this function for me!</div><br>', unsafe_allow_html=True)

    # Prepare AI Streaming Container
    st.markdown("""
    <div class="ai-msg-wrapper">
        <div class="ai-avatar">🔥</div>
        <div class="ai-content-box">
    """, unsafe_allow_html=True)
    
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
        placeholder.markdown(f"""
        <div class="ai-roast-card">
            <div class="ai-roast-header">
                <span class="ai-roast-status">CODE ROAST AI - streaming...</span>
                <div class="ai-roast-badge">🔥 ROASTING...</div>
            </div>
            <div>{cleaned}</div>
        </div>
        """, unsafe_allow_html=True)

    final_clean = clean_roast(accumulated)
    placeholder.markdown(f"""
    <div class="ai-roast-card">
        <div class="ai-roast-header">
            <span class="ai-roast-status">CODE ROAST AI</span>
            <div class="ai-roast-badge">🔥 ROASTING COMPLETE</div>
        </div>
        <div>{final_clean}</div>
        <br>
        <div style="color: #94a3b8; font-style: italic; font-size: 0.85rem;">— {data['grade_reaction']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Save to session history
    st.session_state.chat_history.append({
        "role": "assistant", "content": final_clean,
        "grade": data["scores"]["grade"], "score": data["scores"]["overall"],
        "reaction": data["grade_reaction"], "language": data["language"]
    })

    save_to_leaderboard(
        code_snippet=data["code"], language=data["language"],
        score=data["scores"]["overall"], grade=data["scores"]["grade"],
        roast_text=final_clean
    )

# ─── Bottom Chat Input Bar (Matching Mockup Footer) ──────────────────────────

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="background: #151724; border: 1px solid #272a3d; border-radius: 12px; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between;">
    <div style="color: #64748b; font-size: 0.9rem;">
        Paste code in sidebar & click <strong>🔥 Roast Code</strong> | Type '/' for commands
    </div>
    <div style="display: flex; gap: 8px;">
        <button style="background: #1f2233; border: 1px solid #31354c; color: #94a3b8; padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; cursor: pointer;">📎 Attach</button>
        <button style="background: #f97316; border: none; color: white; padding: 6px 16px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; cursor: pointer;">Send</button>
    </div>
</div>
""", unsafe_allow_html=True)
