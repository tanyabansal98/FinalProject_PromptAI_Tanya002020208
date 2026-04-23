"""Hybrid retrieval: Dense + BM25 + RRF + optional reranker."""
import logging
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from src.config import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, HYBRID_TOP_K, RRF_K, RERANKER_MODEL, RERANK_TOP_K

logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(self, chroma_dir=None):
        chroma_dir = chroma_dir or CHROMA_DIR
        self._client = chromadb.PersistentClient(path=str(chroma_dir))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        self._collection = self._client.get_collection(name=CHROMA_COLLECTION, embedding_function=ef)
        self._all_docs = self._load_all()
        corpus_tokens = [d["text"].lower().split() for d in self._all_docs]
        self._bm25 = BM25Okapi(corpus_tokens) if corpus_tokens else None

    def _load_all(self):
        count = self._collection.count()
        if count == 0:
            return []
        result = self._collection.get(include=["documents", "metadatas"], limit=count)
        return [{"id": result["ids"][i], "text": result["documents"][i],
                 "metadata": result["metadatas"][i] if result["metadatas"] else {}}
                for i in range(len(result["ids"]))]

    def retrieve(self, query, top_k=HYBRID_TOP_K, method="hybrid"):
        if method == "dense":
            return self._dense(query, top_k)
        elif method == "bm25":
            return self._bm25_search(query, top_k)
        return self._hybrid(query, top_k)

    def _dense(self, query, top_k):
        n = min(top_k, self._collection.count())
        if n == 0:
            return []
        r = self._collection.query(query_texts=[query], n_results=n, include=["documents", "metadatas", "distances"])
        return [{"id": r["ids"][0][i], "text": r["documents"][0][i],
                 "metadata": r["metadatas"][0][i] if r["metadatas"] else {},
                 "score": 1.0 - r["distances"][0][i]} for i in range(len(r["ids"][0]))]

    def _bm25_search(self, query, top_k):
        if not self._all_docs or not self._bm25:
            return []
        scores = self._bm25.get_scores(query.lower().split())
        ranked = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]
        return [{"id": self._all_docs[i]["id"], "text": self._all_docs[i]["text"],
                 "metadata": self._all_docs[i]["metadata"], "score": float(scores[i])} for i in ranked]

    def _hybrid(self, query, top_k):
        dense = self._dense(query, top_k)
        bm25 = self._bm25_search(query, top_k)
        dr = {d["id"]: r for r, d in enumerate(dense)}
        br = {d["id"]: r for r, d in enumerate(bm25)}
        lookup = {d["id"]: d for d in dense + bm25}
        fused = []
        for did in set(dr) | set(br):
            s = sum(1.0 / (RRF_K + ranks.get(did, top_k + 1)) for ranks in [dr, br])
            doc = dict(lookup[did])
            doc["score"] = s
            fused.append(doc)
        fused.sort(key=lambda d: -d["score"])
        return fused[:top_k]


class Reranker:
    def __init__(self):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(RERANKER_MODEL)

    def rerank(self, query, documents, top_k=RERANK_TOP_K):
        if not documents:
            return []
        pairs = [(query, d["text"]) for d in documents]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(documents, scores), key=lambda x: -x[1])
        return [{**dict(d), "rerank_score": float(s)} for d, s in ranked[:top_k]]
