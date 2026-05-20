"""Weak area visualization with Plotly."""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_weak_area_chart(weak_areas: list[dict]) -> None:
    if not weak_areas:
        st.info("No weak areas recorded yet. Complete interviews to build your profile.")
        return

    df = pd.DataFrame(weak_areas)
    if "concept" not in df.columns:
        st.warning("Invalid weak area data format.")
        return

    fig = px.bar(
        df,
        x="concept",
        y="score",
        color="domain" if "domain" in df.columns else None,
        title="Weak Areas by Score (lower = needs more work)",
        labels={"score": "Score", "concept": "Concept"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)
