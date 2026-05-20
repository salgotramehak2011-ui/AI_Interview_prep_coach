"""Analytics dashboard page."""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.domain_selector import DOMAINS
from utils.api_client import get_api_client


def show():
    st.markdown('<p class="main-header">Analytics</p>', unsafe_allow_html=True)
    user_id = st.text_input("User ID", value=st.session_state.get("user_id", "default_user"))
    client = get_api_client()

    try:
        data = client.get_analytics(user_id)
    except Exception as exc:
        st.error(f"Could not load analytics: {exc}")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sessions", data.get("total_sessions", 0))
    c2.metric("Average Score", f"{data.get('average_score', 0):.1f}%")
    c3.metric("Weak Areas", len(data.get("weak_areas", [])))

    trend = data.get("performance_trend", [])
    if trend:
        df = pd.DataFrame(trend)
        df["date"] = pd.to_datetime(df["date"])
        fig = px.line(
            df,
            x="date",
            y="score",
            color="domain",
            markers=True,
            title="Performance Trend Over Time",
        )
        st.plotly_chart(fig, use_container_width=True)

    domain_scores = data.get("domain_scores", {})
    if domain_scores:
        df_dom = pd.DataFrame(
            [{"domain": DOMAINS.get(k, k), "score": v} for k, v in domain_scores.items()]
        )
        fig2 = px.bar(df_dom, x="domain", y="score", title="Domain-wise Average Scores")
        st.plotly_chart(fig2, use_container_width=True)

    roadmap = data.get("roadmap", [])
    if roadmap:
        st.subheader("Learning Roadmap")
        for item in roadmap:
            with st.expander(f"{item['concept']} — {item['priority']} priority"):
                st.write("Resources:", ", ".join(item.get("resources", [])))
                st.caption(f"Estimated: {item.get('estimated_weeks', 1)} week(s)")
