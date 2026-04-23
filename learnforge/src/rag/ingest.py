"""Ingest RAG corpus: chunk markdown, embed, store in ChromaDB."""
import os
import logging
from pathlib import Path
from typing import List, Dict

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CORPUS_DIR, CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


def _load_markdown_files(corpus_dir: Path) -> List[Dict]:
    documents = []
    for md_file in sorted(corpus_dir.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8").strip()
        if not text:
            continue
        documents.append({
            "id": md_file.stem,
            "text": text,
            "metadata": {
                "source_id": md_file.name,
                "category": md_file.parent.name,
                "path": str(md_file.relative_to(corpus_dir)),
            },
        })
    return documents


def _chunk_documents(documents: List[Dict]) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        chunk_size=CHUNK_SIZE * 4, chunk_overlap=CHUNK_OVERLAP * 4, length_function=len)
    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["text"])
        for i, chunk_text in enumerate(splits):
            chunks.append({
                "id": f"{doc['id']}_chunk_{i}",
                "text": chunk_text,
                "metadata": {**doc["metadata"], "chunk_index": i},
            })
    return chunks


def build_index(corpus_dir=None, chroma_dir=None):
    corpus_dir = corpus_dir or CORPUS_DIR
    chroma_dir = chroma_dir or CHROMA_DIR
    documents = _load_markdown_files(corpus_dir)
    logger.info(f"Loaded {len(documents)} documents")
    chunks = _chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")
    if not chunks:
        return 0
    os.makedirs(chroma_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_dir))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    try:
        client.delete_collection(name=CHROMA_COLLECTION)
    except Exception:
        pass
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION, embedding_function=ef, metadata={"hnsw:space": "cosine"})
    BATCH = 500
    for start in range(0, len(chunks), BATCH):
        batch = chunks[start:start + BATCH]
        collection.add(ids=[c["id"] for c in batch], documents=[c["text"] for c in batch], metadatas=[c["metadata"] for c in batch])
    logger.info(f"Indexed {collection.count()} chunks")
    return collection.count()
