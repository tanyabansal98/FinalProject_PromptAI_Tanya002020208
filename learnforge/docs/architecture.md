# LearnForge Architecture

## System Overview

LearnForge is a multi-agent personalized learning platform with three AI agents orchestrated via a LangGraph state machine.

## Agent Architecture

### Agent 1: Curriculum Architect (`src/agents/curriculum_architect.py`)
- **Input:** Topic + level (beginner/intermediate/advanced)
- **Output:** Structured curriculum with modules, Bloom's taxonomy levels, prerequisites, time estimates
- **Model:** GPT-4o-mini (API mode) / Ollama (local mode) / Pre-generated JSON (demo mode)

### Agent 2: Content Generator (`src/agents/content_generator.py`)
- **Input:** Module from Agent 1's curriculum
- **Output:** Lessons, quizzes, flashcards in structured JSON format
- **Model:** Fine-tuned Llama-3.2-3B (QLoRA) with GPT-4o-mini fallback
- **Fine-tuning:** Instruction-tuned on 180 educational content examples

### Agent 3: Adaptive Assessor (`src/agents/adaptive_assessor.py`)
- **Input:** Quiz question + user answer + RAG-retrieved reference documents
- **Output:** Score (0-5), feedback, misconception detection, knowledge gap tags
- **Model:** GPT-4o-mini with RAG context injection

## LangGraph Orchestrator (`src/orchestrator/graph.py`)

The orchestrator is a compiled state machine with 7 nodes and conditional routing:

```
Action = CURRICULUM → curriculum_node → END
Action = LESSON     → lesson_node → END
Action = QUIZ       → quiz_node → END
Action = FLASHCARD  → flashcard_node → END
Action = EVALUATE   → retrieve_node (RAG) → evaluate_node (Assessor) → END
Action = RECOMMEND  → recommend_node → END
```

Key design: The EVALUATE action routes through RAG retrieval BEFORE the assessor scores, ensuring all feedback is grounded in reference material.

## RAG Pipeline (`src/rag/`)

```
Query (topic + question + user answer)
    ↓ Hybrid Retrieval
    ├── Dense: ChromaDB cosine similarity (BGE-small-en-v1.5)
    └── Sparse: BM25 keyword matching
    ↓ Reciprocal Rank Fusion (k=60)
    ↓ Cross-Encoder Reranking (BGE-reranker-base) → Top 3
    ↓ Injected into Assessor prompt
```

Corpus: 30 markdown documents across 4 categories (pedagogy, subjects, misconceptions, Bloom's taxonomy).

## Multimodal (`src/content/multimodal.py`)

- **Image Generation:** DALL-E 3 (API mode) or SVG placeholder diagrams (demo/Ollama mode)
- **Text-to-Speech:** OpenAI TTS API (API mode) or browser-native SpeechSynthesis (demo/Ollama mode)

## Three Modes (`src/agents/base.py`)

| Mode | LLM | Images | TTS | Cost |
|------|-----|--------|-----|------|
| Demo | Pre-generated JSON files | SVG placeholders | Browser native | $0 |
| API | GPT-4o-mini via OpenAI | DALL-E 3 | OpenAI TTS | ~$0.01/interaction |
| Ollama | Local models (llama3, mistral) | SVG placeholders | Browser native | $0 |

## Data Storage

| Component | Technology | Location |
|-----------|-----------|----------|
| User progress | SQLite | `learnforge.db` |
| Vector embeddings | ChromaDB | `chroma_db/` |
| Generated content | JSON files | `data/generated/` |
| RAG corpus | Markdown files | `data/corpus/` |
| Fine-tuned weights | LoRA adapter | `models/lora_adapter/` |
