# 🔥 LearnForge — Personalized AI Learning Content Creator

> **Course:** INFO 7375 — Prompt Engineering and Generative AI  
> **Instructor:** Professor Nick Bear Brown  
> **University:** Northeastern University  
> **Author:** Tanya Bansal  
> **NUID:** 002020208  
> **Semester:** Spring 2026

---

## 📖 Project Description

LearnForge is a **multi-agent AI-powered personalized learning platform** that generates complete learning packages for any topic. Users enter a topic (e.g., "Machine Learning", "Kubernetes", "Photosynthesis"), select their level, and the system produces:

- A **structured curriculum** with Bloom's Taxonomy cognitive progression
- **Rich lessons** with concept diagrams and audio narration
- **Interactive quizzes** with instant scoring, misconception detection, and RAG-grounded feedback
- **Spaced-repetition flashcards** with confidence tracking
- A **progress dashboard** with radar charts, score trends, knowledge gap analysis, and study streaks

The system uses **three AI agents** orchestrated via a **LangGraph state machine**, a **RAG pipeline** for grounded assessment, a **fine-tuned LLM** for content generation, and **multimodal capabilities** (image generation + text-to-speech).

### What Makes This Project Unique

- **Multi-agent orchestration** — not a single LLM call, but three specialized agents passing state through a compiled graph
- **Three runtime modes** — Demo (zero cost), API (OpenAI), Ollama (local) — switchable from the UI sidebar
- **Adaptive learning loop** — quiz results feed back into the system to identify and target knowledge gaps
- **RAG-grounded assessment** — the evaluator can't hallucinate feedback; it must cite retrieved reference documents
- **User data ingestion** — upload your own study materials (PDF, TXT, MD) into the RAG knowledge base

---

## 🏆 Rubric Components (5 of 6)

| Component | Implementation | Location in Code |
|-----------|---------------|-----------------|
| **1. Prompt Engineering** | 5 system prompts with strict JSON schemas, Bloom's taxonomy constraints, misconception-based distractors, RAG citation requirements, graceful fallbacks | `src/agents/prompts/*.txt` |
| **2. Fine-Tuning** | QLoRA fine-tuning of Qwen2.5-3B-Instruct on 180 educational content examples. LoRA rank 16, 3 epochs, eval loss 0.609→0.234 | `src/finetuning/`, `data/processed/` |
| **3. RAG** | 30-doc knowledge base → ChromaDB + BM25 hybrid retrieval → Reciprocal Rank Fusion → BGE cross-encoder reranking → top 3 docs injected into assessor | `src/rag/`, `data/corpus/` |
| **4. Multimodal** | DALL-E 3 image generation (API) / SVG concept diagrams (demo) + OpenAI TTS audio (API) / browser SpeechSynthesis (demo) | `src/content/multimodal.py` |
| **5. Synthetic Data** | 180 instruction-tuned training examples generated across 20 topics × 3 levels × 3 content types (lessons, quizzes, flashcards) | `data/processed/*.jsonl` |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (7 pages)                     │
│  Home │ Curriculum │ Lesson │ Quiz │ Flashcards │ Dashboard │ Data Manager │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator (State Machine)           │
│  Routes: CURRICULUM │ LESSON │ QUIZ │ FLASHCARD │ EVALUATE │ RECOMMEND  │
└───────┬──────────────────┬──────────────────┬───────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Agent 1     │  │     Agent 2       │  │     Agent 3       │
│  Curriculum   │  │    Content        │  │    Adaptive       │
│  Architect    │  │    Generator      │  │    Assessor       │
│  (GPT-4o-mini)│  │  (Fine-tuned /   │  │  (GPT-4o-mini    │
│               │  │   API fallback)   │  │   + RAG context)  │
└──────┬───────┘  └────────┬─────────┘  └────────┬─────────┘
       │                   │                      │
       │                   │                      ▼
       │                   │            ┌──────────────────┐
       │                   │            │   RAG Pipeline     │
       │                   │            │  ChromaDB + BM25   │
       │                   │            │  Hybrid + Reranker │
       │                   │            └────────┬─────────┘
       │                   │                     │
       ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                       │
│  ChromaDB (vectors) │ SQLite (scores) │ JSON (content) │ Corpus (30 .md) │
└─────────────────────────────────────────────────────────────┘
```

### Three Agents

| Agent | Model | Input | Output |
|-------|-------|-------|--------|
| **Curriculum Architect** | GPT-4o-mini | Topic + level | Structured module plan with Bloom's taxonomy levels, prerequisites, time estimates |
| **Content Generator** | Fine-tuned Qwen2.5-3B / GPT-4o-mini fallback | Module from Agent 1 | Lessons (sections, key concepts, examples), quizzes (MCQ, T/F, short answer), flashcards |
| **Adaptive Assessor** | GPT-4o-mini + RAG context | Quiz answer + retrieved docs | Score (0-5), feedback, misconception detection, knowledge gap tags |

### RAG Pipeline

```
User submits quiz answer
    ↓
Build query: topic + question + user answer
    ↓
Dense retrieval (ChromaDB/BGE-small) → top 10
BM25 keyword retrieval → top 10
    ↓
Reciprocal Rank Fusion (k=60) → merged top 10
    ↓
BGE cross-encoder reranker → top 3
    ↓
Injected into Assessor prompt as REFERENCE MATERIAL
    ↓
Assessor scores answer with citations from retrieved docs
```

### Three Runtime Modes

| Mode | LLM | Images | TTS | Cost |
|------|-----|--------|-----|------|
| 🎭 **Demo** | Pre-generated JSON | SVG diagrams | Browser speech | $0 |
| 🔑 **API** | GPT-4o-mini (OpenAI) | DALL-E 3 | OpenAI TTS | ~$0.01/interaction |
| 🦙 **Ollama** | Local models (llama3, mistral) | SVG diagrams | Browser speech | $0 |

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or 3.11
- pip

### Step 1: Clone and Setup

```bash
git clone https://github.com/tanyabansal98/learnforge.git
cd learnforge
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

For **Demo mode** (default): no edits needed.

For **API mode**: add your OpenAI key to `.env`:
```
LEARNFORGE_MODE=api
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Build RAG Index

```bash
make index
```

This reads the 30 corpus markdown files, chunks them, embeds with BGE-small, and stores vectors in ChromaDB. **No API calls. Free. Takes ~30 seconds.**

### Step 4: Run the Application

```bash
make demo        # Demo mode (no API key needed)
# OR
make run         # Uses whatever mode is set in .env
```

Open **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
learnforge/
├── app/                              # Streamlit UI
│   ├── streamlit_app.py              # Home page + mode switcher
│   └── pages/
│       ├── 1_Curriculum.py           # Module cards + Bloom's chart
│       ├── 2_Lesson.py               # Lessons + concept image + TTS
│       ├── 3_Quiz_Arena.py           # Interactive quiz + scoring
│       ├── 4_Flashcards.py           # Flip cards + confidence
│       ├── 5_Dashboard.py            # 4-tab analytics dashboard
│       └── 6_Data_Manager.py         # Upload, browse, export
├── src/
│   ├── config.py                     # Central configuration
│   ├── agents/
│   │   ├── base.py                   # Unified LLM backend (demo/api/ollama)
│   │   ├── curriculum_architect.py   # Agent 1
│   │   ├── content_generator.py      # Agent 2 (with fine-tune support)
│   │   ├── adaptive_assessor.py      # Agent 3 (with RAG)
│   │   └── prompts/                  # 5 system prompt files
│   ├── orchestrator/
│   │   └── graph.py                  # LangGraph state machine (7 nodes)
│   ├── rag/
│   │   ├── ingest.py                 # Chunk + embed + ChromaDB
│   │   └── retrieve.py              # Hybrid retrieval + reranker
│   ├── content/
│   │   ├── multimodal.py             # Image gen (DALL-E/SVG) + TTS
│   │   └── manager.py               # File upload, export, persistence
│   ├── profile/
│   │   └── storage.py               # SQLite: scores, gaps, streaks
│   └── finetuning/
│       ├── train_lora.py             # Colab training script
│       ├── inference.py              # LoRA adapter loader (CUDA/MPS/CPU)
│       └── configs/qlora_3b.yaml     # Hyperparameters
├── data/
│   ├── corpus/                       # 30 RAG documents (pre-built)
│   │   ├── pedagogy/                 # 10 files (Bloom's, spaced repetition, etc.)
│   │   ├── subjects/                 # 10 files (ML, Python, stats, etc.)
│   │   ├── misconceptions/           # 4 files (common errors by subject)
│   │   └── blooms/                   # 6 files (one per taxonomy level)
│   ├── processed/                    # Fine-tuning data (pre-built)
│   │   ├── train.jsonl               # 144 training examples
│   │   ├── val.jsonl                 # 18 validation examples
│   │   └── test.jsonl                # 18 test examples
│   └── generated/                    # Auto-saved content (runtime)
├── demo_data/                        # Pre-generated content for demo mode
│   ├── curriculum_demo.json          # Machine Learning curriculum
│   ├── lessons.json                  # Pre-written lessons
│   ├── quizzes.json                  # Pre-written quizzes
│   ├── flashcards.json               # Pre-written flashcards
│   └── upload_samples/               # 4 sample files for upload demo
├── models/lora_adapter/              # Fine-tuned weights (from Colab)
├── chroma_db/                        # ChromaDB vector store (built by make index)
├── learnforge.db                     # SQLite database (runtime)
├── evaluation/                       # Evaluation scripts
│   ├── eval_rag.py                   # RAG ablation (dense vs BM25 vs hybrid)
│   ├── eval_content.py               # Content quality metrics
│   └── eval_e2e.py                   # End-to-end pipeline test
├── tests/                            # Unit tests
│   ├── test_agents.py                # Agent smoke tests
│   ├── test_storage_rag.py           # Storage + RAG tests
│   └── test_orchestrator.py          # Orchestrator pipeline tests
├── docs/                             # Documentation
│   ├── architecture.md
│   ├── prompt_engineering.md
│   ├── rag_design.md
│   ├── finetuning_report.md
│   └── ethics.md
├── SETUP_GUIDE.md                    # Detailed setup + usage guide
├── pyproject.toml                    # Dependencies
├── Makefile                          # Shortcut commands
└── .env.example                      # Environment template
```

### Where Data Is Stored

| What | Where | When Created |
|------|-------|-------------|
| RAG corpus (reference docs) | `data/corpus/*.md` | Pre-built (30 files) + your uploads |
| Vector embeddings | `chroma_db/` | When you run `make index` |
| Demo content | `demo_data/*.json` | Pre-built (5 files) |
| Fine-tuning training data | `data/processed/*.jsonl` | Pre-built (180 examples) |
| Generated content | `data/generated/` | When you use the app (auto-saved) |
| Quiz scores & progress | `learnforge.db` | When you take quizzes |
| Fine-tuned model weights | `models/lora_adapter/` | After Colab training |

---

## 🧠 Fine-Tuning

### Training Data

180 pre-built instruction-tuning examples across 20 topics × 3 levels × 3 content types. Located in `data/processed/`. **No API cost to generate — already included.**

### Training on Google Colab

1. Open [Google Colab](https://colab.research.google.com) → New Notebook → Runtime → Change runtime type → **T4 or A100 GPU**

2. Upload 4 files: `train.jsonl`, `val.jsonl`, `train_lora.py`, `qlora_3b.yaml`

3. Run these cells:

```python
# Cell 1: Install
!pip install -q transformers peft accelerate datasets pyyaml

# Cell 2: Fix paths
import yaml
with open("qlora_3b.yaml") as f:
    cfg = yaml.safe_load(f)
cfg["data"]["train_path"] = "train.jsonl"
cfg["data"]["val_path"] = "val.jsonl"
cfg["training"]["output_dir"] = "./lora_adapter"
with open("qlora_3b.yaml", "w") as f:
    yaml.dump(cfg, f)

# Cell 3: Train (uses basic Trainer, no bitsandbytes needed)
# See train_final.py for the A100-compatible version without quantization
!python train_lora.py
```

4. Download the `lora_adapter/` folder → place in `models/lora_adapter/`

5. Set `USE_FINETUNED=true` in `.env`

### Training Results

| Metric | Value |
|--------|-------|
| Base model | Qwen2.5-3B-Instruct |
| Method | LoRA (r=16, α=32) |
| Trainable params | 7.37M / 3.09B (0.24%) |
| Epochs | 3 |
| Eval loss | 0.609 → 0.313 → 0.234 |
| Training time | ~2.5 min (A100) |

---

## 📊 Features & Screenshots

### Home Page
- Topic input + level selector
- Mode switcher (Demo / API / Ollama) in sidebar
- Data storage overview in sidebar
- Navigation cards to all features

### Curriculum Page
- 5 modules with Bloom's Taxonomy progression chart (Plotly)
- Expandable module cards with objectives, prerequisites, difficulty badges
- Progress bars per module
- "Read Lesson" / "Take Quiz" / "Flashcards" buttons per module

### Lesson Viewer
- Auto-generated **concept diagram** (SVG in demo, DALL-E in API mode) — **Multimodal**
- **Text-to-speech** audio narration — **Multimodal**
- Rich formatted sections with key concept callouts
- Examples in expandable sections
- Summary + key takeaways

### Quiz Arena
- Multiple question types: MCQ, True/False, Short Answer
- Each question tagged with Bloom's level + difficulty
- Submit → instant scoring (score/25)
- Per-question feedback with explanations
- Misconception detection
- Results saved to SQLite → feeds Dashboard

### Flashcards
- Flip-card UI with gradient styling
- Hint button (shows hint without flipping)
- Confidence rating: "Didn't know" / "Kinda knew" / "Knew it!"
- Mastery percentage tracker
- Spaced repetition progress saved to SQLite

### Progress Dashboard
- **Bloom's Taxonomy radar chart** — performance at each cognitive level
- **Score trends line chart** — daily average scores over time
- **Knowledge gaps heatmap** — most-flagged weak concepts
- **Activity tracker** — study days, streaks, daily question counts
- Shows sample visualization data when no quizzes taken yet

### Data Manager
- **Upload tab**: Drag PDF, TXT, MD, CSV files → ingested into RAG corpus
- **RAG Corpus tab**: Browse all 30+ corpus files by category
- **Generated Content tab**: Browse auto-saved curricula, lessons, quizzes
- **Export tab**: Download curriculum (.md), quiz (.csv), flashcards (.csv for Anki import), progress report (.md)
- Storage metrics: corpus file count, ChromaDB status, SQLite size

---

## 🧪 Evaluation

```bash
make eval
```

Runs three evaluation scripts:

| Script | What It Tests |
|--------|--------------|
| `eval_rag.py` | RAG retrieval quality: dense vs BM25 vs hybrid on 10 test queries |
| `eval_content.py` | Curriculum + quiz structure validity across topics/levels |
| `eval_e2e.py` | Full pipeline: curriculum → lesson → quiz → evaluate → recommend (7 steps) |

Results saved to `evaluation/results/`.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | GPT-4o-mini (OpenAI) / Qwen2.5-3B (fine-tuned) / Ollama (local) |
| Orchestration | LangGraph (state machine with 7 nodes) |
| RAG | ChromaDB + BM25 + BGE-small embeddings + BGE cross-encoder reranker |
| Fine-tuning | LoRA via PEFT + HuggingFace Transformers on Google Colab |
| Image generation | DALL-E 3 (API) / Programmatic SVG (demo) |
| Text-to-speech | OpenAI TTS (API) / Browser SpeechSynthesis (demo) |
| Frontend | Streamlit (7 pages) |
| Visualizations | Plotly (radar charts, line charts, heatmaps, bar charts) |
| Vector database | ChromaDB (persistent, cosine similarity) |
| User database | SQLite (quiz scores, knowledge gaps, streaks, flashcard progress) |
| File storage | JSON files (auto-saved generated content) |

---

## 📜 Ethics & Responsible AI

- **Privacy**: All data stored locally. Demo/Ollama modes send zero data externally.
- **Transparency**: Three modes clearly labeled. All generated content inspectable as JSON. RAG citations show source documents.
- **Fairness**: Bloom's taxonomy ensures objective assessment. Adaptive difficulty based on performance, not assumptions.
- **Limitations**: AI-generated content may contain errors. Not a substitute for expert instruction. Fine-tuned model is small (3B params).

See `docs/ethics.md` for full details.

---

## 📚 Documentation

| Document | Description |
|----------|------------|
| [`SETUP_GUIDE.md`](SETUP_GUIDE.md) | Complete step-by-step setup, all modes, troubleshooting |
| [`docs/architecture.md`](docs/architecture.md) | System architecture, agent design, data flow |
| [`docs/prompt_engineering.md`](docs/prompt_engineering.md) | All 5 prompts explained with design rationale |
| [`docs/rag_design.md`](docs/rag_design.md) | RAG pipeline, corpus design, hybrid retrieval |
| [`docs/finetuning_report.md`](docs/finetuning_report.md) | Training data, model config, results |
| [`docs/ethics.md`](docs/ethics.md) | Privacy, fairness, limitations |

---

## 👤 Author | NUID: 002020208

**Tanya Bansal**  
MS in Information Systems, Northeastern University  
[GitHub](https://github.com/tanyabansal98) · [LinkedIn](https://linkedin.com/in/tanyabansal28) · [Portfolio](https://tanyabansal98.github.io)  
Email: bansal.t@northeastern.edu

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
