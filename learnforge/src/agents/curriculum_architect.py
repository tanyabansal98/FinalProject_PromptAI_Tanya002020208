"""Agent 1 — Curriculum Architect: Breaks topics into structured learning paths."""
import json
import logging
from pathlib import Path
from src.agents.base import call_llm, get_mode
from src.config import DEMO_DATA_DIR

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "curriculum_system.txt").read_text()


class CurriculumArchitect:
    """Generates structured curricula from a topic + level."""

    def generate_curriculum(self, topic: str, level: str, num_modules: int = 5) -> dict:
        """
        Generate a full curriculum.
        Returns: {topic, level, modules: [{id, title, description, objectives, prerequisites, bloom_level, estimated_minutes}]}
        """
        mode = get_mode()
        if mode == "demo":
            return self._load_demo(topic, level)

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\nLevel: {level}\nNumber of modules: {num_modules}\n\nGenerate a structured curriculum."},
        ]
        result = call_llm(messages, temperature=0.7)

        if isinstance(result, dict) and "_error" in result:
            logger.error(f"Curriculum generation failed: {result['_error']}")
            return self._fallback(topic, level)

        # Validate
        if "modules" not in result:
            result = self._fallback(topic, level)

        result["topic"] = topic
        result["level"] = level
        return result

    def _load_demo(self, topic: str, level: str) -> dict:
        """Load pre-generated demo curriculum."""
        demo_file = DEMO_DATA_DIR / f"curriculum_{topic.lower().replace(' ', '_')}.json"
        if demo_file.exists():
            return json.loads(demo_file.read_text())
        # Generic demo
        demo_file = DEMO_DATA_DIR / "curriculum_demo.json"
        if demo_file.exists():
            data = json.loads(demo_file.read_text())
            data["topic"] = topic
            data["level"] = level
            return data
        return self._fallback(topic, level)

    def _fallback(self, topic: str, level: str) -> dict:
        return {
            "topic": topic,
            "level": level,
            "description": f"A comprehensive {level}-level course on {topic}.",
            "modules": [
                {"id": f"m{i+1}", "title": f"Module {i+1}: {t}", "description": f"Learn about {t} in {topic}.",
                 "objectives": [f"Understand core concepts of {t}", f"Apply {t} in practice"],
                 "prerequisites": [] if i == 0 else [f"m{i}"],
                 "bloom_level": ["remember", "understand", "apply", "analyze", "evaluate"][min(i, 4)],
                 "estimated_minutes": 20 + i * 5}
                for i, t in enumerate(["Foundations", "Core Concepts", "Practical Applications", "Advanced Topics", "Mastery & Review"])
            ],
        }
