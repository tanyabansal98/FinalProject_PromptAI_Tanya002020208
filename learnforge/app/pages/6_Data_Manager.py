"""Page 6: Data Manager — Upload materials, browse stored data, export content."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
from src.content.manager import (
    ingest_uploaded_file, list_corpus_files, list_generated_files,
    export_curriculum_markdown, export_quiz_csv, export_flashcards_csv,
    export_progress_report, save_curriculum
)
from src.profile.storage import init_db, get_quiz_history, get_knowledge_gaps, get_bloom_distribution
from src.config import CORPUS_DIR, GENERATED_DIR, CHROMA_DIR, SQLITE_DB_PATH

st.set_page_config(page_title="Data Manager — LearnForge", page_icon="📁", layout="wide")
init_db()

st.title("📁 Data Manager")
st.markdown("Upload your own study materials, browse stored data, and export generated content.")

tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Materials", "📂 RAG Corpus", "💾 Generated Content", "📥 Export"])

# ════════════════════════════════════════════════════════════════
# TAB 1: Upload
# ════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Upload Your Study Materials")
    st.markdown("""
    Upload PDFs, text files, or markdown documents. They'll be **ingested into the RAG knowledge base**
    so the Adaptive Assessor can use them when evaluating your quiz answers.
    """)

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Drop files here",
            type=["pdf", "txt", "md", "csv"],
            accept_multiple_files=True,
            help="Supported: PDF, TXT, Markdown, CSV"
        )
    with col2:
        category = st.selectbox(
            "Category",
            ["subjects", "pedagogy", "misconceptions", "custom"],
            help="Where to store in the corpus"
        )

    if uploaded_files:
        if st.button("📤 Ingest into RAG Corpus", type="primary", use_container_width=True):
            with st.spinner("Processing files..."):
                for f in uploaded_files:
                    path = ingest_uploaded_file(f, category)
                    st.success(f"✅ Ingested `{f.name}` → `{path.name}`")

            st.warning("⚠️ Run `make index` in your terminal to rebuild the ChromaDB index with the new files.")
            st.code("make index", language="bash")

    st.divider()
    st.markdown("### Data Storage Overview")

    col_a, col_b, col_c, col_d = st.columns(4)

    # Count corpus files
    corpus_files = list_corpus_files()
    total_corpus = sum(len(v) for v in corpus_files.values())
    col_a.metric("📚 Corpus Files", total_corpus)

    # Count generated files
    gen_files = list_generated_files()
    col_b.metric("💾 Generated Files", len(gen_files))

    # ChromaDB
    chroma_exists = CHROMA_DIR.exists()
    col_c.metric("🧠 Vector DB", "✅ Built" if chroma_exists else "❌ Not built")

    # SQLite
    db_exists = SQLITE_DB_PATH.exists()
    db_size = SQLITE_DB_PATH.stat().st_size / 1024 if db_exists else 0
    col_d.metric("🗄️ SQLite DB", f"{db_size:.1f} KB" if db_exists else "Empty")

    st.divider()
    st.markdown("### Storage Paths")
    st.code(f"""
📁 RAG Corpus:      {CORPUS_DIR}
🧠 ChromaDB:        {CHROMA_DIR}
💾 Generated Files: {GENERATED_DIR}
🗄️ SQLite Database: {SQLITE_DB_PATH}
    """)

# ════════════════════════════════════════════════════════════════
# TAB 2: RAG Corpus Browser
# ════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### RAG Knowledge Base")
    st.markdown("These documents are indexed in ChromaDB and used by the Adaptive Assessor for grounded feedback.")

    corpus_files = list_corpus_files()

    if not corpus_files:
        st.warning("No corpus files found. The corpus directory may be empty.")
    else:
        for category, files in corpus_files.items():
            with st.expander(f"📂 {category}/ ({len(files)} files)", expanded=False):
                for fname in files:
                    fpath = CORPUS_DIR / category / fname
                    col1, col2 = st.columns([4, 1])
                    col1.markdown(f"`{fname}`")
                    with col2:
                        if st.button("👁️ View", key=f"view_{category}_{fname}"):
                            content = fpath.read_text(encoding="utf-8")
                            st.markdown(content[:2000])
                            if len(content) > 2000:
                                st.caption(f"... (truncated, {len(content)} chars total)")

# ════════════════════════════════════════════════════════════════
# TAB 3: Generated Content Browser
# ════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Generated Content")
    st.markdown("All curricula, lessons, quizzes, and flashcards generated during your sessions.")

    gen_files = list_generated_files()

    if not gen_files:
        st.info("No generated content yet. Start learning to generate content!")
    else:
        df = pd.DataFrame(gen_files)
        df.columns = ["Filename", "Path", "Size (KB)", "Last Modified"]
        df["Size (KB)"] = df["Size (KB)"].round(1)
        st.dataframe(df[["Filename", "Size (KB)", "Last Modified"]], use_container_width=True, hide_index=True)

        st.divider()
        selected = st.selectbox("View a file:", [f["name"] for f in gen_files])
        if selected:
            path = GENERATED_DIR / selected
            if path.exists():
                import json
                raw = path.read_text(encoding="utf-8").strip()
                if not raw:
                    st.warning(f"⚠️ `{selected}` is empty.")
                else:
                    try:
                        content = json.loads(raw)
                        st.json(content)
                    except json.JSONDecodeError:
                        st.text(raw[:3000])
                        if len(raw) > 3000:
                            st.caption(f"... (truncated, {len(raw)} chars total)")

# ════════════════════════════════════════════════════════════════
# TAB 4: Export
# ════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Export Your Learning Content")

    curriculum = st.session_state.get("curriculum")
    quiz_data = st.session_state.get("quiz_data")
    flashcard_data = st.session_state.get("flashcard_data")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📚 Curriculum")
        if curriculum:
            md_content = export_curriculum_markdown(curriculum)
            st.download_button(
                "📥 Download Curriculum (.md)",
                data=md_content,
                file_name=f"curriculum_{curriculum.get('topic', 'export').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

            # Also save to generated folder
            if st.button("💾 Save to data/generated/", key="save_curr"):
                path = save_curriculum(curriculum.get("topic", "export"), curriculum)
                st.success(f"Saved to `{path.name}`")
        else:
            st.info("Generate a curriculum first")

        st.markdown("#### 🧪 Quiz")
        if quiz_data:
            csv_content = export_quiz_csv(quiz_data)
            st.download_button(
                "📥 Download Quiz (.csv)",
                data=csv_content,
                file_name="quiz_export.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("Take a quiz first")

    with col2:
        st.markdown("#### 🃏 Flashcards")
        if flashcard_data:
            csv_content = export_flashcards_csv(flashcard_data)
            st.download_button(
                "📥 Download Flashcards (.csv)",
                data=csv_content,
                file_name="flashcards_export.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.caption("💡 Import this CSV into Anki for spaced repetition!")
        else:
            st.info("Generate flashcards first")

        st.markdown("#### 📊 Progress Report")
        history = get_quiz_history("default")
        gaps = get_knowledge_gaps("default")
        bloom = get_bloom_distribution("default")

        if history:
            report = export_progress_report(history, gaps, bloom)
            st.download_button(
                "📥 Download Progress Report (.md)",
                data=report,
                file_name="progress_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.info("Complete some quizzes first")
