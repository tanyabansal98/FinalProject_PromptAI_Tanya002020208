"""Page 4: Flashcards — Spaced repetition with flip animation and confidence rating."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from src.profile.storage import init_db, update_flashcard_progress

st.set_page_config(page_title="Flashcards — LearnForge", page_icon="🃏", layout="wide")
init_db()

if "flashcard_data" not in st.session_state:
    st.session_state.flashcard_data = None
if "fc_index" not in st.session_state:
    st.session_state.fc_index = 0
if "fc_flipped" not in st.session_state:
    st.session_state.fc_flipped = False
if "fc_stats" not in st.session_state:
    st.session_state.fc_stats = {"correct": 0, "incorrect": 0, "total": 0}

st.title("🃏 Flashcards")

module = st.session_state.get("active_module")
topic = st.session_state.get("current_topic", "Machine Learning")
level = st.session_state.get("current_level", "intermediate")

if not module:
    module = {"id": "m1", "title": "Foundations", "objectives": ["Understand core concepts"]}

st.markdown(f"**Module:** {module.get('title', '')} | **Topic:** {topic}")
st.divider()

# ── Generate flashcards ──
if not st.session_state.flashcard_data:
    with st.spinner("🃏 Generating flashcards..."):
        from src.orchestrator.graph import run_pipeline
        result = run_pipeline(
            action="FLASHCARD",
            topic=topic,
            level=level,
            active_module=module,
        )
        fc_data = result.get("flashcards", {})
        st.session_state.flashcard_data = fc_data
        st.session_state.fc_index = 0
        st.session_state.fc_flipped = False
        st.session_state.fc_stats = {"correct": 0, "incorrect": 0, "total": 0}
    st.rerun()

cards = st.session_state.flashcard_data.get("cards", [])

if not cards:
    st.warning("No flashcards available.")
    st.stop()

idx = st.session_state.fc_index
stats = st.session_state.fc_stats

# ── Progress bar ──
col1, col2, col3, col4 = st.columns(4)
col1.metric("Card", f"{idx + 1}/{len(cards)}")
col2.metric("✅ Correct", stats["correct"])
col3.metric("❌ Incorrect", stats["incorrect"])
mastery = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
col4.metric("Mastery", f"{mastery:.0f}%")

st.progress((idx + 1) / len(cards))
st.divider()

# ── Current card ──
card = cards[idx]
diff_badge = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(card.get("difficulty", "medium"), "⚪")

if not st.session_state.fc_flipped:
    # Front of card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px; border-radius: 16px; text-align: center; min-height: 200px;
                display: flex; align-items: center; justify-content: center; flex-direction: column;">
        <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin-bottom: 10px;">{diff_badge} Card {idx+1} of {len(cards)}</p>
        <h2 style="color: white; margin: 0;">{card['front']}</h2>
    </div>
    """, unsafe_allow_html=True)

    col_hint, col_flip = st.columns(2)
    with col_hint:
        if st.button("💡 Show Hint", use_container_width=True):
            st.info(f"**Hint:** {card.get('hint', 'No hint available')}")
    with col_flip:
        if st.button("🔄 Flip Card", type="primary", use_container_width=True):
            st.session_state.fc_flipped = True
            st.rerun()
else:
    # Back of card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                padding: 40px; border-radius: 16px; text-align: center; min-height: 200px;
                display: flex; align-items: center; justify-content: center; flex-direction: column;">
        <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin-bottom: 10px;">ANSWER</p>
        <h3 style="color: white; margin: 0;">{card['back']}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**How well did you know this?**")

    def advance_card(correct_flag):
        stats["total"] += 1
        if correct_flag:
            stats["correct"] += 1
        else:
            stats["incorrect"] += 1
        update_flashcard_progress("default", card["id"], module.get("id", ""), correct_flag)
        st.session_state.fc_flipped = False
        st.session_state.fc_stats = stats
        if st.session_state.fc_index < len(cards) - 1:
            st.session_state.fc_index += 1
        else:
            st.session_state.fc_index = 0
        st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❌ Didn't know", use_container_width=True):
            advance_card(False)
    with col2:
        if st.button("🤔 Kinda knew", use_container_width=True):
            advance_card(True)
    with col3:
        if st.button("✅ Knew it!", use_container_width=True):
            advance_card(True)


# ── Navigation ──
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    if st.button("🔄 Restart Deck", use_container_width=True):
        st.session_state.fc_index = 0
        st.session_state.fc_flipped = False
        st.session_state.fc_stats = {"correct": 0, "incorrect": 0, "total": 0}
        st.rerun()
with col_b:
    if st.button("← Back to Curriculum", use_container_width=True):
        st.switch_page("pages/1_Curriculum.py")
