"""Page 2: Lesson Viewer — Rich formatted lesson content."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from src.profile.storage import init_db, log_study_activity

st.set_page_config(page_title="Lesson — LearnForge", page_icon="📖", layout="wide")
init_db()

if "active_module" not in st.session_state:
    st.session_state.active_module = None
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = None

st.title("📖 Lesson Viewer")

module = st.session_state.get("active_module")
topic = st.session_state.get("current_topic", "")
level = st.session_state.get("current_level", "intermediate")

if not module:
    st.info("Select a module from the Curriculum page to start learning!")
    if st.button("← Go to Curriculum"):
        st.switch_page("pages/1_Curriculum.py")
    st.stop()

# Generate lesson if not cached
if not st.session_state.current_lesson or st.session_state.current_lesson.get("module_id") != module.get("id"):
    with st.spinner(f"📝 Generating lesson for '{module.get('title', '')}'..."):
        from src.orchestrator.graph import run_pipeline
        result = run_pipeline(
            action="LESSON",
            topic=topic,
            level=level,
            active_module=module,
        )
        lesson = result.get("lesson", {})
        st.session_state.current_lesson = lesson

lesson = st.session_state.current_lesson

# ── Header ──
st.markdown(f"## {lesson.get('title', module.get('title', ''))}")

bloom = module.get("bloom_level", "understand")
bloom_emoji = {"remember": "🧠", "understand": "💡", "apply": "🔧",
               "analyze": "🔍", "evaluate": "⚖️", "create": "🎨"}.get(bloom, "📖")

col1, col2, col3 = st.columns(3)
col1.markdown(f"**Topic:** {topic}")
col2.markdown(f"**Level:** {level.title()}")
col3.markdown(f"**Bloom's:** {bloom_emoji} {bloom.title()}")

st.divider()

# ── Multimodal: Concept Image ──
from src.content.multimodal import generate_concept_image

if "lesson_image" not in st.session_state or st.session_state.get("lesson_image_module") != module.get("id"):
    img_result = generate_concept_image(topic, module.get("title", ""), module.get("description", ""))
    st.session_state.lesson_image = img_result
    st.session_state.lesson_image_module = module.get("id")

img = st.session_state.lesson_image
if img["type"] == "url":
    st.image(img["data"], caption=f"🎨 AI-Generated: {img.get('prompt', '')[:80]}", use_container_width=True)
elif img["type"] == "svg":
    st.markdown(img["data"], unsafe_allow_html=True)
    st.caption(f"🎨 Concept diagram — {img.get('prompt', '')}")

st.divider()

# ── Multimodal: Text-to-Speech ──
from src.content.multimodal import generate_audio, get_tts_voices

with st.expander("🔊 Listen to this lesson (Text-to-Speech)"):
    tts_col1, tts_col2 = st.columns([3, 1])
    with tts_col2:
        voice = st.selectbox("Voice", get_tts_voices(), index=0)
    with tts_col1:
        if st.button("🔊 Generate Audio", use_container_width=True):
            # Combine lesson text
            full_text = lesson.get("title", "") + ". "
            for section in lesson.get("sections", []):
                full_text += section.get("heading", "") + ". " + section.get("content", "") + " "
            full_text += lesson.get("summary", "")

            with st.spinner("Generating audio..."):
                audio_result = generate_audio(full_text[:4000], voice)

            if audio_result["type"] == "audio_bytes":
                st.audio(audio_result["data"], format="audio/mp3")
                st.success("✅ Audio generated! You can also find it in `data/generated/`")
            else:
                # Browser TTS fallback
                tts_text = audio_result["data"][:500].replace("'", "\\'").replace("\n", " ")
                st.markdown(f"""
                <button onclick="
                    const utterance = new SpeechSynthesisUtterance('{tts_text}');
                    utterance.rate = 0.9;
                    window.speechSynthesis.speak(utterance);
                " style="padding:10px 20px; background:#667eea; color:white; border:none; border-radius:8px; cursor:pointer; font-size:16px;">
                    ▶️ Play with Browser TTS
                </button>
                <p style="color:#888; font-size:12px; margin-top:5px;">
                    💡 Demo/Ollama mode uses browser-native speech. API mode uses OpenAI's HD voices.
                </p>
                """, unsafe_allow_html=True)

st.divider()

# ── Learning Objectives ──
with st.container():
    st.markdown("### 🎯 Learning Objectives")
    for obj in module.get("objectives", []):
        st.markdown(f"✅ {obj}")

st.divider()

# ── Lesson Sections ──
for i, section in enumerate(lesson.get("sections", [])):
    st.markdown(f"### {section.get('heading', f'Section {i+1}')}")
    st.markdown(section.get("content", ""))

    # Key concepts callout
    concepts = section.get("key_concepts", [])
    if concepts:
        st.info("**💡 Key Concepts:** " + " · ".join(concepts))

    # Examples
    examples = section.get("examples", [])
    if examples:
        with st.expander("📋 Examples"):
            for ex in examples:
                st.markdown(f"- {ex}")

    if i < len(lesson.get("sections", [])) - 1:
        st.divider()

# ── Summary ──
st.divider()
st.markdown("### 📋 Summary")
st.success(lesson.get("summary", ""))

# ── Key Takeaways ──
takeaways = lesson.get("key_takeaways", [])
if takeaways:
    st.markdown("### 🎯 Key Takeaways")
    for t in takeaways:
        st.markdown(f"✨ {t}")

# ── Navigation ──
st.divider()
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("← Back to Curriculum", use_container_width=True):
        # Mark module progress
        mp = st.session_state.get("module_progress", {})
        mp[module["id"]] = max(mp.get(module["id"], 0), 50)
        st.session_state.module_progress = mp
        log_study_activity("default", minutes=module.get("estimated_minutes", 20), modules=1)
        st.switch_page("pages/1_Curriculum.py")
with col_b:
    if st.button("🧪 Take Quiz →", type="primary", use_container_width=True):
        mp = st.session_state.get("module_progress", {})
        mp[module["id"]] = max(mp.get(module["id"], 0), 50)
        st.session_state.module_progress = mp
        st.switch_page("pages/3_Quiz_Arena.py")
with col_c:
    if st.button("🃏 Flashcards →", use_container_width=True):
        st.switch_page("pages/4_Flashcards.py")
