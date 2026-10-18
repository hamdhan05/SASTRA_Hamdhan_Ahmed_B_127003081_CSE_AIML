import json
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.database.connection import get_db
from backend.models import domain as models
from backend.schemas import domain as schemas
from backend.core.config import settings
from backend.services.llm_service import ask_question
from backend.services.retrieval_service import hybrid_retrieve
from backend.services.grounding_service import (
    segment_answer_into_claims,
    verify_claims_against_evidence,
    compute_grounding_score
)

router = APIRouter()

class AskQuery(BaseModel):
    query: str
    document_ids: List[int] = []
    version_label: Optional[str] = None
    strategy: Optional[str] = "dense" # "dense" or "hybrid"
    top_k: Optional[int] = Field(default=5, ge=1, le=10)

class ReviewSubmission(BaseModel):
    decision: str  # Accepted, Rejected, Needs Modification
    reviewer_id: str
    feedback: Optional[str] = ""
    corrected_facts: Optional[str] = ""

@router.post("/projects/{project_id}/ask")
def ask_assistant(project_id: int, query: AskQuery, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    selected_top_k = query.top_k if query.top_k and 1 <= query.top_k <= 10 else getattr(settings, "TOP_K", 5)
    selected_strategy = (query.strategy or "dense").lower()
    if selected_strategy not in ("dense", "hybrid"):
        selected_strategy = "dense"

    # Execute version-aware retrieval (Dense or Hybrid + RRF)
    retrieval_res = hybrid_retrieve(
        db=db,
        project_id=project_id,
        query=query.query,
        top_k=selected_top_k,
        document_ids=query.document_ids if query.document_ids else None,
        version_label=query.version_label,
        strategy=selected_strategy
    )
    
    hits = retrieval_res.get("hits", [])
    latencies = retrieval_res.get("latencies", {})

    # Build context and verified citations
    context = ""
    citations = []
    doc_name_cache = {}

    for idx, hit in enumerate(hits):
        meta = hit.get("metadata", {})
        doc_id = meta.get("document_id")
        page_start = meta.get("page_start", 1)
        page_end = meta.get("page_end", 1)
        ver_lbl = meta.get("version_label", "1.0")
        sec_head = meta.get("section_heading", "")
        passage = hit.get("text_content", "")

        if doc_id not in doc_name_cache:
            doc_record = db.query(models.Document).filter(models.Document.id == doc_id).first()
            doc_name_cache[doc_id] = doc_record.original_filename if doc_record else f"Doc #{doc_id}"

        doc_name = doc_name_cache[doc_id]
        head_suffix = f" [{sec_head}]" if sec_head else ""
        context += f"Document: {doc_name} (Page {page_start}-{page_end}, v{ver_lbl}){head_suffix}\nExcerpt: {passage}\n\n"
        
        citations.append({
            "citation_id": idx + 1,
            "document_id": doc_id,
            "document_name": doc_name,
            "version_label": ver_lbl,
            "section_heading": sec_head,
            "page_start": page_start,
            "page_end": page_end,
            "content": passage
        })

    # Inference via local Ollama llama3.2:3b
    t_llm_0 = time.time()
    answer = ask_question(query.query, context)
    llm_latency_ms = round((time.time() - t_llm_0) * 1000, 2)
    latencies["llm_latency_ms"] = llm_latency_ms

    # Independent claim segmentation and grounding verification
    claims = segment_answer_into_claims(answer)
    verified_claims = verify_claims_against_evidence(claims, citations)
    grounding_metrics = compute_grounding_score(verified_claims, len(citations))

    # Persist session & messages
    session = models.AnalysisSession(project_id=project_id, title=query.query[:50], user_id=None)
    db.add(session)
    db.commit()
    db.refresh(session)
    
    msg_user = models.AnalysisMessage(
        session_id=session.id, 
        role="user", 
        content=query.query
    )
    db.add(msg_user)
    
    msg_assist = models.AnalysisMessage(
        session_id=session.id, 
        role="assistant", 
        content=answer,
        citations_json=json.dumps(citations),
        claims_json=json.dumps(verified_claims),
        grounding_score=grounding_metrics["grounding_score"],
        confidence_level=grounding_metrics["confidence_level"],
        review_recommendation=grounding_metrics["review_recommendation"],
        metadata_json=json.dumps({
            "strategy": selected_strategy,
            "top_k": selected_top_k,
            "version_label": query.version_label or "All",
            "latencies": latencies
        })
    )
    db.add(msg_assist)
    db.commit()
    db.refresh(msg_assist)

    return {
        "message_id": msg_assist.id,
        "session_id": session.id,
        "answer": answer,
        "citations": citations,
        "claims": verified_claims,
        "grounding_score": grounding_metrics["grounding_score"],
        "confidence_level": grounding_metrics["confidence_level"],
        "review_recommendation": grounding_metrics["review_recommendation"],
        "strategy": selected_strategy,
        "top_k": selected_top_k,
        "latencies": latencies
    }

@router.post("/sessions/{session_id}/messages/{message_id}/review")
def review_message(session_id: int, message_id: int, review_data: ReviewSubmission, db: Session = Depends(get_db)):
    msg = db.query(models.AnalysisMessage).filter(
        models.AnalysisMessage.id == message_id,
        models.AnalysisMessage.session_id == session_id
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    valid_decisions = ["Accepted", "Rejected", "Needs Modification"]
    if review_data.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail=f"Invalid decision. Must be one of: {valid_decisions}")

    if not review_data.reviewer_id.strip():
        raise HTTPException(status_code=400, detail="Reviewer ID is required.")

    msg.review_decision = review_data.decision
    msg.reviewer_id = review_data.reviewer_id.strip()
    msg.review_feedback = review_data.feedback or ""
    msg.corrected_facts = review_data.corrected_facts or ""
    msg.reviewed_at = datetime.utcnow()
    db.commit()

    # Log in audit_logs
    session_obj = db.query(models.AnalysisSession).filter(models.AnalysisSession.id == session_id).first()
    proj_id = session_obj.project_id if session_obj else 1
    audit = models.AuditLog(
        project_id=proj_id,
        user_id=None,
        action="ENGINEERING_REVIEW_SUBMITTED",
        resource_type="analysis_message",
        resource_id=message_id,
        details_json=json.dumps({
            "decision": review_data.decision,
            "reviewer_id": review_data.reviewer_id,
            "feedback": review_data.feedback,
            "corrected_facts": review_data.corrected_facts
        })
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "message_id": message_id,
        "review_decision": msg.review_decision,
        "reviewer_id": msg.reviewer_id,
        "reviewed_at": str(msg.reviewed_at)
    }

@router.get("/projects/{project_id}/reviews")
def get_project_reviews(project_id: int, db: Session = Depends(get_db)):
    """Fetches all reviewed AI analysis messages for the Review Audit History view."""
    # Find all sessions in project
    session_ids = [s.id for s in db.query(models.AnalysisSession.id).filter(models.AnalysisSession.project_id == project_id).all()]
    if not session_ids:
        return []

    messages = db.query(models.AnalysisMessage).filter(
        models.AnalysisMessage.session_id.in_(session_ids),
        models.AnalysisMessage.review_decision != None
    ).order_by(models.AnalysisMessage.reviewed_at.desc()).all()

    # Enrich with user question
    results = []
    for m in messages:
        # Get preceding user question in the same session
        prev_user_msg = db.query(models.AnalysisMessage).filter(
            models.AnalysisMessage.session_id == m.session_id,
            models.AnalysisMessage.role == "user",
            models.AnalysisMessage.id < m.id
        ).order_by(models.AnalysisMessage.id.desc()).first()

        results.append({
            "id": m.id,
            "session_id": m.session_id,
            "question": prev_user_msg.content if prev_user_msg else "Unknown Question",
            "answer_summary": m.content[:180] + "..." if len(m.content) > 180 else m.content,
            "full_answer": m.content,
            "decision": m.review_decision,
            "reviewer_id": m.reviewer_id,
            "feedback": m.review_feedback or "",
            "corrections": m.corrected_facts or "",
            "grounding_score": m.grounding_score,
            "confidence_level": m.confidence_level,
            "reviewed_at": str(m.reviewed_at) if m.reviewed_at else str(m.created_at)
        })

    return results

@router.get("/projects/{project_id}/sessions")
def get_project_sessions(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.AnalysisSession).filter(models.AnalysisSession.project_id == project_id).order_by(models.AnalysisSession.created_at.desc()).all()

@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    return db.query(models.AnalysisMessage).filter(models.AnalysisMessage.session_id == session_id).order_by(models.AnalysisMessage.created_at.asc()).all()
