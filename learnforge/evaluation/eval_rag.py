#!/usr/bin/env python3
"""Evaluate RAG retrieval quality."""
import sys, os, json, csv, math, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import CHROMA_DIR, PROJECT_ROOT
logging.basicConfig(level=logging.INFO)

TEST_QUERIES = [
    {"query": "bloom's taxonomy levels cognitive", "relevant": ["blooms_taxonomy", "remember_level", "understand_level"]},
    {"query": "spaced repetition flashcard review", "relevant": ["spaced_repetition", "retrieval_practice"]},
    {"query": "machine learning supervised unsupervised", "relevant": ["machine_learning_fundamentals"]},
    {"query": "neural network backpropagation CNN", "relevant": ["neural_networks_basics"]},
    {"query": "active learning pedagogy techniques", "relevant": ["active_learning", "formative_assessment"]},
    {"query": "cognitive load instructional design", "relevant": ["cognitive_load_theory", "scaffolding"]},
    {"query": "model evaluation accuracy precision recall", "relevant": ["model_evaluation_metrics"]},
    {"query": "common misconceptions ML understanding", "relevant": ["ml_misconceptions", "misconception_driven_learning"]},
    {"query": "zone proximal development scaffolding", "relevant": ["zone_of_proximal_development", "scaffolding"]},
    {"query": "constructive alignment assessment objectives", "relevant": ["constructive_alignment", "formative_assessment"]},
]

def precision_at_k(retrieved, relevant, k=5):
    return sum(1 for r in retrieved[:k] if any(rel in r for rel in relevant)) / k

def mrr(retrieved, relevant):
    for i, r in enumerate(retrieved):
        if any(rel in r for rel in relevant):
            return 1.0 / (i + 1)
    return 0.0

def main():
    from src.rag.retrieve import HybridRetriever
    retriever = HybridRetriever()

    results = []
    for method in ["dense", "bm25", "hybrid"]:
        p5s, mrrs = [], []
        for tq in TEST_QUERIES:
            docs = retriever.retrieve(tq["query"], top_k=5, method=method)
            ids = [d.get("id", "") for d in docs]
            p5s.append(precision_at_k(ids, tq["relevant"]))
            mrrs.append(mrr(ids, tq["relevant"]))
        results.append({"config": method, "p@5": sum(p5s)/len(p5s), "mrr": sum(mrrs)/len(mrrs)})
        print(f"{method}: P@5={results[-1]['p@5']:.3f} MRR={results[-1]['mrr']:.3f}")

    out = PROJECT_ROOT / "evaluation" / "results" / "rag_ablation.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["config", "p@5", "mrr"])
        w.writeheader()
        w.writerows(results)
    print(f"✅ Saved to {out}")

if __name__ == "__main__":
    main()
