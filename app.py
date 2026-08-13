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

# Ensure src is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.analyzer.code_analyzer import CodeAnalyzer
from src.scoring.scorer import calculate_scores, get_grade
from src.roast.generator import RoastGenerator
from src.roast.templates import GRADE_REACTIONS

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
        background: linear-gradient(135deg, #2d1b1b 0%, #1a1a2e 100%);
        border-left: 4px solid #ff4b4b;
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
        scorer = CodeBERTScorer(model_dir=SAVED_MODEL_DIR)
        if scorer._is_loaded:
            return scorer
    except Exception:
        return None
    return None

# ─── Layout ──────────────────────────────────────────────────────────────────

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📝 Paste Your Code")

    code_input = st.text_area(
        "Paste your code here. We will not judge you. "
        "(We will absolutely judge you.)",
        height=400,
        placeholder="def my_function(x):\n    # TODO: write code\n    pass",
        label_visibility="collapsed",
    )

    row1, row2, row3 = st.columns([2, 2, 3])

    with row1:
        language = st.selectbox(
            "Language",
            ["Python", "Java", "JavaScript"],
            label_visibility="collapsed",
        )

    with row2:
        severity = st.slider(
            "Roast Severity",
            min_value=1,
            max_value=3,
            value=2,
            help="1 = Gentle Nudge, 2 = Standard Roast, 3 = No Mercy",
        )

    use_ai_llm = st.checkbox(
        "🤖 Enable Dynamic AI Roast (Qwen2.5-Coder LLM)",
        value=False,
        help="Generates brand-new, unique AI code roasts using a local LLM instead of templates."
    )

    with row3:
        roast_button = st.button(
            "🔥 Roast My Code",
            type="primary",
            use_container_width=True,
        )

with col2:
    if roast_button and code_input:
        with st.spinner("Analyzing your code... (taking deep breaths)"):
            # ── Run analysis pipeline ────────────────────────────────────
            lang_key = language.lower()
            analyzer = CodeAnalyzer(code_input, language=lang_key)
            metrics = analyzer.get_metrics()
            scores = calculate_scores(metrics)

            # ── Determine quality level & severity score ──────────────────
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
                # Fallback: estimate quality from overall score
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

            # ── Generate roast ───────────────────────────────────────────
            if use_ai_llm and roast_generator.llm_generator is None:
                with st.spinner("🤖 Loading AI Roast LLM model (Qwen2.5-Coder-1.5B)..."):
                    from src.roast.llm_generator import LLMRoastGenerator
                    roast_generator.llm_generator = LLMRoastGenerator()

            roast_text = roast_generator.generate_roast(
                metrics=metrics,
                quality_level=quality_level,
                severity=severity,
                code=code_input,
                use_llm=use_ai_llm
            )
            grade_reaction = roast_generator.get_grade_reaction(scores["grade"])

        # ── Display Results ──────────────────────────────────────────────

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
        st.plotly_chart(fig, use_container_width=True)

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

        st.markdown("<br>", unsafe_allow_html=True)

        # The Roast
        st.markdown(f"""
        <div class="roast-box">
            🔥 <strong>CodeRoast Says:</strong><br><br>
            {roast_text}
            <br><br>
            <em style="color: #888;">— {grade_reaction}</em>
        </div>
        """, unsafe_allow_html=True)

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

    elif roast_button and not code_input:
        st.warning("Paste some code first. I need something to roast. 🔥")

    else:
        # Empty state
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

# ─── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #444; font-size: 0.8rem;">'
    'Built by gyr0byte — Not a person, a process. Always building, never stopping. 🔥'
    '</p>',
    unsafe_allow_html=True,
)
