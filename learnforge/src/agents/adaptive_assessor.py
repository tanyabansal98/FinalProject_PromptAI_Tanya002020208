"""Agent 3 — Adaptive Assessor: Evaluates answers with RAG-grounded feedback."""
import json
import logging
from pathlib import Path
from src.agents.base import call_llm, get_mode
from src.config import DEMO_DATA_DIR

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "assessor_system.txt").read_text()


class AdaptiveAssessor:
    """Evaluates quiz answers and provides RAG-grounded feedback."""

    def evaluate_answer(self, question: dict, user_answer: str, retrieved_docs: list) -> dict:
        """
        Evaluate a single answer.
        Returns {correct: bool, score: 0-5, feedback, explanation, misconception, bloom_level, gap_tags}
        """
        mode = get_mode()
        if mode == "demo":
            return self._demo_evaluate(question, user_answer)

        # Build context with retrieved docs
        doc_context = "\n".join([
            f"[{d.get('source_id', 'unknown')}]: {d.get('text', '')[:500]}"
            for d in retrieved_docs[:3]
        ]) if retrieved_docs else "[No reference documents]"

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"""REFERENCE MATERIAL:
{doc_context}

---
QUESTION: {question.get('question', '')}
CORRECT ANSWER: {question.get('correct_answer', '')}
USER'S ANSWER: {user_answer}
BLOOM'S LEVEL: {question.get('bloom_level', 'understand')}

Evaluate the user's answer."""},
        ]

        result = call_llm(messages, temperature=0.3)
        if isinstance(result, dict) and "_error" in result:
            return self._fallback_eval(question, user_answer)
        return self._validate(result, question)

    def generate_study_recommendation(self, gap_tags: list, topic: str, level: str) -> dict:
        """Generate study recommendations based on knowledge gaps."""
        mode = get_mode()
        if mode == "demo":
            return {
                "recommendations": [
                    {"area": tag, "action": f"Review {tag} fundamentals", "priority": "high"}
                    for tag in gap_tags[:3]
                ],
                "next_bloom_level": "understand",
                "suggested_topics": gap_tags[:3],
            }

        messages = [
            {"role": "system", "content": "You are an adaptive learning advisor. Output JSON."},
            {"role": "user", "content": f"Student studying {topic} at {level} level has these knowledge gaps: {json.dumps(gap_tags)}. Recommend study actions. Output JSON with: recommendations (array of {{area, action, priority}}), next_bloom_level, suggested_topics."},
        ]
        result = call_llm(messages, temperature=0.5)
        if isinstance(result, dict) and "_error" not in result:
            return result
        return {"recommendations": [], "next_bloom_level": "understand", "suggested_topics": gap_tags[:3]}

    def _demo_evaluate(self, question, user_answer):
        correct = user_answer.strip().lower() == question.get("correct_answer", "").strip().lower()
        return {
            "correct": correct,
            "score": 5 if correct else 2,
            "feedback": "Great job!" if correct else f"Not quite. The correct answer is: {question.get('correct_answer', '')}",
            "explanation": question.get("explanation", ""),
            "misconception": "" if correct else "Review this concept in the lesson.",
            "bloom_level": question.get("bloom_level", "remember"),
            "gap_tags": [] if correct else [question.get("bloom_level", "understanding")],
        }

    def _fallback_eval(self, question, user_answer):
        correct = user_answer.strip().lower() == question.get("correct_answer", "").strip().lower()
        return {
            "correct": correct, "score": 5 if correct else 1,
            "feedback": "Correct!" if correct else "Incorrect.",
            "explanation": question.get("explanation", ""),
            "misconception": "", "bloom_level": "remember", "gap_tags": [],
        }

    def _validate(self, result, question):
        result.setdefault("correct", False)
        result.setdefault("score", 0)
        result.setdefault("feedback", "")
        result.setdefault("explanation", question.get("explanation", ""))
        result.setdefault("misconception", "")
        result.setdefault("bloom_level", question.get("bloom_level", "remember"))
        result.setdefault("gap_tags", [])
        result["score"] = max(0, min(5, int(result.get("score", 0))))
        return result
