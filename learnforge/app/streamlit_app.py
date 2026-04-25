"""LearnForge — AI-Powered Personalized Learning Content Creator."""
import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(page_title="LearnForge", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")

# ── Auto-build ChromaDB index if missing ──
from src.config import CHROMA_DIR, CORPUS_DIR
if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
    corpus_count = sum(1 for _ in CORPUS_DIR.rglob("*.md")) if CORPUS_DIR.exists() else 0
    if corpus_count > 0:
        with st.spinner(f"🔨 Building RAG index from {corpus_count} corpus files (first run only)..."):
            from src.rag.ingest import build_index
            build_index()
        st.toast("✅ RAG index built automatically!")

# ── Init database ──
from src.profile.storage import init_db
init_db()

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

# ── Custom CSS for polished dark theme ──
st.markdown("""
<style>
    /* Global tweaks */
    .stApp { background-color: #0D1117; }
    .block-container { max-width: 1100px; padding-top: 3.5rem; }

    /* Card styling */
    .feature-card {
        background: #161B22; border: 1px solid #30363D; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem; transition: border-color 0.2s;
    }
    .feature-card:hover { border-color: #FF6B35; }
    .feature-card h3 { margin: 0 0 0.5rem 0; font-size: 1.1rem; }
    .feature-card p { color: #8B949E; font-size: 0.9rem; line-height: 1.5; margin: 0; }

    /* Hero section */
    .hero-title { font-size: 4.5rem; font-weight: 800; margin-bottom: 0.3rem; letter-spacing: -1px; }
    .hero-accent { color: #FF6B35; }
    .hero-sub { color: #8B949E; font-size: 1.15rem; line-height: 1.6; }

    /* Badge */
    .tech-badge {
        display: inline-block; padding: 0.3rem 0.8rem; border-radius: 6px;
        font-size: 0.75rem; font-weight: 600; margin: 0.15rem;
    }
    .badge-orange { background: rgba(255,107,53,0.12); color: #FF6B35; border: 1px solid rgba(255,107,53,0.2); }
    .badge-teal { background: rgba(63,185,160,0.12); color: #3FB9A0; border: 1px solid rgba(63,185,160,0.2); }
    .badge-purple { background: rgba(167,139,250,0.12); color: #A78BFA; border: 1px solid rgba(167,139,250,0.2); }
    .badge-blue { background: rgba(88,166,255,0.12); color: #58A6FF; border: 1px solid rgba(88,166,255,0.2); }
    .badge-coral { background: rgba(247,129,102,0.12); color: #F78166; border: 1px solid rgba(247,129,102,0.2); }

    /* Dividers */
    hr { border-color: #21262D !important; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Main content ──
st.markdown('<p style="font-size:4.5rem; font-weight:800; margin-bottom:0.3rem; letter-spacing:-1px; line-height:1.1;">🔥 Learn<span style="color:#FF6B35;">Forge</span></p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Pick any topic. Tell us your level. Get a complete personalized learning package — structured lessons, interactive quizzes, flashcards, and adaptive progress tracking.</p>', unsafe_allow_html=True)

st.markdown("""
<span class="tech-badge badge-orange">Prompt Engineering</span>
<span class="tech-badge badge-teal">RAG Pipeline</span>
<span class="tech-badge badge-purple">Fine-Tuned LLM</span>
<span class="tech-badge badge-blue">Multimodal</span>
<span class="tech-badge badge-coral">Synthetic Data</span>
""", unsafe_allow_html=True)

st.markdown("")

# ── Topic input ──
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("🎯 What do you want to learn?", placeholder="e.g., Machine Learning, Kubernetes, Photosynthesis, World War II...")
with col2:
    level = st.selectbox("📊 Your level", ["beginner", "intermediate", "advanced"])

if st.button("🚀 Generate Learning Path", type="primary", use_container_width=True, disabled=not topic):
    st.session_state.current_topic = topic
    st.session_state.current_level = level
    st.session_state.curriculum = None
    st.switch_page("pages/1_Curriculum.py")

st.divider()

# ── Feature cards ──
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""<div class="feature-card">
        <h3>📚 Structured Lessons</h3>
        <p>AI breaks any topic into modules with Bloom's Taxonomy progression, key concepts, examples, and takeaways.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("View Curriculum →", use_container_width=True):
        st.switch_page("pages/1_Curriculum.py")

with c2:
    st.markdown("""<div class="feature-card">
        <h3>🧪 Interactive Quizzes</h3>
        <p>MCQ, true/false, short answer. RAG-grounded feedback with misconception detection and Bloom's level tagging.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("Take a Quiz →", use_container_width=True):
        st.switch_page("pages/3_Quiz_Arena.py")

with c3:
    st.markdown("""<div class="feature-card">
        <h3>📊 Progress Dashboard</h3>
        <p>Bloom's radar chart, score trends, knowledge gap heatmap, and study streaks — all in real time.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("View Progress →", use_container_width=True):
        st.switch_page("pages/5_Dashboard.py")

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown("""<div class="feature-card">
        <h3>🃏 Flashcards</h3>
        <p>Spaced repetition cards with hints, flip animation, and confidence tracking for long-term retention.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("Study Flashcards →", use_container_width=True):
        st.switch_page("pages/4_Flashcards.py")

with c5:
    st.markdown("""<div class="feature-card">
        <h3>📁 Data Manager</h3>
        <p>Upload PDFs, TXT, markdown into the RAG corpus. Export content as CSV/MD. Browse all stored data.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("Manage Data →", use_container_width=True):
        st.switch_page("pages/6_Data_Manager.py")

with c6:
    st.markdown("""<div class="feature-card">
        <h3>🎨 Multimodal AI</h3>
        <p>Auto-generated concept diagrams (DALL-E / SVG) and text-to-speech audio narration on every lesson.</p>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Architecture summary ──
st.markdown("#### How LearnForge works")
st.markdown("""
1. **Curriculum Architect** (Agent 1) analyzes your topic and builds a structured learning path using Bloom's Taxonomy
2. **Content Generator** (Agent 2) creates lessons, quizzes, and flashcards — powered by a fine-tuned LLM
3. **Adaptive Assessor** (Agent 3) evaluates your quiz answers using RAG-retrieved reference material
4. **Multimodal Engine** generates concept diagrams and audio narration for each lesson
5. Your **knowledge profile** updates after each quiz — the system targets your weak areas
""")

