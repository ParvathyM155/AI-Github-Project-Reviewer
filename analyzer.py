"""
analyzer.py — Core NLP analysis engine for GitHub Project Reviewer
Uses rule-based scoring, keyword analysis, and sentiment analysis.
No heavy ML model needed — this still looks very AI/ML powered.
"""

import re
from textblob import TextBlob

# ── Tech Stack Keywords ───────────────────────────────────────────────────────
TECH_KEYWORDS = {
    # Languages
    "Python": ["python", "py", ".py"],
    "JavaScript": ["javascript", "js", "node", "nodejs", "node.js"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "spring", "maven", "gradle"],
    "C++": ["c++", "cpp"],
    "Go": ["golang", "go lang"],
    "Rust": ["rust", "cargo"],
    "R": [" r ", "rstudio", "r language"],

    # Web Frameworks
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi", "fast api"],
    "React": ["react", "reactjs", "react.js"],
    "Vue": ["vue", "vuejs", "vue.js"],
    "Next.js": ["next.js", "nextjs"],
    "Streamlit": ["streamlit"],
    "Express": ["express", "expressjs"],

    # ML / AI
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch", "torch"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "Keras": ["keras"],
    "Hugging Face": ["hugging face", "huggingface", "transformers"],
    "OpenCV": ["opencv", "cv2"],
    "NLTK": ["nltk"],
    "SpaCy": ["spacy"],
    "XGBoost": ["xgboost"],
    "LangChain": ["langchain"],

    # Databases
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo"],
    "SQLite": ["sqlite"],
    "Redis": ["redis"],
    "Firebase": ["firebase"],

    # Cloud / DevOps
    "Docker": ["docker", "dockerfile", "containeriz"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "s3", "ec2", "lambda"],
    "GCP": ["gcp", "google cloud", "bigquery"],
    "Azure": ["azure", "microsoft azure"],
    "GitHub Actions": ["github actions", "ci/cd", "cicd"],
    "Heroku": ["heroku"],

    # Data
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Matplotlib": ["matplotlib"],
    "Plotly": ["plotly"],
    "Seaborn": ["seaborn"],
    "Tableau": ["tableau"],
    "Power BI": ["power bi", "powerbi"],
}

# ── ATS Keywords ──────────────────────────────────────────────────────────────
ATS_KEYWORDS = [
    "machine learning", "deep learning", "neural network", "nlp",
    "natural language processing", "computer vision", "data science",
    "api", "rest api", "restful", "microservices", "deployment",
    "docker", "kubernetes", "cloud", "aws", "gcp", "azure",
    "authentication", "oauth", "jwt", "sql", "nosql",
    "real-time", "websocket", "async", "scalable", "production",
    "ci/cd", "testing", "unit test", "end-to-end", "agile",
    "data visualization", "dashboard", "automation", "optimization",
    "recommendation", "classification", "regression", "clustering",
    "transformer", "bert", "gpt", "llm", "rag",
]

# ── Tutorial Project Signals ──────────────────────────────────────────────────
TUTORIAL_PHRASES = [
    "following this tutorial", "built by following", "inspired by",
    "for learning purposes", "practice project", "just learning",
    "beginner project", "my first project", "i am new to",
    "this is a simple", "basic crud", "todo app", "to-do app",
    "weather app", "calculator app", "simple calculator",
    "netflix clone", "amazon clone", "twitter clone", "instagram clone",
    "ecommerce website", "e-commerce website", "portfolio website template",
]

TUTORIAL_FOLDER_NAMES = [
    "day1", "day2", "day3", "challenge", "bootcamp",
    "100daysofcode", "30days", "course project",
]

# ── Section Checkers ──────────────────────────────────────────────────────────
SECTION_PATTERNS = {
    "Project Description":   r"(description|overview|about|what is)",
    "Installation Guide":    r"(install|setup|getting started|how to run|requirements)",
    "Usage / Demo":          r"(usage|demo|example|how to use|screenshot|gif)",
    "Tech Stack Listed":     r"(tech stack|built with|technologies|tools used|dependencies)",
    "Features Listed":       r"(features|functionality|capabilities|what it does)",
    "Live Deployment Link":  r"(live|deploy|hosted|heroku|vercel|netlify|render|demo link|https://)",
    "Contribution Guide":    r"(contribut|pull request|fork|open source)",
    "License":               r"(license|mit|apache|gpl)",
    "Badges":                r"!\[.*?\]\(https://(img\.shields\.io|badge\.fury|travis)",
}

# ── Badge Suggestions ─────────────────────────────────────────────────────────
ALL_BADGES = [
    "![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)",
    "![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)",
    "![MIT License](https://img.shields.io/badge/License-MIT-green.svg)",
    "![GitHub Stars](https://img.shields.io/github/stars/yourusername/yourrepo)",
    "![Issues](https://img.shields.io/github/issues/yourusername/yourrepo)",
    "![Last Commit](https://img.shields.io/github/last-commit/yourusername/yourrepo)",
]


# ── Main Analysis Function ────────────────────────────────────────────────────
def analyze_project(text: str) -> dict:
    text_lower = text.lower()
    blob = TextBlob(text)

    # 1. Tech stack detection
    tech_stack = []
    for tech, keywords in TECH_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tech_stack.append(tech)

    # 2. ATS keywords
    ats_found = [kw for kw in ATS_KEYWORDS if kw in text_lower]

    # 3. Section checks
    sections_check = {
        section: bool(re.search(pattern, text_lower))
        for section, pattern in SECTION_PATTERNS.items()
    }

    # 4. Tutorial detection
    tutorial_hits = [p for p in TUTORIAL_PHRASES if p in text_lower]
    folder_hits   = [f for f in TUTORIAL_FOLDER_NAMES if f in text_lower]
    tutorial_flag = len(tutorial_hits) >= 1 or len(folder_hits) >= 1

    tutorial_reasons = []
    if tutorial_hits:
        tutorial_reasons += [f'Contains phrase: "{p}"' for p in tutorial_hits[:3]]
    if not sections_check.get("Live Deployment Link"):
        tutorial_reasons.append("No deployment/live link found")
    if not sections_check.get("Usage / Demo"):
        tutorial_reasons.append("No screenshots or demo provided")
    if not sections_check.get("Badges"):
        tutorial_reasons.append("No README badges — looks informal")
    if len(tech_stack) <= 2:
        tutorial_reasons.append("Very basic tech stack detected")
    if not tutorial_reasons:
        tutorial_reasons = ["Project appears original and well-structured"]

    # 5. Scores (weighted rule-based)

    # Professionalism (based on sections present + writing quality)
    section_score = sum(sections_check.values()) / len(sections_check)
    sentiment     = (blob.sentiment.subjectivity)
    professionalism_score = round(min(10, max(1,
        section_score * 6 +
        (1 - sentiment) * 2 +
        (1 if len(tech_stack) >= 3 else 0) +
        (1 if not tutorial_flag else 0)
    )), 1)

    # Hiring appeal
    hiring_appeal_score = round(min(10, max(1,
        (len(ats_found) / max(len(ATS_KEYWORDS), 1)) * 4 +
        (1 if sections_check.get("Live Deployment Link") else 0) * 2 +
        (len(tech_stack) / 10) * 2 +
        (1 if not tutorial_flag else 0) * 2
    )), 1)

    # Uniqueness
    uniqueness_score = round(min(10, max(1,
        (0 if tutorial_flag else 5) +
        (len(tech_stack) / 6) * 2 +
        (1 if sections_check.get("Live Deployment Link") else 0) +
        (1 if len(ats_found) >= 3 else 0) +
        (1 if len(text) > 800 else 0)
    )), 1)

    # ATS score
    ats_score = round(min(10, max(1,
        (len(ats_found) / max(len(ATS_KEYWORDS), 1)) * 10
    )), 1)

    # Hackathon score
    innovation_signals = ["real-time", "ai", "ml", "api", "automation",
                          "innovative", "novel", "unique", "first", "solve", "impact"]
    innovation_hits = sum(1 for s in innovation_signals if s in text_lower)
    hackathon_score = round(min(10, max(1,
        (innovation_hits / len(innovation_signals)) * 4 +
        (len(tech_stack) / 8) * 3 +
        (1 if sections_check.get("Live Deployment Link") else 0) * 2 +
        (1 if len(ats_found) >= 5 else 0)
    )), 1)

    # Documentation score
    doc_signals = ["installation", "usage", "example", "screenshot", "api reference",
                   "contributing", "license", "badge", "table of contents"]
    doc_hits = sum(1 for s in doc_signals if s in text_lower)
    documentation_score = round(min(10, max(1,
        (doc_hits / len(doc_signals)) * 8 +
        (1 if len(text) > 1000 else 0) +
        (1 if sections_check.get("Badges") else 0)
    )), 1)

    # 6. Level classification
    advanced_stack  = ["TensorFlow", "PyTorch", "Kubernetes", "Docker", "AWS",
                       "GCP", "Azure", "LangChain", "Hugging Face", "FastAPI"]
    intermediate_stack = ["Scikit-learn", "Flask", "Django", "React", "MongoDB",
                          "PostgreSQL", "Redis", "NLTK", "SpaCy"]
    advanced_hits     = sum(1 for t in tech_stack if t in advanced_stack)
    intermediate_hits = sum(1 for t in tech_stack if t in intermediate_stack)

    if advanced_hits >= 2 or (len(ats_found) >= 5 and sections_check.get("Live Deployment Link")):
        level = "Advanced"
    elif intermediate_hits >= 2 or len(tech_stack) >= 3:
        level = "Intermediate"
    else:
        level = "Beginner"

    # 7. Resume worth
    avg_score = (professionalism_score + hiring_appeal_score + uniqueness_score) / 3
    if avg_score >= 7:
        resume_worth = "High"
    elif avg_score >= 4.5:
        resume_worth = "Medium"
    else:
        resume_worth = "Low"

    # 8. Recruiter feedback (template-based, varies with scores)
    if professionalism_score >= 7 and hiring_appeal_score >= 7:
        recruiter_feedback = (
            "This project demonstrates strong real-world understanding. "
            "The tech stack is relevant, documentation looks professional, "
            "and it shows initiative beyond typical coursework. "
            "Would stand out in a junior developer's portfolio."
        )
    elif professionalism_score >= 5:
        recruiter_feedback = (
            "This project has a solid foundation. "
            "The technical choices are appropriate, but could benefit from "
            "a live deployment link, screenshots, and stronger documentation. "
            "With improvements it could be very resume-worthy."
        )
    else:
        recruiter_feedback = (
            "This project currently looks like coursework or a tutorial follow-along. "
            "Recruiters see hundreds like it. To stand out, add a unique feature, "
            "deploy it live, write a proper README with screenshots, "
            "and integrate a real API or dataset."
        )

    # 9. Portfolio suggestions
    suggestions = []
    if not sections_check.get("Live Deployment Link"):
        suggestions.append("Deploy your project (Streamlit Cloud / Heroku / Render / Vercel) and add the link")
    if not sections_check.get("Usage / Demo"):
        suggestions.append("Add screenshots or a short GIF demo to the README")
    if len(ats_found) < 5:
        suggestions.append("Mention ML/AI techniques, APIs, and deployment tools explicitly")
    if not sections_check.get("Badges"):
        suggestions.append("Add professional badges (language, license, stars, last commit)")
    if len(tech_stack) < 3:
        suggestions.append("Integrate one more tool (an API, database, or visualization library)")
    if not sections_check.get("Contribution Guide"):
        suggestions.append("Add a CONTRIBUTING.md — it signals open-source awareness")
    if tutorial_flag:
        suggestions.append("Remove tutorial-like phrases; describe what YOU built and why")
    if not sections_check.get("License"):
        suggestions.append("Add a LICENSE file (MIT is fine) — missing licenses look incomplete")
    suggestions.append("Add an architecture diagram showing how your components connect")
    suggestions.append("Include performance metrics or accuracy scores if it's an ML project")

    # 10. README tips
    readme_tips = [
        "Use a one-line project tagline below the title — makes it memorable",
        "Lead with a GIF or screenshot — visual first, text second",
        "Bold the key technical terms: **Python**, **Streamlit**, **NLP**",
        "Add a Table of Contents for readability",
        "Use emoji sparingly in section headings (✨ Features, 🚀 Deployment)",
        "Keep installation steps numbered and minimal — fewer steps = better",
        "Add an FAQ section for common errors you encountered",
        "Credit datasets or APIs used — shows professionalism",
    ]

    # 11. Title suggestion
    first_line = text.strip().split("\n")[0].replace("#", "").strip()
    if first_line:
        tech_str = " & ".join(tech_stack[:3]) if tech_stack else "Python"
        title_suggestion = f"{first_line} — {tech_str} | AI-Powered Analysis Dashboard"
    else:
        title_suggestion = "Add a descriptive, keyword-rich project title"

    return {
        "professionalism_score": professionalism_score,
        "hiring_appeal_score":   hiring_appeal_score,
        "uniqueness_score":      uniqueness_score,
        "ats_score":             ats_score,
        "hackathon_score":       hackathon_score,
        "documentation_score":   documentation_score,
        "level":                 level,
        "resume_worth":          resume_worth,
        "tutorial_flag":         tutorial_flag,
        "tutorial_reasons":      tutorial_reasons[:5],
        "sections_check":        sections_check,
        "tech_stack":            tech_stack,
        "ats_keywords":          ats_found,
        "recruiter_feedback":    recruiter_feedback,
        "suggestions":           suggestions[:8],
        "readme_tips":           readme_tips,
        "badge_suggestions":     ALL_BADGES,
        "title_suggestion":      title_suggestion,
    }
