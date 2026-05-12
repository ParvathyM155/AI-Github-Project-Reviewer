import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from analyzer import analyze_project
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Project Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0d0f12;
    color: #e8eaed;
}

.main { background-color: #0d0f12; }

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #7b61ff, #ff6b9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}

.hero-sub {
    font-size: 1.05rem;
    color: #8b95a1;
    margin-bottom: 2rem;
    font-family: 'JetBrains Mono', monospace;
}

.score-card {
    background: #151820;
    border: 1px solid #1e2430;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}

.score-card:hover { border-color: #00d4ff44; }

.score-number {
    font-size: 2.8rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}

.score-label {
    font-size: 0.78rem;
    color: #8b95a1;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.4rem;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}

.badge-green  { background: #0d2b1a; color: #2dd698; border: 1px solid #2dd69833; }
.badge-yellow { background: #2b2200; color: #f5c518; border: 1px solid #f5c51833; }
.badge-red    { background: #2b0f0f; color: #ff5a5a; border: 1px solid #ff5a5a33; }
.badge-blue   { background: #0b1e33; color: #00d4ff; border: 1px solid #00d4ff33; }
.badge-purple { background: #1a1033; color: #7b61ff; border: 1px solid #7b61ff33; }

.section-card {
    background: #151820;
    border: 1px solid #1e2430;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

.section-title {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #8b95a1;
    margin-bottom: 1rem;
}

.check-item { margin: 0.4rem 0; font-size: 0.92rem; }
.check-pass { color: #2dd698; }
.check-fail { color: #ff5a5a; }
.check-warn { color: #f5c518; }

.tech-pill {
    display: inline-block;
    background: #1a1e2e;
    border: 1px solid #2a3050;
    border-radius: 8px;
    padding: 0.3rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #7b61ff;
    margin: 0.2rem;
}

.recruiter-quote {
    background: #0e1520;
    border-left: 3px solid #00d4ff;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.25rem;
    font-style: italic;
    color: #c8d0da;
    font-size: 0.95rem;
    line-height: 1.65;
}

.suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e2430;
    font-size: 0.9rem;
    color: #c8d0da;
}

.suggestion-item:last-child { border-bottom: none; }

.arrow { color: #00d4ff; font-family: 'JetBrains Mono', monospace; }

stTextArea textarea {
    background: #151820 !important;
    border: 1px solid #1e2430 !important;
    color: #e8eaed !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    border-radius: 10px !important;
}

div[data-testid="stTextArea"] textarea {
    background-color: #151820;
    color: #e8eaed;
    border: 1px solid #1e2430;
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
}

div.stButton > button {
    background: linear-gradient(135deg, #00d4ff22, #7b61ff22);
    border: 1px solid #7b61ff66;
    color: #e8eaed;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    width: 100%;
    transition: all 0.2s;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff44, #7b61ff44);
    border-color: #7b61ff;
    transform: translateY(-1px);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif;
    color: #8b95a1;
}

.stTabs [aria-selected="true"] { color: #00d4ff !important; }

hr { border-color: #1e2430; }
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">GitHub Project Reviewer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// AI-powered recruiter-grade analysis for your projects</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        readme_input = st.text_area(
            "Paste your README or project description",
            height=220,
            placeholder="""# My Project

A web app built with Python and Streamlit that...

## Features
- Feature 1
- Feature 2

## Tech Stack
- Python, Streamlit, scikit-learn

## Installation
..."""
        )
    with col2:
        st.markdown("#### What you'll get")
        st.markdown("""
- 📊 **Professionalism score**
- 🎯 **Recruiter appeal rating**
- 🔍 **Tutorial-project detector**
- 💡 **Portfolio upgrade tips**
- 🏷️ **Tech stack extraction**
- 🚀 **ATS keyword strength**
- ⚡ **Hackathon readiness**
- 📝 **README beautifier tips**
        """)
        analyze_btn = st.button("🔍 Analyze Project", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze_btn:
    if not readme_input.strip():
        st.warning("Please paste your README or project description first.")
    else:
        with st.spinner("Analyzing your project..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.015)
                progress.progress(i + 1)
            result = analyze_project(readme_input)
            progress.empty()

        # ── Score cards row ───────────────────────────────────────────────────
        def score_color(s):
            if s >= 7: return "#2dd698"
            if s >= 4: return "#f5c518"
            return "#ff5a5a"

        c1, c2, c3, c4, c5 = st.columns(5)
        scores = [
            (result["professionalism_score"], "Professionalism"),
            (result["hiring_appeal_score"],   "Hiring Appeal"),
            (result["uniqueness_score"],       "Uniqueness"),
            (result["ats_score"],              "ATS Strength"),
            (result["hackathon_score"],        "Hackathon Ready"),
        ]
        for col, (score, label) in zip([c1,c2,c3,c4,c5], scores):
            col.markdown(f"""
            <div class="score-card">
                <div class="score-number" style="color:{score_color(score)}">{score}<span style="font-size:1.2rem;color:#8b95a1">/10</span></div>
                <div class="score-label">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Recruiter Mode",
            "📊 Radar Chart",
            "🛠 Tech Stack",
            "💡 Improvements",
            "📝 README Tips"
        ])

        # TAB 1 — Recruiter Mode
        with tab1:
            col_a, col_b = st.columns([1, 1])

            with col_a:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Project Classification</div>', unsafe_allow_html=True)

                level = result["level"]
                level_colors = {"Beginner": "badge-yellow", "Intermediate": "badge-blue", "Advanced": "badge-purple"}
                st.markdown(f'<span class="badge {level_colors.get(level, "badge-blue")}">{level}</span>', unsafe_allow_html=True)

                resume_worth = result["resume_worth"]
                rw_colors = {"High": "badge-green", "Medium": "badge-yellow", "Low": "badge-red"}
                st.markdown(f'&nbsp;&nbsp;<span class="badge {rw_colors.get(resume_worth, "badge-yellow")}">Resume Worth: {resume_worth}</span>', unsafe_allow_html=True)

                tutorial_flag = result["tutorial_flag"]
                tf_badge = "badge-red" if tutorial_flag else "badge-green"
                tf_label = "⚠ Looks Tutorial-Based" if tutorial_flag else "✓ Looks Original"
                st.markdown(f'&nbsp;&nbsp;<span class="badge {tf_badge}">{tf_label}</span>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-title">Section Checklist</div>', unsafe_allow_html=True)
                sections = result["sections_check"]
                for section, present in sections.items():
                    icon = "✓" if present else "✗"
                    cls  = "check-pass" if present else "check-fail"
                    st.markdown(f'<div class="check-item {cls}">{icon} {section}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Recruiter Feedback</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="recruiter-quote">"{result["recruiter_feedback"]}"</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-title">Why it looks tutorial-based</div>' if tutorial_flag else '<div class="section-title">What makes it stand out</div>', unsafe_allow_html=True)
                for reason in result["tutorial_reasons"]:
                    st.markdown(f'<div class="check-item check-fail">✗ {reason}</div>' if tutorial_flag else f'<div class="check-item check-pass">✓ {reason}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

        # TAB 2 — Radar Chart
        with tab2:
            categories = ["Professionalism", "Hiring Appeal", "Uniqueness", "ATS Strength", "Hackathon Ready", "Documentation"]
            values = [
                result["professionalism_score"],
                result["hiring_appeal_score"],
                result["uniqueness_score"],
                result["ats_score"],
                result["hackathon_score"],
                result["documentation_score"],
            ]

            fig = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(123, 97, 255, 0.15)',
                line=dict(color='#7b61ff', width=2),
                marker=dict(color='#00d4ff', size=7)
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor='#151820',
                    radialaxis=dict(visible=True, range=[0,10], gridcolor='#1e2430', color='#8b95a1', tickfont=dict(size=10)),
                    angularaxis=dict(gridcolor='#1e2430', color='#c8d0da', tickfont=dict(family='Syne', size=12))
                ),
                paper_bgcolor='#0d0f12',
                plot_bgcolor='#0d0f12',
                font=dict(family='Syne', color='#e8eaed'),
                margin=dict(t=20, b=20, l=40, r=40),
                height=420
            )
            st.plotly_chart(fig, use_container_width=True)

            # Score bars
            bar_fig = go.Figure(go.Bar(
                x=values,
                y=categories,
                orientation='h',
                marker=dict(
                    color=values,
                    colorscale=[[0,'#ff5a5a'],[0.5,'#f5c518'],[1,'#2dd698']],
                    cmin=0, cmax=10
                ),
                text=[f"{v}/10" for v in values],
                textposition='outside',
                textfont=dict(family='JetBrains Mono', size=11, color='#e8eaed')
            ))
            bar_fig.update_layout(
                paper_bgcolor='#0d0f12',
                plot_bgcolor='#151820',
                xaxis=dict(range=[0,11], gridcolor='#1e2430', color='#8b95a1'),
                yaxis=dict(gridcolor='#1e2430', color='#c8d0da'),
                font=dict(family='Syne', color='#e8eaed'),
                height=280,
                margin=dict(t=10, b=20, l=140, r=60)
            )
            st.plotly_chart(bar_fig, use_container_width=True)

        # TAB 3 — Tech Stack
        with tab3:
            detected = result["tech_stack"]
            ats_keywords = result["ats_keywords"]

            col_x, col_y = st.columns(2)
            with col_x:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Detected Tech Stack</div>', unsafe_allow_html=True)
                if detected:
                    for tech in detected:
                        st.markdown(f'<span class="tech-pill">{tech}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color:#8b95a1;font-size:0.9rem">No specific technologies detected</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_y:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">ATS Keywords Found</div>', unsafe_allow_html=True)
                if ats_keywords:
                    for kw in ats_keywords:
                        st.markdown(f'<span class="badge badge-blue" style="margin:0.2rem">{kw}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color:#8b95a1;font-size:0.9rem">No strong ATS keywords found</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # TAB 4 — Improvements
        with tab4:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Portfolio Upgrade Suggestions</div>', unsafe_allow_html=True)
            for s in result["suggestions"]:
                st.markdown(f'<div class="suggestion-item"><span class="arrow">→</span><span>{s}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 5 — README Tips
        with tab5:
            col_p, col_q = st.columns(2)
            with col_p:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">README Improvements</div>', unsafe_allow_html=True)
                for tip in result["readme_tips"]:
                    st.markdown(f'<div class="suggestion-item"><span class="arrow">→</span><span>{tip}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_q:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Suggested Badges to Add</div>', unsafe_allow_html=True)
                for badge in result["badge_suggestions"]:
                    st.markdown(f'<div class="check-item check-warn">⬡ {badge}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-title">Title Suggestion</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="recruiter-quote">{result["title_suggestion"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#3a4050;font-size:0.8rem;font-family:JetBrains Mono,monospace">'
    'GitHub Project Reviewer · Built with Streamlit & Python NLP · BCA Minor Project</p>',
    unsafe_allow_html=True
)
