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
from src.roast.templates import GRADE_REACTIONS, NEPALI_ROAST_TEMPLATES

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CodeRoast 🔥",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Dark theme overrides */
    .stApp {
        background-color: #0e1117;
    }

    /* Fire gradient header */
    .fire-header {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8c00 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 30px;
    }

    /* Grade display */
    .grade-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .grade-letter {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ff4b4b, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .grade-label {
        color: #aaa;
        font-size: 1rem;
    }

    /* Roast box */
    .roast-box {
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #e0e0e0;
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

    /* Metric card */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin: 15px 0;
    }

    .metric-item {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ff8c00;
    }

    .metric-name {
        font-size: 0.75rem;
        color: #888;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown('<h1 class="fire-header">🔥 CodeRoast</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Brutally honest code reviews. You asked for this.</p>',
    unsafe_allow_html=True,
)

# ─── Initialize ──────────────────────────────────────────────────────────────

roast_generator = RoastGenerator()

# ─── Hall of Shame / Leaderboard Helpers ─────────────────────────────────────

LEADERBOARD_FILE = Path(__file__).parent / "data" / "leaderboard.json"

def load_leaderboard():
    """Load top worst and best submissions from local JSON storage."""
    if not LEADERBOARD_FILE.exists():
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_to_leaderboard(code_snippet: str, language: str, score: float, grade: str, roast_text: str):
    """Save a roast result to the persistent Hall of Shame leaderboard."""
    LEADERBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    board = load_leaderboard()
    
    # Avoid duplicate exact code entries
    code_sub = code_snippet[:150].strip()
    for item in board:
        if item.get("snippet", "") == code_sub:
            return
            
    board.append({
        "timestamp": os.getenv("CURRENT_TIME", "2026-09-01"),
        "language": language,
        "score": score,
        "grade": grade,
        "snippet": code_sub,
        "roast": roast_text[:180] + ("..." if len(roast_text) > 180 else "")
    })
    
    # Keep top 10 worst code scores
    board.sort(key=lambda x: x["score"])
    board = board[:10]
    
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(board, f, indent=2)
    except Exception:
        pass

def generate_roast_card_image(grade: str, score: float, language: str, roast: str) -> bytes:
    """Generate a shareable PIL image card with fire theme, grade, score, and roast text."""
    width, height = 800, 450
    img = Image.new("RGB", (width, height), color=(14, 17, 23))
    draw = ImageDraw.Draw(img)
    
    # Header gradient border top
    for x in range(width):
        r = int(255 - (x / width) * 100)
        g = int(75 + (x / width) * 100)
        draw.line([(x, 0), (x, 8)], fill=(r, g, 0))

    # Load font
    font_large = ImageFont.load_default()
    
    # Outer Card Box
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(255, 75, 75), width=2)
    
    # Title
    draw.text((40, 40), "CodeRoast - Official Verdict", fill=(255, 140, 0), font=font_large)
    
    # Grade & Score (Sanitize non-ascii like em dashes)
    grade_clean = grade.encode("ascii", "ignore").decode("ascii").strip()
    grade_str = grade_clean.split(" ")[0] if grade_clean else "F"
    
    draw.text((40, 90), f"Grade: {grade_str}", fill=(255, 75, 75), font=font_large)
    draw.text((200, 90), f"Overall Score: {score}/100", fill=(255, 215, 0), font=font_large)
    draw.text((450, 90), f"Language: {language}", fill=(170, 170, 170), font=font_large)
    
    draw.line([(40, 130), (width - 40, 130)], fill=(51, 51, 51), width=1)
    
    # Roast Text Wrapping
    clean_r = (
        roast.replace("🤖 [Gemini Flash AI Roast]: ", "")
        .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
        .replace("🤖 ", "")
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    words = clean_r.split()
    lines = []
    curr_line = ""
    for w in words:
        if len(curr_line + " " + w) > 75:
            lines.append(curr_line)
            curr_line = w
        else:
            curr_line += " " + w if curr_line else w
    if curr_line:
        lines.append(curr_line)
        
    # Draw up to 8 lines
    y = 150
    for line in lines[:8]:
        draw.text((40, y), line, fill=(220, 220, 220), font=font_large)
        y += 24
        
    # Footer
    draw.text((40, height - 45), "Share your pain on GitHub/Twitter | coderoast.dev", fill=(136, 136, 136), font=font_large)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


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
        # Only load CodeBERT if custom fine-tuned weights exist to avoid cloud RAM OOM
        if SAVED_MODEL_DIR.exists():
            scorer = CodeBERTScorer(model_dir=SAVED_MODEL_DIR)
            if scorer._is_loaded:
                return scorer
    except Exception:
        return None
    return None

# ─── Layout ──────────────────────────────────────────────────────────────────

# Create side-by-side columns for input and roast
col1, col2 = st.columns([1, 1], gap="large")

# Variables to store results
metrics = None
scores = None
roast_text = ""
grade_reaction = ""
model_used_label = ""
quality_level = 1
has_results = False

with col1:
    st.markdown("### 📝 Paste Your Code")

    code_input = st.text_area(
        "Paste your code here. We will not judge you. "
        "(We will absolutely judge you.)",
        height=400,
        placeholder="def my_function(x):\n    # TODO: write code\n    pass",
        label_visibility="collapsed",
    )

    row1_col1, row1_col2, row1_col3 = st.columns([1.5, 2.2, 2.3])

    with row1_col1:
        language = st.selectbox(
            "Code Language",
            ["Python", "Java", "JavaScript"],
            label_visibility="visible",
        )

    with row1_col2:
        roast_language = st.selectbox(
            "Roast Output Language",
            ["🇬🇧 English", "🇳🇵 Roman Nepali (रोमन नेपाली)"],
            index=0,
            label_visibility="visible",
        )
        target_lang = "roman_nepali" if "Nepali" in roast_language else "english"

    with row1_col3:
        severity = st.slider(
            "Roast Severity",
            min_value=1,
            max_value=3,
            value=2,
            help="1 = Gentle Nudge, 2 = Standard Roast, 3 = No Mercy",
        )

    row2_col1, row2_col2 = st.columns([2.5, 2])

    with row2_col1:
        use_ai_llm = st.checkbox(
            "🤖 Enable Dynamic AI Roast (Qwen2.5 for English / Gemini Flash for Nepali)",
            value=True,
            help="Generates AI roasts using Qwen2.5 for English and Gemini Flash for Nepali."
        )

    with row2_col2:
        roast_button = st.button(
            "🔥 Roast My Code",
            type="primary",
            width="stretch",
        )

# Execute analysis if the roast button is clicked
if roast_button:
    if not code_input:
        st.warning("Paste some code first. I need something to roast. 🔥")
    else:
        # 1. AST Static Analysis & Machine Learning Quality Scoring
        with st.spinner("📊 Analyzing AST Code Metrics & Quality..."):
            lang_key = language.lower()
            analyzer = CodeAnalyzer(code_input, language=lang_key)
            metrics = analyzer.get_metrics()
            scores = calculate_scores(metrics)

            if metrics.get("_is_plain_text", False):
                st.warning("⚠️ Non-Code Text Detected: This snippet looks like plain text prose rather than source code.")
            elif metrics.get("_language_mismatch", False):
                detected = metrics.get("_detected_lang", "Python").capitalize()
                selected = metrics.get("_selected_lang", "Java").capitalize()
                st.warning(f"⚠️ Language Mismatch Detected: You selected {selected} in the dropdown, but pasted {detected} code!")

            codebert_scorer = get_codebert_scorer()
            classifier = get_classifier()

            if codebert_scorer is not None:
                quality_level, cb_severity = codebert_scorer.predict_quality_and_severity(code_input)
                model_used_label = "🤗 Hugging Face CodeBERT (microsoft/codebert-base)"
            elif classifier is not None:
                quality_level, confidence = classifier.predict_quality(
                    code_input, metrics
                )
                model_used_label = "🌲 Random Forest Quality Classifier"
            else:
                overall = scores["overall"]
                if overall >= 75:
                    quality_level = 0
                elif overall >= 55:
                    quality_level = 1
                elif overall >= 35:
                    quality_level = 2
                else:
                    quality_level = 3
                model_used_label = "📊 Rule-Based Static Analysis (Fallback)"

        if roast_generator.llm_generator is None and use_ai_llm:
            from src.roast.llm_generator import LLMRoastGenerator
            roast_generator.llm_generator = LLMRoastGenerator()

        grade_reaction = roast_generator.get_grade_reaction(
            scores["grade"],
            use_llm=use_ai_llm,
            code=code_input,
            metrics=metrics
        )
        has_results = True

        # Store in session state for persistence across potential UI refreshes
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

# Retrieve from session state if present
if "has_results" in st.session_state and st.session_state["has_results"]:
    metrics = st.session_state["metrics"]
    scores = st.session_state["scores"]
    grade_reaction = st.session_state["grade_reaction"]
    model_used_label = st.session_state["model_used_label"]
    has_results = True

# Render Column 2 (The Roast)
with col2:
    if has_results:
        target_lang = st.session_state.get("target_lang", "english")
        use_ai_llm = st.session_state.get("use_ai_llm", True)

        # Determine background color style
        if use_ai_llm:
            # AI LLM roast: Distinct purple gradient
            roast_style = "background: linear-gradient(135deg, #4c1d95 0%, #1e1b4b 100%); border-left: 5px solid #a78bfa; box-shadow: 0 4px 20px rgba(167, 139, 250, 0.15);"
        else:
            # Template roast: Distinct yellow/amber gradient
            roast_style = "background: linear-gradient(135deg, #78350f 0%, #1c1917 100%); border-left: 5px solid #fbbf24; box-shadow: 0 4px 20px rgba(251, 191, 36, 0.15);"

        roast_box_placeholder = st.empty()

        # ── Streaming or Cached Roast Handling ─────────────────────────────
        if st.session_state.get("is_new_roast", False):
            st.session_state["is_new_roast"] = False

            if roast_generator.llm_generator is None and use_ai_llm:
                from src.roast.llm_generator import LLMRoastGenerator
                roast_generator.llm_generator = LLMRoastGenerator()

            roast_stream = roast_generator.generate_roast_stream(
                metrics=metrics,
                quality_level=st.session_state.get("quality_level", 2),
                severity=st.session_state.get("severity", 2),
                code=st.session_state.get("code_input", ""),
                use_llm=use_ai_llm,
                language=target_lang
            )

            accumulated_text = ""
            for chunk in roast_stream:
                accumulated_text += chunk
                clean_accumulated = (
                    accumulated_text
                    .replace("🤖 [Gemini Flash AI Roast]: ", "")
                    .replace("🤖 [Qwen2.5-Coder AI Roast]: ", "")
                    .replace("🤖 AI Roast: ", "")
                    .replace("🤖 ", "")
                )

                roast_box_placeholder.markdown(f"""
                <div class="roast-box" style="{roast_style}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <span>🔥 <strong>Final Verdict:</strong></span>
                    </div>
                    {clean_accumulated}
                    <br><br>
                    <em style="color: #888;">— {grade_reaction}</em>
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
            <div class="roast-box" style="{roast_style}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <span>🔥 <strong>Final Verdict:</strong></span>
                </div>
                {clean_roast_text}
                <br><br>
                <em style="color: #888;">— {grade_reaction}</em>
            </div>
            """, unsafe_allow_html=True)

        # Save to leaderboard (Hall of Shame)
        save_to_leaderboard(
            code_snippet=st.session_state.get("code_input", ""),
            language=language,
            score=scores["overall"],
            grade=scores["grade"],
            roast_text=clean_roast_text
        )



        # Downloadable Shareable Roast Card Button
        card_img_bytes = generate_roast_card_image(
            grade=scores["grade"],
            score=scores["overall"],
            language=language,
            roast=clean_roast_text
        )
        
        st.download_button(
            label="🖼️ Download Shareable Roast Card (PNG)",
            data=card_img_bytes,
            file_name=f"coderoast_{scores['grade'].split()[0]}_grade.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.markdown("""
        <div style="text-align: center; padding: 80px 20px; color: #555;">
            <div style="font-size: 4rem;">🔥</div>
            <p style="font-size: 1.2rem; margin-top: 10px;">
                Paste your code and hit <strong>Roast My Code</strong>
            </p>
            <p style="font-size: 0.9rem; color: #444;">
                Supports Python, Java, and JavaScript
            </p>
        </div>
        """, unsafe_allow_html=True)


# Render Scoring System below the pasting code and roasting fields
if has_results:
    st.markdown("---")
    st.markdown("### 📊 Code Quality Scorecard")
    
    score_col1, score_col2 = st.columns([1, 1], gap="large")

    with score_col1:
        # Grade Card
        grade_letter = scores["grade"].split(" ")[0]
        grade_desc = " ".join(scores["grade"].split(" ")[1:])

        st.markdown(f"""
        <div class="grade-card">
            <div class="grade-letter">{grade_letter}</div>
            <div class="grade-label">{grade_desc}</div>
            <div style="color: #666; font-size: 0.85rem; margin-top: 8px;">
                Overall Score: {scores['overall']}/100
            </div>
            <div style="color: #4ade80; font-size: 0.8rem; margin-top: 6px; font-weight: 500;">
                {model_used_label}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Score Bars
        def score_bar(label: str, value: float):
            color = (
                "#4ade80" if value >= 75 else
                "#facc15" if value >= 50 else
                "#fb923c" if value >= 30 else
                "#ef4444"
            )
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

    with score_col2:
        # Radar Chart
        fig = go.Figure(data=go.Scatterpolar(
            r=[
                scores["readability"],
                scores["efficiency"],
                scores["structure"],
                scores["creativity"],
                scores["readability"],  # Close the polygon
            ],
            theta=[
                "Readability", "Efficiency",
                "Structure", "Creativity",
                "Readability",
            ],
            fill="toself",
            fillcolor="rgba(255, 75, 75, 0.15)",
            line=dict(color="#FF4B4B", width=2),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    range=[0, 100],
                    showticklabels=True,
                    tickfont=dict(size=10, color="#666"),
                    gridcolor="#333",
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color="#aaa"),
                    gridcolor="#333",
                ),
                bgcolor="rgba(0,0,0,0)",
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=60, r=60, t=30, b=30),
            height=300,
        )
        st.plotly_chart(fig, width="stretch")

    # Raw Metrics (expandable)
    with st.expander("📊 Raw Metrics"):
        metric_cols = st.columns(4)
        metric_items = [
            ("Lines of Code", metrics["lines_of_code"]),
            ("Functions", metrics["function_count"]),
            ("Avg Func Length", f"{metrics['avg_function_length']}"),
            ("Complexity", f"{metrics['cyclomatic_complexity']}"),
            ("Naming Score", f"{metrics['naming_score']}"),
            ("Comment Ratio", f"{metrics['comment_ratio']:.1%}"),
            ("Nesting Depth", metrics["nesting_depth"]),
            ("Duplication", f"{metrics['duplicate_code_score']}"),
        ]
        for i, (name, val) in enumerate(metric_items):
            with metric_cols[i % 4]:
                st.metric(label=name, value=val)

# ─── Leaderboard / Hall of Shame Section ─────────────────────────────────────

st.markdown("---")
with st.expander("🏆 Hall of Shame — Top Worst Code Submissions", expanded=False):
    leaderboard_data = load_leaderboard()
    if not leaderboard_data:
        st.info("No entries in the Hall of Shame yet. Submit some atrocious code to claim your spot! 🔥")
    else:
        st.caption("Showing top worst code snippets submitted to CodeRoast (ranked by lowest quality score):")
        for rank, entry in enumerate(leaderboard_data, 1):
            st.markdown(f"""
            <div style="background: #111827; border-left: 4px solid #ef4444; padding: 12px 16px; margin: 8px 0; border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; font-weight: 600;">
                    <span style="color: #f87171;">#{rank} — {entry.get('grade', 'F')} ({entry.get('score', 0)}/100)</span>
                    <span style="color: #9ca3af; font-size: 0.85rem;">{entry.get('language', 'Python')}</span>
                </div>
                <div style="color: #d1d5db; font-size: 0.9rem; margin-top: 6px; font-style: italic;">
                    "{entry.get('roast', '')}"
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #444; font-size: 0.8rem;">'
    'Built by gyr0byte — Not a person, a process. Always building, never stopping. 🔥'
    '</p>',
    unsafe_allow_html=True,
)
