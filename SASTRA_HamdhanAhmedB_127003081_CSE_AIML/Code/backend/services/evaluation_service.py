import os
import re
import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models import domain as models
from backend.services.retrieval_service import hybrid_retrieve
from backend.services.llm_service import ask_question
from backend.services.grounding_service import (
    segment_answer_into_claims,
    verify_claims_against_evidence,
    compute_grounding_score
)

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "evaluation",
    "benchmark_dataset.json"
)

def load_benchmark_dataset() -> Dict[str, Any]:
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Evaluation benchmark dataset not found at {DATASET_PATH}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation_benchmark(
    db: Session,
    project_id: int,
    strategy: str = "dense",
    top_k: int = 5,
    max_queries: Optional[int] = None
) -> Dict[str, Any]:
    """
    Executes reproducible RAG benchmark against the evaluation dataset.
    Uses existing documents in read-only mode without corrupting production tables.
    """
    dataset = load_benchmark_dataset()
    queries = dataset.get("queries", [])
    if max_queries and max_queries > 0:
        queries = queries[:max_queries]

    per_query_results = []
    
    rr_scores = []
    hit_1_scores = []
    citation_precisions = []
    supported_claim_rates = []
    abstention_scores = []
    latencies_list = []

    for item in queries:
        qid = item["id"]
        q_text = item["query"]
        expected_keywords = item.get("expected_keywords", [])
        is_unanswerable = item.get("expected_unanswerable", False)

        t_q_start = time.time()

        # 1. Retrieval Stage
        retrieval_res = hybrid_retrieve(
            db=db,
            project_id=project_id,
            query=q_text,
            top_k=top_k,
            strategy=strategy
        )
        hits = retrieval_res.get("hits", [])
        stage_latencies = retrieval_res.get("latencies", {})

        # Context Formulation
        context = ""
        citations = []
        for idx, hit in enumerate(hits):
            meta = hit.get("metadata", {})
            passage = hit.get("text_content", "")
            doc_id = meta.get("document_id")
            context += f"Document #{doc_id} (Page {meta.get('page_start', 1)}): {passage}\n\n"
            citations.append({
                "citation_id": idx + 1,
                "document_id": doc_id,
                "document_name": f"Doc #{doc_id}",
                "page_start": meta.get("page_start", 1),
                "page_end": meta.get("page_end", 1),
                "content": passage
            })

        # Measure Retrieval Metrics (MRR & Hit Rate @ 1)
        rank_found = 0
        if not is_unanswerable and expected_keywords:
            for r_idx, hit in enumerate(hits):
                text_lower = (hit.get("text_content") or "").lower()
                if any(kw.lower() in text_lower for kw in expected_keywords):
                    rank_found = r_idx + 1
                    break
            
            reciprocal_rank = (1.0 / rank_found) if rank_found > 0 else 0.0
            hit_at_1 = 1.0 if rank_found == 1 else 0.0
            rr_scores.append(reciprocal_rank)
            hit_1_scores.append(hit_at_1)
        else:
            reciprocal_rank = 1.0 if not hits else 0.5
            hit_at_1 = 1.0 if not hits else 0.0

        # 2. LLM Inference Stage
        t_llm = time.time()
        answer = ask_question(q_text, context)
        llm_dur_ms = round((time.time() - t_llm) * 1000, 2)
        total_q_latency = round((time.time() - t_q_start) * 1000, 2)
        latencies_list.append(total_q_latency)

        # 3. Grounding & Abstention Evaluation
        is_abstention_text = bool(re.search(r'do(?:es)? not provide sufficient evidence|insufficient evidence|not mentioned', answer, re.IGNORECASE))
        
        if is_unanswerable:
            abstention_correct = 1.0 if is_abstention_text else 0.0
            abstention_scores.append(abstention_correct)
            claim_rate = 1.0 if is_abstention_text else 0.0
            cit_prec = 1.0 if not citations else 0.5
        else:
            claims = segment_answer_into_claims(answer)
            v_claims = verify_claims_against_evidence(claims, citations)
            metrics = compute_grounding_score(v_claims, len(citations))
            grounded_cnt = metrics["grounded_count"]
            tot_cl = max(metrics["total_claims"], 1)
            claim_rate = round(grounded_cnt / tot_cl, 3)
            supported_claim_rates.append(claim_rate)
            cit_prec = 1.0 if citations else 0.0
            citation_precisions.append(cit_prec)
            abstention_correct = None

        per_query_results.append({
            "id": qid,
            "query": q_text,
            "is_unanswerable": is_unanswerable,
            "hit_rank": rank_found if not is_unanswerable else None,
            "reciprocal_rank": round(reciprocal_rank, 3) if not is_unanswerable else None,
            "answer_snippet": answer[:140] + "..." if len(answer) > 140 else answer,
            "is_abstention": is_abstention_text,
            "abstention_correct": abstention_correct,
            "supported_claim_rate": claim_rate if not is_unanswerable else None,
            "citations_returned": len(citations),
            "latency_ms": total_q_latency
        })

    # Compute overall averages
    avg_mrr = round((sum(rr_scores) / max(len(rr_scores), 1)), 3) if rr_scores else 0.0
    avg_hit_1 = round((sum(hit_1_scores) / max(len(hit_1_scores), 1)) * 100.0, 1) if hit_1_scores else 0.0
    avg_cit_prec = round((sum(citation_precisions) / max(len(citation_precisions), 1)) * 100.0, 1) if citation_precisions else 0.0
    avg_supp_claims = round((sum(supported_claim_rates) / max(len(supported_claim_rates), 1)) * 100.0, 1) if supported_claim_rates else 0.0
    avg_abstention = round((sum(abstention_scores) / max(len(abstention_scores), 1)) * 100.0, 1) if abstention_scores else 0.0
    avg_lat = round(sum(latencies_list) / max(len(latencies_list), 1), 1)

    # Persist benchmark run record
    run_record = models.BenchmarkRun(
        project_id=project_id,
        dataset_version=dataset.get("dataset_version", "1.0"),
        retrieval_strategy=strategy,
        top_k=top_k,
        total_queries=len(queries),
        completed_queries=len(queries),
        failed_queries=0,
        mrr=avg_mrr,
        hit_rate_at_1=avg_hit_1,
        citation_precision=avg_cit_prec,
        supported_claim_rate=avg_supp_claims,
        abstention_accuracy=avg_abstention,
        avg_latency_ms=avg_lat,
        results_json=json.dumps({
            "dataset_name": dataset.get("name"),
            "per_query_results": per_query_results
        })
    )
    db.add(run_record)
    db.commit()
    db.refresh(run_record)

    return {
        "run_id": run_record.id,
        "dataset_version": dataset.get("dataset_version", "1.0"),
        "retrieval_strategy": strategy,
        "top_k": top_k,
        "total_queries": len(queries),
        "mrr": avg_mrr,
        "hit_rate_at_1": avg_hit_1,
        "citation_precision": avg_cit_prec,
        "supported_claim_rate": avg_supp_claims,
        "abstention_accuracy": avg_abstention,
        "avg_latency_ms": avg_lat,
        "per_query_results": per_query_results
    }
