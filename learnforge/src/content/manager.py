"""Content manager — handles file uploads, exports, and data persistence."""
import json
import csv
import os
import io
import logging
from pathlib import Path
from datetime import datetime

from src.config import GENERATED_DIR, CORPUS_DIR, DATA_DIR

logger = logging.getLogger(__name__)


def save_curriculum(topic: str, curriculum: dict) -> Path:
    """Save generated curriculum to data/generated/ and return the path."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    slug = topic.lower().replace(" ", "_")[:30]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = GENERATED_DIR / f"curriculum_{slug}_{ts}.json"
    with open(path, "w") as f:
        json.dump(curriculum, f, indent=2)
    logger.info(f"Saved curriculum to {path}")
    return path


def save_lesson(module_id: str, lesson: dict) -> Path:
    """Save generated lesson."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / f"lesson_{module_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(lesson, f, indent=2)
    return path


def save_quiz(module_id: str, quiz: dict) -> Path:
    """Save generated quiz."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / f"quiz_{module_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(quiz, f, indent=2)
    return path


def save_flashcards(module_id: str, flashcards: dict) -> Path:
    """Save generated flashcards."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / f"flashcards_{module_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(flashcards, f, indent=2)
    return path


def ingest_uploaded_file(uploaded_file, category: str = "subjects") -> Path:
    """
    Ingest an uploaded file into the RAG corpus.
    Supports: .md, .txt, .pdf (text extraction)
    Returns the saved path.
    """
    corpus_cat_dir = CORPUS_DIR / category
    corpus_cat_dir.mkdir(parents=True, exist_ok=True)

    filename = uploaded_file.name
    stem = Path(filename).stem.lower().replace(" ", "_")
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        # Extract text from PDF
        try:
            import fitz  # PyMuPDF
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            text = "\n\n".join(text_parts)
            doc.close()
        except ImportError:
            # Fallback: just save raw text attempt
            text = uploaded_file.read().decode("utf-8", errors="ignore")
    elif ext in (".md", ".txt"):
        text = uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    # Save as markdown
    md_path = corpus_cat_dir / f"{stem}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {stem.replace('_', ' ').title()}\n\n")
        f.write(text)

    logger.info(f"Ingested {filename} → {md_path}")
    return md_path


def export_curriculum_markdown(curriculum: dict) -> str:
    """Export curriculum as markdown string."""
    lines = [f"# {curriculum.get('topic', 'Curriculum')} — {curriculum.get('level', '').title()} Level\n"]
    lines.append(curriculum.get("description", "") + "\n")
    lines.append(f"**Estimated Time:** {curriculum.get('total_estimated_hours', '?')} hours\n")

    for i, m in enumerate(curriculum.get("modules", []), 1):
        lines.append(f"\n## Module {i}: {m.get('title', '')}")
        lines.append(f"*{m.get('description', '')}*\n")
        lines.append(f"- **Bloom's Level:** {m.get('bloom_level', 'understand').title()}")
        lines.append(f"- **Difficulty:** {m.get('difficulty', 'medium')}")
        lines.append(f"- **Time:** ~{m.get('estimated_minutes', 20)} min")
        lines.append("- **Objectives:**")
        for obj in m.get("objectives", []):
            lines.append(f"  - {obj}")

    return "\n".join(lines)


def export_quiz_csv(quiz: dict) -> str:
    """Export quiz as CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Question", "Type", "Options", "Correct Answer", "Explanation", "Bloom Level", "Difficulty"])
    for q in quiz.get("questions", []):
        writer.writerow([
            q.get("question", ""),
            q.get("type", ""),
            " | ".join(q.get("options", []) or []),
            q.get("correct_answer", ""),
            q.get("explanation", ""),
            q.get("bloom_level", ""),
            q.get("difficulty", ""),
        ])
    return output.getvalue()


def export_flashcards_csv(flashcards: dict) -> str:
    """Export flashcards as CSV (importable to Anki)."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Front", "Back", "Hint", "Difficulty"])
    for card in flashcards.get("cards", []):
        writer.writerow([card.get("front", ""), card.get("back", ""), card.get("hint", ""), card.get("difficulty", "")])
    return output.getvalue()


def export_progress_report(quiz_history: list, gaps: list, bloom_dist: list) -> str:
    """Export a progress report as markdown."""
    lines = ["# LearnForge Progress Report\n"]
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    total = len(quiz_history)
    correct = sum(1 for h in quiz_history if h.get("is_correct"))
    lines.append(f"## Summary\n- Questions answered: {total}\n- Correct: {correct}\n- Accuracy: {correct/total*100:.0f}%\n" if total else "## Summary\nNo quizzes taken yet.\n")

    if gaps:
        lines.append("## Knowledge Gaps\n")
        for g in gaps[:10]:
            lines.append(f"- **{g['tag']}** (flagged {g['count']} times) — {g.get('topic', '')}")

    if bloom_dist:
        lines.append("\n## Bloom's Taxonomy Performance\n")
        for b in bloom_dist:
            lines.append(f"- **{b['bloom_level'].title()}**: {b.get('correct', 0)}/{b.get('total', 0)} correct (avg score: {b.get('avg_score', 0):.1f}/5)")

    return "\n".join(lines)


def list_generated_files() -> list:
    """List all files in data/generated/."""
    if not GENERATED_DIR.exists():
        return []
    files = []
    for f in sorted(GENERATED_DIR.iterdir()):
        if f.is_file():
            files.append({
                "name": f.name,
                "path": str(f),
                "size_kb": f.stat().st_size / 1024,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
    return files


def list_corpus_files() -> dict:
    """List all files in the RAG corpus by category."""
    result = {}
    if not CORPUS_DIR.exists():
        return result
    for cat_dir in sorted(CORPUS_DIR.iterdir()):
        if cat_dir.is_dir():
            files = sorted(f.name for f in cat_dir.glob("*.md"))
            result[cat_dir.name] = files
    return result
