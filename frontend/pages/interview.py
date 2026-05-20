"""Live interview page."""

import streamlit as st

from components.chat_box import render_answer_input, render_chat_history
from components.domain_selector import render_domain_selector
from components.score_card import render_score_card
from utils.api_client import get_api_client


def _init_state():
    defaults = {
        "session_id": None,
        "chat_messages": [],
        "last_evaluation": None,
        "interview_active": False,
        "user_id": "default_user",
        "completed_session_report": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def show():
    _init_state()
    st.markdown('<p class="main-header">Live Interview</p>', unsafe_allow_html=True)

    client = get_api_client()

    # 1. Render Completed Session Report if available
    if st.session_state.completed_session_report:
        report = st.session_state.completed_session_report
        st.markdown("### 📝 Interview Performance Report")
        
        # Grid of overall metrics
        col_overall_1, col_overall_2 = st.columns([1, 1])
        with col_overall_1:
            avg_score = report.get("average_score", 0)
            st.markdown(
                f"""
                <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 14px; text-transform: uppercase; font-weight: 600; color: #818cf8; letter-spacing: 0.5px;">Average Session Score</div>
                    <div style="font-size: 40px; font-weight: 700; color: #ffffff; margin-top: 10px; margin-bottom: 10px;">{avg_score:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(avg_score / 100)
            
        with col_overall_2:
            weak_list = report.get("weak_concepts", [])
            if weak_list:
                weak_tags = "".join([f'<span style="display: inline-block; background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; border-radius: 6px; padding: 4px 8px; margin: 4px; font-size: 12px; font-weight: 500;">{concept}</span>' for concept in weak_list])
                st.markdown(
                    f"""
                    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 12px; padding: 15px; height: 100%;">
                        <div style="font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 8px;">Concepts to Improve</div>
                        <div style="display: flex; flex-wrap: wrap;">
                            {weak_tags}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 20px; text-align: center; height: 100%;">
                        <div style="font-size: 14px; text-transform: uppercase; font-weight: 600; color: #34d399; letter-spacing: 0.5px;">Concepts to Improve</div>
                        <div style="font-size: 16px; font-weight: 600; color: #ffffff; margin-top: 15px;">Excellent work! No major weak areas detected.</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        st.markdown("---")
        st.markdown("#### 🔍 Question Breakdown")
        
        for idx, eval_item in enumerate(report.get("evaluations", [])):
            with st.expander(f"Question {idx+1}: {eval_item['question'][:80]}...", expanded=(idx == 0)):
                st.markdown(f"**Question:** {eval_item['question']}")
                st.markdown(f"**Your Answer:**")
                st.info(eval_item['answer'])
                
                # Metrics for this specific question
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Technical", f"{eval_item.get('technical_correctness', 0):.0f}%")
                col2.metric("Clarity", f"{eval_item.get('communication_clarity', 0):.0f}%")
                col3.metric("Confidence", f"{eval_item.get('confidence', 0):.0f}%")
                col4.metric("Depth", f"{eval_item.get('depth_of_knowledge', 0):.0f}%")
                
                # Feedback
                st.markdown("**Evaluator Feedback:**")
                st.success(eval_item['feedback'])
                
                if eval_item.get("weak_concepts"):
                    st.warning("Weak concepts in this question: " + ", ".join(eval_item["weak_concepts"]))
                    
        st.markdown("---")
        if st.button("Start New Interview", type="primary"):
            st.session_state.completed_session_report = None
            st.rerun()
        
        return

    # 2. Render Setup Expander (if no active interview and no report showing)
    with st.expander("Setup", expanded=not st.session_state.interview_active):
        domain, difficulty, num_q = render_domain_selector()
        user_id = st.text_input("User ID", value=st.session_state.user_id)
        st.session_state.user_id = user_id

        if st.button("Start Interview", type="primary", disabled=st.session_state.interview_active):
            try:
                with st.spinner("Starting interview..."):
                    result = client.start_interview(user_id, domain, difficulty, num_q)
                st.session_state.session_id = result["session_id"]
                st.session_state.chat_messages = [
                    {"role": "interviewer", "content": result["first_question"]}
                ]
                st.session_state.interview_active = True
                st.session_state.last_evaluation = None
                st.session_state.completed_session_report = None
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to start: {exc}")

    # 3. Render Active Chat
    if st.session_state.interview_active:
        col_chat, col_score = st.columns([2, 1])
        with col_chat:
            render_chat_history(st.session_state.chat_messages)
            answer = render_answer_input()
            if answer:
                try:
                    with st.spinner("Evaluating..."):
                        response = client.submit_answer(st.session_state.session_id, answer)
                    st.session_state.chat_messages.append({"role": "candidate", "content": answer})
                    st.session_state.last_evaluation = response.get("evaluation")

                    if response.get("follow_up_question"):
                        st.session_state.chat_messages.append(
                            {"role": "interviewer", "content": response["follow_up_question"]}
                        )
                    elif response.get("next_question"):
                        st.session_state.chat_messages.append(
                            {"role": "interviewer", "content": response["next_question"]}
                        )

                    if response.get("is_complete"):
                        st.session_state.interview_active = False
                        st.balloons()
                        try:
                            summary = client.get_session_summary(st.session_state.session_id)
                            st.session_state.completed_session_report = summary
                        except Exception as exc:
                            st.warning(f"Could not load final report: {exc}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Submit failed: {exc}")

        with col_score:
            st.subheader("Live Scores")
            render_score_card(st.session_state.last_evaluation)

        if st.button("End Interview"):
            if st.session_state.session_id:
                try:
                    with st.spinner("Generating final report..."):
                        summary = client.get_session_summary(st.session_state.session_id)
                    st.session_state.completed_session_report = summary
                except Exception as exc:
                    st.warning(f"No summary available: {exc}")
            st.session_state.interview_active = False
            st.session_state.session_id = None
            st.rerun()
