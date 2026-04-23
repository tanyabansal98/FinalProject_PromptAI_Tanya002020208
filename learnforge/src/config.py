"""Central configuration for LearnForge."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
RAW_DIR = DATA_DIR / "raw"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"
GENERATED_DIR = DATA_DIR / "generated"
EVAL_DIR = DATA_DIR / "eval"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
MODELS_DIR = PROJECT_ROOT / "models"
LORA_ADAPTER_DIR = MODELS_DIR / "lora_adapter"
DEMO_DATA_DIR = PROJECT_ROOT / "demo_data"
SQLITE_DB_PATH = PROJECT_ROOT / "learnforge.db"

# ── API Keys ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# ── Mode: "demo" | "api" | "ollama" ──
MODE = os.getenv("LEARNFORGE_MODE", "demo")

# ── Model Settings ──
LLM_MODEL = "gpt-4o-mini"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
RERANKER_MODEL = "BAAI/bge-reranker-base"
FINETUNE_BASE_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
USE_FINETUNED = os.getenv("USE_FINETUNED", "false").lower() == "true"

# ── RAG Settings ──
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
CHROMA_COLLECTION = "learnforge_rag"
HYBRID_TOP_K = 10
RERANK_TOP_K = 3
RRF_K = 60

# ── Agent Settings ──
MAX_RETRIES = 2
DEFAULT_TEMPERATURE = 0.7

# ── Learning Levels ──
LEVELS = ["beginner", "intermediate", "advanced"]

# ── Subject Categories ──
SUBJECTS = [
    "computer_science", "mathematics", "physics", "chemistry", "biology",
    "history", "economics", "psychology", "philosophy", "literature",
    "data_science", "machine_learning", "web_development", "databases",
    "networking", "cloud_computing", "devops", "cybersecurity",
    "statistics", "linear_algebra",
]

# ── Bloom's Taxonomy Levels ──
BLOOMS_LEVELS = [
    "remember", "understand", "apply", "analyze", "evaluate", "create"
]
