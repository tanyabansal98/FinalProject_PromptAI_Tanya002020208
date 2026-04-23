"""LearnForge — AI-Powered Personalized Learning Content Creator."""
import streamlit as st
import os

st.set_page_config(page_title="LearnForge", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")

# ── Mode management ──
if "mode" not in st.session_state:
    st.session_state.mode = os.getenv("LEARNFORGE_MODE", "demo")

# ── Sidebar ──
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/fire-element.png", width=60)
    st.title("LearnForge")
    st.caption("AI Learning Content Creator")

    st.divider()

    # Mode switcher
    mode = st.radio(
        "⚡ Mode",
        ["🎭 Demo (No API needed)", "🔑 API (OpenAI)", "🦙 Ollama (Local)"],
        index=["demo", "api", "ollama"].index(st.session_state.mode),
        help="Demo mode uses pre-generated content. API mode needs OpenAI key. Ollama mode uses local models."
    )
    mode_map = {"🎭 Demo (No API needed)": "demo", "🔑 API (OpenAI)": "api", "🦙 Ollama (Local)": "ollama"}
    st.session_state.mode = mode_map[mode]
    os.environ["LEARNFORGE_MODE"] = st.session_state.mode

    if st.session_state.mode == "demo":
        st.success("✅ Demo mode — no API key needed")
    elif st.session_state.mode == "api":
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API key set")
        else:
            st.warning("⚠️ Enter your API key")
    else:
        ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
        os.environ["OLLAMA_BASE_URL"] = ollama_url
        st.info("🦙 Make sure Ollama is running")

    st.divider()
    st.markdown("**Data Storage:**")
    st.markdown("📁 `data/corpus/` — RAG knowledge base")
    st.markdown("🗄️ `learnforge.db` — Progress (SQLite)")
    st.markdown("💾 `data/generated/` — Cached content")
    st.markdown("🧠 `chroma_db/` — Vector embeddings")

    st.divider()
    st.caption("Built by Tanya Bansal")
    st.caption("Northeastern University — INFO 7375")

# ── Main content ──
st.title("🔥 LearnForge")
st.subheader("Your AI-Powered Personalized Learning Coach")

st.markdown("""
Pick any topic. Tell us your level. LearnForge generates a **complete personalized learning package** —
structured lessons, interactive quizzes, flashcards, and tracks your progress with adaptive difficulty.
""")

st.divider()

# ── Topic input ──
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("🎯 What do you want to learn?", placeholder="e.g., Machine Learning, Kubernetes, Photosynthesis, World War II...")
with col2:
    level = st.selectbox("📊 Your level", ["beginner", "intermediate", "advanced"])

if st.button("🚀 Generate Learning Path", type="primary", use_container_width=True, disabled=not topic):
    st.session_state.current_topic = topic
    st.session_state.current_level = level
    st.session_state.curriculum = None  # will be generated on curriculum page
    st.switch_page("pages/1_Curriculum.py")

st.divider()

# ── Feature cards ──
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 📚 Structured Lessons")
    st.markdown("AI breaks any topic into modules with clear objectives, examples, and key takeaways — adapted to your level.")
    if st.button("View Curriculum →", use_container_width=True):
        st.switch_page("pages/1_Curriculum.py")

with c2:
    st.markdown("### 🧪 Interactive Quizzes")
    st.markdown("Test your understanding with adaptive quizzes. Get instant feedback with explanations grounded in reference material.")
    if st.button("Take a Quiz →", use_container_width=True):
        st.switch_page("pages/3_Quiz_Arena.py")

with c3:
    st.markdown("### 📊 Progress Dashboard")
    st.markdown("Track scores, visualize knowledge gaps, see Bloom's taxonomy distribution, and study streaks.")
    if st.button("View Progress →", use_container_width=True):
        st.switch_page("pages/5_Dashboard.py")

st.divider()

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown("### 🃏 Flashcards")
    st.markdown("Spaced repetition flashcards. Rate your confidence to optimize review timing.")
    if st.button("Study Flashcards →", use_container_width=True):
        st.switch_page("pages/4_Flashcards.py")

with c5:
    st.markdown("### 📁 Data Manager")
    st.markdown("Upload your own study materials (PDF, TXT, MD). Export content. Browse stored data.")
    if st.button("Manage Data →", use_container_width=True):
        st.switch_page("pages/6_Data_Manager.py")

with c6:
    st.markdown("### 🎨 Multimodal AI")
    st.markdown("Auto-generated concept diagrams for each lesson + text-to-speech audio narration.")

st.divider()

# ── Architecture summary ──
st.markdown("#### How LearnForge Works")
st.markdown("""
1. **Curriculum Architect** (Agent 1) analyzes your topic and builds a structured learning path using Bloom's Taxonomy
2. **Content Generator** (Agent 2) creates lessons, quizzes, and flashcards — powered by a fine-tuned LLM
3. **Adaptive Assessor** (Agent 3) evaluates your quiz answers using RAG-retrieved reference material and adjusts difficulty
4. **Multimodal Engine** generates concept diagrams (DALL-E / SVG) and audio narration (OpenAI TTS / browser TTS)
5. Your **knowledge profile** updates after each interaction — the system gets smarter about your gaps
""")

st.divider()

# ── Rubric components ──
st.markdown("#### 🏆 Technical Components (5 of 6 rubric areas)")
rc1, rc2, rc3, rc4, rc5 = st.columns(5)
rc1.markdown("**Prompt Eng.**\n\n5 system prompts, JSON mode, Bloom's constraints")
rc2.markdown("**Fine-Tuning**\n\nQLoRA on Llama-3.2-3B, 180 training examples")
rc3.markdown("**RAG**\n\n30-doc corpus, hybrid retrieval, cross-encoder reranker")
rc4.markdown("**Multimodal**\n\nImage gen (DALL-E/SVG) + TTS (OpenAI/browser)")
rc5.markdown("**Synthetic Data**\n\n180 instruction-tuned examples for fine-tuning")

