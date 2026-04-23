"""Smoke tests for agents — validates structure without API calls."""
import json
import os
import pytest
from unittest.mock import patch, MagicMock

# Force demo mode for tests
os.environ["LEARNFORGE_MODE"] = "demo"

from src.agents.curriculum_architect import CurriculumArchitect
from src.agents.content_generator import ContentGenerator
from src.agents.adaptive_assessor import AdaptiveAssessor


class TestCurriculumArchitect:
    def test_demo_mode_returns_curriculum(self):
        arch = CurriculumArchitect()
        result = arch.generate_curriculum("Machine Learning", "intermediate")
        assert "topic" in result
        assert "modules" in result
        assert len(result["modules"]) >= 3
        for m in result["modules"]:
            assert "id" in m
            assert "title" in m
            assert "objectives" in m
            assert "bloom_level" in m

    def test_fallback_returns_valid_structure(self):
        arch = CurriculumArchitect()
        result = arch._fallback("Test Topic", "beginner")
        assert result["topic"] == "Test Topic"
        assert result["level"] == "beginner"
        assert len(result["modules"]) == 5


class TestContentGenerator:
    def test_demo_lesson(self):
        gen = ContentGenerator()
        module = {"id": "m1", "title": "Foundations", "objectives": ["Learn basics"], "bloom_level": "remember"}
        result = gen.generate_lesson(module, "Machine Learning", "intermediate")
        assert "sections" in result
        assert len(result["sections"]) >= 1
        for s in result["sections"]:
            assert "heading" in s
            assert "content" in s

    def test_demo_quiz(self):
        gen = ContentGenerator()
        module = {"id": "m1", "title": "Foundations", "objectives": ["Learn basics"]}
        result = gen.generate_quiz(module, "Machine Learning", "intermediate")
        assert "questions" in result
        assert len(result["questions"]) >= 1
        for q in result["questions"]:
            assert "question" in q
            assert "correct_answer" in q

    def test_demo_flashcards(self):
        gen = ContentGenerator()
        module = {"id": "m1", "title": "Foundations", "objectives": ["Learn basics"]}
        result = gen.generate_flashcards(module, "Machine Learning", "intermediate")
        assert "cards" in result
        assert len(result["cards"]) >= 1
        for c in result["cards"]:
            assert "front" in c
            assert "back" in c

    def test_fallback_returns_valid(self):
        gen = ContentGenerator()
        module = {"id": "m99", "title": "Unknown"}
        result = gen._fallback_lesson(module, "Test")
        assert "sections" in result
        assert result["module_id"] == "m99"


class TestAdaptiveAssessor:
    def test_demo_evaluate_correct(self):
        assessor = AdaptiveAssessor()
        question = {"question": "What is ML?", "correct_answer": "Machine Learning", "bloom_level": "remember"}
        result = assessor.evaluate_answer(question, "Machine Learning", [])
        assert result["correct"] is True
        assert result["score"] == 5

    def test_demo_evaluate_incorrect(self):
        assessor = AdaptiveAssessor()
        question = {"question": "What is ML?", "correct_answer": "Machine Learning",
                     "explanation": "ML stands for Machine Learning", "bloom_level": "remember"}
        result = assessor.evaluate_answer(question, "wrong answer", [])
        assert result["correct"] is False
        assert "Machine Learning" in result["feedback"]

    def test_recommendations(self):
        assessor = AdaptiveAssessor()
        result = assessor.generate_study_recommendation(
            ["neural_networks", "backpropagation"], "Machine Learning", "intermediate")
        assert "recommendations" in result
        assert len(result["recommendations"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
