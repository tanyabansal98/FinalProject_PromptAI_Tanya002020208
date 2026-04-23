"""Page 3: Quiz Arena — Interactive quiz with instant scoring and feedback."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import json
from src.profile.storage import init_db, save_quiz_result, update_knowledge_gaps, log_study_activity

st.set_page_config(page_title="Quiz Arena — LearnForge", page_icon="🧪", layout="wide")
init_db()

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []

st.title("🧪 Quiz Arena")

module = st.session_state.get("active_module")
topic = st.session_state.get("current_topic", "Machine Learning")
level = st.session_state.get("current_level", "intermediate")

if not module:
    # Use default module for demo
    module = {"id": "m1", "title": "Foundations", "objectives": ["Understand core concepts"],
              "bloom_level": "understand"}

st.markdown(f"**Module:** {module.get('title', '')} | **Topic:** {topic} | **Level:** {level.title()}")
st.divider()

# ── Generate quiz ──
if not st.session_state.quiz_data:
    with st.spinner("🎲 Generating quiz questions..."):
        from src.orchestrator.graph import run_pipeline
        result = run_pipeline(
            action="QUIZ",
            topic=topic,
            level=level,
            active_module=module,
        )
        quiz = result.get("quiz", {})
        st.session_state.quiz_data = quiz
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.quiz_results = []
    st.rerun()

quiz = st.session_state.quiz_data
questions = quiz.get("questions", [])

if not st.session_state.quiz_submitted:
    # ── Display questions ──
    for i, q in enumerate(questions):
        st.markdown(f"### Question {i+1}")

        bloom = q.get("bloom_level", "remember")
        diff = q.get("difficulty", "medium")
        bloom_emoji = {"remember": "🧠", "understand": "💡", "apply": "🔧",
                       "analyze": "🔍", "evaluate": "⚖️", "create": "🎨"}.get(bloom, "📖")
        diff_badge = {"easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}.get(diff, "")

        st.caption(f"{bloom_emoji} {bloom.title()} | {diff_badge}")
        st.markdown(q["question"])

        qid = q["id"]
        if q["type"] == "multiple_choice":
            options = q.get("options", [])
            st.session_state.quiz_answers[qid] = st.radio(
                "Select your answer:", options, key=f"radio_{qid}",
                index=None, label_visibility="collapsed")
        elif q["type"] == "true_false":
            st.session_state.quiz_answers[qid] = st.radio(
                "True or False:", ["True", "False"], key=f"tf_{qid}",
                index=None, label_visibility="collapsed")
        else:
            st.session_state.quiz_answers[qid] = st.text_area(
                "Your answer:", key=f"text_{qid}", height=80, label_visibility="collapsed")

        st.divider()

    # ── Submit ──
    if st.button("📝 Submit Quiz", type="primary", use_container_width=True):
        st.session_state.quiz_submitted = True
        st.rerun()

else:
    # ── Show results ──
    from src.orchestrator.graph import run_pipeline

    total_score = 0
    total_possible = len(questions) * 5
    all_gaps = []
    results_display = []

    for i, q in enumerate(questions):
        qid = q["id"]
        user_ans = st.session_state.quiz_answers.get(qid, "")

        # Evaluate through orchestrator: EVALUATE → retrieve (RAG) → evaluate (Assessor)
        result = run_pipeline(
            action="EVALUATE",
            topic=topic,
            level=level,
            question=q,
            user_answer=str(user_ans) if user_ans else "",
        )
        evaluation = result.get("evaluation", {})

        is_correct = evaluation.get("correct", False)
        score = evaluation.get("score", 0)
        total_score += score
        gaps = evaluation.get("gap_tags", [])
        all_gaps.extend(gaps)

        # Save to DB
        save_quiz_result("default", 0, module.get("id", ""), topic, qid,
                         q["question"], str(user_ans), q.get("correct_answer", ""),
                         is_correct, score, q.get("bloom_level", ""), gaps,
                         evaluation.get("feedback", ""))

        results_display.append((q, user_ans, evaluation))

    # Update gaps
    if all_gaps:
        update_knowledge_gaps("default", all_gaps, topic)
    log_study_activity("default", quizzes=1)

    # ── Score summary ──
    pct = (total_score / total_possible * 100) if total_possible > 0 else 0
    color = "🟢" if pct >= 80 else "🟡" if pct >= 60 else "🔴"

    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{total_score}/{total_possible}")
    col2.metric("Percentage", f"{color} {pct:.0f}%")
    correct_count = sum(1 for _, _, e in results_display if e.get("correct"))
    col3.metric("Correct", f"{correct_count}/{len(questions)}")

    st.divider()

    # ── Detailed results ──
    for i, (q, user_ans, evaluation) in enumerate(results_display):
        is_correct = evaluation.get("correct", False)
        icon = "✅" if is_correct else "❌"
        score = evaluation.get("score", 0)

        with st.expander(f"{icon} Question {i+1} — Score: {score}/5", expanded=not is_correct):
            st.markdown(f"**Q:** {q['question']}")
            st.markdown(f"**Your answer:** {user_ans or '(no answer)'}")
            st.markdown(f"**Correct answer:** {q.get('correct_answer', '')}")

            feedback = evaluation.get("feedback", "")
            if feedback:
                if is_correct:
                    st.success(feedback)
                else:
                    st.error(feedback)

            explanation = evaluation.get("explanation", "")
            if explanation:
                st.info(f"💡 **Explanation:** {explanation}")

            misconception = evaluation.get("misconception", "")
            if misconception:
                st.warning(f"⚠️ **Common misconception:** {misconception}")

    st.divider()

    # ── Actions ──
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.quiz_data = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers = {}
            st.rerun()
    with col_b:
        if st.button("📊 View Progress", use_container_width=True):
            st.switch_page("pages/5_Dashboard.py")
    with col_c:
        if st.button("← Back to Curriculum", use_container_width=True):
            mp = st.session_state.get("module_progress", {})
            mp[module["id"]] = 100 if pct >= 70 else max(mp.get(module["id"], 0), 75)
            st.session_state.module_progress = mp
            st.switch_page("pages/1_Curriculum.py")
