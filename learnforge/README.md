# 🔥 LearnForge — Personalized AI Learning Content Creator

An AI-powered learning platform that generates **structured lessons, interactive quizzes, flashcards, and adaptive study plans** for any topic — powered by multi-agent orchestration, RAG, and a fine-tuned LLM.

## Three Modes — Zero to Full Power

| Mode | API Key? | What it does |
|------|----------|-------------|
| 🎭 **Demo** | No | Uses pre-generated content. Perfect for demos and testing. |
| 🔑 **API** | OpenAI key | Real-time generation via GPT-4o-mini |
| 🦙 **Ollama** | No | Uses local Ollama models (llama3, mistral) — fully offline |

## Quick Start

```bash
git clone https://github.com/tanyabansal98/learnforge.git
cd learnforge
pip install -e .
make index       # Build RAG vector store (local, free)
make demo        # Launch in demo mode — no API key needed
```

For API mode: `cp .env.example .env`, add your key, run `make run`.

## Architecture

Three AI agents orchestrated via a state machine:

1. **Curriculum Architect** — Breaks any topic into structured modules with Bloom's Taxonomy progression
2. **Content Generator** — Creates lessons, quizzes, flashcards (fine-tuned Llama-3.2-3B or GPT-4o-mini)
3. **Adaptive Assessor** — Evaluates answers with RAG-grounded feedback, identifies knowledge gaps

**RAG Pipeline:** 30+ pedagogy/subject reference docs → ChromaDB + BM25 hybrid retrieval → BGE cross-encoder reranking

**Data Storage:** SQLite (progress tracking) + ChromaDB (vectors) + JSON files (cached content)

## Features

- 📚 **Curriculum generation** with Bloom's Taxonomy progression chart
- 📖 **Rich lessons** with key concepts, examples, and takeaways
- 🧪 **Interactive quizzes** with multiple question types, instant scoring, misconception detection
- 🃏 **Flashcards** with spaced repetition and confidence rating
- 📊 **Dashboard** with radar charts, score trends, knowledge gap heatmap, study streaks
- 🔄 **Adaptive difficulty** — system learns your weak spots

## Fine-Tuning

Training data (144 examples) is pre-built. Upload to Google Colab:

```python
!pip install -q transformers peft trl bitsandbytes accelerate datasets pyyaml
import os; os.environ["HF_TOKEN"] = "hf_..."
!python train_lora.py
```

## Author

**Tanya Bansal** — MS Information Systems, Northeastern University
