"""Weak areas and improvement page."""

import streamlit as st

from components.domain_selector import DOMAINS
from components.weak_area_chart import render_weak_area_chart
from utils.api_client import get_api_client


def show():
    st.markdown('<p class="main-header">Weak Areas</p>', unsafe_allow_html=True)
    user_id = st.text_input("User ID", value=st.session_state.get("user_id", "default_user"))
    domain_filter = st.selectbox(
        "Filter by Domain",
        ["all"] + list(DOMAINS.keys()),
        format_func=lambda x: "All Domains" if x == "all" else DOMAINS[x],
    )

    client = get_api_client()
    try:
        data = client.get_analytics(user_id)
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        return

    weak_areas = data.get("weak_areas", [])
    if domain_filter != "all":
        weak_areas = [w for w in weak_areas if w.get("domain") == domain_filter]

    render_weak_area_chart(weak_areas)

    if weak_areas:
        st.subheader("Improvement Suggestions")
        for wa in weak_areas:
            suggestions = wa.get("suggestions", [])
            st.markdown(f"**{wa.get('concept')}** ({DOMAINS.get(wa.get('domain'), '')}) — Score: {wa.get('score', 0):.0f}")
            for s in suggestions:
                st.write(f"- {s}")
