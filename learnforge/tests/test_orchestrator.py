"""Tests for the LangGraph orchestrator."""
import os
import pytest

os.environ["LEARNFORGE_MODE"] = "demo"


class TestOrchestrator:
    def test_curriculum_pipeline(self):
        from src.orchestrator.graph import run_pipeline
        result = run_pipeline(action="CURRICULUM", topic="Python", level="beginner")
        assert "curriculum" in result
        assert result["curriculum"]["topic"] == "Python"
        assert len(result["curriculum"]["modules"]) >= 3

    def test_lesson_pipeline(self):
        from src.orchestrator.graph import run_pipeline
        module = {"id": "m1", "title": "Intro", "objectives": ["Learn basics"], "bloom_level": "remember"}
        result = run_pipeline(action="LESSON", topic="Python", level="beginner", active_module=module)
        assert "lesson" in result
        assert "sections" in result["lesson"]

    def test_quiz_pipeline(self):
        from src.orchestrator.graph import run_pipeline
        module = {"id": "m1", "title": "Intro", "objectives": ["Learn basics"]}
        result = run_pipeline(action="QUIZ", topic="Python", level="beginner", active_module=module)
        assert "quiz" in result
        assert "questions" in result["quiz"]

    def test_flashcard_pipeline(self):
        from src.orchestrator.graph import run_pipeline
        module = {"id": "m1", "title": "Intro", "objectives": ["Learn basics"]}
        result = run_pipeline(action="FLASHCARD", topic="Python", level="beginner", active_module=module)
        assert "flashcards" in result
        assert "cards" in result["flashcards"]

    def test_evaluate_pipeline_demo(self):
        """In demo mode, evaluate should still return a valid evaluation even without RAG."""
        from src.orchestrator.graph import run_pipeline
        question = {"question": "What is Python?", "correct_answer": "A programming language",
                     "bloom_level": "remember", "explanation": "Python is a language."}
        result = run_pipeline(
            action="EVALUATE", topic="Python", level="beginner",
            question=question, user_answer="A programming language")
        assert "evaluation" in result
        assert result["evaluation"]["correct"] is True

    def test_recommend_pipeline(self):
        from src.orchestrator.graph import run_pipeline
        result = run_pipeline(
            action="RECOMMEND", topic="Python", level="beginner",
            knowledge_gaps=["loops", "functions"])
        assert "recommendations" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
