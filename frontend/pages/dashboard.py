"""Dashboard home page."""

import streamlit as st

from components.domain_selector import DOMAINS
from utils.api_client import get_api_client


def show():
    st.markdown('<p class="main-header">Dashboard</p>', unsafe_allow_html=True)
    st.markdown("Welcome to your AI Interview Preparation Coach.")

    client = get_api_client()
    try:
        health = client.health()
        st.success(f"Backend: {health.get('status', 'unknown')} — {health.get('app', 'API')}")
    except Exception as exc:
        st.error(f"Backend unavailable: {exc}")
        st.info("Start the FastAPI server: `uvicorn app.main:app --reload` from backend/")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Domains", len(DOMAINS))
    with col2:
        st.metric("Sessions", st.session_state.get("total_sessions", 0))
    with col3:
        avg = st.session_state.get("average_score", 0)
        st.metric("Avg Score", f"{avg:.1f}%" if avg else "—")

    st.markdown("### Quick Start")
    st.markdown(
        """
        1. **Ingest** domain documents (sidebar → Admin) or run ingestion scripts
        2. **Interview** — practice with AI-powered questions
        3. **Analytics** — track scores and trends
        4. **Weak Areas** — review gaps and learning roadmap
        """
    )

    user_id = st.session_state.get("user_id", "default_user")
    try:
        analytics = client.get_analytics(user_id)
        st.session_state["total_sessions"] = analytics.get("total_sessions", 0)
        st.session_state["average_score"] = analytics.get("average_score", 0)
        if analytics.get("domain_scores"):
            st.markdown("### Domain Progress")
            for domain, score in analytics["domain_scores"].items():
                st.progress(score / 100, text=f"{DOMAINS.get(domain, domain)}: {score:.1f}%")
    except Exception:
        pass
