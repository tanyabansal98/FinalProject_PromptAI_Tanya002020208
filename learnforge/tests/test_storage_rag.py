"""Tests for SQLite storage and RAG ingest."""
import json
import os
import tempfile
import pytest
from pathlib import Path

os.environ["LEARNFORGE_MODE"] = "demo"

from src.profile.storage import (
    init_db, save_quiz_result, get_quiz_history, update_knowledge_gaps,
    get_knowledge_gaps, get_bloom_distribution, get_daily_activity,
    update_flashcard_progress, log_study_activity, get_streak
)
from src.rag.ingest import _load_markdown_files, _chunk_documents


class TestProfileStorage:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = Path(self.tmp.name)
        init_db(self.db_path)

    def test_save_and_get_quiz_result(self):
        save_quiz_result("test", 1, "m1", "ML", "q1", "What is ML?",
                         "Machine Learning", "Machine Learning", True, 5,
                         "remember", [], "Great!", db_path=self.db_path)
        history = get_quiz_history("test", db_path=self.db_path)
        assert len(history) == 1
        assert history[0]["is_correct"] == 1
        assert history[0]["score"] == 5

    def test_knowledge_gaps(self):
        update_knowledge_gaps("test", ["neural_nets", "backprop"], "ML", db_path=self.db_path)
        update_knowledge_gaps("test", ["neural_nets"], "ML", db_path=self.db_path)
        gaps = get_knowledge_gaps("test", db_path=self.db_path)
        tag_counts = {g["tag"]: g["count"] for g in gaps}
        assert tag_counts["neural_nets"] == 2
        assert tag_counts["backprop"] == 1

    def test_bloom_distribution(self):
        save_quiz_result("test", 1, "m1", "ML", "q1", "Q1",
                         "A", "A", True, 4, "remember", [], "", db_path=self.db_path)
        save_quiz_result("test", 1, "m1", "ML", "q2", "Q2",
                         "B", "A", False, 1, "analyze", [], "", db_path=self.db_path)
        dist = get_bloom_distribution("test", db_path=self.db_path)
        levels = {d["bloom_level"]: d for d in dist}
        assert levels["remember"]["correct"] == 1
        assert levels["analyze"]["correct"] == 0

    def test_flashcard_progress(self):
        update_flashcard_progress("test", "fc1", "m1", True, db_path=self.db_path)
        update_flashcard_progress("test", "fc1", "m1", True, db_path=self.db_path)
        update_flashcard_progress("test", "fc1", "m1", False, db_path=self.db_path)
        # No crash = success (we don't have a getter for individual flashcard progress)

    def test_study_streaks(self):
        log_study_activity("test", minutes=30, modules=1, quizzes=2, db_path=self.db_path)
        dates = get_streak("test", db_path=self.db_path)
        assert len(dates) >= 1


class TestRAGIngest:
    def test_load_markdown_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subdir = tmpdir / "pedagogy"
            subdir.mkdir()
            (subdir / "test1.md").write_text("# Test\n\nSome content here.")
            (subdir / "test2.md").write_text("# Another\n\nMore content.")

            docs = _load_markdown_files(tmpdir)
            assert len(docs) == 2
            assert all("text" in d for d in docs)
            assert all(d["metadata"]["category"] == "pedagogy" for d in docs)

    def test_chunk_documents(self):
        docs = [{
            "id": "test_doc",
            "text": "## Introduction\n\n" + ("word " * 500) + "\n\n## Details\n\n" + ("detail " * 500),
            "metadata": {"source_id": "test.md", "category": "test"},
        }]
        chunks = _chunk_documents(docs)
        assert len(chunks) >= 2
        assert all("text" in c for c in chunks)
        assert all("metadata" in c for c in chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
