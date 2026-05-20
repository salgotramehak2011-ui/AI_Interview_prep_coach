"""Live score display component."""

import streamlit as st


def render_score_card(evaluation: dict | None) -> None:
    if not evaluation:
        st.info("Answer questions to see live scores.")
        return

    cols = st.columns(4)
    metrics = [
        ("Technical", evaluation.get("technical_correctness", 0)),
        ("Clarity", evaluation.get("communication_clarity", 0)),
        ("Confidence", evaluation.get("confidence", 0)),
        ("Depth", evaluation.get("depth_of_knowledge", 0)),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, f"{value:.0f}%")

    overall = evaluation.get("overall_score", 0)
    st.progress(overall / 100, text=f"Overall Score: {overall:.1f}%")

    if evaluation.get("feedback"):
        st.success(evaluation["feedback"])

    weak = evaluation.get("weak_concepts", [])
    if weak:
        st.warning("Weak areas: " + ", ".join(weak))
