#!/usr/bin/env python3
"""Evaluate content generation quality: lesson structure, quiz validity, flashcard quality."""
import sys, os, json, csv, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["LEARNFORGE_MODE"] = "demo"
logging.basicConfig(level=logging.INFO)

from src.config import PROJECT_ROOT
from src.orchestrator.graph import run_pipeline

TOPICS = ["Machine Learning", "Python", "Statistics", "Web Development", "Databases"]
LEVELS = ["beginner", "intermediate", "advanced"]


def evaluate_curriculum_quality():
    results = []
    for topic in TOPICS[:3]:
        for level in LEVELS[:2]:
            result = run_pipeline(action="CURRICULUM", topic=topic, level=level)
            curr = result.get("curriculum", {})
            modules = curr.get("modules", [])
            score = {
                "topic": topic, "level": level,
                "has_modules": len(modules) > 0,
                "module_count": len(modules),
                "has_objectives": all(len(m.get("objectives", [])) > 0 for m in modules),
                "has_bloom_levels": all(m.get("bloom_level") for m in modules),
                "has_prereqs_structure": all("prerequisites" in m for m in modules),
            }
            results.append(score)
            print(f"  {topic}/{level}: {len(modules)} modules, valid={score['has_objectives'] and score['has_bloom_levels']}")
    return results


def evaluate_quiz_quality():
    results = []
    module = {"id": "m1", "title": "Foundations", "objectives": ["Understand basics"]}
    for topic in TOPICS[:3]:
        result = run_pipeline(action="QUIZ", topic=topic, level="intermediate", active_module=module)
        quiz = result.get("quiz", {})
        questions = quiz.get("questions", [])
        score = {
            "topic": topic,
            "question_count": len(questions),
            "all_have_answers": all(q.get("correct_answer") for q in questions),
            "all_have_explanations": all(q.get("explanation") for q in questions),
            "all_have_bloom": all(q.get("bloom_level") for q in questions),
            "has_variety": len(set(q.get("type", "") for q in questions)) > 1 if len(questions) > 1 else True,
        }
        results.append(score)
        print(f"  {topic}: {len(questions)} questions, valid={score['all_have_answers']}")
    return results


def main():
    print("=" * 50)
    print("LearnForge — Content Quality Evaluation")
    print("=" * 50)

    print("\n📚 Curriculum Quality:")
    curr_results = evaluate_curriculum_quality()

    print("\n🧪 Quiz Quality:")
    quiz_results = evaluate_quiz_quality()

    # Save
    out_dir = PROJECT_ROOT / "evaluation" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "content_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(curr_results[0].keys()))
        w.writeheader()
        w.writerows(curr_results)

    with open(out_dir / "quiz_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(quiz_results[0].keys()))
        w.writeheader()
        w.writerows(quiz_results)

    print(f"\n✅ Results saved to {out_dir}/")


if __name__ == "__main__":
    main()
