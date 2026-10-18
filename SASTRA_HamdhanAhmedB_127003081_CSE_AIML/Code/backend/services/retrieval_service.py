import math
import re
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import domain as models
from backend.services.vector_store_service import get_collection

def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer for BM25."""
    return re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())

class BM25Index:
    """In-memory BM25 index over retrieved candidate chunks."""
    def __init__(self, corpus: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_len = [len(tokenize(doc["text_content"])) for doc in corpus]
        self.avg_doc_len = sum(self.doc_len) / max(len(self.doc_len), 1)
        self.doc_count = len(corpus)
        
        # Build inverted index
        self.df: Dict[str, int] = {}
        self.tf: List[Dict[str, int]] = []
        for doc in corpus:
            tokens = tokenize(doc["text_content"])
            term_freq = {}
            for t in tokens:
                term_freq[t] = term_freq.get(t, 0) + 1
            self.tf.append(term_freq)
            for t in term_freq:
                self.df[t] = self.df.get(t, 0) + 1

    def score(self, query_tokens: List[str]) -> List[float]:
        scores = [0.0] * self.doc_count
        for token in query_tokens:
            if token not in self.df:
                continue
            df_val = self.df[token]
            idf = math.log((self.doc_count - df_val + 0.5) / (df_val + 0.5) + 1.0)
            for i in range(self.doc_count):
                tf_val = self.tf[i].get(token, 0)
                if tf_val > 0:
                    numerator = tf_val * (self.k1 + 1)
                    denominator = tf_val + self.k1 * (1 - self.b + self.b * (self.doc_len[i] / max(self.avg_doc_len, 1e-6)))
                    scores[i] += idf * (numerator / denominator)
        return scores

def hybrid_retrieve(
    db: Session,
    project_id: int,
    query: str,
    top_k: int = 5,
    document_ids: Optional[List[int]] = None,
    version_label: Optional[str] = None,
    strategy: str = "dense"
) -> Dict[str, Any]:
    """
    Performs dense or hybrid retrieval with Reciprocal Rank Fusion (RRF).
    Records per-stage latencies for benchmark evaluation.
    """
    latencies = {
        "dense_latency_ms": 0.0,
        "bm25_latency_ms": 0.0,
        "fusion_latency_ms": 0.0,
        "total_latency_ms": 0.0
    }
    t_start = time.time()
    
    # 1. Build vector search where filter
    filter_parts = []
    if document_ids:
        if len(document_ids) == 1:
            filter_parts.append({"document_id": document_ids[0]})
        else:
            filter_parts.append({"document_id": {"$in": document_ids}})
    if version_label and version_label.strip() and version_label not in ("All", "All Versions"):
        filter_parts.append({"version_label": version_label.strip()})
        
    where_filter = None
    if len(filter_parts) == 1:
        where_filter = filter_parts[0]
    elif len(filter_parts) > 1:
        where_filter = {"$and": filter_parts}

    # Execute Dense Search
    t_dense_0 = time.time()
    dense_hits = []
    try:
        collection = get_collection(project_id)
        dense_kwargs = {"query_texts": [query], "n_results": max(top_k * 2, 10)}
        if where_filter:
            dense_kwargs["where"] = where_filter
        res = collection.query(**dense_kwargs)
        if res and res.get("documents") and len(res["documents"][0]) > 0:
            for idx, text_passage in enumerate(res["documents"][0]):
                meta = res["metadatas"][0][idx]
                chunk_id = res["ids"][0][idx]
                dense_hits.append({
                    "id": chunk_id,
                    "text_content": text_passage,
                    "metadata": meta
                })
    except Exception as e:
        pass
    latencies["dense_latency_ms"] = round((time.time() - t_dense_0) * 1000, 2)

    if strategy == "dense" or not dense_hits:
        latencies["total_latency_ms"] = round((time.time() - t_start) * 1000, 2)
        # Sliced to top_k
        final_hits = dense_hits[:top_k]
        return {
            "hits": final_hits,
            "strategy": "dense",
            "latencies": latencies
        }

    # 2. BM25 Keyword Search
    t_bm25_0 = time.time()
    chunk_query = db.query(models.DocumentChunk).filter(models.DocumentChunk.project_id == project_id)
    if document_ids:
        chunk_query = chunk_query.filter(models.DocumentChunk.document_id.in_(document_ids))
    if version_label and version_label.strip() and version_label not in ("All", "All Versions"):
        chunk_query = chunk_query.filter(models.DocumentChunk.version_label == version_label.strip())
        
    candidate_chunks = chunk_query.all()
    bm25_hits = []
    if candidate_chunks:
        corpus = [{
            "id": f"{c.document_id}_{c.chunk_index}",
            "text_content": c.text_content,
            "metadata": {
                "document_id": c.document_id,
                "chunk_index": c.chunk_index,
                "page_start": c.page_start or 1,
                "page_end": c.page_end or 1,
                "version_label": c.version_label or "1.0",
                "section_heading": c.section_heading or ""
            }
        } for c in candidate_chunks]
        
        bm25 = BM25Index(corpus)
        q_tokens = tokenize(query)
        scores = bm25.score(q_tokens)
        scored_corpus = list(zip(scores, corpus))
        scored_corpus.sort(key=lambda x: x[0], reverse=True)
        # Keep positive scores
        bm25_hits = [item[1] for item in scored_corpus[:max(top_k * 2, 10)] if item[0] > 0]
    latencies["bm25_latency_ms"] = round((time.time() - t_bm25_0) * 1000, 2)

    # 3. Reciprocal Rank Fusion (RRF)
    t_rf_0 = time.time()
    RRF_K = 60
    rrf_scores: Dict[str, float] = {}
    item_map: Dict[str, Dict[str, Any]] = {}

    for rank, hit in enumerate(dense_hits):
        cid = hit["id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (RRF_K + rank + 1))
        item_map[cid] = hit

    for rank, hit in enumerate(bm25_hits):
        cid = hit["id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (RRF_K + rank + 1))
        if cid not in item_map:
            item_map[cid] = hit

    sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
    fused_hits = [item_map[cid] for cid in sorted_cids[:top_k]]
    latencies["fusion_latency_ms"] = round((time.time() - t_rf_0) * 1000, 2)
    latencies["total_latency_ms"] = round((time.time() - t_start) * 1000, 2)

    return {
        "hits": fused_hits,
        "strategy": "hybrid",
        "latencies": latencies
    }
