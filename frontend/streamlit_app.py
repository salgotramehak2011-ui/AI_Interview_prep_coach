"""
AI Interview Preparation Coach - Streamlit Frontend
Run: streamlit run streamlit_app.py
"""

import sys
from pathlib import Path

# Ensure frontend package root is on path
FRONTEND_DIR = Path(__file__).resolve().parent
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

import streamlit as st

from pages import analytics, dashboard, interview, voice_interview, weak_areas

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = FRONTEND_DIR / "assets" / "css" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

PAGES = {
    "📊 Dashboard": dashboard.show,
    "💬 Chat Interview": interview.show,
    "🎙️ Voice Interview": voice_interview.show,
    "📈 Analytics": analytics.show,
    "⚠️ Weak Areas": weak_areas.show,
}

with st.sidebar:
    st.markdown("## 🎯 AI PREP COACH")
    st.markdown("---")
    
    page = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("---")
    
    # Glowing glassmorphic control card for the API Endpoint
    st.markdown(
        """
        <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 12px; margin-bottom: -10px;">
            <span style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: #a78bfa; letter-spacing: 0.5px;">📡 Core AI Backend URL</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.session_state.setdefault("api_base_url", "http://localhost:8000/api/v1")
    st.session_state["api_base_url"] = st.text_input(
        "API Base URL",
        value=st.session_state["api_base_url"],
        label_visibility="collapsed"
    )
    
    # Dynamically fetch backend health / active LLM provider
    try:
        from utils.api_client import get_api_client
        client = get_api_client()
        health_data = client.health()
        provider = health_data.get("llm_provider", "LLM")
        status_text = f"Connected to {provider}"
        status_color = "#10b981"
        pulse_color = "#10b981"
    except Exception:
        status_text = "Disconnected from Backend"
        status_color = "#ef4444"
        pulse_color = "#ef4444"

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-top: -8px; margin-bottom: 8px; font-size: 12px; color: {status_color}; font-weight: 500;">
            <span style="width: 8px; height: 8px; background-color: {pulse_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {pulse_color};"></span>
            {status_text}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    with st.expander("Admin — RAG Ingest"):
        from utils.api_client import get_api_client

        domain_ingest = st.selectbox(
            "Domain",
            ["ai_ml", "web_dev", "cybersecurity"],
            key="ingest_domain",
        )
        force = st.checkbox("Force rebuild", value=False)
        if st.button("Run Ingestion"):
            try:
                client = get_api_client()
                result = client.ingest_domain(domain_ingest, force_rebuild=force)
                st.success(result.get("message", "Done"))
                st.json(result)
            except Exception as exc:
                st.error(str(exc))

PAGES[page]()
 