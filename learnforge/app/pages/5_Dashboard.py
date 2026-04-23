"""Page 5: Dashboard — Visualizations, charts, knowledge map, streaks."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from src.profile.storage import (init_db, get_quiz_history, get_knowledge_gaps,
                                  get_topic_scores, get_bloom_distribution,
                                  get_daily_activity, get_streak)

st.set_page_config(page_title="Dashboard — LearnForge", page_icon="📊", layout="wide")
init_db()

st.title("📊 Learning Dashboard")

user_id = "default"
history = get_quiz_history(user_id)
gaps = get_knowledge_gaps(user_id)
topic_scores = get_topic_scores(user_id)
bloom_dist = get_bloom_distribution(user_id)
daily = get_daily_activity(user_id)
streak_dates = get_streak(user_id)

# ── Top-level stats ──
col1, col2, col3, col4 = st.columns(4)
col1.metric("📝 Questions Answered", len(history))
correct = sum(1 for h in history if h.get("is_correct"))
col2.metric("✅ Correct", f"{correct}/{len(history)}" if history else "0")
accuracy = (correct / len(history) * 100) if history else 0
col3.metric("🎯 Accuracy", f"{accuracy:.0f}%")
col4.metric("🔥 Study Days", len(streak_dates))

st.divider()

# ── Use sample data if empty ──
if not history:
    st.info("📊 Take some quizzes to see your analytics here! Showing sample data for preview.")

    # Generate sample data for visualization preview
    sample_bloom = [
        {"bloom_level": "remember", "total": 8, "correct": 7, "avg_score": 4.2},
        {"bloom_level": "understand", "total": 6, "correct": 4, "avg_score": 3.5},
        {"bloom_level": "apply", "total": 5, "correct": 3, "avg_score": 3.0},
        {"bloom_level": "analyze", "total": 3, "correct": 1, "avg_score": 2.3},
        {"bloom_level": "evaluate", "total": 2, "correct": 1, "avg_score": 2.0},
        {"bloom_level": "create", "total": 1, "correct": 0, "avg_score": 1.5},
    ]
    bloom_dist = sample_bloom

    sample_daily = [
        {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
         "questions_answered": max(1, 8 - i), "correct": max(0, 6 - i), "avg_score": 3.0 + (i % 3) * 0.5}
        for i in range(7)
    ]
    daily = sample_daily

    sample_gaps = [
        {"tag": "neural_networks", "count": 4, "topic": "Machine Learning"},
        {"tag": "backpropagation", "count": 3, "topic": "Machine Learning"},
        {"tag": "overfitting", "count": 2, "topic": "Machine Learning"},
        {"tag": "gradient_descent", "count": 2, "topic": "Machine Learning"},
        {"tag": "regularization", "count": 1, "topic": "Machine Learning"},
    ]
    gaps = sample_gaps

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Bloom's Analysis", "📈 Score Trends", "🔍 Knowledge Gaps", "📅 Activity"])

with tab1:
    if bloom_dist:
        st.markdown("### Bloom's Taxonomy Performance")
        st.markdown("How well you perform at each cognitive level — from basic recall to creative synthesis.")

        # Radar chart
        bloom_order = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        bloom_scores = {b["bloom_level"]: b.get("avg_score", 0) for b in bloom_dist}

        fig = go.Figure()
        values = [bloom_scores.get(b, 0) for b in bloom_order]
        values.append(values[0])

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[b.title() for b in bloom_order] + [bloom_order[0].title()],
            fill="toself",
            name="Your Score",
            fillcolor="rgba(99, 110, 250, 0.3)",
            line=dict(color="rgb(99, 110, 250)", width=2),
        ))

        # Target line
        fig.add_trace(go.Scatterpolar(
            r=[4] * 7,
            theta=[b.title() for b in bloom_order] + [bloom_order[0].title()],
            name="Target (4/5)",
            line=dict(color="rgba(0,200,0,0.5)", dash="dash"),
        ))

        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                          showlegend=True, height=450, title="Cognitive Level Radar")
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart
        df_bloom = pd.DataFrame(bloom_dist)
        if "bloom_level" in df_bloom.columns:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_bloom["bloom_level"].str.title(),
                y=df_bloom.get("total", [0] * len(df_bloom)),
                name="Total Questions", marker_color="lightblue"))
            fig2.add_trace(go.Bar(
                x=df_bloom["bloom_level"].str.title(),
                y=df_bloom.get("correct", [0] * len(df_bloom)),
                name="Correct", marker_color="green"))
            fig2.update_layout(barmode="group", title="Questions by Bloom's Level",
                               xaxis_title="Level", yaxis_title="Count", height=350)
            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### Score Trends Over Time")
    if daily:
        df_daily = pd.DataFrame(daily)
        if "date" in df_daily.columns and "avg_score" in df_daily.columns:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df_daily["date"], y=df_daily["avg_score"],
                mode="lines+markers", name="Avg Score",
                line=dict(color="rgb(99, 110, 250)", width=3),
                marker=dict(size=8)))
            fig3.update_layout(title="Average Score per Day", xaxis_title="Date",
                               yaxis_title="Score (0-5)", yaxis=dict(range=[0, 5.5]), height=400)
            st.plotly_chart(fig3, use_container_width=True)

        if "questions_answered" in df_daily.columns:
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                x=df_daily["date"], y=df_daily["questions_answered"],
                name="Questions", marker_color="rgba(99, 110, 250, 0.7)"))
            fig4.update_layout(title="Daily Activity", xaxis_title="Date",
                               yaxis_title="Questions Answered", height=300)
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Complete some quizzes to see trends!")

with tab3:
    st.markdown("### Knowledge Gaps")
    st.markdown("Topics and concepts you need to review, based on quiz performance.")
    if gaps:
        df_gaps = pd.DataFrame(gaps)
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=[g["tag"] for g in gaps[:8]],
            y=[g["count"] for g in gaps[:8]],
            marker=dict(
                color=[g["count"] for g in gaps[:8]],
                colorscale="Reds",
                showscale=True,
                colorbar=dict(title="Frequency"),
            ),
        ))
        fig5.update_layout(title="Most Frequent Knowledge Gaps",
                           xaxis_title="Concept", yaxis_title="Times Flagged", height=400)
        st.plotly_chart(fig5, use_container_width=True)

        # Gap details table
        st.dataframe(
            pd.DataFrame(gaps).rename(columns={"tag": "Concept", "count": "Frequency", "topic": "Topic"}),
            use_container_width=True, hide_index=True)
    else:
        st.success("No knowledge gaps detected! Keep learning!")

with tab4:
    st.markdown("### Study Activity Heatmap")
    if daily:
        df_act = pd.DataFrame(daily)
        if "date" in df_act.columns:
            # Simple activity heatmap
            df_act["day_of_week"] = pd.to_datetime(df_act["date"]).dt.day_name()
            df_act["week"] = pd.to_datetime(df_act["date"]).dt.isocalendar().week

            fig6 = px.density_heatmap(
                df_act, x="date", y="questions_answered",
                title="Activity Heatmap", height=300,
                color_continuous_scale="Greens")
            st.plotly_chart(fig6, use_container_width=True)

    # Streak
    st.markdown("### 🔥 Study Streak")
    if streak_dates:
        st.markdown(f"You've studied on **{len(streak_dates)} days**!")
        streak_text = " → ".join(streak_dates[:7])
        st.code(streak_text)
    else:
        st.info("Start studying to build your streak!")
