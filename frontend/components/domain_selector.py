"""Domain and difficulty selection component."""

import streamlit as st

DOMAINS = {
    "ai_ml": "AI / Machine Learning",
    "web_dev": "Web Development",
    "cybersecurity": "Cybersecurity",
}

DIFFICULTIES = ["beginner", "intermediate", "advanced"]


def render_domain_selector() -> tuple[str, str, int]:
    st.subheader("Interview Setup")
    domain = st.selectbox(
        "Select Domain",
        options=list(DOMAINS.keys()),
        format_func=lambda x: DOMAINS[x],
        key="domain_select",
    )
    difficulty = st.selectbox("Difficulty Level", DIFFICULTIES, index=1, key="difficulty_select")
    num_questions = st.slider("Number of Questions", 3, 15, 5, key="num_questions")
    return domain, difficulty, num_questions
