# RAG Design in LearnForge

## Pipeline

```
Corpus (30 markdown files across 4 categories)
    ↓ RecursiveCharacterTextSplitter (300 tokens, 50 overlap)
Chunks
    ↓ BGE-small-en-v1.5 embeddings
ChromaDB (persistent, cosine similarity)
    ↓ (at query time)
Query → Hybrid Retrieval (Dense + BM25 + RRF) → Reranker → Top 3 → Assessor
```

## Corpus

| Category | Files | Content |
|----------|-------|---------|
| `pedagogy/` | 10 | Bloom's taxonomy, spaced repetition, active learning, scaffolding, cognitive load theory, etc. |
| `subjects/` | 10 | ML fundamentals, neural networks, Python, statistics, databases, web dev, etc. |
| `misconceptions/` | 4 | Common misconceptions in ML, programming, statistics, web development |
| `blooms/` | 6 | One file per Bloom's level with question stems, assessment types, examples |

Each document follows a consistent structure: definition, key concepts, application guidance, common pitfalls.

## User Uploads

Users can upload their own study materials (PDF, TXT, MD, CSV) via the Data Manager page. Files are saved as markdown in `data/corpus/{category}/` and indexed into ChromaDB after running `make index`. This means the assessor can cite the user's own notes when grading.

## Hybrid Retrieval

Dense (semantic) + BM25 (keyword) combined via Reciprocal Rank Fusion:
```
RRF_score(doc) = 1/(k + rank_dense) + 1/(k + rank_bm25)
```
where k=60. This captures both semantic meaning and exact terminology.

## Cross-Encoder Reranking

After RRF produces top-10 candidates, BGE-reranker-base rescores each (query, document) pair. Top 3 are passed to the assessor.

## How RAG Is Used

The EVALUATE action in the orchestrator routes through `retrieve_node` before `evaluate_node`:
1. Build query from topic + question text + user answer
2. Hybrid retrieve top 10
3. Rerank to top 3
4. Inject into assessor prompt as "REFERENCE MATERIAL"
5. Assessor must cite these documents in feedback

## Evaluation

`evaluation/eval_rag.py` tests dense vs BM25 vs hybrid on 10 test queries with labeled relevant documents. Results saved to `evaluation/results/rag_ablation.csv`.
