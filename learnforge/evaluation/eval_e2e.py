#!/usr/bin/env python3
"""End-to-end evaluation: full pipeline from curriculum → lesson → quiz → evaluate."""
import sys, os, json, csv, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["LEARNFORGE_MODE"] = "demo"
logging.basicConfig(level=logging.INFO)

from src.config import PROJECT_ROOT
from src.orchestrator.graph import run_pipeline


def test_full_pipeline():
    """Run full learning pipeline: curriculum → lesson → quiz → evaluate."""
    results = []

    print("Step 1: Generate curriculum")
    state = run_pipeline(action="CURRICULUM", topic="Machine Learning", level="intermediate")
    curriculum = state.get("curriculum", {})
    assert curriculum and curriculum.get("modules"), "Curriculum generation failed"
    results.append({"step": "curriculum", "passed": True, "details": f"{len(curriculum['modules'])} modules"})
    print(f"  ✅ {len(curriculum['modules'])} modules generated")

    module = curriculum["modules"][0]

    print("Step 2: Generate lesson")
    state = run_pipeline(action="LESSON", topic="Machine Learning", level="intermediate", active_module=module)
    lesson = state.get("lesson", {})
    assert lesson and lesson.get("sections"), "Lesson generation failed"
    results.append({"step": "lesson", "passed": True, "details": f"{len(lesson['sections'])} sections"})
    print(f"  ✅ {len(lesson['sections'])} sections generated")

    print("Step 3: Generate quiz")
    state = run_pipeline(action="QUIZ", topic="Machine Learning", level="intermediate", active_module=module)
    quiz = state.get("quiz", {})
    assert quiz and quiz.get("questions"), "Quiz generation failed"
    results.append({"step": "quiz", "passed": True, "details": f"{len(quiz['questions'])} questions"})
    print(f"  ✅ {len(quiz['questions'])} questions generated")

    print("Step 4: Evaluate answer (correct)")
    q = quiz["questions"][0]
    state = run_pipeline(
        action="EVALUATE", topic="Machine Learning", level="intermediate",
        question=q, user_answer=q.get("correct_answer", ""))
    evaluation = state.get("evaluation", {})
    assert evaluation, "Evaluation failed"
    assert evaluation.get("correct") is True, f"Correct answer was marked wrong: {evaluation}"
    results.append({"step": "evaluate_correct", "passed": True, "details": f"score={evaluation.get('score')}"})
    print(f"  ✅ Correct answer scored {evaluation.get('score')}/5")

    print("Step 5: Evaluate answer (incorrect)")
    state = run_pipeline(
        action="EVALUATE", topic="Machine Learning", level="intermediate",
        question=q, user_answer="completely wrong answer xyz")
    evaluation = state.get("evaluation", {})
    assert evaluation, "Evaluation failed"
    assert evaluation.get("correct") is False, "Wrong answer was marked correct"
    results.append({"step": "evaluate_incorrect", "passed": True, "details": f"score={evaluation.get('score')}"})
    print(f"  ✅ Incorrect answer scored {evaluation.get('score')}/5")

    print("Step 6: Generate flashcards")
    state = run_pipeline(action="FLASHCARD", topic="Machine Learning", level="intermediate", active_module=module)
    flashcards = state.get("flashcards", {})
    assert flashcards and flashcards.get("cards"), "Flashcard generation failed"
    results.append({"step": "flashcards", "passed": True, "details": f"{len(flashcards['cards'])} cards"})
    print(f"  ✅ {len(flashcards['cards'])} flashcards generated")

    print("Step 7: Get recommendations")
    state = run_pipeline(
        action="RECOMMEND", topic="Machine Learning", level="intermediate",
        knowledge_gaps=["neural_networks", "overfitting"])
    recs = state.get("recommendations", {})
    assert recs and recs.get("recommendations"), "Recommendations failed"
    results.append({"step": "recommend", "passed": True, "details": f"{len(recs['recommendations'])} recommendations"})
    print(f"  ✅ {len(recs['recommendations'])} recommendations generated")

    return results


def main():
    print("=" * 50)
    print("LearnForge — End-to-End Pipeline Evaluation")
    print("=" * 50)

    results = test_full_pipeline()

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} steps passed")

    out_dir = PROJECT_ROOT / "evaluation" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "e2e_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["step", "passed", "details"])
        w.writeheader()
        w.writerows(results)
    print(f"✅ Results saved to {out_dir}/e2e_eval.csv")


if __name__ == "__main__":
    main()
