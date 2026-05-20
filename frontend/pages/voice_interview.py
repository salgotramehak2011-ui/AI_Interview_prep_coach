"""Live voice-based interview page."""

import os
import streamlit as st
import streamlit.components.v1 as components

from components.domain_selector import render_domain_selector
from components.score_card import render_score_card
from utils.api_client import get_api_client

# Declare voice widget custom component
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_COMP_DIR = os.path.join(os.path.dirname(PARENT_DIR), "components", "voice_widget")
voice_recognition = components.declare_component("voice_recognition", path=VOICE_COMP_DIR)


def _init_state():
    defaults = {
        "voice_session_id": None,
        "voice_chat_messages": [],
        "voice_last_evaluation": None,
        "voice_interview_active": False,
        "voice_interview_completed": False,
        "voice_user_id": "default_user",
        "last_voice_metrics": None,
        "voice_evaluations": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_voice_metrics_card(metrics):
    if not metrics:
        st.info("No speech metrics captured yet. Complete a question to view speech delivery analytics!")
        return

    st.markdown("### 🎙️ Speech Delivery Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    wpm = metrics.get('words_per_minute', 0)
    with col1:
        if 110 <= wpm <= 150:
            delta_str = "Optimal (110-150)"
            color = "normal"
        elif wpm < 110:
            delta_str = "Slow (< 110)"
            color = "inverse"
        else:
            delta_str = "Fast (> 150)"
            color = "inverse"
            
        st.metric(
            label="Speaking Pace",
            value=f"{wpm} WPM",
            delta=delta_str,
            delta_color=color
        )
    with col2:
        clarity = metrics.get('speech_clarity_score', 0)
        st.metric(
            label="Speech Clarity",
            value=f"{clarity}%",
            delta="Excellent (>= 90%)" if clarity >= 90 else "Good (>= 75%)" if clarity >= 75 else "Needs Practice"
        )
    with col3:
        st.metric(
            label="Filler Words",
            value=str(metrics.get('filler_word_count', 0)),
            delta="Great pace!" if metrics.get('filler_word_count', 0) == 0 else "Try using pauses",
            delta_color="normal" if metrics.get('filler_word_count', 0) == 0 else "inverse"
        )
        
    if metrics.get('filler_word_count', 0) > 0:
        detected = metrics.get('filler_words_detected', [])
        st.warning(
            f"**Speech Dynamics Alert:** We detected filler words: {', '.join(f'`{w}`' for w in detected)}. "
            "Try to take a short, silent breath/pause instead of saying filler words when consolidating your thoughts!"
        )


def render_completed_dashboard():
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%); padding: 24px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 24px;">
            <h2 style="margin: 0; color: #8b5cf6; font-size: 28px; font-weight: 600;">🎉 Voice Interview Report</h2>
            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 15px;">Your comprehensive assessment and verbal delivery coaching summary.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    evals = st.session_state.voice_evaluations
    chat_msgs = st.session_state.voice_chat_messages
    candidate_msgs = [m for m in chat_msgs if m["role"] == "candidate"]

    if not evals or not candidate_msgs:
        st.warning("You did not answer any questions during this voice interview session. Please try again!")
        if st.button("Start New Session", type="primary"):
            st.session_state.voice_interview_completed = False
            st.rerun()
        return

    # Calculate overall average scores
    avg_technical = sum(e.get("technical_correctness", 0) for e in evals) / len(evals)
    avg_clarity = sum(e.get("communication_clarity", 0) for e in evals) / len(evals)
    avg_confidence = sum(e.get("confidence", 0) for e in evals) / len(evals)
    avg_depth = sum(e.get("depth_of_knowledge", 0) for e in evals) / len(evals)
    avg_overall = sum(e.get("overall_score", 0) for e in evals) / len(evals)

    # Calculate overall average speech metrics
    avg_wpm = sum(m["metadata"].get("words_per_minute", 0) for m in candidate_msgs) / len(candidate_msgs)
    avg_speech_clarity = sum(m["metadata"].get("speech_clarity_score", 0) for m in candidate_msgs) / len(candidate_msgs)
    total_filler = sum(m["metadata"].get("filler_word_count", 0) for m in candidate_msgs)
    
    # Unique filler words list
    unique_filler = set()
    for m in candidate_msgs:
        unique_filler.update(m["metadata"].get("filler_words_detected", []))

    st.markdown("### 🏆 Overall Assessment Summary")
    
    # Flat, responsive row of 5 metrics cards
    col_overall, col_tech, col_clarity, col_conf, col_depth = st.columns(5)
    
    with col_overall:
        st.markdown(
            f"""
            <div style="background: rgba(139, 92, 246, 0.1); border: 2px solid #8b5cf6; border-radius: 16px; padding: 12px; text-align: center; height: 100%; box-sizing: border-box;">
                <span style="font-size: 12px; text-transform: uppercase; font-weight: 600; color: #8b5cf6; display: block; margin-bottom: 4px; letter-spacing: 0.5px;">Overall Score</span>
                <span style="font-size: 32px; font-weight: 700; color: #8b5cf6; display: block; margin-bottom: 2px;">{avg_overall:.1f}%</span>
                <span style="font-size: 11px; color: #10b981; font-weight: 500; display: block;">✓ Competency OK</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    with col_tech:
        st.metric(label="Technical Depth", value=f"{avg_technical:.1f}%")
        
    with col_clarity:
        st.metric(label="Clarity & Pace", value=f"{avg_clarity:.1f}%")
        
    with col_conf:
        st.metric(label="Confidence Level", value=f"{avg_confidence:.1f}%")
        
    with col_depth:
        st.metric(label="Subject Depth", value=f"{avg_depth:.1f}%")

    st.markdown("---")
    st.markdown("### 🎙️ Verbal Delivery & Fluency Summary")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        st.metric(label="Average Pace", value=f"{avg_wpm:.0f} WPM", delta="110-150 WPM is Optimal")
    with f_col2:
        st.metric(label="Speech Clarity Score", value=f"{avg_speech_clarity:.1f}%", delta=">= 85% is target")
    with f_col3:
        st.metric(label="Total Filler Words Used", value=str(total_filler), delta="Try to reduce fillers", delta_color="inverse" if total_filler > 0 else "normal")

    if total_filler > 0:
        st.warning(
            f"**Fluency Improvement Tip:** You used `{total_filler}` filler words during this session (detected: {', '.join(f'`{w}`' for w in unique_filler)}). "
            "To improve your confidence and presence, practice active pausing: pause in silence for a fraction of a second instead of filling the void."
        )
    else:
        st.success("🌟 **Fluency Excellence:** You answered without using any detected filler words! Outstanding pace control and clarity.")

    st.markdown("---")
    st.markdown("### 📋 Question-by-Question breakdown")

    # Map interviewer and candidate messages together for comparison
    pairs = []
    current_q = None
    
    # We iterate and find corresponding candidate replies and the evaluation details in evaluations list
    eval_idx = 0
    candidate_idx = 0
    
    for msg in chat_msgs:
        if msg["role"] == "interviewer":
            current_q = msg["content"]
        elif msg["role"] == "candidate" and current_q:
            eval_detail = evals[eval_idx] if eval_idx < len(evals) else None
            pairs.append((current_q, msg["content"], msg["metadata"], eval_detail))
            eval_idx += 1
            current_q = None

    for idx, (question, answer, metadata, evaluation) in enumerate(pairs):
        title = f"Question {idx+1}: {question[:65]}..."
        with st.expander(title, expanded=(idx == 0)):
            st.markdown(f"**🎙️ Interviewer Question:**")
            st.info(question)
            
            st.markdown(f"**💬 Your Answer (Transcribed):**")
            st.write(answer)
            
            if evaluation:
                st.markdown("**📊 Technical & Delivery Evaluation:**")
                e_cols = st.columns(4)
                e_cols[0].metric("Technical", f"{evaluation.get('technical_correctness', 0):.0f}%")
                e_cols[1].metric("Clarity", f"{evaluation.get('communication_clarity', 0):.0f}%")
                e_cols[2].metric("Confidence", f"{evaluation.get('confidence', 0):.0f}%")
                e_cols[3].metric("Depth", f"{evaluation.get('depth_of_knowledge', 0):.0f}%")
                
                # Speech metrics for this question
                wpm_val = metadata.get('words_per_minute', 0)
                clarity_val = metadata.get('speech_clarity_score', 0)
                fillers_val = metadata.get('filler_word_count', 0)
                
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 12px 16px; margin: 12px 0; font-size: 14px;">
                        <strong>🔊 Question Speech Analytics:</strong> 
                        &nbsp;&bull;&nbsp; Speaking Pace: <code>{wpm_val} WPM</code> 
                        &nbsp;&bull;&nbsp; Speech Clarity: <code>{clarity_val}%</code> 
                        &nbsp;&bull;&nbsp; Filler Words: <code>{fillers_val}</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if evaluation.get("feedback"):
                    st.success(f"**💡 Expert Feedback:**\n{evaluation['feedback']}")
                    
                weak = evaluation.get("weak_concepts", [])
                if weak:
                    st.warning(f"**⚠️ Improvement Areas:** {', '.join(weak)}")
            else:
                st.info("No evaluation detail available for this answer.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start a New Session", type="primary", key="btn_restart_session"):
        st.session_state.voice_interview_completed = False
        st.session_state.voice_session_id = None
        st.session_state.voice_chat_messages = []
        st.session_state.voice_last_evaluation = None
        st.session_state.last_voice_metrics = None
        st.session_state.voice_evaluations = []
        st.rerun()


def show():
    _init_state()

    # Title Banner
    st.markdown('<p class="main-header">Voice-Based Interview</p>', unsafe_allow_html=True)
    st.markdown("Practice your speaking speed, confidence, and fluency with our interactive voice assistant.")

    client = get_api_client()

    # Case 1: Session is completed, show the premium report page
    if st.session_state.voice_interview_completed:
        render_completed_dashboard()
        return

    # Case 2: Standard workflow (Setup and active session)
    with st.expander("Setup", expanded=not st.session_state.voice_interview_active):
        domain, difficulty, num_q = render_domain_selector()
        user_id = st.text_input("User ID", value=st.session_state.voice_user_id, key="voice_uid_input")
        st.session_state.voice_user_id = user_id

        if st.button("Start Voice Interview", type="primary", disabled=st.session_state.voice_interview_active):
            try:
                with st.spinner("Starting voice interview..."):
                    result = client.start_interview(user_id, domain, difficulty, num_q)
                st.session_state.voice_session_id = result["session_id"]
                st.session_state.voice_chat_messages = [
                    {"role": "interviewer", "content": result["first_question"]}
                ]
                st.session_state.voice_interview_active = True
                st.session_state.voice_interview_completed = False
                st.session_state.voice_last_evaluation = None
                st.session_state.last_voice_metrics = None
                st.session_state.voice_evaluations = []
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to start: {exc}")

    if st.session_state.voice_interview_active:
        col_voice, col_analysis = st.columns([13, 10], gap="large")
        
        with col_voice:
            st.subheader("Interviewer Prompt")
            current_question = ""
            for msg in reversed(st.session_state.voice_chat_messages):
                if msg["role"] == "interviewer":
                    current_question = msg["content"]
                    break
            
            if current_question:
                st.info(current_question)

            # Renders our premium circular visualizer and speech-to-text widget with a dynamic key
            # to reset component return value on next question and prevent stale rerun feedback loop
            voice_data = voice_recognition(
                question=current_question, 
                key=f"voice_rec_widget_{len(st.session_state.voice_chat_messages)}"
            )
            
            if voice_data and "answer" in voice_data:
                answer = voice_data["answer"]
                metrics = voice_data["metrics"]
                
                try:
                    with st.spinner("Analyzing speech and evaluating answer..."):
                        response = client.submit_answer(
                            session_id=st.session_state.voice_session_id,
                            answer=answer,
                            voice_metrics=metrics
                        )
                    
                    evaluation = response.get("evaluation")
                    if evaluation:
                        st.session_state.voice_evaluations.append(evaluation)
                        st.session_state.voice_last_evaluation = evaluation
                        
                    st.session_state.voice_chat_messages.append({"role": "candidate", "content": answer, "metadata": metrics})
                    st.session_state.last_voice_metrics = metrics

                    if response.get("follow_up_question"):
                        st.session_state.voice_chat_messages.append(
                            {"role": "interviewer", "content": response["follow_up_question"]}
                        )
                    elif response.get("next_question"):
                        st.session_state.voice_chat_messages.append(
                            {"role": "interviewer", "content": response["next_question"]}
                        )

                    if response.get("is_complete"):
                        st.session_state.voice_interview_active = False
                        st.session_state.voice_interview_completed = True
                        st.balloons()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Evaluation failed: {exc}")

        with col_analysis:
            st.subheader("Live Analysis")
            
            tab_scores, tab_speech = st.tabs(["🎯 Live Scores", "🎙️ Speech Analytics"])
            with tab_scores:
                render_score_card(st.session_state.voice_last_evaluation)
            with tab_speech:
                render_voice_metrics_card(st.session_state.last_voice_metrics)

        st.markdown("---")
        if st.button("End Voice Interview"):
            st.session_state.voice_interview_active = False
            st.session_state.voice_interview_completed = True # Redirect to report dashboard!
            st.rerun()
