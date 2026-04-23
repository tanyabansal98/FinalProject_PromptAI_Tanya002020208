#!/usr/bin/env python3
"""Build ChromaDB index from the corpus."""
import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO)
from src.config import CORPUS_DIR
from src.rag.ingest import build_index

print(f"Building index from {CORPUS_DIR}")
md_count = sum(1 for _ in CORPUS_DIR.rglob("*.md"))
print(f"Found {md_count} markdown files")
count = build_index()
print(f"✅ Indexed {count} chunks")
