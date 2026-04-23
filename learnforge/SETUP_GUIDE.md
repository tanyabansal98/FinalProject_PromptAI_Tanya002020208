# LearnForge — Complete Setup & Usage Guide

## Table of Contents
1. Prerequisites
2. Installation (Step by Step)
3. Running in Demo Mode (Zero Cost)
4. Running in API Mode (OpenAI)
5. Running in Ollama Mode (Local, Free)
6. Using the Application (Every Feature)
7. Uploading Your Own Study Materials
8. Fine-Tuning on Google Colab
9. Running Evaluations
10. Project Structure Explained
11. Troubleshooting

---

## 1. Prerequisites

You need:
- **Python 3.10 or 3.11** (not 3.12+ — some dependencies don't support it yet)
- **pip** (comes with Python)
- **Terminal / Command Line**

Check your Python version:
```bash
python3 --version
# Should show 3.10.x or 3.11.x
```

---

## 2. Installation (Step by Step)

### Step 2.1: Extract the project
```bash
tar xzf learnforge.tar.gz
cd learnforge
```

### Step 2.2: Create a virtual environment
```bash
python3 -m venv .venv
```

### Step 2.3: Activate the virtual environment

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 2.4: Install dependencies
```bash
pip install -e .
```

This installs all required packages: streamlit, openai, chromadb, plotly, etc.

### Step 2.5: Set up environment file
```bash
cp .env.example .env
```

For **demo mode**, you don't need to edit this file at all.

For **API mode**, open `.env` and add your OpenAI key:
```
LEARNFORGE_MODE=api
OPENAI_API_KEY=sk-your-key-here
```

### Step 2.6: Build the RAG vector index
```bash
make index
```

This reads the 30 corpus markdown files, chunks them, embeds with BGE-small, and stores in ChromaDB. Takes ~30 seconds. **No API calls. Free.**

You should see:
```
Found 30 markdown files
Indexed XXX chunks
✅ ChromaDB index built
```

---

## 3. Running in Demo Mode (Zero Cost)

```bash
make demo
```

This launches Streamlit with `LEARNFORGE_MODE=demo`. Open http://localhost:8501 in your browser.

**What happens in demo mode:**
- Curriculum generation → loads pre-built Machine Learning curriculum from `demo_data/`
- Lessons → loads pre-written lesson content
- Quizzes → loads pre-written questions
- Flashcards → loads pre-written cards
- Concept images → generates SVG placeholder diagrams (no API)
- Text-to-Speech → uses browser-native speech synthesis (no API)
- Dashboard → shows sample visualization data
- Data upload → works normally (files saved locally)

**No API key. No cost. Everything works.**

---

## 4. Running in API Mode (OpenAI)

### Step 4.1: Edit .env
```
LEARNFORGE_MODE=api
OPENAI_API_KEY=sk-your-key-here
```

### Step 4.2: Run
```bash
make run
```

Or you can switch modes in the sidebar at runtime — no restart needed.

**What happens in API mode:**
- Curriculum → GPT-4o-mini generates a real custom curriculum for ANY topic
- Lessons → GPT-4o-mini writes full lesson content
- Quizzes → GPT-4o-mini creates questions with Bloom's taxonomy levels
- Flashcards → GPT-4o-mini generates cards
- Concept images → DALL-E 3 generates real AI images
- Text-to-Speech → OpenAI TTS generates HD audio
- Assessor → GPT-4o-mini evaluates with RAG-grounded citations

**Cost: ~$0.002-0.01 per interaction.** Generating a full curriculum + lesson + quiz + flashcards for one topic costs maybe $0.05.

---

## 5. Running in Ollama Mode (Local, Free)

### Step 5.1: Install Ollama
```bash
# macOS
brew install ollama

# Or download from https://ollama.com
```

### Step 5.2: Pull a model
```bash
ollama pull llama3
```

### Step 5.3: Start Ollama server
```bash
ollama serve
```

### Step 5.4: Edit .env
```
LEARNFORGE_MODE=ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### Step 5.5: Run
```bash
make run
```

**What happens in Ollama mode:**
- All text generation uses local Ollama models
- Images → SVG placeholders (no DALL-E)
- TTS → browser native (no OpenAI TTS)
- Completely offline and free after model download

---

## 6. Using the Application (Every Feature)

### 6.1: Home Page (http://localhost:8501)
- Type a topic (e.g., "Machine Learning", "Kubernetes", "World War II")
- Select your level (beginner / intermediate / advanced)
- Click "Generate Learning Path"
- Sidebar shows mode switcher and data storage info

### 6.2: Curriculum Page
- Visual module cards with Bloom's Taxonomy progression
- **Bloom's Taxonomy chart** — shows cognitive complexity progression across modules
- Each module shows: title, objectives, difficulty, estimated time, prerequisites
- Progress bars per module
- Buttons to: Read Lesson, Take Quiz, or Study Flashcards for each module

### 6.3: Lesson Viewer
- **Concept Diagram** — auto-generated image/SVG at the top of each lesson
- **Text-to-Speech** — click "Generate Audio" to hear the lesson narrated
- Rich formatted sections with key concept callouts
- Examples in expandable sections
- Summary + Key Takeaways at the bottom
- Auto-saves lesson to `data/generated/`

### 6.4: Quiz Arena
- Multiple question types: multiple choice, true/false, short answer
- Each question tagged with Bloom's level and difficulty
- Submit → instant scoring with:
  - Score out of 25 (5 questions × 5 points max)
  - Percentage with color indicator
  - Detailed feedback per question
  - Misconception detection
  - Explanations
- Results saved to SQLite for dashboard analytics

### 6.5: Flashcards
- Flip-card interface with gradient styling
- Front → click "Flip Card" → Back
- Confidence rating: "Didn't know" / "Kinda knew" / "Knew it!"
- Hint button (shows hint without flipping)
- Progress: card count, correct/incorrect, mastery percentage
- Progress saved for spaced repetition

### 6.6: Progress Dashboard
- **4 tabs:**
  - Bloom's Analysis: radar chart + bar chart of performance by cognitive level
  - Score Trends: line chart of daily average scores + daily activity bar chart
  - Knowledge Gaps: heatmap of most frequent gaps + details table
  - Activity: study heatmap + streak tracker
- Shows sample data when no quizzes taken yet (so dashboard always looks good in demos)

### 6.7: Data Manager
- **Upload tab:** Drag PDFs, TXT, MD, CSV files → ingested into RAG corpus
- **Corpus Browser tab:** Browse all 30+ files by category, view content inline
- **Generated Content tab:** Browse all auto-saved curricula, lessons, quizzes, flashcards
- **Export tab:** Download curriculum (.md), quiz (.csv), flashcards (.csv for Anki), progress report (.md)
- Storage overview: file counts, DB sizes, paths

---

## 7. Uploading Your Own Study Materials

Sample files are included in `demo_data/upload_samples/`:
- `python_study_notes.md` — Python basics
- `deep_learning_cheatsheet.txt` — Deep learning reference
- `kubernetes_notes.md` — K8s quick reference
- `statistics_formulas.csv` — Stats formulas table

**To upload:**
1. Go to Data Manager → Upload tab
2. Drag one of these files (or any PDF/TXT/MD of your own)
3. Select a category (subjects, pedagogy, misconceptions, custom)
4. Click "Ingest into RAG Corpus"
5. The file gets saved as markdown in `data/corpus/{category}/`
6. Run `make index` in your terminal to rebuild the vector database
7. Now the Assessor can cite your uploaded content when grading quizzes!

---

## 8. Fine-Tuning on Google Colab

Training data is already pre-built. You do NOT need to generate it.

### Step 8.1: Open Google Colab
Go to https://colab.research.google.com → New Notebook → Change runtime to **T4 GPU** (Runtime → Change runtime type → T4 GPU)

### Step 8.2: Upload 4 files to Colab
Use the file browser on the left to upload:
- `data/processed/train.jsonl` (144 examples)
- `data/processed/val.jsonl` (18 examples)
- `src/finetuning/train_lora.py`
- `src/finetuning/configs/qlora_3b.yaml`

### Step 8.3: Install dependencies
```python
!pip install -q transformers==4.45.0 peft==0.13.0 trl==0.11.0 bitsandbytes==0.44.0 accelerate==1.0.0 datasets==3.0.0 pyyaml
```

### Step 8.4: Set HuggingFace token (for Llama model access)
```python
import os
os.environ["HF_TOKEN"] = "hf_your_token_here"
# Get your token from https://huggingface.co/settings/tokens
```

If you don't have Llama access, the script auto-falls back to Qwen2.5-3B (no approval needed).

### Step 8.5: Run training
```python
!python train_lora.py
```

Takes ~20-30 minutes on T4. You'll see training loss decreasing per epoch.

### Step 8.6: Download the adapter
After training, download the `models/lora_adapter/` folder from Colab.
Place it in your project under `models/lora_adapter/`.

### Step 8.7: Enable fine-tuned model
Edit `.env`:
```
USE_FINETUNED=true
```

Now Agent 2 (Content Generator) uses the fine-tuned model instead of API.

---

## 9. Running Evaluations

```bash
make eval
```

This runs the RAG ablation evaluation (dense vs BM25 vs hybrid). Results are saved to `evaluation/results/rag_ablation.csv`.

For your report/video: show the CSV results proving hybrid retrieval outperforms single methods.

---

## 10. Project Structure Explained

```
learnforge/
├── app/                           # Streamlit UI
│   ├── streamlit_app.py           # Home page with mode switcher
│   └── pages/
│       ├── 1_Curriculum.py        # Module cards + Bloom's chart
│       ├── 2_Lesson.py            # Lessons + concept image + TTS
│       ├── 3_Quiz_Arena.py        # Interactive quiz + scoring
│       ├── 4_Flashcards.py        # Flip cards + confidence rating
│       ├── 5_Dashboard.py         # 4-tab analytics dashboard
│       └── 6_Data_Manager.py      # Upload, browse, export
├── src/
│   ├── config.py                  # All settings, paths, model names
│   ├── agents/
│   │   ├── base.py                # Unified LLM backend (demo/api/ollama)
│   │   ├── curriculum_architect.py # Agent 1 — builds curricula
│   │   ├── content_generator.py   # Agent 2 — lessons, quizzes, flashcards
│   │   ├── adaptive_assessor.py   # Agent 3 — evaluates with RAG
│   │   └── prompts/               # 5 system prompts
│   ├── rag/
│   │   ├── ingest.py              # Chunk + embed + ChromaDB
│   │   └── retrieve.py            # Hybrid retrieval + reranker
│   ├── content/
│   │   ├── manager.py             # File upload, export, data persistence
│   │   └── multimodal.py          # Image gen (DALL-E/SVG) + TTS
│   ├── profile/
│   │   └── storage.py             # SQLite: quiz scores, gaps, streaks
│   └── finetuning/
│       ├── train_lora.py          # Colab training script
│       ├── inference.py           # LoRA adapter loader
│       └── configs/qlora_3b.yaml  # Hyperparameters
├── data/
│   ├── corpus/                    # 30 RAG documents (pre-built)
│   ├── processed/                 # Training data (pre-built)
│   └── generated/                 # Auto-saved content (runtime)
├── demo_data/
│   ├── *.json                     # Pre-generated demo content
│   └── upload_samples/            # 4 sample files for upload demo
├── chroma_db/                     # Vector database (built by make index)
├── models/lora_adapter/           # Fine-tuned weights (from Colab)
└── learnforge.db                  # SQLite database (runtime)
```

### Where data is stored:
| What | Where | When created |
|------|-------|-------------|
| RAG corpus | `data/corpus/*.md` | Pre-built (30 files) + your uploads |
| Vector embeddings | `chroma_db/` | When you run `make index` |
| Demo content | `demo_data/*.json` | Pre-built |
| Training data | `data/processed/*.jsonl` | Pre-built (180 examples) |
| Generated content | `data/generated/` | When you use the app |
| Quiz scores & progress | `learnforge.db` | When you take quizzes |
| Fine-tuned model | `models/lora_adapter/` | After Colab training |
| Upload samples | `demo_data/upload_samples/` | Pre-built (4 sample files) |

---

## 11. Troubleshooting

**"ModuleNotFoundError"**
→ Make sure virtual environment is activated: `source .venv/bin/activate`

**"make: command not found" (Windows)**
→ Run the commands directly:
```bash
pip install -e .
python scripts/build_index.py
streamlit run app/streamlit_app.py --server.port 8501
```

**"No module named src"**
→ Make sure you're in the `learnforge/` directory and ran `pip install -e .`

**ChromaDB index empty / not built**
→ Run `make index` or `python scripts/build_index.py`

**Quiz shows no questions**
→ In demo mode, make sure `demo_data/quizzes.json` exists. If using API mode, check your API key.

**Flashcards not flipping**
→ Click the "Flip Card" button. The confidence buttons only appear after flipping.

**Dashboard shows no data**
→ Take some quizzes first! The dashboard shows sample data as a preview if you haven't taken any quizzes yet.

**Ollama connection refused**
→ Make sure Ollama is running: `ollama serve`

**DALL-E image not generating**
→ DALL-E only works in API mode with a valid OpenAI key. Demo/Ollama mode shows SVG placeholders instead.
