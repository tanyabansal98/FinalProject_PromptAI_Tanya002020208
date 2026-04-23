"""Page 1: Curriculum — Visual learning path with modules and progress."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
from src.profile.storage import init_db

st.set_page_config(page_title="Curriculum — LearnForge", page_icon="📚", layout="wide")
init_db()

# ── Session defaults ──
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "current_level" not in st.session_state:
    st.session_state.current_level = "intermediate"
if "curriculum" not in st.session_state:
    st.session_state.curriculum = None
if "module_progress" not in st.session_state:
    st.session_state.module_progress = {}

st.title("📚 Curriculum")

# ── Topic input if not set ──
if not st.session_state.current_topic:
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Topic", placeholder="e.g., Machine Learning")
    with col2:
        level = st.selectbox("Level", ["beginner", "intermediate", "advanced"])
    if st.button("Generate Curriculum", type="primary") and topic:
        st.session_state.current_topic = topic
        st.session_state.current_level = level
        st.rerun()

# ── Generate curriculum ──
if st.session_state.current_topic and not st.session_state.curriculum:
    with st.spinner(f"🏗️ Building curriculum for '{st.session_state.current_topic}'..."):
        from src.orchestrator.graph import run_pipeline
        from src.content.manager import save_curriculum
        result = run_pipeline(
            action="CURRICULUM",
            topic=st.session_state.current_topic,
            level=st.session_state.current_level,
        )
        curriculum = result.get("curriculum", {})
        st.session_state.curriculum = curriculum
        saved_path = save_curriculum(st.session_state.current_topic, curriculum)
    st.toast(f"💾 Curriculum saved to {saved_path.name}")
    st.rerun()

# ── Display curriculum ──
curriculum = st.session_state.curriculum
if curriculum:
    st.markdown(f"### {curriculum.get('topic', '')} — {curriculum.get('level', '').title()} Level")
    st.markdown(curriculum.get("description", ""))

    total_mins = sum(m.get("estimated_minutes", 20) for m in curriculum.get("modules", []))
    col1, col2, col3 = st.columns(3)
    col1.metric("Modules", len(curriculum.get("modules", [])))
    col2.metric("Est. Time", f"{total_mins} min")
    completed = sum(1 for m in curriculum.get("modules", [])
                    if st.session_state.module_progress.get(m["id"], 0) >= 100)
    col3.metric("Completed", f"{completed}/{len(curriculum.get('modules', []))}")

    st.divider()

    # ── Bloom's Taxonomy Progression Chart ──
    modules = curriculum.get("modules", [])
    bloom_order = {"remember": 1, "understand": 2, "apply": 3, "analyze": 4, "evaluate": 5, "create": 6}

    if modules:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[m["title"][:20] + "..." if len(m["title"]) > 20 else m["title"] for m in modules],
            y=[bloom_order.get(m.get("bloom_level", "remember"), 1) for m in modules],
            mode="lines+markers+text",
            text=[m.get("bloom_level", "").title() for m in modules],
            textposition="top center",
            marker=dict(size=14, color=[bloom_order.get(m.get("bloom_level", "remember"), 1) for m in modules],
                        colorscale="Viridis", showscale=True,
                        colorbar=dict(title="Bloom's Level", tickvals=[1,2,3,4,5,6],
                                      ticktext=["Remember","Understand","Apply","Analyze","Evaluate","Create"])),
            line=dict(color="rgba(100,100,255,0.5)", width=2),
        ))
        fig.update_layout(title="📈 Cognitive Complexity Progression (Bloom's Taxonomy)",
                          yaxis=dict(title="Bloom's Level", tickvals=[1,2,3,4,5,6],
                                     ticktext=["Remember","Understand","Apply","Analyze","Evaluate","Create"]),
                          xaxis=dict(title="Module"), height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Module cards ──
    st.markdown("### Module Details")
    for i, module in enumerate(modules):
        progress = st.session_state.module_progress.get(module["id"], 0)
        bloom = module.get("bloom_level", "remember")
        diff = module.get("difficulty", "medium")
        bloom_emoji = {"remember": "🧠", "understand": "💡", "apply": "🔧",
                       "analyze": "🔍", "evaluate": "⚖️", "create": "🎨"}.get(bloom, "📖")
        diff_color = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")

        with st.expander(f"{bloom_emoji} Module {i+1}: {module['title']}  {diff_color} {diff}", expanded=(i == 0)):
            st.markdown(module.get("description", ""))
            st.markdown("**Learning Objectives:**")
            for obj in module.get("objectives", []):
                st.markdown(f"- {obj}")

            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Bloom's Level:** {bloom.title()}")
            col_b.markdown(f"**Time:** ~{module.get('estimated_minutes', 20)} min")
            col_c.markdown(f"**Prerequisites:** {', '.join(module.get('prerequisites', [])) or 'None'}")

            st.progress(progress / 100, text=f"Progress: {progress}%")

            col_x, col_y, col_z = st.columns(3)
            with col_x:
                if st.button(f"📖 Read Lesson", key=f"lesson_{module['id']}", use_container_width=True):
                    st.session_state.active_module = module
                    st.switch_page("pages/2_Lesson.py")
            with col_y:
                if st.button(f"🧪 Take Quiz", key=f"quiz_{module['id']}", use_container_width=True):
                    st.session_state.active_module = module
                    st.switch_page("pages/3_Quiz_Arena.py")
            with col_z:
                if st.button(f"🃏 Flashcards", key=f"fc_{module['id']}", use_container_width=True):
                    st.session_state.active_module = module
                    st.switch_page("pages/4_Flashcards.py")
else:
    st.info("Enter a topic on the home page or above to generate your curriculum!")
