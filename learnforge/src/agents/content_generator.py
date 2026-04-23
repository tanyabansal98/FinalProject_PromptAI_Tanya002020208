"""Agent 2 — Content Generator: Creates lessons, quizzes, flashcards."""
import json
import uuid
import logging
from pathlib import Path
from src.agents.base import call_llm, get_mode
from src.config import DEMO_DATA_DIR, USE_FINETUNED, LORA_ADAPTER_DIR

logger = logging.getLogger(__name__)

_LESSON_PROMPT = (Path(__file__).parent / "prompts" / "lesson_system.txt").read_text()
_QUIZ_PROMPT = (Path(__file__).parent / "prompts" / "quiz_system.txt").read_text()
_FLASHCARD_PROMPT = (Path(__file__).parent / "prompts" / "flashcard_system.txt").read_text()


class ContentGenerator:
    """Generates educational content: lessons, quizzes, flashcards."""

    def __init__(self):
        self._ft_backend = None
        if USE_FINETUNED and (LORA_ADAPTER_DIR / "adapter_config.json").exists():
            try:
                from src.finetuning.inference import FineTunedGenerator
                self._ft_backend = FineTunedGenerator(str(LORA_ADAPTER_DIR))
                logger.info("Content Generator: using fine-tuned backend")
            except Exception as e:
                logger.warning(f"Fine-tuned model load failed: {e}")

    def generate_lesson(self, module: dict, topic: str, level: str) -> dict:
        """Generate a lesson for a module. Returns {module_id, title, sections: [{heading, content, key_concepts, examples}], summary, key_takeaways}"""
        mode = get_mode()
        if mode == "demo":
            return self._demo_lesson(module, topic)

        messages = [
            {"role": "system", "content": _LESSON_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\nLevel: {level}\nModule: {module.get('title', '')}\nObjectives: {json.dumps(module.get('objectives', []))}\nBloom's Level: {module.get('bloom_level', 'understand')}\n\nGenerate a comprehensive lesson."},
        ]

        if self._ft_backend:
            try:
                result = self._ft_backend.generate(messages[-1]["content"])
                if isinstance(result, str):
                    result = json.loads(result)
                result["module_id"] = module.get("id", str(uuid.uuid4())[:8])
                return result
            except Exception as e:
                logger.warning(f"Fine-tuned generation failed: {e}")

        result = call_llm(messages, temperature=0.7, max_tokens=3000)
        if isinstance(result, dict) and "_error" in result:
            return self._fallback_lesson(module, topic)
        result["module_id"] = module.get("id", "")
        return result

    def generate_quiz(self, module: dict, topic: str, level: str, num_questions: int = 5) -> dict:
        """Generate quiz. Returns {module_id, questions: [{id, question, type, options, correct_answer, explanation, bloom_level}]}"""
        mode = get_mode()
        if mode == "demo":
            return self._demo_quiz(module, topic)

        messages = [
            {"role": "system", "content": _QUIZ_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\nLevel: {level}\nModule: {module.get('title', '')}\nObjectives: {json.dumps(module.get('objectives', []))}\nNumber of questions: {num_questions}\n\nGenerate a quiz."},
        ]
        result = call_llm(messages, temperature=0.5)
        if isinstance(result, dict) and "_error" in result:
            return self._fallback_quiz(module, topic)
        result["module_id"] = module.get("id", "")
        return result

    def generate_flashcards(self, module: dict, topic: str, level: str, num_cards: int = 8) -> dict:
        """Generate flashcards. Returns {module_id, cards: [{id, front, back, hint, difficulty}]}"""
        mode = get_mode()
        if mode == "demo":
            return self._demo_flashcards(module, topic)

        messages = [
            {"role": "system", "content": _FLASHCARD_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\nLevel: {level}\nModule: {module.get('title', '')}\nNumber of flashcards: {num_cards}\n\nGenerate flashcards."},
        ]
        result = call_llm(messages, temperature=0.6)
        if isinstance(result, dict) and "_error" in result:
            return self._fallback_flashcards(module, topic)
        result["module_id"] = module.get("id", "")
        return result

    # ── Demo loaders ──
    def _demo_lesson(self, module, topic):
        p = DEMO_DATA_DIR / "lessons.json"
        if p.exists():
            data = json.loads(p.read_text())
            for l in data.get("lessons", []):
                if l.get("module_id") == module.get("id"):
                    return l
            if data.get("lessons"):
                lesson = data["lessons"][0]
                lesson["module_id"] = module.get("id", "")
                return lesson
        return self._fallback_lesson(module, topic)

    def _demo_quiz(self, module, topic):
        p = DEMO_DATA_DIR / "quizzes.json"
        if p.exists():
            data = json.loads(p.read_text())
            for q in data.get("quizzes", []):
                if q.get("module_id") == module.get("id"):
                    return q
            if data.get("quizzes"):
                quiz = data["quizzes"][0]
                quiz["module_id"] = module.get("id", "")
                return quiz
        return self._fallback_quiz(module, topic)

    def _demo_flashcards(self, module, topic):
        p = DEMO_DATA_DIR / "flashcards.json"
        if p.exists():
            data = json.loads(p.read_text())
            for f in data.get("sets", []):
                if f.get("module_id") == module.get("id"):
                    return f
            if data.get("sets"):
                fc = data["sets"][0]
                fc["module_id"] = module.get("id", "")
                return fc
        return self._fallback_flashcards(module, topic)

    # ── Fallbacks ──
    def _fallback_lesson(self, module, topic):
        title = module.get("title", "Introduction")
        return {
            "module_id": module.get("id", "m1"),
            "title": title,
            "sections": [
                {"heading": "Overview", "content": f"This lesson covers {title} within the context of {topic}.", "key_concepts": [f"{topic} basics"], "examples": []},
                {"heading": "Core Concepts", "content": f"The fundamental ideas behind {title} include understanding the key principles and their applications.", "key_concepts": ["Principles", "Applications"], "examples": ["Example 1"]},
                {"heading": "Practice", "content": "Try applying these concepts to real-world scenarios.", "key_concepts": ["Application"], "examples": []},
            ],
            "summary": f"In this lesson, we covered the essentials of {title}.",
            "key_takeaways": [f"Understand the foundations of {title}", "Apply concepts in practice"],
        }

    def _fallback_quiz(self, module, topic):
        return {
            "module_id": module.get("id", "m1"),
            "questions": [
                {"id": "q1", "question": f"What is a key concept in {module.get('title', topic)}?",
                 "type": "multiple_choice", "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
                 "correct_answer": "Concept A", "explanation": "Concept A is fundamental.", "bloom_level": "remember"},
            ],
        }

    def _fallback_flashcards(self, module, topic):
        return {
            "module_id": module.get("id", "m1"),
            "cards": [
                {"id": "fc1", "front": f"What is {module.get('title', topic)}?", "back": f"A core concept in {topic}.", "hint": "Think about the basics.", "difficulty": "easy"},
            ],
        }
