"""Chat-style interview interface."""

import streamlit as st


def render_chat_history(messages: list[dict]) -> None:
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "interviewer":
            with st.chat_message("assistant", avatar="🎯"):
                st.markdown(content)
        elif role == "candidate":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            st.info(f"{role}: {content}")


def render_answer_input() -> str | None:
    if prompt := st.chat_input("Type your answer..."):
        return prompt
    return None
